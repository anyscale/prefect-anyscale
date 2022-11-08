import ray
import subprocess

ray.init()

subprocess.check_call(["prefect", "agent", "start", "-q", "test"])
