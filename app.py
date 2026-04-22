import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure model with a strict system instruction
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="You are a strict API. Your output must match the expected format exactly. Do not provide explanations, do not include 'Sure' or 'Here is the answer', and do not add conversational filler. If the query is a math question, output exactly 'The sum is [result].'."
)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.json
    query = data.get("query", "")
    
    # Send the query to Gemini
    try:
        response = model.generate_content(query)
        # .strip() removes accidental whitespace
        output_text = response.text.strip()
    except Exception as e:
        output_text = "Error"
        
    return jsonify({"output": output_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)