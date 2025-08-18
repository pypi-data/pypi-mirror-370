import logging
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db import transaction
from django.db.models import Sum

from esi.models import Token
from eveuniverse.models import EveRegion

from .models import (
    MarketCharacter,
    MarketTrackingConfig,
    MarketOrderSnapshot,
    TrackedItem,
    TrackedStructure,
    Delivery,
    ContractSnapshot,
    ContractDelivery,
    TrackedContract,
    ContractError,
)
from .discord import send_items_alert, send_contracts_alert
from .utils import contract_matches

logger = logging.getLogger(__name__)
ESI_BASE_URL = "https://esi.evetech.net/latest"


# ======= WSPÓLNE =======

def _location_name(config: MarketTrackingConfig) -> str:
    if not config:
        return "Unknown"
    if config.scope == "region":
        try:
            return EveRegion.objects.get(id=config.location_id).name
        except EveRegion.DoesNotExist:
            return str(config.location_id)
    else:
        try:
            return TrackedStructure.objects.get(structure_id=config.location_id).name
        except TrackedStructure.DoesNotExist:
            return str(config.location_id)


# ========== MARKET (ITEMS) ==========

@shared_task
def fetch_market_data_auto():
    mc = MarketCharacter.objects.first()
    if not mc:
        logger.warning("[MarketTracker] No MarketCharacter found for auto refresh.")
        return
    # CharacterOwnership zwykle ma character_id
    fetch_market_data(mc.character.character_id)


@shared_task
def fetch_market_data(character_id):
    config = MarketTrackingConfig.objects.first()
    if not config:
        logger.warning("[MarketTracker] No MarketTrackingConfig found")
        return

    yellow_threshold = config.yellow_threshold
    red_threshold = config.red_threshold
    changed_statuses = []

    # token admina
    try:
        character = MarketCharacter.objects.get(character__character_id=character_id)
        admin_token = character.token
        admin_access_token = admin_token.valid_access_token()
    except MarketCharacter.DoesNotExist:
        logger.warning("[MarketTracker] No MarketCharacter found for character_id=%s", character_id)
        return
    except Exception as e:
        logger.error("[MarketTracker] Token refresh failed: %s", e)
        return

    # purge snapshotów zamówień
    MarketOrderSnapshot.objects.all().delete()

    if config.scope == "region":
        seen_orders = _fetch_region_orders(config.location_id)
    else:
        seen_orders = _fetch_structure_orders(config.location_id, admin_access_token)

    logger.info("[MarketTracker] Orders imported: %s", len(seen_orders))

    # statusy
    for item in TrackedItem.objects.all():
        orders = MarketOrderSnapshot.objects.filter(tracked_item=item)
        total_volume = orders.aggregate(Sum("volume_remain"))["volume_remain__sum"] or 0
        desired = item.desired_quantity or 1
        percentage = int((total_volume / desired) * 100)

        if percentage <= red_threshold:
            new_status = "RED"
        elif percentage <= yellow_threshold:
            new_status = "YELLOW"
        else:
            new_status = "OK"

        if new_status != item.last_status:
            # tylko gdy zmiana i alarmowy status
            if new_status in ("YELLOW", "RED"):
                changed_statuses.append((item, new_status, percentage, total_volume, desired))
            item.last_status = new_status
            item.save(update_fields=["last_status"])

    _update_deliveries(config)

    if changed_statuses:
        logger.info("[MarketTracker] Status changes detected (items): %s", changed_statuses)
        send_items_alert(changed_statuses, _location_name(config))


def _fetch_region_orders(region_id):
    seen_orders = set()
    for tracked in TrackedItem.objects.all():
        type_id = tracked.item.id
        page = 1
        while True:
            url = f"{ESI_BASE_URL}/markets/{region_id}/orders/"
            params = {"order_type": "sell", "type_id": type_id, "page": page}
            headers = {"User-Agent": getattr(settings, "ESI_USER_AGENT", "MarketTracker/1.0")}
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                logger.error("[MarketTracker] Region page %s failed for %s: %s", page, tracked.item.name, e)
                break
            data = resp.json()
            pages = int(resp.headers.get("X-Pages", 1))
            seen_orders.update(_save_orders(data, tracked, region_id))
            if page >= pages:
                break
            page += 1
    return seen_orders


