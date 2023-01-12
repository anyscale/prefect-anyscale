import argparse
import os
import subprocess

from fastapi import FastAPI
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
        self.agent = subprocess.Popen(
            ["prefect", "agent", "start", "-q", args.queue],
            env=dict(os.environ, **prefect_env),
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
    "PREFECT_API_KEY": os.environ["PREFECT_API_KEY"],
    "PREFECT_EXTRA_ENTRYPOINTS": "prefect_anyscale",
}))
