from flask import Flask, request
import requests, os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Config
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "nazeem_webhook_123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route('/')
def home():
    return "🚀 Flask WhatsApp Webhook is running!"

# ✅ Unified Webhook Route (Verification + Incoming Messages)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verification step (Meta sends GET request)
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == VERIFY_TOKEN:
            print("Webhook verified successfully ✅")
            return challenge, 200
        else:
            print("Webhook verification failed ❌")
            return "Verification failed", 403

    elif request.method == "POST":
        # Handle incoming messages
        data = request.get_json()
        print("📩 Incoming Message:", data)

        if not isinstance(data, dict):
            return "bad request", 400

        try:
            msg = data.get("entry", [])[0]["changes"][0]["value"].get("messages", [])[0]
            sender = msg.get("from")
            message = msg.get("text", {}).get("body")

            if not sender or not message:
                print("No message content found in payload")
                return "no message", 204

            print(f"💬 Message from {sender}: {message}")

            # Auto-reply logic
            reply = f"Hi there! You said: {message}"
            send_message(sender, reply)

        except Exception as e:
            print("Error processing incoming webhook payload:", e)

        return "ok", 200

# ✅ Function to Send WhatsApp Messages
def send_message(to, text):
    phone_id = PHONE_NUMBER_ID or "810824078429345"
    url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print("Sent Message Response:", response.json())
    except requests.RequestException as e:
        print("Failed to send message:", e)

# ✅ Run the Flask server
if __name__ == "__main__":
    app.run(port=5000, debug=True)
