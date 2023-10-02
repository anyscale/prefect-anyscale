import logging
import os
from typing import Dict, Union
import subprocess
import tempfile

from prefect.infrastructure.base import Infrastructure, InfrastructureResult
from prefect.utilities.asyncutils import sync_compatible
from pydantic import Field
from typing_extensions import Literal


class AnyscaleJob(Infrastructure):
    type: Literal["anyscale-job"] = Field(
        default="anyscale-job", description="The type of infrastructure."
    )

    compute_config: Union[None, str, Dict[str, str]] = Field(
        description="Compute config to use for the execution of the job.",
        default=None,
    )

    cluster_env: Union[None, str, Dict[str, str]] = Field(
        description="Cluster environment to use for the execution of the job."
    )

    project_id: str = Field(
        description="The project id to use for the execution of the job.", default=None
    )

    _block_type_name = "Anyscale Job"

    def preview(self):
        return " \\\n".join(
            "compute_config = " + str(self.compute_config),
            "cluster_env = " + str(self.cluster_env),
            "project_id = " + str(self.project_id),
        )

    @sync_compatible
    async def run(
        self,
        task_status=None,
    ):
        env = self._get_environment_variables()
        api_url = env.get("PREFECT_API_URL")
        api_key = env.get("PREFECT_API_KEY")
        flow_run_id = env.get("PREFECT__FLOW_RUN_ID")

        aws_secret_id = env.get("ANYSCALE_PREFECT_AWS_SECRET_ID")

        cmd = ""
        if api_url:
            cmd += "PREFECT_API_URL={}".format(api_url)
        if aws_secret_id:
            # If we use the AWS secret manager to pass the PREFECT_API_KEY
            # through, we will retrieve the API key when the job gets executed.
            aws_region = env.get("ANYSCALE_PREFECT_AWS_REGION")
            cmd += " PREFECT_API_KEY=`aws secretsmanager get-secret-value --secret-id {} --region {} --output=text --query=SecretString`".format(
                aws_secret_id, aws_region
            )
        elif api_key:
            logging.warn(
                "Your PREFECT_API_KEY is currently stored in plain text. Consider using a secret manager to store your secrets."
            )
            cmd += " PREFECT_API_KEY={}".format(api_key)
        if flow_run_id:
            cmd += " PREFECT__FLOW_RUN_ID={}".format(flow_run_id)

        # Install runtime environment
        cmd += " RAY_RUNTIME_ENV_HOOK=prefect_anyscale.prefect_runtime_environment_hook"

        cmd += " python -m prefect.engine"

        # Link the Job on the Anyscale UI with the prefect flow run
        job_name = "prefect-job-" + flow_run_id

        content = """
name: "{}"
entrypoint: "{}"
""".format(
            job_name, cmd
        )

        if self.compute_config:
            content += 'compute_config: "{}"\n'.format(self.compute_config)

        if self.cluster_env:
            content += 'cluster_env: "{}"\n'.format(self.cluster_env)

        if self.project_id:
            content += 'project_id: "{}"\n'.format(self.project_id)

        if task_status:
            task_status.started(job_name)

        with tempfile.NamedTemporaryFile(mode="w") as f:
            f.write(content)
            f.flush()
            logging.info(f"Submitting Anyscale Job with configuration '{content}'")
            returncode = subprocess.check_call(["anyscale", "job", "submit", f.name])

        return AnyscaleJobResult(status_code=returncode, identifier="")

    def _get_environment_variables(self, include_os_environ: bool = True):
        os_environ = os.environ if include_os_environ else {}
        # The base environment must override the current environment or
        # the Prefect settings context may not be respected
        env = {**os_environ, **self._base_environment(), **self.env}

        # Drop null values allowing users to "unset" variables
        return {key: value for key, value in env.items() if value is not None}


class AnyscaleJobResult(InfrastructureResult):
    """Contains information about the final state of a completed process"""

    pass
