import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

import requests

def send_interactive_list(self, recipient_id, body_text, button_text, sections, header_text=None, footer_text=None):
    """
    Sends an interactive list message to a WhatsApp user
    Args:
        recipient_id[str]: Phone number of the user with country code wihout +
    check https://github.com/Neurotech-HQ/heyoo#sending-interactive-reply-buttons for an example.
    """
    interactive_dict = {}
    if header_text:
        interactive_dict["header"] = {"type": "text", "text": header_text}
    if footer_text:
        interactive_dict["footer"] = {"text": footer_text}
    if body_text:
        interactive_dict["body"] = {"text": body_text}

    interactive_dict["type"] = "list"
    interactive_dict["action"] = {}
    interactive_dict["action"]["button"] = button_text

    interactive_dict["action"]["sections"] = sections

    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": interactive_dict,
    }
    logging.info(f"Sending buttons to {recipient_id}")
    r = requests.post(self.url, headers=self.headers, json=data)
    if r.status_code == 200:
        logging.info(f"Buttons sent to {recipient_id}")
        return r.json()
    logging.info(f"Buttons not sent to {recipient_id}")
    logging.info(f"Status code: {r.status_code}")
    logging.info(f"Response: {r.json()}")
    return r.json()

def send_sticker(client, sticker : str, recipient_id: str, link=True):
    if link:
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "sticker",
            "sticker": {"link": sticker},
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "sticker",
            "sticker": {"id": sticker},
        }
    logging.info(f"Sending sticker to {recipient_id}")
    r = requests.post(client.url, headers=client.headers, json=data)
    if r.status_code == 200:
        logging.info(f"Sticker sent to {recipient_id}")
        return r.json()
    logging.info(f"Sticker not sent to {recipient_id}")
    logging.info(f"Status code: {r.status_code}")
    logging.error(f"Response: {r.json()}")
    return r.json()

def send_typing_indicator(client, message_id: str):
    """
    Sends a typing indicator to the user
    Args:
        message_id[str]: The ID of the message to send the typing indicator for
    """
    data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
            "typing_indicator": {
                "type": "text"
            }
            }
    r = requests.post(client.url, headers=client.headers, json=data)
    if r.status_code == 200:
        return r.json()
    logging.info(f"Status code: {r.status_code}")
    logging.error(f"Response: {r.json()}")
    return r.json()