"""
Version 0.0.1 of the Anyscale Prefect Agent.

It 
"""

import os
import subprocess
import tempfile

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

with tempfile.NamedTemporaryFile(mode="w") as f:
    f.write(content)
    f.flush()
    subprocess.check_call(["anyscale", "job", "submit", f.name])
