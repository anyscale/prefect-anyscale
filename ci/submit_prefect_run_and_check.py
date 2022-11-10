import uuid
from prefect.deployments import Deployment
from prefect.client import get_client

run_name = str(uuid.uuid4())
prefect.deployments.run_deployment("count-to/prefect_test", parameters={"highest_number": 5}, flow_run_name=run_name)

async with get_client() as client:
    while True:
        run = await client.read_flow_run(run_name)
        if run.state.is_completed():
            break
        print(run.state)
        time.sleep(5.0)
    
