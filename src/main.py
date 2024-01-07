from flask import Flask, jsonify, redirect, request
import requests
import json
# add cryptographic library
import hashlib
app = Flask(__name__)


def openai():
    import os
    from openai import OpenAI

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )


@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    # Your OpenAI API key
    api_key='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'

    # Headers for OpenAI request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
    'messages': [
        {'role': 'system', 'content': 'Your prompt here'},
        {'role': 'user', 'content': 'Your questions here'}
    ],
    'model': 'davinci-codex',
    'temperature': 0.2,
    'max_tokens': 500
}

    # URL to forward the request with path
    #print(json.dumps(request.form))
    print(request.get_json())
    #print(request.data)
    #data=request.json
    #print(jsonify(data))
    data=request.get_json()
    url = f'https://api.openai.com/'+ path
    if request.method == 'POST':
        print("post")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())
    elif request.method == 'GET':
        print("get")
        response = requests.get(url, headers=headers, params=request.args)
    return response.json()

if __name__ == '__main__':
    app.run(debug=True, port=8080, ssl_context=('src/cert.pem','src/key.pem'), host='0.0.0.0')
