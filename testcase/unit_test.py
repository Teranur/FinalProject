import sys
import pathlib
import pytest
import aiounittest
import asyncio

from botbuilder.dialogs.prompts import (
    AttachmentPrompt, 
    PromptOptions, 
    PromptValidatorContext, 
)
from botbuilder.core import (
    TurnContext, 
    ConversationState, 
    MemoryStorage, 
    MessageFactory, 
)
from botbuilder.schema import Activity, ActivityTypes, Attachment
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from email_prompt import EmailPrompt
from botbuilder.core.adapters import TestAdapter


class EmailPromptTest(aiounittest.AsyncTestCase):
    async def test_email_prompt(self):
        async def exec_test(turn_context : TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()
            if(results.status == DialogTurnStatus.Empty):
                options = PromptOptions(prompt=Activity(type=ActivityTypes.message,text="what is your email address?"))
                await dialog_context.prompt("email_prompt",options)
            elif results.status == DialogTurnStatus.Complete:
                reply = results.result
                await turn_context.send_activity(reply)



        adapter = TestAdapter(exec_test)
        
        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet()
        dialogs.add(EmailPrompt("email_prompt"))

        step1 = await adapter.test('hello','waht is your email address')
        step2 = await step1.send('my email address is choco@o2.pl')
        await step2.assert_reply('choco@o2.pl')