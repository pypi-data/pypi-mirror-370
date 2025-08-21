from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from django.contrib.auth import get_user_model


class ActionPermission(BasePermission):
    """
    DjangoActionPermissions

    Given an action and a request checks if the user has the permission to access
    the action. It is completely dependable on django auth package and the way it handles permissions. The core part of this class is a permission mapper which maps the requested action to the corresponding permission with specific codename.
    The default mapping is as follow and could be overwritten:

    list: list_(model_name)
    retrieve: view_(model_name)
    create: add_(model_name)
    destroy: delete_(model_name)
    update: change_(model_name)
    partial_update: change_(model_name)

    Note that all permissions is created by Django's auth pacakge except list_(model_name), which should be created automatically for every model after it's migration.
    """

    # A mapping from ModelViewSet actions to permissions' codenames.
    perms_map = {
        "list": "%(app_label)s.list_%(model_name)s",
        "retrieve": "%(app_label)s.view_%(model_name)s",
        "create": "%(app_label)s.add_%(model_name)s",
        "destroy": "%(app_label)s.delete_%(model_name)s",
        "update": "%(app_label)s.change_%(model_name)s",
        "partial_update": "%(app_label)s.change_%(model_name)s",
    }

    def _get_queryset(self, view_set):
        assert (
            hasattr(view_set, "get_queryset")
            or getattr(view_set, "queryset", None) is not None
        ), (
            "Cannot apply {} on a view that does not set "
            "`.queryset` or have a `.get_queryset()` method."
        ).format(
            self.__class__.__name__
        )

        if hasattr(view_set, "get_queryset"):
            queryset = view_set.get_queryset()
            assert queryset is not None, "{}.get_queryset() returned None".format(
                view_set.__class__.__name__
            )
            return queryset
        return view_set.queryset

    def _get_anonymous_user(self):
        return get_user_model().objects.get(id=1)

    def _get_user(self, request: Request):
        if not request.user.is_authenticated:
            return get_user_model().objects.get(id=1)
        else:
            return request.user

    def check_model_permission(self, request: Request, view_set):
        """
        has_permission

        Check if the user has permission for the requested action.

        Parameters
        ----------
        request : Request
            User's request.
        view_set : ViewSet
            Requestd viewset.

        Returns
        -------
        bool
            True if user has the permission for the given action else False.
        """
        if request.user.is_superuser:
            return True

        user = self._get_user(request)

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view_set, "_ignore_model_permissions", False):
            return True

        query_set = self._get_queryset(view_set)
        permission = self.perms_map[view_set.action] % {
            "app_label": query_set.model._meta.app_label,
            "model_name": query_set.model._meta.model_name,
        }

        return user.has_perm(permission) or self._get_anonymous_user().has_perm(
            permission
        )

    def check_object_permission(self, request: Request, view_set: ViewSet):
        if not hasattr(view_set, "{}_object_permission".format(view_set.action)):
            return False
        pf = getattr(view_set, "{}_object_permission".format(view_set.action))
        return pf(request)

    def has_permission(self, request: Request, view_set: ViewSet):
        if request.method == "OPTIONS":
            return True

        if self.check_object_permission(request, view_set):
            return True
        return self.check_model_permission(request, view_set)
