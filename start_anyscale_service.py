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

        # The prefect agent is timing out on the connection to the prefect control
        # plane after about 24h of inactivity. If this happens, restart it.
        while True:
            logging.info(f"Starting prefect agent for queue {args.queue}")
            try:
                subprocess.check_call(["prefect", "agent", "start", "-q", args.queue])
            except Exception:
                logging.exception("Restarting prefect agent due to exception")

serve.run(PrefectAgentDeployment.bind())
