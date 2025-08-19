# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable-all
# flake8: noqa
import ast
import base64
import sys
import subprocess
import mlflow

from os.path import basename, join
from datasets import load_dataset

from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesPipelineType, \
    TimeSeriesTransformer
from azureml.automl.runtime.shared.model_wrappers import ForecastingPipelineWrapper
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
import azureml.evaluate.mlflow as azureml_mlflow
from azureml.evaluate.mlflow.models.evaluation.base import EvaluationDataset
from collections import namedtuple
import json
import pytest
import numpy as np
import sklearn.datasets
import sklearn.linear_model
import tempfile
import pandas as pd
from os.path import join, dirname, exists
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import AutoModelForSequenceClassification, AutoModelForTokenClassification, \
    AutoModelForSeq2SeqLM, AutoModelForQuestionAnswering, AutoModelForCausalLM, AutoModelForMaskedLM, \
    AutoModelForImageClassification, AutoImageProcessor
from transformers import AutoTokenizer
from transformers import AutoConfig
from sklearn.pipeline import Pipeline
from pycocotools import mask as pycoco_mask

"""Named entity recognition dataset wrapper class."""

import logging
from typing import List, Optional
import torch
from torch import nn
from torch.utils.data.dataset import Dataset
from torch.utils.data import Dataset as PyTorchDataset
from transformers import PreTrainedTokenizerBase
from transformers import PreTrainedTokenizer


class DataLiterals:
    NER_IGNORE_TOKENS = ["", " ", "\n"]


logger = logging.getLogger(__name__)


