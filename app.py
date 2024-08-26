import os
from flask import Flask, request, jsonify, render_template
import requests
import re
import markdown

app = Flask(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
API_KEY = os.getenv("gemini_api")  # Replace with your actual API key

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/improve_text', methods=['POST'])
def improve_text():
    try:
        data = request.json
        text = data['text']
        
        payload = {
            "contents": [{
                "parts":[{
                    "text": f"Improve the following text. Then provide a summary of improvements, using markdown formatting for headings, bold, italic, and bullet points: {text}"
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        response = requests.post(f"{GEMINI_API_URL}?key={API_KEY}", json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Split the result into improved text and summary
            parts = re.split(r'\n*(?:##?\s*)?Summary of improvements:?\n*', result, flags=re.IGNORECASE)
            
            if len(parts) > 1:
                improved_text, improvement_summary = parts
            else:
                improved_text = parts[0]
                improvement_summary = "No specific summary provided."
            
            # Convert markdown to HTML
            improved_text_html = markdown.markdown(improved_text)
            improvement_summary_html = markdown.markdown(improvement_summary)
            
            return jsonify({
                "improved_text": improved_text_html,
                "improvement_summary": improvement_summary_html
            })
        else:
            return jsonify({"error": "Failed to improve text"}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)