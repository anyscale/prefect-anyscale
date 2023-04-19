import subprocess
import tempfile
import yaml

import ray

from prefect import flow, task
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
        "description": "An Anyscale Job submitted from Prefect.",
        "config": {
            "runtime_env": {
                "working_dir": ".",
                "upload_dir": "s3://anyscale-prefect-integration-test/github-working-dir/",
            },
            "entrypoint": "python anyscale_job.py " + " ".join([f"--{key} {val}" for key, val in args.items()]),
        }
    }

    with tempfile.NamedTemporaryFile(mode="w") as f:
        yaml.dump(job_config, f)
        f.flush()
        # Submit an Anyscale Job from Prefect and stream the logs
        subprocess.check_output(["anyscale", "job", "submit", f.name, "--follow"])

@flow(task_runner=RayTaskRunner)
def complex_flow():
    result = test_task.submit()
    assert result.result() == 42
    result = anyscale_job.submit({"arg": "value"})
    assert result.result() == None

if __name__ == "__main__":
    complex_flow()
