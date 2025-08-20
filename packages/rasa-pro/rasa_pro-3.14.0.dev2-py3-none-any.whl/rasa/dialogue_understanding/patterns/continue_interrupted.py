from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Text

from rasa.core.actions.action import Action
from rasa.core.channels import OutputChannel
from rasa.core.nlg import NaturalLanguageGenerator
from rasa.dialogue_understanding.stack.frames import PatternFlowStackFrame
from rasa.dialogue_understanding.stack.utils import top_user_flow_frame
from rasa.shared.constants import RASA_DEFAULT_FLOW_PATTERN_PREFIX
from rasa.shared.core.constants import (
    ACTION_ASK_INTERRUPTED_FLOW_TO_CONTINUE,
    ACTION_CANCEL_INTERRUPTED_FLOW,
    ACTION_CONTINUE_INTERRUPTED_FLOW,
    ACTION_SET_INTERRUPTED_FLOWS,
)
from rasa.shared.core.domain import Domain
from rasa.shared.core.events import Event, SlotSet
from rasa.shared.core.trackers import DialogueStateTracker

FLOW_PATTERN_CONTINUE_INTERRUPTED = (
    RASA_DEFAULT_FLOW_PATTERN_PREFIX + "continue_interrupted"
)
INTERRUPTED_FLOWS_SLOT = "interrupted_flows"
INTERRUPTED_FLOW_TO_CONTINUE_SLOT = "interrupted_flow_to_continue"
MULTIPLE_FLOWS_INTERRUPTED_SLOT = "multiple_flows_interrupted"
CONFIRMATION_CONTINUE_INTERRUPTED_FLOW_SLOT = "confirmation_continue_interrupted_flow"


@dataclass
class ContinueInterruptedPatternFlowStackFrame(PatternFlowStackFrame):
    """A pattern flow stack frame that gets added if an interruption is completed."""

    flow_id: str = FLOW_PATTERN_CONTINUE_INTERRUPTED
    """The ID of the flow."""
    previous_flow_name: str = ""
    """The name of the flow that was interrupted."""

    @classmethod
    def type(cls) -> str:
        """Returns the type of the frame."""
        return FLOW_PATTERN_CONTINUE_INTERRUPTED

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ContinueInterruptedPatternFlowStackFrame:
        """Creates a `DialogueStackFrame` from a dictionary.

        Args:
            data: The dictionary to create the `DialogueStackFrame` from.

        Returns:
            The created `DialogueStackFrame`.
        """
        return ContinueInterruptedPatternFlowStackFrame(
            frame_id=data["frame_id"],
            step_id=data["step_id"],
            previous_flow_name=data["previous_flow_name"],
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ContinueInterruptedPatternFlowStackFrame):
            return False
        return (
            self.flow_id == other.flow_id
            and self.step_id == other.step_id
            and self.previous_flow_name == other.previous_flow_name
        )


class ActionSetInterruptedFlows(Action):
    def name(self) -> str:
        return ACTION_SET_INTERRUPTED_FLOWS

    async def run(
        self,
        output_channel: OutputChannel,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracker,
        domain: Domain,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> list[Event]:
        interrupted_flows_set = set()
        interrupted_user_flow_stack_frames = tracker.stack.get_all_user_flow_frames()

        for frame in interrupted_user_flow_stack_frames:
            interrupted_flows_set.add(frame.flow_id)

        interrupted_flows = list(interrupted_flows_set)
        multiple_flows_interrupted = len(interrupted_flows) > 1

        return [
            SlotSet(INTERRUPTED_FLOWS_SLOT, interrupted_flows),
            SlotSet(MULTIPLE_FLOWS_INTERRUPTED_SLOT, multiple_flows_interrupted),
        ]


class ActionAskInterruptedFlowToContinue(Action):
    def name(self) -> str:
        return ACTION_ASK_INTERRUPTED_FLOW_TO_CONTINUE

    async def run(
        self,
        output_channel: OutputChannel,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracker,
        domain: Domain,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> List[Event]:
        interrupted_flows = tracker.get_slot(INTERRUPTED_FLOWS_SLOT) or []

        buttons = [
            {
                "title": flow_id,
                "payload": f'/SetSlots{{"{INTERRUPTED_FLOW_TO_CONTINUE_SLOT}": '
                f'"{flow_id}"}}',
            }
            for flow_id in interrupted_flows or []
        ]
        buttons.append(
            {
                "title": "None of them",
                "payload": f'/SetSlots{{"{INTERRUPTED_FLOW_TO_CONTINUE_SLOT}": '
                f'"none"}}',
            }
        )

        await output_channel.send_text_with_buttons(
            tracker.sender_id,
            "You previously started several other tasks. "
            "Would you like to resume any of them?",
            buttons=buttons,
        )

        return []


class ActionContinueInterruptedFlow(Action):
    def name(self) -> str:
        return ACTION_CONTINUE_INTERRUPTED_FLOW

    async def run(
        self,
        output_channel: OutputChannel,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracker,
        domain: Domain,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> List[Event]:
        from rasa.dialogue_understanding.commands import StartFlowCommand

        # get all necessary slot values
        multiple = tracker.get_slot(MULTIPLE_FLOWS_INTERRUPTED_SLOT)
        selected_flow = tracker.get_slot(INTERRUPTED_FLOW_TO_CONTINUE_SLOT)
        interrupted_flows = tracker.get_slot(INTERRUPTED_FLOWS_SLOT) or []

        original_user_frame = top_user_flow_frame(tracker.stack)

        # case of multiple interrupted flows, where the user selected a flow to continue
        if multiple:
            flow_id = selected_flow if selected_flow else None
        # case of single interrupted flow, so there is only one flow to continue
        else:
            flow_id = interrupted_flows[0] if interrupted_flows else None

        event_list = []
        if flow_id:
            # TODO: refactor to avoid creating a StartFlowCommand first
            # resume the flow with the provided flow id
            start_flow_command = StartFlowCommand(flow_id)
            event_list = start_flow_command.resume_flow(
                tracker, tracker.stack, original_user_frame
            )
        else:
            await output_channel.send_text_message(
                tracker.sender_id,
                "You haven't selected a valid task to resume. "
                "Please specify the task you would like to continue.",
            )

        return event_list


class ActionCancelInterruptedFlow(Action):
    def name(self) -> str:
        return ACTION_CANCEL_INTERRUPTED_FLOW

    async def run(
        self,
        output_channel: OutputChannel,
        nlg: NaturalLanguageGenerator,
        tracker: DialogueStateTracker,
        domain: Domain,
        metadata: Optional[Dict[Text, Any]] = None,
    ) -> List[Event]:
        from rasa.dialogue_understanding.commands import CancelFlowCommand

        interrupted_flows = tracker.get_slot(INTERRUPTED_FLOWS_SLOT) or []

        event_list = []
        for flow_id in interrupted_flows:
            # TODO: refactor to avoid creating a CancelFlowCommand first
            cancel_flow_command = CancelFlowCommand()
            event_list.extend(
                cancel_flow_command.cancel_flow(tracker, tracker.stack, flow_id)
            )

        return event_list + [
            SlotSet(INTERRUPTED_FLOWS_SLOT, None),
            SlotSet(INTERRUPTED_FLOW_TO_CONTINUE_SLOT, None),
            SlotSet(MULTIPLE_FLOWS_INTERRUPTED_SLOT, None),
            SlotSet(CONFIRMATION_CONTINUE_INTERRUPTED_FLOW_SLOT, None),
        ]
