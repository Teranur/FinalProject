import json
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ActionTypes, CardAction, SuggestedActions
from botbuilder.dialogs import DialogSet, DialogTurnStatus, WaterfallDialog, PromptOptions
from botbuilder.dialogs.prompts import TextPrompt
from botbuilder.dialogs import WaterfallStepContext

class SearchBot(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.state_accessor = self.conversation_state.create_property("DialogState")

        self.dialog_set = DialogSet(self.state_accessor)
        self.dialog_set.add(TextPrompt("text_prompt"))

        waterfall_steps = [
            self.ask_question_step,
            self.answer_question_step
        ]
        self.dialog_set.add(WaterfallDialog("main_dialog", waterfall_steps))

    def show_options_list(self, category):
        with open("data.json", "r") as f:
            data = json.load(f)

        if category == "Courses":
            options = "\n".join([f"{k}: {v['name']}" for k, v in data[category].items()])
        elif category == "History":
            options = "\n".join([f"{k}" for k in data[category]])
        elif category == "Buildings":
            options = "\n".join([f"{k}" for k, v in data[category].items()])
        else:
            options = None

        return options

    def get_data_from_json(self, category, key):
        with open("data.json", "r") as f:
            data = json.load(f)

        if category in data:
            if key in data[category]:
                return data[category][key]

        return None

    async def ask_question_step(self, step_context: WaterfallStepContext):
        # Create buttons for each category
        categories = ["Courses", "History", "Buildings"]
        category_buttons = [
            CardAction(title=category, type=ActionTypes.im_back, value=f"List {category}")
            for category in categories
        ]

        # Create a message with suggested actions (buttons)
        message = MessageFactory.text(
            "Please type your query in the format: 'Get data CATEGORY KEY' or click on a category button to display available options."
        )
        message.suggested_actions = SuggestedActions(actions=category_buttons)

        return await step_context.prompt("text_prompt", PromptOptions(prompt=message))

    async def answer_question_step(self, step_context: WaterfallStepContext):
        user_message = step_context.result
        response = None

        if user_message.lower().startswith("get data "):
            try:
                category, key = user_message[9:].split(" ", 1)
                data_item = self.get_data_from_json(category, key)
                if data_item:
                    if isinstance(data_item, dict):
                        response = "\n".join([f"{k}: {v}" for k, v in data_item.items()])
                    else:
                        response = str(data_item)
                else:
                    response = "Data not found."
            except ValueError:
                response = "Invalid input. Please use the format: Get data CATEGORY KEY"

        elif user_message.lower().startswith("list "):
            category = user_message[5:].strip()
            options = self.show_options_list(category)
            if options:
                response = f"Available options for {category}:\n\n{options}"
            else:
                response = "Invalid category. Please try again with a valid category."

        else:
            response = "Invalid command. Please use 'Get data CATEGORY KEY' or 'List CATEGORY'."

        await step_context.context.send_activity(response)
        return await step_context.replace_dialog("main_dialog")

    async def on_turn(self, turn_context: TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        results = await dialog_context.continue_dialog()
        if results.status == DialogTurnStatus.Empty:
            await dialog_context.begin_dialog("main_dialog")

        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

