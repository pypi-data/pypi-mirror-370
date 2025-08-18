from django.urls import re_path

from enums.apiviews import RetrieveEnumAPIView

urlpatterns = (
    re_path(
        r"^api/v1/enums/(?P<enum_class_name>[0-9a-zA-Z\-]+)$",
        RetrieveEnumAPIView.as_view(),
        name="retrieve_enum",
    ),
)
