from flask import Flask, request
import requests, os
from dotenv import load_dotenv

# ✅ Load environment variables (works both locally and on Render/Railway)
load_dotenv()

app = Flask(__name__)

# ✅ Configuration
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nazeem_webhook_123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route('/')
def home():
    return "🚀 Flask WhatsApp Webhook is running on Render!"

# ✅ Webhook Route (Verification + Incoming Messages)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # 🔍 Meta verification (WhatsApp calls this when you press Verify)
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        # ✅ Only check verify_token (hub.mode isn’t mandatory)
        if token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Verification failed.")
            return "Verification failed", 403

    elif request.method == "POST":
        # 📩 Handle incoming messages
        data = request.get_json(force=True, silent=True)
        print("📩 Incoming Message:", data)

        try:
            entry = data.get("entry", [])
            if not entry:
                print("⚠️ Empty entry list.")
                return "no entry", 204

            msg_data = entry[0]["changes"][0]["value"].get("messages", [])[0]
            sender = msg_data.get("from")
            message = msg_data.get("text", {}).get("body")

            if not sender or not message:
                print("⚠️ Empty or malformed message payload.")
                return "no message", 204

            print(f"💬 Message from {sender}: {message}")

            # Auto-reply logic
            reply = f"Hi there! You said: {message}"
            send_message(sender, reply)

        except Exception as e:
            print("⚠️ Error processing payload:", e)

        return "EVENT_RECEIVED", 200


# ✅ Function to Send WhatsApp Messages
def send_message(to, text):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ Missing ACCESS_TOKEN or PHONE_NUMBER_ID.")
        return

    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
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
        print("📤 Sent message response:", response.json())
    except requests.RequestException as e:
        print("❌ Failed to send message:", e)


# ✅ Correct port handling for Render/Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
