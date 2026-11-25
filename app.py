"""Forno Rosso: pizza ordering with NO database (Flask; deploys to Vercel).

An order is priced on the server from menu.py, sent to the kitchen as a message (Telegram and/or Discord),
and the customer gets a signed receipt link. Nothing is stored, so there is nothing to host or back up.
"""
import json, os, re, secrets, time, urllib.request
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from flask import Flask, abort, jsonify, render_template, request
from itsdangerous import BadSignature, URLSafeSerializer
from werkzeug.middleware.proxy_fix import ProxyFix

from menu import SEED

DELIVERY_FEE = int(os.environ.get("DELIVERY_FEE", "60"))
SHOP_TZ_HOURS = float(os.environ.get("SHOP_TZ_HOURS", "8"))  # Philippines = UTC+8
SHOP_PHONE = re.sub(r"[^0-9+]", "", os.environ.get("SHOP_PHONE", ""))
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
SOLD_OUT = {x.strip() for x in os.environ.get("SOLD_OUT", "").split(",") if x.strip()}
SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-only-change-me"
TICKET_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # no 0/O/1/I, easy to read out loud

# static files live in public/ (Vercel serves that folder from its CDN; Flask serves it when run locally)
app = Flask(__name__, static_folder="public", static_url_path="")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
signer = URLSafeSerializer(SECRET_KEY, salt="receipt")

MENU = {(t, i): {"type": t, "id": i, "name": n, "price": p, "meta": m, "sort": k}
        for k, (t, i, n, p, m) in enumerate(SEED)}


def sold_out(row):
    return row["id"] in SOLD_OUT or "%s:%s" % (row["type"], row["id"]) in SOLD_OUT


def raw(kind, id_):
    """Menu row whether or not it is sold out (used for a pizza's default options)."""
    return MENU.get((kind, str(id_)))


def pick(kind, id_):
    row = raw(kind, id_)
    return row if row and not sold_out(row) else None


# best-effort only: each serverless instance keeps its own counters
_hits = {}


def limited(key, n, window):
    now = time.time()
    q = [t for t in _hits.get(key, []) if now - t < window]
    if len(q) >= n:
        _hits[key] = q
        return True
    _hits[key] = q + [now]
    return False


def err(msg, code=400):
    return jsonify(error=msg), code


# ---------- pages ----------

@app.get("/")
def builder():
    return render_template("builder.html")


@app.get("/healthz")
def healthz():
    return "ok"


@app.get("/api/menu")
def api_menu():
    out = {"delivery_fee": DELIVERY_FEE, "size_ref": MENU[("size", "m")]["price"]}
    for r in sorted(MENU.values(), key=lambda r: r["sort"]):
        if not sold_out(r):
            out.setdefault(r["type"], []).append({"id": r["id"], "n": r["name"], "p": r["price"], **r["meta"]})
    return jsonify(out)


# ---------- ordering ----------

def price_cart(cart):
    """Return (lines, error). lines = [kind, name, qty, unit price, [detail...]]. Every price comes from menu.py."""
    if not isinstance(cart, list) or not 1 <= len(cart) <= 15:
        return None, "Your order is empty, or has too many different items (15 at most)."
    lines = []
    for l in cart:
        q = l.get("qty") if isinstance(l, dict) else None
        if not isinstance(q, int) or isinstance(q, bool) or not 1 <= q <= 20:
            return None, "Quantities must be between 1 and 20."
        if l.get("kind") == "pizza":
            preset = None
            if l.get("preset") not in (None, ""):
                preset = pick("pizza", l.get("preset"))
                if not preset:
                    return None, "That pizza is no longer available. Please reload and try again."
            pm = preset["meta"] if preset else {}
            incl = pm.get("top", {})
            gone = "Some pizza choices are no longer available. Please reload and try again."
            size = pick("size", l.get("size"))
            if not size:
                return None, gone
            ref = raw("size", "m")
            # a named pizza is priced for Medium; other sizes add or subtract the difference
            parts = [(size["name"], size["price"] - (ref["price"] if ref else 0) if preset else size["price"])]
            for kind in ("crust", "sauce", "cheese"):
                row = pick(kind, l.get(kind))
                if not row:
                    return None, gone
                dflt = raw(kind, pm.get(kind)) if preset else None
                # options the pizza already comes with are free; swaps only cost the difference upward
                parts.append((row["name"], max(0, row["price"] - (dflt["price"] if dflt else 0)) if preset else row["price"]))
            tops = l.get("toppings") or {}
            if not isinstance(tops, dict) or len(tops) > 20:
                return None, "Invalid toppings."
            picked = []
            for tid, side in tops.items():
                row = pick("topping", tid)
                if not row or side not in ("all", "left", "right"):
                    return None, "A topping you picked is no longer available."
                free = bool(preset) and row["id"] in incl
                picked.append((row["sort"], row["name"] + ("" if side == "all" else " (%s half)" % side), 0 if free else row["price"]))
            parts += [(n, p) for _, n, p in sorted(picked)]  # menu order, so kitchen tickets are consistent
            for t in sorted((t for t in incl if t not in tops), key=lambda t: (raw("topping", t) or {"sort": 0})["sort"]):
                if raw("topping", t):
                    parts.append(("No " + raw("topping", t)["name"], 0))  # removed from the recipe: shown on the ticket
            lines.append(["pizza", preset["name"] if preset else "Custom pizza", q,
                          (preset["price"] if preset else 0) + sum(p for _, p in parts), [n for n, _ in parts]])
        elif l.get("kind") == "item":
            row = pick("product", l.get("id"))
            if not row:
                return None, "An item in your order is no longer available. Please reload and try again."
            lines.append(["item", row["name"], q, row["price"], []])
        else:
            return None, "Invalid order."
    if sum(l[2] for l in lines) > 60:
        return None, "That is a big order! Please call the shop for more than 60 items."
    return lines, None


