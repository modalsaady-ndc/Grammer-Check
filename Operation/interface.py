from datetime import datetime
import logging
import pytz
import subprocess
import sys
import gc
import os
import re
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace
from logging.handlers import RotatingFileHandler
from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    MT5Tokenizer, MT5ForConditionalGeneration,
    BartTokenizer, BartForConditionalGeneration
)
import torch

# --- Local model paths ---
EN_BART_DIR = "/var/www/html/python/grammer_check/models/facebook_bart_base"
EN_FLAN_DIR = "/var/www/html/python/grammer_check/models/flan_t5_base"
EN_FALLBACK = "/var/www/html/python/grammer_check/models/flan_t5_small"
AR_MT5_DIR  = "/var/www/html/python/grammer_check/models/mt5_base"

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

def install_packages():
    packages = ["transformers", "torch", "flask", "flask-restx", "pytz", "huggingface_hub"]
    for p in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])
            interface_ns.logger.info(f"Successfully installed: {p}")
        except subprocess.CalledProcessError:
            interface_ns.logger.info(f"Failed to install: {p}")

# --- Language detection ---
def is_arabic(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))

# --- Model loaders ---
def _load_english():
    if os.path.exists(os.path.join(EN_BART_DIR, "pytorch_model.bin")) or os.path.exists(os.path.join(EN_BART_DIR, "model.safetensors")):
        tok = BartTokenizer.from_pretrained(EN_BART_DIR)
        mdl = BartForConditionalGeneration.from_pretrained(EN_BART_DIR, torch_dtype=torch.float32, device_map={"": "cpu"})
    elif os.path.exists(os.path.join(EN_FLAN_DIR, "pytorch_model.bin")) or os.path.exists(os.path.join(EN_FLAN_DIR, "model.safetensors")):
        tok = AutoTokenizer.from_pretrained(EN_FLAN_DIR)
        mdl = AutoModelForSeq2SeqLM.from_pretrained(EN_FLAN_DIR, torch_dtype=torch.float32, device_map={"": "cpu"})
    else:
        tok = AutoTokenizer.from_pretrained(EN_FALLBACK)
        mdl = AutoModelForSeq2SeqLM.from_pretrained(EN_FALLBACK, torch_dtype=torch.float32, device_map={"": "cpu"})
    mdl.eval()
    return tok, mdl

def _load_arabic():
    tok = MT5Tokenizer.from_pretrained(AR_MT5_DIR)
    mdl = MT5ForConditionalGeneration.from_pretrained(AR_MT5_DIR, torch_dtype=torch.float32, device_map={"": "cpu"})
    mdl.eval()
    return tok, mdl

# -------------------- Grammar Correction with styles (Arabic + English) --------------------
def correct_grammar_with_style(text: str, style: str = "standard") -> str:
    text = (text or "").strip()
    style = (style or "standard").strip().lower()

    if is_arabic(text):
        # --- Arabic via mT5 ---
        tok, mdl = _load_arabic()  # your loader that returns MT5Tokenizer + MT5ForConditionalGeneration

        # Block T5 “sentinel” tokens like <extra_id_0>, <extra_id_1>, …
        sentinel_ids = []
        for i in range(100):  # mT5 supports many sentinel tokens; 100 is safe
            tok_id = tok.convert_tokens_to_ids(f"<extra_id_{i}>")
            if tok_id is not None and tok_id != tok.unk_token_id:
                sentinel_ids.append([tok_id])

        prompts = {
            "standard": (
                "صحح الأخطاء النحوية والإملائية وعلامات الترقيم في الجملة التالية "
                "مع الحفاظ على نفس المعنى. اكتب الجملة المصححة فقط دون أي شروح أو رموز خاصة:\n"
                f"{text}\n"
                "النص المصحح:"
            ),
            "academic": (
                "صحح الأخطاء وأعد صياغة الجملة بأسلوب أكاديمي رسمي وواضح، "
                "ثم اكتب الجملة المصححة فقط دون أي شروح أو رموز خاصة:\n"
                f"{text}\n"
                "النص المصحح:"
            ),
            "technical": (
                "صحح الأخطاء وأعد صياغة الجملة بأسلوب تقني دقيق مع مصطلحات مناسبة، "
                "ثم اكتب الجملة المصححة فقط دون أي شروح أو رموز خاصة:\n"
                f"{text}\n"
                "النص المصحح:"
            ),
        }
        prompt = prompts.get(style, prompts["standard"])

        with torch.no_grad():
            ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
            out = mdl.generate(
                ids,
                max_new_tokens=96,
                min_new_tokens=12,                 # nudge it to produce a full sentence
                num_beams=6,
                do_sample=False,
                no_repeat_ngram_size=3,
                bad_words_ids=sentinel_ids,        # <-- forbid <extra_id_*>
                early_stopping=True,
            )
        result = tok.decode(out[0], skip_special_tokens=True).strip()

        # Trim label if echoed
        if result.startswith("النص المصحح:"):
            result = result[len("النص المصحح:"):].strip()

        del tok, mdl, ids, out
        cleanup_memory()
        return result

    else:
        # --- Your existing English path (unchanged) ---
        tok, mdl = _load_english()
        prompts = {
            "standard":  f"Correct grammar, spelling, and punctuation. Keep the same meaning.\nOriginal: {text}\nCorrected:",
            "academic":  f"Correct grammar and rewrite in a formal, academic tone. Keep meaning.\nOriginal: {text}\nCorrected:",
            "technical": f"Correct grammar and rewrite in a precise, technical style. Keep meaning.\nOriginal: {text}\nCorrected:",
        }
        prompt = prompts.get(style, prompts["standard"])

        with torch.no_grad():
            ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
            out = mdl.generate(
                ids,
                max_new_tokens=96,
                num_beams=6,
                do_sample=False,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        result = tok.decode(out[0], skip_special_tokens=True).strip()
        if result.startswith("Corrected:"):
            result = result[len("Corrected:"):].strip()

        del tok, mdl, ids, out
        cleanup_memory()
        return result


# -------------------- Grammar Check Route --------------------
@interface_ns.route('/grammar_check')
class GrammarCheck(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            text = data.get("text", "")
            style = (data.get("style", "standard") or "").strip().lower()

            allowed_styles = {"standard", "academic", "technical"}
            if not text:
                return make_response(jsonify({"error": "text is required"}), 400)
            if style not in allowed_styles:
                return make_response(jsonify({"error": f"Invalid style. Allowed: {sorted(list(allowed_styles))}"}), 400)

            corrected_text = correct_grammar_with_style(text, style)
            return jsonify({"corrected_text": corrected_text})

        except Exception as e:
            interface_ns.logger.exception(f"Exception in /grammar_check: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)
