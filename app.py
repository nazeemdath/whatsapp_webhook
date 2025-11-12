from flask import Flask, request
import requests, os, json
from dotenv import load_dotenv
from backend.db import query_products_by_name  # ✅ Supabase DB query function

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Configuration
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nazeem_webhook_123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


# ------------------------------------------------------------------------------------
# ✅ Home Route (for Render testing)
# ------------------------------------------------------------------------------------
@app.route('/')
def home():
    return "🚀 Flask WhatsApp + Supabase Webhook is running successfully on Render!"


# ------------------------------------------------------------------------------------
# ✅ Webhook Route (Verification + Incoming Messages)
# ------------------------------------------------------------------------------------
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # 🔍 Meta verification (called when you press Verify in Meta Developer)
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Webhook verification failed.")
            return "Verification failed", 403

    elif request.method == "POST":
        # 📩 Handle incoming messages
        data = request.get_json(force=True, silent=True)
        print("📩 Incoming Webhook Payload:")
        print(json.dumps(data, indent=2))

        try:
            entry = data.get("entry", [])
            if not entry:
                print("⚠️ Empty entry list.")
                return "no entry", 204

            value = entry[0].get("changes", [])[0].get("value", {})
            messages = value.get("messages", [])

            if not messages:
                print("⚠️ No messages found.")
                return "no message", 204

            msg_data = messages[0]
            sender = msg_data.get("from")
            message_text = msg_data.get("text", {}).get("body", "").strip().lower()

            if not sender or not message_text:
                print("⚠️ Empty or malformed message payload.")
                return "ignored", 204

            print(f"💬 Message from {sender}: {message_text}")

            # --------------------------------------------------------------------------------
            # 🧠 Step 1: Try to match products from Supabase
            # --------------------------------------------------------------------------------
            products = query_products_by_name(message_text)

            if products:
                # ✅ Found matching products
                reply_lines = ["📦 *Product Details:*"]
                for p in products:
                    reply_lines.append(
                        f"\n🧾 *{p['name']}* (Model: {p['model']})\n💰 Price: ₹{p['price']}\n📦 Stock: {p['stock']}\n📂 Category: {p['category']}"
                    )
                reply = "\n".join(reply_lines)
            else:
                # ❌ No product found
                reply = (
                    f"Sorry, no products found for '{message_text}'.\n"
                    "Please check the name or try another model."
                )

            # --------------------------------------------------------------------------------
            # 💬 Step 2: Send reply message
            # --------------------------------------------------------------------------------
            send_message(sender, reply)

        except Exception as e:
            print("❌ Error processing webhook:", str(e))

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
        print("📤 Sent message response:", json.dumps(response.json(), indent=2))
        if response.status_code != 200:
            print("⚠️ Message sending failed:", response.text)
    except requests.RequestException as e:
        print("❌ Failed to send message:", e)


# ------------------------------------------------------------------------------------
# ✅ Flask App Runner
# ------------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 WhatsApp-Supabase bot running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
