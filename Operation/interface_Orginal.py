from datetime import datetime
import logging
import pytz
import subprocess
import sys
import gc
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace
from logging.handlers import RotatingFileHandler
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Use ONE small model for both grammar and paraphrase
SMALL_DIR = "/var/www/html/python/grammer_check/models/flan_t5_small"
# SMALL_DIR = "/var/www/html/python/grammer_check/models/flan_t5_base"

interface_ns = Namespace("/api/interface", description="A namespace for our Interface")

log_handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=3)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]  - %(message)s')
log_handler.setFormatter(formatter)
interface_ns.logger = logging.getLogger("interface_ns")
interface_ns.logger.setLevel(logging.INFO)
interface_ns.logger.addHandler(log_handler)

def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# --- load-on-demand to keep RAM low (you can preload later if you want speed) ---
def _load_small():
    tok = AutoTokenizer.from_pretrained(SMALL_DIR)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(
        SMALL_DIR,
        torch_dtype=torch.float32,
        device_map={"": "cpu"},
    )
    mdl.eval()
    return tok, mdl

def correct_grammar(text: str) -> str:
    tok, mdl = _load_small()
    prompt = f"Correct the grammar: {text}"
    with torch.no_grad():
        ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
        out = mdl.generate(
            ids,
            max_new_tokens=64,
            num_beams=1,      # greedy for speed
            do_sample=False,
            early_stopping=True,
        )
    result = tok.decode(out[0], skip_special_tokens=True)
    del tok, mdl, ids, out
    cleanup_memory()
    return result

def paraphrase_text(text: str, style: str = "Shortened") -> str:
    tok, mdl = _load_small()
    style_map = {
        "Shortened": f"Paraphrase concisely: {text}",
        "Expanded":  f"Paraphrase with more detail: {text}",
        "Academic":  f"Paraphrase formally: {text}",
    }
    prompt = style_map.get(style, f"Paraphrase: {text}")
    with torch.no_grad():
        ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
        out = mdl.generate(
            ids,
            max_new_tokens=64,
            num_beams=1,
            do_sample=False,
            early_stopping=True,
        )
    result = tok.decode(out[0], skip_special_tokens=True)
    del tok, mdl, ids, out
    cleanup_memory()
    return result

def install_packages():
    packages = ["transformers", "torch", "flask", "flask-restx", "pytz", "huggingface_hub"]
    for p in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])
            interface_ns.logger.info(f"Successfully installed: {p}")
        except subprocess.CalledProcessError:
            interface_ns.logger.info(f"Failed to install: {p}")





@interface_ns.route('/grammar_check')
class GrammarCheck(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            text = data.get("text", "")
            if not text:
                return make_response(jsonify({"error": "text is required"}), 400)
            return jsonify({"corrected_text": correct_grammar(text)})
        except Exception as e:
            interface_ns.logger.exception(f"Exception in /grammar_check: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)



@interface_ns.route('/aiBypass')
class AiBypass(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            text = data.get("text", "")
            style = data.get("style", "standard").lower()

            if not text:
                return make_response(jsonify({"error": "text is required"}), 400)

            # Define prompt templates for aiBypass
            style_map = {
                "standard": f"Rewrite this text so it sounds natural and undetectable by AI detectors: {text}",
                "advanced": f"Rewrite this text with a high level of vocabulary and sentence complexity to avoid AI detection: {text}",
                "creative": f"Rewrite this text with a creative and human-like tone, making it harder for AI detection tools to classify: {text}"
            }

            if style not in style_map:
                return make_response(jsonify({
                    "error": f"Invalid style. Allowed: {list(style_map.keys())}"
                }), 400)

            prompt = style_map[style]

            # Load small model on demand (same as grammar/paraphrase)
            tok, mdl = _load_small()
            with torch.no_grad():
                ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
                out = mdl.generate(
                    ids,
                    max_new_tokens=128,
                    num_beams=1,
                    do_sample=False,
                    early_stopping=True,
                )
            result = tok.decode(out[0], skip_special_tokens=True)

            del tok, mdl, ids, out
            cleanup_memory()

            return jsonify({"aiBypass_text": result})

        except Exception as e:
            interface_ns.logger.exception(f"Exception in /aiBypass: {e}")
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
