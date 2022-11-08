"""
Version 0.0.2 of the Anyscale Prefect Agent.
"""

import argparse
import logging
import os
import subprocess
import tempfile

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--cluster-environment", type=str)
parser.add_argument("--compute-config", type=str)
args = parser.parse_args()

api_url = os.environ.get("PREFECT_API_URL")
api_key = os.environ.get("PREFECT_API_KEY")
flow_run_id = os.environ.get("PREFECT__FLOW_RUN_ID")

cmd = ""
if api_url:
    cmd += "PREFECT_API_URL={}".format(api_url)
if api_key:
    cmd += " PREFECT_API_KEY={}".format(api_key)
if flow_run_id:
    cmd += " PREFECT__FLOW_RUN_ID={}".format(flow_run_id)

cmd += " /home/ray/anaconda3/bin/python -m prefect.engine"

content = """
entrypoint: "{}"
""".format(cmd)

if args.compute_config:
    content += """
    compute_config: "{}"
    """.format(args.compute_config)

if args.cluster_environment:
    content += """
    cluster_environment: "{}"
    """.format(args.cluster_environment)

with tempfile.NamedTemporaryFile(mode="w") as f:
    f.write(content)
    f.flush()
    logging.info(f"Submitting Anyscale Job with configuration '{content}'")
    subprocess.check_call(["anyscale", "job", "submit", f.name])
