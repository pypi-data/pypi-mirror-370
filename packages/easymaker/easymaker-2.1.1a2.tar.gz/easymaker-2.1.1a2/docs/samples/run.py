import logging
import os
import pathlib
import subprocess

import yaml

logging.basicConfig(level=logging.INFO)


current_file = pathlib.Path(__file__)
current_dir = current_file.parent.resolve()


def main():
    with open(current_dir / "config.yaml") as f:
        config = yaml.safe_load(f)

    for root, _dirs, files in os.walk(current_dir):
        for file in files:
            if root == str(current_dir) and file == "run.py":
                continue

            if file == "run.py":
                print(f"Running {root}/run.py")
                config_str = " ".join([f"--{k} {v}" for k, v in config.items()])
                subprocess.run(f"python {root}/run.py {config_str}", shell=True)


if __name__ == "__main__":
    main()
