# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-outer-name
# cspell: ignore nbytes

import json
import queue
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pyarrow.flight
from azure.ai.ml._telemetry.activity import ActivityType, log_activity
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationException
from azure.core.credentials import AccessToken

from azureml.featurestore._utils._constants import ON_THE_FLY_ENTITY_KEY, PACKAGE_NAME
from azureml.featurestore._utils.utils import _build_logger
from azureml.featurestore.online._online_feature_getter_v3 import OnlineFeatureGetterV3

ops_logger = _build_logger(__name__)


class AuthTokenCredential(object):
    def __init__(self, token_dict):
        self.tokens = token_dict

    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        if len(scopes) != 1:
            msg = "This credential requires exactly one scope per token request."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.IDENTITY,
                error_category=ErrorCategory.USER_ERROR,
            )

        token = self.tokens[scopes[0]]
        return AccessToken(token["token"], token["expires_on"])


class FlightFeatureRetrievalServer(pyarrow.flight.FlightServerBase):
    def __init__(self, location, credential, feature_uris, on_the_fly_feature_set_uris, redis_database_overrides):
        self.log_queue = queue.Queue()
        self.logger = ops_logger

        with log_activity(
            self.logger.package_logger,
            f"{PACKAGE_NAME}->FlightFeatureRetrievalServer->Init",
            ActivityType.INTERNALCALL,
            {"feature_count": len(feature_uris)},
        ) as activity:
            print("Initializing feature getter...", flush=True)
            self.online_feature_getter = OnlineFeatureGetterV3(
                credential,
                feature_uris,
                on_the_fly_feature_set_uris,
                redis_database_overrides=redis_database_overrides
            )
            print("Finished feature getter initialization! Starting server...", flush=True)
            super(FlightFeatureRetrievalServer, self).__init__(location)
            print("Started gRPC server!\n----\n", flush=True)
            activity.activity_info["redis_database_count"] = len(self.online_feature_getter.redis_clients)

    def do_exchange(self, context, descriptor, reader, writer):  # pylint: disable=unused-argument
        """Write data to a flight.
        Applications should override this method to implement their
        own behavior. The default method raises a NotImplementedError.
        Parameters
        ----------
        context : ServerCallContext
            Common contextual information.
        descriptor : FlightDescriptor
            The descriptor for the flight provided by the client.
        reader : MetadataRecordBatchReader
            A reader for data uploaded by the client.
        writer : MetadataRecordBatchWriter
            A writer to send responses to the client.
        """
        try:
            # Get feature list from descriptor
            scenario = descriptor.path[0].decode("utf-8")

            if scenario == "online":
                feature_getter = self.online_feature_getter.get_online_features
            elif scenario.startswith("offline:"):
                raise NotImplementedError("Offline feature data retrieval over grpc is not yet supported.")
            else:
                raise NotImplementedError(f"Unsupported scenario: {scenario}")

            if descriptor.path[1].decode("utf-8") == ON_THE_FLY_ENTITY_KEY:
                on_the_fly_entities = descriptor.path[2].decode("utf-8")
                feature_uris = [path.decode("utf-8") for path in descriptor.path[3:]]
            else:
                on_the_fly_entities = None
                feature_uris = [path.decode("utf-8") for path in descriptor.path[1:]]

            read_start = time.perf_counter()
            # Get observations dataframe from request
            observation_df = reader.read_all()
            read_latency = time.perf_counter() - read_start

            retrieval_start = time.perf_counter()
            features_df = feature_getter(feature_uris, observation_df, on_the_fly_entities=on_the_fly_entities)
            retrieval_latency = time.perf_counter() - retrieval_start

            writer.begin(features_df.schema)
            writer.write_table(features_df)
            writer.close()
        except Exception as ex:
            _log_failure(self.logger, ex)
            raise
        else:
            # cspell:disable-next-line
            self.log_queue.put(
                (features_df.num_rows,
                 features_df.num_columns,
                 features_df.nbytes,
                 read_latency,
                 retrieval_latency)
            )


