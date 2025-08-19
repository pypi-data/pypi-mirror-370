import base64
import datetime
import itertools
from mlflow.entities import Metric
from mlflow.tracking import MlflowClient
import numpy
import os
import pyarrow
from pyspark.sql import SparkSession
import random
import redis
from scipy.stats import norm
import shutil
import string
import tempfile
import time

from azure.identity import ManagedIdentityCredential
from azure.mgmt.redis import RedisManagementClient
from azureml.core import Experiment, Run
from azureml.featurestore import FeatureStoreClient, init_online_lookup, get_online_features, shutdown_online_lookup
from azureml.featurestore.online._online_feature_materialization import materialize_online


_COUNTRIES = ['AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BV', 'BR', 'IO', 'VG', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'BQ', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC', 'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'SZ', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'TF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT', 'HM', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP', 'JE', 'JO', 'KZ', 'KE', 'KI', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MO', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'KP', 'MK', 'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU', 'RW', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'KR', 'SS', 'ES', 'LK', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'SD', 'SR', 'SJ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UM', 'VI', 'UG', 'UA', 'AE', 'GB', 'US', 'UY', 'UZ', 'VU', 'VA', 'VE', 'VN', 'WF', 'EH', 'YE', 'ZM', 'ZW']


def _generate_feature_rows():
    seen_account_ids = set()
    rows = []
    for _ in range(10000):
        while True:
            account_id = 'A' + ''.join(random.choices(string.digits, k=9))
            if account_id not in seen_account_ids:
                seen_account_ids.add(account_id)
                break

        # integer features
        account_age = random.randint(10, 1000)
        num_payment_rejects_this_month = random.randint(0, 8)

        # floating point features
        account_annual_spend = random.uniform(0, 8000)
        account_monthly_spend = random.uniform(0, 2000)

        # string features
        account_country = random.choice(_COUNTRIES)

        # boolean features
        is_user_registered = random.choice([True, False])

        # binary features
        embedding_data = numpy.random.uniform(-1.0, 1.0, 256).tobytes()

        rows.append({
            'accountID': account_id,
            'timestamp': (datetime.datetime(2020, 1, 1) + datetime.timedelta(random.randint(0, 500))).strftime('%Y-%m-%d %H:%M:%S'),
            'accountAge': account_age,
            'accountAnnualSpend': account_annual_spend,
            'accountMonthlySpend': account_monthly_spend,
            'accountCountry': account_country,
            'isUserRegistered': is_user_registered,
            'numPaymentRejectsThisMonth': num_payment_rejects_this_month,
            'embeddingVector': embedding_data,
            'embeddingVectorStr': base64.b85encode(embedding_data).decode('utf-8') })
    
    return rows


def _get_feature_set():
    subscription = os.getenv("AZUREML_ARM_SUBSCRIPTION")
    resource_group = os.getenv("AZUREML_ARM_RESOURCEGROUP")
    feature_store = os.getenv("AZUREML_ARM_FEATURESTORE_NAME")

    cred = ManagedIdentityCredential(client_id=os.getenv('AZUREML_ARM_MSI_CLIENT_ID'))

    fs_client = FeatureStoreClient(credential=cred, subscription_id=subscription, resource_group_name=resource_group, name=feature_store)
    return fs_client.feature_sets.get('accounts', '1')


def _create_redis_client(redis_arm_id):
    parts = redis_arm_id.split("/")
    redis_subscription = parts[2]
    redis_resource_group = parts[4]
    redis_resource_name = parts[-1]

    management_client = RedisManagementClient(credential=ManagedIdentityCredential(client_id=os.getenv('AZUREML_ARM_MSI_CLIENT_ID')), subscription_id=redis_subscription)
    instance_response = management_client.redis.get(redis_resource_group, redis_resource_name)
    keys_response = management_client.redis.list_keys(redis_resource_group, redis_resource_name)

    host = instance_response.host_name
    port = instance_response.ssl_port
    password = keys_response.primary_key
    return redis.Redis.from_url(f"rediss://:{password}@{host}:{port}/0")


