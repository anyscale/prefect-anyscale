import asyncio
import time

import prefect.deployments
from prefect.client import get_client
from prefect.filesystems import S3

from prefect_anyscale import RayJob

from prefect_test import count_to

deployment = prefect.deployments.Deployment.build_from_flow(
    flow=count_to,
    name="prefect_test",
    work_queue_name="test",
    storage=S3.load("test-storage-github"),
    infrastructure=RayJob()
)
deployment.apply()

print("time at A is ", time.time())
flow_run1 = prefect.deployments.run_deployment("count-to/prefect_test", parameters={"highest_number": 5})
print("time at B is ", time.time())
flow_run2 = prefect.deployments.run_deployment("count-to/prefect_test", parameters={"highest_number": 7})
print("time at C is ", time.time())

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
    
asyncio.run(wait_for_run_complete(flow_run1.id))
asyncio.run(wait_for_run_complete(flow_run2.id))