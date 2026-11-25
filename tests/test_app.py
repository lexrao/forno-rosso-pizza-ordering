import importlib, os, sys, re
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
ENV = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "DISCORD_WEBHOOK_URL", "SOLD_OUT", "SHOP_PHONE", "DELIVERY_FEE")


@pytest.fixture()
def load(monkeypatch):
    def _load(**env):
        for k in ENV:
            monkeypatch.delenv(k, raising=False)
        monkeypatch.setenv("SECRET_KEY", "test-secret")
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        import app as m
        importlib.reload(m)
        return m
    return _load


@pytest.fixture()
def app_mod(load):
    return load()


PIZZA = {"kind": "pizza", "qty": 1, "size": "m", "crust": "stuffed", "sauce": "pesto", "cheese": "extra",
         "toppings": {"pep": "all", "mush": "left"}}  # 179+70+30+50+60+45 = 434
CUST = {"name": "Lex", "phone": "0917 123 4567", "mode": "pickup"}
order = lambda cart, **kw: {"cart": cart, **CUST, **kw}
LIST = {
    "Classic Pizzas": {"Hawaiian": 199, "Pepperoni": 229, "Cheese Lovers": 219, "Ham & Cheese": 199, "Bacon Pizza": 239, "All Meat": 269},
    "Special Pizzas": {"Supreme": 279, "Overload Pizza": 299, "Meat Lovers": 289, "Garden Veggie": 229, "Seafood Delight": 299, "Deluxe Special": 319},
    "Cheese Specials": {"Four Cheese": 279, "Mozzarella Overload": 269, "Creamy Cheese": 249, "Garlic Cheese": 229, "Cheesy Bacon": 269},
}
named = lambda pid, **kw: {"kind": "pizza", "qty": 1, "preset": pid, "size": "m", "crust": "classic", **kw}


def test_no_database_anywhere(app_mod):
    root = os.path.join(os.path.dirname(__file__), "..")
    assert "sqlite" not in open(os.path.join(root, "app.py")).read().lower()
    app_mod.app.test_client().post("/api/orders", json=order([PIZZA]))
    assert not [f for f in os.listdir(root) if f.endswith((".db", ".sqlite", ".sqlite3"))]


def test_menu_pages_and_static_files(app_mod):
    c = app_mod.app.test_client()
    m = c.get("/api/menu").get_json()
    assert [s["id"] for s in m["size"]] == ["s", "m", "l"] and len(m["topping"]) == 18 and m["size_ref"] == 179
    got = {}
    for p in m["pizza"]:
        got.setdefault(p["cat"], {})[p["n"]] = p["p"]
    assert got == LIST
    assert [p["cat"] for p in m["product"]][0] == "Chicken"
    assert c.get("/").status_code == 200
    for f in ("style.css", "builder.js", "receipt.js", "favicon.svg", "favicon.ico", "apple-touch-icon.png"):
        assert c.get("/" + f).status_code == 200, f   # served from public/ at the site root


def test_mixed_cart_priced_by_server(app_mod):
    c = app_mod.app.test_client()
    cart = [{**PIZZA, "qty": 2}, {"kind": "item", "id": "fries-r", "qty": 2}, {"kind": "item", "id": "coke", "qty": 1}]
    r = c.post("/api/orders", json=order(cart, total=1, price=1))
    assert r.status_code == 201 and r.get_json()["total"] == 434 * 2 + 79 * 2 + 65


def test_every_named_pizza_orders_at_its_listed_price(app_mod):
    c = app_mod.app.test_client()
    for p in c.get("/api/menu").get_json()["pizza"]:
        app_mod._hits.clear()
        r = c.post("/api/orders", json=order([named(p["id"], sauce=p["sauce"], cheese=p["cheese"], toppings=p["top"])]))
        assert r.status_code == 201 and r.get_json()["total"] == p["p"], p["n"]


