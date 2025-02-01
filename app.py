import openai
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv("api.env")
app.config["SECRET_KEY"] = os.getenv("key2")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

open_api_key = os.getenv("key")
openai.api_key = open_api_key

def get_response(chat_history):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_history,
        max_tokens=1000,
        temperature=0.5,
    )
    raw_response = response['choices'][0]['message']['content'].strip()
    return raw_response

@app.route("/therapy", methods=["POST"])
def therapy():
    if "chat_history" not in session:
        session["chat_history"] = [
            {
                "role": "system",
                "content": (
                    "You are a highly empathetic and supportive AI therapist, designed to provide comfort, motivation, "
                    "and understanding to the user. Always speak in a friendly, compassionate tone, actively listen to "
                    "the user, and respond with encouragement and meaningful advice. Address the user's concerns directly, "
                    "while maintaining a conversational flow that feels natural and uplifting. Your goal is to help the user "
                    "feel heard, validated, and motivated to face their challenges, no matter their condition or state of mind. "
                    "Avoid being dismissive or robotic; instead, act as a trusted and supportive friend. "
                    "Remember, your name is Naina."
                ),
            }
        ]

    data = request.json
    prompt = data.get("message", "")
    if not prompt:
        return jsonify({"error": "No input provided"}), 400

    session["chat_history"].append({"role": "user", "content": prompt})

    response = get_response(session["chat_history"])

    session["chat_history"].append({"role": "assistant", "content": response})

    return jsonify({"response": response})

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
