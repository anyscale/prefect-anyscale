from typing import Dict, Union
from typing_extensions import Literal

from prefect.infrastructure.base import Infrastructure
from prefect.utilities.asyncutils import sync_compatible
from pydantic import Field


class AnyscaleJob(Infrastructure):

    type: Literal["anyscale_job"] = Field(
        default="anyscale_job", description="The type of infrastructure."
    )

    compute_config: Union[None, str, Dict[str, str]] = Field(
        description="Compute config to use for the execution of the job.",
        default=None,
    )

    cluster_env: Union[None, str, Dict[str, str]] = Field(
        description="Cluster environment to use for the execution of the job."
    )

    def preview(self):
        return " \\\n".join(
            "compute_config = " + str(self.compute_config),
            "cluster_env = " + str(self.cluster_env),
        )

    @sync_compatible
    async def run(
        self,
        task_status = None,
    ):
        pass
