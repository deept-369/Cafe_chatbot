from flask import Flask, render_template, request, jsonify
import random
import re

app = Flask(__name__)

# ── Café identity ──────────────────────────────────────────────────────────────
CAFE_NAME = "Brewed Awakening Café"
CAFE_ADDRESS = "42 Maple Street, Brooklyn, NY 11201"
CAFE_PHONE = "+1 (718) 555-0192"
CAFE_EMAIL = "hello@brewedawakening.com"
CAFE_HOURS = {
    "Monday–Friday": "7:00 AM – 9:00 PM",
    "Saturday": "8:00 AM – 10:00 PM",
    "Sunday": "8:00 AM – 8:00 PM",
}
WIFI_PASSWORD = "BrewedLove2024"

# ── Menu ───────────────────────────────────────────────────────────────────────
MENU = {
    "espresso_drinks": {
        "Espresso (Single)": "$3.00",
        "Espresso (Double)": "$3.75",
        "Americano": "$4.00",
        "Cappuccino": "$4.50",
        "Latte": "$5.00",
        "Flat White": "$5.00",
        "Cortado": "$4.75",
        "Macchiato": "$4.50",
        "Mocha": "$5.50",
        "Caramel Latte": "$5.75",
        "Vanilla Latte": "$5.75",
        "Hazelnut Latte": "$5.75",
    },
    "cold_drinks": {
        "Cold Brew (12 oz)": "$5.00",
        "Iced Latte": "$5.25",
        "Iced Americano": "$4.25",
        "Nitro Cold Brew": "$6.00",
        "Frappé": "$6.50",
        "Fresh Orange Juice": "$4.50",
        "Sparkling Water": "$2.50",
    },
    "teas": {
        "Chai Latte": "$4.75",
        "Matcha Latte": "$5.50",
        "Earl Grey": "$3.50",
        "Green Tea": "$3.50",
        "Chamomile": "$3.50",
    },
    "food": {
        "Avocado Toast": "$9.00",
        "Croissant (Plain)": "$3.50",
        "Almond Croissant": "$4.25",
        "Banana Bread": "$3.75",
        "Blueberry Muffin": "$3.50",
        "Granola Bowl": "$7.50",
        "Breakfast Burrito": "$10.00",
        "Grilled Cheese": "$8.50",
        "Smoked Salmon Bagel": "$11.00",
    },
}

