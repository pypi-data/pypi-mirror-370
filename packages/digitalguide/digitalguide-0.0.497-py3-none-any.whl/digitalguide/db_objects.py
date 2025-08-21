import mongoengine
import datetime

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

dbname = config["bot"]["bot_name"]
class WhatsAppUser(mongoengine.Document):
    ProfileName = mongoengine.StringField(required=True)
    WaId = mongoengine.StringField(required=True, max_length=50)
    entry_time = mongoengine.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    meta = {'db_alias': dbname}

class WhatsAppInteraction(mongoengine.Document):
    user = mongoengine.ReferenceField(WhatsAppUser)
    text = mongoengine.StringField()
    state = mongoengine.StringField()
    WaId = mongoengine.StringField()
    ProfileName = mongoengine.StringField()
    date = mongoengine.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc))
    meta = {'db_alias': dbname}

class WhatsAppUserContextState(mongoengine.Document):
    WaId = mongoengine.StringField(primary_key=True, db_field='_id')
    context = mongoengine.DictField()
    state = mongoengine.StringField()
    meta = {'db_alias': dbname}

class WhatsAppAction(mongoengine.Document):
    ActionName = mongoengine.StringField(primary_key=True)
    Action = mongoengine.ListField()
    meta = {'db_alias': dbname}

class WhatsAppHandler(mongoengine.Document):
    SateName = mongoengine.StringField(primary_key=True)
    Handlers = mongoengine.ListField()
    meta = {'db_alias': dbname}