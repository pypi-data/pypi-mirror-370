import json

from django.conf import settings
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.db.models.query import QuerySet
from django.template import Library
from django.template.loader import get_template
from django.urls import NoReverseMatch

from djadmin_detail_view.defaults import EXCLUDE_BOOTSTRAP_TAGS

try:
    from moneyed import Money
except ImportError:
    Money = None

from ..url_helpers import admin_path_for

register = Library()


@register.simple_tag
def exclude_bootstrap_tags():
    return EXCLUDE_BOOTSTRAP_TAGS


@register.filter
def is_dict(value):
    return isinstance(value, dict)


# Check to add link for file fields
@register.simple_tag
def is_file_field(field_value):
    return isinstance(field_value, FieldFile)


@register.simple_tag
def is_link_field(field_value):
    return isinstance(field_value, str) and field_value.startswith("http")


# Check to add link to related models
@register.simple_tag
def is_model_field(field_value):
    return isinstance(field_value, Model)


@register.simple_tag
def get_obj_detail_url(obj):
    return f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}"


@register.simple_tag
def get_obj_classname(obj):
    if hasattr(obj, "display_name") and obj.display_name is not None:
        if callable(obj.display_name):
            return obj.display_name()

        return obj.display_name

    return obj._meta.verbose_name.title()


@register.filter
def is_partial(value):
    if isinstance(value, str) and value.count("/") > 1 and value.endswith(".html"):
        return True
    return False


@register.filter
def is_list(value):
    return isinstance(value, list)


@register.simple_tag
def is_production():
    return settings.IS_PRODUCTION


@register.simple_tag(name="admin_path_for")
def admin_get_path_url(obj, action="change"):
    return admin_path_for(obj, action)


@register.simple_tag
def admin_change_path(obj):
    return admin_path_for(obj)


class CustomEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if Money is not None and isinstance(obj, Money):
            return obj.amount
        return super().default(obj)


@register.filter(is_safe=True)
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize("json", object)
    return json.dumps(object, indent=4, cls=CustomEncoder)


@register.simple_tag
def check_simple_history(obj):
    try:
        admin_path_for(obj, "history")

        return True
    except NoReverseMatch:
        return False


@register.filter
def filter_none(list):
    return [item for item in list if item is not None]


@register.simple_tag(takes_context=True)
def include_dynamic_with(context, template_name, args_dict):
    # Get the template object
    template_obj = get_template(template_name)
    # Create a new context based on the current one, but also add the kwargs
    new_context = context.flatten()
    new_context.update(args_dict)
    # Render the template with the new context
    return template_obj.render(new_context)