def test_named_pizza_customising_and_delivery(app_mod):
    c = app_mod.app.test_client()
    def tot(cart, **kw):
        app_mod._hits.clear()
        return c.post("/api/orders", json=order(cart, **kw)).get_json()["total"]
    base = dict(sauce="tomato", cheese="reg", toppings={"ham": "all", "pine": "all"})  # Hawaiian as defined
    assert tot([named("hawaiian", **base)]) == 199
    assert tot([named("hawaiian", **{**base, "size": "l"})]) == 299 and tot([named("hawaiian", **{**base, "size": "s"})]) == 149
    assert tot([named("hawaiian", **{**base, "crust": "stuffed"})]) == 269
    assert tot([named("hawaiian", **{**base, "toppings": {**base["toppings"], "mush": "right"}})]) == 244
    assert tot([named("hawaiian", **{**base, "toppings": {"ham": "all"}})]) == 199  # topping removed: no refund
    assert tot([named("creamy", sauce="pesto", cheese="reg", toppings={"cream": "all"})]) == 249
    assert tot([{"kind": "item", "id": "water", "qty": 3}], mode="delivery", address="12 Pardo Rd, Cebu City") == 35 * 3 + 60


def test_validation(app_mod):
    c = app_mod.app.test_client()
    ok = dict(sauce="tomato", cheese="reg", toppings={})
    bad = [order([]), order("x"), {**CUST}, order(["x"]),
           order([{"kind": "item", "id": "coke", "qty": 0}]), order([{"kind": "item", "id": "coke", "qty": 21}]),
           order([{"kind": "item", "id": "coke", "qty": True}]), order([{"kind": "item", "id": "nope", "qty": 1}]),
           order([{"kind": "item", "id": "pep", "qty": 1}]), order([{**PIZZA, "toppings": {"nope": "all"}}]),
           order([{**PIZZA, "toppings": {"pep": "middle"}}]), order([{**PIZZA, "size": "xl"}]),
           order([named("nope", **ok)]), order([named("pep", **ok)]), order([{"kind": "burger", "qty": 1}]),
           order([PIZZA], phone="abc"), order([PIZZA], mode="drone"), order([PIZZA], mode="delivery"),  # no address
           order([PIZZA], name=""), order([{"kind": "item", "id": "coke", "qty": 20}] * 4),  # 80 items
           order([{"kind": "item", "id": "coke", "qty": 1}] * 16)]  # more than 15 lines
    for b in bad:
        app_mod._hits.clear()
        assert c.post("/api/orders", json=b).status_code == 400, b
    assert c.post("/api/orders", data="not json").status_code == 400
    app_mod._hits.clear()
    for _ in range(6):
        c.post("/api/orders", json=order([PIZZA]))
    assert c.post("/api/orders", json=order([PIZZA])).status_code == 429


def test_sold_out_via_env(load):
    m = load(SOLD_OUT="coke,pizza:bacon,topping:shrimp")
    c = m.app.test_client()
    menu = c.get("/api/menu").get_json()
    assert "coke" not in [p["id"] for p in menu["product"]]
    assert "bacon" not in [p["id"] for p in menu["pizza"]] and "bacon" in [t["id"] for t in menu["topping"]]  # only the pizza
    assert "shrimp" not in [t["id"] for t in menu["topping"]]
    ok = dict(sauce="tomato", cheese="reg", toppings={})
    for bad in (order([{"kind": "item", "id": "coke", "qty": 1}]), order([named("bacon", **ok)]),
                order([{**PIZZA, "toppings": {"shrimp": "all"}}])):
        m._hits.clear()
        assert c.post("/api/orders", json=bad).status_code == 400


