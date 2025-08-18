import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Min, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _t
from django.views.decorators.http import require_POST

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from esi.decorators import token_required

from .models import (
    MarketTrackingConfig,
    TrackedItem,
    TrackedContract,
    MarketOrderSnapshot,
    MarketCharacter,
    TrackedStructure,
    Delivery,
    ContractSnapshot,
    ContractError,
    ContractDelivery,
)

from .utils import contract_matches
from .forms import (
    TrackedItemForm,
    DeliveryQuantityForm,
    TrackedContractForm,
    ContractDeliveryQuantityForm,
)
from .tasks import fetch_market_data, refresh_contracts  # zakładam, że już masz te taski

logger = logging.getLogger(__name__)


@login_required
@token_required(scopes=[
    "esi-contracts.read_character_contracts.v1",
    "esi-assets.read_assets.v1",
    "esi-markets.read_character_orders.v1"
])
def character_login_list(request, token):
    if MarketCharacter.objects.filter(token=token).exists():
        messages.error(request, _t("This character is already used as admin market character."))
        return redirect("markettracker:list_items")

    messages.success(request, _t("Character successfully linked for item list tracking."))
    return redirect("markettracker:list_items")


@login_required
@token_required(scopes=[
    "esi-markets.structure_markets.v1",
    "esi-universe.read_structures.v1",
    "esi-contracts.read_character_contracts.v1",
    "esi-assets.read_assets.v1",
    "esi-markets.read_character_orders.v1"
])
def character_login_manage(request, token):
    MarketCharacter.objects.all().delete()

    eve_character, _ = EveCharacter.objects.get_or_create(
        character_id=token.character_id, defaults={"character_name": token.character_name}
    )
    ownership, _ = CharacterOwnership.objects.get_or_create(character=eve_character, user=request.user)
    MarketCharacter.objects.create(character=ownership, token=token)

    messages.success(request, _t("Admin market character successfully linked."))
    return redirect("markettracker:manage_stock")


