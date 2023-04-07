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

@flow(task_runner=RayTaskRunner)
def complex_flow():
    result = test_task.submit()
    assert result.result() == 42

if __name__ == "__main__":
    complex_flow()