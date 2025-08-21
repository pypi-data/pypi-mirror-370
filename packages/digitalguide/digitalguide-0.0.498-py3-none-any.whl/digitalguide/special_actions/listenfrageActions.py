from digitalguide.WhatsAppUpdate import WhatsAppUpdate
from digitalguide.generateActions import Action

def whatsapp_loop_list(client, update: WhatsAppUpdate, context,  key, value, doppelte_antwort):
    if not key in context:
        context[key] = []

    if value in context[key]:
        Action(doppelte_antwort)(client, update, context)
        return "{}_FRAGE".format(key.upper())
    else:
        context[key].append(value)

def whatsapp_loop_list_fertig(client, update: WhatsAppUpdate, context, key, answer_id_list, fertig_antwort):
    if set(answer_id_list).issubset(set(context[key])):
        Action(fertig_antwort)(client, update, context)

def whatsapp_eval_list(client, update: WhatsAppUpdate, context, answer_id_name_list, poi, response_text):
    if not poi in context:
        context[poi] = []

    response_text += "\n"

    for id, name in answer_id_name_list:
        if id in context[poi]:
            response_text += "✅ {}\n".format(name)
        else:
            response_text += "◽ {}\n".format(name)

    client.send_message(response_text, update.get_from())

whatsapp_action_functions = {"loop_list": whatsapp_loop_list,
                             "eval_list": whatsapp_eval_list,
                             "loop_list_fertig": whatsapp_loop_list_fertig
                             }
