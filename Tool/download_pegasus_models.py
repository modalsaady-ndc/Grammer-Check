# one-time download
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="tuner007/pegasus_paraphrase",
    repo_type="model",
    local_dir="/var/www/html/python/grammer_check/models/pegasus_paraphrase",
    local_dir_use_symlinks=False,
)

# loader
from transformers import PegasusTokenizer, PegasusForConditionalGeneration