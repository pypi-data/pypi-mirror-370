# xl_dashboard/controllers.py
import asyncio

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseNotFound

try:
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.permissions import IsAuthenticated

    imported = True
except ImportError:
    imported = False

if imported:
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    async def action_view(request, action_name):
        """
        Ищет функцию (или корутину) в XL_DASHBOARD['xl-actions'] и вызывает её.
        """
        print(f"action_view called with action_name={action_name}")  # Лог
        user = request.user
        if not (user and user.is_staff):
            return HttpResponseForbidden('Access denied')

        actions = getattr(settings, 'XL_DASHBOARD', {}).get('xl-actions', {})
        action_func = actions.get(action_name)
        if not action_func or not callable(action_func):
            return HttpResponseNotFound('Action not found or not callable')

        # Вызываем экшен (учитывая, что он может быть async)
        if asyncio.iscoroutinefunction(action_func):
            return await action_func(request)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, action_func, request)
else:
    def action_view(request, action_name):
        return HttpResponseNotFound('DRF not installed')
