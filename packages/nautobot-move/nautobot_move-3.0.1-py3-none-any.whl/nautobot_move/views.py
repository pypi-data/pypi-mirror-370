from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from django.views.generic import View
from nautobot.apps.views import GetReturnURLMixin
from nautobot.dcim.models import Device

from .forms import InstallForm, ReverseInstallForm, ReplaceForm, ReverseReplaceForm


class MoveView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = "dcim.add_device"
    template_name = "nautobot_move/install.html"

    def get(self, request, *args, pk=None, **kwargs):
        inventory = Device.objects.get(pk=pk)
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        form = InstallForm(initial=initial_data)

        return render(
            request,
            self.template_name,
            {
                "inventory": inventory,
                "form": form,
                "return_url": self.get_return_url(request, inventory),
            },
        )

    def post(self, request, *args, pk=None, **kwargs):
        inventory = Device.objects.get(pk=pk)
        form = InstallForm(request.POST, request.FILES, instance=inventory)

        if form.is_valid():
            moved = form.save()

            msg = 'Moved device <a href="{}">{}</a>'.format(
                moved.get_absolute_url(), escape(moved)
            )
            messages.success(request, mark_safe(msg))

            return_url = form.cleaned_data.get("return_url")
            if return_url is not None and url_has_allowed_host_and_scheme(
                url=return_url, allowed_hosts=request.get_host()
            ):
                return redirect(return_url)
            return redirect(self.get_return_url(request, moved))

        return render(
            request,
            self.template_name,
            {
                "inventory": inventory,
                "form": form,
                "return_url": self.get_return_url(request, inventory),
            },
        )


class ReverseMoveView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = "dcim.add_device"
    template_name = "nautobot_move/reverse_install.html"

    def get(self, request, *args, pk=None, **kwargs):
        planned = Device.objects.get(pk=pk)
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        form = ReverseInstallForm(initial=initial_data)

        return render(
            request,
            self.template_name,
            {
                "planned": planned,
                "form": form,
                "return_url": self.get_return_url(request, planned),
            },
        )

    def post(self, request, *args, pk=None, **kwargs):
        planned = Device.objects.get(pk=pk)
        form = ReverseInstallForm(request.POST, request.FILES, instance=planned)

        if form.is_valid():
            moved = form.save()

            msg = 'Moved device <a href="{}">{}</a>'.format(
                moved.get_absolute_url(), escape(moved)
            )
            messages.success(request, mark_safe(msg))

            return_url = form.cleaned_data.get("return_url")
            if return_url is not None and url_has_allowed_host_and_scheme(
                url=return_url, allowed_hosts=request.get_host()
            ):
                return redirect(return_url)
            return redirect(self.get_return_url(request, moved))

        return render(
            request,
            self.template_name,
            {
                "planned": planned,
                "form": form,
                "return_url": self.get_return_url(request, planned),
            },
        )


class ReplaceView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = "dcim.add_device"
    template_name = "nautobot_move/replace.html"
    template_name_success = "nautobot_move/replace_success.html"

    def get(self, request, *args, pk=None, **kwargs):
        inventory = Device.objects.get(pk=pk)
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        form = ReplaceForm(initial=initial_data)

        return render(
            request,
            self.template_name,
            {
                "inventory": inventory,
                "form": form,
                "return_url": self.get_return_url(request, inventory),
            },
        )

    def post(self, request, *args, pk=None, **kwargs):
        inventory = Device.objects.get(pk=pk)
        form = ReplaceForm(request.POST, request.FILES, instance=inventory)

        if form.is_valid():
            inventory, failed, interface_lut, components_create = form.save()
            return render(
                request,
                self.template_name_success,
                {
                    "failed": failed,
                    "inventory": inventory,
                    "interface_lut": interface_lut,
                    "components_create": components_create,
                },
            )

        return render(
            request,
            self.template_name,
            {
                "inventory": inventory,
                "form": form,
                "return_url": self.get_return_url(request, inventory),
            },
        )


class ReverseReplaceView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = "dcim.add_device"
    template_name = "nautobot_move/reverse_replace.html"
    template_name_success = "nautobot_move/replace_success.html"

    def get(self, request, *args, pk=None, **kwargs):
        failed = Device.objects.get(pk=pk)
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        form = ReverseReplaceForm(initial=initial_data)

        return render(
            request,
            self.template_name,
            {
                "failed": failed,
                "form": form,
                "return_url": self.get_return_url(request, failed),
            },
        )

    def post(self, request, *args, pk=None, **kwargs):
        failed = Device.objects.get(pk=pk)
        form = ReverseReplaceForm(request.POST, request.FILES, instance=failed)

        if form.is_valid():
            inventory, failed, interface_lut, components_create = form.save()
            return render(
                request,
                self.template_name_success,
                {
                    "failed": failed,
                    "inventory": inventory,
                    "interface_lut": interface_lut,
                    "components_create": components_create,
                },
            )

        return render(
            request,
            self.template_name,
            {
                "inventory": inventory,
                "form": form,
                "return_url": self.get_return_url(request, failed),
            },
        )