class NerDatasetWrapper(Dataset):
    """This will be superseded by a framework-agnostic approach soon."""

    def __init__(
            self,
            data,
            tokenizer: PreTrainedTokenizer,
            labels: List[str],
            max_seq_length: Optional[int] = None,
    ):
        """Token classification dataset constructor func."""
        # data = data.replace("-DOCSTART- O\n\n", "")
        # self.data = data.split("\n\n")
        self.data = data
        self.tokenizer = tokenizer
        self.label_map = {label: i for i, label in enumerate(labels)}
        self.max_seq_length = max_seq_length

    def __len__(self):
        """Token classification dataset len func."""
        return len(self.data)

    def __getitem__(self, idx):
        """Token classification dataset getitem func."""

        tokens = self.data['X'][idx].split(" ")

        # append label which will be used to align predictions only
        words = [item for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
        labels = ["O"] * len(words)

        tokenized = self.tokenizer(words,
                                   None,
                                   max_length=self.max_seq_length,
                                   padding='max_length',
                                   return_token_type_ids=True,
                                   truncation=True,
                                   is_split_into_words=True)
        # The code below sets label ids for tokens computed above
        # Set padding to nn.CrossEntropyLoss().ignore_index so it isnt used in loss computation
        pad_id = nn.CrossEntropyLoss().ignore_index
        label_ids = np.full((self.max_seq_length), fill_value=pad_id, dtype=np.int32)

        token_idx = 1  # start with index 1 because 0 is a special token
        for label_idx in range(len(words)):

            if token_idx < self.max_seq_length:
                # set label at the starting index of the token
                label_ids[token_idx] = self.label_map[labels[label_idx]]

            # increment token index according to number of tokens generated for the 'word'
            # Note that BERT can create multiple tokens for single word in a language
            token_idx += len(self.tokenizer.tokenize(words[label_idx]))
            # TODO: Remove extra tokenization step if possible ^

        # this should only be added during Split.test once we stop return labels for test split
        tokenized["labels"] = [int(item) for item in label_ids]
        return tokenized


class PyTorchClassificationDatasetWrapper(PyTorchDataset):
    """
    Class for obtaining dataset to be passed into model for multi-class classification.
    This is based on the datasets.Dataset package from HuggingFace.
    """

    def __init__(self, dataframe: pd.DataFrame,
                 tokenizer: PreTrainedTokenizerBase,
                 max_seq_length: int):
        """ Init function definition

        :param dataframe: pd.DataFrame holding data to be passed
        :param train_label_list: list of labels from training data
        :param tokenizer: tokenizer to be used to tokenize the data
        :param max_seq_length: dynamically computed max sequence length
        :param label_column_name: name/title of the label column
        """
        self.tokenizer = tokenizer
        self.data = dataframe
        self.padding = "max_length"
        self.max_seq_length = min(max_seq_length, self.tokenizer.model_max_length)

    def __len__(self):
        """Len function definition."""
        return len(self.data)

    def __getitem__(self, index):
        """Getitem function definition."""
        sample = self.data.iloc[index].astype(str).str.cat(sep=". ")
        tokenized = self.tokenizer(sample, padding=self.padding, max_length=self.max_seq_length,
                                   truncation=True)
        for tokenizer_key in tokenized:
            tokenized[tokenizer_key] = torch.tensor(tokenized[tokenizer_key], dtype=torch.long)

        return tokenized


def get_iris():
    iris = sklearn.datasets.load_iris()
    return iris.data, iris.target


def get_diabetes_dataset():
    data = sklearn.datasets.load_diabetes()
    return data.data, data.target


def get_diabetes_dataset_timeseries():
    # We will hack the diabetes data set so that it
    # will mimic time series.
    bn = sklearn.datasets.load_diabetes(return_X_y=False)
    X = bn.data
    df_diabetes = pd.DataFrame(X, columns=bn.feature_names)
    df_diabetes['y'] = bn.target
    df_diabetes['date'] = pd.date_range('2001-01-01', periods=df_diabetes.shape[0])
    X_train = df_diabetes.iloc[:-7]
    y_train = X_train.pop('y').values
    X_test = df_diabetes.iloc[-7:]
    y_test = X_test.pop('y').values
    return X_train, y_train, X_test, y_test


def get_breast_cancer_dataset():
    data = sklearn.datasets.load_breast_cancer()
    return data.data, data.target


def get_20newsgroup_dataset():
    data = {
        'data': [
            'Subject: Re:  PLANETS STILL: IMAGES ORBIT BY ETHER TWIST\nFrom: alien@acheron.amigans.gen.nz (Ross Smith)\nDistribution: world\nOrganization: Muppet Labs\nLines: 27\n\nIn article <1993Apr22.213815.12288@mksol.dseg.ti.com> mccall@mksol.dseg.ti.com (fred j mccall 575-3539) writes:\n>In <1993Apr22.130923.115397@zeus.calpoly.edu> dmcaloon@tuba.calpoly.edu (David McAloon) writes:\n>\n>> ETHER IMPLODES 2 EARTH CORE, IS GRAVITY!!!\n>\n>If not for the lack of extraneously capitalized words, I\'d swear that\n>McElwaine had changed his name and moved to Cal Poly.  I also find the\n>choice of newsgroups \'interesting\'.  Perhaps someone should tell this\n>guy that \'sci.astro\' doesn\'t stand for \'astrology\'?\n>\n>It\'s truly frightening that posts like this are originating at what\n>are ostensibly centers of higher learning in this country.  Small\n>wonder that the rest of the world thinks we\'re all nuts and that we\n>have the problems that we do.\n>\n>[In case you haven\'t gotten it yet, David, I don\'t think this was\n>quite appropriate for a posting to \'sci\' groups.]\n\nWas that post for real? I thought it was a late April Fool joke. Some of it\nseemed a bit over the top even by McElwaine/Abian/etc standards :-)\n\n--\n... Ross Smith (Wanganui, NZ) ............ alien@acheron.amigans.gen.nz ...\n      "And crawling on the planet\'s face\n      Some insects called the human race\n      Lost in time and lost in space"      (RHPS)\n\n',
            'Subject: Re:  PLANETS STILL: IMAGES ORBIT BY ETHER TWIST\nFrom:  alien@acheron.amigans.gen.nz (Ross Smith)\nDistribution: world\nOrganization: Muppet Labs\nLines: 27\n\nIn article <1993Apr22.213815.12288@mksol.dseg.ti.com> mccall@mksol.dseg.ti.com (fred j mccall 575-3539) writes:\n>In <1993Apr22.130923.115397@zeus.calpoly.edu> dmcaloon@tuba.calpoly.edu (David McAloon) writes:\n>\n>> ETHER IMPLODES 2 EARTH CORE, IS GRAVITY!!!\n>\n>If not for the lack of extraneously capitalized words, I\'d swear that\n>McElwaine had changed his name and moved to Cal Poly.  I also find the\n>choice of newsgroups \'interesting\'.  Perhaps someone should tell this\n>guy that \'sci.astro\' doesn\'t stand for \'astrology\'?\n>\n>It\'s truly frightening that posts like this are originating at what\n>are ostensibly centers of higher learning in this country.  Small\n>wonder that the rest of the world thinks we\'re all nuts and that we\n>have the problems that we do.\n>\n>[In case you haven\'t gotten it yet, David, I don\'t think this was\n>quite appropriate for a posting to \'sci\' groups.]\n\nWas that post for real? I thought it was a late April Fool joke. Some of it\nseemed a bit over the top even by McElwaine/Abian/etc standards :-)\n\n--\n... Ross Smith (Wanganui, NZ) ............ alien@acheron.amigans.gen.nz ...\n      "And crawling on the planet\'s face\n      Some insects called the human race\n      Lost in time and lost in space"      (RHPS)\n\n'],
        'target': ['3', '1']
    }
    return data


def get_arxiv_dataset():
    # data = pd.read_csv("models/data/arxiv_dataset.csv")
    data_str = '''titles,summaries,terms
Addressing Action Oscillations through Learning Policy Inertia,"Deep reinforcement learning (DRL) algorithms have been 
demonstrated to be effective in a wide range of challenging decision making and control tasks. However, these methods 
typically suffer from severe action oscillations in particular in discrete action setting, which means that agents 
select different actions within consecutive steps even though states only slightly differ. This issue is often neglected
 since the policy is usually evaluated by its cumulative rewards only. Action oscillation strongly affects the user
 experience and can even cause serious potential security menace especially in real-world domains with the main concern 
 of safety, such as autonomous driving. To this end, we introduce Policy Inertia Controller (PIC) which serves as a 
 generic plug-in framework to off-the-shelf DRL algorithms, to enables adaptive trade-off between the optimality and 
 smoothness of the learned policy in a formal way. We propose Nested Policy Iteration as a general training algorithm 
 for PIC-augmented policy which ensures monotonically non-decreasing updates under some mild conditions. Further, we 
 derive a practical DRL algorithm, namely Nested Soft Actor-Critic. Experiments on a collection of autonomous driving
  tasks and several Atari games suggest that our approach demonstrates substantial oscillation reduction in comparison 
  to a range of commonly adopted baselines with almost no performance degradation.",['cs.LG']
Micro-Attention for Micro-Expression recognition,"Micro-expression, for its high objectivity in emotion detection, has 
emerged to be a promising modality in affective computing. Recently, deep learning methods have been successfully 
introduced into the micro-expression recognition area. Whilst the higher recognition accuracy achieved, substantial 
challenges in micro-expression recognition remain. The existence of micro expression in small-local areas on face and 
limited size of available databases still constrain the recognition accuracy on such emotional facial behavior. In this
 work, to tackle such challenges, we propose a novel attention mechanism called micro-attention cooperating with 
 residual network. Micro-attention enables the network to learn to focus on facial areas of interest covering different 
 action units. Moreover, coping with small datasets, the micro-attention is designed without adding noticeable 
 parameters while a simple yet efficient transfer learning approach is together utilized to alleviate the overfitting 
 risk. With extensive experimental evaluations on three benchmarks (CASMEII, SAMM and SMIC) and post-hoc feature
  visualizations, we demonstrate the effectiveness of the proposed micro-attention and push the boundary of automatic
   recognition of micro-expression.",['cs.CV']
DeRF: Decomposed Radiance Fields,"With the advent of Neural Radiance Fields (NeRF), neural networks can now render novel
views of a 3D scene with quality that fools the human eye. Yet, generating these images is very computationally 
intensive, limiting their applicability in practical scenarios. In this paper, we propose a technique based on spatial 
decomposition capable of mitigating this issue. Our key observation is that there are diminishing returns in employing
larger (deeper and/or wider) networks. Hence, we propose to spatially decompose a scene and dedicate smaller networks 
for each decomposed part. When working together, these networks can render the whole scene. This allows us
near-constant inference time regardless of the number of decomposed parts. Moreover, we show that a Voronoi spatial 
decomposition is preferable for this purpose, as it is provably compatible with the Painter's Algorithm for efficient
and GPU-friendly rendering. Our experiments show that for real-world scenes, our method provides up to 3x more 
efficient inference than NeRF (with the same rendering quality), or an improvement of up to 1.0~dB in PSNR (for the
 same inference cost).","['cs.CV', 'cs.GR']"
Class-dependent Compression of Deep Neural Networks,"Today's deep neural networks require substantial computation
resources for their training, storage, and inference, which limits their effective use on resource-constrained devices.
Many recent research activities explore different options for compressing and optimizing deep models. On the one hand, 
in many real-world applications, we face the data imbalance challenge, i.e. when the number of labeled instances of 
one class considerably outweighs the number of labeled instances of the other class. On the other hand, applications 
may pose a class imbalance problem, i.e. higher number of false positives produced when training a model and optimizing
 its performance may be tolerable, yet the number of false negatives must stay low. The problem originates from the 
fact that some classes are more important for the application than others, e.g. detection problems in medical and 
surveillance domains. Motivated by the success of the lottery ticket hypothesis, in this paper we propose an iterative
deep model compression technique, which keeps the number of false negatives of the compressed model close to the one 
of the original model at the price of increasing the number of false positives if necessary. Our experimental 
evaluation using two benchmark data sets shows that the resulting compressed sub-networks 1) achieve up to 35% lower 
number of false negatives than the compressed model without class optimization, 2) provide an overall higher AUC_ROC 
measure, and 3) use up to 99% fewer parameters compared to the original network.","['cs.LG', 'cs.CV']"
The gap between theory and practice in function approximation with deep neural networks,"Deep learning (DL) is 
transforming industry as decision-making processes are being automated by deep neural networks (DNNs) trained on 
real-world data. Driven partly by rapidly-expanding literature on DNN approximation theory showing they can approximate 
a rich variety of functions, such tools are increasingly being considered for problems in scientific computing. Yet, 
unlike traditional algorithms in this field, little is known about DNNs from the principles of numerical analysis, e.g.,
 stability, accuracy, computational efficiency and sample complexity. In this paper we introduce a computational 
framework for examining DNNs in practice, and use it to study empirical performance with regard to these issues. We 
study performance of DNNs of different widths & depths on test functions in various dimensions, including smooth and 
piecewise smooth functions. We also compare DL against best-in-class methods for smooth function approx. based on 
compressed sensing (CS). Our main conclusion from these experiments is that there is a crucial gap between the 
approximation theory of DNNs and their practical performance, with trained DNNs performing relatively poorly on 
functions for which there are strong approximation results (e.g. smooth functions), yet performing well in comparison 
to best-in-class methods for other functions. To analyze this gap further, we provide some theoretical insights. We 
establish a practical existence theorem, asserting existence of a DNN architecture and training procedure that offers 
the same performance as CS. This establishes a key theoretical benchmark, showing the gap can be closed, albeit via a 
strategy guaranteed to perform as well as, but no better than, current best-in-class schemes. Nevertheless, it 
demonstrates the promise of practical DNN approx., by highlighting potential for better schemes through careful design 
of DNN architectures and training strategies.","['cs.LG', 'stat.ML']"
Human Action Generation with Generative Adversarial Networks,"Inspired by the recent advances in generative models, we 
introduce a human action generation model in order to generate a consecutive sequence of human motions to formulate 
novel actions. We propose a framework of an autoencoder and a generative adversarial network (GAN) to produce multiple 
and consecutive human actions conditioned on the initial state and the given class label. The proposed model is trained 
in an end-to-end fashion, where the autoencoder is jointly trained with the GAN. The model is trained on the NTU RGB+D 
dataset and we show that the proposed model can generate different styles of actions. Moreover, the model can 
successfully generate a sequence of novel actions given different action labels as conditions. The conventional human 
action prediction and generation models lack those features, which are essential for practical applications.",['cs.CV']
'''
    import io
    df = pd.read_csv(io.StringIO(data_str), sep=",")
    return df


@pytest.fixture(scope="module")
def iris_dataset():
    X, y = get_iris()
    eval_X, eval_y = X[0::3], y[0::3]
    constructor_args = {"data": eval_X, "targets": eval_y, "name": "iris_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture(scope="module")
def diabetes_dataset():
    X, y = get_diabetes_dataset()
    eval_X, eval_y = X[0::3], y[0::3]
    constructor_args = {"data": eval_X, "targets": eval_y, "name": "diabetes_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def linear_regressor_model_uri():
    X, y = get_diabetes_dataset()
    reg = sklearn.linear_model.LinearRegression()
    reg.fit(X, y)

    with azureml_mlflow.start_run() as run:
        azureml_mlflow.sklearn.log_model(reg, "reg_model")
        linear_regressor_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                             "reg_model")

    return linear_regressor_model_uri


@pytest.fixture
def multiclass_logistic_regressor_model_uri():
    X, y = get_iris()
    clf = sklearn.linear_model.LogisticRegression(max_iter=2)
    clf.fit(X, y)

    with azureml_mlflow.start_run() as run:
        azureml_mlflow.sklearn.log_model(clf, "clf_model")
        multiclass_logistic_regressor_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(
            run.info.run_id, "clf_model")

    return multiclass_logistic_regressor_model_uri


RunData = namedtuple("RunData", ["params", "metrics", "tags", "artifacts"])


def get_run_data(run_id):
    client = azureml_mlflow.tracking.MlflowClient()
    data = client.get_run(run_id).data
    tags = {k: v for k, v in data.tags.items()}
    artifacts = [f.path for f in client.list_artifacts(run_id)]
    return RunData(params=data.params, metrics=data.metrics, tags=tags, artifacts=artifacts)


def remove_blanks_20news(data, feature_column_name):
    for index, row in data.iterrows():
        data.at[index, feature_column_name] = (
            row[feature_column_name].replace("\n", " ").strip()
        )

    data = data[data[feature_column_name] != ""]

    return data


@pytest.fixture
def newsgroup_dataset():
    data = get_20newsgroup_dataset()
    data = pd.DataFrame(
        {'X': data["data"], 'y': data["target"]}
    )
    constructor_args = {"data": data, "targets": 'y', "name": "newsgroup_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    train_label_list = np.unique(data[ds._constructor_args['targets']])
    train_labels = {i: value for i, value in enumerate(train_label_list)}
    return {
        'dataset': ds,
        'train_labels': train_labels,
        'train_label_list': train_label_list
    }


@pytest.fixture
def newsgroup_dataset_text_pair():
    data = get_20newsgroup_dataset()
    data = pd.DataFrame(
        {'X1': data["data"], 'X2': data["data"], 'y': data["target"]}
    )
    constructor_args = {"data": data, "targets": 'y', "name": "newsgroup_dataset_text_pair"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def billsum_dataset():
    articles = ['''the past decades have seen tremendous success in the implementation of control schemes for the motional state of matter via light fields either in free space or in optical cavities . 
     a diversity of examples exist where the quantum regime of motion has been reached . 
     the masses span many orders of magnitude , from the microscopic atomic size systems such as atoms in optical cavities  @xcite and laser - cooled ions in ion traps  @xcite to the macroscopic level with cavity - embedded membranes  @xcite , mirrors  @xcite or levitated dielectric nano - particles  @xcite .    a common interaction hamiltonian that well approximates many quantum light 
     matter interfaces is quadrature  quadrature coupling  @xcite ; more specifically , the displacement of the mechanics is coupled directly to a quadrature of the high-@xmath0 optical field mode that can be then used as an observable for indirect position detection . adding a second mechanical system coupled to the field then allows one to engineer an effective two - particle mechanical coupling by eliminating the mediating light mode . 
     recently , an expansion to quadratic coupling has been proposed  @xcite and the investigation of dissipation - induced  @xcite , noise - induced  @xcite and remote entanglement  @xcite has been of great interest , including a scheme for sensitive force measurements  @xcite and entanglement of macroscopic oscillators  @xcite . 
     here we show that all this can be implemented in a system consisting of two particles strongly trapped in the cosine mode of a ring cavity , where the two - particle interaction is carried by sideband photons in the sine mode . 
     for deep trapping it yields the typical linearized optomechanical hamiltonian  @xcite . ''']
    summaries = [
        '''the motion of two distant trapped particles or mechanical oscillators can be strongly coupled by light modes in a high finesse optical resonator . in a two mode ring cavity geometry , trapping , cooling and coupling is implemented by the same modes . while the cosine mode provides for trapping , the sine mode facilitates ground state cooling and mediates non - local interactions . for classical point particles the centre - of - mass mode \n is strongly damped and the individual momenta get anti - correlated . \n surprisingly , quantum fluctuations induce the opposite effect of positively - correlated particle motion , which close to zero temperature generates entanglement . \n the non - classical correlations and entanglement are dissipation - induced and particularly strong after detection of a scattered photon in the sine mode . \n this allows for heralded entanglement by post - selection . \n entanglement is concurrent with squeezing of the particle distance and relative momenta while the centre - of - mass observables acquires larger uncertainties .''']
    data = pd.DataFrame({"articles": articles, "abstract": summaries})
    constructor_args = {"data": data, "targets": 'abstract', "name": "billsum_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def opus_dataset():
    books = load_dataset("opus_books", "en-fr")
    books = books["train"].train_test_split(test_size=0.1)
    source, target = 'en', 'fr'
    source_texts, target_texts = [], []
    for i in range(5):
        item = books["test"][i]
        source_texts.append(item['translation'][source])
        target_texts.append(item['translation'][target])
    data = pd.DataFrame({'X': source_texts, 'y': target_texts})
    constructor_args = {"data": data, "targets": 'y', "name": "opus_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def squad_qna_dataset():
    squad = load_dataset("squad")
    squad = squad["train"].train_test_split(test_size=0.2)
    test_dataset = squad["test"][:3]
    context, questions, answers = [], [], []
    for i in range(len(test_dataset["context"])):
        context.append(test_dataset["context"][i])
        questions.append(test_dataset["question"][i])
        answers.append(test_dataset["answers"][i]['text'][0])
    data = pd.DataFrame({'question': questions, 'context': context, 'answer': answers})
    constructor_args = {"data": data, "targets": 'answer', "name": "squad_qna_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def arxiv_dataset():
    data = get_arxiv_dataset()
    constructor_args = {"data": data[:20], "targets": 'terms', "name": "arxiv_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def multiclass_llm_model_uri():
    newsgroup_dataset = get_20newsgroup_dataset()
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=2, output_attentions=False,
                                        output_hidden_states=False,
                                        train_label_list=np.unique(newsgroup_dataset["target"]))
    misc_conf = {
        "train_label_list": np.unique(newsgroup_dataset["target"]),
        "task_type": "multiclass"
    }
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    print('Loading tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)

    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_multiclass_model", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        multiclass_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                           "llm_multiclass_model")

    return multiclass_llm_model_uri


def get_multiclass_model_class():
    """
    Defines a custom Python model class that wraps a scikit-learn estimator.
    This can be invoked within a pytest fixture to define the class in the ``__main__`` scope.
    Alternatively, it can be invoked within a module to define the class in the module's scope.
    """

    class CustomHFModel(azureml_mlflow.aml.AzureMLClassifierModel):
        def __init__(self, class_name, train_label_list):
            self.class_name = class_name
            self.train_label_list = train_label_list

        def load_context(self, context):
            super().load_context(context)
            # pylint: disable=attribute-defined-outside-init
            import os
            import transformers
            from transformers import AutoTokenizer
            from transformers import Trainer
            hf_model_class = getattr(transformers, self.class_name)
            from transformers import AutoConfig
            config = AutoConfig.from_pretrained(f"{context.artifacts['hf_model_path']}/config")
            self.model = hf_model_class.from_pretrained(f"{context.artifacts['hf_model_path']}/model", config=config)
            self.tokenizer = AutoTokenizer.from_pretrained(f"{context.artifacts['hf_model_path']}/tokenizer",
                                                           config=config)
            self.trainer = Trainer(
                model=self.model,
                tokenizer=self.tokenizer
            )
            _ = self.model.eval()

        def predict(self, context, data):
            import numpy as np
            pred = self.predict_proba(context, data)
            preds = np.argmax(pred, axis=1)
            return np.array([self.train_label_list[item] for item in preds])

        def predict_proba(self, context, data):
            from scipy.special import softmax
            max_seq_length = 128
            print(data)
            inference_data = PyTorchClassificationDatasetWrapper(data, self.train_label_list, self.tokenizer,
                                                                 max_seq_length)
            pred = self.trainer.predict(test_dataset=inference_data).predictions
            return softmax(pred, axis=1)

    return CustomHFModel


@pytest.fixture
def multiclass_llm_aml_model_uri():
    newsgroup_dataset = get_20newsgroup_dataset()

    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=2, output_attentions=False,
                                        output_hidden_states=False,
                                        train_label_list=np.unique(newsgroup_dataset["target"]))
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)

    path = "model_save_path"
    model.save_pretrained(f"{path}/model")
    tokenizer.save_pretrained(f"{path}/tokenizer")
    config.save_pretrained(f"{path}/config")

    artifacts = {
        'hf_model_path': path,
        "tokenizer_config": {
            "padding": "max_length",
            "truncation": True
        }
    }
    model_class_name = model.__class__.__name__
    wrapper = get_multiclass_model_class()(model_class_name, train_label_list=np.unique(newsgroup_dataset["target"]))
    with azureml_mlflow.start_run() as run:
        azureml_mlflow.aml.log_model('model_multiclass_class', loader_module=None, data_path=None, code_path=None,
                                     conda_env=None, aml_model=wrapper,
                                     artifacts=artifacts, registered_model_name=None,
                                     input_example=None, await_registration_for=0)

        multiclass_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                           "model_multiclass_class")
    return multiclass_llm_model_uri


def get_y_transformer(df, label_col_name):
    label_col = df[label_col_name].apply(ast.literal_eval)
    label_col = [[str(x) for x in item] for item in label_col]
    y_transformer = MultiLabelBinarizer(sparse_output=True)
    y_transformer.fit(label_col)
    return y_transformer


@pytest.fixture
def y_transformer_arxiv():
    arxiv_dataset = get_arxiv_dataset()
    label_col_name = "terms"
    return get_y_transformer(arxiv_dataset, label_col_name)


@pytest.fixture
def multilabel_llm_model_uri():
    arxiv_dataset = get_arxiv_dataset()
    label_col_name = "terms"
    y_transformer = get_y_transformer(arxiv_dataset, label_col_name)
    num_labels = len(y_transformer.classes_)

    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=num_labels, output_attentions=False,
                                        output_hidden_states=False, problem_type='multi_label_classification')
    misc_conf = {
        "train_label_list": y_transformer.classes_,
        "task_type": "multilabel",
        "multilabel": True,
        'y_transformer': y_transformer,
        "tokenizer_config": {
            "padding": "max_length",
            "truncation": True,
            "return_all_scores": True,
        }
    }
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    print('Loading tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)

    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_multilabel_model", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        multilabel_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                           "llm_multilabel_model")
    return multilabel_llm_model_uri


def _get_label_list(
        data_dir: str,
        train_ds_filename: str
):
    # Get the unique label list
    unique_labels = set()
    import os
    file_path = os.path.join(data_dir, train_ds_filename)
    with open(file_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line != "" and line != "\n":
                unique_labels.add(line.split()[-1])
    label_list = list(unique_labels)
    label_list.sort()

    return label_list


def get_connll_dataset():
    data = '''-DOCSTART- -X- -X- O

SOCCER NN B-NP O
- : O O
JAPAN NNP B-NP B-LOC
GET VB B-VP O
LUCKY NNP B-NP O
WIN NNP I-NP O
, , O O
CHINA NNP B-NP B-PER
IN IN B-PP O
SURPRISE DT B-NP O
DEFEAT NN I-NP O
. . O O

Nadim NNP B-NP B-PER
Ladki NNP I-NP I-PER

AL-AIN NNP B-NP B-LOC
, , O O
United NNP B-NP B-LOC
Arab NNP I-NP I-LOC
Emirates NNPS I-NP I-LOC
1996-12-06 CD I-NP O

Japan NNP B-NP B-LOC
began VBD B-VP O
the DT B-NP O
defence NN I-NP O
of IN B-PP O
their PRP$ B-NP O
Asian JJ I-NP B-MISC
Cup NNP I-NP I-MISC
title NN I-NP O
with IN B-PP O
a DT B-NP O
lucky JJ I-NP O
2-1 CD I-NP O
win VBP B-VP O
against IN B-PP O
Syria NNP B-NP B-LOC
in IN B-PP O
a DT B-NP O
Group NNP I-NP O
C NNP I-NP O
championship NN I-NP O
match NN I-NP O
on IN B-PP O
Friday NNP B-NP O
. . O O

But CC O O
China NNP B-NP B-LOC
saw VBD B-VP O
their PRP$ B-NP O
luck NN I-NP O
desert VB B-VP O
them PRP B-NP O
in IN B-PP O
the DT B-NP O
second NN I-NP O
match NN I-NP O
of IN B-PP O
the DT B-NP O
group NN I-NP O
, , O O
crashing VBG B-VP O
to TO B-PP O
a DT B-NP O
surprise NN I-NP O
2-0 CD I-NP O
defeat NN I-NP O
to TO B-PP O
newcomers NNS B-NP O
Uzbekistan NNP I-NP B-LOC
. . O O
'''

    # with open("tests/models/data/data_ner/test.txt", encoding='utf-8', errors='replace') as f:
    #     data = f.read()
    # labels_list = _get_label_list("models/data/data_ner", "train.txt")
    labels_list = ['B-LOC', 'B-MISC', 'B-ORG', 'B-PER', 'I-LOC', 'I-MISC', 'I-ORG', 'I-PER', 'O']
    data = data.replace("-DOCSTART- O\n\n", "")
    data = data.split("\n\n")[:50]
    all_words, all_labels = [], []
    label_included = " " in data[0].split("\n")[0]
    for item in data:
        tokens = item.split("\n")
        if label_included:
            splits = [item.split(" ") for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
            words = [item[0] for item in splits]
            labels = [item[-1] for item in splits]
        else:
            words = [item for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
            labels = ["O"] * len(words)
        all_words.append(" ".join(words))
        all_labels.append(str(labels))
    return all_words, all_labels, labels_list


@pytest.fixture
def ner_dataset():
    words, labels, _ = get_connll_dataset()
    data = pd.DataFrame({'X': words, 'y': labels})
    constructor_args = {"data": data, "targets": 'y', "name": "conll_dataset"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


# from azureml.evaluate.mlflow.aml import AMLClassifierModel
# class NERAzuremlHFWrapper(AMLClassifierModel):
#
#     def __init__(self, class_name, train_label_list):
#         self.class_name = class_name
#         self.train_label_list = train_label_list
#         self.label_map = {i: label for i, label in enumerate(train_label_list)}
#
#     def load_context(self, context):
#         import os
#         import transformers
#         from transformers import AutoTokenizer
#         from transformers import Trainer
#         hf_model_class = getattr(transformers, self.class_name)
#         from transformers import AutoConfig
#         self.model = hf_model_class.from_pretrained(f"{context.artifacts['hf_model_path']}\model")
#         print("Loaded model")
#         print('Loading tokenizer...', context.artifacts)
#         config = AutoConfig.from_pretrained(f"{context.artifacts['hf_model_path']}\config")
#         self.tokenizer = AutoTokenizer.from_pretrained(f"{context.artifacts['hf_model_path']}\\tokenizer",
#                                                        config=config)
#         self.trainer = Trainer(
#             model=self.model,
#             tokenizer=self.tokenizer
#         )
#         _ = self.model.eval()
#
#     def _align_predictions_with_proba(self, predictions, label_ids):
#         import numpy as np
#         from torch import nn
#         import scipy
#         preds = np.argmax(predictions, axis=2)
#         probas = scipy.special.softmax(predictions, axis=2)
#         pred_probas = np.amax(probas, axis=2)
#         batch_size, seq_len = preds.shape
#
#         out_label_list = [[] for _ in range(batch_size)]
#         preds_list = [[] for _ in range(batch_size)]
#         preds_proba_list = [[] for _ in range(batch_size)]
#
#         for i in range(batch_size):
#             for j in range(seq_len):
#                 if label_ids[i, j] != nn.CrossEntropyLoss().ignore_index:
#                     out_label_list[i].append(self.label_map[label_ids[i][j]])
#                     preds_list[i].append(self.label_map[preds[i][j]])
#                     preds_proba_list[i].append(pred_probas[i][j])
#         print(self.label_map, "labellll")
#         print(preds_list, out_label_list, preds_proba_list)
#         return preds_list, out_label_list, preds_proba_list
#
#     def predict(self, context, data):
#         data = DatasetWrapper(
#             data=data,
#             tokenizer=self.tokenizer,
#             labels=self.train_label_list,
#             max_seq_length=128
#         )
#         predictions, label_ids, _ = self.trainer.predict(data)
#         preds_list, _, _ = self._align_predictions_with_proba(predictions, label_ids)
#         print(preds_list)
#         return preds_list
#
#     def predict_proba(self, context, data):
#         data = DatasetWrapper(
#             data=data,
#             tokenizer=self.tokenizer,
#             labels=self.train_label_list,
#             max_seq_length=128
#         )
#         predictions, label_ids, _ = self.trainer.predict(data)
#         _, _, preds_proba_list = self._align_predictions_with_proba(predictions, label_ids)
#         print(preds_proba_list)
#         return preds_proba_list
#


@pytest.fixture
def ner_llm_model_uri():
    words, labels, labels_list = get_connll_dataset()
    model_name = 'bert-base-cased'
    num_labels = len(labels_list)
    config = AutoConfig.from_pretrained(
        model_name,
        num_labels=num_labels,
        finetuning_task="ner"
    )
    model = AutoModelForTokenClassification.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, config=config)
    misc_conf = {
        "train_label_list": labels_list,
        "task_type": "ner",
        "tokenizer_config": {
            "truncation": True,
            "padding": "max_length"
        }
    }

    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_ner_model", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        ner_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                    "llm_ner_model")
    return ner_llm_model_uri


@pytest.fixture
def summarization_llm_model_uri():
    model_name = 't5-small'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    misc_conf = {
        "task_type": "summarization",
        "tokenizer_config": {
            "truncation": True,
            "max_length": 128,
            "clean_up_tokenization_spaces": True
        },
        'model_hf_load_kwargs': {
            'torch_dtype': 'torch.bfloat16',
            'low_cpu_mem_usage': True
        }
    }
    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_summarization_mdl", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        summarization_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                              "llm_summarization_mdl")
    return summarization_llm_model_uri


@pytest.fixture
def translation_llm_model_uri():
    model_name = 't5-small'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    misc_conf = {
        "task_type": "translation_en_to_fr",
        "tokenizer_config": {
            "truncation": True,
            "max_length": 128
        }
    }
    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_translation_mdl", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        translation_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                            "llm_translation_mdl")
    return translation_llm_model_uri


@pytest.fixture
def qna_llm_model_uri():
    model_name = 'NeuML/bert-small-cord19qa'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    misc_conf = {
        "task_type": "question-answering",
        "tokenizer_config": {
            "max_answer_len": 30,
            "max_question_len": 100,
            "padding": "max_length",
            "doc_stride": 128,
            "max_seq_len": 384,
        }
    }
    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_qna_mdl", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        qna_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id, "llm_qna_mdl")
    return qna_llm_model_uri


@pytest.fixture
def wiki_mask():
    fm_data = load_dataset("rcds/wikipedia-for-mask-filling", "original_512", trust_remote_code=True)
    fm_data = fm_data["train"].train_test_split(test_size=0.2)
    fm_dataset = fm_data["test"]
    data = fm_dataset.to_pandas().sample(n=5)
    data["texts"] = data["texts"].apply(lambda x: x.replace("<mask>", "[MASK]"))
    data = data[["texts", "masks"]]
    data["masks"] = data["masks"].apply(lambda x: tuple(x))
    constructor_args = {"data": data, "targets": 'masks', "name": "wikipedia_for_fill_mask"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def text_gen_data():
    text_gen_data = load_dataset("lmqg/qg_squad", trust_remote_code=True)
    text_gen_data = text_gen_data["train"].train_test_split(test_size=0.2)
    text_gen_dataset = text_gen_data["test"]
    data = text_gen_dataset.to_pandas().sample(n=5)
    data = data[["paragraph", "sentence"]]
    constructor_args = {"data": data, "targets": 'paragraph', "name": "qg_squad"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def text_generation_llm_model_uri():
    model_name = 'distilgpt2'
    config = AutoConfig.from_pretrained(model_name)
    config.task_specific_params['text-generation']['max_length'] = 90
    model = AutoModelForCausalLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    misc_conf = {
        "task_type": "text-generation"
    }
    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_text_generation_mdl", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        text_generation_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                                "llm_text_generation_mdl")
    return text_generation_llm_model_uri


@pytest.fixture
def fill_mask_llm_model_uri():
    model_name = 'distilbert-base-uncased'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    misc_conf = {
        "task_type": "fill-mask"
    }
    with azureml_mlflow.start_run() as run:
        azureml_mlflow.hftransformers.log_model(model, "llm_fill_mask_mdl", tokenizer=tokenizer, config=config,
                                                hf_conf=misc_conf)
        fill_mask_llm_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                          "llm_fill_mask_mdl")
    return fill_mask_llm_model_uri

def read_image(image_path: str):
    """Read image from path"""
    with open(image_path, "rb") as f:
        return base64.encodebytes(f.read()).decode("utf-8")

@pytest.fixture
def fridge_object():
    dataset_path = join(dirname(__file__), "data", "image-object-detection")

    image_class_mapping = {
        "path": [
            join(dataset_path, "10.jpg"),
            join(dataset_path, "100.jpg"),
            join(dataset_path, "101.jpg"),
            join(dataset_path, "102.jpg"),
            join(dataset_path, "104.jpg"),
            join(dataset_path, "105.jpg"),
            join(dataset_path, "106.jpg"),
            join(dataset_path, "107.jpg"),
            join(dataset_path, "109.jpg"),
            join(dataset_path, "11.jpg"),
        ],
    }

    with open(join(dataset_path, "annotations.jsonl"), "r") as f:
        jsonl = f.readlines()
        image_class_mapping["label"] = []
        image_class_mapping["image_meta_info"] = []
        for line in jsonl:
            obj = json.loads(line)
            width = obj["image_details"]['width']
            height = obj["image_details"]['height']
            boxes, labels = [], []
            for ann in obj['label']:
                boxes.append([ann['topX']*width, ann['topY']*height, ann['bottomX']*width, ann['bottomY']*height])
                labels.append(ann['label'])
            
            image_class_mapping["label"].append({'boxes':boxes, 'labels':labels})
            image_class_mapping["image_meta_info"].append({"iscrowd": [0]*len(obj['label']),
                                                             "height": height,
                                                             "width": width,})


    data = pd.DataFrame.from_dict(image_class_mapping)

    data["image"] = data["path"].apply(lambda x: read_image(x))

    constructor_args = {"data": data, "targets": "label", "name": "fridge-od-tiny"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds

@pytest.fixture
def fridge_object_mask():
    dataset_path = join(dirname(__file__), "data", "image-instance-segmentation")

    image_class_mapping = {
        "path": [
            join(dataset_path, "1.jpg"),
            join(dataset_path, "103.jpg"),
            join(dataset_path, "108.jpg"),
            join(dataset_path, "112.jpg"),
            join(dataset_path, "117.jpg"),
            join(dataset_path, "121.jpg"),
            join(dataset_path, "126.jpg"),
            join(dataset_path, "15.jpg"),
            join(dataset_path, "2.jpg"),
            join(dataset_path, "24.jpg"),
        ],
    }

    with open(join(dataset_path, "annotations.jsonl"), "r") as f:
        jsonl = f.readlines()
        image_class_mapping["label"] = []
        image_class_mapping["image_meta_info"] = []
        for line in jsonl:
            obj = json.loads(line)
            width = obj["image_details"]['width']
            height = obj["image_details"]['height']
            boxes, labels, masks = [], [], []
            for ann in obj['label']:
                labels.append(ann['label'])
                for polygon in ann['polygon']:
                    for idx in range(0, len(polygon), 2):
                        polygon[idx] *= width
                        polygon[idx+1] *= height
                masks.append(pycoco_mask.frPyObjects(ann['polygon'], height, width)[0])
                if 'topX' in ann:
                    boxes.append([ann['topX']*width, ann['topY']*height, ann['bottomX']*width, ann['bottomY']*height])
                else:
                    boxes.append([0,0,1,1])
            image_class_mapping["label"].append({'boxes':boxes, 'labels':labels, "masks": masks})
            image_class_mapping["image_meta_info"].append({"iscrowd": [0]*len(obj['label']),
                                                             "height": height,
                                                             "width": width,})


    data = pd.DataFrame.from_dict(image_class_mapping)

    data["image"] = data["path"].apply(lambda x: read_image(x))

    constructor_args = {"data": data, "targets": "label", "name": "fridge-is-tiny"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds

def _install_dependencies(reqs_file):
    with open(reqs_file, "r") as f:
        for line in f.readlines():
            if line.strip() == "mlflow":
                continue
            if "azureml_evaluate_mlflow" in line.strip() or "azureml-evaluate-mlflow" in line.strip():
                continue
            if "azureml_metrics" in line.strip() or "azureml-metrics" in line.strip():
                continue
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", line.strip()])
            except Exception:
                print("Failed to install package", line)
                print("Traceback:")
                # traceback.print_exc()

@pytest.fixture
def image_od_model_uri():
    task = "image-object-detection"
    model_path = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-yolof_r50_c5_8x8_1x_coco/artifacts/pytorch_model.bin"
    config_path = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-yolof_r50_c5_8x8_1x_coco/artifacts/yolof_r50_c5_8x8_1x_coco.py"
    model_metafile = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-yolof_r50_c5_8x8_1x_coco/artifacts/model_metadata.json"
    augementation_config = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-yolof_r50_c5_8x8_1x_coco/artifacts/augmentations.yaml"
    mlflow_dir = join(
        dirname(dirname(dirname(dirname(__file__)))),
        "azureml-acft-image-components",
        "azureml",
        "acft",
        "image",
        "components",
        "finetune",
        "common",
        "mlflow",
    )
    sys.path.append(mlflow_dir)
    req_file = join(mlflow_dir, "mmdet-od-requirements.txt")
    _install_dependencies(req_file)

    from mmdet_mlflow_model_wrapper import ImagesMLFlowModelWrapper
    
    files_to_include = ['common_constants.py', 'common_utils.py', 'mmdet_mlflow_model_wrapper.py',
                    'mmdet_modules.py', 'mmdet_utils.py', 'augmentation_helper.py',
                    'custom_augmentations.py']

    code_path = [join(mlflow_dir, x) for x in files_to_include]

    with tempfile.TemporaryDirectory() as temp_dir:
        import urllib.request
        urllib.request.urlretrieve(model_path, join(temp_dir, basename(model_path)))
        urllib.request.urlretrieve(config_path, join(temp_dir, basename(config_path)))
        urllib.request.urlretrieve(model_metafile, join(temp_dir, basename(model_metafile)))
        urllib.request.urlretrieve(augementation_config, join(temp_dir, basename(augementation_config)))

        with azureml_mlflow.start_run() as run:
            artifacts_dict = {
                "config_path" : join(temp_dir, basename(config_path)),
                "weights_path" : join(temp_dir, basename(model_path)),
                "augmentations_path": join(temp_dir, basename(augementation_config)),
                "model_metadata": join(temp_dir, basename(model_metafile)),
            }
            mlflow.pyfunc.log_model(
                task,
                python_model=ImagesMLFlowModelWrapper(task),
                artifacts=artifacts_dict,
                pip_requirements=req_file,
                code_path=code_path,
            )
        mlflow_od_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(
            run.info.run_id, task
        )
    return mlflow_od_uri

@pytest.fixture
def image_is_model_uri():
    task = "image-instance-segmentation"
    model_path = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-mask-rcnn_swin-t-p4-w7_fpn_1x_coco/artifacts/pytorch_model.bin"
    config_path = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-mask-rcnn_swin-t-p4-w7_fpn_1x_coco/artifacts/mask-rcnn_swin-t-p4-w7_fpn_1x_coco.py"
    model_metafile = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-mask-rcnn_swin-t-p4-w7_fpn_1x_coco/artifacts/model_metadata.json"
    augementation_config = "https://automlcesdkdataresources.blob.core.windows.net/finetuning-image-models/MMDetection-mlflow/mmd_3x-mask-rcnn_swin-t-p4-w7_fpn_1x_coco/artifacts/augmentations.yaml"

    mlflow_dir = join(
        dirname(dirname(dirname(dirname(__file__)))),
        "azureml-acft-image-components",
        "azureml",
        "acft",
        "image",
        "components",
        "finetune",
        "common",
        "mlflow",
    )
    sys.path.append(mlflow_dir)
    req_file = join(mlflow_dir, "mmdet-is-requirements.txt")
    _install_dependencies(req_file)

    from mmdet_mlflow_model_wrapper import ImagesMLFlowModelWrapper
    
    files_to_include = ['common_constants.py', 'common_utils.py', 'mmdet_mlflow_model_wrapper.py',
                    'mmdet_modules.py', 'mmdet_utils.py', 'augmentation_helper.py',
                    'custom_augmentations.py', 'masktools.py']

    code_path = [join(mlflow_dir, x) for x in files_to_include]

    with tempfile.TemporaryDirectory() as temp_dir:
        import urllib.request
        urllib.request.urlretrieve(model_path, join(temp_dir, basename(model_path)))
        urllib.request.urlretrieve(config_path, join(temp_dir, basename(config_path)))
        urllib.request.urlretrieve(model_metafile, join(temp_dir, basename(model_metafile)))
        urllib.request.urlretrieve(augementation_config, join(temp_dir, basename(augementation_config)))

        with azureml_mlflow.start_run() as run:
            artifacts_dict = {
                "config_path" : join(temp_dir, basename(config_path)),
                "weights_path" : join(temp_dir, basename(model_path)),
                "augmentations_path": join(temp_dir, basename(augementation_config)),
                "model_metadata": join(temp_dir, basename(model_metafile)),
            }
            mlflow.pyfunc.log_model(
                task,
                python_model=ImagesMLFlowModelWrapper(task),
                artifacts=artifacts_dict,
                pip_requirements=req_file,
                code_path=code_path,
            )
        mlflow_is_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(
                    run.info.run_id, task
                )
    return mlflow_is_uri

@pytest.fixture
def fridge_multi_label():
    dataset_path = join(dirname(__file__), "data", "image-classification-multilabel")

    image_class_mapping = {
        "path": [
            join(dataset_path, "1.jpg"),
            join(dataset_path, "10.jpg"),
            join(dataset_path, "12.jpg"),
            join(dataset_path, "100.jpg"),
            join(dataset_path, "101.jpg"),
            join(dataset_path, "111.jpg"),
            join(dataset_path, "122.jpg"),
        ],
        "label": [
            '["carton"]',
            '["carton", "milk_bottle"]',
            '["carton", "milk_bottle"]',
            '["can"]',
            '["water_bottle"]',
            '["water_bottle", "carton"]',
            '["water_bottle", "milk_bottle"]',
        ],
    }

    data = pd.DataFrame.from_dict(image_class_mapping)

    data["image"] = data["path"].apply(lambda x: read_image(x))

    constructor_args = {"data": data, "targets": "label", "name": "fridge-tiny"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture(scope="module")
def diabetes_dataset_timeseries():
    _, _, X_test, y_test = get_diabetes_dataset_timeseries()
    X_test["y"] = y_test
    constructor_args = {"data": X_test, "targets": "y", "name": "diabetes_dataset_timeseries"}
    ds = EvaluationDataset(**constructor_args)
    ds._constructor_args = constructor_args
    return ds


@pytest.fixture
def forecaster_model_uri():
    X_train, y_train, _, _ = get_diabetes_dataset_timeseries()
    ts_config = {
        TimeSeries.TIME_COLUMN_NAME: 'date',
        TimeSeries.GRAIN_COLUMN_NAMES: None,
        TimeSeries.MAX_HORIZON: 7,
        TimeSeriesInternal.DROP_NA: True,
    }
    featurization_config = FeaturizationConfig()
    (
        forecasting_pipeline,
        ts_config,
        lookback_removed,
        time_index_non_holiday_features
    ) = _ml_engine.suggest_featurizers_timeseries(
        X_train,
        y_train,
        featurization_config,
        ts_config,
        TimeSeriesPipelineType.FULL,
        y_transformer=None
    )

    ts_transformer = TimeSeriesTransformer(
        forecasting_pipeline,
        TimeSeriesPipelineType.FULL,
        featurization_config,
        time_index_non_holiday_features,
        lookback_removed,
        **ts_config
    )
    X_train = ts_transformer.fit_transform(X_train, y_train)
    y_train = X_train.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
    estimator = sklearn.linear_model.LinearRegression()

    estimator.fit(X_train, y_train)
    model = Pipeline([('ts_transformer', ts_transformer),
                      ('estimator', estimator)])

    stdev = list(np.arange(1, ts_config[TimeSeries.MAX_HORIZON] + 1))
    fw = ForecastingPipelineWrapper(
        pipeline=model, stddev=stdev)

    with azureml_mlflow.start_run() as run:
        azureml_mlflow.sklearn.log_model(fw, "reg_model")
        linear_regressor_model_uri = azureml_mlflow.tracking.artifact_utils.get_artifact_uri(run.info.run_id,
                                                                                             "reg_model")
    return linear_regressor_model_uri
