from rest_framework import permissions


class IsAdminGroup(permissions.BasePermission):
    """
    Allow access only to users in the 'Admin' group.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.groups.filter(name="Admin").exists()
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
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # If user is in Admin or HR, allow all view-level access (list, create, etc.)
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # If user is in the Employee group, allow view-level (object checks happen below)
        if user.groups.filter(name="Employee").exists():
            return True

        # Otherwise, deny
        return False

    def has_object_permission(self, request, view, obj):
        # `obj` is an Employee instance here
        user = request.user

        # Admin and HR can do anything
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # Employee can only operate on their own Employee record
        if user.groups.filter(name="Employee").exists():
            # CORRECTION: obj is already an Employee, so `obj.user` is the related User
            return obj.user == user

        return False


# --------------------------------------------------------
# Next, analogous classes for Attendance and Performance
# --------------------------------------------------------

class IsAttendanceSelfOrHRorAdmin(permissions.BasePermission):
    """
    - Admin and HR users can view or edit any Attendance record.
    - An 'Employee' user can view or edit only Attendance records belonging to their own Employee instance.
    - All other users are denied.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin or HR may list/create attendance
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # Employee may list (object-level filtering occurs below)
        if user.groups.filter(name="Employee").exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # `obj` is an Attendance instance
        user = request.user

        # Admin and HR can do anything
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # Employee can only view/edit their own attendance
        if user.groups.filter(name="Employee").exists():
            # obj.employee.user is the User who owns this attendance
            return obj.employee.user == user

        return False


class IsPerformanceSelfOrHRorAdmin(permissions.BasePermission):
    """
    - Admin and HR users can view or edit any Performance record.
    - An 'Employee' user can view or edit only Performance records belonging to their own Employee instance.
    - All other users are denied.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin or HR may list/create performance
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # Employee may list (object-level filtering occurs below)
        if user.groups.filter(name="Employee").exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # `obj` is a Performance instance
        user = request.user

        # Admin and HR can do anything
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return True

        # Employee can only view/edit their own performance
        if user.groups.filter(name="Employee").exists():
            # obj.employee.user is the User who owns this performance entry
            return obj.employee.user == user

        return False
