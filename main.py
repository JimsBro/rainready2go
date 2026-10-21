"""
RainReady2Go - PyScript logic
Renders the page content, mobile menu, order dialog and checkout.
Needs index.html + styles.css in the same folder.
"""
from html import escape

from pyodide.ffi import create_proxy # type: ignore
from pyodide.http import pyfetch # type: ignore
from pyscript import document, window # type: ignore
import json

# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------
GCASH_CHECKOUT_URL = ""

# ------------------------------------------------------------------
# DATA
# ------------------------------------------------------------------
PRODUCTS = [
    {"id": "pocket-umbrella", "name": "Pocket Umbrella",
     "description": "A compact, reusable umbrella that folds into any bag.",
     "price": 95, "badge": "Most picked"},
    {"id": "disposable-raincoat", "name": "Disposable Raincoat",    
     "description": "Keeps your clothes and upper body dry on the way home.",
     "price": 65},
    {"id": "backpack-rain-cover", "name": "Backpack Rain Cover",
     "description": "Guards books, notes, and gadgets inside your bag.",
     "price": 75},
    {"id": "waterproof-shoe-covers", "name": "Waterproof Shoe Covers",
     "description": "Keep your feet and shoes dry through puddles.",
     "price": 65},
    {"id": "rain-boots", "name": "Rain Boots",
     "description": "Full foot protection for wet days and flooded walkways.",
     "price": 120},
    {"id": "emergency-kit", "name": "RainReady Emergency Kit",
     "description": "Raincoat, backpack cover, pocket umbrella, and shoe covers in one bundle.",
     "price": 150, "badge": "Bundle", "featured": True},
]

PICKUP_SPOTS = {"gate": "School entrance / gate", "canteen": "Canteen"}

PAYMENT_OPTIONS = [
    {"value": "cash", "title": "Cash on pickup",
     "description": "Pay in cash when you collect your order."},
    {"value": "gcash", "title": "GCash",
     "description": "Pay online with GCash before you collect."},
]

HERO_PICKS = [
    {"id": "pocket-umbrella", "name": "Pocket Umbrella", "note": "Compact and reusable", "price": "₱95"},
    {"id": "disposable-raincoat", "name": "Disposable Raincoat", "note": "Covers clothes and upper body", "price": "₱65"},
    {"id": "emergency-kit", "name": "Emergency Kit", "note": "Four essentials in one bundle", "price": "₱150"},
]

PROBLEMS = [
    {"title": "Sudden showers", "icon": "clock",
     "description": "Rain can start while you're still on campus, with no umbrella in your bag."},
    {"title": "Soaked essentials", "icon": "smartphone",
     "description": "Wet clothes, shoes, and gadgets turn a small shower into a real loss."},
    {"title": "Online is too slow", "icon": "droplets",
     "description": "Ordering online doesn't help when the rain is already falling."},
]

VALUES = [
    {"title": "Affordable", "icon": "wallet",
     "description": "Prices that fit a student budget, without cutting corners."},
    {"title": "Convenient", "icon": "map-pin",
     "description": "Sold on campus, right when the rain starts."},
    {"title": "Dependable", "icon": "shield-check",
     "description": "Quality matters most to students, so every product is chosen with care."},
]

CAMPUS_SPOTS = [
    {"name": "School entrance / gate", "share": 43},
    {"name": "Canteen", "share": 37},
]

STEPS = [
    {"title": "Rain starts",
     "description": "Look up and notice the sky changing before you head out."},
    {"title": "Head to the entrance or canteen",
     "description": "The two spots students picked most in our survey."},
    {"title": "Grab what you need and go",
     "description": "Pick a single item or the full kit, and you're covered."},
]

STATS = [
    {"value": "93%", "label": "run into rain on their commute at least sometimes."},
    {"value": "40%", "label": "chose the pocket umbrella as the product they'd most want."},
    {"value": "70%", "label": "were interested or very interested in the Emergency Kit."},
    {"value": "53%", "label": "said product quality matters most when buying rain gear."},
]

ICONS = {
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "smartphone": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "droplets": '<path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/><path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "map-pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "shield-check": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
}


def icon(name, size=24):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</svg>')


def by_id(element_id):
    return document.getElementById(element_id)


def render_hero_picks():
    by_id("hero-picks").innerHTML = "".join(
        f'''<li>
              <div class="pick-left">
                <div class="pick-img">
                  <img src="{p["id"]}.jpg" alt="{escape(p["name"])}" style="width:100%; height:100%; object-fit:cover; border-radius:0.75rem;" onerror="this.style.display='none';" />
                </div>
                <div>
                  <p class="pick-name">{escape(p["name"])}</p>
                  <p class="pick-note">{escape(p["note"])}</p>
                </div>
              </div>
              <span class="pick-price">{p["price"]}</span>
            </li>'''
        for p in HERO_PICKS
    )


