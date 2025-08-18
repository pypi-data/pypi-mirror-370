from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from enums.framework.registry import SystemEnumRegistry


class RetrieveEnumAPIView(APIView):
    authentication_classes = []  # Add authentication classes if needed
    permission_classes = [AllowAny]  # Add permission classes if needed

    @staticmethod
    def get_enum_representation(enum_class_name):
        registry = SystemEnumRegistry()
        enum_class = registry.get_enum_class(class_name=enum_class_name)
        if enum_class is None:
            return []

        return enum_class.get_full_representation()

    def get(self, request, *args, **kwargs):
        enum_class_name = kwargs.get("enum_class_name")
        data = self.get_enum_representation(enum_class_name=enum_class_name)
        return Response(data=data, status=status.HTTP_200_OK)
