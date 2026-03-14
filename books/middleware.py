from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class AdminForceStaffLogoutMiddleware:
    """
    Logs out non-staff users who try to access the admin panel.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            user = request.user
            if user.is_authenticated and not user.is_staff:
                logout(request)
                return redirect(reverse('admin:login'))
        return self.get_response(request)


class SessionValidationMiddleware:
    """
    Validates that user's session still exists in UserLoginSession table.
    If admin deletes a session, user is automatically logged out on next request.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = [
            '/login/',
            '/register/',
            '/logout/',
            '/api/',
            '/admin/',  # Exclude entire admin section to avoid blocking login
            '/offline/',
        ]
    
    def __call__(self, request):
        # Check if user is authenticated and session should be validated
        if request.user.is_authenticated:
            # Skip validation for certain paths to avoid issues
            if not any(request.path.startswith(path) for path in self.excluded_paths):
                try:
                    from books.models import UserLoginSession
                    session_key = request.session.session_key
                    
                    if session_key:
                        # Check if UserLoginSession record still exists
                        session_exists = UserLoginSession.objects.filter(
                            user=request.user,
                            session_key=session_key
                        ).exists()
                        
                        if not session_exists:
                            # Session was deleted by admin, logout this user
                            logger.warning(
                                f"Session terminated for user {request.user.username} "
                                f"(session {session_key}). Logging out."
                            )
                            logout(request)
                            # Redirect to login without trying to add message
                            # (MessageMiddleware may not have processed yet)
                            return redirect('login')
                except Exception as e:
                    logger.error(f"Error in SessionValidationMiddleware: {e}", exc_info=True)
                    # Continue anyway to avoid breaking the app
        
        return self.get_response(request)
