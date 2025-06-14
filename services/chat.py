import os
import requests
import re
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from logger import logger
from Config.setting import config
import ast
import io
import base64
from datetime import datetime

GROQ_API_KEY = config.GROQ_API_KEY
GROQ_API_URL = config.GROQ_API_URL
MODEL_NAME = config.MODEL

def is_plot_request(user_input: str) -> bool:
    """Check if the user input contains keywords indicating a plot request."""
    plot_keywords = ['graph', 'plot', 'chart', 'visualize', 'diagram', 'scatter', 'line', 'bar', 'pie']
    return any(keyword in user_input.lower() for keyword in plot_keywords)

def extract_code_block(response: str) -> str:
    """Extract Python code block from LLaMA response (between ```python and ```)."""
    code_pattern = r'```python\n(.*?)\n```'
    match = re.search(code_pattern, response, re.DOTALL)
    return match.group(1) if match else ""

def execute_plot_code(code: str, output_dir: str = "plots") -> tuple[str, bool]:
    """Execute Matplotlib code and save the plot as an image. Return file path and success status."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(output_dir, f"plot_{timestamp}.png")
        
        # Create a safe locals dictionary to capture plt
        locals_dict = {'plt': plt}
        
        # Execute the code
        exec(code, {'plt': plt, 'np': __import__('numpy')}, locals_dict)
        
        # Save the plot
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        
        logger.info(f"Plot saved successfully at: {plot_path}")
        return plot_path, True
    except Exception as e:
        logger.error(f"Error executing plot code: {str(e)}")
        return str(e), False

def get_llama_response(user_input: str, history: list[dict] = None) -> tuple[str, str | None]:
    """
    Get response from LLaMA via Groq API. If a plot is requested, generate and save it.
    Returns (response_text, plot_path or None).
    """
    if history is None:
        history = []

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepare the prompt based on whether a plot is requested
    if is_plot_request(user_input):
        system_prompt = (
            "You are a helpful assistant that generates Python code using Matplotlib to create plots. "
            "For the user's request, provide a brief explanation and then include the complete Python code "
            "to generate the plot inside a code block (```python\n...\n```). The code should be ready to execute "
            "with matplotlib.pyplot (imported as plt) and numpy (imported as np) if needed. Do not include plt.show()."
        )
    else:
        system_prompt = "You are a helpful assistant. Provide a concise and accurate answer to the user's question."

    # Update history with the new user input
    history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": system_prompt}] + history

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 1024
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Sending conversation history: {messages}")
        logger.info(f"LLaMA response: {data}")

        response_content = data['choices'][0]['message']['content']
        
        # If a plot is requested, extract and execute the code
        if is_plot_request(user_input):
            code = extract_code_block(response_content)
            if code:
                plot_path, success = execute_plot_code(code)
                if success:
                    return (
                        f"{response_content}\n\nPlot generated and saved at: {plot_path}",
                        plot_path
                    )
                else:
                    return (
                        f"{response_content}\n\nError generating plot: {plot_path}",
                        None
                    )
            else:
                logger.warning("No valid Python code block found in LLaMA response.")
                return (
                    f"{response_content}\n\nNo valid plot code was generated.",
                    None
                )
        
        # For non-plot requests, return the response as-is
        return response_content, None

    except Exception as e:
        logger.error(f"LLaMA API error: {str(e)}")
        return f"Error communicating with LLaMA: {str(e)}", None

if __name__ == "__main__":
    # Example usage
    user_input = input("Ask a question or request a plot: ")
    response, plot_path = get_llama_response(user_input)
    print(response)
    if plot_path:
        print(f"Plot available at: {plot_path}")