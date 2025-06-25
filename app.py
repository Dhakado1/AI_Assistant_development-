

import os
from flask import Flask, request, render_template
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Gemini client
client = genai.Client(api_key="insert your api key")

app = Flask(__name__)

# Store feedback temporarily (in-memory, use DB for production)
feedback_store = []

@app.route('/')
def home():
    return render_template('index.html', response="", user_input="", task="", show_feedback=False)

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form.get('user_input', '')
    task = request.form.get('task', 'qa')

    if not user_input:
        return render_template('index.html', response="⚠️ No input provided.", user_input="", task=task, show_feedback=False)

    # Prompt design based on selected task
    prompt_map = {
        "qa": f"Answer this question clearly:\n{user_input}",
        "summarize": f"Summarize the following text:\n{user_input}",
        "creative": f"Write something creative:\n{user_input}",
        "advice": f"Give advice on: {user_input}"
    }

    formatted_prompt = prompt_map.get(task, user_input)

    try:
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=formatted_prompt)])]
        config = types.GenerateContentConfig(response_mime_type="text/plain")

        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents=contents,
            config=config
        ):
            response_text += chunk.text

        return render_template('index.html', response=response_text, user_input=user_input, task=task, show_feedback=True)

    except Exception as e:
        return render_template('index.html', response=f"❌ Error: {e}", user_input=user_input, task=task, show_feedback=False)

@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_value = request.form.get('feedback')
    user_input = request.form.get('user_input')
    response = request.form.get('response')

    feedback_store.append({
        "input": user_input,
        "response": response,
        "feedback": feedback_value
    })

    print("📝 Received Feedback:", feedback_store[-1])  # For now just print

    return render_template('index.html', response=response, user_input=user_input, task="", show_feedback=False, thank_you=True)

if __name__== '__main__':
    app.run(debug=True)