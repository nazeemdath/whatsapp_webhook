from flask import Flask, request
import requests, os, json
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Configuration
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nazeem_webhook_123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# ------------------------------------------------------------------------------------
# ✅ Home Route
# ------------------------------------------------------------------------------------
@app.route('/')
def home():
    return "🚀 Flask WhatsApp Webhook is live and running!"

# ------------------------------------------------------------------------------------
# ✅ Webhook Route (Verification + Message Handling)
# ------------------------------------------------------------------------------------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # 🌐 Meta verification (only once when connecting webhook)
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Webhook verification failed.")
            return "Verification failed", 403

    elif request.method == "POST":
        # 📨 Handle incoming messages or status updates
        data = request.get_json(force=True, silent=True)
        print("📩 Incoming webhook payload:\n", json.dumps(data, indent=2))

        try:
            # Extract the main object safely
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})

            # Process message events only
            if "messages" in value:
                message = value["messages"][0]
                sender = message.get("from")
                text = message.get("text", {}).get("body", "")

                if not sender or not text:
                    print("⚠️ Message missing sender or text.")
                    return "ignored", 204

                print(f"💬 Message from {sender}: {text}")

                # 🧠 Simple auto-reply logic (you can extend this later)
                reply = f"Hi there! You said: {text}"
                send_message(sender, reply)

            elif "statuses" in value:
                # Ignore delivery/read receipts
                status = value["statuses"][0].get("status")
                msg_id = value["statuses"][0].get("id")
                print(f"ℹ️ Status update for message {msg_id}: {status}")

            else:
                print("ℹ️ Non-message event received, ignored.")

        except IndexError:
            print("⚠️ Unexpected payload structure (IndexError). Payload ignored.")
        except Exception as e:
            print("❌ Error processing payload:", e)

        return "EVENT_RECEIVED", 200

# ------------------------------------------------------------------------------------
# ✅ Function to Send WhatsApp Messages
# ------------------------------------------------------------------------------------
def send_message(to, text):
    """Send a WhatsApp message via Cloud API"""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ Missing ACCESS_TOKEN or PHONE_NUMBER_ID in environment.")
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
        result = response.json()
        print("📤 Sent message response:", json.dumps(result, indent=2))

        if response.status_code != 200:
            print("⚠️ Send message failed:", response.text)

    except requests.RequestException as e:
        print("❌ Failed to send message:", e)

# ------------------------------------------------------------------------------------
# ✅ Run Flask App
# ------------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask server on port {port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
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
    print("Using Phone Number ID:", PHONE_NUMBER_ID)
    print("Using Access Token (first 15 chars):", ACCESS_TOKEN[:15])

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
        if response.status_code != 200:
            print("⚠️ Error:", response.text)
    except requests.RequestException as e:
        print("❌ Failed to send message:", e)



# ✅ Correct port handling for Render/Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
