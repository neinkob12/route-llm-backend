from flask import Flask, request, jsonify
import os
from routellm.controller import Controller

app = Flask(__name__)

port = int(os.environ.get('PORT', 8000))

# Initialize RouteLLM controller (no need to set os.environ manually)
client = Controller(
    routers=["mf"],
    strong_model="gpt-4-1106-preview",
    weak_model="anyscale/Mixtral-8x7B-Instruct-v0.1",
    anyscale_api_base="https://api.endpoints.anyscale.com/v1"  # Add this line
)

@app.route('/route', methods=['POST'])
def route_llm():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    token = auth_header.split(' ')[1]
    if token != os.environ.get('SECRET_KEY'):
        return jsonify({"error": "Invalid API key"}), 401

    # Process request
    data = request.json
    messages = data.get('messages', [])

    # Get RouteLLM response
    response = client.chat.completions.create(
        model="router-mf-0.11593",
        messages=messages
    )

    # Format response
    return jsonify({
        "choices": [{
            "message": {
                "role": "assistant",
                "content": response.choices[0].message.content
            }
        }],
        "used_model": response.model  # Adjust if RouteLLM uses a different key
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
