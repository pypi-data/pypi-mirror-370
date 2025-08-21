from django.conf import settings
from django.urls import include, path

from ag_grid import api

app_name = "ag-grid"

urlpatterns = [
    path("<str:app_label>/<str:model_name>/list-headers/", api.AgGridHeaderAPIView.as_view(), name="headers"),
    path("<str:app_label>/<str:model_name>/<int:pk>/update/", api.AgGridUpdateAPIView.as_view(), name="update"),
    path("<str:app_label>/<str:model_name>/<int:pk>/delete/", api.AgGridDeleteAPIView.as_view(), name="delete"),
    path("<str:app_label>/<str:model_name>/form-fields/", api.AgGridFormFieldsAPIView.as_view(), name="form-fields"),
    path("<str:app_label>/<str:model_name>/filtered-data-source/", api.AgGridFilteredListView.as_view(), name="filtered-data-source"),
    path("<str:app_label>/<str:model_name>/excel-export/", api.AgGridExcelExportAPIView.as_view(), name="list"),
    path(
        "<str:app_label>/<str:model_name>/foreign-options/<str:field_name>/",
        api.AgGridFormForeignKeyOptionsAPIView.as_view(),
        name="ag_grid_foreign_key_options"
    ),
    path(
        "<str:app_label>/<str:model_name>/form-create/",
        api.AgGridFormCreateAPIView.as_view(),
        name='ag_grid_form_create'
    ),
]

try:
    if "ag_grid.contrib.notification" in settings.INSTALLED_APPS:
        from ag_grid.contrib.notification import urls as notification_urls

        urlpatterns += [
            path("notifications/", include(notification_urls, namespace="notification")),
        ]
except ImportError:
    pass
