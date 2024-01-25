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
# say hello
logger.info("Hello, GPT")

# speak
import subprocess
import shlex

app = Flask(__name__)


import re

def sanitize_text(text):
    # Regular expression pattern to match only allowed characters
    # ^ outside of character set means negation, so it matches everything that is NOT a-zA-Z0-9.,
    pattern = '[^a-zA-Z0-9.,]'

    # Replace all characters not in the allowed set with an empty string
    sanitized_text = re.sub(pattern, '', text)

    return sanitized_text

def termux_tts_speak(text, pitch=1.0, rate=1.0, language='eng'):
    # Constructing the command
    text=sanitize_text(text)
    command = f"termux-tts-speak -l {language} -p {pitch} -r {rate} {shlex.quote(text)}"
    command = f"echo '{text}' | gtts-cli - -l 'en' | mpv -"
    # Executing the command
    try:
        # Executing the command with a timeout of 5 seconds
        subprocess.run(command, shell=True, check=True, timeout=10)
    except subprocess.TimeoutExpired:
        raise Exception("The subprocess did not respond in 5 seconds.")

    return "Success"

@app.route('/speak', methods=['POST'])
def speak():
    try:
        # Extracting data from the POST request
        data = request.json
        text = data.get('text')
        pitch = data.get('pitch', 1.0)  # Default value for pitch
        rate = data.get('rate', 1.0)    # Default value for rate
        language = data.get('language','eng')

        if not text:
            raise ValueError("Text is required")

        # Call the Termux TTS function
        result = termux_tts_speak(text, pitch, rate, language)
        logger.info(result)
        return jsonify({'message': result})
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 400

@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    try:
      # Your OpenAI API key
      api_key=os.environ.get("OPENAI_API_KEY")
      # Headers for OpenAI request
      headers = {
          'Authorization': f'Bearer {api_key}',
          'Content-Type': 'application/json'
      }
      # URL to forward the request with path
      #print(json.dumps(request.form))
      logger.info(request.get_json())
      #print(request.data)
      #data=request.json
      #print(jsonify(data))
      data=request.get_json()
      url = f'https://api.openai.com/'+ path
      if request.method == 'POST':
          logger.info("post")
          response = requests.post(url, headers=headers, data=json.dumps(data))
      elif request.method == 'GET':
          logger.info("get")
          response = requests.get(url, headers=headers, params=request.args)
      logger.info(response.json())
      return response.json()
    except Exception as e:
        logger.error(e)
        return "error"


if __name__ == '__main__':
    app.run(debug=True, port=8080, ssl_context=('certs/cert.pem','certs/key.pem'), host='0.0.0.0')
