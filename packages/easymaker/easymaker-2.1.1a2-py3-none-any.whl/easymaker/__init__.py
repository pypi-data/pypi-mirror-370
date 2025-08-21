from importlib import metadata

from easymaker import initializer
from easymaker.batch_inference import batch_inference
from easymaker.common import constants
from easymaker.common.parameter import Parameter
from easymaker.common.storage import Nas
from easymaker.endpoint import endpoint
from easymaker.endpoint.components import EndpointModelResource, ResourceOptionDetail
from easymaker.experiment import experiment
from easymaker.log import logger
from easymaker.model import model
from easymaker.model_evaluation import model_evaluation
from easymaker.pipeline import pipeline, pipeline_recurring_run, pipeline_run
from easymaker.sample import sample
from easymaker.storage import objectstorage
from easymaker.training import hyperparameter_tuning, training
from easymaker.training.components import Dataset, HyperparameterSpec, Metric

__version__ = metadata.version("easymaker")

easymaker_config = initializer.global_config

init = easymaker_config.init

logger = logger.Logger

Nas = Nas

Experiment = experiment.Experiment

Training = training.Training
Parameter = Parameter
Dataset = Dataset

HyperparameterTuning = hyperparameter_tuning.HyperparameterTuning
HyperparameterSpec = HyperparameterSpec
Metric = Metric

Model = model.Model

Endpoint = endpoint.Endpoint
EndpointStage = endpoint.EndpointStage
EndpointModel = endpoint.EndpointModel
EndpointModelResource = EndpointModelResource
ResourceOptionDetail = ResourceOptionDetail

BatchInference = batch_inference.BatchInference

Pipeline = pipeline.Pipeline

PipelineRun = pipeline_run.PipelineRun

PipelineRecurringRun = pipeline_recurring_run.PipelineRecurringRun

ModelEvaluation = model_evaluation.ModelEvaluation

download = objectstorage.download

upload = objectstorage.upload

ObjectStorage = objectstorage.ObjectStorage

TENSORFLOW = "TENSORFLOW"
PYTORCH = "PYTORCH"
SCIKIT_LEARN = "SCIKIT_LEARN"
HUGGING_FACE = "HUGGING_FACE"
CLASSIFICATION = "CLASSIFICATION"
REGRESSION = "REGRESSION"

HYPERPARAMETER_TYPE_CODE = constants.HYPERPARAMETER_TYPE_CODE
OBJECTIVE_TYPE_CODE = constants.OBJECTIVE_TYPE_CODE
TUNING_STRATEGY = constants.TUNING_STRATEGY
EARLY_STOPPING_ALGORITHM = constants.EARLY_STOPPING_ALGORITHM
INPUT_DATA_TYPE_CODE = constants.INPUT_DATA_TYPE_CODE
SCALE_METRIC_CODE = constants.SCALE_METRIC_CODE

__all__ = (
    "init",
    "Training",
)
