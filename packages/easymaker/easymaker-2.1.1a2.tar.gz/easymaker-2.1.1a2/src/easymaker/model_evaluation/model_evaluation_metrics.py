from typing import Any

from pydantic import Field

from easymaker.common.base_model.easymaker_base_model import BaseModel


class RegressionEvaluationMetrics(BaseModel):
    root_mean_squared_error: float | None
    mean_absolute_error: float | None
    mean_absolute_percentage_error: float | None
    r_squared: float | None = Field(default=None, validation_alias="rsquared")
    root_mean_squared_log_error: float | None


class AnnotationSpec(BaseModel):
    id_: str = Field(alias="id")
    display_name: str | None

    @property
    def id(self) -> str:
        return self.id_


class ConfusionMatrix(BaseModel):
    annotation_specs: list[AnnotationSpec] | None
    rows: list[Any] | None


class ConfidenceMetric(BaseModel):
    confidenceThreshold: float | None
    recall: float | None
    precision: float | None
    false_positive_rate: float | None
    f1_score: float | None
    f1_score_macro: float | None
    confusion_matrix: ConfusionMatrix | None


class ClassificationEvaluationMetrics(BaseModel):
    au_prc: float | None
    au_roc: float | None
    log_loss: float | None
    confidence_metrics: list[ConfidenceMetric] | None
