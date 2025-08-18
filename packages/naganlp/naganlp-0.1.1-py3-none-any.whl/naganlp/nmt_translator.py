import os
import pickle
import random
import re
from typing import List, Optional, Tuple
import heapq
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from huggingface_hub import HfApi, hf_hub_download
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset, Subset
from tqdm import tqdm
import sentencepiece as spm
import tempfile # <-- Added for safe saving

# --- User-Facing Translator Class (for inference after training) ---
class Translator:
    def __init__(self, model_id: str, device: Optional[str] = None):
        if device is None: self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else: self.device = device
        print(f"Loading translator model to device: {self.device}")
        model_path = hf_hub_download(repo_id=model_id, filename="nmt_checkpoint.pt")
        src_tokenizer_path = hf_hub_download(repo_id=model_id, filename="naga_sp_nagamese.model")
        tgt_tokenizer_path = hf_hub_download(repo_id=model_id, filename="eng_sp_english.model")
        self.src_vocab = SPVocab(src_tokenizer_path)
        self.tgt_vocab = SPVocab(tgt_tokenizer_path)
        checkpoint = torch.load(model_path, map_location=self.device)
        hid_dim, n_layers, dropout, emb_dim = 512, 2, 0.4, 256
        attn = Attention(hid_dim)
        enc = Encoder(len(self.src_vocab), emb_dim, hid_dim, n_layers, dropout, self.src_vocab.pad_idx)
        dec = Decoder(len(self.tgt_vocab), emb_dim, hid_dim, n_layers, dropout, attn, self.tgt_vocab.pad_idx)
        self.model = Seq2Seq(enc, dec, self.device).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        print("Translator loaded successfully.")

    def translate(self, sentence: str, beam_size: int = 5, max_len: int = 50) -> str:
        self.model.eval()
        tokens = self.src_vocab.sp.encode(sentence.lower())
        src_tensor = torch.LongTensor(tokens).unsqueeze(1).to(self.device)
        with torch.no_grad():
            translation_ids, _ = beam_search_decode(self.model, src_tensor, self.tgt_vocab, beam_size, max_len)
        if translation_ids and translation_ids[0] == self.tgt_vocab.sos_idx: translation_ids = translation_ids[1:]
        if translation_ids and translation_ids[-1] == self.tgt_vocab.eos_idx: translation_ids = translation_ids[:-1]
        return self.tgt_vocab.sp.decode(translation_ids)


# --- Data and Tokenizer Utilities ---
def train_sentencepiece_model(text_data_path: str, model_prefix: str, vocab_size: int, lang: str) -> Tuple[str, str]:
    model_path, vocab_path = f"{model_prefix}_{lang}.model", f"{model_prefix}_{lang}.vocab"
    if os.path.exists(model_path): return model_path, vocab_path
    spm.SentencePieceTrainer.train(
        f'--input={text_data_path} --model_prefix={model_prefix}_{lang} '
        f'--vocab_size={vocab_size} --character_coverage=1.0 --model_type=bpe '
        f'--pad_id=0 --unk_id=1 --bos_id=2 --eos_id=3 '
        f'--pad_piece=<pad> --unk_piece=<unk> --bos_piece=<sos> --eos_piece=<eos>'
    )
    return model_path, vocab_path

def prep_dataframe(df: pd.DataFrame, src_tokenizer: spm.SentencePieceProcessor, tgt_tokenizer: spm.SentencePieceProcessor, max_len: int = 256) -> pd.DataFrame:
    def clean_text(text: str) -> str:
        if not isinstance(text, str): return ""
        text = re.sub(r'<[^>]+>', '', text).strip().lower()
        return re.sub(r'\s+', ' ', text)
    df['english_cleaned'] = df['english'].apply(clean_text)
    df['nagamese_cleaned'] = df['nagamese'].apply(clean_text)
    df.dropna(subset=['english_cleaned', 'nagamese_cleaned'], inplace=True)
    df = df[df['english_cleaned'].str.len() > 0]
    df = df[df['nagamese_cleaned'].str.len() > 0]
    df['nagamese_tokens'] = df['nagamese_cleaned'].apply(lambda x: src_tokenizer.encode(x))
    df['english_tokens'] = df['english_cleaned'].apply(lambda x: tgt_tokenizer.encode(x))
    df = df[df['nagamese_tokens'].str.len() <= max_len]
    df = df[df['english_tokens'].str.len() <= max_len]
    return df

