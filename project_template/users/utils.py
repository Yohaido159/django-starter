from functools import wraps


def authenticated_users(func):
    """
    This decorator is used to abstract common authentication checking functionality
    out of permission checks. It determines which parameter is the request based on name.
    """
    is_object_permission = "has_object" in func.__name__

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        request = args[0]
        # use second parameter if object permission
        if is_object_permission:
            request = args[1]

        if not(request.user and request.user.is_authenticated):
            return False

        return func(*args, **kwargs)

    return func_wrapper


def allow_staff_or_superuser(func):
    """
    This decorator is used to abstract common is_staff and is_superuser functionality
    out of permission checks. It determines which parameter is the request based on name.
    """
    is_object_permission = "has_object" in func.__name__

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        request = args[0]
        # use second parameter if object permission
        if is_object_permission:
            request = args[1]

        if request.user.is_staff or request.user.is_superuser:
            return True

        return func(*args, **kwargs)

    return func_wrapper
