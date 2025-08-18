from typing import *
from flask import Request
from ..user_queries.userManager import UserManager
from ..ip_queries.userIpManager import UserIPManager
def get_request_info(req: Optional[Request] = None, 
                    obj: Optional[Union[str, None]] = None, 
                    res_type: str = 'user') -> Optional[str]:
    """
    Retrieve information from a Flask request based on specified type.
    
    Args:
        req: Flask Request object
        obj: Fallback object (username or IP address)
        res_type: Type of response ('user' or 'ip_addr')
    
    Returns:
        Requested information (username or IP address) or None if not found
    
    Raises:
        ValueError: If invalid res_type is provided
    """
    if obj is not None:
        return obj
        
    if req is None:
        return None
        
    try:
        if res_type == 'user':
            if hasattr(req, 'user') and req.user and 'username' in req.user:
                return req.user['username']
            if req.remote_addr:
                return get_user_by_ip(req.remote_addr)
        elif res_type == 'ip_addr':
            return req.remote_addr
        else:
            raise ValueError(f"Invalid response type: {res_type}")
    except Exception:
        return None
    
    return None
def get_ip_addr(req=None,ip_addr=None):
    return get_request_info(req=req,
                         obj=ip_addr,
                         res_type='ip_addr')

def get_user_name(req=None,user_name=None):
    return get_request_info(req=req,
                         obj=user_name,
                         res_type='username')
def extract_request_data(
    req: Optional[Request] = None,
    res_type: str = 'all',
    user_manager: Optional[UserManager] = None,
    ip_manager: Optional[UserIPManager] = None
) -> Optional[Dict[str, Any]]:
    """
    Extract all available data from a Flask request, including user, IP, query params, 
    form data, JSON, files, headers, cookies, and more.

    Args:
        req: Flask Request object
        res_type: Type of data to extract ('all', 'user', 'user_id', 'ip_addr', 'query', 
                  'form', 'json', 'files', 'headers', 'cookies')
        user_manager: Optional UserManager instance for user data
        ip_manager: Optional UserIPManager instance for IP logging

    Returns:
        Dictionary containing requested data, or None if no data is available

    Raises:
        ValueError: If invalid res_type is provided
    """
    # Valid response types
    valid_types = {
        'all', 'user', 'user_id', 'ip_addr', 'query', 'form', 
        'json', 'files', 'headers', 'cookies'
    }

    # Validate res_type
    if res_type not in valid_types:
        raise ValueError(f"Invalid response type: {res_type}. Valid types: {valid_types}")

    # Return None if no request is provided
    if req is None:
        return None

    # Initialize managers
    user_manager = user_manager or UserManager()
    ip_manager = ip_manager or UserIPManager()

    # Initialize result dictionary
    result: Dict[str, Any] = {}

    try:
        # Extract user and user_id
        if res_type in ('all', 'user', 'user_id'):
            if hasattr(req, 'user') and req.user and 'username' in req.user:
                result['user'] = req.user['username']
                if 'id' in req.user:
                    result['user_id'] = req.user['id']
            elif req.remote_addr:
                users = ip_manager.get_user_by_ip(req.remote_addr)
                if users and isinstance(users, list) and len(users) > 0:
                    user = users[0]
                    if 'username' in user:
                        result['user'] = user['username']
                    if 'id' in user:
                        result['user_id'] = user['id']

        # Extract and log IP address
        if res_type in ('all', 'ip_addr'):
            if req.remote_addr:
                result['ip_addr'] = req.remote_addr
                # Log IP if user_id is available
                if 'user_id' in result:
                    ip_manager.log_user_ip(result['user_id'], req.remote_addr)

        # Extract query parameters
        if res_type in ('all', 'query'):
            if req.args:
                result['query'] = dict(req.args)

        # Extract form data
        if res_type in ('all', 'form'):
            if req.form:
                result['form'] = dict(req.form)

        # Extract JSON data
        if res_type in ('all', 'json'):
            try:
                if req.is_json:
                    result['json'] = req.get_json(silent=True) or {}
            except Exception:
                result['json'] = {}

        # Extract files
        if res_type in ('all', 'files'):
            if req.files:
                result['files'] = {
                    key: {
                        'filename': file.filename,
                        'content_type': file.content_type,
                        'size': file.content_length or 0
                    } for key, file in req.files.items()
                }

        # Extract headers
        if res_type in ('all', 'headers'):
            result['headers'] = dict(req.headers)

        # Extract cookies
        if res_type in ('all', 'cookies'):
            if req.cookies:
                result['cookies'] = dict(req.cookies)

        # Add request metadata
        if res_type == 'all':
            result['method'] = req.method
            result['url'] = req.url
            result['path'] = req.path
            result['host'] = req.host

        # Return specific type if requested
        if res_type != 'all':
            return result.get(res_type)

        return result if result else None

    except Exception as e:
        print(f"Error in extract_request_data: {e}")
        return None
