import json
import os
import re
from configparser import ConfigParser
from typing import List

import requests as req
from digitalguide.pattern import (EMOJI_PATTERN, JA_PATTERN, JAHRESZAHL_PATTERN, KOMMAZAHL_PATTERN, NEIN_PATTERN,
                                  WEITER_PATTERN, WOHIN_PATTERN, ZURUECK_PATTERN, DATENSCHUTZ_PATTERN)
from digitalguide.WhatsAppUpdate import WhatsAppUpdate

import logging
logger = logging.getLogger(__name__).addHandler(logging.NullHandler())

def read_state(handlers, prechecks: List = []):
    handler_list = prechecks[:]
    for handler in handlers:
        if handler["handler"] == "PollAnswerHandler":
            newHandler = MessageHandler(RegexFilter(
                "^(.)+"), handler["action"])
        elif handler["handler"] == "MessageHandler":
            if handler["filter"] == "regex":
                if handler["regex"] == "EMOJI_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(EMOJI_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "WEITER_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(WEITER_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "WOHIN_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(WOHIN_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "JA_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(JA_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "NEIN_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(NEIN_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "ZURUECK_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(ZURUECK_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "JAHRESZAHL_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(JAHRESZAHL_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "KOMMAZAHL_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)), handler["action"])
                elif handler["regex"] == "DATENSCHUTZ_PATTERN":
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(DATENSCHUTZ_PATTERN,re.IGNORECASE)), handler["action"])
                else:
                    newHandler = MessageHandler(RegexFilter(
                        re.compile(handler["regex"],re.IGNORECASE)), handler["action"])
            elif handler["filter"] == "text":
                newHandler = MessageHandler(
                    TextFilter(), handler["action"])
            elif handler["filter"] == "photo":
                newHandler = MessageHandler(
                    PhotoFilter(), handler["action"])
            elif handler["filter"] == "voice":
                newHandler = MessageHandler(
                    VoiceFilter(), handler["action"])
            elif handler["filter"] == "rasa":
                newHandler = MessageHandler(FilterRasa(
                    handler["intent"]), handler["action"])
            else:
                raise NotImplementedError(
                    "This Filter is not implemented: {}".format(handler["filter"]))
        elif handler["handler"] == "CommandHandler":
            newHandler = CommandHandler(
                handler["command"], handler["action"])
        elif handler["handler"] == "TypeHandler":
            if handler["type"] == "Update":
                type_ = WhatsAppUpdate
            else:
                raise NotImplementedError(
                "This Updatetype is not implemented: {}".format(handler["type"]))
            newHandler = TypeHandler(type_, handler["action"])
        else:
            raise NotImplementedError(
                "This Handler is not implemented: {}".format(handler["handler"]))

        handler_list.append(newHandler)

    return handler_list


class MessageHandler:
    def __init__(self, filters, callback):
        self.filters = filters
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        return self.filters(update)


class CommandHandler:
    def __init__(self, command, callback):
        self.command = command
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        if update.get_message_text() != "" and update.get_message_text().strip("/").lower() == self.command.lower():
            return True


class TypeHandler:
    def __init__(self, type_, callback):
        self.type_ = type_
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        return type(update) is self.type_


class RegexFilter:
    def __init__(self, regex) -> None:
        self.regex = regex

    def __call__(self, update: WhatsAppUpdate) -> bool:
        if update.get_message_text() != "":
            return re.search(self.regex, update.get_message_text())
        else:
            return False


class TextFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.get_message_text() != ""


class PhotoFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.get_message()._type == "image"


class VoiceFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.get_message()._type == "audio"


config = ConfigParser()
config.read('config.ini')


class FilterRasa:
    def __init__(self, intent, confidence=0.8):
        self.intent = intent
        self.confidence = confidence

    def __call__(self, update: WhatsAppUpdate):
        if self.intent == "weiter":
            return True
        else:
            return False

        #if update.get_message_text() == "":
        #    return False
        #try:
        #    payload = json.dumps({
        #        "username": os.getenv('RASA_USER'),
        #        "password": os.getenv('RASA_PASSWORD')
        #    })

        #    token_response = req.post(
        #        config["rasa"]["url"] + "/api/auth", data=payload, timeout=1)

        #    RASA_TOKEN = token_response.json()["access_token"]
        #    response = req.post(config["rasa"]["url"] + "/api/projects/default/logs", params={
        #                        "q": update.get_message_text()}, headers={'Authorization': 'Bearer {}'.format(RASA_TOKEN)},  timeout=(3, 8))
        #    logging.info(response.json())
        #except Exception as e:
        #    logging.debug(e)
        #    return False
        #else:
        #    if not response.ok:
        #        return False
        #    return response.json()["user_input"]["intent"]["name"] == self.intent and response.json()["user_input"]["intent"]["confidence"] >= self.confidence