def peso(n):
    return "₱{:,}".format(n)


def order_text(o, for_shop=True):
    """Plain-text ticket: what the kitchen receives, and what the customer can text or copy."""
    head = ("NEW ORDER %s (%s)" if for_shop else "Order %s (%s)") % (o["ticket"], o["mode"])
    out = [head, "%s · %s" % (o["name"], o["phone"])]
    if o["address"]:
        out.append("Deliver to: " + o["address"])
    out.append("-" * 24)
    for kind, name, qty, unit, detail in o["lines"]:
        out.append("%d× %s  %s" % (qty, name, peso(qty * unit)))
        if detail:
            out.append("   " + " · ".join(detail))
    out.append("-" * 24)
    if o["fee"]:
        out.append("Delivery %s" % peso(o["fee"]))
    out.append("TOTAL %s (pay on %s)" % (peso(o["total"]), "delivery" if o["mode"] == "delivery" else "pickup"))
    out.append(o["at"])
    return "\n".join(out)


def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return 200 <= r.status < 300
    except Exception:
        app.logger.exception("Could not notify the shop")
        return False


def notify_shop(text):
    """True = reached the shop, False = every configured channel failed, None = no channel configured."""
    results = []
    if TG_TOKEN and TG_CHAT:
        results.append(post_json("https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN, {"chat_id": TG_CHAT, "text": text}))
    if DISCORD_URL:
        results.append(post_json(DISCORD_URL, {"content": text[:1900]}))
    return None if not results else any(results)


@app.post("/api/orders")
def create_order():
    if limited("order:" + (request.remote_addr or "?"), 6, 600):
        return err("Too many orders from this device. Please try again in a few minutes.", 429)
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return err("Invalid request.")
    lines, problem = price_cart(d.get("cart"))
    if problem:
        return err(problem)

    name, phone = str(d.get("name", "")).strip(), str(d.get("phone", "")).strip()
    mode, address = d.get("mode"), str(d.get("address", "")).strip()[:200]
    if not 1 <= len(name) <= 60:
        return err("Please enter your name.")
    if not re.fullmatch(r"[0-9+\-\s()]{7,20}", phone):
        return err("Please enter a valid mobile number.")
    if mode not in ("pickup", "delivery"):
        return err("Choose pickup or delivery.")
    if mode == "delivery" and len(address) < 8:
        return err("Please enter your delivery address.")

    subtotal = sum(l[2] * l[3] for l in lines)
    fee = DELIVERY_FEE if mode == "delivery" else 0
    now = datetime.now(timezone(timedelta(hours=SHOP_TZ_HOURS)))
    order = {"ticket": "F" + "".join(secrets.choice(TICKET_CHARS) for _ in range(5)),
             "at": now.strftime("%b %d, %I:%M %p"), "name": name, "phone": phone, "mode": mode,
             "address": address if mode == "delivery" else "", "lines": lines,
             "subtotal": subtotal, "fee": fee, "total": subtotal + fee}
    sent = notify_shop(order_text(order))
    if sent is False:  # the shop never got it, so don't pretend it did
        return err("We couldn't send your order to the shop. Please try again, or call the shop.", 502)
    order["sent"] = bool(sent)
    return jsonify(ticket=order["ticket"], total=order["total"], sent=order["sent"],
                   receipt_url="/r/" + signer.dumps(order)), 201


@app.get("/r/<token>")
def receipt(token):
    try:
        o = signer.loads(token)
    except BadSignature:
        abort(404)
    text = order_text(o, for_shop=False)
    sms = "sms:%s?&body=%s" % (SHOP_PHONE, quote(text + "\n" + request.url_root.rstrip("/") + request.path, safe="")) if SHOP_PHONE else ""
    return render_template("receipt.html", o=o, text=text, sms=sms, shop_phone=SHOP_PHONE)


@app.errorhandler(404)
def not_found(_):
    return render_template("receipt.html", o=None, text="", sms="", shop_phone=""), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=bool(os.environ.get("FLASK_DEBUG")))
