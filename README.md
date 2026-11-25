# Forno Rosso: pizza ordering, no database

Customers pick one of 17 named pizzas (or build their own), customize it, add chicken, sides, pasta, desserts
and drinks, and place an order for pickup or delivery. **Nothing is stored.** The order is priced on the server,
sent to the shop as a message (Telegram and/or Discord), and the customer gets a receipt page. Deploys to Vercel.

## What you get, and what you give up
| Included | Not included (it needs a database) |
|---|---|
| Pizza gallery, builder, cart, prices checked on the server | Staff dashboard with order list and status buttons |
| Order arrives on your phone as a message | Live order status for the customer |
| Signed receipt page and ticket number | Editing the menu in the browser (edit `menu.py` instead) |
| Pay on pickup or delivery | Online payment |
| Nothing to host, back up or pay for | Order history |

## Run it on your computer
```bash
pip install -r requirements.txt
python app.py            # http://localhost:5000
python -m pytest tests   # optional (pip install pytest first)
```
With no settings the shop channel is "not set", so after ordering the receipt shows **Text the order** and
**Copy the order** buttons. That is the backup path when no channel is configured.

## Get orders on your phone (set up at least one)
**Telegram (recommended: push notifications)**
1. In Telegram, message **@BotFather**, send `/newbot`, follow the steps, and copy the **bot token**.
2. Open a chat with your new bot and send it any message. For a staff group, add the bot to the group and send a message there.
3. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser and find `"chat":{"id": ...}`. That number is the **chat id** (groups are negative).
4. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

**Discord:** channel settings → Integrations → Webhooks → New Webhook → Copy Webhook URL → set `DISCORD_WEBHOOK_URL`.

If a channel is set but the message can't be delivered, the customer sees an error and keeps their cart. The site
never tells a customer an order went through when it didn't.

## Deploy to Vercel
1. Push this folder to a GitHub repository.
2. On vercel.com: **Add New → Project**, import the repository. Vercel detects Flask (`app.py`), so there is no build setting to change.
3. Under **Environment Variables** add `SECRET_KEY` (any long random text) and your Telegram and/or Discord settings. Optionally `SHOP_PHONE`, `DELIVERY_FEE`.
4. Click **Deploy**. After changing a variable later, redeploy so it takes effect.

Static files are in `public/` because Vercel ignores Flask's `static` folder and serves `public/` from its CDN.

## Changing the menu
- **Prices and names:** edit `menu.py`, push to GitHub, Vercel redeploys.
- **Sold out for today:** set `SOLD_OUT` to a list of ids, e.g. `lava,pizza:bacon,topping:shrimp`, then redeploy. A bare id hides that id everywhere; `type:id` hides one item only. Ids are in `menu.py`.
- How named pizzas are priced: the listed price is for Medium; its own sauce, cheese and toppings are included; Small is ₱50 less and Large ₱100 more (the gap between the size prices); extras cost extra; removed toppings are shown as "No …" on the ticket with no refund.

## Settings
See `.env.example`. Only `SECRET_KEY` is required.

## Security notes
- Prices always come from `menu.py` on the server, never from the browser.
- Receipt links are signed with `SECRET_KEY`, so they can't be edited. Keep the key private and don't change it, or old receipt links stop working.
- Anyone can submit an order, so a prankster could spam your channel. The per-device limit here is best-effort (each serverless instance counts separately). Turn on **Vercel Firewall rate limiting** for `/api/orders` for a real limit.
- Keep the Telegram bot token and Discord webhook URL secret (environment variables only, never in the code).

## Want a staff dashboard and live status later?
Those need storage. The full version with a database, admin page and status tracking is a separate project
(it runs on a normal host with a disk, or on Vercel with a hosted Postgres).
