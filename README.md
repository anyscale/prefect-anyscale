# Prefect Integration with Anyscale

This repository contains the integration of Prefect with Anyscale.

## Development Setup

For development, we strongly recommend using Anyscale Workspaces together with [Prefect Ray](https://github.com/PrefectHQ/prefect-ray).
No further integration is needed and you can just run a Python script like
```python
import time

from prefect import flow, task
from prefect_ray import RayTaskRunner

@task
def shout(number):
    time.sleep(0.5)
    print(f"#{number}")

@flow(task_runner=RayTaskRunner)
def count_to(highest_number):
    for number in range(highest_number):
        shout.submit(number)

if __name__ == "__main__":
    count_to(10)
```
inside your workspace and connect to Prefect via `prefect login`. Please *do not* use the Ray or Anyscale Client, i.e.
do not use the `RayTaskRunner(address="ray://...")` or `RayTaskRunner(address="anyscale://...")` since these can
cause various issues (version mismatches between client and cluster, loosing connection, slower data transfer and API
calls between client and server etc).

## Production Setup

This repository is providing an integration between Anyscale and Prefect for production scenarios, where you
want to submit your experiments from the Prefect UI and have them run in Anyscale. It uses
[Prefect Ray](https://github.com/PrefectHQ/prefect-ray) internally and defines a Prefect agent that can run
as an Anyscale Service in your cloud account. This agent will pick work from the Prefect work queue, convert it
into an Anyscale Job that will run the work on a Ray cluster in the same way as the development setup (to keep
production and development close).

### Getting Started

#### Setting up the Anyscale Prefect Service

This part only needs to be done once per Anyscale account to set up
the Anyscale Prefect agent (and subsequently to update it if desired).

To get started, you should first start the Anyscale Prefect Service in your Anyscale Cloud. It will be connected
to your Prefect UI, receive new work, convert it into Anyscale Jobs and run those inside of Anyscale. You can set
up the service from your laptop, you just need the Anyscale CLI installed. Generate a long lived Prefect API token
from the Prefect UI and check the "Never Expire" checkmark (you can always rotate the token and restart the service
with the new token if that becomes necessary):

![set up prefect api token](./doc/prefect_api_token.png)

From your laptop, then log into Prefect by running the following from your shell (substitute the API token you just generated):
```bash
prefect cloud login -k pnu_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

We now need to create an Anyscale Service file for deploying the Anyscale Prefect Agent. First display the settings with
```bash
prefect config view --hide-sources
```
and create a `prefect-agent-service.yaml` file where you fill in the information just displayed in place of the `...`:
```yaml
name: prefect-agent
ray_serve_config:
  import_path: start_anyscale_service:entrypoint
  runtime_env:
    env_vars:
      PREFECT_API_URL: "https://api.prefect.cloud/api/accounts/..."
      PREFECT_API_KEY: "..."
      ANYSCALE_PREFECT_QUEUE: test
    pip: ["prefect-anyscale"]
    working_dir: https://github.com/anyscale/prefect-anyscale/archive/refs/tags/v0.2.0.zip
```

**NOTE**: This will store your Prefect API token in the service
definition, which can be accessed from the Anyscale UI.  If you want
to avoid this, you can store the token in the AWS Secrets Manager (or
another secret manager of your choice) and retrieve it from there in
`start_anyscale_service.py`.

The `working_dir` contains the version of the Anyscale Prefect agent, which you can upgrade going forward as new versions are released.
You can then start the service with
```bash
anyscale service deploy prefect-agent-service.yaml
```

Now create a Prefect infrastructure that will be used to run the deployments inside of Anyscale. You can do this
by running `pip install prefect-anyscale` and then in a Python interpreter
```python
import prefect_anyscale
infra = prefect_anyscale.AnyscaleJob(cluster_env="prefect-test-environment")
infra.save("test-infra")
```

#### Creating a deployment and scheduling the run

Now we can go ahead and create a Prefect deployment:
```python
import prefect
from prefect.filesystems import S3
from prefect_anyscale import AnyscaleJob

from prefect_test import count_to

deployment = prefect.deployments.Deployment.build_from_flow(
    flow=count_to,
    name="prefect_test",
    work_queue_name="test",
    storage=S3.load("test-storage"),
    infrastructure=AnyscaleJob.load("test-infra")
)
deployment.apply()
```

You can now schedule new runs with this deployment from the Prefect UI

![submit prefect run](./doc/prefect_submit_run.png)

and it will be executed as an Anyscale Job on an autoscaling Ray Cluster which has the same setup as the development setup described above.

#### Overriding properties of the infra block

You can override properties of the Anyscale infra block in a deployment like this

```python
import prefect
from prefect.filesystems import S3
from prefect_anyscale import AnyscaleJob

from prefect_test import count_to

deployment = prefect.deployments.Deployment.build_from_flow(
    flow=count_to,
    name="prefect_test_custom",
    work_queue_name="test",
    storage=S3.load("test-storage"),
    infrastructure=AnyscaleJob.load("test-infra"),
    infra_overrides={"compute_config": "test-compute-config"}
)
deployment.apply()
```