def measure(feature_set, feature_rows):
    feature_data_map = {row['accountID']: row for row in feature_rows}

    latencies = {
        'single_observation_single_feature': {
            'wall_elapsed_seconds': [],
            'network_elapsed_seconds': [],
            'overhead_seconds': [],
        },
        'single_observation_single_feature_large_binary': {
            'wall_elapsed_seconds': [],
            'network_elapsed_seconds': [],
            'overhead_seconds': [],
        },
        'single_observation_multi_feature': {
            'wall_elapsed_seconds': [],
            'network_elapsed_seconds': [],
            'overhead_seconds': [],
        },
        'multi_observation_single_feature': {
            'wall_elapsed_seconds': [],
            'network_elapsed_seconds': [],
            'overhead_seconds': [],
        },
        'multi_observation_single_feature_large_binary': {
            'wall_elapsed_seconds': [],
            'network_elapsed_seconds': [],
            'overhead_seconds': [],
        },
        'multi_observation_multi_feature': {
            'wall_elapsed_seconds': [],
            'network_elapsed_seconds': [],
            'overhead_seconds': [],
        },
    }

    account_ids = list(feature_data_map.keys())

    # burn some lookups to reach steady state
    for _ in range(32):
        observation_df = pyarrow.Table.from_pydict({'accountID': random.sample(account_ids, 100)})
        features = get_online_features(feature_set.features[:-2] + [feature_set.features[-1]], observation_df)

    # profile perf for single-obeservation, single-feature retrieval.
    for _ in range(4096):
        feature_name = random.choice([ 'accountAge', 'accountAnnualSpend', 'accountMonthlySpend', 'accountCountry', 'isUserRegistered', 'numPaymentRejectsThisMonth' ])
        account_id = random.choice(account_ids)

        observation_df = observation_df = pyarrow.Table.from_pydict({'accountID': [ account_id ]})
        
        start_time = time.perf_counter()
        result_dataframe = get_online_features([feature_set.get_feature(feature_name)], observation_df)
        wall_elapsed = time.perf_counter() - start_time
        
        expected_value = feature_data_map[account_id][feature_name]
        actual_value = result_dataframe[feature_name][0].as_py()
        try:
            assert expected_value == actual_value
        except AssertionError:
            print(f'{account_id}:{feature_name} | {expected_value} | {actual_value}')
            raise

        redis_latency = result_dataframe['azureml_featurestore_network_latency'][0].as_py()
        overhead = wall_elapsed - redis_latency

        latencies['single_observation_single_feature']['wall_elapsed_seconds'].append(wall_elapsed)
        latencies['single_observation_single_feature']['network_elapsed_seconds'].append(redis_latency)
        latencies['single_observation_single_feature']['overhead_seconds'].append(overhead)

    # profile perf for single-observation single-feature retrieval, retrieving large binary feature data.
    for _ in range(4096):
        feature_name = 'embeddingVector'
        account_id = random.choice(account_ids)

        observation_df = observation_df = pyarrow.Table.from_pydict({'accountID': [ account_id ]})
        
        start_time = time.perf_counter()
        result_dataframe = get_online_features([feature_set.get_feature(feature_name)], observation_df)
        wall_elapsed = time.perf_counter() - start_time
        
        expected_value = feature_data_map[account_id][feature_name]
        actual_value = result_dataframe[feature_name][0].as_py()
        try:
            assert expected_value == actual_value
        except AssertionError:
            print(f'{account_id}:{feature_name} | {expected_value} | {actual_value}')
            raise

        assert expected_value == actual_value

        redis_latency = result_dataframe['azureml_featurestore_network_latency'][0].as_py()
        overhead = wall_elapsed - redis_latency

        latencies['single_observation_single_feature_large_binary']['wall_elapsed_seconds'].append(wall_elapsed)
        latencies['single_observation_single_feature_large_binary']['network_elapsed_seconds'].append(redis_latency)
        latencies['single_observation_single_feature_large_binary']['overhead_seconds'].append(overhead)

    # profile perf for single-observation, multi-feature retrieval, retrieving 4 features at a time.
    for _ in range(4096):
        feature_names = random.sample([ 'accountAge', 'accountAnnualSpend', 'accountMonthlySpend', 'accountCountry', 'isUserRegistered', 'numPaymentRejectsThisMonth' ], 4)
        account_id = random.choice(account_ids)

        observation_df = observation_df = pyarrow.Table.from_pydict({'accountID': [ account_id ]})
        
        start_time = time.perf_counter()
        result_dataframe = get_online_features([feature_set.get_feature(feature_name) for feature_name in feature_names], observation_df)
        wall_elapsed = time.perf_counter() - start_time
        
        for feature_name in feature_names:
            expected_value = feature_data_map[account_id][feature_name]
            actual_value = result_dataframe[feature_name][0].as_py()
            assert expected_value == actual_value

        redis_latency = result_dataframe['azureml_featurestore_network_latency'][0].as_py()
        overhead = wall_elapsed - redis_latency

        latencies['single_observation_multi_feature']['wall_elapsed_seconds'].append(wall_elapsed)
        latencies['single_observation_multi_feature']['network_elapsed_seconds'].append(redis_latency)
        latencies['single_observation_multi_feature']['overhead_seconds'].append(overhead)
    

    # profile perf for multi-obeservation, single-feature retrieval, 100 observations at a time.
    for _ in range(4096):
        feature_name = random.choice([ 'accountAge', 'accountAnnualSpend', 'accountMonthlySpend', 'accountCountry', 'isUserRegistered', 'numPaymentRejectsThisMonth' ])
        selected_account_ids = random.choices(account_ids, k=100)

        observation_df = observation_df = pyarrow.Table.from_pydict({'accountID': selected_account_ids})
        
        start_time = time.perf_counter()
        result_dataframe = get_online_features([feature_set.get_feature(feature_name)], observation_df)
        wall_elapsed = time.perf_counter() - start_time

        for account_id, result_container in zip(selected_account_ids, result_dataframe[feature_name]):
            expected_value = feature_data_map[account_id][feature_name]
            actual_value = result_container.as_py()
            try:
                assert expected_value == actual_value
            except AssertionError:
                print(f'{account_id}:{feature_name} | {expected_value} | {actual_value}')
                raise

        redis_latency = result_dataframe['azureml_featurestore_network_latency'][0].as_py()
        overhead = wall_elapsed - redis_latency

        latencies['multi_observation_single_feature']['wall_elapsed_seconds'].append(wall_elapsed)
        latencies['multi_observation_single_feature']['network_elapsed_seconds'].append(redis_latency)
        latencies['multi_observation_single_feature']['overhead_seconds'].append(overhead)

    # profile perf for multi-observation single-feature retrieval, retrieving large binary feature data for 100 observations at a time.
    for _ in range(4096):
        feature_name = 'embeddingVector'
        selected_account_ids = random.choices(account_ids, k=100)

        observation_df = observation_df = pyarrow.Table.from_pydict({'accountID': selected_account_ids})
        
        start_time = time.perf_counter()
        result_dataframe = get_online_features([feature_set.get_feature(feature_name)], observation_df)
        wall_elapsed = time.perf_counter() - start_time
        
        for account_id, result_container in zip(selected_account_ids, result_dataframe[feature_name]):
            expected_value = feature_data_map[account_id][feature_name]
            actual_value = result_container.as_py()
            try:
                assert expected_value == actual_value
            except AssertionError:
                print(f'{account_id}:{feature_name} | {expected_value} | {actual_value}')
                raise

        redis_latency = result_dataframe['azureml_featurestore_network_latency'][0].as_py()
        overhead = wall_elapsed - redis_latency

        latencies['multi_observation_single_feature_large_binary']['wall_elapsed_seconds'].append(wall_elapsed)
        latencies['multi_observation_single_feature_large_binary']['network_elapsed_seconds'].append(redis_latency)
        latencies['multi_observation_single_feature_large_binary']['overhead_seconds'].append(overhead)

    # profile perf for single-observation, multi-feature retrieval, retrieving 4 features at a time.
    for _ in range(4096):
        feature_names = random.sample([ 'accountAge', 'accountAnnualSpend', 'accountMonthlySpend', 'accountCountry', 'isUserRegistered', 'numPaymentRejectsThisMonth' ], 4)
        selected_account_ids = random.choices(account_ids, k=100)

        observation_df = observation_df = pyarrow.Table.from_pydict({'accountID': selected_account_ids})
        
        start_time = time.perf_counter()
        result_dataframe = get_online_features([feature_set.get_feature(feature_name) for feature_name in feature_names], observation_df)
        wall_elapsed = time.perf_counter() - start_time

        for feature_name in feature_names:
            for account_id, result_container in zip(selected_account_ids, result_dataframe[feature_name]):
                expected_value = feature_data_map[account_id][feature_name]
                actual_value = result_container.as_py()
                try:
                    assert expected_value == actual_value
                except AssertionError:
                    print(f'{account_id}:{feature_name} | {expected_value} | {actual_value}')
                    raise

        redis_latency = result_dataframe['azureml_featurestore_network_latency'][0].as_py()
        overhead = wall_elapsed - redis_latency

        latencies['multi_observation_multi_feature']['wall_elapsed_seconds'].append(wall_elapsed)
        latencies['multi_observation_multi_feature']['network_elapsed_seconds'].append(redis_latency)
        latencies['multi_observation_multi_feature']['overhead_seconds'].append(overhead)


    return latencies


