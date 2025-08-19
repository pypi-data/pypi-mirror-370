from django.contrib import admin
from django.urls import path
from django.utils.html import format_html

from .url_helpers import admin_path_for, admin_path_name


class AdminChangeListViewDetail:
    default_detail_view = None

    def get_default_detail_view(self):
        if self.default_detail_view:
            return self.default_detail_view

        raise ValueError("Please define default_detail_view. Recommended: override `get_default_detail_view` method.")

    def get_urls(self):
        default_urls = super().get_urls()

        urls = self._remove_default_detail_redirect(default_urls)
        urls = self._add_default_detail(urls)

        return urls

    def _remove_default_detail_redirect(self, urls):
        cleaned_urls = [
            url
            for url in urls
            if not (url.name is None and url.lookup_str == "django.views.generic.base.RedirectView")
        ]
        return cleaned_urls

    def _add_default_detail(self, urls):
        detail_view = self.get_default_detail_view()

        detail_path = path(
            f"<{detail_view.pk_url_kwarg}>/",
            self.admin_site.admin_view(detail_view.as_view(admin_obj=self)),
            name=admin_path_name(detail_view.model, "detail"),
        )

        return urls + [detail_path]

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        list_display_list = list(list_display)

        if "view_details" in list_display_list:
            list_display_list.remove("view_details")

        list_display_list.insert(1, "view_details")

        return tuple(list_display_list)

    @admin.display(description="View Details")
    def view_details(self, obj):
        url = admin_path_for(obj, action="detail")
        return format_html('<a href="{}">View</a>', url)


class AdminDetailMixin:
    template_name = "admin/djadmin_components/auto_layout_detail.html"
    admin_obj = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(request, *args, object=self.object, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        admin_base_context = dict(
            # This will make the left side bar navigation appear with all controls.
            self.admin_obj.admin_site.each_context(request),
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            title=self.object,
            original=self.object,
            has_view_permission=self.admin_obj.has_view_permission(request, self.object),
        )
        return context | admin_base_context
