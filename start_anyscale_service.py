import argparse
import logging
import os
import shutil
import subprocess

from fastapi import FastAPI
import ray
from ray import serve

parser = argparse.ArgumentParser()
parser.add_argument("--queue", type=str)
args = parser.parse_args()

serve.start(detached=True)

app = FastAPI()

@serve.deployment(route_prefix="/")
@serve.ingress(app)
class PrefectAgentDeployment:
    def __init__(self):
        anyscale_prefect_dir = os.path.dirname(os.path.realpath(__file__))
        shutil.copy(os.path.join(anyscale_prefect_dir, "anyscale_prefect_agent.py"), "/home/ray/")

        self.agent = subprocess.Popen(["prefect", "agent", "start", "-q", args.queue])

    @app.get("/healthcheck")
    def healthcheck(self):
        poll = self.agent.poll()
        if poll is None:
            return
        else:
            raise RuntimeError("Prefect agent died")

serve.run(PrefectAgentDeployment.bind())