def render_cards(container_id, items, icon_class=""):
    by_id(container_id).innerHTML = "".join(
        f'''<div class="card">
              <span class="card-icon {icon_class}">{icon(item["icon"])}</span>
              <h3>{escape(item["title"])}</h3>
              <p>{escape(item["description"])}</p>
            </div>'''
        for item in items
    )


def render_products():
    cards = []
    for p in PRODUCTS:
        featured = " featured" if p.get("featured") else ""
        badge = f'<span class="badge">{escape(p["badge"])}</span>' if p.get("badge") else ""
        cards.append(f'''
            <article class="product{featured}">
              {badge}
              <div class="product-img">
                <img src="{p["id"]}.jpg" alt="{escape(p["name"])}" style="width:100%; height:100%; object-fit:cover; border-radius:1rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                <span style="display:none; width:100%; height:100%; align-items:center; justify-content:center; font-size:0.875rem;">Product image</span>
              </div>
              <h3>{escape(p["name"])}</h3>
              <p class="product-desc">{escape(p["description"])}</p>
              <div class="product-bottom">
                <p class="product-price">₱{p["price"]}</p>
                <button type="button" class="buy-btn" data-product="{p["id"]}">Buy now</button>
              </div>
            </article>''')
    by_id("products-grid").innerHTML = "".join(cards)


def render_campus():
    by_id("campus-spots").innerHTML = "".join(
        f'''<div>
              <div class="spot-top">
                <span class="spot-name">{icon("map-pin", 16)}{escape(s["name"])}</span>
                <span>{s["share"]}%</span>
              </div>
              <div class="bar"><div class="bar-fill" style="width:{s["share"]}%"></div></div>
            </div>'''
        for s in CAMPUS_SPOTS
    )
    by_id("steps-list").innerHTML = "".join(
        f'''<li class="step">
              <span class="step-num">{i}</span>
              <div>
                <h3>{escape(s["title"])}</h3>
                <p>{escape(s["description"])}</p>
              </div>
            </li>'''
        for i, s in enumerate(STEPS, start=1)
    )


def render_stats():
    by_id("stats-grid").innerHTML = "".join(
        f'''<div class="stat">
              <p class="stat-value">{s["value"]}</p>
              <p class="stat-label">{escape(s["label"])}</p>
            </div>'''
        for s in STATS
    )


def set_menu(open_):
    by_id("nav-mobile").hidden = not open_
    by_id("icon-menu").hidden = open_
    by_id("icon-close").hidden = not open_
    toggle = by_id("menu-toggle")
    toggle.setAttribute("aria-expanded", "true" if open_ else "false")
    toggle.setAttribute("aria-label", "Close menu" if open_ else "Open menu")


def on_menu_toggle(event):
    set_menu(by_id("nav-mobile").hidden)


def on_mobile_nav_click(event):
    if event.target.closest("a"):
        set_menu(False)


def show_payment_banner():
    status = window.URLSearchParams.new(window.location.search).get("payment")
    messages = {
        "success": "Thanks for your order! We're confirming your GCash payment.",
        "cancelled": "Payment was cancelled, so no order was placed.",
    }
    message = messages.get(status)
    if not message:
        return

    root = by_id("banner-root")
    root.innerHTML = f'''
        <div class="banner" role="status">
          <div class="banner-inner">
            <p>{escape(message)}</p>
            <button type="button" id="banner-dismiss">Dismiss</button>
          </div>
        </div>'''

    def dismiss(event):
        root.innerHTML = ""
        window.history.replaceState(None, "", window.location.pathname)

    by_id("banner-dismiss").addEventListener("click", create_proxy(dismiss))


order = {}


def find_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def close_dialog(event=None):
    by_id("order-dialog").close()


def refresh_order_summary():
    total = order["product"]["price"] * order["quantity"]
    by_id("order-total").innerText = f"₱{total}"
    button = by_id("order-submit")
    if order["method"] == "gcash":
        button.innerText = f"Pay ₱{total} with GCash"
    else:
        button.innerText = "Place order"