def _fetch_structure_orders(structure_id, access_token):
    seen_orders = set()
    for tracked in TrackedItem.objects.all():
        type_id = tracked.item.id
        page = 1
        while True:
            url = f"{ESI_BASE_URL}/markets/structures/{structure_id}/"
            params = {"page": page}
            headers = {
                "User-Agent": getattr(settings, "ESI_USER_AGENT", "MarketTracker/1.0"),
                "Authorization": f"Bearer {access_token}",
            }
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                logger.error("[MarketTracker] Structure page %s failed for %s: %s", page, tracked.item.name, e)
                break

            data = resp.json()
            pages = int(resp.headers.get("X-Pages", 1))
            filtered = [o for o in data if o.get("type_id") == type_id and not o.get("is_buy_order", False)]
            seen_orders.update(_save_orders(filtered, tracked, structure_id))
            if page >= pages:
                break
            page += 1
    return seen_orders


def _save_orders(orders, tracked_item, location_id):
    from django.utils import timezone as _tz
    seen_ids = set()
    for order in orders:
        if not isinstance(order, dict) or "type_id" not in order or "order_id" not in order:
            continue
        MarketOrderSnapshot.objects.update_or_create(
            order_id=order["order_id"],
            defaults={
                "tracked_item": tracked_item,
                "structure_id": location_id,
                "price": order.get("price", 0),
                "volume_remain": order.get("volume_remain", 0),
                "is_buy_order": order.get("is_buy_order", False),
                "issued": order.get("issued", _tz.now().isoformat()),
            },
        )
        seen_ids.add(order["order_id"])
    return seen_ids


def _update_deliveries(config):
    deliveries = Delivery.objects.filter(status="PENDING")
    tokens = [
        t for t in Token.objects.select_related("user").all()
        if t.scopes.filter(name="esi-markets.read_character_orders.v1").exists()
    ]

    for delivery in deliveries:
        total_delivered = 0
        for token in tokens:
            try:
                access_token = token.valid_access_token()
                orders = _fetch_character_orders(token.character_id, access_token, config)
                filtered = []
                for o in orders:
                    if "issued" not in o or "type_id" not in o:
                        continue
                    issued_dt = parse_datetime(o["issued"])
                    if issued_dt:
                        issued_dt = issued_dt.astimezone(timezone.utc)
                    if (
                        issued_dt
                        and issued_dt >= delivery.created_at
                        and o["type_id"] == delivery.item.id
                        and not o.get("is_buy_order", False)
                    ):
                        filtered.append(o)
                delivered_from_orders = sum(o["volume_remain"] for o in filtered)
                total_delivered += delivered_from_orders
            except Exception:
                logger.exception("[MarketTracker] Orders fetch failed for char %s", token.character_id)

        delivery.delivered_quantity = min(total_delivered, delivery.declared_quantity)
        if delivery.delivered_quantity >= delivery.declared_quantity:
            delivery.status = "FINISHED"
        delivery.save(update_fields=["delivered_quantity", "status"])


def _fetch_character_orders(character_id, access_token, config):
    url = f"{ESI_BASE_URL}/characters/{character_id}/orders/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": getattr(settings, "ESI_USER_AGENT", "MarketTracker/1.0"),
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    orders = resp.json()
    if config.scope == "region":
        return [o for o in orders if o.get("region_id") == config.location_id]
    return [o for o in orders if o.get("location_id") == config.location_id]


# ========== CONTRACTS ==========

@shared_task
def refresh_contracts():
    fetch_contracts_snapshots()
    _recalculate_contract_statuses_and_alert()
    _update_contract_deliveries()


