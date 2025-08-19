from typing import Any
from django import forms
from nautobot.apps.forms import DynamicModelChoiceField
from nautobot.dcim.models import Device
from nautobot_move.replace_switch_utils import replace_device


class InstallBaseForm(forms.Form):
    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        return super().__init__(*args, **kwargs)

    def save(self):
        inventory, failed, interface_lut, components_create = replace_device(
            self.get_planned(), self.get_inventory(), True
        )
        failed.delete()
        return inventory


class InstallForm(InstallBaseForm):
    planned = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Planned",
        },
        help_text="The planned device where this device is going to be installed.",
    )

    def get_planned(self) -> Device:
        return Device.objects.get(pk=self.cleaned_data.get("planned").pk)

    def get_inventory(self) -> Device:
        return self.instance


class ReverseInstallForm(InstallBaseForm):
    inventory = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Inventory",
        },
        help_text="The inventory device that is going to be installed.",
    )

    def get_planned(self) -> Device:
        return self.instance

    def get_inventory(self) -> Device:
        return Device.objects.get(pk=self.cleaned_data.get("inventory").pk)


class ReplaceBaseForm(forms.Form):
    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        return super().__init__(*args, **kwargs)

    def save(self):
        return replace_device(self.get_failed(), self.get_inventory(), False)

    def clean(self) -> dict[str, Any]:
        failed = self.get_failed()
        inventory = self.get_inventory()
        if inventory == failed:
            raise forms.ValidationError("Can't replace device with itself")
        return super().clean()


class ReplaceForm(ReplaceBaseForm):
    failed = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Failed",
        },
        help_text="The failed device which this device is going to replace.",
    )

    def get_failed(self) -> Device:
        return self.cleaned_data.get("failed")

    def get_inventory(self) -> Device:
        return self.instance


class ReverseReplaceForm(ReplaceBaseForm):
    inventory = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        display_field="display_name",
        query_params={
            "status": "Inventory",
        },
        help_text="The inventory device with which this device is going to be replaced with.",
    )

    def get_failed(self) -> Device:
        return self.instance

    def get_inventory(self) -> Device:
        return self.cleaned_data.get("inventory")
