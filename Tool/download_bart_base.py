from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="facebook/bart-base",
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/facebook_bart_base",
    local_dir_use_symlinks=False,
    resume_download=True  # Continue if interrupted
)
