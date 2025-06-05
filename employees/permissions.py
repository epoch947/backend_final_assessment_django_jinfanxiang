from rest_framework import permissions


class IsAdminGroup(permissions.BasePermission):
    """
    Allow access only to users in the 'Admin' group.
    """

    def has_permission(self, request, view):
        user = request.user
        # Check if user is authenticated and belongs to 'Admin' group
        return (
            user and user.is_authenticated and user.groups.filter(name="Admin").exists()
        )


class IsHRGroup(permissions.BasePermission):
    """
    Allow access only to users in the 'HR' group.
    """

    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.groups.filter(name="HR").exists()


class IsEmployeeSelfOrHRorAdmin(permissions.BasePermission):
    """
    - Admin and HR users can view or edit any Employee record.
    - An 'Employee' user can view or edit only their own Employee instance.
    - All other users are denied.
    """

    def has_permission(self, request, view):
        # This method checks permission at the view level (before .has_object_permission).
        # We'll allow any authenticated user who is in one of the three groups to proceed.
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # If user is in Admin or HR, allow list/create
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # If user is in the Employee group, they only get object‐level permission (handled below)
        if user.groups.filter(name="Employee").exists():
            return True

        # Otherwise, disallow
        return False

    def has_object_permission(self, request, view, obj):
        # obj is an Employee instance
        user = request.user

        # Admin and HR can do anything
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # An Employee user can only operate on their own Employee record
        if user.groups.filter(name="Employee").exists():
            # obj.user is the User linked to obj (Employee instance)
            return obj.user == user

        return False