@login_required
def list_items_view(request):
    config = MarketTrackingConfig.objects.first()
    if not config:
        messages.error(request, _t("Market tracking configuration not found."))
        return redirect("markettracker:manage_stock")

    # nazwa lokalizacji (region albo znana struktura)
    location_name = str(config.location_id)
    if config.scope == "region":
        from eveuniverse.models import EveRegion
        try:
            location_name = EveRegion.objects.get(id=config.location_id).name
        except EveRegion.DoesNotExist:
            pass
    else:
        try:
            structure = TrackedStructure.objects.get(structure_id=config.location_id)
            location_name = structure.name
        except TrackedStructure.DoesNotExist:
            pass

    # progi – bierzemy z configu
    yellow_threshold = config.yellow_threshold or 50
    red_threshold = config.red_threshold or 25

    q = request.GET.get("q", "").strip()
    status_filter = (request.GET.get("status") or "").lower()  # 'red' jako toggle

    tracked_items = TrackedItem.objects.all()
    if q:
        tracked_items = tracked_items.filter(item__name__icontains=q)

    items_data = []
    for tracked in tracked_items:
        orders = MarketOrderSnapshot.objects.filter(tracked_item=tracked)
        agg = orders.aggregate(min_price=Min("price"), total_vol=Sum("volume_remain"))
        min_price = agg["min_price"]
        total_volume = agg["total_vol"] or 0

        desired = tracked.desired_quantity or 1
        percentage = int((total_volume / desired) * 100)

        if percentage <= red_threshold:
            computed_status = "RED"
        elif percentage <= yellow_threshold:
            computed_status = "YELLOW"
        else:
            computed_status = "OK"

        items_data.append({
            "item": tracked.item,
            "desired_quantity": tracked.desired_quantity,
            "price": min_price,
            "volume_remain": total_volume,
            "status": computed_status,
            "percentage": percentage,
        })

    # filtr toggle "Only RED"
    if status_filter == "red":
        items_data = [it for it in items_data if it["status"] == "RED"]
    if status_filter == "yellow":
        items_data = [it for it in items_data if it["status"] == "YELLOW"]

    return render(
        request,
        "markettracker/list_items.html",
        {
            "items": items_data,
            "region": location_name,
            "q": q,
            "status": status_filter,
            "yellow_threshold": yellow_threshold,
            "red_threshold": red_threshold,
        },
    )


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def manage_stock_view(request):
    """
    Jeden widok obsługuje:
    - Items: add/edit
    - Contracts: add/edit
    - Szybkie refresh'e: items / contracts
    """
    q = request.GET.get("q", "")
    cq = request.GET.get("cq", "")

    add_mode = "add" in request.GET
    edit_id = request.GET.get("edit_id")

    tc_add_mode = "tc_add" in request.GET
    tc_edit_id = request.GET.get("tc_edit")

    if request.method == "POST":
        if "refresh" in request.POST:
            fetch_market_data.delay(request.user.pk)
            messages.success(request, _t("Market data refresh started."))
            return redirect("markettracker:manage_stock")

        if "refresh_contracts" in request.POST:
            refresh_contracts.delay()
            messages.success(request, _t("Contracts refresh started."))
            return redirect("markettracker:manage_stock")

        if "add" in request.POST:
            form = TrackedItemForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _t("Item added successfully."))
                return redirect("markettracker:manage_stock")

        if "edit" in request.POST:
            tracked_item = get_object_or_404(TrackedItem, pk=request.POST.get("item_id"))
            form = TrackedItemForm(request.POST, instance=tracked_item)
            if form.is_valid():
                form.save()
                messages.success(request, _t("Item updated successfully."))
                return redirect("markettracker:manage_stock")

        if "tc_add_submit" in request.POST:
            tc_form = TrackedContractForm(request.POST)
            if tc_form.is_valid():
                obj = tc_form.save(commit=False)
                obj.created_by = request.user
                obj.save()
                messages.success(request, _t("Tracked contract added."))
                return redirect("markettracker:manage_stock")
            form = None
            tc_add_mode = True

        if "tc_edit_submit" in request.POST:
            tc_obj = get_object_or_404(TrackedContract, pk=request.POST.get("tc_id"))
            tc_form = TrackedContractForm(request.POST, instance=tc_obj)
            if tc_form.is_valid():
                tc_form.save()
                messages.success(request, _t("Tracked contract updated."))
                return redirect("markettracker:manage_stock")
            tc_edit_id = tc_obj.pk

    # GET – przygotowanie formularzy
    if edit_id:
        _obj = get_object_or_404(TrackedItem, pk=edit_id)
        form = TrackedItemForm(instance=_obj)
    elif add_mode:
        form = TrackedItemForm()
    else:
        form = None

    tc_form = None
    if tc_add_mode:
        tc_form = TrackedContractForm()
    elif tc_edit_id:
        _tc = get_object_or_404(TrackedContract, pk=tc_edit_id)
        tc_form = TrackedContractForm(instance=_tc)

    tracked_items = TrackedItem.objects.all()
    if q:
        tracked_items = tracked_items.filter(item__name__icontains=q)

    tracked_contracts = (
        TrackedContract.objects.select_related("fitting", "fitting__ship_type")
        .all()
        .order_by("mode", "title_filter", "fitting__name")
    )
    if cq:
        tracked_contracts = tracked_contracts.filter(
            Q(fitting__ship_type__name__icontains=cq) |
            Q(fitting__name__icontains=cq) |
            Q(title_filter__icontains=cq)
        )

    market_character = MarketCharacter.objects.first()

    return render(
        request,
        "markettracker/manage_stock.html",
        {
            "form": form,
            "tc_form": tc_form,
            "tc_add_mode": tc_add_mode,
            "tc_edit_id": tc_edit_id,
            "tracked_items": tracked_items,
            "tracked_contracts": tracked_contracts,
            "market_character": market_character,
            "q": q,
            "cq": cq,
        },
    )


@login_required
def refresh_market_data(request):
    fetch_market_data.delay(request.user.pk)
    messages.success(request, _t("Market data refresh started."))
    return redirect("markettracker:manage_stock")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def contract_errors_view(request):
    errors = ContractError.objects.filter(is_resolved=False).order_by("-created_at")
    return render(request, "markettracker/contract_errors.html", {"errors": errors})


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
@require_POST
def delete_trackeditem(request, pk):
    item = get_object_or_404(TrackedItem, pk=pk)
    item.delete()
    messages.success(request, _t("Item deleted successfully."))
    return redirect("markettracker:manage_stock")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def tracked_contract_delete(request, pk):
    if request.method != "POST":
        messages.error(request, _t("Invalid request."))
        return redirect("markettracker:manage_stock")
    tc = get_object_or_404(TrackedContract, pk=pk)
    tc.delete()
    messages.success(request, _t("Tracked contract deleted."))
    return redirect("markettracker:manage_stock")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def tracked_contract_edit(request, pk):
    url = f"{reverse('markettracker:manage_stock')}?tc_edit={pk}"
    return redirect(url)


@login_required
def create_delivery(request, item_id):
    tracked_item = get_object_or_404(TrackedItem, item__id=item_id)

    if request.method == "POST":
        form = DeliveryQuantityForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.user = request.user
            delivery.item = tracked_item.item
            delivery.save()
            messages.success(request, _t("Delivery declared successfully."))
            return redirect("markettracker:deliveries_list")
    else:
        form = DeliveryQuantityForm()

    return render(request, "markettracker/delivery_form.html", {"form": form, "tracked_item": tracked_item})


