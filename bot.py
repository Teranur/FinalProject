import os
import json
import requests
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus, WaterfallDialog, PromptOptions
from botbuilder.dialogs.prompts import TextPrompt
from botbuilder.core import TurnContext, MessageFactory

class CovUniChatBot(ActivityHandler):
    def __init__(self):
        self.endpoint = "https://pytonglingo.cognitiveservices.azure.com/language/:query-knowledgebases"
        self.api_key = "18c5e7bae1c24876a9ebd4db8f456a61"

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

    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text

        if not user_message:
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
                await turn_context.send_activity("Hello and welcome! Please type your question:")