def quantilize(latency_data):
    quantilized_data = dict()
    
    points = numpy.linspace(0, 1, 101)

    for scenario in latency_data:
        quantilized_data[scenario] = dict()
        for metric in latency_data[scenario]:
            quantiles = numpy.quantile(latency_data[scenario][metric], points)
            quantilized_data[scenario][metric] = quantiles
    
    return quantilized_data


def log_metrics(quantile_data):
    run_id = os.getenv('AZUREML_RUN_ID')
    client = MlflowClient()
    for scenario in quantile_data:
        for metric in quantile_data[scenario]:
            client.log_batch(run_id, metrics=[Metric(key=f'{scenario}.{metric}.percentile', value=value, timestamp=int(time.time() * 1000), step=i) for i, value in enumerate(quantile_data[scenario][metric])])


def test_stats(quantile_data):
    run = Run.get_context()
    if run.experiment.name == 'reference':
        return

    points_of_interest = [25, 50, 75, 90, 95]
    reference_experiment = Experiment(run.experiment.workspace, 'reference')
    reference_runs = list(itertools.islice(Run.list(reference_experiment, status='Completed'), 32))

    result = True
    for scenario in quantile_data:
        for metric in quantile_data[scenario]:
            metricses = [reference_run.get_metrics(f'{scenario}.{metric}.percentile') for reference_run in reference_runs]
            metrics_arr = numpy.array([metrics_dict[f'{scenario}.{metric}.percentile'] for metrics_dict in metricses])
            means = metrics_arr.mean(axis=0)
            stds = metrics_arr.std(axis=0)

            for point_of_interest in points_of_interest:
                cdf = norm.cdf(quantile_data[scenario][metric][point_of_interest], means[point_of_interest], stds[point_of_interest])
                if (1 - cdf) < 0.05:
                    print(f'!! Latency for {scenario}.{metric}.P{point_of_interest} is outside the acceptable range (p={1-cdf}).')
                    print(f'Reference latency is [{means[point_of_interest] - 2 * stds[point_of_interest]}, {means[point_of_interest] + 2 * stds[point_of_interest]}] with 95% confidence, measured P{point_of_interest} latency was {quantile_data[scenario][metric][point_of_interest]}.')
                    result = False
            
            print()
    
    if not result:
        raise AssertionError('There is a high likelihood that one or more retrieval performance metrics have regressed.')


