from test_python_file import test

from prefect import flow, task
from prefect_ray import RayTaskRunner

@task
def test_task():
    return test()

@flow(task_runner=RayTaskRunner)
def complex_flow():
    result = test_task.submit()
    assert result == 42

if __name__ == "__main__":
    complex_flow()