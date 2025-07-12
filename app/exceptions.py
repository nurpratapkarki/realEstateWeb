from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle 403 Forbidden errors
    if isinstance(exc, PermissionDenied):
        return Response(
            {'error': 'Authentication credentials were not provided.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Handle 401 Unauthorized
    if response is not None and response.status_code == 401:
        response.data = {
            'error': 'Authentication credentials were not provided.'
        }
    
    # Handle 403 Forbidden
    if response is not None and response.status_code == 403:
        response.data = {
            'error': 'You do not have permission to perform this action.'
        }
    
    return response
