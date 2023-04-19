import ray

from anyscale import AnyscaleSDK
from anyscale.controllers.job_controller import JobController
from anyscale.sdk.anyscale_client import CreateProductionJob

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
    # Submit an Anyscale Job from Prefect
    sdk = AnyscaleSDK()
    job = sdk.create_job(CreateProductionJob(
        name = "my-anyscale-job",
        description = "An Anyscale Job submitted from Prefect.",
        config= {
            "runtime_env": {
                "working_dir": ".",
                "upload_dir": "s3://anyscale-prefect-integration-test/github-working-dir/",
            },
            "entrypoint": "python anyscale_job.py " + " ".join([f"--{key} {val}" for key, val in args.items()]),
        }
    ))
    # Stream the Job logs into Prefect and fail if the job fails
    JobController().logs(job.id, should_follow=True)

@flow(task_runner=RayTaskRunner)
def complex_flow():
    result = test_task.submit()
    assert result.result() == 42
    result = anyscale_job.submit({"arg": "value"})
    assert result.result() == None

if __name__ == "__main__":
    complex_flow()
