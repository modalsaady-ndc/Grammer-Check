from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="google/flan-t5-base",
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/flan_t5_base",
    local_dir_use_symlinks=False,  # Store actual files, not symlinks
    # resume_download=True           # Continue from last partial download
    force_download=True
)
