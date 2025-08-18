# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["RunRunFlowResponse"]


class RunRunFlowResponse(BaseModel):
    flow_status: str

    run_number: int
