from prefect_anyscale.infrastructure import AnyscaleJob, RayJob


def prefect_runtime_environment_hook(runtime_env):

    if not runtime_env:
        runtime_env = {}

    # If no working_dir is specified, we use the current
    # directory as the working directory -- this will be
    # the directory containing the source code which is
    # downloaded by the Prefect engine.
    if not runtime_env.get("working_dir"):
        runtime_env["working_dir"] = "."

    return runtime_env

        
__all__ = [
    "AnyscaleJob",
    "RayJob",
    "prefect_runtime_environment_hook",
]
