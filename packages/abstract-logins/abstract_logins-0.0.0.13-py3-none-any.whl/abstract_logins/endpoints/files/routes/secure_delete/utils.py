# /flask_app/login_app/endpoints/files/secure_files.py
import glob,os, shutil, hashlib
from abstract_utilities import get_logFile
from abstract_ocr.functions import generate_file_id
from pathlib import Path
ABS_UPLOAD_ROOT = '/var/www/abstractendeavors/secure-files/uploads'
ABS_REMOVED_DIR = os.path.join(ABS_UPLOAD_ROOT,'removed')
logger = get_logFile('remove_utils')
def file_hash(path: str, block_size: int = 1 << 16) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            h.update(chunk)
    return h.hexdigest()
def get_file_attribs(row):
    file_path = get_file_path(row)
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    filename,ext = os.path.splitext(basename)
    return {"dirname":dirname,"basename":basename,"filename":filename,"ext":ext}

def get_user_removed_dir(row):
    uploader_id = row.get('uploader_id','all')
    USER_REMOVED_DIR = os.path.join(ABS_REMOVED_DIR,uploader_id)
    os.makedirs(USER_REMOVED_DIR,exist_ok=True)
    return USER_REMOVED_DIR

def get_removed_file_dir(row):
    file_attribs = get_file_attribs(row)
    filename = file_attribs.get('filename')
    user_removed_dir = get_user_removed_dir(row)
    removed_file_dir = os.path.join(user_removed_dir,filename)
    os.makedirs(removed_file_dir,exist_ok=True)
    return removed_file_dir

def remove_from_user_dir(row):
    src_path         = Path(get_file_path(row))
    removed_dir      = Path(get_removed_file_dir(row))
    removed_dir.mkdir(parents=True, exist_ok=True)

    if not src_path.exists():
        logger.warning("delete_from_user_dir: %s not found", src_path)
        return

    src_hash = file_hash(src_path)

    # 1) look for identical file already in trash
    for p in removed_dir.rglob("*"):            # recursive, skip symlinks if needed
        if p.is_file() and file_hash(p) == src_hash:
            logger.info("identical file already in %s → just unlinking %s", p, src_path)
            src_path.unlink()
            return

    # 2) need to move it — pick unique name
    stem, suffix = src_path.stem, src_path.suffix
    dest = removed_dir / (stem + suffix)
    i = 1
    while dest.exists():
        dest = removed_dir / f"{stem}-{i}{suffix}"
        i += 1

    logger.info("moving %s → %s", src_path, dest)
    shutil.move(src_path, dest)
        
def get_file_path(row):
    rel_path = row
    if isinstance(row,dict):
        rel_path = row.get('filepath')
    filepath = os.path.join(ABS_UPLOAD_ROOT,rel_path)
    return filepath
