import logging

# Setup logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

class WhatsAppEntry:
    '''
    An array of entry objects. Entry objects have the following properties:

    id — String. The WhatsApp Business Account ID for the business that is subscribed to the webhook.
    changes — Array of WhatsAppChange objects. An array of change objects. 
    '''
    def __init__(self, id, changes) -> None:
        self.id = id
        self.changes = [WhatsAppChange(**change) for change in changes]


class WhatsAppChange:
    '''
    value — Object. A value object. See Value Object.
    field — String. Notification type. Value will be messages.
    '''
    def __init__(self, value, field):
        self.value = WhatsAppValue(**value)
        self.field = field


class WhatsAppValue:
    '''
    The value object contains details for the change that triggered the webhook. This object is nested within the changes array of the entry array.

    contacts - array of objects: Array of contact objects with information for the customer who sent a message to the business.
    errors - array of objects: An array of error objects describing the error.
    messaging_product - string: Product used to send the message. Value is always whatsapp.
    messages - array of objects: Information about a message received by the business that is subscribed to the webhook.
    metadata - object: A metadata object describing the business subscribed to the webhook.
    statuses - array of objects: Status object for a message that was sent by the business that is subscribed to the webhook.

    '''

    def __init__(self, metadata, contacts:list=[], messaging_product:str="whatsapp", messages:list=[], statuses:list=[], errors:list=[]):
        self.contacts = [WhatsAppContact(**contact) for contact in contacts]
        self.messaging_product = messaging_product
        messages_list = []
        for message in messages:
            message["_from"] = message["from"]
            del message["from"]
            messages_list.append(message)
        self.messages = [WhatsAppMessage(**message)
                         for message in messages_list]
        self.metadata = WhatsAppMetadata(**metadata)
        self.statuses = [WhatsAppStatus(**status) for status in statuses]
        if errors:
            self.errors = [WhatsAppError(**error)
                            for error in errors]

class WhatsAppContact:
    '''
    wa_id — String. The customer's WhatsApp ID. A business can respond to a message using this ID.
    profile — Object. A customer profile object. Profile objects have the following properties:
        name — String. The customer's name.
    '''
    def __init__(self, wa_id:str, profile:dict) -> None:
        self.wa_id = wa_id
        self.profile_name = profile["name"]


class WhatsAppError:
    '''
    Error objects have the following properties, which map to their equivalent properties in API error response payloads.

    Webhooks triggered by v15.0 and older requests:

    code — Integer. Example: 130429.
    title — String. Error code title. Example: Rate limit hit.

    Webhooks triggered by v16.0 and newer requests:

    code — Integer. Error code. Example: 130429.
    title — String. Error code title. Example: Rate limit hit.
    message — String. Error code message. This value is the same as the title value. For example: Rate limit hit. Note that the message property in API error response payloads pre-pends this value with the a # symbol and the error code in parenthesis. For example: (#130429) Rate limit hit.
    error_data — Object. An error data object with the following properties:
    details — String. Describes the error. Example: Message failed to send because there were too many messages sent from this phone number in a short period of time.
    '''

    def __init__(self, code:int, title:str, href:str="", message:str="", error_data:dict=None) -> None:
        self.code = code
        self.title = title
        self.href = href
        self.message = message
        if error_data:
            self.error_data_details = error_data["details"]
        else:
            self.error_data_details = None


class WhatsAppMessage:
    '''
    audio - object: When the messages type is set to audio, including voice messages
    button - object: When the messages type field is set to button, this object is included in the messages object
    context - object: Context object. Only included when a user replies or interacts with one of your messages. #Todo
    document - object: A document object. When messages type is set to document, this object is included in the messages object.
    errors - array of objects: An array of error objects describing the error.
    _from - string: The customer's phone number who sent the message to the business.
    id - string: The ID for the message that was received by the business. You could use messages endpoint to mark this specific message as read.
    identity - object: An identity object. Webhook is triggered when a customer's phone number or profile information has been updated. #Todo
    image - object: When messages type is set to image
    interactive - object: When a customer has interacted with your message, this object is included in the messages object. #Todo
    order - object: Included in the messages object when a customer has placed an order. #Todo
    referral - object: Referral object. When a customer clicks an ad that redirects to WhatsApp, this object is included in the messages object.
    '''

    def __init__(self, _from, id, timestamp, type, audio=None, button=None, context=None, document=None, errors=None, identity=None, image=None, interactive=None, order=None, referral=None, sticker=None, system=None, text=None, video=None) -> None:
        self.type = type

        if type == "audio":
            self.audio = WhatsAppAudio(**audio)
        elif type == "button":
            self.button = WhatsAppButton(**button)
        elif type == "text":
            self.text = text["body"]
        elif type == "document":
            self.document = WhatsAppDocument(**document)
        elif type == "image":
            self.image = WhatsAppImage(**image)
        
        self.context = context
        if errors:
            self.errors = [WhatsAppError(**error)
                            for error in errors]
        self._from = _from
        self.id = id
        self.identity = identity
        self.interactive = interactive
        self.order = order
        self.referral = referral
        self.sticker = sticker
        self.system = system
        self.timestamp = timestamp
        self._type = type
        self.video = video

