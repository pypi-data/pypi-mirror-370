import datetime
import os
import random
import string
import tempfile
from textwrap import dedent
from uuid import uuid4

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    FeatureStore,
    MaterializationStore,
    ComputeInstance,
    DataColumn,
    DataColumnType,
    FeatureStoreEntity,
    FeatureSet,
    FeatureSetSpecification,
    MaterializationSettings,
    MaterializationComputeResource,
    NetworkSettings,
    RecurrenceTrigger,
    Workspace,
)

from azure.identity import AzureCliCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.redis.models import RedisCreateParameters, Sku, SkuFamily, SkuName
from azure.mgmt.resource import ResourceManagementClient


def provision_redis_database():
    subscription = os.getenv('AZUREML_ARM_SUBSCRIPTION')
    resource_group = os.getenv('AZUREML_ARM_RESOURCEGROUP')
    feature_store = os.getenv('AZUREML_ARM_FEATURESTORE_NAME')
    location = os.getenv('AZUREML_ARM_REGION')

    redis_resource_name = ''.join([c for c in feature_store if c in string.ascii_letters + string.digits][:14]) + ''.join(random.choices('0123456789', k=10))
    
    management_client = RedisManagementClient(AzureCliCredential(), subscription)
    return management_client.redis.begin_create(
        resource_group_name=resource_group,
        name=redis_resource_name,
        parameters=RedisCreateParameters(
            location=location,
            sku=Sku(name=SkuName.PREMIUM, family=SkuFamily.P, capacity=2),
            subnet_id=f'/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/VirtualNetworks/vnet-1/subnets/default'
        )).result()


def provision_materialization_identity():
    subscription = os.getenv('AZUREML_ARM_SUBSCRIPTION')
    resource_group = os.getenv('AZUREML_ARM_RESOURCEGROUP')
    feature_store = os.getenv('AZUREML_ARM_FEATURESTORE_NAME')
    location = os.getenv('AZUREML_ARM_REGION')

    client = ManagedServiceIdentityClient(credential=AzureCliCredential(), subscription_id=subscription)
    msi_resource_name = ''.join([c for c in feature_store if c in string.ascii_letters + string.digits][:14]) + ''.join(random.choices('0123456789', k=10))
   
    return client.user_assigned_identities.create_or_update(
        resource_group_name=resource_group,
        resource_name=msi_resource_name,
        parameters={ 'location': location },
    )


def provision_feature_store(uai):
    subscription = os.getenv('AZUREML_ARM_SUBSCRIPTION')
    resource_group = os.getenv('AZUREML_ARM_RESOURCEGROUP')
    feature_store = os.getenv('AZUREML_ARM_FEATURESTORE_NAME')
    location = os.getenv('AZUREML_ARM_REGION')

    materialization_identity = ManagedIdentityConfiguration(
        client_id=uai.client_id,
        principal_id=uai.principal_id,
        resource_id=uai.id,
    )
    
    print('Provisioning redis resource...')
    redis_resource = provision_redis_database()
    print(redis_resource)
    print()

    online_store = MaterializationStore(type='redis', target=redis_resource.id)

    fs = FeatureStore(
        name=feature_store,
        online_store=online_store,
        materialization_identity=materialization_identity,
        location=location
    )
    
    ml_client = MLClient(AzureCliCredential(), subscription, resource_group, feature_store)

    print('Provisioning feature store...')
    print(ml_client.feature_stores.begin_create(fs, update_dependent_resources=True).result())
    print()

    columns = [DataColumn(name='accountID', type=DataColumnType.string)]
    fs_entity = FeatureStoreEntity(name='account', version='1', index_columns=columns)
    print('Provisioning feature store entity...')
    print(ml_client.feature_store_entities.begin_create_or_update(fs_entity).result())
    print()

    with tempfile.TemporaryDirectory() as tmpdirname:
        with open(os.path.join(tmpdirname, 'FeatureSetSpec.yaml'), 'w', encoding='utf-8') as fset_spec:
            fset_spec.write(dedent('''\
                $schema: http://azureml/sdk-2-0/FeatureSetSpec.json

                source:
                  type: parquet
                  path: wasbs://data@azuremlexampledata.blob.core.windows.net/feature-store-prp/datasources/accounts-precalculated/*.parquet
                  timestamp_column:
                    name: timestamp
                
                features:
                - name: accountAge
                  type: integer
                - name: accountAnnualSpend
                  type: double
                - name: accountMonthlySpend
                  type: double
                - name: accountCountry
                  type: string
                - name: isUserRegistered
                  type: boolean
                - name: numPaymentRejectsThisMonth
                  type: integer
                - name: embeddingVector
                  type: binary
                - name: embeddingVectorStr
                  type: string
                
                index_columns:
                - name: accountID
                  type: string
            '''))

        fset = FeatureSet(
            name='accounts',
            version='1',
            entities=['azureml:account:1'],
            specification=FeatureSetSpecification(path=tmpdirname),
            stage='Development',
            materialization_settings=MaterializationSettings(
                schedule=RecurrenceTrigger(start_time=datetime.datetime.now(), frequency='Hour', interval=12),
                offline_enabled=False,
                online_enabled=True,
                resource=MaterializationComputeResource(instance_type='standard_e8s_v3'),
                spark_configuration={
                    'spark.driver.cores': 2,
                    'spark.driver.memory': '4g',
                    'spark.executor.cores': 4,
                    'spark.executor.memory': '4g',
                    'spark.executor.instances': 5,
                    },
            ),
        )

        print('Provisioning feature set...')
        print(ml_client.feature_sets.begin_create_or_update(fset).result())
        print()

    authorization_client = AuthorizationManagementClient(credential=AzureCliCredential(),subscription_id=subscription,api_version='2018-01-01-preview')
    print('Assigning roles to MSI...')
    print(
      authorization_client.role_assignments.create(
        f'/subscriptions/{subscription}/resourceGroups/{resource_group}',
        uuid4(),
        {
          'role_definition_id': f'/subscriptions/{subscription}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c',
          'principal_id': uai.principal_id,
        }
      )
    )
    print()