@login_required
def create_contract_delivery(request, tc_id):
    tc = get_object_or_404(TrackedContract, pk=tc_id)
    if request.method == "POST":
        form = ContractDeliveryQuantityForm(request.POST)
        if form.is_valid():
            d = form.save(commit=False)
            d.user = request.user
            d.tracked_contract = tc
            d.save()
            messages.success(request, _t("Contract delivery declared."))
            return redirect("markettracker:deliveries_list")
    else:
        form = ContractDeliveryQuantityForm()
    return render(request, "markettracker/contract_delivery_form.html", {"form": form, "tc": tc})


@login_required
def deliveries_list_view(request):
    item_deliveries = Delivery.objects.filter(user=request.user, status="PENDING")
    contract_deliveries = ContractDelivery.objects.filter(user=request.user, status="PENDING").select_related(
        "tracked_contract", "tracked_contract__fitting"
    )
    return render(request, "markettracker/deliveries_list.html", {
        "item_deliveries": item_deliveries,
        "contract_deliveries": contract_deliveries,
    })


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def admin_deliveries_view(request):
    item_deliveries = Delivery.objects.all()
    contract_deliveries = ContractDelivery.objects.all().select_related(
        "tracked_contract", "tracked_contract__fitting", "user"
    )
    return render(request, "markettracker/admin_deliveries.html", {
        "item_deliveries": item_deliveries,
        "contract_deliveries": contract_deliveries,
    })


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def delete_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.delete()
    messages.success(request, _t("Delivery deleted successfully."))
    return redirect("markettracker:admin_deliveries")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def finish_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.delivered_quantity = delivery.declared_quantity
    delivery.status = "FINISHED"
    delivery.save()
    messages.success(request, _t("Delivery marked as finished."))
    return redirect("markettracker:admin_deliveries")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def refresh_contracts_data(request):
    refresh_contracts.delay()
    messages.success(request, _t("Contracts refresh started."))
    return redirect("markettracker:contracts_list")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def contracts_list_view(request):
    alert = MarketTrackingConfig.objects.first()
    yellow = alert.yellow_threshold if alert else 50
    red = alert.red_threshold if alert else 25

    tc_query = (request.GET.get("tc") or "").strip().lower()
    status_filter = (request.GET.get("status") or "").lower()

    all_contracts = list(
        ContractSnapshot.objects
        .filter(status__iexact="outstanding", type__iexact="item_exchange")
        .order_by("-date_issued")
    )

    tracked_qs = (
        TrackedContract.objects
        .select_related("fitting", "fitting__ship_type")
        .all()
    )

    rows = []
    for tc in tracked_qs:
        matched = []
        for c in all_contracts:
            ok, reason = contract_matches(tc, c)
            if ok:
                matched.append(c)
            else:
                logger.debug("[Contracts] No match for TC#%s vs #%s: %s", tc.id, c.contract_id, reason)

        current_qty = len(matched)
        desired = tc.desired_quantity or 0

        if desired <= 0:
            status = "OK"
            percent = 100
        else:
            percent = int((current_qty / desired) * 100)
            if percent <= red:
                status = "RED"
            elif percent <= yellow:
                status = "YELLOW"
            else:
                status = "OK"

        min_price = None
        if matched:
            prices = [float(m.price) for m in matched if getattr(m, "price", None) is not None]
            if prices:
                min_price = min(prices)

        if tc.mode == TrackedContract.Mode.DOCTRINE and tc.fitting:
            icon_type_id = tc.fitting.ship_type_id
            name = tc.fitting.name
            ship_name = getattr(tc.fitting.ship_type, "name", "") or ""
        else:
            icon_type_id = None
            name = tc.title_filter or "—"
            ship_name = ""

        rows.append({
            "tc": tc,
            "mode": tc.mode,
            "name": name,
            "ship_name": ship_name,
            "icon_type_id": icon_type_id,
            "current_qty": current_qty,
            "desired_qty": desired,
            "min_price": min_price,
            "status": status,
            "percent": percent,
        })
    if tc_query:
        def _hit(r):
            hay = " ".join([
                r["name"] or "",
                r.get("ship_name") or "",
                getattr(r["tc"], "title_filter", "") or "",
            ]).lower()
            return tc_query in hay
        rows = [r for r in rows if _hit(r)]

    if status_filter == "red":
        rows = [r for r in rows if r["status"] == "RED"]
    elif status_filter == "yellow":
        rows = [r for r in rows if r["status"] == "YELLOW"]

    return render(
        request,
        "markettracker/contracts_list.html",
        {
            "rows": rows,
            "tc": request.GET.get("tc", ""),
            "status": status_filter,
            "yellow_threshold": yellow,
            "red_threshold": red,
        },
    )
