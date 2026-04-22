import os
import re
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
# You must add GEMINI_API_KEY to your Environment Variables in Render
API_KEY = os.environ.get("GEMINI_API_KEY", "")
model = None
if API_KEY:
    genai.configure(api_key=API_KEY)
    try:
        # Dynamically find an available model
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Available models: {available_models}")
        if available_models:
            # Prefer flash or pro if available, otherwise pick the first one
            preferred = next((m for m in available_models if 'flash' in m or 'pro' in m), available_models[0])
            model = genai.GenerativeModel(preferred)
            print(f"Selected model: {preferred}")
    except Exception as e:
        print(f"Error listing models: {e}")

@app.route('/v1/answer', methods=['POST'])
def answer():
    # Safely get data even if Content-Type isn't application/json
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    
    print(f"Received data: {data}")
    query = data.get("query", "")
    assets = data.get("assets", [])
    
    print(f"Question: {query}")
    
    # 1. Try simple math logic first (handles "What is 10 + 15?")
    match = re.search(r'(\d+)\s*\+\s*(\d+)', query)
    if match:
        num1 = int(match.group(1))
        num2 = int(match.group(2))
        result = num1 + num2
        return jsonify({"output": f"The sum is {result}."})
    
    # 2. If it's not a simple addition question, use Gemini to answer
    if model:
        try:
            prompt = f"Answer the following question directly and concisely without any markdown or extra text. Question: {query}"
            response = model.generate_content(prompt)
            answer_text = response.text.strip()
            print(f"Gemini Answer: {answer_text}")
            return jsonify({"output": answer_text})
        except Exception as e:
            error_msg = f"Gemini Error: {str(e)}"
            print(error_msg)
            return jsonify({"output": error_msg})
            
    # 3. Fallback if API key is completely missing
    return jsonify({"output": "Error: GEMINI_API_KEY environment variable is not set."})

if __name__ == '__main__':
    # Use port 10000 for Render, fallback to 5000 locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)