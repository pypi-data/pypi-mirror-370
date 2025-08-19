# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

def materialize_online(feature_set, dataframe_to_store, materialization_version=None):
    if hasattr(feature_set, "schema_version"):
        if feature_set.schema_version is None:
            # If the feature set has no schema version, we assume it is version 1
            featureset_schema_version = 1
        else:
            featureset_schema_version = feature_set.schema_version
    else:
        # If the feature set does not have a schema version, we assume it is version 1
        featureset_schema_version = 1

    if featureset_schema_version == 1:
        from azureml.featurestore.online._online_feature_materialization.v1.materialize import \
            materialize_online as materialize_online_v1
        return materialize_online_v1(
            feature_set, dataframe_to_store, materialization_version
        )

    if featureset_schema_version == 2:
        from azureml.featurestore.online._online_feature_materialization.v2.materialize import \
            materialize_online as materialize_online_v2
        return materialize_online_v2(
            feature_set, dataframe_to_store, materialization_version
        )

    raise ValueError(
        f"Unsupported feature set schema version: {featureset_schema_version}"
    )
