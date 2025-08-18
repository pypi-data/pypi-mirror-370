import logging
import requests
from typing import Dict, Tuple
from collections import Counter

from django.conf import settings

from allianceauth.groupmanagement.models import Group
from allianceauth.services.modules.discord.models import DiscordUser
from requests.exceptions import HTTPError

from eveuniverse.models import EveSolarSystem, EveRegion
from esi.clients import EsiClientProvider

from .models import (
    MarketCharacter,
    TrackedStructure,
    TrackedContract,
    ContractSnapshot,
    HAS_FITTINGS,
    Fitting,
)

logger = logging.getLogger(__name__)
ESI_BASE_URL = "https://esi.evetech.net/latest"
esi = EsiClientProvider()


def resolve_ping_target(ping_value: str) -> str:
    if not ping_value:
        return ""
    if ping_value in ("@here", "@everyone"):
        return ping_value

    if ping_value.startswith("@"):
        group_name = ping_value[1:]
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return f"@{group_name}"

        try:
            discord_group_info = DiscordUser.objects.group_to_role(group=group)
        except HTTPError:
            return f"@{group_name}"
        except Exception:
            # bezpieczeństwo: nie wysypujemy taska
            return f"@{group_name}"

        if discord_group_info and "id" in discord_group_info:
            return f"<@&{discord_group_info['id']}>"
        return f"@{group_name}"

    return ""



def location_display(scope: str, location_id: int) -> str:
    """Ładna nazwa lokalizacji (Region albo zapisany TrackedStructure)."""
    if scope == "region":
        try:
            return EveRegion.objects.get(id=location_id).name
        except EveRegion.DoesNotExist:
            return str(location_id)
    else:
        try:
            return TrackedStructure.objects.get(structure_id=location_id).name
        except TrackedStructure.DoesNotExist:
            return str(location_id)


def resolve_ping_target_from_config(config) -> str:
    """
    Zwraca treść do 'content' dla Discorda na podstawie MarketTrackingConfig:
    - @here / @everyone / "" (none)
    - lub <@&ROLE_ID> dla zmapowanej grupy
    """
    if config.discord_ping_group:
        try:
            mapping = DiscordUser.objects.group_to_role(group=config.discord_ping_group)
            role_id = mapping.get("id") if mapping else None
            if role_id:
                return f"<@&{role_id}>"
        except HTTPError:
            logger.exception("[MarketTracker] Discord service error when resolving group role")
        # fallback – nazwa grupy
        return f"@{config.discord_ping_group.name}"

    v = (config.discord_ping_group_text or "").strip()
    if v in {"here", "@here"}:
        return "@here"
    if v in {"everyone", "@everyone"}:
        return "@everyone"
    return ""


_ALLOWED_SLOT_PREFIXES = (
    "LoSlot", "MedSlot", "HiSlot",
    "RigSlot", "SubSystemSlot", "ServiceSlot",
)
_IGNORE_FLAGS = {"Cargo", "DroneBay", "FighterBay", "Invalid"}


def _fitting_requirements(fitting: Fitting) -> Tuple[int, Dict[int, int]]:
    hull_id = int(fitting.ship_type_id)
    req = Counter()
    for it in fitting.items.all():
        flag = it.flag or ""
        if flag in _IGNORE_FLAGS:
            continue
        if not flag.startswith(_ALLOWED_SLOT_PREFIXES):
            continue
        req[int(it.type_id)] += int(it.quantity or 1)
    return hull_id, dict(req)


def _contract_items_as_counter(contract) -> Tuple[int | None, Dict[int, int]]:
    items = getattr(contract, "items", None) or []
    counts = Counter()
    hull_id = None
    for it in items:
        try:
            t = int(it.get("type_id"))
            q = int(it.get("quantity") or it.get("quantity_delivered") or 0)
            counts[t] += q
            if it.get("is_singleton"):
                hull_id = hull_id or t
        except Exception:
            continue
    return hull_id, dict(counts)


def contract_matches(tc: TrackedContract, snap: ContractSnapshot):
    """True/False, 'code' — jak wcześniej, plus logi DEBUG."""
    if not tc.is_active:
        return False, None

    if (snap.type or "").lower() != "item_exchange":
        return False, "type"
    if (snap.status or "").lower() != "outstanding":
        return False, "status"

    # MAX PRICE
    if tc.max_price and float(tc.max_price) > 0:
        price = snap.price or 0
        if float(price) > float(tc.max_price):
            logger.debug("[match] snap %s price %.2f > max %.2f", snap.contract_id, price, float(tc.max_price))
            return False, "price"

    title = (snap.title or "").strip()

    if tc.mode == TrackedContract.Mode.CUSTOM:
        filt = (tc.title_filter or "").strip()
        if not filt:
            return False, "title"
        if filt.lower() not in title.lower():
            logger.debug("[match] snap %s title '%s' !contains '%s'", snap.contract_id, title, filt)
            return False, "title"
        return True, None

    if tc.mode == TrackedContract.Mode.DOCTRINE:
        if not tc.fitting:
            return False, "doctrine"

        fit_name = (tc.fitting.name or "").strip()
        if fit_name and fit_name.lower() not in title.lower():
            logger.debug("[match] snap %s title '%s' !contains fit '%s'", snap.contract_id, title, fit_name)
            return False, "title"

        items = snap.items or []
        if not items:
            return False, "modules"

        contract_type_ids = set()
        for it in items:
            try:
                tid = int(it.get("type_id"))
                if tid > 0:
                    contract_type_ids.add(tid)
            except Exception:
                continue

        required_type_ids = set()
        for fi in tc.fitting.items.all():
            if fi.flag in ("Cargo", "DroneBay", "FighterBay"):
                continue
            tid = int(fi.type_id)
            if tid > 0:
                required_type_ids.add(tid)

        missing = required_type_ids - contract_type_ids
        if missing:
            logger.debug("[match] snap %s missing modules: %s", snap.contract_id, sorted(list(missing)))
            return False, "modules"

        return True, None

    return False, "mode"
