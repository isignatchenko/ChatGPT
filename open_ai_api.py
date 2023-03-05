import time

import openai
from openai import APIError
from openai.error import RateLimitError, InvalidRequestError

from config import api_key, temp_max_tokens
from db_content import count_messages_text_len, update_total_tokens
from db_users import decrease_users_balance, get_from_user

openai.api_key = api_key


def get_response(messages, user_id, chat_id):
    time.sleep(0.5)
    max_tokens = temp_max_tokens - count_messages_text_len(chat_id)
    if max_tokens < 0:
        max_tokens = max_tokens * (-1)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=get_from_user(user_id, "temperature"),
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=get_from_user(user_id, "frequency_penalty"),
            presence_penalty=get_from_user(user_id, "presence_penalty")
        )
        total_tokens = response.usage['total_tokens']
        decrease_users_balance(user_id, int(total_tokens))
        update_total_tokens(chat_id, total_tokens)
        base_str = response.choices[0].message['content']
        return [True, base_str]
    except APIError:
        return [False, "APIError"]
    except RateLimitError:
        return [False, "RateLimitError"]
    except InvalidRequestError:
        return [False, "InvalidRequestError"]

# def img_get_response(prompt):
#     response = openai.Image.create(
#         prompt=prompt,
#         n=1,
#         size="1024x1024"
#     )
#
#     url = response['data'][0]['url']
#
#     data = requests.get(url).content
#
#     f = open('img.jpg', 'wb')
#     f.write(data)
#     f.close()
#
#     # Opening the saved image and displaying it
#     img = Image.open('img.jpg')
#     img.show()
#
#
# def img_variation_get_response():
#     response = openai.Image.create_variation(
#         image=open("img.jpg", "rb"),
#         n=1,
#         size="1024x1024"
#     )
#     url = response['data'][0]['url']
#
#     data = requests.get(url).content
#
#     f = open('img2.jpg', 'wb')
#     f.write(data)
#     f.close()
#
#     # Opening the saved image and displaying it
#     img = Image.open('img2.jpg')
#     img.show()
#
#
# # img_get_response("a close up, studio photographic portrait of a white siamese cat that looks curious, backlit ears")
# img_variation_get_response()
