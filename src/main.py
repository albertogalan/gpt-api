from flask import Flask, jsonify, redirect, request
import requests
import json
# add cryptographic library
import hashlib
import os

# logs
import logging
logger = logging.getLogger(__name__)
if os.environ.get("LOGLEVEL")=="DEBUG":
    logger.setLevel(logging.DEBUG)
if os.environ.get("LOGLEVEL")=="INFO":
    logger.setLevel(logging.INFO)
else:
    logging.debug("invisible magic")
    logger.setLevel(logging.ERROR)

logger.setLevel(logging.DEBUG)
import sys

# speak
import subprocess
import shlex
import io
app = Flask(__name__)


import re

# Elevenlabs
# Define constants for the script
CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
XI_API_KEY = "ea904e6a1e8aa96e324539f3d47d6b25"  # Your API key for authentication


def sanitize_text(text):
    # Regular expression pattern to match only allowed characters
    # ^ outside of character set means negation, so it matches everything that is NOT a-zA-Z0-9.,
    pattern = '[^a-zA-Z0-9.,]'
    # sanitize the text with letters, numbers, and punctuation, line breaks, quotes, spaces not more than one if there are more than one makes it one
    pattern = '[^a-zA-Z0-9.,\n\'" ]'

    # Replace all characters not in the allowed set with an empty string
    sanitized_text = re.sub(pattern, '', text)

    return sanitized_text


def download_audio(text, voice_id, output_path):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    logger.info(tts_url)
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.2,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    if response.ok:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        print("Audio stream saved successfully.")
    else:
        print(response.text)

def elevenlabs_speak(text, voice_id, output_path):
    try:
        download_audio(text, voice_id, output_path)
        return True
    except Exception as e:
        logger.error(e)
        termux_tts_speakold(e, "en")
        return jsonify({'error': str(e)}), 500


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

def termux_tts_speak(text, language='en', endpoint="http://fake.com"):
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
        subprocess.run(['mpv', '-'], input=mp3_fp.read(), check=True, timeout=60)

    except subprocess.TimeoutExpired:
        raise Exception("The subprocess did not respond in 60 seconds.")
    return "Success"

@app.route('/shuo2', methods=['POST'])
def elevenlabs(v_id="TWUKKXAylkYxxlPe4gx0"):
    try:
        # play audio using elevenlabs
        data = request.json
        text = data.get('text')
        v_id = data.get('v_id')
        logger.info(text)
        resp=elevenlabs_speak(text=text, voice_id=v_id, output_path="play.mp3")
        if True:
            os.system(f"termux-media-player play play.mp3")
            return jsonify({'message': text})
        else:
            return resp, 500
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/shuo', methods=['POST'])
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
        # show the error line
        exc_type, exc_obj, tb = sys.exc_info()
        frame = os.path.split(tb.tb_frame.f_code.co_filename)[1]
        logger.error(exc_type, frame, tb.tb_lineno)
        return jsonify({'error': str(e)}), 500

@app.route('/ey', methods=['POST'])
def test():
    logger.info("test")

    posted_data = request.json

    # Log the posted data
    #logger.info(f"Posted data: {posted_data}")
    return "Data logged", 200


@app.route('/openai', methods=['POST'])
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
      data = {"text": response.json()["choices"][0]["message"]["content"]}
      return data
    except Exception as e:
        print("eyy")
        logger.error(e)
        return logger.error(e), 500

@app.route('/claude', methods=['POST'])
def claude():
    try:
        # Your Anthropics API key
        api_key=os.environ.get("ANTHROPIC_API_KEY")
        # Headers for Anthropics request
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        url = f'https://api.anthropic.com/v1/complete'
        logger.info(request.get_json())
        data=request.get_json()
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info(response.json())
        #data = {"text": response.json()["completion"]}
        data = {"text": response.json()}
        return data
    except Exception as e:
        print("eyy")
        logger.error(e)
        return logger.error(response.json()), 500

if __name__ == '__main__':
    app.run(debug=True, port=8083, ssl_context=('certs/cert.pem','certs/key.pem'), host='0.0.0.0')
