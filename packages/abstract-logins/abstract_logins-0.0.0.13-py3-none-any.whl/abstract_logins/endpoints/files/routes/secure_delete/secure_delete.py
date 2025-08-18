# /flask_app/login_app/endpoints/files/secure_files.py
from ....imports import *
import glob
from flask import send_file
from abstract_ocr.functions import generate_file_id
from .utils import remove_from_user_dir
# Correct get_bp signature:  get_bp(name, *, url_prefix=None, static_folder=None)
secure_remove_bp, logger = get_bp(
    "secure_remove",
    __name__,
    url_prefix=URL_PREFIX,
    static_folder = STATIC_FOLDER
)
@secure_remove_bp.route("/remove", methods=["POST","GET"])
@login_required
def remove_file():
    initialize_call_log()
    request_data = extract_request_data(request)
    data = request_data.get('json')
    logger.info(data)
    username = request.user['username']
    data = request.get_json() or {}
    file_id = data.get('id')
    if not file_id:
        return get_json_call_response('no file id', 403)
    seatch_map = {'id':file_id}
    try:
        row = fetch_any_combo(
            column_names='*',
            table_name='uploads',
            search_map=seatch_map
            )
        if not row:
            return get_json_call_response('File not found.', 404)
        if len(row) == 1:
            row = row[0]
        uploader_id = row.get('uploader_id')
        if uploader_id.lower() != username.lower():
            return get_json_call_response(f'unauthorized user: {uploader_id}', 404)
        try:
            remove_from_user_dir(row)
            remove_any_combo(
                table_name='uploads',
                search_map=seatch_map
                )
            
            
            return get_json_call_response(True, 200)
        except Exception as e:
            return get_json_call_response(f"{e}", 401)
    except Exception as e:
        return get_json_call_response(f"SERVER ERROR: {e}", 500)
