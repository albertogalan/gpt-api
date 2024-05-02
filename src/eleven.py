
# Import necessary libraries
import requests  # Used for making HTTP requests
import json  # Used for working with JSON data

# Define constants for the script
CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
XI_API_KEY = "ea904e6a1e8aa96e324539f3d47d6b25"  # Your API key for authentication

# create a function to download the audio file from eleven api
def download_audio(text, voice_id, output_path):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
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

# create a text about the most famous scienties about three lines
text="""
1. Risk Assessment: This is the first step in any business continuity plan. It involves identifying potential cyber threats and vulnerabilities that could disrupt your business operations. This could range from data breaches, malware attacks, phishing scams, to DDoS attacks.

2. Incident Response Plan: This is a detailed plan on how to respond to a cyber attack. It outlines the steps to take, who is responsible for each step, and how to communicate during and after the incident. The goal is to minimize the impact of the attack and restore normal operations as quickly as possible.

3. Data Backup and Recovery: Regularly backing up data is crucial for business continuity. In the event of a cyber attack, having a backup allows you to restore your data and continue operations. The backup should be stored in a secure, off-site location and be encrypted to protect against unauthorized access.

4. Disaster Recovery Plan: This is a subset of the business continuity plan that focuses on restoring IT infrastructure and systems after a cyber attack. It includes details on recovering data, restoring systems, and managing communication during the recovery process.

5. Regular Testing and Updating: Business continuity plans should be regularly tested to ensure they are effective and updated to address new threats. This could involve conducting drills, reviewing procedures, and updating the plan based on feedback and lessons learned.

6. Employee Training: Employees are often the first line of defense against cyber attacks. Regular training can help them recognize potential threats, understand the importance of cybersecurity, and know what to do in the event of an attack.

7. Vendor Management: Businesses often work with third-party vendors who have access to their data or systems. It's important to ensure these vendors also have robust cybersecurity measures in place.

8. Cybersecurity Insurance: This can help cover the costs associated with a cyber attack, including data recovery, notification of customers, legal fees, and any fines or penalties.

9. Compliance: Depending on the industry, businesses may need to comply with certain cybersecurity regulations. Compliance not only helps protect against cyber threats but also avoids potential fines or penalties.

10. Technology: Implementing the right technology is crucial for detecting and preventing cyber attacks. This could include firewalls, antivirus software, encryption tools, and intrusion detection systems.
"""

download_audio(text, "TWUKKXAylkYxxlPe4gx0", "hello.mp3")
# play the audio file on termux
import os
os.system(f"termux-media-player play hello.mp3")
