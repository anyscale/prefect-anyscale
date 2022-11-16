import argparse
import logging
import os
import shutil
import subprocess

import ray
from ray import serve

parser = argparse.ArgumentParser()
parser.add_argument("--queue", type=str)
args = parser.parse_args()

ray.init()

serve.start(detached=True)

@serve.deployment
class PrefectAgentDeployment:
    def __init__(self):
        anyscale_prefect_dir = os.path.dirname(os.path.realpath(__file__))
        shutil.copy(os.path.join(anyscale_prefect_dir, "anyscale_prefect_agent.py"), "/home/ray/")

        self.agent = subprocess.Popen((["prefect", "agent", "start", "-q", args.queue])

serve.run(PrefectAgentDeployment.bind())
