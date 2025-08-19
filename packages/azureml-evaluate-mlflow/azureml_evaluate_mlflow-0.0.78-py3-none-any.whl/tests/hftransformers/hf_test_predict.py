from azureml.evaluate.mlflow.hftransformers._task_based_predictors import ClassificationPredictor


def predict(data, task, model, tokenizer, config, **kwargs):
    predictor = ClassificationPredictor(task_type=task, model=model, tokenizer=tokenizer, config=config)
    return predictor.predict(data, **kwargs)
