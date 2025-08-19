# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os

__AZUREML_PRIVATE_FEATURES_ENVVAR = "AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"
__AZUREML_TEST_PIPELINE_ENVVAR = "IS_IN_CI_PIPELINE"


def _is_private_preview_enabled():
    return os.getenv(__AZUREML_PRIVATE_FEATURES_ENVVAR) in ["True", "true", True] or os.getenv(
        __AZUREML_TEST_PIPELINE_ENVVAR
    ) in ["True", "true", True]
