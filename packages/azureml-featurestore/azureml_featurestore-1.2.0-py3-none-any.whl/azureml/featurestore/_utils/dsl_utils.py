# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
from typing import List

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from jinja2 import Template

from azureml.featurestore._utils.error_constants import FEATURE_NAME_NOT_FOUND_DSL


def _to_feathr_join_config(
    timestamp_col_name: str,
    timestamp_col_format: str,
    feature_names: List[str],
    join_keys: List[str],
    start_time: str,
    end_time: str,
):
    feathr_join_tm = Template(
        # TODO: obsDataTimeSettings timeFormat should be configurable
        """
settings: {
    observationDataTimeSettings: {
        absoluteTimeRange: {
            startTime: "{{start_time}}"
            endTime: "{{end_time}}"
            timeFormat: "yyyy-MM-dd HH:mm:ss"
        }
    },
    joinTimeSettings: {
        timestampColumn: {
            def: "{{timestamp_column}}"
            format: "{{timestamp_format}}"
        }
    }
}
features: [
    {
        key: [{{join_keys}}],
        featureList: [{{feature_names}}]
    }
]
"""
    )
    feathr_join_string = feathr_join_tm.render(
        timestamp_column=timestamp_col_name,
        timestamp_format=timestamp_col_format,
        feature_names=", ".join(feature_names),
        join_keys=", ".join(join_keys),
        start_time=start_time,
        end_time=end_time,
    )

    return feathr_join_string


def _to_feathr_fset_config(feature_sets: List):
    feathr_config_tm = Template(
        """
anchors: {
    {%- for feature_set in feature_sets %}
        {{feature_set._to_feathr_config("anchor")}}
    {%- endfor %}
}

sources: {
    {%- for feature_set in feature_sets %}
        {{feature_set._to_feathr_config("source")}}
    {%- endfor %}
}
"""
    )
    feathr_config_string = feathr_config_tm.render(feature_sets=feature_sets)

    return feathr_config_string


def _to_feathr_anchor_config(feature_set_or_spec, join_keys: List[str]):
    anchor_tm = Template(
        """
"{{feature_set.name + "_" + feature_set.version + "_anchor"}}": {
    source: {{feature_set.name + "_" + feature_set.version + "_source"}}
    key: [{{join_keys}}]
    features: {
        {%- for feature in feature_set.feature_transformation.transformation_expressions %}
            {{feature._to_feathr_config()}}
        {%- endfor %}
    }
}
"""
    )
    anchor_string = anchor_tm.render(feature_set=feature_set_or_spec, join_keys=",".join(join_keys))
    return anchor_string


def _to_feathr_source_config(feature_set_or_spec):
    source_name = feature_set_or_spec.name + "_" + feature_set_or_spec.version + "_source"
    source_string = feature_set_or_spec.source._to_feathr_config(source_name)  # pylint: disable=protected-access
    return source_string


def _to_feathr_shim_config(source_df, feature_set_or_spec, features: List[str] = None, is_materialized: bool = False):
    from azureml.featurestore._utils._constants import COL_OBSERVATION_ENTITY_TIMESTAMP
    from pyspark.sql.session import SparkSession

    spark = SparkSession.builder.getOrCreate()
    gateway = spark.sparkContext._gateway
    Tuple6 = gateway.jvm.scala.Tuple6

    join_keys = [idx_col.name for idx_col in feature_set_or_spec.get_index_columns()]
    join_keys.sort()

    source_delay = (
        feature_set_or_spec.source.source_delay.to_minutes()
        if feature_set_or_spec.source.source_delay is not None
        else 0
    )
    temporal_join_lookback = (
        feature_set_or_spec.temporal_join_lookback.to_minutes()
        if feature_set_or_spec.temporal_join_lookback is not None
        else -1
    )

    if not features:
        features = [feature.name for feature in feature_set_or_spec.features]

    config = []
    if is_materialized:
        for feature_name in features:
            config.append(
                {
                    "name": feature_name,
                    "sourceColumn": feature_name,
                    "aggType": "DUMMY",
                    "windowSizeInMinute": 0,
                }
            )
    else:
        feature_look_up = set(features)
        transformation_look_up = set()
        for transformation_expression in feature_set_or_spec.feature_transformation.transformation_expressions:
            transformation_look_up.add(transformation_expression.feature_name)
            if transformation_expression.feature_name in feature_look_up:
                config.append(
                    {
                        "name": transformation_expression.feature_name,
                        "sourceColumn": transformation_expression.source_column,
                        "aggType": transformation_expression.aggregation.value.upper(),
                        "windowSizeInMinute": transformation_expression.window.to_minutes(),
                    }
                )
        transformation_look_up.update(join_keys)
        transformation_look_up.update(feature_set_or_spec.get_timestamp_column()[0])

        if not feature_look_up.issubset(transformation_look_up):
            raise ValidationException(
                message=FEATURE_NAME_NOT_FOUND_DSL.format(feature_look_up.difference(transformation_look_up)),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=FEATURE_NAME_NOT_FOUND_DSL,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    return Tuple6(
        source_df._jdf,
        COL_OBSERVATION_ENTITY_TIMESTAMP,
        ",".join(join_keys),
        json.dumps(config),
        str(source_delay),
        str(temporal_join_lookback),
    )
