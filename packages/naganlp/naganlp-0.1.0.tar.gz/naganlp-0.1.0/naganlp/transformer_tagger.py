# file: naganlp/transformer_tagger.py

import os
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from datasets import Dataset
from sklearn.metrics import classification_report, accuracy_score
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
    pipeline
)

def read_conll(path: str, delimiter: str = '\t') -> Dataset:
    """Reads a CoNLL-formatted file and returns a Hugging Face Dataset."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"The CoNLL file was not found at: {path}")
    sentences, tags = [], []
    with open(path, encoding='utf-8') as f:
        sent, sent_tags = [], []
        for line in f:
            line = line.strip()
            if not line:
                if sent:
                    sentences.append(sent)
                    tags.append(sent_tags)
                    sent, sent_tags = [], []
            else:
                parts = line.split(delimiter)
                if len(parts) >= 2:
                    sent.append(parts[0])
                    sent_tags.append(parts[-1])
        if sent:
            sentences.append(sent)
            tags.append(sent_tags)
    return Dataset.from_dict({'tokens': sentences, 'pos_tags': tags})

class PosTagger:
    """
    A high-accuracy Part-of-Speech tagger for Nagamese.

    This class uses a fine-tuned Transformer model. On first use, it will
    download the model from the Hugging Face Hub and cache it locally.

    Example:
        >>> tagger = PosTagger("agnivamaiti/naganlp-pos-tagger")
        >>> result = tagger.tag("Moi ghor te jai ase")
        >>> print(result)
        [{'entity_group': 'PRON', 'word': 'moi', ...}]
    """

    def __init__(self, model_name_or_path: str = "agnivamaiti/naganlp-pos-tagger"):
        """
        Initialize the POS Tagger with a pre-trained model.

        Args:
            model_name_or_path (str, optional): The model identifier from the Hugging Face Hub or a
                                              path to a local directory. Defaults to "agnivamaiti/naganlp-pos-tagger".
        """
        if not model_name_or_path or not isinstance(model_name_or_path, str):
            raise ValueError("model_name_or_path must be a non-empty string")
        
        if model_name_or_path == "your-username/naganlp-pos-tagger":
            import warnings
            warnings.warn(
                "Using default model 'agnivamaiti/naganlp-pos-tagger'. "
                "For better performance, train your own model using the CLI."
            )
            model_name_or_path = "agnivamaiti/naganlp-pos-tagger"

        self.model_name_or_path = model_name_or_path
        self.device = 0 if torch.cuda.is_available() else -1
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the token classification pipeline."""
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.tagger = pipeline(
                "token-classification",
                model=self.model_name_or_path,
                tokenizer=self.model_name_or_path,
                device=device,
                aggregation_strategy="simple"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model '{self.model_name_or_path}'. "
                "Please ensure it's a valid Hugging Face model ID or local path."
            ) from e

    def tag(self, text: str) -> list[dict]:
        """
        Tag a Nagamese sentence with part-of-speech labels.

        Args:
            text (str): The input text to tag.

        Returns:
            list[dict]: A list of dictionaries for each tagged word.
        """
        if not isinstance(text, str):
            raise ValueError(f"Input text must be a string, got {type(text).__name__}")
        if not text.strip():
            return []
        try:
            return self.tagger(text)
        except Exception as e:
            raise RuntimeError(f"Failed to tag text. Error: {str(e)}") from e
            
    def __repr__(self) -> str:
        """Return a string representation of the tagger."""
        return f"{self.__class__.__name__}(model_name_or_path='{self.model_name_or_path}')"

def train_and_upload_tagger(conll_path: str, hub_model_id: str):
    """
    (Developer function) Trains a POS tagger and uploads it to the Hugging Face Hub.
    You must be logged in via `huggingface-cli login` to use this.
    """
    print("--- Preparing Dataset ---")
    dataset = read_conll(conll_path)

    unique_tags = sorted({tag for tag_list in dataset['pos_tags'] for tag in tag_list})
    label2id = {label: i for i, label in enumerate(unique_tags)}
    id2label = {i: label for i, label in enumerate(unique_tags)}
    
    checkpoint = 'bert-base-multilingual-cased'
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)

    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)
        labels = []
        for i, label in enumerate(examples["pos_tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None or word_idx == previous_word_idx:
                    label_ids.append(-100)
                else:
                    label_ids.append(label2id[label[word_idx]])
                previous_word_idx = word_idx
            labels.append(label_ids)
        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    tokenized_ds = dataset.map(tokenize_and_align_labels, batched=True)
    split = tokenized_ds.train_test_split(test_size=0.1, seed=42)
    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)
    
    model = AutoModelForTokenClassification.from_pretrained(
        checkpoint, num_labels=len(unique_tags), id2label=id2label, label2id=label2id
    )

    def compute_metrics(p):
        predictions = np.argmax(p.predictions, axis=2)
        true_labels = p.label_ids
        true_predictions = [
            [id2label[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, true_labels)
        ]
        true_labels = [
            [id2label[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, true_labels)
        ]
        flat_true_predictions = [item for sublist in true_predictions for item in sublist]
        flat_true_labels = [item for sublist in true_labels for item in sublist]
        results = classification_report(flat_true_labels, flat_true_predictions, output_dict=True, zero_division=0)
        return {
            "f1": results["weighted avg"]["f1-score"],
            "accuracy": accuracy_score(flat_true_labels, flat_true_predictions)
        }

    print("--- Configuring Training ---")
    training_args = TrainingArguments(
        # The output_dir is where the Trainer saves model checkpoints during training.
        # It also serves as the local clone of your Hub repo.
        output_dir=hub_model_id.split("/")[-1],
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        load_best_model_at_end=True,
        report_to="none",
        
        # --- KEY CHANGE 1: ENABLE PUSH TO HUB ---
        # This tells the Trainer to log in and prepare for uploading.
        push_to_hub=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    print(f"--- Starting Training & Uploading to {hub_model_id} ---")
    trainer.train()
    
    # --- KEY CHANGE 2: EXPLICITLY PUSH THE FINAL MODEL ---
    # This command uploads the best model, tokenizer, and training history.
    print("--- Uploading final model to the Hub ---")
    trainer.push_to_hub(commit_message="End of training")
    
    print("--- Model successfully trained and uploaded! ---")