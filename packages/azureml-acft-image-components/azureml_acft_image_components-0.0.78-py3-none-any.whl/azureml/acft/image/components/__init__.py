# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image Components package."""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import os
import sys

# adding mlflow folder path here to be used by(finetune, evaluation and unittests)
sys.path.append(os.path.join(os.path.dirname(__file__), "finetune", "common", "mlflow"))
