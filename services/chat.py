import os
import requests
from dotenv import load_dotenv
from logger import logger
from Config.setting import config

GROQ_API_KEY = config.GROQ_API_KEY
GROQ_API_URL = config.GROQ_API_URL
MODEL_NAME = config.MODEL

def get_llama_response(history: list[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": history, 
        "temperature": 0.6,
        "max_tokens": 1024
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Sending conversation history: {history}")
        logger.info(f"LLaMA response: {data}")

        return data['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"LLaMA API error: {str(e)}")
        return f"Error communicating with LLaMA: {str(e)}"