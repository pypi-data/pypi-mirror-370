# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC


class AbstractFeatureStore(ABC):
    """Represents the base class for all featurestores.

    You should not work with this class directly. To create a featurestore, use the ``register`` method
    of the FeatureStore class.

    :param name: The featurestore name.
    :type name: str
    :param featurestore_type: The featurestore type, for example, "Managed".
    :type featurestore_type: str
    """

    def __init__(self, name, featurestore_type):
        """Class AbstractDatastore constructor.

        This is a base class and users should not be creating this class using the constructor.

        :param name: The featurestore name.
        :type name: str
        :param featurestore_type: The featurestore type, for example, "Managed".
        :type featurestore_type: str
        """
        self._name = name
        self._featurestore_type = featurestore_type