def load_and_prep_data(filepath: str, src_tokenizer: spm.SentencePieceProcessor, tgt_tokenizer: spm.SentencePieceProcessor, max_len: int = 256) -> Optional[pd.DataFrame]:
    if not os.path.exists(filepath): return None
    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='warn', header=None, names=['nagamese', 'english'])
    return prep_dataframe(df, src_tokenizer, tgt_tokenizer, max_len)


# --- Vocabulary and Dataset Classes ---
class SPVocab:
    def __init__(self, sp_model_path: str):
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(sp_model_path)
        self.pad_idx, self.unk_idx, self.sos_idx, self.eos_idx = self.sp.pad_id(), self.sp.unk_id(), self.sp.bos_id(), self.sp.eos_id()
    def __len__(self): return self.sp.get_piece_size()
    def __getitem__(self, idx): return self.sp.id_to_piece(idx)

class TranslationDataset(Dataset):
    def __init__(self, df: pd.DataFrame):
        self.src_sents, self.tgt_sents = df['nagamese_tokens'].tolist(), df['english_tokens'].tolist()
    def __len__(self): return len(self.src_sents)
    def __getitem__(self, idx): return torch.tensor(self.src_sents[idx], dtype=torch.long), torch.tensor(self.tgt_sents[idx], dtype=torch.long)


# --- Model Component Classes ---
class Encoder(nn.Module):
    def __init__(self, input_dim, emb_dim, hid_dim, n_layers, dropout, pad_idx):
        super().__init__()
        self.embedding = nn.Embedding(input_dim, emb_dim, padding_idx=pad_idx)
        self.rnn = nn.GRU(emb_dim, hid_dim, num_layers=n_layers, bidirectional=True, dropout=dropout if n_layers > 1 else 0)
        self.fc = nn.Linear(hid_dim * 2, hid_dim)
        self.dropout = nn.Dropout(dropout)
    def forward(self, src):
        embedded = self.dropout(self.embedding(src))
        outputs, hidden = self.rnn(embedded)
        hidden = torch.tanh(self.fc(torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)))
        return outputs, hidden

class Attention(nn.Module):
    def __init__(self, hid_dim):
        super().__init__()
        self.attn = nn.Linear((hid_dim * 2) + hid_dim, hid_dim)
        self.v = nn.Linear(hid_dim, 1, bias=False)
    def forward(self, hidden, encoder_outputs):
        hidden = hidden.unsqueeze(1).repeat(1, encoder_outputs.shape[0], 1)
        encoder_outputs = encoder_outputs.permute(1, 0, 2)
        energy = torch.tanh(self.attn(torch.cat((hidden, encoder_outputs), dim=2)))
        attention = self.v(energy).squeeze(2)
        return torch.softmax(attention, dim=1)

class Decoder(nn.Module):
    def __init__(self, output_dim, emb_dim, hid_dim, n_layers, dropout, attention, pad_idx):
        super().__init__()
        self.output_dim = output_dim
        self.attention = attention
        self.embedding = nn.Embedding(output_dim, emb_dim, padding_idx=pad_idx)
        self.n_layers = n_layers
        self.hid_dim = hid_dim
        self.rnn = nn.GRU((hid_dim * 2) + emb_dim, hid_dim, num_layers=n_layers, dropout=dropout if n_layers > 1 else 0)
        self.fc_out = nn.Linear((hid_dim * 2) + hid_dim + emb_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, input, hidden, encoder_outputs):
        input = input.unsqueeze(0)
        embedded = self.dropout(self.embedding(input))
        a = self.attention(hidden[-1], encoder_outputs).unsqueeze(1)
        weighted = torch.bmm(a, encoder_outputs.permute(1, 0, 2)).permute(1, 0, 2)
        rnn_input = torch.cat((embedded, weighted), dim=2)
        output, hidden = self.rnn(rnn_input, hidden)
        prediction = self.fc_out(torch.cat((output.squeeze(0), weighted.squeeze(0), embedded.squeeze(0)), dim=1))
        return prediction, hidden, a.squeeze(1)

