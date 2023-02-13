import argparse
import os
import subprocess

from fastapi import FastAPI
from ray import serve

# parser = argparse.ArgumentParser()
# parser.add_argument("--queue", type=str)
# args = parser.parse_args()

serve.start(detached=True)

app = FastAPI()

@serve.deployment(route_prefix="/", num_replicas=1, health_check_period_s=10, health_check_timeout_s=30)
@serve.ingress(app)
class PrefectAgentDeployment:
    def __init__(self, prefect_env):
        self.agent = subprocess.Popen(
            # ["prefect", "agent", "start", "-q", args.queue],
            ["prefect", "agent", "start", "-q", "test"],
            env=dict(os.environ, **prefect_env),
        )

    def check_health(self):
        poll = self.agent.poll()
        if poll is None:
            return
        else:
            raise RuntimeError("Prefect agent died")

# serve.run(PrefectAgentDeployment.bind({
#     "PREFECT_API_URL": os.environ["PREFECT_API_URL"],
#     "PREFECT_API_KEY": os.environ["PREFECT_API_KEY"],
#     "PREFECT_EXTRA_ENTRYPOINTS": "prefect_anyscale",
# }))

entrypoint = PrefectAgentDeployment.bind({
    "PREFECT_API_URL": os.environ["PREFECT_API_URL"],
    "PREFECT_API_KEY": os.environ["PREFECT_API_KEY"],
    "PREFECT_EXTRA_ENTRYPOINTS": "prefect_anyscale",
})
