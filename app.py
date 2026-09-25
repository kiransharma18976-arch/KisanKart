from flask import Flask, render_template, request, redirect, url_for, session
import os
import time
from functools import lru_cache
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.secret_key = "kisankart_secret_key_2026"

@app.context_processor
def inject_user():
    return {
        "logged_in": "user_id" in session,
        "user_id": session.get("user_id"),
        "user_name": session.get("user_name"),
        "user_role": session.get("user_role"),
        "user_location": session.get("user_location")
    }

def message_page(
    title,
    message,
    icon="✨",
    button_text="Go Back",
    button_url="/"
):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title} | KisanKart</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                min-height: 100vh;
                font-family: Arial, Helvetica, sans-serif;

                background:
                    linear-gradient(
                        135deg,
                    );

                display: flex;
                justify-content: center;
                align-items: center;

                padding: 25px;
            }}

            .message-card {{
                width: 100%;
                max-width: 560px;

                background: rgba(255,255,255,0.96);

                border-radius: 28px;
                padding: 45px 35px;

                text-align: center;

                box-shadow:
                    0 20px 60px
                    rgba(0,0,0,0.12);

                animation: appear 0.5s ease;
            }}

            @keyframes appear {{
                from {{
                    opacity: 0;
                    transform:
                        translateY(25px)
                        scale(0.97);
                }}

                to {{
                    opacity: 1;
                    transform:
                        translateY(0)
                        scale(1);
                }}
            }}

            .icon {{
                width: 90px;
                height: 90px;

                margin: 0 auto 22px;

                border-radius: 50%;

                background:
                    linear-gradient(
                        135deg,
                    );

                display: flex;
                align-items: center;
                justify-content: center;

                font-size: 42px;

                box-shadow:
                    0 10px 25px
                    rgba(67,160,71,0.25);
            }}

            h1 {{
                color: #1b5e20;
                font-size: 30px;
                margin-bottom: 15px;
            }}

            p {{
                color: #607d63;
                font-size: 16px;
                line-height: 1.7;
                margin-bottom: 25px;
            }}

            .btn {{
                display: inline-block;

                text-decoration: none;

                background:
                    linear-gradient(
                        135deg,
                    );

                color: white;

                padding: 14px 28px;

                border-radius: 14px;

                font-weight: bold;

                transition: 0.25s;

                box-shadow:
                    0 8px 20px
                    rgba(46,125,50,0.25);
            }}

            .btn:hover {{
                transform: translateY(-2px);

                box-shadow:
                    0 12px 25px
                    rgba(46,125,50,0.35);
            }}

            .footer {{
                margin-top: 25px;
                font-size: 13px;
                color: #9e9e9e;
            }}
        </style>
    </head>

    <body>

        <div class="message-card">

            <div class="icon">
                {icon}
            </div>

            <h1>
                {title}
            </h1>

            <p>
                {message}
            </p>

            <a
                class="btn"
                href="{button_url}"
            >
                {button_text}
            </a>

            <div class="footer">
                🌱 KisanKart — Connecting Farmers & Buyers
            </div>

        </div>

    </body>
    </html>
    """

def get_product_image(product_name, uploaded_image=None):

    uploaded = str(uploaded_image or "").strip()

    if uploaded:
        if uploaded.startswith("/"):
            return uploaded

        if uploaded.startswith("http://") or uploaded.startswith("https://"):
            return uploaded

        return url_for(
            "static",
            filename=uploaded
        )

    name = str(product_name or "").lower().strip()

    online_image_map = {
        "strawberry": "https://commons.wikimedia.org/wiki/Special:FilePath/Strawberries.jpg?width=900",

        "pigeon pea": "https://commons.wikimedia.org/wiki/Special:FilePath/Split_pigeon_peas.jpg?width=900",
        "pigeon peas": "https://commons.wikimedia.org/wiki/Special:FilePath/Split_pigeon_peas.jpg?width=900",
        "toor dal": "https://commons.wikimedia.org/wiki/Special:FilePath/Split_pigeon_peas.jpg?width=900",
        "tuar dal": "https://commons.wikimedia.org/wiki/Special:FilePath/Split_pigeon_peas.jpg?width=900",
        "tur dal": "https://commons.wikimedia.org/wiki/Special:FilePath/Split_pigeon_peas.jpg?width=900",
        "arhar dal": "https://commons.wikimedia.org/wiki/Special:FilePath/Split_pigeon_peas.jpg?width=900",
        "green gram": "https://commons.wikimedia.org/wiki/Special:FilePath/Green_Gram_Dal_%28_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%B8%E0%A6%B9_%E0%A6%8F%E0%A6%AC%E0%A6%82_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%9B%E0%A6%BE%E0%A6%A1%E0%A6%BC%E0%A6%BE_%E0%A6%AE%E0%A7%81%E0%A6%97_%E0%A6%A1%E0%A6%BE%E0%A6%B2%29.JPG?width=900",
        "green gram dal": "https://commons.wikimedia.org/wiki/Special:FilePath/Green_Gram_Dal_%28_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%B8%E0%A6%B9_%E0%A6%8F%E0%A6%AC%E0%A6%82_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%9B%E0%A6%BE%E0%A6%A1%E0%A6%BC%E0%A6%BE_%E0%A6%AE%E0%A7%81%E0%A6%97_%E0%A6%A1%E0%A6%BE%E0%A6%B2%29.JPG?width=900",
        "mung bean": "https://commons.wikimedia.org/wiki/Special:FilePath/Green_Gram_Dal_%28_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%B8%E0%A6%B9_%E0%A6%8F%E0%A6%AC%E0%A6%82_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%9B%E0%A6%BE%E0%A6%A1%E0%A6%BC%E0%A6%BE_%E0%A6%AE%E0%A7%81%E0%A6%97_%E0%A6%A1%E0%A6%BE%E0%A6%B2%29.JPG?width=900",
        "mung beans": "https://commons.wikimedia.org/wiki/Special:FilePath/Green_Gram_Dal_%28_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%B8%E0%A6%B9_%E0%A6%8F%E0%A6%AC%E0%A6%82_%E0%A6%96%E0%A7%8B%E0%A6%B8%E0%A6%BE_%E0%A6%9B%E0%A6%BE%E0%A6%A1%E0%A6%BC%E0%A6%BE_%E0%A6%AE%E0%A7%81%E0%A6%97_%E0%A6%A1%E0%A6%BE%E0%A6%B2%29.JPG?width=900",
        "garam masala": "https://commons.wikimedia.org/wiki/Special:FilePath/Garam_Masala.JPG?width=900",
        "garam masala powder": "https://commons.wikimedia.org/wiki/Special:FilePath/Garam_Masala.JPG?width=900",
        "lentils": "https://commons.wikimedia.org/wiki/Special:FilePath/Masoor_daal.jpg?width=900",
        "lentil": "https://commons.wikimedia.org/wiki/Special:FilePath/Masoor_daal.jpg?width=900",
        "masoor": "https://commons.wikimedia.org/wiki/Special:FilePath/Masoor_daal.jpg?width=900",
        "masoor dal": "https://commons.wikimedia.org/wiki/Special:FilePath/Masoor_daal.jpg?width=900",
    }

    image_search_name = name.split("(", 1)[0].strip()

    if image_search_name in online_image_map:
        return online_image_map[image_search_name]

    for keyword, image_url in sorted(online_image_map.items(), key=lambda item: len(item[0]), reverse=True):
        if keyword in name:
            return image_url

    image_map = {
        "tomato": "tomato.jpg",
        "potato": "potato.jpg",
        "onion": "onion.jpg",
        "carrot": "carrot.jpg",
        "cabbage": "cabbage.jpg",
        "cauliflower": "cauliflower.jpg",
        "spinach": "spinach.jpg",
        "brinjal": "brinjal.jpg",
        "capsicum": "capsicum.jpg",
        "peas": "peas.jpg",
        "lady finger": "lady.jpg",
        "ladyfinger": "lady.jpg",
        "okra": "lady.jpg",

        "apple": "apple.jpg",
        "banana": "banana.jpg",
        "orange": "orange.jpg",
        "mango": "mango.jpg",
        "grapes": "grapes.jpg",
        "pomegranate": "pomegranate.jpg",
        "papaya": "papaya.jpg",
        "guava": "guava.jpg",
        "watermelon": "watermelon.jpg",
        "muskmelon": "Muskmelon.jpg",

        "premium basmati rice": "Premium Basmati Rice.jpg",
        "basmati rice": "Premium Basmati Rice.jpg",
        "wheat": "Wheat.jpg",
        "maize": "Maize.jpg",
        "jowar": "Jowar.jpg",
        "bajra": "bajra.jpg",
        "brown rice": "Brown Rice.jpg",
        "poha rice": "poha rice.jpg",
        "sona masoori rice": "Sona Masoori Rice.jpg",
        "ragi": "Ragi.jpg",
        "barley": "Barley.jpg",

        "fresh cow milk": "fresh Cow Milk.jpg",
        "cow milk": "fresh Cow Milk.jpg",
        "buffalo milk": "Buffalo Milk.jpg",
        "fresh curd": "Fresh Curd.jpg",
        "curd": "Fresh Curd.jpg",
        "paneer": "Paneer.jpg",
        "butter": "Butter.jpg",
        "ghee": "Ghee.jpg",
        "cheese": "Cheese.jpg",
        "buttermilk": "Buttermilk.jpg",
        "fresh cream": "Fresh Cream.jpg",
        "milk powder": "Milk Powder.jpg",

        "red chilli": "Red Chilli.jpg",
        "red chili": "Red Chilli.jpg",
        "turmeric": "Turmeric.jpg",
        "coriander seeds": "Coriander Seeds.jpg",
        "cumin seeds": "Cumin Seeds.jpg",
        "black pepper": "Black Pepper.jpg",
        "fennel seeds": "Fennel Seeds.jpg",
        "mustard seeds": "Mustard Seeds.jpg",
        "fenugreek seeds": "Fenugreek Seeds.jpg",
        "cloves": "Cloves.jpg",
        "cardamom": "Cardamom.jpg"
    }

    if name in image_map:
        return url_for(
            "static",
            filename="images/" + image_map[name]
        )

    for keyword, filename in image_map.items():
        if keyword in name:
            return url_for(
                "static",
                filename="images/" + filename
            )

    image_search_name = name.split("(", 1)[0].strip() if "(" in name else name
    if image_search_name:
        online_url = get_wikimedia_product_image(image_search_name)
        if online_url:
            return online_url

    return url_for(
        "static",
        filename="images/food.jpg"
    )

@lru_cache(maxsize=256)
def get_wikimedia_product_image(product_name):
    try:
        import requests

        query = str(product_name or '').strip()
        if not query:
            return None

        api_url = 'https://commons.wikimedia.org/w/api.php'
        params = {
            'action': 'query',
            'generator': 'search',
            'gsrsearch': query,
            'gsrnamespace': 6,
            'gsrlimit': 8,
            'prop': 'imageinfo',
            'iiprop': 'url',
            'iiurlwidth': 900,
            'format': 'json',
            'origin': '*',
        }

        response = requests.get(
            api_url,
            params=params,
            timeout=4,
            headers={'User-Agent': 'KisanKart/1.0 product image lookup'}
        )
        response.raise_for_status()
        data = response.json()

        pages = list((data.get('query') or {}).get('pages', {}).values())
        if not pages:
            return None

        normalized = ' '.join(query.lower().split())
        def score(page):
            title = str(page.get('title', '')).lower()
            title = title.replace('file:', '').replace('_', ' ')
            score_value = 0
            if normalized in title:
                score_value += 100
            for word in normalized.split():
                if len(word) >= 3 and word in title:
                    score_value += 10
            return score_value

        pages.sort(key=score, reverse=True)

        for page in pages:
            info = (page.get('imageinfo') or [{}])[0]
            image_url = info.get('thumburl') or info.get('url')
            if image_url:
                return image_url

    except Exception:
        return None

    return None

app.jinja_env.globals["get_product_image"] = get_product_image

def get_food_image(food_name, uploaded_image=None):
    uploaded = str(uploaded_image or "").strip()

    if uploaded:
        if uploaded.startswith("http://") or uploaded.startswith("https://"):
            return uploaded

        if uploaded.startswith("/static/"):
            return uploaded

        if uploaded.startswith("static/"):
            return "/" + uploaded

        return url_for(
            "static",
            filename="uploads/donations/" + uploaded
        )

    name = str(food_name or "").lower().strip()

    local_food_map = {
        "tomato": "tomato.jpg",
        "potato": "potato.jpg",
        "onion": "onion.jpg",
        "carrot": "carrot.jpg",
        "cabbage": "cabbage.jpg",
        "cauliflower": "cauliflower.jpg",
        "spinach": "spinach.jpg",
        "apple": "apple.jpg",
        "banana": "banana.jpg",
        "mango": "mango.jpg",
        "grapes": "grapes.jpg",
        "paneer": "Paneer.jpg",
        "curd": "Fresh Curd.jpg",
        "milk": "fresh Cow Milk.jpg",
        "cheese": "Cheese.jpg",
        "butter": "Butter.jpg",
        "ghee": "Ghee.jpg",
        "wheat": "Wheat.jpg",
        "basmati rice": "Premium Basmati Rice.jpg",
        "poha": "poha rice.jpg",
    }

    for keyword in sorted(local_food_map, key=len, reverse=True):
        if keyword in name:
            filename = local_food_map[keyword]
            local_file = os.path.join(app.static_folder, "images", filename)
            if os.path.exists(local_file):
                return url_for("static", filename="images/" + filename)

    online_food_map = [
        ("paneer", "Matar Paneer"),
        ("dal", "Dal fry"),
        ("biryani", "Lamb Biryani"),
        ("pulao", "Lamb Biryani"),
        ("rice", "Arroz al horno"),
        ("vegetable", "Vegetarian Casserole"),
        ("sabji", "Matar Paneer"),
        ("sabzi", "Matar Paneer"),
        ("curry", "Kidney Bean Curry"),
        ("chapati", "Matar Paneer"),
        ("roti", "Matar Paneer"),
        ("khichdi", "Vegetable Khichdi"),
        ("potato", "Spicy North African Potato Salad"),
        ("tomato", "Creamy Tomato Soup"),
        ("salad", "Mediterranean Pasta Salad"),
        ("pasta", "Mediterranean Pasta Salad"),
        ("pizza", "Pizza Express Margherita"),
        ("bread", "Bread omelette"),
    ]

    try:
        import requests

        selected_search = None
        for keyword, search_term in online_food_map:
            if keyword in name:
                selected_search = search_term
                break

        search_terms = []
        if selected_search:
            search_terms.append(selected_search)
        if str(food_name or "").strip() and str(food_name or "").strip() not in search_terms:
            search_terms.append(str(food_name or "").strip())

        for search_term in search_terms:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/search.php",
                params={"s": search_term},
                timeout=2.5
            )

            if response.ok:
                data = response.json()
                meals = data.get("meals") or []
                if meals and meals[0].get("strMealThumb"):
                    return meals[0]["strMealThumb"]

    except Exception:
        pass

    return url_for("static", filename="images/food.jpg")

app.jinja_env.globals["get_food_image"] = get_food_image

def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "kiran123"),
        database=os.getenv("DB_NAME", "kisankart")
    )

def ensure_notification_table():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                is_read TINYINT(1) DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_notifications_user (user_id),
                INDEX idx_notifications_read (user_id, is_read)
            )
        """)

        connection.commit()

    except Exception as e:
        print("Notification table setup warning:", e)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

