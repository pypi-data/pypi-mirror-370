# xldashboard

> Sometimes I use this in different projects, so I decided to put it on pypi

`xldashboard` is a more beautiful/customizable admin dashboard for Django.
- [Images](#images)
- [Installation](#installation-%EF%B8%8F)
- [Settings](#settings-%EF%B8%8F)

## Images
![](docs/img/1.png)
![](docs/img/2.png)
![](docs/img/3.png)

## Installation 🛠️

```bash
pip install xldashboard
```

## Settings ⚙️
### Customize jazzmin.py (or just copy it)
```python
# jazzmin.py

JAZZMIN_SETTINGS = {
    # Заголовки и логотипы# Headlines and logos
    'site_title': 'xlartas',
    'site_header': 'xlartas',
    'site_brand': 'xlartas',
    'site_logo': '/img/icon/logo.png',  # Link to logo
    'site_logo_classes': '',
    'site_icon': '/img/icon/logo.png',  # Link to Favicon (32x32 PX)

    # Logo on the entrance page
    "login_logo": '/img/icon/logo.png',
    "login_logo_dark": '/img/icon/logo.png',

    # Text on the entrance screen
    "welcome_sign": "",

    # Copyright on the footer
    "copyright": "xlartas © 2025",

    ############
    # Side menu
    ############
    "show_sidebar": True,
    "navigation_expanded": True, # Default menu is deployed
    "hide_apps": [],  # You can hide unnecessary applications
    "hide_models": [],  # Hiding unnecessary models
    "order_with_respect_to": [
        "core",
    ],

    # Custom links in the side menu
    # "custom_links": {

    # },
    "user_avatar": 'avatar',

    #################
    # Modal windows for related objects
    #################
    "related_modal_active": True,

    ###############
    # CSS and js files
    ###############
    "custom_css": "/admin/css/jazzmin.css",  # Path to CSS User
    "custom_js": "/admin/js/jazzmin.js", # Path to User JS

    ###############
    # Dark theme and interface settings
    ###############
    "theme": "darkly", # The main topic (Dark by default)
    "dark_mode_theme": "darkly",  # The topic for the dark mode

    # Turning on the color switch and UI configurator
    # "show_ui_builder": True,

    ####################
    # Additional interface settings
    ####################
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-lightblue",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": True,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,

    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },

    "actions_sticky_top": True,
}

# Additional settings for user topics, flowers and customization
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",  # The Dark Topic by default
    "dark_mode_theme": "darkly", # The topic for the dark mode
    "navbar": "navbar-dark",  # Navigation panel color
    "accent": "accent-lightblue",  # Basic accent color
    "navbar_small_text": False,  # Regular text on the navigation panel
    "sidebar": "sidebar-dark-indigo",  # Dark side panel
    "sidebar_nav_small_text": False,  # Normal text in the side menu
    "sidebar_disable_expand": True,  # Shutdown of menu turning
    "sidebar_nav_child_indent": False,  # Without indentation for nested elements
    "sidebar_nav_compact_style": True,  # Compact navigation style
    "footer_fixed": False,  # Disconnection of a fixed footer
    "navbar_fixed": True,  # Fixed navigation panel
    "actions_sticky_top": True,  # Fixation of actions in the upper part of the page
}
```

### In `settings.py`

```python
# settings.py
from .jazzmin import JAZZMIN_SETTINGS as _JAZZMIN_SETTINGS

INSTALLED_APPS = [
    # ...
    'xldashboard',
]

# xl-dashboard
XL_DASHBOARD = {
    'General': {
        'Users': 'app.User',
    },
    'And some tab again': {
        'Product': 'shop_app.ProductModel',
    },
    ...
}

# Jazzmin
JAZZMIN_SETTINGS = _JAZZMIN_SETTINGS | {
    'usermenu_links': [
        {'name': 'Site', 'url': f'https://...', 'new_window': True},
        {'name': 'Logs', 'url': f'https://...', 'new_window': True},
    ],
}
```
