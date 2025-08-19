from django.apps import apps
from django.urls import reverse
from django.utils.html import format_html

# Attempt to use hosts_reverse first.
try:
    from django_hosts.resolvers import reverse as hosts_reverse

    HOST_NAME_FOR_ADMIN = "internal"
except ImportError:
    hosts_reverse = None


def admin_filtered_list_path_for(obj, **kwargs):
    path = admin_path_for(obj, action="changelist")

    filter_str = "&".join([f"{k}={v}" for k, v in kwargs.items()])

    return f"{path}?{filter_str}"


def auto_link(obj, action, text=None, html_class=None):
    admin_path = admin_path_for(obj, action)

    if text is None:
        text = obj

    if html_class:
        return format_html('<a href="{}" class="{}">{}</a>', admin_path, html_class, text)

    return format_html('<a href="{}">{}</a>', admin_path, text)


def admin_path_for(obj, action="change", site_name="admin"):
    # Allow for passing of "application.model" strings
    if isinstance(obj, str):
        obj = _class_from_str(obj)

        # If we're here, there's no change, model only
        if action == "change":
            action = "changelist"

    if action in ["add", "changelist", "search"]:
        return reverse(f"{site_name}:{admin_path_name(obj, action=action)}")

    return reverse(f"{site_name}:{admin_path_name(obj, action=action)}", args=[obj.id])


def admin_url_for(obj, action="change", site_name="admin"):
    if hosts_reverse is None:
        if action in ["add", "changelist"]:
            return reverse(f"{site_name}:{admin_path_name(obj, action=action)}")

        return reverse(f"{site_name}:{admin_path_name(obj, action=action)}", args=[obj.id])

    else:
        if action in ["add", "changelist"]:
            return hosts_reverse(
                f"{site_name}:{admin_path_name(obj, action=action)}",
                host=HOST_NAME_FOR_ADMIN,
                scheme="https",
            )

        return hosts_reverse(
            f"{site_name}:{admin_path_name(obj, action=action)}",
            args=[obj.id],
            host=HOST_NAME_FOR_ADMIN,
            scheme="https",
        )


def admin_path_name(klass, action="change"):
    if isinstance(klass, str):
        klass = _class_from_str(klass)

    return f"{klass._meta.app_label}_{klass._meta.model_name}_{action}"


def _class_from_str(obj):
    app_label, model_name = obj.split(".")
    return apps.get_model(app_label, model_name)
