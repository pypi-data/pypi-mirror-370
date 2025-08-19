import os
import shutil
from datetime import datetime
from typing import List

from tests.e2etest.spark_e2e_test_base import SparkJobE2EBase

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

# test constants
SCENARIO_FOLDERS = ["./tests/perftest/src/offline/scenarios"]


class SparkJobPERFBase(SparkJobE2EBase):
    @classmethod
    def setUpClass(cls) -> None:
        now = datetime.utcnow()
        cls._test_id = now.strftime("%Y%m%d-%H%M%SZ")
        cls._experiment_name = f"SparkJobV2_DSL_PERF_{now.strftime('%Y%m')}"

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
                        timeout_sec = 5400
                        self._test_spark_job(spark_job, timeout_sec=timeout_sec)

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
            driver_cores=32,
            driver_memory="224g",
            executor_cores=32,
            executor_memory="224g",
            executor_instances=20,
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
            resources=SparkResourceConfiguration(instance_type="standard_e32s_v3", runtime_version=spark_version),
        )
