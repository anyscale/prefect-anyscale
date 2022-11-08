import os
import ray
import shutil
import subprocess

ray.init()

ANYSCALE_PREFECT_DIR = os.path.dirname(os.path.realpath(__file__))

shutil.copy(os.path.join(ANYSCALE_PREFECT_DIR, "anyscale_prefect_agent.py"), "/home/ray/")

subprocess.check_call(["prefect", "agent", "start", "-q", "test"])
