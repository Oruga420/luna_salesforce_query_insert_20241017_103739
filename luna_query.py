import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce
import time
import openai
import json
import requests
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

# Load environment variables
load_dotenv()
username = os.getenv('salesforceusr')
password = os.getenv('salesforcepswd')
security_token = os.getenv('SECURITY_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID')
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

# Set up Salesforce and OpenAI
sf = Salesforce(username=username, password=password, security_token=security_token)
openai.api_key = openai_api_key

# Function for running the SOQL query
def run_soql_query():
    query = """
    Your Query here 
    """
    response = sf.query_all(query)
    return response

# Function to update records
def update_records(records):
    updated_count = 0
    for record in records:
        if record['Field to update here'] == 'New field value':
            sf.Account.update(record['Id'], {'field to update here': 'Waiting'})
            updated_count += 1
    return updated_count

# Function for sending a message to OpenAI Chat
def send_chat_message(prompt, last_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who outputs puns."},
            {"role": "user", "content": last_message},
            {"role": "assistant", "content": prompt},
        ],
    )
    return response['choices'][0]['message']['content']

# Function to generate audio using ElevenLabs API
def generate_elevenlabs(text, voice_id, api_key, model_id='eleven_multilingual_v1'):
    url = 'https://api.elevenlabs.com/engine/synthesize'
    headers = {'x-api-key': api_key}
    data = {
        'modelId': model_id,
        'text': text.strip(),
        'voiceId': voice_id
    }
    response = requests.post(url, headers=headers, json=data)
    audio_data = response.content
    return audio_data

# Function to play audio
def play_audio(audio_data):
    audio = AudioSegment.from_file(BytesIO(audio_data), format="mp3")
    play(audio)

# Function for countdown
def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f"Waiting {i} seconds...", end="\r")
        time.sleep(1)

# Function to process records with OpenAI
def process_records(records, updated_count):
    company_names = ", ".join([record['Name'] for record in records])
    last_message = f"There are {updated_count} records stuck. Companies: {company_names}. Give me a pun."
    pun = send_chat_message(last_message)
    return pun

# Main loop
while True:
    query_result = run_soql_query()

    if query_result['totalSize'] > 0:
        updated_count = update_records(query_result['records'])
        print(f"Updated {updated_count} records.")
        
        if updated_count > 0:
            pun = process_records(query_result['records'], updated_count)
            print(pun)
            
            audio_data = generate_elevenlabs(pun, voice_id=elevenlabs_voice_id, api_key=elevenlabs_api_key)
            play_audio(audio_data)
    else:
        print("No records to update.")

countdown(30)