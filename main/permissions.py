from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    message = "Only the owner can create/delete; Editors may update experience."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
