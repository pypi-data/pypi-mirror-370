# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
mlflow utilities
"""

from acft import task_factory # type: ignore

import logging
_logger = logging.getLogger(__name__)

from pathlib import Path
MLFLOW_MODEL_PATH = Path(__file__).resolve().parent.parent
MLFLOW_TOKENIZER_PATH = Path(MLFLOW_MODEL_PATH, "data", "tokenizer")

def preprocess(data):
    _logger.log(2, "Test message")
    print("Preprocessing with script", data)
    task_name = "NamedEntityRecognition"
    runner = task_factory.get_task_runner(task_name)()
    data = runner.run_preprocess_for_infer(**{"data": data, "tokenizer_path": MLFLOW_TOKENIZER_PATH})
    return data
