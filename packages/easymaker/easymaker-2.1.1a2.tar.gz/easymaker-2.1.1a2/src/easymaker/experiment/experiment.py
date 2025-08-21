import easymaker
from easymaker.api.request_body import ExperimentCreateBody
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel


class Experiment(EasyMakerBaseModel):
    experiment_id: str | None = None
    experiment_name: str | None = None
    experiment_status_code: str | None = None
    tensorboard_access_uri: str | None = None

    def create(
        self,
        experiment_name: str,
        description: str | None = None,
        wait: bool | None = True,
    ):
        try:
            experiment = Experiment.get_by_name(experiment_name)
            print(f"[AI EasyMaker] Experiment '{experiment_name}' already exists. experiment_id: {experiment.id}")

            return experiment
        except ValueError:
            pass

        response = easymaker.easymaker_config.api_sender.create_experiment(
            ExperimentCreateBody(
                experiment_name=experiment_name,
                description=description,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Experiment create request complete. experiment_id: {self.experiment_id}")
        if wait:
            self.wait()

        return self
