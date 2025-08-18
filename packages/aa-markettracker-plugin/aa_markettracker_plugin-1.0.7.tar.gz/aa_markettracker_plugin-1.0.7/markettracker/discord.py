# discord.py
import logging
import requests
from django.utils import timezone
from django.conf import settings
from .models import DiscordWebhook, DiscordMessage
from .utils import resolve_ping_target

logger = logging.getLogger(__name__)


def _iter_webhook_urls():
    for wh in DiscordWebhook.objects.all():
        url = (wh.url or "").strip()
        if url:
            yield url


def _get_ping_string(dm: DiscordMessage, which: str) -> str:
    """
    Zwraca JEDEN string jak w greenlight:
      "", "@here", "@everyone", "@NazwaGrupy"
    Składamy go z Twojego modelu (choice + group_fk).
    """
    if which == "items":
        # choice najpierw (here/everyone/none)
        if dm.item_ping_choice in ("here", "everyone"):
            return f"@{dm.item_ping_choice}"
        # jeśli wskazano grupę – zwracamy @GroupName
        if dm.item_ping_group:
            return f"@{dm.item_ping_group.name}"
        return ""
    else:
        if dm.contract_ping_choice in ("here", "everyone"):
            return f"@{dm.contract_ping_choice}"
        if dm.contract_ping_group:
            return f"@{dm.contract_ping_group.name}"
        return ""


def _post_embed(embed: dict, ping: str = ""):
    payload = {
        "username": "Market Tracker",
        
        "content": ping or "", "embeds": [embed]
        }
    headers = {"User-Agent": getattr(settings, "ESI_USER_AGENT", "MarketTracker/1.0")}
    for url in _iter_webhook_urls():
        try:
            requests.post(url, json=payload, headers=headers, timeout=6)
        except Exception:
            logger.exception("[MarketTracker] Discord send failed for %s", url)


def send_items_alert(changed_items, location_name: str):
    # filtr: tylko żółty/czerwony
    changed_items = [(i, s, p, t, d) for (i, s, p, t, d) in changed_items if s in ("YELLOW", "RED")]
    if not changed_items:
        return

    dm = DiscordMessage.objects.first()
    header = (dm.item_alert_header if dm and dm.item_alert_header else "⚠️ MarketTracker Items")

    embed = {
        "title": f"Items status changes in {location_name}",
        "description": header,
        "color": 0xFF0000,
        "fields": [],
        "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
    }
    for item, status, percent, total, desired in changed_items:
        embed["fields"].append({
            "name": item.item.name,
            "value": f"**{status}** ({percent}%) – {total}/{desired}",
            "inline": False,
        })

    ping_str = _get_ping_string(dm, "items") if dm else ""
    _post_embed(embed, resolve_ping_target(ping_str))


def send_contracts_alert(changed_rows):
    changed_rows = [r for r in changed_rows if r.get("status") in ("YELLOW", "RED")]
    if not changed_rows:
        return

    dm = DiscordMessage.objects.first()
    header = (dm.contract_alert_header if dm and dm.contract_alert_header else "📦 MarketTracker Contracts")

    embed = {
        "title": "Tracked Contracts status changes",
        "description": header,
        "color": 0xFF0000,
        "fields": [],
        "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
    }
    for r in changed_rows:
        line = f"**{r['status']}** ({r['percent']}%) – {r['current']}/{r['desired']}"
        if r.get("min_price") is not None:
            line += f" | min: {r['min_price']:.2f} ISK"
        embed["fields"].append({"name": r["name"], "value": line, "inline": False})

    ping_str = _get_ping_string(dm, "contracts") if dm else ""
    _post_embed(embed, resolve_ping_target(ping_str))
