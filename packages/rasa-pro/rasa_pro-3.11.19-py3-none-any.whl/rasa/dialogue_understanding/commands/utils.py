from typing import List
from rasa.shared.core.flows import FlowsList


def find_default_flows_collecting_slot(
    slot_name: str, all_flows: FlowsList
) -> List[str]:
    """Find default flows that have collect steps matching the specified slot name.

    Args:
        slot_name: The name of the slot to search for.
        all_flows: All flows in the assistant.

    Returns:
        List of flow IDs for default flows that collect the specified slot
        without asking before filling.
    """
    return [
        flow.id
        for flow in all_flows.underlying_flows
        if flow.is_rasa_default_flow
        and any(
            step.collect == slot_name and not step.ask_before_filling
            for step in flow.get_collect_steps()
        )
    ]
