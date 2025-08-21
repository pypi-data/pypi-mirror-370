# xl_dashboard/templatetags/xl_dashboard_tags.py

from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.admin.sites import site as admin_site
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('xl_dashboard/xl_dashboard.html', takes_context=True)
def show_xl_dashboard(context, side_menu_list=None):
    """Рендерит элементы XL Dashboard.

    По умолчанию строит разделы на основании настроек ``XL_DASHBOARD``.
    Если передать ``side_menu_list`` (результат ``get_side_menu`` из jazzmin),
    то для каждой установленной в админке модели будет создан свой элемент в
    том же стиле, что и для настроек ``XL_DASHBOARD``.
    Вызывается в шаблоне как::

        {% load xl_dashboard_tags %}
        {% show_xl_dashboard %}               # из настроек
        {% show_xl_dashboard side_menu_list %}  # из списка приложений
    """
    sections: list[tuple[str, list[tuple[str, str]]]] = []
    actions = {}

    if side_menu_list is not None:
        # Формируем список секций из доступных приложений и моделей

        # Добавляем ссылку на главную страницу админки
        sections.append(('Dashboard', [('Dashboard', reverse('admin:index'))]))

        for app in side_menu_list:
            app_name = getattr(app, 'name', getattr(app, 'app_label', None))
            if app_name is None and isinstance(app, dict):
                app_name = app.get('name')

            models = getattr(app, 'models', None)
            if models is None and isinstance(app, dict):
                models = app.get('models', [])

            items = []
            for model in models or []:
                model_name = getattr(model, 'name', None)
                if model_name is None and isinstance(model, dict):
                    model_name = model.get('name')

                model_url = getattr(model, 'url', None)
                if model_url is None and isinstance(model, dict):
                    model_url = model.get('url')

                if model_url:
                    items.append((model_name, model_url))
                else:
                    items.append((model_name, '#'))

            sections.append((app_name, items))

        return {
            'sections': sections,
            'actions': actions,
            'request': context['request']
        }

    xl_dashboard = getattr(settings, 'XL_DASHBOARD', {})
    user = context['request'].user  # noqa

    actions = xl_dashboard.get('xl-actions', {})

    for section_name, models_map in xl_dashboard.items():
        if section_name == 'xl-actions':
            continue  # пропускаем экшены, они отдельно выводятся
        items = []
        for item_name, model_path in models_map.items():
            if isinstance(model_path, str):
                if model_path.startswith('/'):
                    # Если значение начинается с '/', считаем, что это готовая ссылка
                    admin_link = model_path
                    items.append((item_name, admin_link))
                    continue
                try:
                    # Пытаемся получить модель через apps.get_model
                    try:
                        model = apps.get_model(model_path)
                    except LookupError:
                        # Если не получилось – пробуем импортировать напрямую
                        module_path, class_name = model_path.rsplit('.', 1)
                        mod = __import__(module_path, fromlist=[class_name])
                        model = getattr(mod, class_name)
                    # Если модель не зарегистрирована в админке, генерировать URL не получится
                    if model not in admin_site._registry:  # noqa
                        raise Exception('Model not registered in admin')
                    admin_link = reverse(
                        f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist'  # noqa
                    )
                    items.append((item_name, admin_link))
                except Exception as e:  # noqa
                    # print(f"Ошибка для модели {model_path}: {e}")  # Лог ошибки
                    items.append((item_name, '#invalid-model-path'))
            else:
                items.append((item_name, '#unknown-type'))
        sections.append((section_name, items))

    return {
        'sections': sections,
        'actions': actions,
        'request': context['request']
    }
