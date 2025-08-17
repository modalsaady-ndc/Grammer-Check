from datetime import datetime
import logging
import pytz
import subprocess
import sys
import gc
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace
from logging.handlers import RotatingFileHandler
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, T5ForConditionalGeneration
import torch

# -------------------- Paths to local models (downloaded already) --------------------
GRAMMAR_DIR = "/var/www/html/python/grammer_check/models/grammarly_coedit"
PARA_DIR    = "/var/www/html/python/grammer_check/models/vamsi_paraphraser"

# Create Namespace
interface_ns = Namespace("/api/interface", description="A namespace for our Interface")

# Set up logging
log_handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=3)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]  - %(message)s')
log_handler.setFormatter(formatter)
interface_ns.logger = logging.getLogger("interface_ns")
interface_ns.logger.setLevel(logging.INFO)
interface_ns.logger.addHandler(log_handler)

# -------------------- Helpers --------------------
def cleanup_memory():
    """Free Python objects and (if present) GPU cache. Safe on CPU-only boxes."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# -------------------- Grammar Correction (load-on-demand, CPU) --------------------
def correct_grammar(input_text: str) -> str:
    # Load tokenizer & model from local dir on CPU only
    grammar_tokenizer = AutoTokenizer.from_pretrained(GRAMMAR_DIR)
    grammar_model = T5ForConditionalGeneration.from_pretrained(
        GRAMMAR_DIR,
        torch_dtype=torch.float32,            # keep RAM usage predictable
        device_map={"": "cpu"}                # force CPU
    )

    with torch.no_grad():
        input_ids = grammar_tokenizer(input_text, return_tensors="pt").input_ids
        outputs = grammar_model.generate(input_ids, max_length=256)

    text = grammar_tokenizer.decode(outputs[0], skip_special_tokens=True)

    # free memory
    del grammar_model, grammar_tokenizer, input_ids, outputs
    cleanup_memory()
    return text

# -------------------- Paraphrasing (load-on-demand, CPU) --------------------
def paraphrase_text(input_text: str, style: str = "Shortened") -> str:
    paraphrase_tokenizer = AutoTokenizer.from_pretrained(PARA_DIR)
    paraphrase_model = AutoModelForSeq2SeqLM.from_pretrained(
        PARA_DIR,
        torch_dtype=torch.float32,
        device_map={"": "cpu"}                # force CPU
    )

    prompt_templates = {
        "Shortened": f"paraphrase: {input_text}",
        "Expanded":  f"expand the sentence: {input_text}",
        "Academic":  f"paraphrase formally: {input_text}",
    }
    prompt = prompt_templates.get(style, f"paraphrase: {input_text}")

    with torch.no_grad():
        input_ids = paraphrase_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True).input_ids
        outputs = paraphrase_model.generate(
            input_ids,
            max_length=256,
            num_beams=5,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=1.2,
            top_k=50,
            top_p=0.95,
            early_stopping=True
        )

    text = paraphrase_tokenizer.decode(outputs[0], skip_special_tokens=True)

    # free memory
    del paraphrase_model, paraphrase_tokenizer, input_ids, outputs
    cleanup_memory()
    return text

# -------------------- Package Installation Route (optional) --------------------
def install_packages():
    packages = ["transformers", "torch", "flask", "flask-restx", "pytz", "huggingface_hub"]
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            interface_ns.logger.info(f"Successfully installed: {package}")
        except subprocess.CalledProcessError:
            interface_ns.logger.info(f"Failed to install: {package}")

# -------------------- Routes --------------------
@interface_ns.route('/grammar_check')
class GrammarCheck(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            input_text = data.get("text", "")
            if not input_text:
                return make_response(jsonify({"error": "text is required"}), 400)
            corrected_text = correct_grammar(input_text)
            return jsonify({"corrected_text": corrected_text})
        except Exception as e:
            interface_ns.logger.exception(f"Exception in /grammar_check: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)

@interface_ns.route('/paraphrase')
class ParaphraseText(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            input_text = data.get("text", "")
            style = data.get("style", "Shortened")
            if not input_text:
                return make_response(jsonify({"error": "text is required"}), 400)
            paraphrased_text = paraphrase_text(input_text, style)
            return jsonify({"paraphrased_text": paraphrased_text})
        except Exception as e:
            interface_ns.logger.exception(f"Exception in /paraphrase: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)

@interface_ns.route('/install_packages')
class InstallPackages(Resource):
    def post(self):
        try:
            install_packages()
            return jsonify({"message": "Packages installed successfully"})
        except Exception as e:
            interface_ns.logger.exception(f"Exception in /install_packages: {e}")
            return make_response(jsonify({"error": "Failed to install packages"}), 500)
