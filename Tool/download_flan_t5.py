from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="google/mt5-base",  # you can also use "google/mt5-large"
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/mt5_base",
    local_dir_use_symlinks=False,
    resume_download=True
)