def create_notification(cursor, user_id, title, message):
    try:
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message)
            VALUES (%s, %s, %s)
        """, (user_id, title, message))

    except Exception as e:
        print("Notification insert warning:", e)

def get_unread_notification_count(user_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        result = cursor.fetchone()
        return int(result[0]) if result else 0

    except Exception as e:
        print("Unread notification count warning:", e)
        return 0

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/notifications")
def notifications():

    if "user_id" not in session:
        session["next_url"] = request.path
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                message,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC, id DESC
        """, (session["user_id"],))

        notification_list = cursor.fetchall()

        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = %s
              AND is_read = 0
        """, (session["user_id"],))

        connection.commit()

        return render_template(
            "notifications.html",
            notifications=notification_list
        )

    except Exception as e:
        print("NOTIFICATIONS ERROR:", e)

        return message_page(
            "Unable to Load Notifications",
            "Something went wrong while loading your notifications.",
            "🔔",
            "Back to Dashboard",
            url_for("home")
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route("/")
def home():

    return render_template("index.html")

@app.route("/surplus-food")
def surplus_food():
    return render_template("surplus_food.html")

@app.route("/explore/<category>")
def explore(category):

    category_map = {

        "vegetables": "Vegetables",
        "fruits": "Fruits",
        "grains": "Grains",
        "dairy": "Dairy",
        "spices": "Spices"
    }

    category_name = category_map.get(
        category.lower()
    )

    if not category_name:

        return message_page(
            "Category Not Found",
            "The category you are trying to open does not exist.",
            "🔍",
            "Back to Home",
            url_for("home")
        )

    product_query = request.args.get("product", "").strip()
    selected_location = request.args.get("location", "").strip()

    allowed_locations = {"thane", "pune", "nashik"}
    if selected_location and selected_location.lower() not in allowed_locations:
        return message_page(
            "Location Not Found",
            f"{selected_location} is not available. Please search in Thane, Pune or Nashik.",
            "📍",
            "Back to Home",
            url_for("home")
        )

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            products.*,
            users.first_name,
            users.last_name
        FROM products
        LEFT JOIN users
            ON products.farmer_id = users.id
        WHERE LOWER(TRIM(products.category))
              = LOWER(TRIM(%s))
        AND LOWER(TRIM(products.location))
              IN ('nashik', 'pune', 'thane')
    """
    values = [category_name]

    if product_query:
        query += """
            AND LOWER(products.product_name) LIKE LOWER(%s)
        """
        values.append("%" + product_query + "%")

    query += """
        ORDER BY
            products.location,
            products.id DESC
    """

    cursor.execute(query, values)

    all_products = cursor.fetchall()

    cursor.close()
    connection.close()

    nashik_products = [
        p for p in all_products
        if str(
            p.get("location", "")
        ).strip().lower() == "nashik"
    ]

    pune_products = [
        p for p in all_products
        if str(
            p.get("location", "")
        ).strip().lower() == "pune"
    ]

    thane_products = [
        p for p in all_products
        if str(
            p.get("location", "")
        ).strip().lower() == "thane"
    ]

    wishlist = session.get(
        "wishlist",
        []
    )

    return render_template(
        "explore.html",

        category=category_name,

        nashik_products=nashik_products,

        pune_products=pune_products,

        thane_products=thane_products,

        wishlist=wishlist,

        search_product=product_query,

        selected_location=selected_location
    )

