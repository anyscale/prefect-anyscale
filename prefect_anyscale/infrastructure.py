from typing import Dict, Union
from typing_extensions import Literal

from prefect.infrastructure.base import Infrastructure
from pydantic import Field


class AnscaleJob(Infrastructure):

    type: Literal["anyscale_job"] = Field(
        default="anyscale_job", description="The type of infrastructure."
    )

    compute_config: Union[str, Dict[str, str]] = Field(
        description="Compute config to use for the execution of the job."
    )

    cluster_env: Union[str, Dict[str, str]] = Field(
        description="Cluster environment to use for the execution of the job."
    )

