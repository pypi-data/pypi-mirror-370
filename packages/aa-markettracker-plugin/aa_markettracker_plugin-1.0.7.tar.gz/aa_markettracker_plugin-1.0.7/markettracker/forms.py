from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from eveuniverse.models import EveRegion, EveType

from .models import (
    MarketTrackingConfig,
    TrackedItem,
    Delivery,
    TrackedContract,
    ContractDelivery,
    DiscordMessage,
    HAS_FITTINGS,
    Fitting,
)

# ===== Tracked Items =====

class TrackedItemForm(forms.ModelForm):
    class Meta:
        model = TrackedItem
        fields = ["item", "desired_quantity"]
        widgets = {"item": forms.Select(attrs={"class": "select-search"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = (
            EveType.objects.filter(published=True, name__isnull=False)
            .exclude(eve_group_id__in=[6, 25, 1, 14, 52, 67, 89])
            .order_by("name")
        )


# ===== Market Tracking Config (region / structure + thresholds) =====

class MarketTrackingConfigForm(forms.ModelForm):
    LOCATION_TYPE_CHOICES = [("region", "Region"), ("structure", "Structure")]

    location_type = forms.ChoiceField(
        choices=LOCATION_TYPE_CHOICES,
        label=_("Location Type"),
        initial="region",
        help_text=_("Select whether to track a region or a specific structure."),
    )
    region = forms.ModelChoiceField(
        queryset=EveRegion.objects.all(),
        required=False,
        label=_("Region"),
        help_text=_("Select region if tracking entire region."),
    )
    structure_id = forms.CharField(
        required=False,
        label=_("Structure ID"),
        help_text=_("Enter structure ID if tracking a specific structure."),
    )

    class Meta:
        model = MarketTrackingConfig
        fields = [
            "location_type",
            "region",
            "structure_id",
            "yellow_threshold",
            "red_threshold",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # pre-fill current state from instance
        if self.instance and self.instance.pk:
            if self.instance.scope == "region":
                self.initial["location_type"] = "region"
                try:
                    self.initial["region"] = EveRegion.objects.get(id=self.instance.location_id)
                except EveRegion.DoesNotExist:
                    pass
            else:
                self.initial["location_type"] = "structure"
                self.initial["structure_id"] = str(self.instance.location_id)

    def clean(self):
        cleaned = super().clean()
        loc_type = cleaned.get("location_type")
        reg = cleaned.get("region")
        struct = cleaned.get("structure_id")

        if loc_type == "region":
            if not reg:
                raise forms.ValidationError(_("You must select a region."))
            cleaned["location_id"] = reg.id
            cleaned["structure_id"] = "1"  # Twoje wymaganie: ustaw 1 gdy region
        else:
            try:
                cleaned["location_id"] = int(struct)
            except (ValueError, TypeError):
                raise forms.ValidationError(_("Structure ID must be a number."))

        return cleaned

    def save(self, commit=True):
        inst = super().save(commit=False)
        data = self.cleaned_data
        inst.scope = data["location_type"]
        inst.location_id = data["location_id"]
        if commit:
            inst.save()
        return inst


# ===== Deliveries =====

class DeliveryQuantityForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ["declared_quantity"]
        widgets = {"declared_quantity": forms.NumberInput(attrs={"class": "form-control"})}


class ContractDeliveryQuantityForm(forms.ModelForm):
    class Meta:
        model = ContractDelivery
        fields = ["declared_quantity"]
        widgets = {"declared_quantity": forms.NumberInput(attrs={"class": "form-control"})}


# ===== Tracked Contracts =====

class TrackedContractForm(forms.ModelForm):
    class Meta:
        model = TrackedContract
        fields = ["mode", "title_filter", "fitting", "max_price", "desired_quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["mode"].label = _("Tracking type")
        self.fields["title_filter"].label = _("Title contains")
        self.fields["fitting"].label = _("Doctrine fitting")
        self.fields["max_price"].label = _("Max price (ISK)")
        self.fields["desired_quantity"].label = _("Desired contracts")

        if HAS_FITTINGS:
            self.fields["fitting"].widget = forms.Select(attrs={"class": "select-search"})
            self.fields["fitting"].queryset = Fitting.objects.all().order_by("name")
        else:
            self.fields["fitting"].widget = forms.Select(attrs={"disabled": "disabled"})
            self.fields["fitting"].help_text = _("Fittings app not installed.")

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get("mode")
        title = (cleaned.get("title_filter") or "").strip()
        fit = cleaned.get("fitting")

        if mode == TrackedContract.Mode.CUSTOM:
            if not title:
                raise forms.ValidationError(_("For custom tracking please provide 'Title contains'."))

        if mode == TrackedContract.Mode.DOCTRINE:
            if not HAS_FITTINGS:
                raise forms.ValidationError(_("Fittings app required for doctrine tracking."))
            if not fit:
                raise forms.ValidationError(_("Please select a doctrine fitting."))
        return cleaned


# ===== Discord Messages (nagłówki + ping dropdowny) =====

class DiscordMessageForm(forms.ModelForm):
    # dropdowny widoczne w adminie (łączenie 'none/here/everyone' + grupy AA)
    PING_CHOICES_BASE = [("none", "None"), ("here", "@here"), ("everyone", "@everyone")]

    item_ping_target = forms.ChoiceField(label=_("Items ping target"), required=False)
    contract_ping_target = forms.ChoiceField(label=_("Contracts ping target"), required=False)

    class Meta:
        model = DiscordMessage
        fields = [
            "item_alert_header",
            "contract_alert_header",
            # zapisy do tych pól ustawimy w save():
            # item_ping_choice, item_ping_group, contract_ping_choice, contract_ping_group
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        groups = [(f"group:{g.pk}", g.name) for g in Group.objects.all().order_by("name")]
        self.fields["item_ping_target"].choices = self.PING_CHOICES_BASE + groups
        self.fields["contract_ping_target"].choices = self.PING_CHOICES_BASE + groups

        # initiale z instance
        if self.instance:
            # items
            if self.instance.item_ping_group:
                self.initial["item_ping_target"] = f"group:{self.instance.item_ping_group.pk}"
            else:
                self.initial["item_ping_target"] = self.instance.item_ping_choice or "none"
            # contracts
            if self.instance.contract_ping_group:
                self.initial["contract_ping_target"] = f"group:{self.instance.contract_ping_group.pk}"
            else:
                self.initial["contract_ping_target"] = self.instance.contract_ping_choice or "none"

    def save(self, commit=True):
        inst = super().save(commit=False)

        # ITEMS
        val_i = self.cleaned_data.get("item_ping_target") or "none"
        if val_i.startswith("group:"):
            inst.item_ping_group = Group.objects.get(pk=int(val_i.split(":")[1]))
            inst.item_ping_choice = None
        else:
            inst.item_ping_group = None
            inst.item_ping_choice = val_i  # none/here/everyone

        # CONTRACTS
        val_c = self.cleaned_data.get("contract_ping_target") or "none"
        if val_c.startswith("group:"):
            inst.contract_ping_group = Group.objects.get(pk=int(val_c.split(":")[1]))
            inst.contract_ping_choice = None
        else:
            inst.contract_ping_group = None
            inst.contract_ping_choice = val_c

        if commit:
            inst.save()
        return inst