class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder, self.decoder, self.device = encoder, decoder, device
    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size, trg_len, trg_vocab_size = trg.shape[1], trg.shape[0], self.decoder.output_dim
        outputs = torch.zeros(trg_len, batch_size, trg_vocab_size).to(self.device)
        encoder_outputs, hidden = self.encoder(src)
        hidden = hidden.unsqueeze(0).repeat(self.decoder.n_layers, 1, 1)
        input = trg[0,:]
        for t in range(1, trg_len):
            output, hidden, _ = self.decoder(input, hidden, encoder_outputs)
            outputs[t] = output
            top1 = output.argmax(1)
            input = trg[t] if random.random() < teacher_forcing_ratio else top1
        return outputs


# --- Training and Evaluation Utilities ---
def collate_fn(batch, pad_idx, device, sos_idx=2, eos_idx=3):
    src_batch, tgt_batch = [], []
    for src_sample, tgt_sample in batch:
        src_batch.append(torch.cat([torch.tensor([sos_idx]), src_sample, torch.tensor([eos_idx])]))
        tgt_batch.append(torch.cat([torch.tensor([sos_idx]), tgt_sample, torch.tensor([eos_idx])]))
    return pad_sequence(src_batch, padding_value=pad_idx).to(device), \
           pad_sequence(tgt_batch, padding_value=pad_idx).to(device)

