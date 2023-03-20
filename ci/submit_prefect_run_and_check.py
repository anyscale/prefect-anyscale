import argparse
import asyncio

import prefect.deployments
from prefect.client import get_client
from prefect.filesystems import S3

from prefect_anyscale import AnyscaleJob

from prefect_test import count_to

parser = argparse.ArgumentParser()
parser.add_argument("--queue", help="prefect queue to submit to")
args = parser.parse_args()

deployment = prefect.deployments.Deployment.build_from_flow(
    flow=count_to,
    name="prefect_test",
    work_queue_name=args.queue,
    storage=S3.load("test-storage-github"),
    infrastructure=AnyscaleJob.load("anyscale-job-infra"),
    infra_overrides={"compute_config": "test-compute-config"},
)
deployment.apply()

flow_run = prefect.deployments.run_deployment("count-to/prefect_test", parameters={"highest_number": 5})

async def wait_for_run_complete(flow_id):
    async with get_client() as client:
        while True:
            run = await client.read_flow_run(flow_id)
            if run.state.is_completed():
                return
            print(run.state)
            if run.state.is_failed():
                raise RuntimeError("Run failed")
            await asyncio.sleep(5.0)
    
asyncio.run(wait_for_run_complete(flow_run.id))
