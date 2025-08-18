from pydantic import BaseModel, Field, model_validator
from enum import StrEnum
from datetime import datetime
from typing import List, Optional
from .chain_of_thought_in_chat import ChainOfThoughtInChatRequest
from ....messages.chatty_messages.base.message_draft import MessageDraft
from letschatty.models.company.assets.ai_agents_v2.chatty_ai_agent import ChattyAIAgent

class SmartFollowUpDecisionAction(StrEnum):
    """Action for the smart follow up"""
    SEND = "send"
    SKIP = "skip"
    SUGGEST = "suggest"
    REMOVE = "remove"
    ESCALATE = "escalate"

class SmartFollowUpDecision(BaseModel):
    """Decision for the smart follow up"""
    action: SmartFollowUpDecisionAction = Field(description="The action for the smart follow up")
    next_call_time: Optional[datetime] = Field(description="The next call time for the smart follow up", default=None)
    messages : Optional[List[MessageDraft]] = Field(description="The messages to send to the chat", default=[])
    chain_of_thought: ChainOfThoughtInChatRequest = Field(description="The chain of thought for the smart follow up")

    @property
    def next_call_time_value(self) -> datetime:
        if self.next_call_time is None:
            raise ValueError("Next call time is required")
        return self.next_call_time

    @model_validator(mode="after")
    def validate_messages(self):
        if self.action == SmartFollowUpDecisionAction.SEND or self.action == SmartFollowUpDecisionAction.SUGGEST:
            if self.messages is None or len(self.messages) == 0:
                raise ValueError("Messages are required when action is send or suggest")
        else:
            if self.messages is not None and len(self.messages) > 0:
                raise ValueError("Messages are not allowed when action is skip or remove")
        return self

    def set_chain_of_thought_id(self, chain_of_thought_id: str):
        if self.messages:
            for message in self.messages:
                message.context_value.chain_of_thought_id = chain_of_thought_id

    @property
    def messages_to_send(self) -> List[MessageDraft]:
        if not self.messages:
            raise ValueError("Messages are required when action is send or suggest")
        return self.messages


class IncomingMessageDecisionAction(StrEnum):
    """Action for the chat ai decision"""
    SEND = "send"
    SKIP = "skip"
    SUGGEST = "suggest"
    ESCALATE = "escalate"

class IncomingMessageAIDecision(BaseModel):
    """Decision for the chat ai"""
    action: IncomingMessageDecisionAction = Field(description="The action for the chat ai decision")
    messages : Optional[List[MessageDraft]] = Field(description="The messages to send to the chat", default=[])
    chain_of_thought: ChainOfThoughtInChatRequest = Field(description="The chain of thought for the smart follow up")

    @model_validator(mode="after")
    def validate_messages(self):
        if self.action == SmartFollowUpDecisionAction.SEND or self.action == SmartFollowUpDecisionAction.SUGGEST:
            if self.messages is None or len(self.messages) == 0:
                raise ValueError("Messages are required when action is send or suggest")
        else:
            if self.messages is not None and len(self.messages) > 0:
                raise ValueError("Messages are not allowed when action is skip or remove")
        return self

    @property
    def messages_to_send(self) -> List[MessageDraft]:
        if not self.messages:
            raise ValueError("Messages are required when action is send or suggest")
        return self.messages

    def set_chain_of_thought_id(self, chain_of_thought_id: str):
        if self.messages:
            for message in self.messages:
                message.context_value.chain_of_thought_id = chain_of_thought_id