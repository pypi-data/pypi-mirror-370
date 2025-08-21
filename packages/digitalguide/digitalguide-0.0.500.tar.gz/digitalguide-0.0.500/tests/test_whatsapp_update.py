import pytest
from digitalguide.WhatsAppUpdate import WhatsAppUpdate

def test_message_update():
    response = {'object': 'whatsapp_business_account', 'entry': [{'id': '108993638620871', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550504267', 'phone_number_id': '104884819035584'}, 'contacts': [{'profile': {'name': 'Sören'}, 'wa_id': '4917652163847'}], 'messages': [{'from': '4917652163847', 'id': 'wamid.HBgNNDkxNzY1MjE2Mzg0NxUCABIYFDNFQjBCMTIzMjc3MzAxRUE0QkJBAA==', 'timestamp': '1662911162', 'text': {'body': 'test'}, 'type': 'text'}]}, 'field': 'messages'}]}]}
    update =  WhatsAppUpdate(**response)
    assert(update.get_from()=="4917652163847")
    assert(update.get_message()._type == "text")
    assert(update.get_message_text() == "test")

def test_image_update():
    response = {'object': 'whatsapp_business_account', 'entry': [{'id': '108993638620871', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550504267', 'phone_number_id': '104884819035584'}, 'contacts': [{'profile': {'name': 'Sören'}, 'wa_id': '4917652163847'}], 'messages': [{'from': '4917652163847', 'id': 'wamid.HBgNNDkxNzY1MjE2Mzg0NxUCABIYFDNFQjAyNTk2NjBGQkJERTIzODFEAA==', 'timestamp': '1662911946', 'type': 'image', 'image': {'mime_type': 'image/jpeg', 'sha256': 'o95BYLgDj/EV6bQEcYuJlJ4gLUlhHQDVoZzBGBLNC/E=', 'id': '769823047618750'}}]}, 'field': 'messages'}]}]}
    update =  WhatsAppUpdate(**response)

def test_status_read_update():
    response = {'object': 'whatsapp_business_account', 'entry': [{'id': '108993638620871', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550504267', 'phone_number_id': '104884819035584'}, 'statuses': [{'id': 'wamid.HBgNNDkxNzY1MjE2Mzg0NxUCABEYEjUyNkVFRTAzQjBDNkY0MkFDQgA=', 'status': 'read', 'timestamp': '1662934933', 'recipient_id': '4917652163847'}]}, 'field': 'messages'}]}]}
    update =  WhatsAppUpdate(**response)
    assert(update.get_delivery() == "read")

def test_status_delivered_update():
    response = {'object': 'whatsapp_business_account', 'entry': [{'id': '108993638620871', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550504267', 'phone_number_id': '104884819035584'}, 'statuses': [{'id': 'wamid.HBgNNDkxNzY1MjE2Mzg0NxUCABEYEkY2MkJEMTAzMjU0OTk2QkYyOAA=', 'status': 'delivered', 'timestamp': '1662936587', 'recipient_id': '4917652163847', 'conversation': {'id': '6f5cf7b979575198977c5fe889d9af8f', 'origin': {'type': 'user_initiated'}}, 'pricing': {'billable': True, 'pricing_model': 'CBP', 'category': 'user_initiated'}}]}, 'field': 'messages'}]}]}
    update =  WhatsAppUpdate(**response)

def test_interactive_reply_update():
    response = {'object': 'whatsapp_business_account', 'entry': [{'id': '108993638620871', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550504267', 'phone_number_id': '104884819035584'}, 'contacts': [{'profile': {'name': 'Sören'}, 'wa_id': '4917652163847'}], 'messages': [{'context': {'from': '15550504267', 'id': 'wamid.HBgNNDkxNzY1MjE2Mzg0NxUCABEYEjM1MUQyRURDMzgxOTlEMDIxMwA='}, 'from': '4917652163847', 'id': 'wamid.HBgNNDkxNzY1MjE2Mzg0NxUCABIYFDNFQjA1RkJEQUU0OTU0MzQxQTk4AA==', 'timestamp': '1665912525', 'type': 'interactive', 'interactive': {'type': 'button_reply', 'button_reply': {'id': 'Weiter', 'title': 'Ja 🤩'}}}]}, 'field': 'messages'}]}]}
    update =  WhatsAppUpdate(**response)
    assert(update.get_message()._type == "interactive")
    assert(update.get_message_text() == "Ja 🤩")

def test_error_update():
    response = {'object': 'whatsapp_business_account', 'entry': [{'id': '108993638620871', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15550504267', 'phone_number_id': '104884819035584'}, 'statuses': [{'id': 'wamid.HBgMNDkxNzcxNzU3Nzg1FQIAERgSRjE0Njk1NzBDQTNCOTUxODNCAA==', 'status': 'failed', 'timestamp': '1666602770', 'recipient_id': '491771757785', 'errors': [{'code': 131047, 'title': 'Message failed to send because more than 24 hours have passed since the customer last replied to this number.', 'href': 'https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes/'}]}]}, 'field': 'messages'}]}]}
    update =  WhatsAppUpdate(**response)