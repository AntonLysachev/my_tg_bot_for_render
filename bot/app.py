import os
from flask import Flask, request
import telebot
from dotenv import load_dotenv
import logging
from google.cloud import dialogflow_v2


load_dotenv()

TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')
DEBUG_SWITCH = os.getenv('DEBUG_SWITCH')
PROJECT_ID = os.getenv('PROJECT_ID')
SESSION_ID = os.getenv('SESSION_ID')

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)


def get_dialogflow_response(user_input):
    project_id = PROJECT_ID
    session_id = SESSION_ID
    language_code = 'ru'

    session_client = dialogflow_v2.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)

    text_input = dialogflow_v2.TextInput(text=user_input, language_code=language_code)
    query_input = dialogflow_v2.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session_path, query_input=query_input)
    return response.query_result.fulfillment_text


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет {message.chat.first_name}!')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.send_message(message.chat.id, get_dialogflow_response(message.text))


@app.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route('/')
def index():
    bot.remove_webhook()
    bot.set_webhook(url=URL)
    return 'OK', 200

 
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=URL)
    app.run(debug=DEBUG_SWITCH)

    