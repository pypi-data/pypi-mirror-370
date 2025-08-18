from .files import (
    secure_files_bp,
    secure_download_bp,
    secure_upload_bp,
    secure_limiter,
    secure_remove_bp,
    secure_env_bp,
    secure_register_bp
    )
from .settings import secure_settings_bp,secure_endpoints_bp
from .users import (
    secure_logout_bp,
    secure_login_bp,
    change_passwords_bp,
    secure_u_bp
    )

from .views import secure_views_bp
bp_list = [secure_logout_bp,
    secure_login_bp,
    change_passwords_bp,
    secure_u_bp,
    secure_files_bp,
    secure_download_bp,
    secure_upload_bp,
    secure_limiter,
    secure_remove_bp,
    secure_env_bp,
    secure_register_bp,
    secure_settings_bp,
    secure_endpoints_bp
    secure_views_bp]
