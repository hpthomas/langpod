import json
import requests
import os
import time

MAX_PROMPT_CHARS = 100000
MAX_RESPONSE_TOKENS = 4096

TEXT_SYSTEM_PROMPT = "Respond with the exact content requested, line-by-line. Include no additional characters or explanations unless requested."

def chat(query, model = "gpt-4o", system_prompt=None):
    retries = 0
    while retries < 3:
        try:
            return _chat(query, model, system_prompt)
        except ValueError as e:
            print(f"Error: {e}")
            retries += 1
            time.sleep(2**retries)

        
def _chat(query, model, system_prompt):
    default_system_prompt = "You are an AI JSON Generation Assistant. You always respond with JSON only, without preambles or additional text in your response. "
    sys_prompt = system_prompt or default_system_prompt

    if len(query) > MAX_PROMPT_CHARS:
        raise ValueError('Unable to process the provided input.')

    headers = {
        'Content-Type': 'application/json',
    }

    if model.startswith('gpt'):
        url = "https://api.openai.com/v1/chat/completions"
        headers['Authorization'] = f"Bearer {os.environ['OPENAI_API_KEY']}"
    elif model.startswith('claude'):
        url = "https://api.anthropic.com/v1/messages"
        headers['x-api-key'] = os.environ["ANTHROPIC_API_KEY"]
        headers['anthropic-version'] = '2023-06-01'
    else:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers['Authorization'] = f"Bearer {os.environ['GROQ_API_KEY']}"

    user_message = {"role": "user", "content": query}

    body = {
        "model": model,
        "max_tokens": MAX_RESPONSE_TOKENS,
    }

    if model.startswith('claude'):
        body['system'] = sys_prompt
        body['messages'] = [user_message]
    else:
        body['messages'] = [
            {"role": "system", "content": sys_prompt},
            user_message
        ]
        if 'json' in sys_prompt.lower():
            body["response_format"] = {"type": "json_object"}
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        json_response = response.json()
        
        if model.startswith('claude'):
            message = json_response["content"][0]["text"]
        else:
            message = json_response["choices"][0]["message"]["content"]

        try:
            if 'json' in sys_prompt.lower():
                obj = json.loads(message)
            else:
                obj = message
            
            return obj
        except json.JSONDecodeError:
            print('Received invalid JSON from LLM:')
            print(message)
            raise ValueError("Could not parse response from LLM as JSON")
    else:
        print(response.text)
        raise ValueError("Could not get response from LLM")