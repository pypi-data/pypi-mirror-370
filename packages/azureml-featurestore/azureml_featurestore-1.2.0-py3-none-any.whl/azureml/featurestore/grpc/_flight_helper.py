# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=global-statement

import datetime
import json
import os
import random
import subprocess
import sys
import tempfile
import threading
import time
import warnings
from typing import List

import pyarrow.flight as flight
from azureml.featurestore._utils._constants import ON_THE_FLY_FEATURE_SETS
from azureml.featurestore._utils.error_constants import ONLINE_MATERIALIZATION_DISABLED
from azureml.featurestore.contracts.feature import Feature

__AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY = "AZUREML_FEATURESTORE_SERVICE_ENDPOINT"

__INITIALIZER_MUTEX = threading.Lock()

__FEATURESTORE_SERVICE_PROCESS = None

__FEATURE_RETRIEVAL_CLIENT = None
__FEATURE_RETRIEVAL_CLIENT_MUTEX = threading.Lock()

__auth_token_scopes = [
    "https://management.core.windows.net/.default",
    "https://management.azure.com/.default",
    "https://storage.azure.com/.default",
]


def _get_feature_retrieval_client():
    global __FEATURE_RETRIEVAL_CLIENT

    if not __FEATURE_RETRIEVAL_CLIENT:
        with __FEATURE_RETRIEVAL_CLIENT_MUTEX:
            if not __FEATURE_RETRIEVAL_CLIENT:
                if __AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY not in os.environ:
                    from ._inline_feature_retrieval_client import InlineFeatureRetrievalClient

                    warnings.warn(
                        f'The environment variable "{__AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY}" is not defined, did'
                        " you forget to run `Featurestore.initialize(...)`? Falling back to inline feature retrieval -"
                        " this feature is experimental, and may not be supported in future releases."
                    )
                    __FEATURE_RETRIEVAL_CLIENT = InlineFeatureRetrievalClient()
                else:
                    from ._flight_feature_retrieval_client import FlightFeatureRetrievalClient

                    endpoint = os.environ[__AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY]
                    __FEATURE_RETRIEVAL_CLIENT = FlightFeatureRetrievalClient(endpoint)

    return __FEATURE_RETRIEVAL_CLIENT


def initialize(features: List[Feature], credential, force, **kwargs): # pylint: disable=too-many-locals
    global __FEATURESTORE_SERVICE_PROCESS

    for feature in features:
        if not feature.feature_set_reference.materialization_settings.online_enabled:
            raise Exception(
                ONLINE_MATERIALIZATION_DISABLED.format(
                    feature.feature_set_reference.name, feature.feature_set_reference.version
                )
            )

        if (
            feature.feature_set_reference.online_store.connection_name
            != feature.feature_set_reference.online_store_connection_name
        ):
            from azureml.featurestore._utils.error_constants import ONLINE_CONNECTION_NAME_MISMATCH

            from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

            raise ValidationException(
                message=ONLINE_CONNECTION_NAME_MISMATCH,
                no_personal_data_message=ONLINE_CONNECTION_NAME_MISMATCH,
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

    with __INITIALIZER_MUTEX:
        if __AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY in os.environ and not force:
            raise AssertionError(
                f'The environment variable "{__AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY}" is already defined.'
                " To override it, invoke `Featurestore.initialize(features, credential, force=True)`"
            )

        if __FEATURESTORE_SERVICE_PROCESS is not None and not force:
            raise AssertionError(
                "A featurestore retrieval service instance is already running."
                " To reinitialize it, invoke `Featurestore.initialize(features, credential, force=True)`"
            )

        shutdown()

        logdir = os.path.join(tempfile.gettempdir(), "azureml-logs", "featurestore")
        timestamp = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d.%H%M%S")
        os.makedirs(logdir, exist_ok=True)

        server_file = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "_flight_feature_retrieval_server.py")
        )

        proc = subprocess.Popen(
            [sys.executable, server_file],
            stdin=subprocess.PIPE,
            stdout=open(os.path.join(logdir, f"retrieval-server.{timestamp}.out"), "w"),
            stderr=open(os.path.join(logdir, f"retrieval-server.{timestamp}.err"), "w"),
        )

        if proc.poll() is not None:
            raise AssertionError(
                f"Failed to start feature store server - process exited with status code {proc.returncode}."
            )

        # Server process is alive. Write initialization parameters.
        tokens = {}
        for scope in __auth_token_scopes:
            token = credential.get_token(scope)
            tokens[scope] = {"token": token.token, "expires_on": token.expires_on}

        on_the_fly_feature_sets = kwargs.get(ON_THE_FLY_FEATURE_SETS, [])

        port = random.randint(5000, 10000)
        port_find_attempts = 20
        while _is_port_in_use(port):
            port = random.randint(5000, 10000)
            port_find_attempts -= 1

            if port_find_attempts <= 0:
                raise AssertionError("Failed to find an open port for the feature retrieval service.")

        location = f"grpc+tcp://localhost:{port}"

        initialization_params = {
            "location": location,
            "features": [f.uri for f in features],
            "tokens": tokens,
            "on_the_fly_feature_sets": [f.uri for f in on_the_fly_feature_sets],
            "redis_database_overrides": kwargs.get("redis_database_overrides", {}),
        }

        proc.stdin.write(json.dumps(initialization_params).encode("utf-8") + os.linesep.encode("utf-8"))
        proc.stdin.flush()

        wait_until = time.time() + kwargs.get("timeout", 120)
        while True:
            time.sleep(2)
            try:
                connection = flight.connect(initialization_params["location"])
                connection.wait_for_available()
                connection.close()
                break
            except:  # pylint: disable=bare-except
                pass

            if time.time() > wait_until:
                with open(os.path.join(logdir, f"retrieval-server.{timestamp}.err"), "r", encoding="utf-8") as f:
                    raise AssertionError("Failed to start the feature retrieval service: " + os.linesep + f.read())

        os.environ[__AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY] = initialization_params["location"]
        __FEATURESTORE_SERVICE_PROCESS = proc
        __FEATURE_RETRIEVAL_CLIENT = None  # noqa


def is_initialized():
    return __AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY in os.environ


def shutdown():
    global __FEATURESTORE_SERVICE_PROCESS

    if __FEATURESTORE_SERVICE_PROCESS is not None:
        with __INITIALIZER_MUTEX:
            if __FEATURESTORE_SERVICE_PROCESS is not None:
                __FEATURESTORE_SERVICE_PROCESS.stdin.close()
                __FEATURESTORE_SERVICE_PROCESS.wait()
                __FEATURESTORE_SERVICE_PROCESS = None
                del os.environ[__AZUREML_FEATURESTORE_SERVICE_ENDPOINT_KEY]


def get_online_features(feature_list, observation_df, **kwargs):
    client = _get_feature_retrieval_client()
    return client.get_online_features(feature_list, observation_df, **kwargs)


def get_offline_features(feature_list, observation_df, timestamp_column):
    raise NotImplementedError()


def _is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
