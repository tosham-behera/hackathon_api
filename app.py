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
    
    import operator
    ops = {
        '+': ('sum', operator.add),
        '-': ('difference', operator.sub),
        '*': ('product', operator.mul),
        '/': ('quotient', operator.truediv),
    }
    
    # 1. Try comprehensive math logic first
    match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', query)
    if match:
        num1 = int(match.group(1))
        op_symbol = match.group(2)
        num2 = int(match.group(3))
        
        name, func = ops[op_symbol]
        result = func(num1, num2)
        
        # Format division nicely
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        formatted_answer = f"The {name} is {result}."
        print(f"Math Parser Answer: {formatted_answer}")
        return jsonify({"output": formatted_answer})
    
    # 2. If it's not a simple math expression, use Gemini with strict formatting rules
    if model:
        try:
            prompt = f"""You are an AI answering questions. 
If the user asks a simple math question, you MUST format your answer exactly like this:
- Addition: 'The sum is <answer>.'
- Subtraction: 'The difference is <answer>.'
- Multiplication: 'The product is <answer>.'
- Division: 'The quotient is <answer>.'
For example, if the question is 'What is 10 + 15?', answer exactly 'The sum is 25.'
If it is not a math question, just provide the direct, concise answer without any markdown.
Question: {query}"""
            
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