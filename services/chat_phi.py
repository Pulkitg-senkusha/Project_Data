from logger import logger
import requests
from Config.setting import config

MODEL_NAME = config.phi_model
OLLAMA_API_URL = config.phi_api_url  

def get_phi_response(history: list[dict]) -> str:
    try:
        # Ensure all messages have 'role' and 'content'
        cleaned = []
        for msg in history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                cleaned.append(f"{msg['role'].capitalize()}: {msg['content']}")
            else:
                logger.warning(f"Skipping invalid message: {msg}")

        prompt = "\n".join(cleaned)

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "temperature": 0.6,
            "stream": False,
            "max_tokens": 1024
        }

        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Sending prompt:\n{prompt}")
        logger.info(f"Ollama response: {data['response']}")

        return data['response']

    except Exception as e:
        logger.error(f"Error in get_llama_response: {str(e)}")
        return f"Error: {str(e)}"