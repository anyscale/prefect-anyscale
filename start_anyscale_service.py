import argparse
import os
import ray
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--queue", type=str)
args = parser.parse_args()

ray.init()

ANYSCALE_PREFECT_DIR = os.path.dirname(os.path.realpath(__file__))

shutil.copy(os.path.join(ANYSCALE_PREFECT_DIR, "anyscale_prefect_agent.py"), "/home/ray/")

subprocess.check_call(["prefect", "agent", "start", "-q", args.queue])