class WhatsAppImage:
    '''
    caption — String. Caption for the image, if provided.
    sha256 — String. Image hash.
    id — String. ID for the image.
    mime_type — String. Mime type for the image.
    '''
    
    def __init__(self, id: str, mime_type: str, sha256: str, caption: str=None) -> None:
        self.id = id
        self.mime_type = mime_type
        self.sha256 = sha256
        self.caption = caption

class WhatsAppDocument:
    '''
    caption — String. Caption for the document, if provided.
    filename — String. Name for the file on the sender's device.
    sha256 — String. SHA 256 hash.
    mime_type — _String. _ Mime type of the document file.
    id — String. ID for the document.
    '''
    
    def __init__(self, id: str, mime_type: str, sha256: str, filename: str, caption: str=None) -> None:
        self.id = id
        self.mime_type = mime_type
        self.sha256 = sha256
        self.filename = filename
        self.caption = caption

class WhatsAppAudio:
    '''
    id — String. ID for the audio file.
    mime_type — String. Mime type of the audio file.
    sha256 - String #Missing in Facebook Documentation
    voice - String #Missing in Facebook Documentation
    '''
    def __init__(self, id:str, mime_type:str, sha256: str, voice: str) -> None:
        self.id = id
        self.mime_type = mime_type
        self.sha256 = sha256
        self.voice = voice


class WhatsAppButton:
    '''
    payload — String. The payload for a button set up by the business that a customer clicked as part of an interactive message.
    text — String. Button text.
    '''
    def __init__(self, payload:str, text:str) -> None:
        self.payload = payload
        self.text = text


class WhatsAppMetadata:
    '''
    display_phone_number — String. The phone number that is displayed for a business.
    phone_number_id — String. ID for the phone number. A business can respond to a message using this ID.
    '''
    def __init__(self, display_phone_number:str, phone_number_id:str) -> None:
        self.display_phone_number = display_phone_number
        self.phone_number_id = phone_number_id


class WhatsAppStatus:
    def __init__(self, id, recipient_id, status, timestamp, errors=[], conversation=None, pricing=None) -> None:
        if conversation:
            self.conversation = WhatsAppConversation(**conversation)
        self.id = id
        if pricing:
            self.pricing_category = pricing["category"]
            self.pricing_model = pricing["pricing_model"]
        if errors:
            self.errors = [WhatsAppError(**error) for error in errors]
        self.recipient_id = recipient_id
        self.status = status
        self.timestamp = timestamp


class WhatsAppConversation:
    def __init__(self, id, origin, expiration_timestamp=None) -> None:
        self.id = id
        self.origin_type = origin["type"]
        if expiration_timestamp:
            self.expiration_timestamp = expiration_timestamp

class WhatsAppUpdate:
    '''
    object - string: The specific webhook a business is subscribed to. The webhook is whatsapp_business_account.
    entry - array of WhatsAppEntry objects: An array of entry objects.
    '''

    def __init__(self, object:str, entry:list[dict]) -> None:
        self.object = object
        self.entry = [WhatsAppEntry(**e) for e in entry]

    def get_from(self) -> str:
        if self.entry[0].changes[0].value.contacts:
            return self.entry[0].changes[0].value.contacts[0].wa_id
        elif self.entry[0].changes[0].value.statuses:
            return self.entry[0].changes[0].value.statuses[0].recipient_id

    def get_message(self) -> WhatsAppMessage:
        return self.entry[0].changes[0].value.messages[0]

    def get_message_text(self) -> str:
        message = self.entry[0].changes[0].value.messages[0]
        if message._type == "text":
            return message.text
        elif message._type == "interactive":
            if message.interactive["type"] == "button_reply":
                return message.interactive["button_reply"]["title"]
            elif message.interactive["type"] == "list_reply":
                if "description" in message.interactive["list_reply"]:
                    return "{} {}".format(message.interactive["list_reply"]["title"], message.interactive["list_reply"]["description"])
                else:
                    return "{}".format(message.interactive["list_reply"]["title"])
            else:
                logging.warning("There is no message text defined for this interactive type: {}".format(
                    message.interactive["type"]))
                return ""
        else:
            logging.warning("There is no message text defined for this message type: {}".format(
                message._type))
            return ""

    def get_delivery(self):
        if self.entry[0].changes[0].value.statuses:
            return self.entry[0].changes[0].value.statuses[0].status
