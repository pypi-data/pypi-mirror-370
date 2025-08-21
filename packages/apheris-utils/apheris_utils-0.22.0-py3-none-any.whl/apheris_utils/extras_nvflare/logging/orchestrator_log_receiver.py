from nvflare.apis.dxo import from_shareable
from nvflare.apis.fl_component import FLComponent
from nvflare.apis.fl_constant import FLContextKey
from nvflare.apis.fl_context import FLContext

from .util import get_logger_fn_for_level


class OrchestratorLogReceiver(FLComponent):
    """
    A component that receives messages sent to the Orchestrator from the Gateways as
    FLARE events and writes them into the Orchestrator logs.
    """

    def handle_event(self, event_type: str, fl_ctx: FLContext):
        super().handle_event(event_type=event_type, fl_ctx=fl_ctx)

        if event_type == "debug_message":
            shareable = fl_ctx.get_prop(key=FLContextKey.EVENT_DATA)
            dxo = from_shareable(shareable)
            data = dxo.data
            client_message = data["message"]
            client_name = data["client_name"]
            level = data["level"]

            get_logger_fn_for_level(component=self, level=level)(
                fl_ctx,
                f"OrchestratorLogReceiver: Message from '{client_name} [{level}]': "
                f"{client_message}",
            )
