import os
import subprocess
import tempfile
import yaml

import ray

from prefect import flow, task, get_run_logger
from prefect_ray import RayTaskRunner

# This custom resource will cause another node to be added
# to the cluster so we can test that the working directory
# is indeed synced to all nodes in the cluster.
@ray.remote(resources={"custom_resource": 1})
def remote_task():
    from ci.test_python_file import test
    return test()

@task
def test_task():
    return ray.get(remote_task.remote())

@task
def anyscale_job(args):
    job_config = {
        "name": "my-anyscale-job",
        "cloud": "anyscale_v2_default_cloud",
        "description": "An Anyscale Job submitted from Prefect.",
        "cluster_env": "default_cluster_env_2.3.1_py39",
        "runtime_env": {
            "working_dir": "ci/",
            "upload_path": "s3://anyscale-prefect-integration-test/working-dir/",
        },
        "entrypoint": "python anyscale_job.py " + " ".join([f"--{key} {val}" for key, val in args.items()]),
    }

    with tempfile.NamedTemporaryFile(mode="w") as f:
        yaml.dump(job_config, f)
        f.flush()
        # Submit an Anyscale Job from Prefect and record the logs
        output = subprocess.check_output(
            ["anyscale", "job", "submit", f.name, "--follow"]
        )
        logger = get_run_logger()
        logger.info("Anyscale Job output: " + output.decode())

@flow(task_runner=RayTaskRunner)
def complex_flow():
    result = test_task.submit()
    assert result.result() == 42
    result = anyscale_job.submit({"arg": "value"})
    assert result.result() == None

if __name__ == "__main__":
    complex_flow()
