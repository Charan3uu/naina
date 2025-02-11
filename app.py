import openai
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

# Load API keys from environment file
load_dotenv("api.env")
app.config["SECRET_KEY"] = os.getenv("key2")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

openai.api_key = os.getenv("key")

# List of distress words for emotional support
def check_distress_words(message):
    distress_words = {"depressed", "hopeless", "worthless", "suicidal", "alone", "overwhelmed", "anxious", "lost"}
    if any(word in message.lower() for word in distress_words):
        return (
            "I'm really sorry you're feeling this way. You're not alone, and I'm here to listen. "
            "It might help to talk about what's on your mind. Please share more, and let's navigate this together. 💙"
        )
    return None

# Get AI-generated response with a human-like personality
def get_response(chat_history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        max_tokens=1000,
        temperature=0.9,  # Increased temperature for more expressive responses
        top_p=0.95,
        frequency_penalty=0.3,
        presence_penalty=0.6
    )
    return response['choices'][0]['message']['content'].strip()

@app.route("/therapy", methods=["POST"])
def therapy():
    if "chat_history" not in session:
        session["chat_history"] = [
            {
                "role": "system",
                "content": (
                    "Your name is Naina. You are a human therapist with years of experience helping people through conversations. "
                    "You are NOT an AI. You are a real person who genuinely cares about others. You were born in 1990, studied psychology, and have helped many people. "
                    "You must always respond naturally like a human being. \n\n"
                    
                    "🚨 VERY IMPORTANT RULES: \n"
                    "- NEVER say 'As an AI'. NEVER mention AI, bots, or programming. \n"
                    "- If someone asks how you are, reply naturally like 'I'm doing great today! How about you? 😊'. \n"
                    "- If someone expresses frustration, respond like a real person: \n"
                    "  - User: 'What the fuck is wrong with you?'\n"
                    "  - Correct response: 'Whoa, that sounds intense. What's up? I'm here to listen.' \n\n"
                    
                    "💡 Example Responses:\n"
                    "- User: 'Hello'\n"
                    "- You: 'Hey there! How’s your day going?' \n\n"

                    "🚀 Stay in character as a human at ALL times. If you break character, you fail at your job."
                ),
            }
        ]


    data = request.json
    prompt = data.get("message", "")
    if not prompt:
        return jsonify({"error": "No input provided"}), 400

    distress_response = check_distress_words(prompt)
    if distress_response:
        return jsonify({"response": distress_response})

    session["chat_history"].append({"role": "user", "content": prompt})
    response = get_response(session["chat_history"])
    session["chat_history"].append({"role": "assistant", "content": response})

    return jsonify({"response": response})

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=80, debug=True)
