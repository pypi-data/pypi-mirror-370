
# Example usage in a settings or share-view:
token = make_download_token("alice", "invoices/2025-06-01.pdf", expires_minutes=30)
link  = url_for("secure_files.download_with_token",
                token=token,
                _external=True)
