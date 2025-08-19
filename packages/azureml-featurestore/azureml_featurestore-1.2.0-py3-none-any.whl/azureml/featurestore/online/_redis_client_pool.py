# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re

__REDIS_CACHE_ARM_ID_FORMAT = \
    re.compile(
        r"^\/subscriptions\/[^/]+\/resourceGroups\/[^/]+\/providers\/Microsoft\.Cache\/Redis\/[^/]+$",
        re.IGNORECASE
    )

__REDIS_ENTERPRISE_DATABASE_ARM_ID_FORMAT = \
    re.compile(
        r"^\/subscriptions\/[^/]+\/resourceGroups/[^/]+\/providers\/Microsoft\.Cache\/RedisEnterprise\/[^/]+\/databases/[^/]+$", # pylint: disable=line-too-long
        re.IGNORECASE
    )


def _deconstruct_arm_id(arm_id):
    '''
    Supports two formats:
    1. /subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Cache/Redis/{redis_instance_name} # pylint: disable=line-too-long
    2. /subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Cache/RedisEnterprise/{redis_instance_name}/databases/{database_name} # pylint: disable=line-too-long
    '''

    parts = arm_id.split("/")
    if __REDIS_CACHE_ARM_ID_FORMAT.match(arm_id) is not None:
        return parts[7], parts[2], parts[4], parts[8], None

    if __REDIS_ENTERPRISE_DATABASE_ARM_ID_FORMAT.match(arm_id) is not None:
        return parts[7], parts[2], parts[4], parts[8], parts[10]

    raise ValueError(f"Invalid ARM ID format: {arm_id}. Expected format: "
                        "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/"
                        "Microsoft.Cache/Redis/{redis_instance_name} or "
                        "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/"
                        "Microsoft.Cache/RedisEnterprise/{redis_instance_name}/databases/{database_name}")


def _get_redis_connection_string(arm_id, credential):
    resource_type, subscription_id, resource_group, resource_name, database_name = _deconstruct_arm_id(arm_id)

    if resource_type.lower() == "redisenterprise":
        from azure.mgmt.redisenterprise import RedisEnterpriseManagementClient # pylint: disable=no-name-in-module,import-error

        management_client = RedisEnterpriseManagementClient(credential=credential, subscription_id=subscription_id)
        instance_response = management_client.redis_enterprise.get(resource_group, resource_name)
        database_response = management_client.databases.get(resource_group, resource_name, database_name)
        keys_response = management_client.databases.list_keys(resource_group, resource_name, database_name)

        instance_dict = instance_response.as_dict()
        database_dict = database_response.as_dict()
        keys_dict = keys_response.as_dict()

        host = instance_dict["host_name"]
        port = database_dict["port"]
        password = keys_dict["primary_key"]
        return (f"rediss://:{password}@{host}:{port}/0", True)

    if resource_type.lower() == "redis":
        from azure.mgmt.redis import RedisManagementClient

        management_client = RedisManagementClient(credential=credential, subscription_id=subscription_id)
        instance_response = management_client.redis.get(resource_group, resource_name)
        keys_response = management_client.redis.list_keys(resource_group, resource_name)

        instance_dict = instance_response.as_dict()
        keys_dict = keys_response.as_dict()

        host = instance_dict["host_name"]
        port = instance_dict["ssl_port"]
        password = keys_dict["primary_key"]

        clustering_enabled = ("shard_count" in instance_dict and\
                              instance_dict["shard_count"] is not None and\
                              instance_dict["shard_count"] > 1)

        return (f"rediss://:{password}@{host}:{port}/0", clustering_enabled)

    raise ValueError(f"Invalid resource type: {resource_type}. Expected 'Redis' or 'RedisEnterprise'.")


def _get_redis_client(redis_arm_id, credential):
    connection_string, clustering_enabled = _get_redis_connection_string(redis_arm_id, credential)
    if clustering_enabled:
        from redis.cluster import RedisCluster as Redis
    else:
        from redis import Redis

    return Redis.from_url(connection_string)


class RedisClientPool(object):
    def __init__(self, redis_resource_ids, credential):
        self.clients = {
            redis_resource_id: _get_redis_client(redis_resource_id, credential)
            for redis_resource_id in redis_resource_ids
        }

    def get_client(self, redis_resource_id):
        return self.clients[redis_resource_id]
