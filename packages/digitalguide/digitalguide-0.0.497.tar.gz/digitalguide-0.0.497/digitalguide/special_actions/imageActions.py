from PIL import Image
from io import BytesIO

from digitalguide.WhatsAppUpdate import WhatsAppUpdate
from configparser import ConfigParser

from time import sleep
import requests

config = ConfigParser()
config.read("config.ini")

def generate_gif(im1, im2):
    im1 = im1.resize((512, 512))
    im2 = im2.resize((512, 512))

    im2 = im2.convert(im1.mode)


    images = []
    frames = 5

    for i in range(frames+1):
        im = Image.blend(im1, im2, i/frames)
        images.append(im)

    for i in range(frames+1):
        im = Image.blend(im1, im2, 1-i/frames)
        images.append(im)

    bio = BytesIO()
    bio.name = 'image.webp'

    images[0].save(bio, 'webp', save_all=True,
                   append_images=images[1:], duration=500, loop=0, optimize=True, quality=50, minimize_size=True)
    bio.seek(0)
    return bio


def overlay_images(background, foreground, x_position="left", y_position="up", resize=True):
    x_scale_ratio = foreground.size[0]/background.size[0]
    y_scale_ratio = foreground.size[1]/background.size[1]
    
    if x_scale_ratio >= y_scale_ratio:
        scale_ratio = foreground.size[0]/background.size[0]
        background = background.resize(
            (foreground.size[0], round(background.size[1]*scale_ratio)))
    elif x_scale_ratio < y_scale_ratio:
        scale_ratio = foreground.size[1]/background.size[1]
        background = background.resize(
            (round(background.size[0]*scale_ratio), foreground.size[1]))
    
    if x_position=="left":
        x_coordinate = 0
    elif x_position=="right":
        x_coordinate = background.size[0] - foreground.size[0]
    elif x_position=="middle":
        x_coordinate = background.size[0]/2 - foreground.size[0]/2

    if y_position =="up":
        y_coordinate = 0
    elif y_position =="middle":
        y_coordinate = background.size[1]/2 - foreground.size[1]/2
    elif y_position == "bottom":
        y_coordinate = background.size[1] - foreground.size[1]


    background.paste(foreground, (x_coordinate, y_coordinate), foreground)
    return background

def whatsapp_eval_image_overlay(client, update: WhatsAppUpdate, context, picture, x_position="left", y_position="up", resize="x"):
    
    if resize in ["False", "false"]:
        resize = False

    media_id = update.get_message().image.id
    get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

    media_url = get_media_response.json()["url"]

    media_response = requests.get(media_url, headers=client.headers)
    im_bytes = media_response.content

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open(picture)

    new_im = overlay_images(im1, im2, x_position,y_position, resize)

    bio = BytesIO()
    bio.name = 'image.png'
    new_im.save(bio, 'PNG')
    bio.seek(0)

    import boto3
    import os
    import time
    session = boto3.session.Session()
    s3_client = session.client('s3',
                           region_name=config["space"]["region_name"],
                           endpoint_url=config["space"]["endpoint_url"],
                           aws_access_key_id=os.getenv('SPACES_KEY'),
                           aws_secret_access_key=os.getenv('SPACES_SECRET'))

    time_str = str(round(time.time() * 1000))

    s3_client.put_object(Bucket=config["space"]["bucket"],
                            Key= time_str  + "_" + str(update.entry[0].id) + '.png',
                            Body=bio,
                            ACL='public-read',
                            ContentType='image/png'
                            # Metadata={
                            #    'x-amz-meta-my-key': 'your-value'
                            # }
                            )
    
    client.send_image(config["space"]["url"] + "/" + time_str + "_" + str(update.entry[0].id) + '.png', update.get_from())


