from __future__ import unicode_literals

from django.urls import path

from . import views

app_name = "nautobot_move"
urlpatterns = [
    path(r"install/<uuid:pk>/edit/", views.MoveView.as_view(), name="install"),
    path(r"reverse-install/<uuid:pk>/edit/", views.ReverseMoveView.as_view(), name="reverse_install"),
    path(r"replace/<uuid:pk>/edit/", views.ReplaceView.as_view(), name="replace"),
    path(r"reverse-replace/<uuid:pk>/edit/", views.ReverseReplaceView.as_view(), name="reverse_replace"),
]
