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


@app.route('/')
def home():
    return "🚀 Flask WhatsApp Webhook is live and running!"


# ------------------------------------------------------------------------------------
# ✅ Webhook Route (Verification + Incoming Messages)
# ------------------------------------------------------------------------------------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # 🧾 Webhook Verification
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Webhook verification failed.")
            return "Verification failed", 403

    elif request.method == "POST":
        # 📩 Incoming messages and status events
        data = request.get_json(force=True, silent=True)
        print("📩 Incoming Webhook Payload:")
        print(json.dumps(data, indent=2))

        try:
            # Safety: check if entry and changes exist
            if not data.get("entry"):
                print("⚠️ No entry found in payload.")
                return "no entry", 204

            entry = data["entry"][0]
            changes = entry.get("changes", [])
            if not changes:
                print("⚠️ No changes found.")
                return "no changes", 204

            value = changes[0].get("value", {})

            # Process incoming messages only
            if "messages" in value:
                message = value["messages"][0]
                sender = message.get("from")
                text = message.get("text", {}).get("body", "")

                if not sender or not text:
                    print("⚠️ Empty or malformed message payload.")
                    return "ignored", 204

                print(f"💬 Message from {sender}: {text}")

                # 🧠 Simple reply (extend this logic later)
                reply = f"Hi there! You said: {text}"
                send_message(sender, reply)

            elif "statuses" in value:
                # Status updates (sent, delivered, read, etc.)
                statuses = value.get("statuses", [])
                if statuses:
                    status_event = statuses[0]
                    message_id = status_event.get("id")
                    status = status_event.get("status")
                    timestamp = status_event.get("timestamp")
                    print(f"ℹ️ Message {message_id} → {status} at {timestamp}")
                else:
                    print("ℹ️ Received status event with no details.")

            else:
                print("ℹ️ Ignored non-message event type.")

        except Exception as e:
            print("❌ Error processing payload:", str(e))

        return "EVENT_RECEIVED", 200


# ------------------------------------------------------------------------------------
# ✅ Function to Send WhatsApp Messages
# ------------------------------------------------------------------------------------
def send_message(to, text):
    """Send a WhatsApp message using Cloud API"""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ Missing ACCESS_TOKEN or PHONE_NUMBER_ID.")
        return

    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        print("📤 Sent message response:", json.dumps(res_data, indent=2))
        if response.status_code != 200:
            print("⚠️ Message sending failed:", response.text)
    except requests.RequestException as e:
        print("❌ Error sending message:", str(e))


# ------------------------------------------------------------------------------------
# ✅ Flask App Runner
# ------------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask WhatsApp bot on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
