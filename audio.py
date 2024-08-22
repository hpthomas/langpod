import requests
import io
import os
from pydub import AudioSegment
from pydub.playback import play
import threading

import os
import requests

def speak_eleven(text, filename):
    xi_api_key = os.environ['ELEVENLABS_API_KEY']
    voice_id = "NFG5qt843uXKj4pFvR7C"  # Replace with the desired voice ID
    
    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    
    # Set up headers for the API request, including the API key for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": xi_api_key
    }
    
    # Set up the data payload for the API request, including the text and voice settings
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
    
    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)
    
    # Check if the request was successful
    if response.ok:
        # Open the output file in write-binary mode
        with open(filename, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Audio saved as {filename}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def speak_openai(text, filename):
    url = "https://api.openai.com/v1/audio/speech"
    
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "tts-1",
        "input": text,
        "voice": "onyx",
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        audio_data = response.content
        with open(filename, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved as {filename}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def speak(text, filename, model = None):
    if model == "eleven":
        speak_eleven(text, filename)
    elif model == "openai":
        speak_openai(text, filename)
    elif 'ELEVENLABS_API_KEY' in os.environ:
        speak_eleven(text, filename)
    elif 'OPENAI_API_KEY' in os.environ:
        speak_openai(text, filename)
    else:
        raise ValueError("No API key found for Eleven Labs or OpenAI.")

def speak_batch(texts, filenames, model = None):
    threads = []
    for text, filename in zip(texts, filenames):
        if (os.path.exists(filename)):
            print(f"File {filename} already exists, skipping.")
            continue
        thread = threading.Thread(target=speak, args=(text, filename, model))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def play_mp3(file):
    play(AudioSegment.from_file(file, codec="mp3"))

def test(model = None):
    if os.path.exists("sample_en.mp3"):
        os.remove("sample_en.mp3")
    if os.path.exists("sample_es.mp3"):
        os.remove("sample_es.mp3")
    s1 = "The Battle of Winwick happened on August 19, 1648 near a small town called Winwick in England."
    s2 = "La Batalla de Winwick ocurrió el 19 de agosto de 1648 cerca de un pequeño pueblo llamado Winwick, en Inglaterra."
    speak_batch([s1, s2], ["sample_en.mp3", "sample_es.mp3"], model)
    play_mp3("sample_es.mp3")
    play_mp3("sample_en.mp3")