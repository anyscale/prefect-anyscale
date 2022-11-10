import asyncio
import uuid

import prefect.deployments
from prefect.client import get_client

flow_run = prefect.deployments.run_deployment("count-to/prefect_test", parameters={"highest_number": 5})

async def wait_for_run_complete(flow_id):
    async with get_client() as client:
        while True:
            run = await client.read_flow_run(flow_id)
            if run.state.is_completed():
                return
            print(run.state)
            await asyncio.sleep(5.0)
    
asyncio.run(wait_for_run_complete(flow_run.id))
