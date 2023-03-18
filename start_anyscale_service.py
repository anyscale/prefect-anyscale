import argparse
import os
import subprocess

from fastapi import FastAPI
from ray import serve

def get_prefect_secret_environment():
    # We retrieve the PREFECT_API_KEY from the secret store so
    # we can pass it to the prefect agent since the agent will
    # need it to connect to the prefect control plane.
    aws_secret_id = os.environ.get("ANYSCALE_PREFECT_AWS_SECRET_ID")
    if aws_secret_id:
        import boto3
        client = boto3.client(
            "secretsmanager", region_name=os.environ["ANYSCALE_PREFECT_AWS_REGION"]
        )
        response = client.get_secret_value(SecretId=aws_secret_id)
        return {
            "PREFECT_API_KEY": response["SecretString"],
            "ANYSCALE_PREFECT_AWS_SECRET_ID": aws_secret_id,
            "ANYSCALE_PREFECT_AWS_REGION": os.environ["ANYSCALE_PREFECT_AWS_REGION"],
        }
    else:
        return {
            "PREFECT_API_KEY": os.environ["PREFECT_API_KEY"]
        }

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
    "PREFECT_EXTRA_ENTRYPOINTS": "prefect_anyscale",
    "ANYSCALE_PREFECT_QUEUE": os.environ["ANYSCALE_PREFECT_QUEUE"],
    **get_prefect_secret_environment()
})