if __name__ == '__main__':
    # generate the feature dataframe to test with
    print('Synthesizing feature data...', end='', flush=True)
    feature_rows = _generate_feature_rows()
    print(' done.')
    
    # get a reference to the target feature set
    print('Getting feature set reference...', end='', flush=True)
    feature_set = _get_feature_set()
    print(' done.')

    # initialize a redis client and clear the database
    print('Flushing redis database...', end='', flush=True)
    redis_client = _create_redis_client(feature_set.online_store.target)
    redis_client.flushall()
    print(' done.')

    # materialize data to redis
    print('Materializing feature data to redis...', end='', flush=True)
    import azure.ai.ml.identity
    from functools import partial
    azure.ai.ml.identity.AzureMLOnBehalfOfCredential = partial(ManagedIdentityCredential, client_id=os.getenv('AZUREML_ARM_MSI_CLIENT_ID'))
    column_names = list(feature_rows[0].keys())
    row_values = [tuple(row[column_name] for column_name in column_names) for row in feature_rows]
    spark_session = SparkSession.builder.getOrCreate()
    feature_df = spark_session.createDataFrame(row_values, column_names)
    materialize_online(feature_set, feature_df)
    print(' done.')

    # start retrieval server
    print('Starting retrieval server...', end='', flush=True)
    os.environ['AZUREML_FEATURESTORE_DEBUG'] = 'true'
    init_online_lookup(feature_set.features, ManagedIdentityCredential(client_id=os.getenv('AZUREML_ARM_MSI_CLIENT_ID')))
    print(' done.')

    # measure perf
    print('Profiling retrieval perf...', end='', flush=True)
    perf_data = measure(feature_set, feature_rows)
    print(' done.')

    # stop retrieval server
    print('Stopping retrieval server...', end='', flush=True)
    shutdown_online_lookup()
    print(' done.')

    for filename in os.listdir(os.path.join(tempfile.gettempdir(), "azureml-logs", "featurestore")):
        shutil.copyfile(os.path.join(tempfile.gettempdir(), "azureml-logs", "featurestore", filename), f"./logs/{filename}")

    # transform latency data to quantiles
    print('Postprocessing measured data...', end='', flush=True)
    quantile_data = quantilize(perf_data)
    print(' done.')

    # log quantilized latencies as metrics
    print('Logging metrics...', end='', flush=True)
    log_metrics(quantile_data)
    print(' done.')

    # test for regressions
    test_stats(quantile_data)
