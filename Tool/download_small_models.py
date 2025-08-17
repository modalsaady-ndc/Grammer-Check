from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="google/flan-t5-small",
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/flan_t5_small",
    local_dir_use_symlinks=False,
)

# Optional if you want separate t5-small for paraphrase; otherwise reuse flan-t5-small
# snapshot_download(
#     repo_id="google-t5/t5-small",
#     repo_type="model",
#     local_dir="/var/www/html/python/grammer_check/models/t5_small",
#     local_dir_use_symlinks=False,
# )






