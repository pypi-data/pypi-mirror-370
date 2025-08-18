import importlib
from django_enums import settings
from enums.utils.logging import logger


class SystemEnumRegistry:
    @classmethod
    def _get_base_list_of_enums(cls):
        base_enums = []
        try:
            base_enums = settings.STANDARD_ENUM_REGISTRY
        except Exception as e:
            logger.warning(
                f"Exception occurred while trying to get base list of Enums - {str(e)}"
            )
        return base_enums

    def get_all_list_of_enums(self):
        return self._get_base_list_of_enums()

    @classmethod
    def import_and_get_class(cls, class_path_string):
        try:
            full_class_path = class_path_string.split(".")
            class_name = full_class_path[-1]
            class_path = ".".join(full_class_path[:-1])
            module_containing_class = importlib.import_module(name=class_path)
            task_class = getattr(module_containing_class, class_name)
            return task_class
        except Exception as e:
            logger.warning(
                f"Exception occurred while trying to import and get class - {str(e)}"
            )
            return None

    def get_enum_class(self, class_name):
        all_enum_classes, class_path = self.get_all_list_of_enums(), None
        for enum_class_path in all_enum_classes:
            class_name_in_enum = enum_class_path.split(".")[-1]
            if class_name_in_enum == class_name:
                class_path = enum_class_path
                break
        if not class_path:
            return None

        return self.import_and_get_class(class_path_string=class_path)
