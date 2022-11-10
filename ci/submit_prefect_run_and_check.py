import asyncio
import uuid

import prefect.deployments
from prefect.client import get_client

run_name = str(uuid.uuid4())
prefect.deployments.run_deployment("count-to/prefect_test", parameters={"highest_number": 5}, flow_run_name=run_name)

async def wait_for_run_complete(name):
    async with get_client() as client:
        while True:
            run = await client.read_flow_run(name)
            if run.state.is_completed():
                break
            print(run.state)
            await asyncio.sleep(5.0)
    
asyncio.run(wait_for_run_complete(run_name))
