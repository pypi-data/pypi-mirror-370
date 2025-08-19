# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
mlflow utilities
"""

from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent
BASE_PATH = Path(__file__).resolve().parent.parent
print(BASE_PATH)


def prepare_mlflow_preprocess():
    print(f"\n\nChaitanya: {BASE_PATH}\n\n")
    preprocess_file = str(Path(FILE_PATH, "preprocess.py"))
    acft_code_path = BASE_PATH
    return [preprocess_file, acft_code_path]


def restructure_mlflow_acft_code(mlflow_model_path):
    preprocess_file = Path(mlflow_model_path, "code", "preprocess.py")
    if preprocess_file.is_file():
        hf_contrib_folder_name = Path(mlflow_model_path, "code", BASE_PATH.stem)
        new_code_path = Path(mlflow_model_path, "code", "acft")
        new_code_path.parent.mkdir(parents=True, exist_ok=True)
        hf_contrib_folder_name.rename(new_code_path)
        init_file = Path(new_code_path, "__init__.py")
        with open(init_file, "a+") as fp:
            fp.write("\nfrom . import task_factory\n")
