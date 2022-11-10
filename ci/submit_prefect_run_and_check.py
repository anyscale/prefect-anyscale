import asyncio
import uuid
import logging

import prefect.deployments
from prefect.client import get_client
from prefect.filesystems import S3
from prefect.infrastructure import Process

from prefect_test import count_to

import s3fs

import botocore, boto3
for name in logging.Logger.manager.loggerDict.keys():
    if ('boto' in name) or ('urllib3' in name):
        logging.getLogger(name).setLevel(logging.DEBUG)

fs = s3fs.S3FileSystem()
d = fs.ls('anyscale-prefect-integration-test')
print("d", d)

with fs.open('anyscale-prefect-integration-test/test-file', 'wb') as f:
    f.write(b'hello')

deployment = prefect.deployments.Deployment.build_from_flow(
    flow=count_to,
    name="prefect_test",
    work_queue_name="test",
    storage=S3.load("test-storage-github"),
    infrastructure=Process.load("anyscale-infra")
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
