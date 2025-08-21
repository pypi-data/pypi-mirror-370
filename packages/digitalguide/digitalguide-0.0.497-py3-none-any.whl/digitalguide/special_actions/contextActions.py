from digitalguide.WhatsAppUpdate import WhatsAppUpdate


def whatsapp_default_name(client, update: WhatsAppUpdate, context):
    context["name"] = update.entry[0].changes[0].value.contacts[0].profile_name


def whatsapp_save_text_to_context(client, update: WhatsAppUpdate, context, key):
    context[key] = update.get_message_text()


def whatsapp_save_value_to_context(client, update: WhatsAppUpdate, context, key, value):
    context[key] = value


whatsapp_action_functions = {"default_name": whatsapp_default_name,
                           "save_text_to_context": whatsapp_save_text_to_context,
                           "save_value_to_context": whatsapp_save_value_to_context
                           }
