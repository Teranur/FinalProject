from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, ActionTypes, CardAction, HeroCard, Attachment

class MyBot(ActivityHandler):
    def __init__(self):
        self.choices = {
            "Courses": {
                "Course11": {
                    "name": "Course 11 - Full Name",
                    "modules": {
                        "Module11": "Module 11 - Introduction",
                        "Module12": "Module 12 - Introduction"
                    }
                },
                "Course12": {
                    "name": "Course 12 - Full Name",
                    "modules": {
                        "Module21": "Module 21 - Introduction",
                        "Module22": "Module 22 - Introduction"
                    }
                }
            },
            "History": ["Founding", "Mission"],
            "Buildings": ["John Lang", "Jaguar"]
        }
        self.current_choice = None
        self.current_course = None

    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text

        if self.current_choice is None:
            if user_message in self.choices:
                await self.send_list_of_choices(turn_context, user_message)
            else:
                await turn_context.send_activity(f"'{ user_message }'")
        elif self.current_choice == "Courses":
            if user_message in self.choices["Courses"]:
                self.current_course = user_message
                await self.send_list_of_modules(turn_context, user_message)
            else:
                await turn_context.send_activity(f"'{ user_message }', please select a course")
        elif self.current_course:
            if user_message in self.choices["Courses"][self.current_course]["modules"]:
                await self.send_module_info(turn_context, user_message)
            else:
                await turn_context.send_activity(f"'{ user_message }', please select a module")
        else:
            await turn_context.send_activity(f"'{ user_message }', please select an option")

    async def send_list_of_choices(self, turn_context: TurnContext, option: str):
        self.current_choice = option

        buttons = []
        if option == "Courses":
            for course_code, course_info in self.choices[option].items():
                buttons.append(CardAction(type=ActionTypes.im_back, title=course_code, value=course_code))
        else:
            for choice in self.choices[option]:
                buttons.append(CardAction(type=ActionTypes.im_back, title=choice, value=choice))

        card = HeroCard(title=f"Choose a {option} option", buttons=buttons)
        attachment = Attachment(content_type="application/vnd.microsoft.card.hero", content=card)
        message = MessageFactory.attachment(attachment)
        await turn_context.send_activity(message)

    async def send_list_of_modules(self, turn_context: TurnContext, course_code: str):
        buttons = []
        for module_code, module_intro in self.choices["Courses"][course_code]["modules"].items():
            buttons.append(CardAction(type=ActionTypes.im_back, title=module_code, value=module_code))

        card = HeroCard(title=f"Choose a module for {self.choices['Courses'][course_code]['name']}:", buttons=buttons)
        attachment = Attachment(content_type="application/vnd.microsoft.card.hero", content=card)
        message = MessageFactory.attachment(attachment)
        await turn_context.send_activity(message)

    async def send_module_info(self, turn_context: TurnContext, module_code: str):
        module_intro = self.choices["Courses"][self.current_course]["modules"][module_code]

        card = HeroCard(
        title=f"{module_code} - Introduction",
        text=module_intro
        )
        attachment = Attachment(content_type="application/vnd.microsoft.card.hero", content=card)
        message = MessageFactory.attachment(attachment)
        await turn_context.send_activity(message)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                card = HeroCard(
                    title="Welcome to the Coventry University Primer Bot!",
                    text="Choose an option:",
                    buttons=[
                        CardAction(
                            type=ActionTypes.im_back,
                            title="Courses",
                            value="Courses"
                        ),
                        CardAction(
                            type=ActionTypes.im_back,
                            title="History",
                            value="History"
                        ),
                        CardAction(
                            type=ActionTypes.im_back,
                            title="Buildings",
                            value="Buildings"
                        )
                    ]
                )
                attachment = Attachment(content_type="application/vnd.microsoft.card.hero", content=card)
                message = MessageFactory.attachment(attachment)
                await turn_context.send_activity(message)

