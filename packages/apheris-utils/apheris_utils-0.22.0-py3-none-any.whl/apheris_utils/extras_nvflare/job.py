from uuid import UUID

from nvflare.apis.fl_context import FLContext


def get_job_id(fl_ctx: FLContext) -> UUID:
    """Get the job ID from the FLContext."""
    if not fl_ctx:
        raise ValueError("A valid FLContext is required to get the job ID.")

    job_id = fl_ctx.get_job_id()
    if not job_id:
        raise ValueError("Job ID not found in FLContext.")

    try:
        return UUID(job_id)
    except ValueError:
        raise ValueError("Job ID is not a valid UUID")
