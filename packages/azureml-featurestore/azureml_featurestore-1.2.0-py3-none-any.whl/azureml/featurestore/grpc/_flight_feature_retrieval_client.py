# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=client-accepts-api-version-keyword,missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs,client-method-missing-type-annotations

from typing import List

import pyarrow
import pyarrow.flight as flight
from azureml.featurestore._utils._constants import ON_THE_FLY_ENTITY_KEY
from azureml.featurestore.contracts.feature import Feature


class FlightFeatureRetrievalClient:
    def __init__(self, uri):
        self.location = flight.Location(uri)
        self.connection = flight.connect(self.location)
        self.connection.wait_for_available()

    def get_online_features(self, features: List[Feature], observation_df: pyarrow.Table, **kwargs) -> pyarrow.Table:
        # on_the_fly_entities is an optional serialized string kwarg passed by user
        on_the_fly_entities = kwargs.pop(ON_THE_FLY_ENTITY_KEY, None)
        if on_the_fly_entities:
            descriptor = flight.FlightDescriptor.for_path(
                "online", ON_THE_FLY_ENTITY_KEY, on_the_fly_entities, *[f.uri for f in features]
            )
        else:
            descriptor = flight.FlightDescriptor.for_path("online", *[f.uri for f in features])
        writer, reader = self.connection.do_exchange(descriptor)

        writer.begin(observation_df.schema)
        writer.write(observation_df)
        writer.done_writing()

        features_df = reader.read_all()
        writer.close()

        return features_df

    # pylint: disable=unused-argument,unused-variable,no-self-use
    def get_offline_features(
        self, features: List[Feature], observation_df: "pyspark.sql.DataFrame", timestamp_column: str
    ):
        descriptor = flight.FlightDescriptor.for_path(f"offline:{timestamp_column}", *[f.uri for f in features])  # noqa
        raise NotImplementedError()
