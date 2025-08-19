# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: disable

from azureml.featurestore._version import VERSION

# constants
CREATE_TIMESTAMP_COLUMN = "create_timestamp"
SYS_CREATE_TIMESTAMP_COLUMN = "sys_create_timestamp"
SYS_UPDATE_TIMESTAMP_COLUMN = "sys_update_timestamp"

PARTITION_COLUMN = "partition"

MAXIMUM_MATERIALIZATION_RETRY_TIMES = 3

FEATURE_SET_SPEC_YAML_FILENAME = "FeatureSetSpec.yaml"
FEATURE_SET_SPEC_YAML_FILENAME_FALLBACK = "FeaturesetSpec.yaml"
FEATURE_SET_SPEC_FOLDERNAME = "spec"

FEATURE_RETRIEVAL_SPEC_YAML_FILENAME = "feature_retrieval_spec.yaml"

AZUREML_URI_PATTERNS = r"azureml://"
CLOUD_URI_PATTERNS = r"^https?://"
STORAGE_URI_PATTERNS = r"adl://|wasbs?://|abfss?://"

DATALAKE_URI_REGEX = r"([a-zA-Z0-9_\-]+)@([a-zA-Z0-9_\-]+).dfs.core.windows.net/([a-zA-Z0-9_/\-]+)"

PACKAGE_NAME = "{}/{}".format("azureml-featurestore", VERSION)

OFFLINE_STORE_CONNECTION_NAME_KEY = "offlineStoreConnectionName"
ONLINE_STORE_CONNECTION_NAME_KEY = "onlineStoreConnectionName"

OFFLINE_MATERIALIZATION_VERSION_KEY = "offlineMaterializationVersion"
ONLINE_MATERIALIZATION_VERSION_KEY = "onlineMaterializationVersion"

# regions
CHINA_EAST2 = "chinaeast2"
CHINA_NORTH3 = "chinanorth3"
US_GOV_VIRGINIA = "usgovvirginia"
US_GOV_ARIZONA = "usgovarizona"
US_SEC_EAST = "usseceast"
US_SEC_WEST = "ussecwest"
US_NAT_EAST = "usnateast"
US_NAT_WEST = "usnatwest"

# metrics
NUMBER_OF_OFFLINE_MATERIALIZED_ROWS = "numberOfOfflineMaterializedRows"
NUMBER_OF_ONLINE_MATERIALIZED_ROWS = "numberOfOnlineMaterializedRows"
NUMBER_OF_SOURCE_ROWS = "numberOfSourceRows"

# offline store url
CHINA_ADLS_GEN2_URL_FORMAT = "abfs://{}@{}.dfs.core.chinacloudapi.cn"
GLOBAL_ADLS_GEN2_URL_FORMAT = "abfs://{}@{}.dfs.core.windows.net"
US_GOV_ADLS_GEN2_URL_FORMAT = "abfs://{}@{}.dfs.core.usgovcloudapi.net"
US_SEC_ADLS_GEN2_URL_FORMAT = "abfs://{}@{}.dfs.core.microsoft.scloud"
US_NAT_ADLS_GEN2_URL_FORMAT = "abfs://{}@{}.dfs.core.eaglex.ic.gov"

# offline query
DSL_QUERY_MODE_KEY = "dsl_query_mode"
QUERY_MODE_DSL = "dsl"
QUERY_MODE_DSL_SHIM = "dsl_shim"
QUERY_MODE_FEAST = "point_at_time_feast"

QUERY_APPLY_SOURCE_DELAY_KEY = "apply_source_delay"
QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY = "apply_temporal_join_lookback"

COL_OBSERVATION_FEATURE_SET_UNIQUE_ROW_ID = "{fstore_guid}_{fset_name}_{fset_version}_entity_row_unique_id"

COL_OBSERVATION_ENTITY_TIMESTAMP = "entity_timestamp"
TIME_STAMP_FORMAT_ARG = "timestamp_format"

# online materialization
TIME_TO_LIVE = "time_to_live"
ON_THE_FLY_FEATURE_SETS = "on_the_fly_feature_sets"
AZUREML_ONLINE_MATERIALIZATION_MAX_ATTEMPTS = "AZUREML_ONLINE_MATERIALIZATION_MAX_ATTEMPTS"
AZUREML_ONLINE_MATERIALIZATION_BATCH_SIZE = "AZUREML_ONLINE_MATERIALIZATION_BATCH_SIZE"
AZUREML_ONLINE_MATERIALIZATION_EVALS_PER_TASK_PER_SECOND = "AZUREML_ONLINE_MATERIALIZATION_EVALS_PER_TASK_PER_SECOND"

# online retrieval
AZUREML_FEATURESTORE_DEBUG_ENVVAR = "AZUREML_FEATURESTORE_DEBUG"
NETWORK_LATENCY_COLUMN_NAME = "azureml_featurestore_network_latency"
IS_IN_CI_PIPELINE = "IS_IN_CI_PIPELINE"
ONLINE_ON_THE_FLY = "online_on_the_fly"
ON_THE_FLY_ENTITY_KEY = "on_the_fly_entities"
FEATURE_STORE_ONLINE_INFERENCE = "feature-store-online-inference"

DEPRECATED_FEATURE_START_NAME = "featureWindowStartDateTime"
DEPRECATED_FEATURE_END_NAME = "featureWindowEndDateTime"

AML_FEATURESTORE_EVENTLOG_ENABLED = "amlfeaturestore.eventLog.enabled"
AZURE_SERVICE = "AZURE_SERVICE"
AZURE_SERVICE_VALUE = "microsoft.projectarcadia"

# AML Spark Environment Variables
AML_SPARK_SUBSCRIPTION_ENVVAR = "AZUREML_ARM_SUBSCRIPTION"
AML_SPARK_RESOURCEGROUP_ENVVAR = "AZUREML_ARM_RESOURCEGROUP"
AML_SPARK_WORKSPACE_ENVVAR = "AZUREML_ARM_WORKSPACE_NAME"
