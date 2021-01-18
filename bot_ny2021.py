#!/usr/bin/env python
# --coding:utf-8--

import vk_api
import time
import random
import urllib2
import sqlite3
import configparser
from PIL import Image, ImageDraw, ImageFont

config = configparser.ConfigParser()
config.read("settings.ini")

vk = vk_api.VkApi(token=config["serial_sled"]["token"])
id_group = int(config["serial_sled"]["id_group"])

vk._auth_token()
upload = vk_api.VkUpload(vk)

conn = sqlite3.connect('set.db')
c = conn.cursor()

while True:
	try:
		messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unanswered"})
		if messages["count"] >= 1:
			for i in range(messages["count"]):
				id = messages["items"][i]["last_message"]["from_id"]
				body = messages["items"][i]["last_message"]["text"]
				body = ''.join(e for e in body if e.isalnum())
				if body == "2021":
					c.execute("SELECT EXISTS(SELECT * FROM users WHERE user_id = ? LIMIT 1)", (id, ))
					if c.fetchone()[0] == 0:
						c.execute("INSERT INTO users (user_id) VALUES (?)", (id,))
						conn.commit()
						vk.method("messages.send", {"peer_id": id, "random_id": 0, "message": "С Новым Годом! &#127876;"})
						profiles = vk.method('users.get', {'user_ids' : id, 'fields': 'photo_400'})
						print(profiles[0]['first_name']+ ' ' +profiles[0]['last_name'])
						try:
							url = profiles[0]['photo_400']
							xx, yy = (142, 65)
						except Exception as E:
							print(E)
							profile = vk.method('users.get', {'user_ids' : id, 'fields': 'photo_max_orig'})
							url = profile[0]['photo_max_orig']
							xx, yy = (142, 72)
						finally:
							url = url.replace("?ava=1", "")
							response = urllib2.urlopen(url)
							content = response.read()
							file = open('image.jpg', 'w')
							file.write(content)
							file.close()
							numart = random.randint(0, 8)
							x, y = (30, 300)

							img = Image.open(str(numart) + '.jpg')
							watermark = Image.open('image.jpg')
							water = Image.open('temp.png')

							watermark = watermark.convert('RGBA')

							img.paste(watermark, (xx, yy),  watermark)
							img.paste(water, (96, 30),  water)

							draw = ImageDraw.Draw(img)
							font = ImageFont.truetype("6426.ttf", 32)

							text = profiles[0]['first_name']+'!'
							x = x + (193 - float(len(text))/2*15)
							draw.text((x, y), text, font=font, fill=(0,0,0))
							draw.text((x+3, y), text, font=font, fill=(0,0,0))
							draw.text((x, y+3), text, font=font, fill=(0,0,0))
							draw.text((x+3, y+3), text, font=font, fill=(0,0,0))
							draw.text((x, y), text, font=font, fill=(255,255,255))

							img.save("img_result.png")

							photo = upload.photo_messages('img_result.png')
							owner_id = photo[0]['owner_id']
							photo_id = photo[0]['id']
							access_key = photo[0]['access_key']
							attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)
							vk.method("messages.send", {"peer_id": id, "random_id": 0, "attachment": attachment})
					else:
						vk.method("messages.send", {"peer_id": id, "random_id": 0, "message": "У нас ограниченное количество открыток :( Но ты не унывай, а мы от лица всей администрации желаем счастливого Нового года! &#9924;"})
				else:
					vk.method("messages.markAsAnsweredConversation", {"peer_id": id, "answered": 1, "group_id": id_group})
	except Exception as E:
		print(E)
		time.sleep(1)