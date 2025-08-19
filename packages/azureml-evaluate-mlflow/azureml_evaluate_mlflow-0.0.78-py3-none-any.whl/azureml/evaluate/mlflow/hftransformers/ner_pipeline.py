# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Union

import numpy as np
import scipy
import torch
from torch import nn

from azureml.evaluate.mlflow.hftransformers.constants import DataLiterals

from transformers.pipelines.base import Pipeline


class TokenClassificationCustomPipeline(Pipeline):
    """
    Named Entity Recognition pipeline using any `ModelForTokenClassification`. See the [named entity recognition
    examples](../task_summary#named-entity-recognition) for more information.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.train_labels = kwargs.pop("train_labels")
        self.max_seq_length = kwargs.pop("max_seq_length")
        self.label_map = {self.train_labels[key]: key for key in self.train_labels}

    def _sanitize_parameters(
            self,
            **tokenizer_config
    ):
        preprocess_params = tokenizer_config
        return preprocess_params, {}, {}

    def __call__(self, inputs: Union[str, List[str]], **kwargs):
        """
        Classify each token of the text(s) given as inputs.
        """
        self._tokenizer_config = kwargs.copy()
        return super().__call__(inputs, **kwargs)

    def preprocess(self, sentence, **preprocess_params):
        tokens = sentence.split(" ")
        # append label which will be used to align predictions only
        words = [item for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
        labels = ["O"] * len(words)
        tokenizer_config = {
            'max_length': self.max_seq_length,
            'padding': 'max_length',
            'truncation': True,
            'return_tensors': "pt",
            'is_split_into_words': True,
            **self._tokenizer_config
        }
        tokenized = self.tokenizer(words,
                                   None,
                                   **tokenizer_config)
        pad_id = nn.CrossEntropyLoss().ignore_index
        label_ids = np.full(self.max_seq_length, fill_value=pad_id, dtype=np.int32)

        token_idx = 1  # start with index 1 because 0 is a special token
        for label_idx in range(len(words)):
            if token_idx < self.max_seq_length:
                # set label at the starting index of the token
                label_ids[token_idx] = self.label_map[labels[label_idx]]
            token_idx += len(self.tokenizer.tokenize(words[label_idx]))
            # TODO: Remove extra tokenization step if possible ^

        # this should only be added during Split.test once we stop return labels for test split
        tokenized["labels"] = torch.LongTensor([[int(item) for item in label_ids]])
        return tokenized

    def _forward(self, model_inputs):
        # Forward
        labels = model_inputs.pop("labels")
        if self.framework == "tf":
            logits = self.model(**model_inputs)[0]
        else:
            output = self.model(**model_inputs)
            logits = output["logits"] if isinstance(output, dict) else output[0]
        return {
            "logits": logits,
            "labels": labels,
            **model_inputs
        }

    def postprocess(self, all_outputs):
        predictions, label_ids = all_outputs["logits"].detach().numpy(), all_outputs["labels"]
        preds_list, _, _ = self._align_predictions_with_proba(np.array(predictions), np.array(label_ids))
        preds_list = list(map(lambda x: str(x), preds_list))
        return preds_list

    def _align_predictions_with_proba(self, predictions, label_ids):
        """
        Helper function to align predictions with words
        @param predictions:
        @param label_ids:
        @return:
        """
        preds = np.argmax(predictions, axis=2)
        probas = scipy.special.softmax(predictions, axis=2)
        pred_probas = np.amax(probas, axis=2)
        batch_size, seq_len = preds.shape

        out_label_list = [[] for _ in range(batch_size)]
        preds_list = [[] for _ in range(batch_size)]
        preds_proba_list = [[] for _ in range(batch_size)]

        for i in range(batch_size):
            for j in range(seq_len):
                if label_ids[i, j] != nn.CrossEntropyLoss().ignore_index:
                    out_label_list[i].append(self.train_labels[label_ids[i][j]])
                    preds_list[i].append(self.train_labels[preds[i][j]])
                    preds_proba_list[i].append(pred_probas[i][j])
        return preds_list, out_label_list, preds_proba_list