@app.route("/search-products")
def search_products():

    product_query = request.args.get(
        "product",
        ""
    ).strip()

    location_query = request.args.get(
        "location",
        ""
    ).strip()

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            products.*,
            users.first_name,
            users.last_name
        FROM products
        LEFT JOIN users
            ON products.farmer_id = users.id
        WHERE 1=1
    """

    values = []

    if product_query:

        query += """
            AND LOWER(products.product_name)
            LIKE LOWER(%s)
        """

        values.append(
            "%" + product_query + "%"
        )

    if location_query:

        query += """
            AND LOWER(products.location)
            LIKE LOWER(%s)
        """

        values.append(
            "%" + location_query + "%"
        )

    query += """
        ORDER BY products.id DESC
    """

    cursor.execute(
        query,
        values
    )

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "search_results.html",

        products=products,

        product_query=product_query,

        location_query=location_query
    )

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    if "user_id" not in session:

        session["next_url"] = request.path

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "buyer":

        return message_page(
            "Buyer Login Required",
            "Only buyer accounts can add products to the shopping cart.",
            "🛒",
            "Go to Login",
            url_for("login")
        )

    cart = session.get(
        "cart",
        []
    )

    if product_id not in cart:

        cart.append(product_id)

    session["cart"] = cart

    return redirect(
        request.referrer
        or url_for("buyer_products")
    )

@app.route("/remove-from-cart/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get(
        "cart",
        []
    )

    if product_id in cart:

        cart.remove(product_id)

    session["cart"] = cart

    return redirect(
        url_for("cart")
    )

@app.route("/cart")
def cart():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "buyer":

        return message_page(
            "Buyer Account Required",
            "Please login using a buyer account to access your cart.",
            "🛒",
            "Go to Login",
            url_for("login")
        )

    cart_ids = session.get(
        "cart",
        []
    )

    products = []

    if cart_ids:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        placeholders = ",".join(
            ["%s"] * len(cart_ids)
        )

        query = f"""
            SELECT
                products.*,
                users.first_name,
                users.last_name
            FROM products
            LEFT JOIN users
                ON products.farmer_id = users.id
            WHERE products.id IN ({placeholders})
            ORDER BY products.id DESC
        """

        cursor.execute(
            query,
            tuple(cart_ids)
        )

        products = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template(
        "cart.html",
        products=products
    )

@app.route("/wishlist/<int:product_id>")
def toggle_wishlist(product_id):

    if "user_id" not in session:

        session["next_url"] = request.path

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "buyer":

        return message_page(
            "Buyer Login Required",
            "Please login as a buyer to use the wishlist.",
            "❤️",
            "Go to Login",
            url_for("login")
        )

    wishlist = session.get(
        "wishlist",
        []
    )

    if product_id in wishlist:

        wishlist.remove(product_id)

    else:

        wishlist.append(product_id)

    session["wishlist"] = wishlist

    return redirect(
        request.referrer
        or url_for("buyer_products")
    )

@app.route("/wishlist")
def wishlist():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "buyer":

        return message_page(
            "Buyer Account Required",
            "Please login using a buyer account to access your wishlist.",
            "❤️",
            "Go to Login",
            url_for("login")
        )

    wishlist_ids = session.get(
        "wishlist",
        []
    )

    products = []

    if wishlist_ids:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        placeholders = ",".join(
            ["%s"] * len(wishlist_ids)
        )

        query = f"""
            SELECT
                products.*,
                users.first_name,
                users.last_name
            FROM products
            LEFT JOIN users
                ON products.farmer_id = users.id
            WHERE products.id IN ({placeholders})
            ORDER BY products.id DESC
        """

        cursor.execute(
            query,
            tuple(wishlist_ids)
        )

        products = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template(
        "wishlist.html",
        products=products
    )

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            AND password = %s
            """,
            (
                email,
                password
            )
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:

            session["user_id"] = user["id"]

            session["user_role"] = user["role"]

            session["user_name"] = (
                str(user["first_name"])
                + " "
                + str(user["last_name"])
            )

            session["user_location"] = user.get(
                "location"
            )

            next_url = session.pop(
                "next_url",
                None
            )

            if next_url:

                return redirect(
                    next_url
                )

            if user["role"] == "farmer":

                return redirect(
                    url_for(
                        "farmer_dashboard"
                    )
                )

            elif user["role"] == "buyer":

                return redirect(
                    url_for(
                        "buyer_dashboard"
                    )
                )

            elif user["role"] == "ngo":

                return redirect(
                    url_for(
                        "ngo_dashboard"
                    )
                )

        return message_page(
            "Invalid Email or Password",

            "The email or password you entered is incorrect. Please check your details and try again.",

            "❌",

            "Try Again",

            url_for("login")
        )

    return render_template(
        "login.html"
    )

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    first_name = request.form.get(
        "first_name",
        ""
    ).strip()

    last_name = request.form.get(
        "last_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    role = request.form.get(
        "role",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    if (
        not first_name
        or not last_name
        or not email
        or not password
        or not confirm_password
        or not role
    ):

        return message_page(
            "Missing Information",

            "Please fill in all required fields before creating your account.",

            "⚠️",

            "Try Again",

            url_for("register")
        )

    if password != confirm_password:

        return message_page(
            "Passwords Do Not Match",

            "The password and confirm password are different. Please enter the same password in both fields.",

            "🔐",

            "Try Again",

            url_for("register")
        )

    if role not in [
        "farmer",
        "buyer",
        "ngo"
    ]:

        return message_page(
            "Invalid Account Type",

            "Please select a valid account type: Farmer, Buyer or NGO.",

            "⚠️",

            "Try Again",

            url_for("register")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return message_page(
                "Email Already Registered",

                "This email already has an account on KisanKart. Please login using your existing account.",

                "⚠️",

                "Go to Login",

                url_for("login")
            )

        cursor.execute(
            """
            INSERT INTO users
            (
                first_name,
                last_name,
                email,
                phone,
                role,
                buyer_type,
                business_name,
                business_type,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                first_name,
                last_name,
                email,
                phone,
                role,
                ("business" if role == "buyer" else None),
                (f"{first_name} {last_name} Business" if role == "buyer" else None),
                ("Business" if role == "buyer" else None),
                password
            )
        )

        connection.commit()

    except mysql.connector.Error:

        if connection:

            connection.rollback()

        return message_page(
            "Registration Failed",

            "Something went wrong while creating your account. Please check your details and try again.",

            "❌",

            "Try Again",

            url_for("register")
        )

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()

    role_name = role.capitalize()

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Account Created | KisanKart
        </title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <style>

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                min-height: 100vh;

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                background:
                    linear-gradient(
                        135deg,
                    );

                display: flex;
                justify-content: center;
                align-items: center;

                padding: 25px;
            }}

            .success-card {{
                width: 100%;
                max-width: 620px;

                background: white;

                border-radius: 30px;

                padding: 45px 38px;

                text-align: center;

                box-shadow:
                    0 25px 70px
                    rgba(0,0,0,0.13);

                animation:
                    showCard 0.6s ease;
            }}

            @keyframes showCard {{

                from {{
                    opacity: 0;

                    transform:
                        translateY(30px)
                        scale(0.95);
                }}

                to {{
                    opacity: 1;

                    transform:
                        translateY(0)
                        scale(1);
                }}
            }}

            .success-icon {{
                width: 100px;
                height: 100px;

                margin:
                    0 auto 25px;

                border-radius: 50%;

                background:
                    linear-gradient(
                        135deg,
                    );

                display: flex;
                align-items: center;
                justify-content: center;

                color: white;

                font-size: 48px;

                box-shadow:
                    0 12px 30px
                    rgba(46,125,50,0.25);
            }}

            h1 {{
                color: #1b5e20;
                font-size: 31px;
                margin-bottom: 13px;
            }}

            .welcome {{
                font-size: 17px;
                color: #607d63;
                margin-bottom: 28px;
                line-height: 1.6;
            }}

            .name {{
                color: #2e7d32;
                font-weight: bold;
            }}

            .details {{
                background: #f1f8f2;

                border-radius: 18px;

                padding: 20px;

                margin-bottom: 28px;

                text-align: left;
            }}

            .detail-row {{
                display: flex;

                justify-content:
                    space-between;

                gap: 15px;

                padding: 11px 5px;

                border-bottom:
                    1px solid #dcebdc;
            }}

            .detail-row:last-child {{
                border-bottom: none;
            }}

            .label {{
                color: #78907b;
            }}

            .value {{
                color: #1b5e20;

                font-weight: bold;

                text-align: right;
            }}

            .login-btn {{
                display: inline-block;

                text-decoration: none;

                background:
                    linear-gradient(
                        135deg,
                    );

                color: white;

                padding: 15px 32px;

                border-radius: 14px;

                font-weight: bold;

                font-size: 16px;

                box-shadow:
                    0 10px 25px
                    rgba(46,125,50,0.25);

                transition: 0.25s;
            }}

            .login-btn:hover {{
                transform:
                    translateY(-3px);

                box-shadow:
                    0 15px 30px
                    rgba(46,125,50,0.32);
            }}

            .footer {{
                margin-top: 25px;

                color: #9e9e9e;

                font-size: 13px;
            }}

        </style>

    </head>

    <body>

        <div class="success-card">

            <div class="success-icon">
                ✓
            </div>

            <h1>
                Account Created Successfully!
            </h1>

            <p class="welcome">

                Welcome to

                <span class="name">
                    KisanKart
                </span>,

                <span class="name">
                    {first_name} {last_name}
                </span>! 🌱

            </p>

            <div class="details">

                <div class="detail-row">

                    <span class="label">
                        👤 Name
                    </span>

                    <span class="value">
                        {first_name} {last_name}
                    </span>

                </div>

                <div class="detail-row">

                    <span class="label">
                        📧 Email
                    </span>

                    <span class="value">
                        {email}
                    </span>

                </div>

                <div class="detail-row">

                    <span class="label">
                        👥 Account Type
                    </span>

                    <span class="value">
                        {role_name}
                    </span>

                </div>

            </div>

            <a
                href="/login"
                class="login-btn"
            >
                Go to Login →
            </a>

            <div class="footer">

                🌾 KisanKart —
                Connecting Farmers, Buyers & Communities

            </div>

        </div>

    </body>

    </html>
    """

@app.route("/farmer-dashboard")
def farmer_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "farmer":
        return message_page(
            "Access Denied",
            "This dashboard is only available for farmer accounts.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    farmer_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE farmer_id = %s
    """, (farmer_id,))
    total_products = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE products.farmer_id = %s
        AND orders.status IN ('Pending', 'Accepted', 'Processing', 'Out for Delivery')
    """, (farmer_id,))
    active_orders = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(orders.total_amount), 0)
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE products.farmer_id = %s
        AND orders.status = 'Completed'
    """, (farmer_id,))
    total_earnings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            COALESCE(AVG(orders.review_rating), 0),
            COUNT(orders.review_rating)
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE products.farmer_id = %s
        AND orders.review_rating IS NOT NULL
        AND orders.review_rating > 0
    """, (farmer_id,))
    rating_row = cursor.fetchone()

    product_rating = round(float(rating_row[0] or 0), 1)
    review_count = int(rating_row[1] or 0)

    cursor.close()
    connection.close()

    return render_template(
        "farmer_dashboard.html",
        total_products=total_products,
        active_orders=active_orders,
        total_earnings=total_earnings,
        product_rating=product_rating,
        review_count=review_count
    )

@app.route("/farmer-reviews")
def farmer_reviews():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "farmer":
        return message_page(
            "Access Denied",
            "Only farmers can view reviews.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    farmer_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT orders.id, orders.review_rating, orders.review_text,
               orders.order_date, orders.buyer_name,
               products.product_name
        FROM orders
        JOIN products ON orders.product_id = products.id
        WHERE products.farmer_id = %s
          AND orders.status = 'Completed'
          AND orders.review_rating IS NOT NULL
          AND orders.review_rating > 0
        ORDER BY orders.id DESC
        """,
        (farmer_id,)
    )

    reviews = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("farmer_reviews.html", reviews=reviews)

@app.route("/farmer-profile")
def farmer_profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "farmer":

        return message_page(
            "Access Denied",

            "Only farmers can access the farmer profile.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            first_name,
            last_name,
            email,
            phone,
            role,
            location,
            created_at
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    farmer = cursor.fetchone()

    cursor.close()
    connection.close()

    if not farmer:

        return message_page(
            "Profile Not Found",

            "We could not find your farmer profile.",

            "👤",

            "Back to Dashboard",

            url_for("farmer_dashboard")
        )

    return render_template(
        "farmer_profile.html",
        farmer=farmer
    )

@app.route("/buyer-dashboard")
def buyer_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Access Denied",
            "Only buyer accounts can access the buyer dashboard.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    unread_notifications = get_unread_notification_count(session["user_id"])

    donation_reviews = []
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sf.id,
                sf.food_name,
                sf.review_rating,
                sf.review_text,
                sf.reviewed_at,
                CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, '')) AS ngo_name
            FROM surplus_food sf
            LEFT JOIN users u ON u.id = sf.ngo_id
            WHERE sf.donor_id = %s
              AND sf.review_rating IS NOT NULL
              AND sf.review_rating > 0
            ORDER BY sf.reviewed_at DESC, sf.id DESC
        """, (session["user_id"],))

        donation_reviews = cursor.fetchall()

    except Exception as e:
        print("BUYER DONATION REVIEWS ERROR:", e)
        donation_reviews = []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template(
        "buyer_dashboard.html",
        unread_notifications=unread_notifications,
        donation_reviews=donation_reviews
    )

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Access Denied",
            "Only buyer accounts can access the buyer profile.",
            "🔒",
            "Go to Dashboard",
            url_for("buyer_dashboard")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            first_name,
            last_name,
            email,
            phone,
            role,
            location,
            created_at
        FROM users
        WHERE id = %s
    """, (session["user_id"],))

    buyer = cursor.fetchone()

    cursor.close()
    connection.close()

    if not buyer:
        return message_page(
            "Profile Not Found",
            "We could not find your buyer profile.",
            "👤",
            "Go to Dashboard",
            url_for("buyer_dashboard")
        )

    return render_template(
        "buyer_profile.html",
        buyer=buyer
    )

@app.route("/donate-surplus-food", methods=["GET", "POST"])
def donate_surplus_food():

    if "user_id" not in session:
        session["next_url"] = request.path
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Access Denied",
            "Only buyer accounts can donate surplus food.",
            "🔒",
            "Go to Dashboard",
            url_for("buyer_dashboard")
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT first_name, last_name, business_name, business_type, location, buyer_type
            FROM users
            WHERE id = %s
        """, (session["user_id"],))

        buyer = cursor.fetchone()

    except Exception as e:
        print("BUYER DETAILS ERROR:", e)
        buyer = None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    if not buyer or buyer.get("buyer_type") != "business":
        return message_page(
            "Business Account Required",
            "Surplus food donation is available for restaurants, messes, canteens and other business buyers.",
            "🏪",
            "Back to Dashboard",
            url_for("buyer_dashboard")
        )

    if request.method == "POST":
        food_name = request.form.get("food_name", "").strip()
        quantity = request.form.get("quantity", "").strip()
        unit = request.form.get("unit", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        food_image = request.files.get("food_image")

        if not food_name or not quantity or not unit or not location:
            return message_page(
                "Missing Information",
                "Please fill in all required food donation details.",
                "⚠️",
                "Try Again",
                url_for("donate_surplus_food")
            )

        try:
            quantity_value = float(quantity)
            if quantity_value <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return message_page(
                "Invalid Quantity",
                "Please enter a valid quantity greater than 0.",
                "⚠️",
                "Try Again",
                url_for("donate_surplus_food")
            )

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            saved_food_image = None

            if food_image and food_image.filename:
                original_name = secure_filename(food_image.filename)
                extension = original_name.rsplit(".", 1)[1].lower() if "." in original_name else ""
                allowed_extensions = {"jpg", "jpeg", "png", "webp"}

                if extension not in allowed_extensions:
                    return message_page(
                        "Invalid Image",
                        "Please upload only JPG, JPEG, PNG or WEBP images.",
                        "🖼️",
                        "Try Again",
                        url_for("donate_surplus_food")
                    )

                saved_food_image = (
                    f"donation_{session['user_id']}_{time.time_ns()}.{extension}"
                )

                upload_folder = os.path.join(
                    app.static_folder,
                    "uploads",
                    "donations"
                )
                os.makedirs(upload_folder, exist_ok=True)
                food_image.save(
                    os.path.join(upload_folder, saved_food_image)
                )

            cursor.execute("""
                INSERT INTO surplus_food
                (donor_id, food_name, quantity, unit, location, description, food_image, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session["user_id"],
                food_name,
                quantity_value,
                unit,
                location,
                description,
                saved_food_image,
                "Pending"
            ))

            cursor.execute("""
                SELECT id
                FROM users
                WHERE role = 'ngo'
            """)

            ngo_users = cursor.fetchall()

            for ngo_user in ngo_users:
                create_notification(
                    cursor,
                    ngo_user[0],
                    "New Food Donation Available",
                    f"A new surplus food donation ({food_name}, "
                    f"{quantity_value:g} {unit}) has been listed in {location}. "
                    f"Open Notifications to view it."
                )

            connection.commit()

        except Exception as e:
            if connection:
                connection.rollback()
            print("SURPLUS FOOD DONATION ERROR:", e)
            return message_page(
                "Donation Failed",
                "Something went wrong while submitting the food donation.",
                "❌",
                "Try Again",
                url_for("donate_surplus_food")
            )
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return message_page(
            "Food Donation Submitted",
            "Your surplus food has been successfully listed for NGOs.",
            "🍱",
            "View My Donations",
            url_for("my_food_donations")
        )

    return render_template("donate_surplus_food.html", buyer=buyer)

@app.route("/my-food-donations")
def my_food_donations():

    if "user_id" not in session:
        session["next_url"] = request.path
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Access Denied",
            "Only buyer accounts can view food donations.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    connection = None
    cursor = None
    donations = []

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sf.id,
                sf.food_name,
                sf.quantity,
                sf.unit,
                sf.location,
                sf.description,
                sf.food_image,
                sf.donation_date,
                sf.status,
                sf.ngo_id,
                CASE
                    WHEN sf.ngo_id IS NOT NULL THEN
                        CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, ''))
                    ELSE NULL
                END AS ngo_name
            FROM surplus_food sf
            LEFT JOIN users u ON sf.ngo_id = u.id
            WHERE sf.donor_id = %s
            ORDER BY sf.id DESC
        """, (session["user_id"],))

        donations = cursor.fetchall()

    except Exception as e:
        print("MY FOOD DONATIONS ERROR:", e)
        return message_page(
            "Unable to Load Donations",
            "We could not load your food donation history right now.",
            "❌",
            "Back to Dashboard",
            url_for("buyer_dashboard")
        )
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template(
        "my_food_donations.html",
        donations=donations
    )

@app.route("/bulk-buyer")
def bulk_buyer_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can access the bulk buyer dashboard.",
            "📦",
            "Go to Login",
            url_for("login")
        )

    return render_template("bulk_buyer_dashboard.html")

