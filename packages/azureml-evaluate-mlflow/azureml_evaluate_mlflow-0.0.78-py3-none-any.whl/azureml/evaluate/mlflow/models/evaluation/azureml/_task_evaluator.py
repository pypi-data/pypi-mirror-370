# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd
import numpy as np


class TaskEvaluator(ABC):

    @abstractmethod
    def evaluate(self, model, X_test, y_test, **kwargs) -> Dict:
        ...

    def _convert_predictions(self, preds):
        if isinstance(preds, pd.DataFrame) and len(preds.columns) == 1:
            return preds[preds.columns[0]].to_numpy()
        if isinstance(preds, pd.DataFrame) or isinstance(preds, pd.Series):
            return preds.to_numpy()
        if isinstance(preds, list):
            return np.array(preds)
        return preds
