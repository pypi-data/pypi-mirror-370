import os,jwt,logging
from abstract_utilities.time_utils import *
from pathlib import Path
from abstract_security import get_env_value
from functools import wraps
from .functions.routes import (
    verify_password,
    ensure_users_table_exists
)
from .functions.auth_utils.user_store.table_utils.users_utils import (
    get_existing_users,
    get_user,
    add_or_update_user
    )
from flask import has_request_context
from .functions.auth_utils.query_utils import *
from .functions import *
from abstract_flask import (CORS,
                            get_request_data,
                            Flask,
                            redirect,
                            request,
                            jsonify,
                            get_bp,
                            get_request_data,
                            initialize_call_log,
                            get_json_call_response,
                            send_from_directory,
                            abort,
                            secure_filename,
                            send_from_directory,
                            parse_and_spec_vars,
                            addHandler,
                            get_request_info,
                            get_ip_addr,
                            get_user_name,
                            get_user_filename,
                            get_safe_subdir,
                            get_subdir,
                            get_request_safe_filename,
                            get_request_filename,
                            get_request_file,
                            get_request_files
                            )
from .paths import *
from .query_utils import *
from abstract_database import insert_any_combo,update_any_combo,fetch_any_combo,remove_any_combo
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