def show_order_form(product):
    order.update({"product": product, "quantity": 1, "method": "cash", "pickup": "gate"})

    pickup_html = "".join(
        f'''<label class="option pickup">
              <input type="radio" name="pickup" value="{value}" {"checked" if value == "gate" else ""}>
              {escape(label)}
            </label>'''
        for value, label in PICKUP_SPOTS.items()
    )
    payment_html = "".join(
        f'''<label class="option">
              <input type="radio" name="payment" value="{o["value"]}" {"checked" if o["value"] == "cash" else ""}>
              <span>
                <span class="option-title">{escape(o["title"])}</span>
                <span class="option-desc">{escape(o["description"])}</span>
              </span>
            </label>'''
        for o in PAYMENT_OPTIONS
    )

    by_id("order-content").innerHTML = f'''
        <button type="button" class="dialog-close" id="dialog-close" aria-label="Close">&times;</button>
        <form id="order-form" class="dialog-body">
          <h2>Order {escape(product["name"])}</h2>
          <p class="dialog-sub">₱{product["price"]} each. Pick it up on campus.</p>

          <div class="form">
            <div class="field">
              <label for="qty">Quantity</label>
              <input class="input" id="qty" type="number" min="1" max="10" value="1">
            </div>
            <div class="field">
              <label for="cust-name">Full name</label>
              <input class="input" id="cust-name" type="text" required maxlength="100" autocomplete="name">
            </div>
            <div class="field">
              <label for="cust-phone">Phone number</label>
              <input class="input" id="cust-phone" type="tel" required minlength="7" maxlength="20" autocomplete="tel">
            </div>
            <fieldset class="field">
              <legend>Pickup spot</legend>
              <div class="options">{pickup_html}</div>
            </fieldset>
            <fieldset class="field">
              <legend>Payment</legend>
              <div class="options">{payment_html}</div>
            </fieldset>
          </div>

          <p id="order-error" class="form-error" role="alert" hidden></p>

          <div class="form-footer">
            <div>
              <p class="total-label">Total</p>
              <p class="total-value" id="order-total">₱{product["price"]}</p>
            </div>
            <button type="submit" class="submit-btn" id="order-submit">Place order</button>
          </div>
        </form>'''

    by_id("dialog-close").addEventListener("click", create_proxy(close_dialog))
    by_id("order-form").addEventListener("submit", create_proxy(on_order_submit))
    by_id("qty").addEventListener("input", create_proxy(on_quantity_change))
    for radio in document.querySelectorAll('input[name="payment"]'):
        radio.addEventListener("change", create_proxy(on_payment_change))
    for radio in document.querySelectorAll('input[name="pickup"]'):
        radio.addEventListener("change", create_proxy(on_pickup_change))

    refresh_order_summary()


def on_quantity_change(event):
    try:
        qty = int(float(event.target.value))
    except ValueError:
        qty = 1
    order["quantity"] = min(10, max(1, qty))
    refresh_order_summary()


def on_payment_change(event):
    order["method"] = event.target.value
    refresh_order_summary()


def on_pickup_change(event):
    order["pickup"] = event.target.value


def show_error(message):
    box = by_id("order-error")
    box.innerText = message
    box.hidden = False


def show_order_placed():
    product = order["product"]
    total = product["price"] * order["quantity"]
    by_id("order-content").innerHTML = f'''
        <div class="dialog-done">
          <h2>Order placed!</h2>
          <p class="dialog-sub">
            Pay ₱{total} in cash at {escape(PICKUP_SPOTS[order["pickup"]])}
            when you pick up your {escape(product["name"])}.
          </p>
          <button type="button" class="btn btn-ink" id="done-btn">Done</button>
        </div>'''
    by_id("done-btn").addEventListener("click", create_proxy(close_dialog))


async def start_gcash_checkout():
    button = by_id("order-submit")
    if not GCASH_CHECKOUT_URL:
        show_error("GCash payments are not set up yet.")
        return

    button.disabled = True
    button.innerText = "Redirecting to GCash..."
    body = {
        "productId": order["product"]["id"],
        "quantity": order["quantity"],
        "customerName": by_id("cust-name").value,
        "phone": by_id("cust-phone").value,
        "pickup": order["pickup"],
    }
    try:
        response = await pyfetch(
            GCASH_CHECKOUT_URL,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(body),
        )
        data = await response.json()
        if not response.ok or "checkoutUrl" not in data:
            show_error(data.get("error", "Could not start GCash payment."))
            button.disabled = False
            refresh_order_summary()
            return
        window.location.href = data["checkoutUrl"]
    except Exception:
        show_error("Could not reach the payment provider. Please try again.")
        button.disabled = False
        refresh_order_summary()


async def on_order_submit(event):
    event.preventDefault()
    by_id("order-error").hidden = True

    if order["method"] == "cash":
        show_order_placed()
    else:
        await start_gcash_checkout()


def on_products_click(event):
    button = event.target.closest("[data-product]")
    if not button:
        return
    product = find_product(button.getAttribute("data-product"))
    if product:
        show_order_form(product)
        by_id("order-dialog").showModal()


def on_dialog_click(event):
    if event.target == by_id("order-dialog"):
        close_dialog()


def main():
    show_payment_banner()
    render_hero_picks()
    render_cards("problems-grid", PROBLEMS)
    render_products()
    render_campus()
    render_cards("values-grid", VALUES, icon_class="sun")
    render_stats()

    by_id("year").innerText = str(window.Date.new().getFullYear())

    by_id("menu-toggle").addEventListener("click", create_proxy(on_menu_toggle))
    by_id("nav-mobile").addEventListener("click", create_proxy(on_mobile_nav_click))
    by_id("products-grid").addEventListener("click", create_proxy(on_products_click))
    by_id("order-dialog").addEventListener("click", create_proxy(on_dialog_click))


main()