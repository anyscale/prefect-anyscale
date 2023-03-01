import argparse
import os
import subprocess

from fastapi import FastAPI
from ray import serve

serve.start(detached=True)

app = FastAPI()

@serve.deployment(route_prefix="/", num_replicas=1, health_check_period_s=10, health_check_timeout_s=30)
@serve.ingress(app)
class PrefectAgentDeployment:
    def __init__(self, prefect_env):
        self.agent = subprocess.Popen(
            ["prefect", "agent", "start", "-q", prefect_env["ANYSCALE_PREFECT_QUEUE"]],
            env=dict(os.environ, **prefect_env),
        )

    def check_health(self):
        poll = self.agent.poll()
        if poll is None:
            return
        else:
            raise RuntimeError("Prefect agent died")

if os.environ.get("ANYSCALE_PREFECT_DEVELOPMENT", "0") == "1":
    subprocess.check_call(["pip", "install", "-e", "."])

entrypoint = PrefectAgentDeployment.bind({
    "PREFECT_API_URL": os.environ["PREFECT_API_URL"],
    "PREFECT_API_KEY": os.environ["PREFECT_API_KEY"],
    "PREFECT_EXTRA_ENTRYPOINTS": "prefect_anyscale",
    "ANYSCALE_PREFECT_QUEUE": os.environ["ANYSCALE_PREFECT_QUEUE"],
})
