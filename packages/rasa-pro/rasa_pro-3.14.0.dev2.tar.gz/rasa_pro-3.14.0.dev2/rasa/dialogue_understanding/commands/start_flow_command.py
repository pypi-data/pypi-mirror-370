from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import structlog

from rasa.dialogue_understanding.commands.command import Command
from rasa.dialogue_understanding.commands.command_syntax_manager import (
    CommandSyntaxManager,
    CommandSyntaxVersion,
)
from rasa.dialogue_understanding.stack.dialogue_stack import DialogueStack
from rasa.dialogue_understanding.stack.frames.dialogue_stack_frame import (
    DialogueStackFrame,
)
from rasa.dialogue_understanding.stack.frames.flow_stack_frame import (
    AgentStackFrame,
    AgentState,
    FlowStackFrameType,
    UserFlowStackFrame,
)
from rasa.dialogue_understanding.stack.utils import (
    top_user_flow_frame,
    user_flows_on_the_stack,
)
from rasa.shared.core.events import (
    AgentInterrupted,
    AgentResumed,
    Event,
    FlowInterrupted,
    FlowResumed,
)
from rasa.shared.core.flows import FlowsList
from rasa.shared.core.trackers import DialogueStateTracker

structlogger = structlog.get_logger()


@dataclass
class StartFlowCommand(Command):
    """A command to start a flow."""

    flow: str

    @classmethod
    def command(cls) -> str:
        """Returns the command type."""
        return "start flow"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StartFlowCommand:
        """Converts the dictionary to a command.

        Returns:
            The converted dictionary.
        """
        try:
            return StartFlowCommand(flow=data["flow"])
        except KeyError as e:
            raise ValueError(
                f"Missing parameter '{e}' while parsing StartFlowCommand."
            ) from e

    def run_command_on_tracker(
        self,
        tracker: DialogueStateTracker,
        all_flows: FlowsList,
        original_tracker: DialogueStateTracker,
    ) -> List[Event]:
        """Runs the command on the tracker.

        Args:
            tracker: The tracker to run the command on.
            all_flows: All flows in the assistant.
            original_tracker: The tracker before any command was executed.

        Returns:
            The events to apply to the tracker.
        """
        stack = tracker.stack
        original_stack = original_tracker.stack
        applied_events: List[Event] = []

        if self.flow not in all_flows.flow_ids:
            structlogger.debug(
                "start_flow_command.skip_command.start_invalid_flow_id", command=self
            )
            return []

        original_user_frame = top_user_flow_frame(original_stack)
        original_top_flow = (
            original_user_frame.flow(all_flows) if original_user_frame else None
        )

        # if the original top flow is the same as the flow to start, the flow is
        # already active, do nothing
        if original_top_flow is not None and original_top_flow.id == self.flow:
            return []

        # if the flow is already on the stack, resume it
        if (
            self.flow in user_flows_on_the_stack(stack)
            and original_user_frame is not None
        ):
            return self.resume_flow(tracker, stack, original_user_frame)

        frame_type = FlowStackFrameType.REGULAR

        if original_top_flow:
            # if the original top flow is not the same as the flow to start,
            # interrupt the current active flow
            frame_type = FlowStackFrameType.INTERRUPT

            if original_user_frame is not None:
                applied_events.append(
                    FlowInterrupted(
                        original_user_frame.flow_id, original_user_frame.step_id
                    )
                )

            # If there is an active agent frame, interrupt it
            active_agent_stack_frame = stack.find_active_agent_frame()
            if active_agent_stack_frame:
                structlogger.debug(
                    "start_flow_command.interrupt_agent",
                    command=self,
                    agent_id=active_agent_stack_frame.agent_id,
                    frame_id=active_agent_stack_frame.frame_id,
                    flow_id=active_agent_stack_frame.flow_id,
                )
                active_agent_stack_frame.state = AgentState.INTERRUPTED
                applied_events.append(
                    AgentInterrupted(
                        active_agent_stack_frame.agent_id,
                        active_agent_stack_frame.flow_id,
                    )
                )

        structlogger.debug("start_flow_command.start_flow", command=self)
        stack.push(UserFlowStackFrame(flow_id=self.flow, frame_type=frame_type))
        return applied_events + tracker.create_stack_updated_events(stack)

    def __hash__(self) -> int:
        return hash(self.flow)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StartFlowCommand):
            return False

        return other.flow == self.flow

    def to_dsl(self) -> str:
        """Converts the command to a DSL string."""
        mapper = {
            CommandSyntaxVersion.v1: f"StartFlow({self.flow})",
            CommandSyntaxVersion.v2: f"start flow {self.flow}",
            CommandSyntaxVersion.v3: f"start flow {self.flow}",
        }
        return mapper.get(
            CommandSyntaxManager.get_syntax_version(),
            mapper[CommandSyntaxManager.get_default_syntax_version()],
        )

    @classmethod
    def from_dsl(cls, match: re.Match, **kwargs: Any) -> Optional[StartFlowCommand]:
        """Converts the DSL string to a command."""
        return StartFlowCommand(flow=str(match.group(1).strip()))

    @staticmethod
    def regex_pattern() -> str:
        mapper = {
            CommandSyntaxVersion.v1: r"StartFlow\(['\"]?([a-zA-Z0-9_-]+)['\"]?\)",
            CommandSyntaxVersion.v2: (
                r"""^[\s\W\d]*start flow ['"`]?([a-zA-Z0-9_-]+)['"`]*"""
            ),
            CommandSyntaxVersion.v3: (
                r"""^[\s\W\d]*start flow ['"`]?([a-zA-Z0-9_-]+)['"`]*"""
            ),
        }
        return mapper.get(
            CommandSyntaxManager.get_syntax_version(),
            mapper[CommandSyntaxManager.get_default_syntax_version()],
        )

    def resume_flow(
        self,
        tracker: DialogueStateTracker,
        stack: DialogueStack,
        original_user_frame: UserFlowStackFrame,
    ) -> List[Event]:
        """Resumes a flow by reordering frames."""
        applied_events: List[Event] = []

        # Resume existing flow by reordering frames
        frames_to_resume, user_frame_to_resume = self._collect_frames_to_resume(
            stack, self.flow
        )

        # if the flow is not on the stack, do nothing
        # this should not happen, but just in case
        if user_frame_to_resume is None:
            structlogger.error(
                "start_flow_command.resume_flow.no_user_frame_to_resume",
                command=self,
            )
            return []

        # move the frames to the top of the stack, e.g. reorder the frames
        # on the stack
        stack.move_frames_to_top(frames_to_resume)
        agent_stack_frame = next(
            (frame for frame in frames_to_resume if isinstance(frame, AgentStackFrame)),
            None,
        )
        if agent_stack_frame:
            agent_id = agent_stack_frame.agent_id
            applied_events.append(AgentResumed(agent_id, agent_stack_frame.flow_id))

        # Create flow interruption and resumption events
        applied_events.extend(
            [
                # the current active flow is interrupted
                FlowInterrupted(
                    original_user_frame.flow_id, original_user_frame.step_id
                ),
                # the flow, which was on the stack, is resumed
                FlowResumed(user_frame_to_resume.flow_id, user_frame_to_resume.step_id),
            ]
        )

        return applied_events + tracker.create_stack_updated_events(stack)

    def _collect_frames_to_resume(
        self, stack: DialogueStack, target_flow_id: str
    ) -> Tuple[List[DialogueStackFrame], Optional[UserFlowStackFrame]]:
        """Collect frames that need to be resumed for the target flow.

        Args:
            stack: The stack to collect frames from.
            target_flow_id: The ID of the flow to resume.

        Returns:
            A tuple containing (frames_to_resume, frame_to_resume).
        """
        frames_to_resume: List[DialogueStackFrame] = []
        frame_found = False
        frame_to_resume = None

        for frame in stack.frames:
            if isinstance(frame, UserFlowStackFrame) and (
                frame.frame_type == FlowStackFrameType.REGULAR
                or frame.frame_type == FlowStackFrameType.INTERRUPT
            ):
                if frame.flow_id == target_flow_id:
                    frames_to_resume.append(frame)
                    frame_to_resume = frame
                    frame_found = True
                    continue
                elif frame_found:
                    break

            if frame_found:
                frames_to_resume.append(frame)

        return list(frames_to_resume), frame_to_resume