def _log_success(logger, num_rows, num_cols, num_bytes, read_latency, retrieval_latency):
    """Log a successful feature data retrieval event.
    This method should *never* throw."""
    try:
        print(
            f"{PACKAGE_NAME}->FlightFeatureRetrievalServer->DoExchange->Success "
            f"[feature_data_rows: {num_rows}; feature_data_columns: {num_cols};"
            f" feature_data_bytes: {num_bytes}; observation_read_latency: {read_latency:4f};"
            f" feature_retrieval_latency: {retrieval_latency:4f}]",
            flush=True)

        with log_activity(
            logger.package_logger,
            f"{PACKAGE_NAME}->FlightFeatureRetrievalServer->DoExchange->Success",
            ActivityType.INTERNALCALL,
            {
                "feature_data_rows": num_rows,
                "feature_data_columns": num_cols,
                "feature_data_bytes": num_bytes,
                "observation_read_latency": read_latency,
                "feature_retrieval_latency": retrieval_latency,
            },
        ):
            pass
    except:  # pylint: disable=bare-except
        pass


def _log_failure(logger, exception):
    """Log an unsuccessful feature data retrieval event.
    This method should *never* throw."""
    try:
        if isinstance(exception, MlException):
            log_activity(
                logger.package_logger,
                f"{PACKAGE_NAME}->FlightFeatureRetrievalServer->DoExchange->Error",
                ActivityType.INTERNALCALL,
                {
                    "exception": f"{type(exception).__name__}: {exception.no_personal_data_message}",
                },
            )
        else:
            log_activity(
                logger.package_logger,
                f"{PACKAGE_NAME}->FlightFeatureRetrievalServer->DoExchange->Error",
                ActivityType.INTERNALCALL,
                {
                    "exception": f"{type(exception).__name__}: {exception}",
                },
            )
    except:  # pylint: disable=bare-except
        pass


def sentinel(server):
    # Wait as long as stdin is open.
    for line in sys.stdin:  # pylint: disable=unused-variable
        pass

    # stdin was closed - the parent process is likely dead.
    # Emit telemetry to appinsights
    with log_activity(
        ops_logger.package_logger, f"{PACKAGE_NAME}->FlightFeatureRetrievalServer->Shutdown", ActivityType.INTERNALCALL
    ):
        pass

    # Flush logs
    sys.stdout.flush()
    sys.stderr.flush()

    # Shut the server down
    server.shutdown()
    print("\n----\nServer shuts down.", flush=True)

    # Signal the log worker to exit
    server.log_queue.put(None)


def log_worker(server):
    while True:
        log = (
            server.log_queue.get()
        )  # Wait here until an item is available; Since it is a blocking operation, no try-catch block is needed.
        if log is None:
            break
        num_rows, num_cols, num_bytes, read_latency, retrieval_latency = log
        _log_success(server.logger, num_rows, num_cols, num_bytes, read_latency, retrieval_latency)

    print("Log queue has been exhausted.", flush=True)


def main(location, credential, feature_uris, on_the_fly_feature_sets, redis_database_overrides):
    server = FlightFeatureRetrievalServer(
        location, credential, feature_uris, on_the_fly_feature_sets, redis_database_overrides)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(sentinel, server)
        executor.submit(log_worker, server)

    server.serve()


if __name__ == "__main__":
    # Read initialization params from stdin
    initialization_params = json.loads(sys.stdin.readline())
    location = initialization_params["location"]
    feature_uris = initialization_params["features"]
    credential = AuthTokenCredential(initialization_params["tokens"])
    on_the_fly_feature_sets = initialization_params["on_the_fly_feature_sets"]
    redis_database_overrides = initialization_params.get("redis_database_overrides", {})

    main(location, credential, feature_uris, on_the_fly_feature_sets, redis_database_overrides)
