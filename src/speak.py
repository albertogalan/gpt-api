from flask import Flask, request, jsonify
import subprocess
import shlex

app = Flask(__name__)

def termux_tts_speak(text, pitch, rate, language):
    # Constructing the command
    command = f"termux-tts-speak -l {language} -p {pitch} -r {rate} {shlex.quote(text)}"
    try:
        # Executing the command
        subprocess.run(command, shell=True, check=True)
        return "Success"
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {str(e)}"

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
        return jsonify({'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
