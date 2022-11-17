import argparse
import logging
import os
import shutil
import subprocess
import uuid

from fastapi import FastAPI
import ray
from ray import serve

parser = argparse.ArgumentParser()
parser.add_argument("--queue", type=str)
args = parser.parse_args()

serve.start(detached=True)

app = FastAPI()

@serve.deployment(route_prefix="/", num_replicas=1)
@serve.ingress(app)
class PrefectAgentDeployment:
    def __init__(self, prefect_env):
        anyscale_prefect_dir = os.path.dirname(os.path.realpath(__file__))
        shutil.copy(os.path.join(anyscale_prefect_dir, "anyscale_prefect_agent.py"), "/home/ray/")

        # Logfiles will be closed when the process exits
        prefect_agent_id = uuid.uuid4()
        self.logfile_out = open(f"/tmp/prefect-agent-{prefect_agent_id}.out", "w")
        self.logfile_err = open(f"/tmp/prefect-agent-{prefect_agent_id}.err", "w")
        self.agent = subprocess.Popen(
            ["prefect", "agent", "start", "-q", args.queue],
            env=dict(os.environ, **prefect_env),
            stdout=self.logfile_out, stderr=self.logfile_err,
        )

    @app.get("/healthcheck")
    def healthcheck(self):
        poll = self.agent.poll()
        if poll is None:
            return
        else:
            raise RuntimeError("Prefect agent died")

serve.run(PrefectAgentDeployment.bind({
    "PREFECT_API_URL": os.environ["PREFECT_API_URL"],
    "PREFECT_API_KEY": os.environ["PREFECT_API_KEY"]
}))
