import logging
import os
import shutil
import time
import unittest
from datetime import datetime
from typing import List

from azure.ai.ml import Input, MLClient, Output, spark
from azure.ai.ml.entities import (
    Environment,
    Job,
    ManagedIdentityConfiguration,
    Spark,
    SparkJobEntry,
    SparkResourceConfiguration,
    UserIdentityConfiguration,
)
from azure.ai.ml.operations._run_history_constants import JobStatus, RunHistoryConstants
from azure.identity import DefaultAzureCredential

# test constants
SUBSCRIPTION_ID = "1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a"
RESOURCE_GROUP = "featurestore-test-rg"
WORKSPACE_NAME = "featurestore-test-project-ws"

SCENARIO_FOLDERS = ["./tests/e2etest/scenarios", "./scala-impl/feathrentrypoint/src/test/python"]


class SparkJobE2EBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        now = datetime.utcnow()
        cls._test_id = now.strftime("%Y%m%d-%H%M%SZ")
        cls._experiment_name = f"SparkJobV2_E2E_{now.strftime('%Y%m')}"
        logging.basicConfig(level=logging.INFO)

    def _get_spark_job(self, test_file, scenario_folder, sdk_package_version=None, spark_version="3.2.0") -> Spark:
        env = Environment(conda_file="./tests/e2etest/env/test_env.yml")
        if sdk_package_version:
            pip = env.conda_file["dependencies"][-1]["pip"]
            pip.remove("azureml-featurestore")
            pip.append(f"azureml-featurestore==0.0.{sdk_package_version}")
            env.conda_file["dependencies"][-1]["pip"] = pip
        print(env.conda_file)

        # both input_path and output_path is available
        return spark(
            display_name=f"{self.__class__._test_id}_{test_file}",
            experiment_name=self.__class__._experiment_name,
            code=scenario_folder,
            entry=SparkJobEntry(entry=test_file),
            environment=env,
            driver_cores=2,
            driver_memory="2g",
            executor_cores=2,
            executor_memory="2g",
            executor_instances=2,
            jars=["azureml-fs-scala-impl-1.0.0.jar"],
            conf={"spark.yarn.appMasterEnv.AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED": "true"},
            inputs={
                # "input": Input(
                #     type=input_type.name,
                #     path=inout_path.input_path,
                #     mode=InputOutputModes.DIRECT
                # )
            },
            outputs={},
            args=None,  # "--input ${{inputs.input}} --output ${{outputs.output}}" + f" --storage_type {storage_type.name} --input_mode {input_type.name} --output_mode {output_type.name}",
            identity=UserIdentityConfiguration(),
            # else ManagedIdentityConfiguration(),
            compute=None,
            resources=SparkResourceConfiguration(instance_type="Standard_E8S_V3", runtime_version=spark_version),
        )

    def _test_spark_job(self, spark_job_spec, ml_client=None, timeout_sec=600, skip_validation=False):
        if ml_client is None:
            ml_client = MLClient(
                DefaultAzureCredential(exclude_managed_identity_credential=True),
                SUBSCRIPTION_ID,
                RESOURCE_GROUP,
                WORKSPACE_NAME,
            )

        spark_job = ml_client.jobs.create_or_update(spark_job_spec, skip_validation=skip_validation)
        spark_job = SparkJobE2EBase._wait_until_done(ml_client, spark_job, timeout_interval_sec=timeout_sec)

        if spark_job.status in RunHistoryConstants.TERMINAL_STATUSES:
            self.assertEqual(
                spark_job.status,
                JobStatus.COMPLETED,
                f"Spark job should be completed successfully, but {spark_job.status}. Please go to {spark_job.studio_url} for more details.",
            )
        else:
            self.fail(
                f"Spark job run longer than usual, fail the case as timeout error. Please go to {spark_job.studio_url} for more details."
            )
        logging.info(
            f"Spark job: {spark_job.display_name} was completed successfully. Please go to {spark_job.studio_url} for more details."
        )
        return spark_job

    def _test_spark_jobs(self, sdk_version=None, scenarios_to_test: List[str] = None, fs_scala_jar: str = None):
        for dir in SCENARIO_FOLDERS:
            if fs_scala_jar:
                shutil.copy(fs_scala_jar, dir)
            scenario_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(".py")]
            if scenarios_to_test:
                scenario_files = [f + ".py" for f in scenarios_to_test]
            for f in scenario_files:
                test_case_name = f"TEST CASE: {f}"
                with self.subTest(test_case_name):
                    print(test_case_name)
                    spark_job = self._get_spark_job(test_file=f, scenario_folder=dir, sdk_package_version=sdk_version)
                    if spark_job is not None:
                        timeout_sec = 2400
                        self._test_spark_job(spark_job, timeout_sec=timeout_sec)

    @staticmethod
    def _wait_until_done(
        client: MLClient, job: Job, skip_interval_sec=30, poll_interval_sec=15, timeout_interval_sec=600, verbose=True
    ) -> Job:
        def print_job_status(job: Job):
            if verbose:
                logging.info(f"[{job.display_name}] {time.time() - poll_start_time:.2f}: {job.status}")

        poll_start_time = time.time()
        print_job_status(job)
        time.sleep(skip_interval_sec)
        job = client.jobs.get(job.name)
        while (
            job.status not in RunHistoryConstants.TERMINAL_STATUSES
            and time.time() - poll_start_time < timeout_interval_sec
        ):
            print_job_status(job)
            time.sleep(poll_interval_sec)
            job = client.jobs.get(job.name)
        print_job_status(job)
        return job
