import os
import json
import requests
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount, ActionTypes
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus, WaterfallDialog, PromptOptions, DialogState, DialogContext
from botbuilder.dialogs.prompts import TextPrompt, ChoicePrompt, ConfirmPrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.core import TurnContext, MessageFactory,UserState
from botbuilder.dialogs import WaterfallStepContext
from botbuilder.dialogs.prompts import PromptOptions
from botbuilder.schema import Attachment
from CustomDialogState import CustomDialogState


class CovUniChatBot(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.state_accessor = self.conversation_state.create_property("DialogState")
        self.endpoint = "https://pytonglingo.cognitiveservices.azure.com/language/:query-knowledgebases"
        self.api_key = "18c5e7bae1c24876a9ebd4db8f456a61"

        self.dialog_set = DialogSet(self.state_accessor)
        self.dialog_set.add(TextPrompt("text_prompt"))
        self.dialog_set.add(ChoicePrompt("choice_prompt"))

        waterfall_steps = [
            self.select_option_step,
            self.process_option_step
        ]
        self.dialog_set.add(WaterfallDialog("main_dialog", waterfall_steps))


    def query_knowledge_base(self, question):
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/json",
        }
        params = {
            "projectName": "pytong",
            "api-version": "2021-10-01",
            "deploymentName": "production",
        }
        data = {
            "top": 3,
            "question": question,
            "includeUnstructuredSources": True,
        }
        response = requests.post(self.endpoint, headers=headers, params=params, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_data_from_json(self, category, key):
        with open("data.json", "r") as f:
            data = json.load(f)

        if category in data and key in data[category]:
            return data[category][key]

        return None

    async def on_turn(self, turn_context: TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if dialog_context.active_dialog is not None:
            status = await dialog_context.continue_dialog()
        else:
            status = await dialog_context.begin_dialog("main_dialog")

        if status.status == DialogTurnStatus.Empty or status.status == DialogTurnStatus.Waiting:
            await self.conversation_state.save_changes(turn_context)
        elif status.status == DialogTurnStatus.Complete:
            # Reset the dialog state when the conversation is over
            await self.state_accessor.set(turn_context, {})
            await self.conversation_state.save_changes(turn_context)
            # Call on_message_activity() to process the message
            await self.on_message_activity(turn_context)

    
    async def select_option_step(self, step_context: WaterfallStepContext):
        card = {
            "type": "AdaptiveCard",
            "version": "1.0",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Please choose an option:",
                    "size": "medium",
                    "weight": "bolder",
                },
                {
                    "type": "ActionSet",
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Custom Question Answering",
                            "data": "Custom Question Answering",
                        },
                        {
                            "type": "Action.Submit",
                            "title": "Search data.json",
                            "data": "Search data.json",
                        },
                    ],
                },
            ],
        }
        message = MessageFactory.attachment(Attachment(content_type="application/vnd.microsoft.card.adaptive", content=card))
        return await step_context.prompt("text_prompt", PromptOptions(prompt=message))
   
    async def process_option_step(self, step_context):
        choice = step_context.result

        if choice == "Custom Question Answering":
            step_context.values["custom_answering"] = True
        elif choice == "Search data.json":
            step_context.values["custom_answering"] = False

        prompt_options = PromptOptions(prompt=MessageFactory.text("Please type your question:"))
        return await step_context.prompt("text_prompt", prompt_options)
    
    async def on_message_activity(self, turn_context: TurnContext):
        user_state_accessor = self.user_state.create_property("dialog_state")
        dialog_state = await user_state_accessor.get(turn_context, CustomDialogState)
        dialog_context = DialogContext(self.dialog_set, turn_context, dialog_state)

        if not turn_context.activity.text:
            return

        if dialog_context.active_dialog is not None:
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")

        await self.user_state.save_changes(turn_context)

# ...


        if dialog_context.active_dialog is None:
            return

        user_message = turn_context.activity.text

        if dialog_state.get("custom_answering"):
            response_json = self.query_knowledge_base(user_message)
            answers = response_json.get("answers")

            if answers and len(answers) > 0:
                reply = answers[0]["answer"]
                await turn_context.send_activity(MessageFactory.text(reply))
            else:
                await turn_context.send_activity(MessageFactory.text("Sorry, I didn't understand that."))

        elif not dialog_state.get("custom_answering"):
            if user_message.lower().startswith("get data "):
                try:
                    category, key = user_message[9:].split(" ", 1)
                    data_item = self.get_data_from_json(category, key)
                    if data_item:
                        if isinstance(data_item, dict):
                            reply = "\n".join([f"{k}: {v}" for k, v in data_item.items()])
                        else:
                            reply = str(data_item)
                        await turn_context.send_activity(MessageFactory.text(reply))
                        return
                    else:
                        await turn_context.send_activity(MessageFactory.text("Data not found."))
                        return
                except ValueError:
                    await turn_context.send_activity(MessageFactory.text("Invalid input. Please use the format: Get data CATEGORY KEY"))
                    return

        response_json = self.query_knowledge_base(user_message)
        answers = response_json.get("answers")

        if answers and len(answers) > 0:
            reply = answers[0]["answer"]
            await turn_context.send_activity(MessageFactory.text(reply))
        else:
            await turn_context.send_activity(MessageFactory.text("Sorry, I didn't understand that."))

    async def on_members_added_activity(self, members_added: ChannelAccount, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")
                await self.on_turn(turn_context)