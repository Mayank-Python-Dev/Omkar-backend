"""
ASGI config for OmkarProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omkar_proj.settings")

django_asgi_app = get_asgi_application()

from superadmin.consumers import (
    DashboardConsumer,
    # PracticeConsumer
)


application= ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket':AuthMiddlewareStack(
        URLRouter([
            # path('ws/communicate/<room_code>',CommunicationConsumer.as_asgi()), 
            path("ws/room/<room_code>",DashboardConsumer.as_asgi()),
        ]
        )
    ),
})