def train_epoch(model, loader, optimizer, criterion, clip):
    model.train()
    epoch_loss = 0
    for src, trg in tqdm(loader, desc="Training Progress", leave=False):
        optimizer.zero_grad()
        output = model(src, trg)
        loss = criterion(output[1:].view(-1, output.shape[-1]), trg[1:].view(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
        optimizer.step()
        epoch_loss += loss.item()
    return epoch_loss / len(loader)

def evaluate_model(model, loader, criterion, src_vocab, tgt_vocab, beam_size, length_penalty):
    model.eval()
    epoch_loss = 0
    candidate_corpus, references_corpus = [], []
    printed_examples_this_epoch = False
    with torch.no_grad():
        for src, trg in tqdm(loader, desc="Validation Progress", leave=False):
            output = model(src, trg, 0)
            loss = criterion(output[1:].view(-1, output.shape[-1]), trg[1:].view(-1))
            epoch_loss += loss.item()
            for i in range(src.shape[1]):
                src_sent, trg_sent = src[:, i].unsqueeze(1), trg[:, i]
                src_tokens = [token for token in src_sent.squeeze().tolist() if token not in {src_vocab.pad_idx, src_vocab.sos_idx, src_vocab.eos_idx}]
                source_text = src_vocab.sp.decode(src_tokens)
                ref_tokens = [token for token in trg_sent.tolist() if token not in {tgt_vocab.pad_idx, tgt_vocab.sos_idx, tgt_vocab.eos_idx}]
                reference_text = tgt_vocab.sp.decode(ref_tokens)
                references_corpus.append([reference_text.split()])
                translation_ids, _ = beam_search_decode(model, src_sent, tgt_vocab, beam_size, 50, length_penalty)
                pred_tokens = [token for token in translation_ids if token not in {tgt_vocab.pad_idx, tgt_vocab.sos_idx, tgt_vocab.eos_idx}]
                candidate_text = tgt_vocab.sp.decode(pred_tokens)
                candidate_corpus.append(candidate_text.split())
                if not printed_examples_this_epoch and i < 3:
                    print("\n--- Validation Example ---")
                    print(f"  Source:     {source_text}")
                    print(f"  Reference:  {reference_text}")
                    print(f"  Predicted:  {candidate_text}")
                    print("------------------------")
            printed_examples_this_epoch = True
    bleu = corpus_bleu(references_corpus, candidate_corpus, smoothing_function=SmoothingFunction().method4)
    return epoch_loss / len(loader), bleu

def beam_search_decode(model, src_tensor, tgt_vocab, beam_size, max_len, length_penalty=0.7):
    model.eval()
    with torch.no_grad():
        encoder_outputs, hidden = model.encoder(src_tensor)
        hidden = hidden.unsqueeze(0).repeat(model.decoder.n_layers, 1, 1)
    
    beam = [(0.0, [tgt_vocab.sos_idx], hidden)]
    completed_sequences = []

    for _ in range(max_len):
        new_beam = []
        for score, seq, hidden_state in beam:
            if seq[-1] == tgt_vocab.eos_idx:
                final_score = score / (len(seq) ** length_penalty)
                completed_sequences.append((final_score, seq))
                continue
            trg_tensor = torch.LongTensor([seq[-1]]).to(model.device)
            output, new_hidden, _ = model.decoder(trg_tensor, hidden_state, encoder_outputs)
            log_probs = torch.log_softmax(output, dim=1)
            top_log_probs, top_indices = log_probs.topk(beam_size)
            for i in range(beam_size):
                next_token, log_prob = top_indices[0, i].item(), top_log_probs[0, i].item()
                new_beam.append((score + log_prob, seq + [next_token], new_hidden))

        if not new_beam: break
        beam = sorted(new_beam, key=lambda x: x[0], reverse=True)[:beam_size]
        if all(b[1][-1] == tgt_vocab.eos_idx for b in beam):
            completed_sequences.extend([(s / (len(q) ** length_penalty), q) for s, q, _ in beam])
            break

    if not completed_sequences:
        completed_sequences.extend([(s / (len(q) ** length_penalty), q) for s, q, _ in beam])

    best_sequence = sorted(completed_sequences, key=lambda x: x[0], reverse=True)[0][1]
    return best_sequence, None


# --- Main Training Orchestration Function ---
def train_and_upload_translator(
    csv_path: str,
    hub_model_id: str,
    gloss_path: Optional[str] = None,
    intermediate_phrases_path: Optional[str] = None
):
    # --- Hyperparameters ---
    MAX_FINETUNE_EPOCHS = 0
    PRETRAIN_EPOCHS = 20
    INTERMEDIATE_EPOCHS = 40
    BATCH_SIZE = 32
    PATIENCE = 5
    ENC_EMB_DIM, DEC_EMB_DIM, HID_DIM, N_LAYERS = 256, 256, 512, 2
    DROPOUT = 0.4
    LEARNING_RATE, WEIGHT_DECAY, CLIP = 1e-4, 1e-5, 1.0
    SP_VOCAB_SIZE, BEAM_SIZE, LENGTH_PENALTY = 8000, 3, 0.7
    VAL_SPLIT_SIZE = 0.1
    CHECKPOINT_PATH = 'nmt_checkpoint.pt'

    # --- CORRECTED: Safe saving function to prevent corruption ---
    def safe_save(state: dict, path: str):
        """Atomically saves a checkpoint to avoid corruption from interruptions."""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, dir=os.path.dirname(path), suffix='.tmp') as f:
                temp_path = f.name
                torch.save(state, f)
            os.rename(temp_path, path)
        except Exception as e:
            print(f"!!! FAILED to save checkpoint: {e}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # --- Phase 1a: Tokenizer Training ---
    print("--- Phase 1a: Preparing Data and Training Tokenizers ---")
    full_df_for_tok = pd.read_csv(csv_path)
    if gloss_path and os.path.exists(gloss_path):
        gloss_df_temp = pd.read_csv(gloss_path, header=None, names=['nagamese', 'english'])
        full_df_for_tok = pd.concat([full_df_for_tok, gloss_df_temp], ignore_index=True)
    
    nagamese_text_path = "temp_nagamese.txt"
    english_text_path = "temp_english.txt"
    with open(nagamese_text_path, "w", encoding="utf-8") as f: f.write("\n".join(full_df_for_tok['nagamese'].dropna().astype(str).tolist()))
    with open(english_text_path, "w", encoding="utf-8") as f: f.write("\n".join(full_df_for_tok['english'].dropna().astype(str).tolist()))
    
    src_sp_model_path, src_sp_vocab_path = train_sentencepiece_model(nagamese_text_path, "naga_sp", SP_VOCAB_SIZE, "nagamese")
    tgt_sp_model_path, tgt_sp_vocab_path = train_sentencepiece_model(english_text_path, "eng_sp", SP_VOCAB_SIZE, "english")
    
    src_vocab = SPVocab(src_sp_model_path)
    tgt_vocab = SPVocab(tgt_sp_model_path)
    
    os.remove(nagamese_text_path); os.remove(english_text_path)
    print(f"Source vocab size: {len(src_vocab)}; Target vocab size: {len(tgt_vocab)}")

    # --- Phase 1b: Model and Optimizer Initialization ---
    print("--- Phase 1b: Initializing Model ---")
    attn = Attention(HID_DIM)
    enc = Encoder(len(src_vocab), ENC_EMB_DIM, HID_DIM, N_LAYERS, DROPOUT, src_vocab.pad_idx)
    dec = Decoder(len(tgt_vocab), DEC_EMB_DIM, HID_DIM, N_LAYERS, DROPOUT, attn, tgt_vocab.pad_idx)
    model = Seq2Seq(enc, dec, device).to(device)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    criterion = nn.CrossEntropyLoss(ignore_index=tgt_vocab.pad_idx)

    # --- CORRECTED: Checkpoint Loading with Error Handling ---
    start_epoch = 0
    best_bleu = -1.0
    if os.path.exists(CHECKPOINT_PATH):
        try:
            print(f"Resuming training from checkpoint: {CHECKPOINT_PATH}")
            checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            start_epoch = checkpoint['epoch'] + 1
            best_bleu = checkpoint.get('bleu', -1.0)
            print(f"Resumed from Epoch {start_epoch}. Best BLEU so far: {best_bleu*100:.2f}")
        except (RuntimeError, EOFError) as e:
            print(f"!!! WARNING: Could not load checkpoint file. It may be corrupt: {e}")
            print("--- Deleting corrupt checkpoint and starting training from scratch. ---")
            os.remove(CHECKPOINT_PATH)
            start_epoch = 0
            best_bleu = -1.0

    # --- Phase 2: Pre-training (Glossary) ---
    if start_epoch < PRETRAIN_EPOCHS:
        if gloss_path and os.path.exists(gloss_path):
            print("\n--- Phase 2: Pre-training on Augmented Glossary Data ---")
            gloss_df = pd.read_csv(gloss_path, header=None, names=['nagamese', 'english'])
            gloss_df_flipped = gloss_df.rename(columns={'nagamese': 'english', 'english': 'nagamese'})
            augmented_gloss_df = pd.concat([gloss_df, gloss_df_flipped], ignore_index=True)
            print(f"Original glossary size: {len(gloss_df)}. Augmented size: {len(augmented_gloss_df)}")
            
            pretrain_dataset = TranslationDataset(prep_dataframe(augmented_gloss_df, src_vocab.sp, tgt_vocab.sp))
            pretrain_loader = DataLoader(pretrain_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=lambda b: collate_fn(b, src_vocab.pad_idx, device))

            for epoch in range(start_epoch, PRETRAIN_EPOCHS):
                train_loss = train_epoch(model, pretrain_loader, optimizer, criterion, CLIP)
                print(f"Pre-train Epoch: {epoch+1:02}/{PRETRAIN_EPOCHS} | Train Loss: {train_loss:.3f}")
                safe_save({'epoch': epoch, 'model_state_dict': model.state_dict(), 'optimizer_state_dict': optimizer.state_dict(), 'bleu': best_bleu}, CHECKPOINT_PATH)
        else:
             print("\n--- Skipping Phase 2: Pre-training (no glossary file provided or found) ---")
    
    # --- Phase 3: Intermediate Training (Phrases) ---
    INTERMEDIATE_END_EPOCH = PRETRAIN_EPOCHS + INTERMEDIATE_EPOCHS
    if start_epoch < INTERMEDIATE_END_EPOCH:
        if intermediate_phrases_path and os.path.exists(intermediate_phrases_path):
            print("\n--- Phase 3: Intermediate Training on Phrases Data ---")
            phrases_df = pd.read_csv(intermediate_phrases_path, header=None, names=['nagamese', 'english'])
            print(f"Phrases data size: {len(phrases_df)}")
            
            intermediate_dataset = TranslationDataset(prep_dataframe(phrases_df, src_vocab.sp, tgt_vocab.sp))
            intermediate_loader = DataLoader(intermediate_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=lambda b: collate_fn(b, src_vocab.pad_idx, device))
            
            loop_start_epoch = max(start_epoch, PRETRAIN_EPOCHS)
            for epoch in range(loop_start_epoch, INTERMEDIATE_END_EPOCH):
                train_loss = train_epoch(model, intermediate_loader, optimizer, criterion, CLIP)
                print(f"Intermediate-train Epoch: {epoch+1:02}/{INTERMEDIATE_END_EPOCH} | Train Loss: {train_loss:.3f}")
                safe_save({'epoch': epoch, 'model_state_dict': model.state_dict(), 'optimizer_state_dict': optimizer.state_dict(), 'bleu': best_bleu}, CHECKPOINT_PATH)
        else:
            if intermediate_phrases_path:
                 print(f"\n--- WARNING: Skipping Phase 3. Intermediate phrases file not found at: '{intermediate_phrases_path}' ---")
            else:
                 print("\n--- Skipping Phase 3: Intermediate Training (no phrases file provided) ---")

    # --- Phase 4: Fine-tuning with Validation (Sentences) ---
    print("\n--- Phase 4: Fine-tuning on Sentence Data ---")
    main_df_for_finetune = pd.read_csv(csv_path)
    full_dataset = TranslationDataset(prep_dataframe(main_df_for_finetune, src_vocab.sp, tgt_vocab.sp))
    
    indices = list(range(len(full_dataset)))
    split = int(np.floor(VAL_SPLIT_SIZE * len(full_dataset)))
    np.random.seed(42)
    np.random.shuffle(indices)
    train_indices, val_indices = indices[split:], indices[:split]
    
    train_dataset = Subset(full_dataset, train_indices)
    val_dataset = Subset(full_dataset, val_indices)
    
    print(f"Full dataset size: {len(full_dataset)}. Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=lambda b: collate_fn(b, src_vocab.pad_idx, device))
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=lambda b: collate_fn(b, src_vocab.pad_idx, device))

    patience_counter = 0
    fine_tune_start_epoch = max(start_epoch, INTERMEDIATE_END_EPOCH)
    FINETUNE_END_EPOCH = fine_tune_start_epoch + MAX_FINETUNE_EPOCHS

    for epoch in range(fine_tune_start_epoch, FINETUNE_END_EPOCH):
        print(f"\n--- Fine-tuning Epoch {epoch+1} ---")
        train_loss = train_epoch(model, train_loader, optimizer, criterion, CLIP)
        val_loss, val_bleu = evaluate_model(model, val_loader, criterion, src_vocab, tgt_vocab, BEAM_SIZE, LENGTH_PENALTY)
        
        print(f"Epoch Summary: Train Loss: {train_loss:.3f} | Val. Loss: {val_loss:.3f} | Val. BLEU: {val_bleu*100:.2f}")

        if val_bleu > best_bleu:
            best_bleu = val_bleu
            patience_counter = 0
            print(f"\n  New best BLEU score! Saving checkpoint to '{CHECKPOINT_PATH}'")
            safe_save({'epoch': epoch, 'model_state_dict': model.state_dict(), 'optimizer_state_dict': optimizer.state_dict(), 'bleu': best_bleu}, CHECKPOINT_PATH)
        else:
            patience_counter += 1
            print(f"\n  BLEU did not improve. Patience: {patience_counter}/{PATIENCE}")

        if patience_counter >= PATIENCE:
            print(f"--- Early stopping triggered after {PATIENCE} epochs with no improvement. ---")
            break

    # --- Phase 5: Uploading to Hugging Face Hub ---
    print(f"\n--- Phase 5: Uploading Best Model and Tokenizers to {hub_model_id} ---")
    try:
        api = HfApi()
        api.upload_file(path_or_fileobj=CHECKPOINT_PATH, path_in_repo="nmt_checkpoint.pt", repo_id=hub_model_id, repo_type="model")
        api.upload_file(path_or_fileobj=src_sp_model_path, path_in_repo=os.path.basename(src_sp_model_path), repo_id=hub_model_id)
        api.upload_file(path_or_fileobj=tgt_sp_model_path, path_in_repo=os.path.basename(tgt_sp_model_path), repo_id=hub_model_id)
        api.upload_file(path_or_fileobj=src_sp_vocab_path, path_in_repo=os.path.basename(src_sp_vocab_path), repo_id=hub_model_id)
        api.upload_file(path_or_fileobj=tgt_sp_vocab_path, path_in_repo=os.path.basename(tgt_sp_vocab_path), repo_id=hub_model_id)
        print("--- Best model, tokenizers, and vocabs successfully uploaded. ---")
    except Exception as e:
        print(f"!!! FAILED TO UPLOAD TO HUB: {e}")