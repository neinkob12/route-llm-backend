from flask import Flask, request, jsonify
import os
from routellm.controller import Controller

app = Flask(__name__)

# Get port from environment variable (Railway sets this automatically)
port = int(os.environ.get('PORT', 8000))

# Set your API keys from environment variables
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
os.environ["ANYSCALE_API_KEY"] = os.environ.get("ANYSCALE_API_KEY", "")

# Initialize your RouteLLM controller
client = Controller(
    routers=["mf"],
    strong_model="gpt-4-1106-preview",
    weak_model="anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1",
)

@app.route('/route', methods=['POST'])
def route_llm():
    # Simple authentication (optional, but recommended)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    token = auth_header.split(' ')[1]
    if token != os.environ.get('SECRET_KEY'):
        return jsonify({"error": "Invalid API key"}), 401

    data = request.json
    messages = data.get('messages', [])

    # RouteLLM expects a list of messages, pass them to the client
    result = client(messages)

    response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": result['choices'][0]['message']['content']
                }
            }
        ],
        "used_model": result.get("used_model", "unknown")
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