@app.route("/bulk-products")
def bulk_products():

    if "user_id" not in session:
        session["next_url"] = request.path
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can browse bulk products.",
            "📦",
            "Go to Login",
            url_for("login")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT products.*, users.first_name, users.last_name
        FROM products
        LEFT JOIN users ON products.farmer_id = users.id
        WHERE products.quantity > 0
        ORDER BY products.location, products.id DESC
    """)

    products = cursor.fetchall()

    nashik_products = [
        p for p in products
        if str(p.get("location", "")).strip().lower() == "nashik"
    ]

    pune_products = [
        p for p in products
        if str(p.get("location", "")).strip().lower() == "pune"
    ]

    thane_products = [
        p for p in products
        if str(p.get("location", "")).strip().lower() == "thane"
    ]

    cursor.close()
    connection.close()

    return render_template(
        "bulk_products.html",
        products=products,
        nashik_products=nashik_products,
        pune_products=pune_products,
        thane_products=thane_products
    )

@app.route("/bulk-add-to-cart/<int:product_id>")
def bulk_add_to_cart(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can use the bulk buying cart.",
            "📦",
            "Go to Login",
            url_for("login")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, quantity
        FROM products
        WHERE id = %s AND quantity > 0
    """, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    connection.close()

    if not product:
        return message_page(
            "Product Not Found",
            "The selected product is no longer available.",
            "🔍",
            "Back to Bulk Products",
            url_for("bulk_products")
        )

    bulk_cart = session.get("bulk_cart", [])
    if product_id not in bulk_cart:
        bulk_cart.append(product_id)
    session["bulk_cart"] = bulk_cart

    return redirect(url_for("bulk_cart"))

@app.route("/bulk-remove-from-cart/<int:product_id>")
def bulk_remove_from_cart(product_id):
    bulk_cart = session.get("bulk_cart", [])
    if product_id in bulk_cart:
        bulk_cart.remove(product_id)
    session["bulk_cart"] = bulk_cart
    return redirect(url_for("bulk_cart"))

@app.route("/bulk-cart", methods=["GET"])
def bulk_cart():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can access the bulk cart.",
            "📦",
            "Go to Login",
            url_for("login")
        )

    bulk_cart_ids = session.get("bulk_cart", [])
    products = []

    if bulk_cart_ids:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        placeholders = ",".join(["%s"] * len(bulk_cart_ids))
        cursor.execute(f"""
            SELECT id, product_name, price, quantity, unit, location
            FROM products
            WHERE id IN ({placeholders}) AND quantity > 0
            ORDER BY id DESC
        """, tuple(bulk_cart_ids))
        products = cursor.fetchall()
        cursor.close()
        connection.close()

    return render_template("bulk_cart.html", products=products)