def provision_ml_workspace(uai):
    subscription = os.getenv('AZUREML_ARM_SUBSCRIPTION')
    resource_group = os.getenv('AZUREML_ARM_RESOURCEGROUP')
    ml_workspace = os.getenv('AZUREML_ARM_WORKSPACE_NAME')
    location = os.getenv('AZUREML_ARM_REGION')

    ws = Workspace(
        name=ml_workspace,
        location=location,
        display_name='Online featurestore perftesting workspace',
        hbi_workspace=False
    )

    ml_client = MLClient(AzureCliCredential(), subscription, resource_group, ml_workspace)
    print('Provisioning ml workspace...')
    print(ml_client.workspaces.begin_create(ws).result())
    print()

    ci_basic = ComputeInstance(
      name='retrieval-compute',
      size="STANDARD_F8s_v2",
      network_settings=NetworkSettings(vnet_name='vnet-1', subnet='default'),
      identity=IdentityConfiguration(type='user_assigned', user_assigned_identities=[ManagedIdentityConfiguration(
        client_id=uai.client_id,
        principal_id=uai.principal_id,
        resource_id=uai.id,
      )]))

    print('Provisioning compute...')
    print(ml_client.compute.begin_create_or_update(ci_basic).result())
    print()


def provision_resource_group():
    subscription = os.getenv('AZUREML_ARM_SUBSCRIPTION')
    resource_group = os.getenv('AZUREML_ARM_RESOURCEGROUP')
    location = os.getenv('AZUREML_ARM_REGION')

    resource_client = ResourceManagementClient(AzureCliCredential(), subscription)
    print('Provisioning resource group...')
    print(resource_client.resource_groups.create_or_update(resource_group, { 'location': location }))
    print()

    network_client = NetworkManagementClient(AzureCliCredential(), subscription)
    print('Provisioning vnet...')
    print(
      network_client.virtual_networks.begin_create_or_update(
        resource_group,
        'vnet-1',
        {
            'location': location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }).result()
    )
    print(
      network_client.subnets.begin_create_or_update(
        resource_group,
        'vnet-1',
        'default',
        {'address_prefix': '10.0.0.0/24'}).result()
    )
    print()


if __name__ == '__main__':
    provision_resource_group()
    
    print('Provisioning managed identity...')
    uai = provision_materialization_identity()
    print(uai)
    print()

    provision_ml_workspace(uai)
    provision_feature_store(uai)
