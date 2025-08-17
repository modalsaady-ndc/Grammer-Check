from huggingface_hub import snapshot_download

# Download grammarly/coedit-large
snapshot_download(
    repo_id="grammarly/coedit-large",
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/grammarly_coedit",
    local_dir_use_symlinks=False
)

# Download Vamsi/T5_Paraphrase_Paws
snapshot_download(
    repo_id="Vamsi/T5_Paraphrase_Paws",
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/vamsi_paraphraser",
    local_dir_use_symlinks=False
)
