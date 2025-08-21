import argparse
import os
import pathlib
import sys

import papermill as pm

# ipynb 파일 위치의 parameters 디렉토리에 있는 동일한 이름의 yaml 파일을 파라미터로 사용한다.

current_file = pathlib.Path(__file__)
current_dir = current_file.parent.resolve()
os.makedirs(current_dir / "out", exist_ok=True)


def execute_notebook(args, notebook_name: str, parameters: dict = None):
    if parameters is None:
        parameters = {}
    parameters.update(vars(args))
    pm.execute_notebook(
        input_path=str(current_dir / f"{notebook_name}.ipynb"),
        output_path=str(current_dir / f"out/{notebook_name}.ipynb"),
        parameters=parameters,
        progress_bar=False,
        stdout_file=sys.stdout,
        stderr_file=sys.stderr,
    )


def main(args):
    execute_notebook(
        args,
        "create_model_from_uri",
        {
            "model_type_code": "PYTORCH",
            "model_upload_uri": "obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_33634be0ec1340f3aa966a610eea77f0/easymaker/model/tensorflow",
            "model_name": "modelnbpy",
        },
    )


def get_arg_parser():
    parser = argparse.ArgumentParser(description="Model Notebook Runner")

    parser.add_argument("--profile", dest="profile", type=str)
    parser.add_argument("--region", dest="region", type=str)
    parser.add_argument("--app_key", dest="app_key", type=str)
    parser.add_argument("--access_token", dest="access_token", type=str)

    return parser


if __name__ == "__main__":
    parser = get_arg_parser()
    args, unknown = parser.parse_known_args()
    main(args)
