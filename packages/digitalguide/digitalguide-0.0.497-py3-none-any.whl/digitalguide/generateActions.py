import requests
import os
from digitalguide.WhatsAppUpdate import WhatsAppUpdate
from digitalguide.send_utils import send_interactive_list, send_sticker, send_typing_indicator

import redis
from time import sleep

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

redis_url=os.environ.get("REDIS_URL")
r_unsend_messages = redis.from_url(redis_url, decode_responses=True)

class Action():
    def __init__(self, actions, action_functions={}):
        self.actions = actions
        self.action_functions = action_functions
        
    def __call__(self, client, update: WhatsAppUpdate, context):
        send_typing_indicator(client, update.get_message().id)
        if not ("user_id" in context.keys()):
            from digitalguide.db_objects import WhatsAppUser
            db_user = WhatsAppUser(ProfileName=update.entry[0].changes[0].value.contacts[0].profile_name,
                                   WaId=update.get_from())
            db_user.save()
            context["user_id"] = db_user

        
        from digitalguide.db_objects import WhatsAppInteraction
        WhatsAppInteraction(user=context["user_id"],
                            ProfileName=update.entry[0].changes[0].value.contacts[0].profile_name,
                            WaId=update.get_from(),
                            text=update.get_message_text(),
                            state=context["state"]
                            ).save()

        for item in self.actions:
            send_typing_indicator(client, update.get_message().id)
            if item["type"] == "return":
                return item["state"]
            
            max_wait_itteration = 100
            for i in range(max_wait_itteration):
                logging.info("unsend messages iterration {}: {}".format(i, r_unsend_messages.get(update.get_from())))
                if not r_unsend_messages.get(update.get_from()):
                    logging.info("BREAK")
                    break
                sleep(.1)
            else:
                logging.info("Previous messages were not send within {} ms.".format(max_wait_itteration))

            try:
                result_json = None
                if item["type"] == "message":
                    placeholder_dict = {**context}
                    placeholder_dict["profile_name"] = update.entry[0].changes[0].value.contacts[0].profile_name
                    placeholder_dict["echo"] = update.get_message_text()

                    if "reply_buttons" in item.keys():
                        buttons = []

                        for button in item["reply_buttons"]:
                            buttons.append({
                                "type": "reply",
                                "reply": {
                                    "id": button["id"],
                                    "title": button["text"]
                                }
                            })

                        button_dict = {
                            "type": "button",
                                    "body": {
                                        "text": item["text"].format(**placeholder_dict)
                                    },
                            "action": {
                                        "buttons": buttons
                                    }
                        }

                        if "footer" in item.keys():
                            button_dict["footer"] = {"text": item["footer"]}

                        result_json = client.send_reply_button(recipient_id=update.get_from(),
                                                            button=button_dict)

                    elif "button" in item.keys() and "section_title" in item.keys():
                        section_dict = [
                            {
                                "title": item["section_title"],
                                "rows": [],
                            }
                        ]

                        for row in item["rows"]:
                            row_dict = {"id": row["id"],
                                        "title": row["title"],
                                        "description": row.get("description", "")}
                            section_dict[0]["rows"].append(
                                row_dict)

                        result_json = send_interactive_list(client,
                                            recipient_id=update.get_from(),
                                            body_text=item["text"].format(
                                                **placeholder_dict),
                                            button_text=item["button"],
                                            sections=section_dict,
                                            header_text=item.get("header", None),
                                            footer_text=item.get("footer", None))

                    else:
                        client.send_message(item["text"].format(
                            **placeholder_dict), update.get_from())

                elif item["type"] == "venue":
                    result_json = client.send_location(
                        name=item["title"],
                        lat=item["latitude"],
                        long=item["longitude"],
                        address=item["address"],
                        recipient_id=update.get_from()
                    )
                elif item["type"] == "photo":
                    if "caption" in item.keys():
                        caption = item["caption"]
                    else:
                        caption = None
                    if "url" in item.keys():
                        result_json = client.send_image(
                            item["url"],
                            update.get_from(),
                            caption=caption
                        )
                    else:
                        result_json = client.send_image(
                            item["id"],
                            update.get_from(),
                            link=False,
                            caption=caption
                        )
                elif item["type"] == "video":
                    result_json = client.send_video(
                        item["url"],
                        update.get_from()
                    )
                elif item["type"] == "sticker":
                    result_json = send_sticker(client,
                        item["url"],
                        update.get_from()
                    )
                elif item["type"] == "media_group":
                    pass
                    # message = client.messages.create(
                    #    media_url=item["urls"],
                    #    from_=update.To,
                    #    to=update.From
                    # )
                elif item["type"] == "audio" or item["type"] == "voice":
                    if "url" in item.keys():
                        result_json = client.send_audio(
                            item["url"],
                            update.get_from()
                        )
                    else:
                        result_json = client.send_audio(
                            item["id"],
                            update.get_from(),
                            link=False
                        )
                elif item["type"] == "poll":
                    message = item["question"] + "\n"
                    for option in item["options"]:
                        message += option + "\n"
                    result_json = client.send_message(message, update.get_from())

                elif item["type"] == "function":
                    arguments = {i: item[i]
                                for i in item if i != 'type' and i != 'func'}
                    if item["func"] in self.action_functions.keys():
                        self.action_functions[item["func"]](
                            client, update, context, **arguments)
                    else:
                        module, function = item["func"].split(":")

                        if module == "contextActions":
                            from digitalguide.special_actions import contextActions
                            contextActions.whatsapp_action_functions[function](client, update, context, **arguments)
                        elif module == "imageActions":
                            from digitalguide.special_actions import imageActions
                            imageActions.whatsapp_action_functions[function](client, update, context, **arguments)
                        elif module == "listenfrageActions":
                            from digitalguide.special_actions import listenfrageActions
                            listenfrageActions.whatsapp_action_functions[function](client, update, context, **arguments)
                        elif module == "schaetzfragenActions":
                            from digitalguide.special_actions import schaetzfragenActions
                            schaetzfragenActions.whatsapp_action_functions[function](client, update, context, **arguments)
                        elif module == "writeActions":
                            from digitalguide.special_actions import writeActions
                            writeActions.whatsapp_action_functions[function](client, update, context, **arguments)
                
                if result_json:
                    r_unsend_messages.set(update.get_from(), result_json["messages"][0]["id"], ex=10)
            except Exception as e:
                logging.exception("Error during the Execution of action: {item}")
    