@shared_task
def fetch_contracts_snapshots():
    # purge
    ContractSnapshot.objects.all().delete()
    logger.info("[Contracts] Purged old snapshots")

    tokens = Token.objects.filter(scopes__name="esi-contracts.read_character_contracts.v1").distinct()
    total = 0

    for token in tokens:
        try:
            access_token = token.valid_access_token()
        except Exception as e:
            logger.warning("[MarketTracker] Token refresh failed for %s: %s", token.character_name, e)
            continue

        char_id = token.character_id
        char_name = token.character_name or str(char_id)
        page = 1

        while True:
            url = f"{ESI_BASE_URL}/characters/{char_id}/contracts/"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": getattr(settings, "ESI_USER_AGENT", "MarketTracker/1.0"),
            }
            try:
                resp = requests.get(url, params={"page": page}, headers=headers, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                logger.error("[MarketTracker] Contracts fetch error for %s p.%s: %s", char_name, page, e)
                break

            data = resp.json()
            pages = int(resp.headers.get("X-Pages", 1))

            with transaction.atomic():
                for c in data:
                    # filtr: tylko outstanding + item_exchange
                    typ = (c.get("type") or "").lower()
                    status = (c.get("status") or "").lower()
                    if typ != "item_exchange" or status != "outstanding":
                        continue

                    title = c.get("title") or c.get("description") or ""
                    obj, _ = ContractSnapshot.objects.update_or_create(
                        contract_id=c["contract_id"],
                        defaults={
                            "owner_character_id": char_id,
                            "owner_character_name": char_name,
                            "type": typ,
                            "availability": (c.get("availability") or "").lower(),
                            "status": status,
                            "title": title,
                            "date_issued": c.get("date_issued"),
                            "date_expired": c.get("date_expired"),
                            "start_location_id": c.get("start_location_id"),
                            "end_location_id": c.get("end_location_id"),
                            "price": c.get("price"),
                            "reward": c.get("reward"),
                            "collateral": c.get("collateral"),
                            "volume": c.get("volume"),
                            "for_corporation": bool(c.get("for_corporation", False)),
                            "assignee_id": c.get("assignee_id"),
                            "acceptor_id": c.get("acceptor_id"),
                            "issuer_id": c.get("issuer_id"),
                            "issuer_corporation_id": c.get("issuer_corporation_id"),
                        },
                    )

                    # dociągnięcie items (opcjonalnie)
                    try:
                        items_url = f"{ESI_BASE_URL}/characters/{char_id}/contracts/{c['contract_id']}/items/"
                        items_resp = requests.get(items_url, headers=headers, timeout=15)
                        if items_resp.status_code == 200:
                            obj.items = items_resp.json()
                            obj.save(update_fields=["items"])
                    except Exception:
                        logger.debug("[MarketTracker] Items fetch failed for contract %s", c["contract_id"])

                    total += 1

            if page >= pages:
                break
            page += 1

    logger.info("[MarketTracker] Contracts fetched/updated: %s", total)


def _recalculate_contract_statuses_and_alert():
    config = MarketTrackingConfig.objects.first()
    if not config:
        return

    yellow = config.yellow_threshold
    red = config.red_threshold

    all_contracts = list(
        ContractSnapshot.objects.filter(
            status__iexact="outstanding",
            type__iexact="item_exchange",
        )
    )

    changed = []
    for tc in TrackedContract.objects.select_related("fitting").all():
        matched = []
        for c in all_contracts:
            ok, _err = contract_matches(tc, c)
            if ok:
                matched.append(c)

        current_qty = len(matched)
        desired = tc.desired_quantity or 0

        if desired <= 0:
            percent = 100
            new_status = "OK"
        else:
            percent = int((current_qty / desired) * 100)
            if percent <= red:
                new_status = "RED"
            elif percent <= yellow:
                new_status = "YELLOW"
            else:
                new_status = "OK"

        # wysyłamy tylko przy ZMIANIE i tylko YELLOW/RED
        if getattr(tc, "last_status", None) != new_status:
            tc.last_status = new_status
            tc.save(update_fields=["last_status"])

            if new_status in ("YELLOW", "RED"):
                name = (
                    tc.fitting.name
                    if (getattr(tc, "mode", None) == "doctrine" and tc.fitting)
                    else (tc.title_filter or "—")
                )
                prices = [float(m.price) for m in matched if getattr(m, "price", None) is not None]
                min_price = min(prices) if prices else None

                changed.append({
                    "name": name,
                    "status": new_status,
                    "percent": percent,
                    "current": current_qty,
                    "desired": desired,
                    "min_price": min_price,
                })

    if changed:
        send_contracts_alert(changed)


def _update_contract_deliveries():
    deliveries = ContractDelivery.objects.filter(status="PENDING").select_related("tracked_contract")
    if not deliveries.exists():
        return

    all_contracts = list(
        ContractSnapshot.objects.filter(
            status__iexact="outstanding",
            type__iexact="item_exchange",
        )
    )

    for d in deliveries:
        tc = d.tracked_contract
        matched = 0
        for c in all_contracts:
            ok, _err = contract_matches(tc, c)
            if ok:
                matched += 1

        d.delivered_quantity = min(matched, d.declared_quantity)
        if d.delivered_quantity >= d.declared_quantity:
            d.status = "FINISHED"
        d.save(update_fields=["delivered_quantity", "status"])
