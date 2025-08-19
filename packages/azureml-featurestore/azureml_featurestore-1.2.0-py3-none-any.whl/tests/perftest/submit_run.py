import argparse
import os
import tempfile
import time
import sys

from azure.ai.ml import command, MLClient
from azure.ai.ml.entities import BuildContext, Environment
from azure.identity import AzureCliCredential


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', action='store_true')
    parser.add_argument('--n-runs', type=int, default=1)

    args = parser.parse_args()

    subscription = os.getenv('AZUREML_ARM_SUBSCRIPTION')
    resource_group = os.getenv('AZUREML_ARM_RESOURCEGROUP')
    workspace = os.getenv('AZUREML_ARM_WORKSPACE_NAME')
    feature_store = os.getenv('AZUREML_ARM_FEATURESTORE_NAME')
    client_id = os.getenv('AZUREML_ARM_MSI_CLIENT_ID')

    ml_client = MLClient(AzureCliCredential(), subscription, resource_group, workspace)

    experiment_name = 'reference' if args.reference else 'test'

    with tempfile.TemporaryDirectory() as tmpdir:
        root_directory = os.path.abspath(os.path.join(__file__, '../../../'))

        from sys import platform
        if platform == "linux" or platform == "linux2":
            os.system(f'cd {root_directory}; {sys.executable} setup.py bdist_wheel --dist-dir={tmpdir}')
            os.system(f'cp -v {root_directory}/tests/perftest/docker/Dockerfile {tmpdir}')
        elif platform == "win32":
            os.system(rf'cd {root_directory} && {sys.executable} setup.py bdist_wheel --dist-dir={tmpdir}')
            os.system(rf'copy {root_directory}\tests\perftest\docker\Dockerfile {tmpdir}')
        else:
            raise Exception("OS is not supported")

        print('Creating environment...')
        environment=ml_client.environments.create_or_update(Environment(
            name='online-fs-perftest-env',
            build=BuildContext(
                path=tmpdir,
                dockerfile_path='Dockerfile',
            )
        ))
    
    print('Submitting runs...')
    for run_ix in range(args.n_runs):
        command_job = command(
            experiment_name=experiment_name,
            code="./src",
            command="python test_retrieval_perf.py",
            environment=environment,
            environment_variables={
                'AZUREML_ARM_MSI_CLIENT_ID': client_id,
                'AZUREML_ARM_FEATURESTORE_NAME': feature_store,
                'AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED': 'True',
                'amlfeaturestore.eventLog.enabled': 'True',
            },
            compute="retrieval-compute",
        )

        returned_job = ml_client.jobs.create_or_update(command_job)
        print(returned_job.studio_url)
        while True:
            returned_job = ml_client.jobs.get(returned_job.name)
            if returned_job.status in { 'Completed', 'Failed', 'Canceled' }:
                print(returned_job.status)
                print()
                break

            time.sleep(15)