@app.route("/bulk-checkout", methods=["POST"])
def bulk_checkout():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can place bulk orders.",
            "📦",
            "Go to Login",
            url_for("login")
        )

    buyer_name = request.form.get("buyer_name", session.get("user_name", "")).strip()
    business_name = request.form.get("business_name", "").strip()
    delivery_address = request.form.get("delivery_address", "").strip()
    city = request.form.get("city", "").strip()
    pincode = request.form.get("pincode", "").strip()
    bulk_cart_ids = session.get("bulk_cart", [])

    if (
        not buyer_name
        or not delivery_address
        or not city
        or not pincode.isdigit()
        or len(pincode) != 6
        or not bulk_cart_ids
    ):
        return message_page(
            "Invalid Bulk Order",
            "Please enter your name, delivery address, city, valid 6-digit pincode and select at least one product.",
            "⚠️",
            "Back to Bulk Cart",
            url_for("bulk_cart")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        placeholders = ",".join(["%s"] * len(bulk_cart_ids))
        cursor.execute(f"""
            SELECT id, product_name, price, quantity, unit
            FROM products
            WHERE id IN ({placeholders}) AND quantity > 0
        """, tuple(bulk_cart_ids))
        products = cursor.fetchall()

        if not products:
            return message_page(
                "Bulk Cart Empty",
                "The selected products are no longer available.",
                "🛒",
                "Back to Bulk Products",
                url_for("bulk_products")
            )

        for product in products:
            try:
                qty = int(request.form.get(f"qty_{product['id']}", "0"))
            except (TypeError, ValueError):
                qty = 0

            if qty <= 0 or qty > int(product["quantity"]):
                connection.rollback()
                return message_page(
                    "Invalid Quantity",
                    f"Please enter a valid quantity for {product['product_name']}.",
                    "⚠️",
                    "Back to Bulk Cart",
                    url_for("bulk_cart")
                )

            total_amount = float(product["price"]) * qty
            order_name = buyer_name + (" - " + business_name if business_name else "")

            cursor.execute("""
                INSERT INTO orders
                (product_id, buyer_name, quantity, total_amount, status, order_type, delivery_address, city, pincode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                product["id"], order_name, qty, total_amount, "Pending", "Bulk",
                delivery_address, city, pincode
            ))

        connection.commit()
        session["bulk_cart"] = []

    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

    return message_page(
        "Bulk Order Request Sent!",
        "Your bulk order request has been submitted successfully to the farmer for confirmation.",
        "📦",
        "Back to Buyer Options",
        url_for("buyer_dashboard")
    )

@app.route("/bulk-order", methods=["GET", "POST"], endpoint="bulk_order")
def bulk_order():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can use the bulk buying section.",
            "📦",
            "Go to Login",
            url_for("login")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        product_id = request.form.get("product_id")
        buyer_name = request.form.get("buyer_name", session.get("user_name", "")).strip()
        business_name = request.form.get("business_name", "").strip()
        delivery_address = request.form.get("delivery_address", "").strip()
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()

        try:
            quantity = int(request.form.get("quantity", "0"))
        except (TypeError, ValueError):
            quantity = 0

        if (
            not product_id
            or not buyer_name
            or not delivery_address
            or not city
            or not pincode.isdigit()
            or len(pincode) != 6
            or quantity <= 0
        ):
            cursor.close()
            connection.close()
            return message_page(
                "Invalid Bulk Request",
                "Please select a product, enter your name, complete delivery address, city, valid 6-digit pincode and quantity.",
                "⚠️",
                "Try Again",
                url_for("bulk_buyer")
            )

        cursor.execute("""
            SELECT id, product_name, price, quantity, unit
            FROM products
            WHERE id = %s
        """, (product_id,))
        product = cursor.fetchone()

        if not product:
            cursor.close()
            connection.close()
            return message_page(
                "Product Not Found",
                "The selected product is no longer available.",
                "🔍",
                "Back to Bulk Buying",
                url_for("bulk_buyer")
            )

        available = int(product["quantity"])
        if quantity > available:
            cursor.close()
            connection.close()
            return message_page(
                "Quantity Not Available",
                f"Only {available} {product['unit']} of this product is currently available.",
                "📦",
                "Try Again",
                url_for("bulk_buyer")
            )

        total_amount = float(product["price"]) * quantity
        order_name = buyer_name
        if business_name:
            order_name += " - " + business_name

        cursor.execute("""
            INSERT INTO orders
            (product_id, buyer_name, quantity, total_amount, status, order_type, delivery_address, city, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            product["id"],
            order_name,
            quantity,
            total_amount,
            "Pending",
            "Bulk",
            delivery_address,
            city,
            pincode
        ))

        connection.commit()
        cursor.close()
        connection.close()

        return message_page(
            "Bulk Order Request Sent!",
            f"Your bulk request for <strong>{product['product_name']}</strong> ({quantity} {product['unit']}) has been sent to the farmer for confirmation.",
            "📦",
            "Back to Buyer Options",
            url_for("buyer_dashboard")
        )

    cursor.execute("""
        SELECT id, product_name, price, quantity, unit, location
        FROM products
        WHERE quantity > 0
        ORDER BY product_name ASC
    """)
    products = cursor.fetchall()
    cursor.close()
    connection.close()

    selected_product_id = request.args.get("product_id", "")

    product_options = "".join(
        f'<option value="{p["id"]}" {"selected" if str(p["id"]) == str(selected_product_id) else ""}>{p["product_name"]} — ₹{p["price"]}/{p["unit"]} — {p["location"]}</option>'
        for p in products
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bulk Buyer | KisanKart</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{{box-sizing:border-box}}
            body{{margin:0;min-height:100vh;font-family:Arial,sans-serif;background:linear-gradient(135deg,#fff8e1,#e8f5e9);padding:30px 18px}}
            .box{{max-width:650px;margin:20px auto;background:#fff;border-radius:25px;padding:35px;box-shadow:0 20px 55px rgba(0,0,0,.10)}}
            .logo{{color:#1b5e20;font-size:27px;font-weight:800}}
            h1{{color:#183b20;margin:10px 0}}
            .sub{{color:#6f7c73;line-height:1.6}}
            label{{display:block;margin:17px 0 7px;font-weight:700;color:#314338}}
            input,select{{width:100%;padding:13px;border:1px solid #d6e0d8;border-radius:12px;font-size:15px}}
            button{{width:100%;margin-top:22px;padding:14px;border:0;border-radius:13px;background:#ef8f00;color:white;font-size:16px;font-weight:800;cursor:pointer}}
            .back{{display:block;text-align:center;margin-top:18px;color:#52705a;text-decoration:none;font-weight:600}}
        </style>
    </head>
    <body>
        <div class="box">
            <div class="logo">📦 KisanKart Bulk Buying</div>
            <h1>Place a Bulk Order Request</h1>
            <p class="sub">Select a product and the quantity required for your business or organization.</p>
            <form method="POST">
                <label>Your Name</label>
                <input type="text" name="buyer_name" value="{session.get("user_name", "")}" required>
                <label>Business / Organization Name (optional)</label>
                <input type="text" name="business_name" placeholder="Restaurant, Mess, Shop, etc.">
                <label>🏠 Delivery Address</label>
                <input type="text" name="delivery_address" placeholder="Enter your complete delivery address" required>

                <label>📍 City</label>
                <input type="text" name="city" placeholder="Enter city" required>

                <label>📮 Pincode</label>
                <input type="text" name="pincode" placeholder="Enter 6-digit pincode" maxlength="6" pattern="[0-9]{{6}}" inputmode="numeric" required>

                <label>Select Product</label>
                <select name="product_id" required>
                    <option value="">Select a product</option>
                    {product_options}
                </select>
                <label>Required Quantity</label>
                <input type="number" name="quantity" min="1" placeholder="Enter quantity" required>
                <button type="submit">📦 Send Bulk Order Request</button>
            </form>
            <a class="back" href="/bulk-buyer">← Back to Bulk Buyer Dashboard</a>
        </div>
    </body>
    </html>
    """

@app.route("/contact-farmer/<int:product_id>")
def contact_farmer(product_id):
    if "user_id" not in session:
        session["next_url"] = request.path
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Login Required",
            "Only buyer accounts can contact farmers from the buyer products section.",
            "👨‍🌾",
            "Go to Login",
            url_for("login")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT products.product_name, products.location,
               users.id AS farmer_id, users.first_name, users.last_name,
               users.phone, users.email
        FROM products
        LEFT JOIN users ON products.farmer_id = users.id
        WHERE products.id = %s
    """, (product_id,))
    farmer = cursor.fetchone()
    cursor.close()
    connection.close()

    if not farmer or not farmer.get("farmer_id"):
        return message_page(
            "Farmer Not Found",
            "We could not find the farmer for this product.",
            "🔍",
            "Back to Products",
            url_for("buyer_products")
        )

    farmer_name = f"{farmer.get('first_name', '')} {farmer.get('last_name', '')}".strip()
    phone = farmer.get("phone") or "Not available"
    email = farmer.get("email") or "Not available"
    location = farmer.get("location") or "Not available"

    phone_link = ""
    if farmer.get("phone"):
        safe_phone = str(farmer["phone"]).replace(" ", "")
        phone_link = f'<a class="contact-btn phone" href="tel:{safe_phone}">📞 Call Farmer</a>'

    email_link = ""
    if farmer.get("email"):
        email_link = f'<a class="contact-btn email" href="mailto:{farmer["email"]}">✉️ Email Farmer</a>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact Farmer | KisanKart</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin:0; min-height:100vh; font-family:Arial,Helvetica,sans-serif; background:#f5f8f4; display:flex; align-items:center; justify-content:center; padding:25px; }}
            .card {{ width:100%; max-width:560px; background:white; border-radius:24px; padding:35px; box-shadow:0 12px 35px rgba(0,0,0,.10); }}
            .logo {{ color:#2e7d32; font-size:26px; font-weight:800; margin-bottom:22px; }}
            h1 {{ color:#1b5e20; margin:0 0 8px; }}
            .sub {{ color:#6b776d; margin-bottom:24px; }}
            .info {{ background:#f7faf6; border-radius:15px; padding:18px; margin:10px 0; color:#344238; line-height:1.7; }}
            .label {{ font-weight:700; color:#2e7d32; }}
            .actions {{ display:grid; gap:10px; margin-top:22px; }}
            .contact-btn {{ display:block; text-align:center; text-decoration:none; padding:13px; border-radius:11px; font-weight:700; }}
            .phone {{ background:#2e7d32; color:white; }}
            .email {{ background:#e8f5e9; color:#2e7d32; border:1px solid #b9ddb9; }}
            .back {{ display:block; text-align:center; margin-top:18px; color:#55705b; text-decoration:none; font-weight:600; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">🌱 KisanKart</div>
            <h1>Contact Farmer</h1>
            <p class="sub">Connect directly with the farmer about this product.</p>
            <div class="info">
                <div><span class="label">👨‍🌾 Farmer:</span> {farmer_name or 'Farmer'}</div>
                <div><span class="label">🌾 Product:</span> {farmer.get('product_name', 'Product')}</div>
                <div><span class="label">📍 Location:</span> {location}</div>
                <div><span class="label">📞 Phone:</span> {phone}</div>
                <div><span class="label">✉️ Email:</span> {email}</div>
            </div>
            <div class="actions">{phone_link}{email_link}</div>
            <a class="back" href="{url_for('buyer_products')}">← Back to Products</a>
        </div>
    </body>
    </html>
    """

@app.route("/buyer-products")
def buyer_products():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            products.*,
            users.first_name,
            users.last_name
        FROM products
        LEFT JOIN users
            ON products.farmer_id = users.id
        WHERE LOWER(
            TRIM(products.location)
        ) = 'nashik'
        ORDER BY products.id DESC
        """
    )

    nashik_products = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            products.*,
            users.first_name,
            users.last_name
        FROM products
        LEFT JOIN users
            ON products.farmer_id = users.id
        WHERE LOWER(
            TRIM(products.location)
        ) = 'pune'
        ORDER BY products.id DESC
        """
    )

    pune_products = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            products.*,
            users.first_name,
            users.last_name
        FROM products
        LEFT JOIN users
            ON products.farmer_id = users.id
        WHERE LOWER(
            TRIM(products.location)
        ) = 'thane'
        ORDER BY products.id DESC
        """
    )

    thane_products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "buyer_products.html",

        nashik_products=nashik_products,

        pune_products=pune_products,

        thane_products=thane_products
    )

@app.route("/my-orders")
def my_orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Access Denied",
            "Only buyers can view order status.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    buyer_name = session.get("user_name", "").strip()

    cursor.execute("""
        SELECT
            orders.id,
            orders.buyer_name,
            orders.quantity,
            orders.total_amount,
            orders.status,
            orders.order_date,

            products.product_name,
            products.unit,
            products.location,

            users.first_name AS farmer_first_name,
            users.last_name AS farmer_last_name

        FROM orders

        JOIN products
            ON orders.product_id = products.id

        LEFT JOIN users
            ON products.farmer_id = users.id

        WHERE
            orders.buyer_name = %s
            OR orders.buyer_name LIKE CONCAT(%s, ' - %')

        ORDER BY orders.id DESC
    """, (
        buyer_name,
        buyer_name
    ))

    orders = cursor.fetchall()

    for order in orders:

        if " - " in str(order.get("buyer_name", "")):
            order["order_type"] = "Bulk"
        else:
            order["order_type"] = "Regular"

    cursor.close()
    connection.close()

    return render_template(
        "my_orders.html",
        orders=orders
    )

@app.route("/vegetables")
def vegetables():

    return render_template(
        "vegetables.html"
    )

@app.route("/vegetable")
def vegetable():

    return redirect(
        url_for("vegetables")
    )

@app.route("/fruits")
def fruits():

    return render_template(
        "fruits.html"
    )

@app.route("/grains")
def grains():

    return render_template(
        "grains.html"
    )

@app.route("/dairy")
def dairy():

    return render_template(
        "dairy.html"
    )

@app.route("/spices")
def spices():

    return render_template(
        "spices.html"
    )

@app.route("/farmer-orders")
def farmer_orders():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "farmer":

        return message_page(
            "Access Denied",

            "Only farmers can view farmer orders.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    farmer_id = session["user_id"]

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            orders.id,
            orders.buyer_name,
            orders.quantity,
            orders.total_amount,
            orders.status,
            orders.order_date,

            products.product_name,
            products.category,
            products.unit,
            products.price,
            products.location

        FROM orders

        JOIN products
            ON orders.product_id = products.id

        WHERE products.farmer_id = %s

        ORDER BY orders.id DESC
        """,
        (farmer_id,)
    )

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "farmer_orders.html",
        orders=orders
    )

@app.route(
    "/update-order/<int:order_id>/<status>"
)
def update_order(order_id, status):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "farmer":
        return message_page(
            "Access Denied",
            "Only farmers can update orders.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    allowed_statuses = [
        "Accepted",
        "Rejected",
        "Out for Delivery",
        "Completed",
        "Unable to Deliver"
    ]

    if status not in allowed_statuses:
        return message_page(
            "Invalid Order Status",
            "The order status you selected is not valid.",
            "⚠️",
            "Back to Orders",
            url_for("farmer_orders")
        )

    farmer_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT orders.id, orders.status
        FROM orders
        JOIN products
            ON orders.product_id = products.id
        WHERE orders.id = %s
        AND products.farmer_id = %s
        """,
        (order_id, farmer_id)
    )

    order = cursor.fetchone()

    if not order:
        cursor.close()
        connection.close()

        return message_page(
            "Order Not Found",
            "This order does not exist or does not belong to your products.",
            "🔍",
            "Back to Orders",
            url_for("farmer_orders")
        )

    current_status = order["status"] or "Pending"

    valid_transitions = {
        "Pending": ["Accepted", "Rejected"],
        "Accepted": ["Out for Delivery"],
        "Out for Delivery": ["Completed", "Unable to Deliver"],
        "Rejected": [],
        "Completed": [],
        "Unable to Deliver": []
    }

    if status not in valid_transitions.get(current_status, []):
        cursor.close()
        connection.close()

        return message_page(
            "Invalid Order Action",
            f"This order is currently <strong>{current_status}</strong>, so it cannot be changed to <strong>{status}</strong>.",
            "⚠️",
            "Back to Orders",
            url_for("farmer_orders")
        )

    cursor.execute(
        """
        UPDATE orders
        JOIN products
            ON orders.product_id = products.id
        SET orders.status = %s
        WHERE orders.id = %s
        AND products.farmer_id = %s
        """,
        (status, order_id, farmer_id)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("farmer_orders"))

@app.route(
    "/add-product",
    methods=["GET", "POST"]
)
def add_product():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "farmer":

        return message_page(
            "Farmer Account Required",

            "Only farmers can add products to KisanKart.",

            "🌾",

            "Go to Login",

            url_for("login")
        )

    farmer_id = session["user_id"]

    if request.method == "POST":

        product_name = request.form.get(
            "product_name"
        )

        category = request.form.get(
            "category"
        )

        price = request.form.get(
            "price"
        )

        quantity = request.form.get(
            "quantity"
        )

        unit = request.form.get(
            "unit"
        )

        description = request.form.get(
            "description"
        )

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT location
            FROM users
            WHERE id = %s
            """,
            (farmer_id,)
        )

        farmer = cursor.fetchone()

        location = (
            farmer["location"]
            if farmer
            else None
        )

        cursor.execute(
            """
            INSERT INTO products
            (
                farmer_id,
                product_name,
                category,
                price,
                quantity,
                unit,
                description,
                location
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                farmer_id,
                product_name,
                category,
                price,
                quantity,
                unit,
                description,
                location
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return message_page(
            "Product Added Successfully!",

            f"Your product <strong>{product_name}</strong> has been added successfully and is now saved in your KisanKart account.",

            "🌱",

            "View My Products",

            url_for("my_products")
        )

    return render_template(
        "add_product.html"
    )

@app.route("/my-products")
def my_products():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "farmer":

        return message_page(
            "Access Denied",

            "Only farmers can view their products.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    farmer_id = session["user_id"]

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE farmer_id = %s
        ORDER BY id DESC
        """,
        (farmer_id,)
    )

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "my_products.html",
        products=products
    )

@app.route(
    "/order/<int:product_id>",
    methods=["GET", "POST"]
)
@app.route(
    "/buy-now/<int:product_id>",
    methods=["GET", "POST"],
    endpoint="buy_now"
)
def order_product(product_id):

    if "user_id" not in session:

        session["next_url"] = request.path

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "buyer":

        return message_page(
            "Buyer Login Required",

            "Only buyer accounts can place orders.",

            "🛒",

            "Go to Login",

            url_for("login")
        )

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            products.*,
            users.first_name,
            users.last_name,
            users.location AS farmer_location

        FROM products

        LEFT JOIN users
            ON products.farmer_id = users.id

        WHERE products.id = %s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:

        cursor.close()
        connection.close()

        return message_page(
            "Product Not Found",

            "The product you are trying to order does not exist or has been removed.",

            "🔍",

            "Back to Products",

            url_for("buyer_products")
        )

    if request.method == "POST":

        buyer_name = request.form.get(
            "buyer_name"
        )

        try:

            quantity = int(
                request.form.get(
                    "quantity"
                )
            )

        except (
            TypeError,
            ValueError
        ):

            cursor.close()
            connection.close()

            return message_page(
                "Invalid Quantity",

                "Please enter a valid numeric quantity.",

                "⚠️",

                "Try Again",

                url_for(
                    "order_product",
                    product_id=product_id
                )
            )

        if quantity <= 0:

            cursor.close()
            connection.close()

            return message_page(
                "Invalid Quantity",

                "Quantity must be greater than zero.",

                "⚠️",

                "Try Again",

                url_for(
                    "order_product",
                    product_id=product_id
                )
            )

        total_amount = (
            float(product["price"])
            * quantity
        )

        cursor.execute(
            """
            INSERT INTO orders
            (
                product_id,
                buyer_name,
                quantity,
                total_amount,
                status,
                order_type
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                product_id,
                buyer_name,
                quantity,
                total_amount,
                "Pending",
                "Regular"
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return render_template(
            "order_success.html",

            product=product,

            buyer_name=buyer_name,

            quantity=quantity,

            total_amount=total_amount
        )

    cursor.close()
    connection.close()

    return render_template(
        "buy_now_checkout.html",
        product=product,
        default_buyer_name=session.get("user_name", ""),
        default_phone="",
        default_address="",
        payment_methods=["COD", "Online"]
    )

@app.route(
    "/edit-product/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "farmer":

        return message_page(
            "Access Denied",

            "Only farmers can edit products.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    farmer_id = session["user_id"]

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM products

        WHERE id = %s
        AND farmer_id = %s
        """,
        (
            product_id,
            farmer_id
        )
    )

    product = cursor.fetchone()

    if not product:

        cursor.close()
        connection.close()

        return message_page(
            "Product Not Found",

            "This product does not belong to your farmer account.",

            "🔍",

            "Back to My Products",

            url_for("my_products")
        )

    if request.method == "POST":

        product_name = request.form.get(
            "product_name"
        )

        category = request.form.get(
            "category"
        )

        price = request.form.get(
            "price"
        )

        quantity = request.form.get(
            "quantity"
        )

        unit = request.form.get(
            "unit"
        )

        description = request.form.get(
            "description"
        )

        cursor.execute(
            """
            SELECT location
            FROM users
            WHERE id = %s
            """,
            (farmer_id,)
        )

        farmer = cursor.fetchone()

        location = (
            farmer["location"]
            if farmer
            else product["location"]
        )

        cursor.execute(
            """
            UPDATE products

            SET
                product_name = %s,
                category = %s,
                price = %s,
                quantity = %s,
                unit = %s,
                description = %s,
                location = %s

            WHERE id = %s
            AND farmer_id = %s
            """,
            (
                product_name,
                category,
                price,
                quantity,
                unit,
                description,
                location,
                product_id,
                farmer_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(
            url_for("my_products")
        )

    cursor.close()
    connection.close()

    return render_template(
        "edit_product.html",
        product=product
    )

@app.route(
    "/delete-product/<int:product_id>",
    methods=["POST"]
)
def delete_product(product_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "farmer":

        return message_page(
            "Access Denied",

            "Only farmers can delete products.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    farmer_id = session["user_id"]

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM products

        WHERE id = %s
        AND farmer_id = %s
        """,
        (
            product_id,
            farmer_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        url_for("my_products")
    )

@app.route("/food-donation", methods=["GET", "POST"])
def food_donation():

    if "user_id" not in session:
        session["next_url"] = request.path
        return redirect(url_for("login"))

    if session.get("user_role") != "buyer":
        return message_page(
            "Buyer Account Required",
            "Only buyer accounts can submit food donations.",
            "🍱",
            "Go to Buyer Dashboard",
            url_for("buyer_dashboard")
        )

    if request.method == "POST":

        food_type = request.form.get(
            "food_type",
            ""
        ).strip()

        quantity = request.form.get(
            "quantity",
            ""
        ).strip()

        donation_date = request.form.get(
            "donation_date",
            ""
        ).strip()

        pickup_time = request.form.get(
            "pickup_time",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        contact = request.form.get(
            "contact",
            ""
        ).strip()

        food_condition = request.form.get(
            "food_condition",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        if (
            not food_type
            or not quantity
            or not donation_date
            or not pickup_time
            or not location
            or not contact
            or not food_condition
        ):
            return message_page(
                "Incomplete Donation Form",
                "Please fill in all required food donation details.",
                "⚠️",
                "Try Again",
                url_for("food_donation")
            )

        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO food_donations
                (
                    donor_id,
                    food_type,
                    quantity,
                    donation_date,
                    pickup_time,
                    location,
                    contact,
                    food_condition,
                    message,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session["user_id"],
                    food_type,
                    quantity,
                    donation_date,
                    pickup_time,
                    location,
                    contact,
                    food_condition,
                    message,
                    "Pending"
                )
            )

            connection.commit()

        except Exception as e:

            if connection:
                connection.rollback()

            print(
                "Food donation error:",
                e
            )

            return message_page(
                "Donation Failed",
                "Something went wrong while submitting your food donation. Please try again.",
                "❌",
                "Try Again",
                url_for("food_donation")
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

        return message_page(
            "Food Donation Submitted!",
            "Thank you for your donation. Your food donation has been submitted successfully and is now waiting for NGO confirmation.",
            "🍱",
            "Back to Buyer Dashboard",
            url_for("buyer_dashboard")
        )

    return render_template(
        "food_donation.html"
    )
def ensure_surplus_food_review_columns():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        for column_name, column_type in [
            ("review_rating", "INT NULL"),
            ("review_text", "TEXT NULL"),
            ("reviewed_at", "DATETIME NULL")
        ]:
            cursor.execute("""
                SELECT COUNT(*) AS column_exists
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'surplus_food'
                  AND COLUMN_NAME = %s
            """, (column_name,))

            if not cursor.fetchone()["column_exists"]:
                cursor.execute(
                    f"ALTER TABLE surplus_food ADD COLUMN {column_name} {column_type}"
                )

        connection.commit()
    except Exception as e:
        print("Surplus food review setup warning:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/ngo-dashboard")
def ngo_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "ngo":
        return message_page(
            "Access Denied",
            "This dashboard is only available for NGO accounts.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    ngo_id = session["user_id"]
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sf.id,
                sf.donor_id,
                sf.food_name,
                sf.quantity,
                sf.unit,
                sf.location,
                sf.description,
                sf.food_image,
                sf.donation_date,
                sf.status,
                sf.ngo_id,
                sf.food_image,
                CONCAT(
                    COALESCE(u.first_name, ''),
                    ' ',
                    COALESCE(u.last_name, '')
                ) AS donor_name
            FROM surplus_food sf
            LEFT JOIN users u ON sf.donor_id = u.id
            WHERE sf.status = 'Pending'
              AND sf.ngo_id IS NULL
            ORDER BY sf.id DESC
        """)
        donations = cursor.fetchall()

        cursor.execute("""
            SELECT
                sf.id,
                sf.food_name,
                sf.quantity,
                sf.unit,
                sf.location,
                sf.description,
                sf.food_image,
                sf.donation_date,
                sf.status,
                sf.ngo_id,
                sf.food_image,
                sf.review_rating,
                sf.review_text,
                sf.reviewed_at,
                CONCAT(
                    COALESCE(u.first_name, ''),
                    ' ',
                    COALESCE(u.last_name, '')
                ) AS donor_name
            FROM surplus_food sf
            LEFT JOIN users u ON sf.donor_id = u.id
            WHERE sf.ngo_id = %s
            ORDER BY sf.id DESC
        """, (ngo_id,))
        history = cursor.fetchall()

        pending_donations = sum(
            1 for d in donations if d.get("status") == "Pending"
        )
        accepted_donations = sum(
            1 for d in history if d.get("status") == "Accepted"
        )
        completed_donations = sum(
            1 for d in history if d.get("status") == "Completed"
        )
        total_donations = (
            pending_donations
            + accepted_donations
            + completed_donations
        )

        cursor.execute("""
            SELECT
                id,
                first_name,
                last_name,
                email,
                phone,
                role,
                location,
                created_at
            FROM users
            WHERE id = %s
        """, (ngo_id,))
        ngo = cursor.fetchone()

        if not ngo:
            return message_page(
                "NGO Profile Not Found",
                "We could not find your NGO account.",
                "🤝",
                "Back to Home",
                url_for("home")
            )

        return render_template(
            "ngo_dashboard.html",
            ngo=ngo,
            total_donations=total_donations,
            pending_donations=pending_donations,
            accepted_donations=accepted_donations,
            completed_donations=completed_donations,
            donations=donations,
            history=history,
            unread_notifications=get_unread_notification_count(ngo_id)
        )

    except Exception as e:
        print("NGO DASHBOARD ERROR:", e)
        return message_page(
            "Unable to Load NGO Dashboard",
            "Something went wrong while loading food donations. Please try again.",
            "❌",
            "Back to Home",
            url_for("home")
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/accept-donation/<int:donation_id>", methods=["POST"])
def accept_donation(donation_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "ngo":
        return message_page(
            "Access Denied",
            "Only NGO accounts can accept food donations.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    ngo_id = session["user_id"]
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                food_name,
                donor_id,
                status,
                ngo_id
            FROM surplus_food
            WHERE id = %s
              AND status = 'Pending'
              AND ngo_id IS NULL
        """, (donation_id,))

        donation = cursor.fetchone()

        if not donation:
            return message_page(
                "Donation No Longer Available",
                "This food donation has already been accepted or is no longer available.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        cursor.execute("""
            UPDATE surplus_food
            SET
                ngo_id = %s,
                status = 'Accepted'
            WHERE id = %s
              AND status = 'Pending'
              AND ngo_id IS NULL
        """, (ngo_id, donation_id))

        if cursor.rowcount == 1:
            create_notification(
                cursor,
                donation["donor_id"],
                "Food Donation Accepted",
                f"Your surplus food donation ({donation['food_name']}) "
                f"has been accepted by an NGO."
            )

        connection.commit()

        if cursor.rowcount != 1:
            connection.rollback()
            return message_page(
                "Donation Not Accepted",
                "The donation could not be accepted because it was already taken by another NGO.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        return message_page(
            "Donation Accepted!",
            f"{donation['food_name']} has been successfully accepted by your NGO.",
            "✅",
            "View NGO Dashboard",
            url_for("ngo_dashboard")
        )

    except Exception as e:
        if connection:
            connection.rollback()
        print("ACCEPT DONATION ERROR:", e)
        return message_page(
            "Unable to Accept Donation",
            "Something went wrong while accepting this food donation.",
            "❌",
            "Back to NGO Dashboard",
            url_for("ngo_dashboard")
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/reject-donation/<int:donation_id>", methods=["POST"])
def reject_donation(donation_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "ngo":
        return message_page(
            "Access Denied",
            "Only NGO accounts can reject food donations.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                food_name,
                donor_id,
                status,
                ngo_id
            FROM surplus_food
            WHERE id = %s
              AND status = 'Pending'
              AND ngo_id IS NULL
        """, (donation_id,))

        donation = cursor.fetchone()

        if not donation:
            return message_page(
                "Donation No Longer Available",
                "This food donation has already been accepted, rejected, or is no longer available.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        cursor.execute("""
            UPDATE surplus_food
            SET status = 'Cancelled'
            WHERE id = %s
              AND status = 'Pending'
              AND ngo_id IS NULL
        """, (donation_id,))

        if cursor.rowcount == 1:
            create_notification(
                cursor,
                donation["donor_id"],
                "Food Donation Rejected",
                f"Your surplus food donation ({donation['food_name']}) "
                f"was rejected by an NGO and is no longer available for acceptance."
            )

        updated = cursor.rowcount
        connection.commit()

        if updated != 1:
            connection.rollback()
            return message_page(
                "Donation Not Rejected",
                "The donation could not be rejected because it was already taken by another NGO.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        return message_page(
            "Donation Rejected",
            f"{donation['food_name']} has been rejected successfully.",
            "❌",
            "View NGO Dashboard",
            url_for("ngo_dashboard")
        )

    except Exception as e:
        if connection:
            connection.rollback()
        print("REJECT DONATION ERROR:", e)
        return message_page(
            "Unable to Reject Donation",
            "Something went wrong while rejecting this food donation.",
            "❌",
            "Back to NGO Dashboard",
            url_for("ngo_dashboard")
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/complete-donation/<int:donation_id>", methods=["POST"])
def complete_donation(donation_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "ngo":
        return message_page(
            "Access Denied",
            "Only NGO accounts can complete food donations.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    ngo_id = session["user_id"]
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, food_name, donor_id, status
            FROM surplus_food
            WHERE id = %s
              AND ngo_id = %s
              AND status = 'Accepted'
        """, (donation_id, ngo_id))

        donation = cursor.fetchone()

        if not donation:
            return message_page(
                "Donation Not Available",
                "Only an accepted donation assigned to your NGO can be marked as completed.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        cursor.execute("""
            UPDATE surplus_food
            SET status = 'Completed'
            WHERE id = %s
              AND ngo_id = %s
              AND status = 'Accepted'
        """, (donation_id, ngo_id))

        if cursor.rowcount == 1:
            create_notification(
                cursor,
                donation["donor_id"],
                "Food Donation Completed",
                f"Your surplus food donation ({donation['food_name']}) "
                f"has been marked as completed by the NGO."
            )

        connection.commit()

        if cursor.rowcount != 1:
            connection.rollback()
            return message_page(
                "Donation Not Completed",
                "The donation could not be marked as completed.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        return message_page(
            "Donation Completed!",
            f"{donation['food_name']} has been marked as successfully collected.",
            "📦",
            "View NGO Dashboard",
            url_for("ngo_dashboard")
        )

    except Exception as e:
        if connection:
            connection.rollback()
        print("COMPLETE DONATION ERROR:", e)
        return message_page(
            "Unable to Complete Donation",
            "Something went wrong while updating the donation status.",
            "❌",
            "Back to NGO Dashboard",
            url_for("ngo_dashboard")
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/review-donation/<int:donation_id>", methods=["POST"])
def review_donation(donation_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "ngo":
        return message_page(
            "Access Denied",
            "Only NGO accounts can review food donations.",
            "🔒",
            "Go to Login",
            url_for("login")
        )

    rating = request.form.get("rating")
    review_text = (request.form.get("review_text") or "").strip()
    ngo_id = session["user_id"]

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return message_page(
                "Invalid Rating",
                "Please select a rating between 1 and 5 stars.",
                "⭐",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, food_name, donor_id, status, ngo_id, review_rating
            FROM surplus_food
            WHERE id = %s
              AND ngo_id = %s
              AND status IN ('Accepted', 'Completed')
        """, (donation_id, ngo_id))
        donation = cursor.fetchone()

        if not donation:
            cursor.close()
            connection.close()
            return message_page(
                "Review Not Available",
                "Only food donations accepted by your NGO can be reviewed.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        if donation.get("review_rating"):
            cursor.close()
            connection.close()
            return message_page(
                "Review Already Submitted",
                "This food donation has already been reviewed.",
                "⭐",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        cursor.execute("""
            UPDATE surplus_food
            SET review_rating = %s,
                review_text = %s,
                reviewed_at = NOW()
            WHERE id = %s
              AND ngo_id = %s
              AND review_rating IS NULL
        """, (rating, review_text, donation_id, ngo_id))

        if cursor.rowcount != 1:
            connection.rollback()
            cursor.close()
            connection.close()
            return message_page(
                "Review Not Submitted",
                "The review could not be saved. Please try again.",
                "⚠️",
                "Back to NGO Dashboard",
                url_for("ngo_dashboard")
            )

        review_message = (
            f"An NGO rated your surplus food donation "
            f"({donation['food_name']}) {rating}/5 stars."
        )

        if review_text:
            review_message += f" Review: {review_text}"

        create_notification(
            cursor,
            donation["donor_id"],
            "New Food Donation Review",
            review_message
        )

        connection.commit()
        cursor.close()
        connection.close()

        return message_page(
            "Review Submitted!",
            f"Thank you for reviewing {donation['food_name']}.",
            "⭐",
            "View NGO Dashboard",
            url_for("ngo_dashboard")
        )

    except Exception as e:
        print("DONATION REVIEW ERROR:", e)
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except Exception:
            pass
        return message_page(
            "Unable to Submit Review",
            "Something went wrong while saving your review.",
            "❌",
            "Back to NGO Dashboard",
            url_for("ngo_dashboard")
        )

@app.route("/ngo-profile")
def ngo_profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "ngo":

        return message_page(
            "Access Denied",

            "Only NGO accounts can access the NGO profile.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            id,
            first_name,
            last_name,
            email,
            phone,
            role,
            location,
            created_at

        FROM users

        WHERE id = %s
        """,
        (session["user_id"],)
    )

    ngo = cursor.fetchone()

    cursor.close()
    connection.close()

    if not ngo:

        return message_page(
            "Profile Not Found",

            "We could not find your NGO profile.",

            "👤",

            "Back to NGO Dashboard",

            url_for("ngo_dashboard")
        )

    return render_template(
        "ngo_profile.html",
        ngo=ngo
    )

@app.route("/ngo-products")
def ngo_products():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "ngo":

        return message_page(
            "Access Denied",

            "Only NGO accounts can access available products.",

            "🔒",

            "Go to Login",

            url_for("login")
        )

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT
            products.*,
            users.first_name,
            users.last_name

        FROM products

        LEFT JOIN users
            ON products.farmer_id = users.id

        WHERE products.quantity > 0

        ORDER BY products.id DESC
        """
    )

    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "ngo_products.html",
        products=products
    )

@app.route("/ngo-logout")
def ngo_logout():

    session.clear()

    return redirect(
        url_for("home")
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )

def ensure_bulk_order_columns():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        for column_name, column_definition in [
            ("delivery_address", "TEXT NULL"),
            ("city", "VARCHAR(100) NULL"),
            ("pincode", "VARCHAR(10) NULL"),
        ]:
            cursor.execute("""
                SELECT COUNT(*) AS column_exists
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'orders'
                  AND COLUMN_NAME = %s
            """, (column_name,))

            if not cursor.fetchone()["column_exists"]:
                cursor.execute(
                    f"ALTER TABLE orders ADD COLUMN {column_name} {column_definition}"
                )

        connection.commit()

    except Exception as e:
        print("Bulk order address setup warning:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def ensure_order_type_column():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS column_exists
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'orders'
              AND COLUMN_NAME = 'order_type'
        """)
        exists = cursor.fetchone()["column_exists"]

        if not exists:
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN order_type VARCHAR(20) NOT NULL DEFAULT 'Regular'
            """)
            connection.commit()

        cursor.execute("""
            UPDATE orders
            SET order_type = 'Bulk'
            WHERE buyer_name LIKE '% - %'
              AND (order_type IS NULL OR order_type = 'Regular')
        """)
        connection.commit()

    except Exception as e:
        print("Order type setup warning:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def ensure_review_columns():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        for column_name, column_type in [
            ("review_rating", "INT NULL"),
            ("review_text", "TEXT NULL")
        ]:
            cursor.execute("""
                SELECT COUNT(*) AS column_exists
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'orders'
                  AND COLUMN_NAME = %s
            """, (column_name,))

            if not cursor.fetchone()["column_exists"]:
                cursor.execute(
                    f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}"
                )

        connection.commit()

    except Exception as e:
        print("Review setup warning:", e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/submit-review", methods=["POST"])
def submit_review():

    if "user_id" not in session:
        return redirect(url_for("login"))

    order_id = request.form.get("order_id")
    rating = request.form.get("rating")
    review_text = (request.form.get("review_text") or "").strip()

    try:
        order_id = int(order_id)
        rating = int(rating)

        if rating < 1 or rating > 5:
            return "Invalid rating", 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        buyer_name = (session.get("user_name") or "").strip()

        cursor.execute("""
            SELECT id, buyer_id, buyer_name, status
            FROM orders
            WHERE id = %s
              AND (
                    buyer_id = %s
                    OR buyer_name = %s
                    OR buyer_name LIKE CONCAT(%s, ' - %')
                  )
        """, (
            order_id,
            session["user_id"],
            buyer_name,
            buyer_name
        ))

        order = cursor.fetchone()

        if not order:
            cursor.close()
            connection.close()
            return "Order not found", 404

        if str(order["status"]).lower() != "completed":
            cursor.close()
            connection.close()
            return "Review is available only after order completion.", 400

        cursor.execute("""
            UPDATE orders
            SET review_rating = %s,
                review_text = %s
            WHERE id = %s
              AND (
                    buyer_id = %s
                    OR buyer_name = %s
                    OR buyer_name LIKE CONCAT(%s, ' - %')
                  )
              AND (review_rating IS NULL OR review_rating = 0)
        """, (
            rating,
            review_text,
            order_id,
            session["user_id"],
            buyer_name,
            buyer_name
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("my_orders"))

    except Exception as e:
        print("Review error:", e)
        return "Unable to submit review", 500

if __name__ == "__main__":

    ensure_surplus_food_review_columns()
    ensure_notification_table()
    ensure_review_columns()

    ensure_bulk_order_columns()
    ensure_order_type_column()

    app.run(
        debug=True
    )
