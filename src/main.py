from flask import Flask, jsonify, redirect, request
import requests
import json
# add cryptographic library
import hashlib
import os

# logs
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# speak
import subprocess
import shlex
import io
app = Flask(__name__)


import re

def sanitize_text(text):
    # Regular expression pattern to match only allowed characters
    # ^ outside of character set means negation, so it matches everything that is NOT a-zA-Z0-9.,
    pattern = '[^a-zA-Z0-9.,]'

    # Replace all characters not in the allowed set with an empty string
    sanitized_text = re.sub(pattern, '', text)

    return sanitized_text


def termux_tts_speakold(text, language='en'):
    # Constructing the command
    text=sanitize_text(text)
    command = f"echo '{text}' | gtts-cli - -l 'en' | mpv -"
    try:
        # Executing the command with a timeout of 5 seconds
        subprocess.run(command, shell=True, check=True, timeout=20)
    except subprocess.TimeoutExpired:
        raise Exception("The subprocess did not respond in 20 seconds.")
    return "Success"

def termux_tts_speak(text, language='en', endpoint='192.168.141:8080'):
    # Constructing the command
    text=sanitize_text(text)
    # Your specific data
    data = {
        "text": text,
        "language": language,
        }
    url = "http://"+endpoint

    # Send the POST request
    response = requests.post(url, data=data)
    # Check if the request was successful
    if response.status_code == 200:
    # Use io.BytesIO to create a file-like object from the response content
        mp3_fp = io.BytesIO(response.content)

    try:
        # Executing the command with a timeout of 40 seconds
        logger.info("playing ... ")
        subprocess.run(['mpv', '-'], input=mp3_fp.read(), check=True, timeout=40)

    except subprocess.TimeoutExpired:
        raise Exception("The subprocess did not respond in 20 seconds.")
    return "Success"

@app.route('/speakold', methods=['POST'])
def speakold():
    try:
        data = request.json
        text = data.get('text')
        logger.info(text)
        language = data.get('language','eng')
        endpoint="http://fake.com"
        result = termux_tts_speakold(text, language)
        return jsonify({'message': text})
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['POST'])
def speak():
    try:
        # Extracting data from the POST request
        data = request.json
        text = data.get('text')
        language = data.get('language','eng')
        model = data.get('model','gpt2')

        # get endpoint form env variable
        endpoint=os.environ.get("ENDPOINT")

        if not text:
            raise ValueError("Text is required")

        # Call the Termux TTS function
        result = termux_tts_speak(text, language, endpoint)
        logger.info(result)
        return jsonify({'message': result})
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/ey', methods=['POST'])
def test():
    logger.info("test")

    posted_data = request.json

    # Log the posted data
    #logger.info(f"Posted data: {posted_data}")
    return "Data logged", 200


@app.route('/completion', methods=['POST'])
def proxy():
    try:
      # Your OpenAI API key
      api_key=os.environ.get("OPENAI_API_KEY")
      # Headers for OpenAI request
      headers = {
          'Authorization': f'Bearer {api_key}',
          'Content-Type': 'application/json'
      }
      logger.info(request.get_json())
      data=request.get_json()
      url = f'https://api.openai.com/v1/chat/completions'
      logger.info("post")
      response = requests.post(url, headers=headers, data=json.dumps(data))
      return response.json()
      return "Success", 200
    except Exception as e:
        print("eyy")
        logger.error(e)
        return logger.error(e), 500


if __name__ == '__main__':
    app.run(debug=True, port=8083, ssl_context=('certs/cert.pem','certs/key.pem'), host='0.0.0.0')
