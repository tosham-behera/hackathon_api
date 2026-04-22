import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# This pulls the key from the Render Environment settings
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.json
    query = data.get("query", "")
    
    # Use Gemini to answer the query
    try:
        response = model.generate_content(query)
        output_text = response.text.strip()
    except Exception as e:
        output_text = "Error processing request"
        
    return jsonify({"output": output_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)