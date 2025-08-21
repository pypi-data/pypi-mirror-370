import os
from configparser import ConfigParser
from datetime import datetime

import boto3
import requests

from digitalguide.WhatsAppUpdate import WhatsAppUpdate

config = ConfigParser()
config.read("config.ini")


def init_space():
    session = boto3.session.Session()
    s3_client = session.client('s3',
                            region_name=config["space"]["region_name"],
                            endpoint_url=config["space"]["endpoint_url"],
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))
    return s3_client


def whatsapp_write_photo(client, update: WhatsAppUpdate, context, bucket, folder):
    media_id = update.get_message().image.id
    get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

    media_url = get_media_response.json()["url"]
    media_mime_type = get_media_response.json()["mime_type"]

    media_response = requests.get(media_url, headers=client.headers)
    media_content = media_response.content
    extension = media_response.headers.get("Content-Disposition").split("filename=")[1].split(".")[-1]

    s3_client = init_space()
    user_id = update.get_from()

    s3_client.put_object(Bucket=bucket,
                    Key=folder + "/" +
                    str(datetime.now())+"_"+str(user_id) + "." + extension,
                    Body=media_content,
                    ContentType=media_mime_type,
                    ACL='private',
                    # Metadata={
                    #    'x-amz-meta-my-key': 'your-value'
                    # }
                    )


def whatsapp_write_message(client, update: WhatsAppUpdate, context, bucket, folder):
    message = update.get_message_text()

    s3_client = init_space()
    user_id = update.get_from()

    s3_client.put_object(Bucket=bucket,
                    Key=folder + "/" +
                    str(datetime.now())+"_"+str(user_id) + ".txt",
                    Body=message,
                    ContentType="text/plain",
                    ACL='private',
                    # Metadata={
                    #    'x-amz-meta-my-key': 'your-value'
                    # }
                    )


def whatsapp_write_voice(client, update: WhatsAppUpdate, context, bucket, folder):
    media_id = update.get_message().audio.id
    get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

    media_url = get_media_response.json()["url"]
    media_mime_type = get_media_response.json()["mime_type"]

    media_response = requests.get(media_url, headers=client.headers)
    media_content = media_response.content
    extension = media_response.headers.get("Content-Disposition").split("filename=")[1].split(".")[-1]

    s3_client = init_space()
    user_id = update.get_from()

    s3_client.put_object(Bucket=bucket,
                    Key=folder + "/" +
                    str(datetime.now())+"_"+str(user_id) + "." + extension,
                    Body=media_content,
                    ContentType=media_mime_type,
                    ACL='private',
                    # Metadata={
                    #    'x-amz-meta-my-key': 'your-value'
                    # }
                    )
    
def whatsapp_write_document(client, update: WhatsAppUpdate, context, bucket, folder):
    media_id = update.get_message().document.id
    get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

    media_url = get_media_response.json()["url"]
    media_mime_type = get_media_response.json()["mime_type"]

    media_response = requests.get(media_url, headers=client.headers)
    media_content = media_response.content
    extension = update.get_message().document.filename.split(".")[-1]

    s3_client = init_space()
    user_id = update.get_from()

    s3_client.put_object(Bucket=bucket,
                    Key=folder + "/" +
                    str(datetime.now())+"_"+str(user_id) + "." + extension,
                    Body=media_content,
                    ContentType=media_mime_type,
                    ACL='private',
                    # Metadata={
                    #    'x-amz-meta-my-key': 'your-value'
                    # }
                    )
    
def whatsapp_write_video(client, update: WhatsAppUpdate, context, bucket, folder):
    media_id = update.get_message().video.id
    get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

    media_url = get_media_response.json()["url"]
    media_mime_type = get_media_response.json()["mime_type"]

    media_response = requests.get(media_url, headers=client.headers)
    media_content = media_response.content
    extension = update.get_message().document.filename.split(".")[-1]

    s3_client = init_space()
    user_id = update.get_from()

    s3_client.put_object(Bucket=bucket,
                    Key=folder + "/" +
                    str(datetime.now())+"_"+str(user_id) + "." + extension,
                    Body=media_content,
                    ContentType=media_mime_type,
                    ACL='private',
                    # Metadata={
                    #    'x-amz-meta-my-key': 'your-value'
                    # }
                    )

def whatsapp_write(client, update: WhatsAppUpdate, context, bucket, folder):
    if update.get_message().type == "audio":
        whatsapp_write_voice(client, update, context, bucket, folder)
    elif  update.get_message().type == "image":
        whatsapp_write_photo(client, update, context, bucket, folder)
    elif  update.get_message().type == "document":
        whatsapp_write_document(client, update, context, bucket, folder)
    elif  update.get_message().type == "video":
        whatsapp_write_video(client, update, context, bucket, folder)
    elif update.get_message_text() != "":
        whatsapp_write_message(client, update, context, bucket, folder)
    else:
        raise NotImplementedError("This type of update can not be saved")

whatsapp_action_functions = {"write_photo": whatsapp_write_photo,
                             "write_message": whatsapp_write_message,
                             "write_voice": whatsapp_write_voice,
                             "write_document": whatsapp_write_document,
                             "write": whatsapp_write
                             }