def test_order_reaches_shop_and_receipt_works(load, monkeypatch):
    m = load(TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="-100", DISCORD_WEBHOOK_URL="https://discord.example/hook", SHOP_PHONE="+63 917 000 1111")
    calls = []
    monkeypatch.setattr(m, "post_json", lambda url, payload: calls.append((url, payload)) or True)
    c = m.app.test_client()
    r = c.post("/api/orders", json=order([named("hawaiian", sauce="tomato", cheese="reg", toppings={"ham": "all"}), {"kind": "item", "id": "coke", "qty": 2}], mode="delivery", address="12 Pardo Rd, Cebu City"))
    j = r.get_json()
    assert r.status_code == 201 and j["sent"] is True and re.fullmatch(r"F[2-9A-HJ-NP-Z]{5}", j["ticket"])
    assert j["total"] == 199 + 130 + 60
    urls = [u for u, _ in calls]
    assert urls == ["https://api.telegram.org/bot123:abc/sendMessage", "https://discord.example/hook"]
    ticket = calls[0][1]["text"]
    for want in ("NEW ORDER " + j["ticket"], "Lex · 0917 123 4567", "Deliver to: 12 Pardo Rd, Cebu City", "1× Hawaiian", "No Pineapple", "2× Coke (can)", "Delivery ₱60", "TOTAL ₱389"):
        assert want in ticket, want
    assert calls[0][1]["chat_id"] == "-100"
    page = c.get(j["receipt_url"])
    assert page.status_code == 200 and b"was sent to the shop" in page.data and b"Hawaiian" in page.data and b"389" in page.data
    assert b"Text the order" not in page.data  # not needed when it was delivered


def test_one_channel_down_is_fine_all_down_is_an_error(load, monkeypatch):
    m = load(TELEGRAM_BOT_TOKEN="t", TELEGRAM_CHAT_ID="c", DISCORD_WEBHOOK_URL="https://d.example/h")
    c = m.app.test_client()
    monkeypatch.setattr(m, "post_json", lambda url, p: "telegram" in url)  # discord fails
    assert c.post("/api/orders", json=order([PIZZA])).get_json()["sent"] is True
    m._hits.clear()
    monkeypatch.setattr(m, "post_json", lambda url, p: False)
    r = c.post("/api/orders", json=order([PIZZA]))
    assert r.status_code == 502 and "couldn't send" in r.get_json()["error"]


def test_no_channel_configured_falls_back_to_sms_and_copy(load):
    m = load(SHOP_PHONE="+63 917 000 1111")
    c = m.app.test_client()
    j = c.post("/api/orders", json=order([PIZZA])).get_json()
    assert j["sent"] is False
    page = c.get(j["receipt_url"]).data.decode()
    assert "has not reached the shop yet" in page and 'href="sms:+639170001111?&amp;body=' in page  # &amp; is how HTML writes &
    assert 'id="copy"' in page
    m2 = load()  # no phone either: still shows the copy button
    j = m2.app.test_client().post("/api/orders", json=order([PIZZA])).get_json()
    page = m2.app.test_client().get(j["receipt_url"]).data.decode()
    assert 'id="copy"' in page and "sms:" not in page


def test_receipt_cannot_be_forged_or_inject_html(load, monkeypatch):
    m = load()
    c = m.app.test_client()
    j = c.post("/api/orders", json=order([PIZZA], name="<script>alert(1)</script>")).get_json()
    html = c.get(j["receipt_url"]).data.decode()
    assert "<script>alert(1)" not in html and "&lt;script&gt;alert(1)" in html
    tok = j["receipt_url"].split("/r/")[1]
    assert c.get("/r/" + tok[:-3] + "AAA").status_code == 404 and c.get("/r/garbage").status_code == 404
    other = load()  # a different SECRET_KEY must not accept this token
    monkeypatch.setenv("SECRET_KEY", "another-secret")
    other = importlib.reload(sys.modules["app"])
    assert other.app.test_client().get("/r/" + tok).status_code == 404


def test_big_order_receipt_link_stays_a_sensible_length(app_mod):
    c = app_mod.app.test_client()
    full = {"kind": "pizza", "qty": 20, "size": "l", "crust": "stuffed", "sauce": "white", "cheese": "extra", "toppings": {t["id"]: "all" for t in c.get("/api/menu").get_json()["topping"]}}
    cart = [{**full, "size": s, "crust": cr} for s in "sml" for cr in ("thin", "classic", "stuffed")] + [{"kind": "item", "id": i, "qty": 1} for i in ("coke", "water", "lava", "fries-r", "spaghetti", "caesar")]
    for line in cart[:9]:
        line["qty"] = 1
    r = c.post("/api/orders", json=order(cart))
    assert r.status_code == 201 and len(r.get_json()["receipt_url"]) < 6000