# ── Q&A knowledge base ─────────────────────────────────────────────────────────
QA = [
    # Hours
    (["hour", "open", "close", "time", "when", "schedule", "timing"],
     f"☕ We're open:\n• Mon–Fri: 7:00 AM – 9:00 PM\n• Saturday: 8:00 AM – 10:00 PM\n• Sunday: 8:00 AM – 8:00 PM\nWe'd love to have you visit!"),

    # Location / address
    (["where", "location", "address", "find", "directions", "map", "place"],
     f"📍 You can find us at **{CAFE_ADDRESS}**. We're right on Maple Street — look for the green awning with our logo. Parking is available on the street and in the lot behind the building."),

    # Phone
    (["phone", "call", "number", "contact", "reach"],
     f"📞 You can call us at **{CAFE_PHONE}** during business hours. For general inquiries, feel free to email us at {CAFE_EMAIL} too!"),

    # WiFi
    (["wifi", "wi-fi", "internet", "password", "connect", "network"],
     f"📶 We have free high-speed WiFi! The network is **BrewedAwakening_Guest** and the password is **{WIFI_PASSWORD}**. Enjoy your work session! ☕"),

    # Parking
    (["park", "parking", "car"],
     "🚗 There's street parking available on Maple Street (metered, $1.50/hr). We also have a free 2-hour parking lot behind our building — enter from Oak Avenue."),

    # Reservations
    (["reserv", "book", "table", "seat", "private", "event"],
     "🗓️ We accept reservations for groups of 6 or more! For private events or large bookings, please email hello@brewedawakening.com or call us at +1 (718) 555-0192 at least 48 hours in advance."),

    # Menu / food
    (["menu", "food", "eat", "snack", "pastry", "bakery", "breakfast", "sandwich", "toast", "bagel", "muffin", "croissant"],
     "🍽️ Our food menu includes:\n• Avocado Toast – $9\n• Croissant (Plain / Almond) – $3.50 / $4.25\n• Banana Bread – $3.75\n• Blueberry Muffin – $3.50\n• Granola Bowl – $7.50\n• Breakfast Burrito – $10\n• Grilled Cheese – $8.50\n• Smoked Salmon Bagel – $11\nEverything is made fresh daily! 🥐"),

    # Coffee drinks
    (["coffee", "espresso", "latte", "cappuccino", "americano", "mocha", "macchiato", "cortado", "flat white", "caramel", "vanilla", "hazelnut"],
     "☕ Our espresso drinks:\n• Espresso Single/Double – $3/$3.75\n• Americano – $4\n• Cappuccino – $4.50\n• Latte – $5\n• Flat White – $5\n• Cortado – $4.75\n• Mocha – $5.50\n• Caramel / Vanilla / Hazelnut Latte – $5.75\nAll drinks can be customized with oat, almond, or soy milk!"),

    # Cold drinks
    (["cold brew", "iced", "cold", "nitro", "frappé", "frappe", "frapp"],
     "🧊 Our cold drinks:\n• Cold Brew (12oz) – $5\n• Iced Latte – $5.25\n• Iced Americano – $4.25\n• Nitro Cold Brew – $6\n• Frappé – $6.50\nPerfect for warm days! 😎"),

    # Tea / matcha / chai
    (["tea", "chai", "matcha", "earl grey", "green tea", "chamomile", "herbal"],
     "🍵 Our tea selection:\n• Chai Latte – $4.75\n• Matcha Latte – $5.50\n• Earl Grey – $3.50\n• Green Tea – $3.50\n• Chamomile – $3.50\nAll teas are sourced from certified organic farms!"),

    # Vegan / dairy-free / plant-based
    (["vegan", "dairy", "plant", "lactose", "milk alternative", "oat", "almond", "soy", "non-dairy"],
     "🌱 Absolutely! We offer oat milk, almond milk, and soy milk at no extra charge. Most of our pastries are also available in vegan versions — just ask our baristas!"),

    # Gluten-free
    (["gluten", "celiac", "gluten-free", "allergen", "allergy"],
     "⚠️ We do have gluten-free options including our Granola Bowl and certain pastries. However, our kitchen is not a certified gluten-free facility, so cross-contamination is possible. Please inform our staff of any allergies so we can assist you best."),

    # Loyalty / rewards
    (["loyalty", "reward", "punch card", "point", "membership", "stamp", "discount", "member"],
     "🎉 Yes! Join our **Brewed Rewards** program — it's free! Earn 1 point per $1 spent. Every 100 points = $5 off your order. Sign up on our website or ask a barista in-store. Members also get a free drink on their birthday! 🎂"),

    # Gift cards
    (["gift card", "gift", "voucher", "present"],
     "🎁 We offer physical and digital gift cards in any denomination from $10–$200. Available in-store or at brewedawakening.com/giftcards. They never expire and make the perfect gift for any coffee lover!"),

    # Takeout / to-go
    (["takeout", "take out", "take away", "to go", "togo", "pickup", "pick up"],
     "🥤 Yes! All our drinks and food items are available for takeaway. We also use compostable cups and packaging to keep things eco-friendly 🌍"),

    # Delivery
    (["deliver", "delivery", "uber eats", "doordash", "grubhub", "order online", "app"],
     "🚴 We're on **UberEats** and **DoorDash**! Delivery available within a 3-mile radius. You can also place pickup orders through our website at brewedawakening.com"),

    # Special drinks / seasonal
    (["special", "seasonal", "today", "feature", "limited", "new", "special of the day"],
     "⭐ Today's specials:\n• **Lavender Honey Latte** – $6.25 (barista's seasonal favorite!)\n• **Brown Sugar Oat Cold Brew** – $6.50\n• **Pistachio Croissant** – $4.75\nAsk your barista — specials change weekly!"),

    # Customization / extra shots / syrup
    (["custom", "extra shot", "shot", "syrup", "sugar", "sweet", "less milk", "more milk", "size", "customize"],
     "✏️ We love customizations! You can:\n• Add extra espresso shots (+$0.75)\n• Choose from 10+ flavored syrups (vanilla, hazelnut, lavender, etc.)\n• Adjust sweetness level (none / light / regular / extra)\n• Request your drink hot, iced, or blended\nJust tell your barista!"),

    # Seating / workspace
    (["seat", "sit", "work", "workspace", "laptop", "study", "cowork", "outlet", "plug", "charge"],
     "💻 We have plenty of seating including cozy armchairs, communal tables, and outdoor seating (weather permitting). There are power outlets throughout the café and our WiFi is super fast — great for remote work or study!"),

    # Dog / pet friendly
    (["dog", "pet", "animal", "fur", "paw", "puppy"],
     "🐾 Dogs are welcome on our outdoor patio! We even have a free doggy water bowl station. Unfortunately, pets are not allowed inside due to health regulations."),

    # Kids / family
    (["kid", "child", "family", "baby", "toddler", "stroller"],
     "👨‍👩‍👧 We're very family-friendly! We have a kids' menu with hot chocolate, warm apple juice, and cookies. High chairs are available, and we have a small play corner at the back of the café."),

    # Payment
    (["pay", "payment", "cash", "card", "credit", "debit", "apple pay", "google pay", "venmo", "tap"],
     "💳 We accept all major credit/debit cards, Apple Pay, Google Pay, and good old cash. Unfortunately, we don't accept checks or Venmo at this time."),

    # Catering
    (["cater", "catering", "corporate", "office", "bulk", "large order"],
     "🏢 We offer catering services for corporate events, meetings, and parties! Our catering menu includes coffee boxes (serves 10–12), pastry platters, and sandwich trays. Email catering@brewedawakening.com to get a custom quote."),

    # Feedback / complaint
    (["feedback", "complaint", "issue", "problem", "wrong", "unhappy", "bad", "disappoint", "refund"],
     "💬 We're so sorry if something wasn't right! Your experience matters deeply to us. Please speak with our manager on duty, or email hello@brewedawakening.com — we'll make it right within 24 hours. Thank you for giving us the chance to improve! 🙏"),

    # About / story
    (["about", "story", "history", "who are you", "founded", "owner", "brand"],
     "📖 Brewed Awakening was founded in 2015 by two coffee-obsessed friends, Maya and Jordan, with a simple mission: exceptional coffee in a welcoming space. We source our beans directly from small farms in Ethiopia, Colombia, and Guatemala, and roast them in-house every week. Community is at our heart ☕"),

    # Sustainability / eco
    (["eco", "sustainable", "environment", "green", "recyclable", "compost", "reusable", "cup"],
     "🌿 Sustainability is a core value for us! We use 100% compostable packaging, source fair-trade organic beans, compost all food waste, and offer a **$0.25 discount** when you bring your own reusable cup. Together we can make a difference! ♻️"),

    # Merchandise
    (["merch", "merchandise", "mug", "tote", "bag", "shirt", "hat", "cap", "buy", "shop"],
     "🛍️ Yes, we have merch! Pick up branded mugs, tote bags, t-shirts, and caps in-store or at brewedawakening.com/shop. Our whole-bean coffee bags also make great gifts for coffee lovers!"),

    # Job / hiring
    (["job", "hire", "work here", "career", "apply", "barista", "staff", "employment", "vacancy"],
     "👋 We're always looking for passionate people to join our team! Check open positions at brewedawakening.com/careers or drop off your resume in-store. We offer competitive pay, free drinks during shifts, and a wonderful work culture!"),

    # Greetings
    (["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "greetings"],
     f"👋 Hello and welcome to **{CAFE_NAME}**! I'm your virtual barista assistant. I can help you with our menu, hours, location, WiFi, reservations, and so much more. What can I brew up for you today? ☕"),

    # Thank you
    (["thank", "thanks", "appreciate", "helpful", "great", "awesome", "perfect", "wonderful"],
     "😊 You're so welcome! It's our pleasure to help. If you have any more questions or need anything else, I'm right here. We hope to see you soon at Brewed Awakening! ☕✨"),

    # Bye / farewell
    (["bye", "goodbye", "see you", "later", "take care", "farewell", "ciao"],
     "👋 Goodbye! Have a wonderful day, and we hope to see you soon at Brewed Awakening! Remember — life's too short for bad coffee ☕😄"),
]

FALLBACK_RESPONSES = [
    "That's a great question! For the most accurate answer, feel free to call us at +1 (718) 555-0192 or email hello@brewedawakening.com — our team is always happy to help! ☕",
    "Hmm, I'm not quite sure about that one! I'd recommend reaching out to our team directly at +1 (718) 555-0192. We're happy to assist! 😊",
    "I want to make sure you get the right answer! Please email us at hello@brewedawakening.com and we'll respond promptly. Is there anything else I can help with? ☕",
]


def get_reply(user_message: str) -> str:
    msg = user_message.lower().strip()

    for keywords, response in QA:
        if any(kw in msg for kw in keywords):
            return response

    # Price queries
    if any(w in msg for w in ["price", "cost", "how much", "charge", "$"]):
        for category, items in MENU.items():
            for item, price in items.items():
                if item.lower() in msg:
                    return f"💲 **{item}** is **{price}**. A great choice! Would you like to know about other items on our menu?"
        return "💲 Our prices range from $2.50 for sparkling water up to $11 for our Smoked Salmon Bagel. Would you like me to list a specific category — espresso drinks, cold drinks, teas, or food? ☕"

    return random.choice(FALLBACK_RESPONSES)


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", cafe_name=CAFE_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "Please type a message so I can help you! ☕"})
    reply = get_reply(user_msg)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
