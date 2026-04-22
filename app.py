from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/v1/answer', methods=['POST'])
def answer():
    data = request.json
    query = data.get("query", "")
    
    clean_query = re.sub(r'[^0-9+\-*/. ]', '', query)
    
    try:
        result = eval(clean_query)
        response_text = f"The sum is {result}."
    except:
        response_text = "The sum is calculation error."
        
    return jsonify({"output": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)