def whatsapp_eval_multi_image_overlay(client, update: WhatsAppUpdate, context, overlay_top_left=None, overlay_top_right=None, overlay_bottom_left=None, overlay_bottom_right=None):
    try:
        import requests
        media_id = update.get_message().image.id
        get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

        media_url = get_media_response.json()["url"]

        media_response = requests.get(media_url, headers=client.headers)
        im_bytes = media_response.content

        im_file = BytesIO(im_bytes)  # convert image to file-like object
        im1 = Image.open(im_file)   # img is now PIL Image object

        if overlay_top_left:
            overlay_bytes = requests.get(config["space"]["url"] + "/" + overlay_top_left).content
            im2 = Image.open(BytesIO(overlay_bytes))
            im1 = overlay_images(im1, im2, "left","up", True)
        if overlay_top_right:
            overlay_bytes = requests.get(config["space"]["url"] + "/" + overlay_top_right).content
            im2 = Image.open(BytesIO(overlay_bytes))
            im1 = overlay_images(im1, im2, "right","up", True)
        if overlay_bottom_left:
            overlay_bytes = requests.get(config["space"]["url"] + "/" + overlay_bottom_left).content
            im2 = Image.open(BytesIO(overlay_bytes))
            im1 = overlay_images(im1, im2, "left","bottom", True)
        if overlay_bottom_right:
            overlay_bytes = requests.get(config["space"]["url"] + "/" + overlay_bottom_right).content
            im2 = Image.open(BytesIO(overlay_bytes))
            im1 = overlay_images(im1, im2, "right","bottom", True)

        bio = BytesIO()
        bio.name = 'image.png'
        im1.save(bio, 'PNG')
        bio.seek(0)

        import boto3
        import os
        import time
        session = boto3.session.Session()
        s3_client = session.client('s3',
                            region_name=config["space"]["region_name"],
                            endpoint_url=config["space"]["endpoint_url"],
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

        time_str = str(round(time.time() * 1000))

        s3_client.put_object(Bucket=config["space"]["bucket"],
                                Key= time_str  + "_" + str(update.entry[0].id) + '.png',
                                Body=bio,
                                ACL='public-read',
                                ContentType='image/png'
                                # Metadata={
                                #    'x-amz-meta-my-key': 'your-value'
                                # }
                                )
        
        client.send_image(config["space"]["url"] + "/" + time_str + "_" + str(update.entry[0].id) + '.png', update.get_from())
    except Exception as e:
        client.send_message("{}".format(e), update.get_from())



def whatsapp_eval_gif_generation(client, update: WhatsAppUpdate, context, picture):
    import requests
    try:
        media_id = update.get_message().image.id
        get_media_response = requests.get(f"{client.base_url}/{media_id}", headers=client.headers)

        media_url = get_media_response.json()["url"]

        media_response = requests.get(media_url, headers=client.headers)
        im_bytes = media_response.content

        im_file = BytesIO(im_bytes)  # convert image to file-like object
        im1 = Image.open(im_file)   # img is now PIL Image object
        im2 = Image.open(picture)

        import PIL.features
        client.send_message("webp_anim: {}".format(PIL.features.check("webp_anim")), update.get_from())

        bio = generate_gif(im1, im2)
    except Exception as e:
        client.send_message("{}".format(e), update.get_from())


    import boto3
    import os
    import time
    session = boto3.session.Session()
    s3_client = session.client('s3',
                               region_name=config["space"]["region_name"],
                               endpoint_url=config["space"]["endpoint_url"],
                               aws_access_key_id=os.getenv('SPACES_KEY'),
                               aws_secret_access_key=os.getenv('SPACES_SECRET'))

    time_str = str(round(time.time() * 1000))

    s3_client.put_object(Bucket=config["space"]["bucket"],
                            Key= time_str  + "_" + str(update.entry[0].id) + '.webp',
                            Body=bio,
                            ACL='public-read',
                            ContentType='image/webp'
                            # Metadata={
                            #    'x-amz-meta-my-key': 'your-value'
                            # }
                            )
    
    client.send_sticker(config["space"]["url"] + "/" + time_str + "_" + str(update.entry[0].id) + '.webp', update.get_from())

    sleep(1)


whatsapp_action_functions = {"eval_image_overlay": whatsapp_eval_image_overlay,
                             "eval_multi_image_overlay": whatsapp_eval_multi_image_overlay,
                             "eval_gif_generation": whatsapp_eval_gif_generation
                             }
