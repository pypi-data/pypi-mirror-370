import requests

def ai_explain_function(function_code, comment_block, model="mistral"):
    prompt = (
        "Read the following function and its documentation comments. "
        "Explain in greater detail how to utilize this function, including a practical example if possible.\n\n"
        f"Comments:\n{comment_block}\n\nCode:\n{function_code}\n"
    )
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={"model": model, "prompt": prompt, "stream": False}
    )
    data = response.json()
    return data.get("response", "").strip()