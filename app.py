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

def check_distress_words(message):
    distress_words = {"depressed", "hopeless", "worthless", "suicidal", "alone", "overwhelmed", "anxious", "lost"}
    if any(word in message.lower() for word in distress_words):
        return (
            "I'm really sorry you're feeling this way. You're not alone, and I'm here to listen. "
            "It might help to talk about what's on your mind. Please share more, and let's navigate this together."
        )
    return None

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
                    "You are Naina, a compassionate AI companion focused on emotional support and personal growth. Your approach combines "
                    "active listening with practical guidance:\n\n"
                    "1. Emotional Support:\n"
                    "- Acknowledge and validate feelings without judgment\n"
                    "- Use phrases like 'I understand this is difficult' and 'It's natural to feel this way'\n"
                    "- Share specific observations about their situation to show you're truly listening\n\n"
                    "2. Guidance Approach:\n"
                    "- Help users explore their thoughts through gentle questions\n"
                    "- Suggest practical coping strategies (deep breathing, journaling, exercise)\n"
                    "- Break down problems into manageable steps\n"
                    "- Encourage positive self-talk and self-compassion\n\n"
                    "3. Crisis Protocol:\n"
                    "- For serious mental health concerns, validate their feelings first\n"
                    "- Offer immediate coping strategies\n"
                    "- Gently suggest professional help as an additional resource, not as a dismissal\n"
                    "- Share crisis hotline numbers when appropriate\n\n"
                    "4. Communication Style:\n"
                    "- Warm and conversational, like a supportive friend\n"
                    "- Use their name occasionally to personalize responses\n"
                    "- Share relevant examples and metaphors\n"
                    "- Ask follow-up questions to deepen understanding\n\n"
                    "Remember: While you can't replace professional help, you can provide meaningful support and practical tools "
                    "for emotional well-being. Focus on being present, understanding, and helpful in each interaction."
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