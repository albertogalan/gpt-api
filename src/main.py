from flask import Flask, jsonify, redirect, request
import requests
import json
# add cryptographic library
import hashlib
app = Flask(__name__)

@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    # Your OpenAI API key
    api_key = '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'

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
    url = f'https://api.openai.com/{path}'
    if request.method == 'POST':
        print("post")
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif request.method == 'GET':
        print("get")
        response = requests.get(url, headers=headers, params=request.args)


    return response.json()
    #return "ehho"

if __name__ == '__main__':
    app.run(debug=True, port=5000, ssl_context='adhoc', host='0.0.0.0')
