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
# SMALL_DIR = "/var/www/html/python/grammer_check/models/flan_t5_small"
SMALL_DIR = "/var/www/html/python/grammer_check/models/flan_t5_base"
# SMALL_DIR = "/var/www/html/python/grammer_check/models/mt5_base"
# SMALL_DIR = "/var/www/html/python/grammer_check/models/facebook_bart_base"

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


def install_packages():
    packages = ["transformers", "torch", "flask", "flask-restx", "pytz", "huggingface_hub"]
    for p in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])
            interface_ns.logger.info(f"Successfully installed: {p}")
        except subprocess.CalledProcessError:
            interface_ns.logger.info(f"Failed to install: {p}")






# -------------------- Grammar Correction with styles --------------------
def correct_grammar_with_style(text: str, style: str = "standard") -> str:
    tok, mdl = _load_small()

    style_prompts = {
        "standard": (
            f"Correct grammar, spelling, and punctuation without changing meaning:\n"
            f"Original: {text}\nCorrected:"
        ),
        "academic": (
            f"Correct grammar and rewrite in a formal, academic tone. "
            f"Ensure proper spelling, punctuation, and clarity:\n"
            f"Original: {text}\nCorrected:"
        ),
        "technical": (
            f"Correct grammar and rewrite in a precise, technical style. "
            f"Ensure formal tone and accurate terminology:\n"
            f"Original: {text}\nCorrected:"
        ),
    }

    prompt = style_prompts.get(style.lower(), style_prompts["standard"])

    with torch.no_grad():
        ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
        out = mdl.generate(
            ids,
            max_new_tokens=128,
            num_beams=4,
            do_sample=False,
            early_stopping=True,
        )

    result = tok.decode(out[0], skip_special_tokens=True).strip()

    del tok, mdl, ids, out
    cleanup_memory()
    return result

#######################################################################################################################
# -------------------- API Route --------------------
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
                return make_response(jsonify({
                    "error": f"Invalid style. Allowed: {sorted(list(allowed_styles))}"
                }), 400)

            corrected_text = correct_grammar_with_style(text, style)
            return jsonify({"corrected_text": corrected_text})

        except Exception as e:
            interface_ns.logger.exception(f"Exception in /grammar_check: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)





def paraphrase_text(text: str, style: str = "academic") -> str:
    tok, mdl = _load_small()  # flan-t5-small local dir
    style = style.lower()

    # ---- Few-shot prompt (forces rewording + tone) ----
    shots = {
        "academic": (
            "Rewrite the sentence in a formal, academic tone using different wording. "
            "Do NOT repeat 3-word phrases from the original. Keep the meaning the same.\n"
            "Original: The study shows people sleep less during the summer.\n"
            "Paraphrase: The findings indicate that individuals tend to obtain less sleep in the summer months.\n"
        ),
        "casual": (
            "Rewrite the sentence in a relaxed, conversational tone using different wording. "
            "Do NOT repeat 3-word phrases from the original. Keep the meaning the same.\n"
            "Original: The device malfunctioned during the demonstration.\n"
            "Paraphrase: The gadget messed up while we were showing it off.\n"
        ),
        "professional": (
            "Rewrite the sentence in a clear, concise, professional tone using different wording. "
            "Do NOT repeat 3-word phrases from the original. Keep the meaning the same.\n"
            "Original: We will try to resolve the issue as soon as possible.\n"
            "Paraphrase: We will address the issue promptly.\n"
        ),
        "shortened":    f"Paraphrase concisely without losing meaning: {text}",
        "expanded":     f"Paraphrase with a bit more detail and clarity: {text}",
    }
    prefix = shots.get(style, shots["academic"])
    prompt = f"{prefix}Original: {text}\nParaphrase:"

    def _generate(pmt, strong=False):
        with torch.no_grad():
            ids = tok(pmt, return_tensors="pt", truncation=True, max_length=256).input_ids
            out = mdl.generate(
                ids,
                max_new_tokens=64,
                # diversity / anti-copy
                no_repeat_ngram_size=3,
                encoder_no_repeat_ngram_size=3,   # <-- prevents copying source n-grams
                repetition_penalty=1.25,
                # decoding
                num_beams=4 if not strong else 6,
                do_sample=True,
                temperature=0.9 if not strong else 1.0,
                top_p=0.92,
                early_stopping=True,
            )
        return tok.decode(out[0], skip_special_tokens=True).strip()

    # First try
    result = _generate(prompt)

    # Simple similarity check; if too similar, retry stronger
    def _too_similar(a, b):
        a_set, b_set = set(a.lower().split()), set(b.lower().split())
        if not a_set or not b_set:
            return True
        jacc = len(a_set & b_set) / max(1, len(a_set | b_set))
        return jacc > 0.72  # tweakable threshold

    if _too_similar(result, text):
        result = _generate(prompt, strong=True)

    # trim any leading label
    for tag in ("Paraphrase:", "Paraphrase -", "Paraphrase —"):
        if result.startswith(tag):
            result = result[len(tag):].strip()

    del tok, mdl
    cleanup_memory()
    return result



#######################################################################################################################
@interface_ns.route('/paraphrase')
class ParaphraseText(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            input_text = data.get("text", "")
            style = data.get("style", "academic").lower()
            allowed = {"academic", "casual", "professional", "shortened", "expanded"}

            if not input_text:
                return make_response(jsonify({"error": "text is required"}), 400)
            if style not in allowed:
                return make_response(jsonify({"error": f"Invalid style. Allowed: {sorted(list(allowed))}"}), 400)

            paraphrased_text = paraphrase_text(input_text, style)
            return jsonify({"paraphrased_text": paraphrased_text})
        except Exception as e:
            interface_ns.logger.exception(f"Exception in /paraphrase: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)







#######################################################################################################################
def _too_similar(src: str, out: str, thresh: float = 0.72) -> bool:
    a, b = set(src.lower().split()), set(out.lower().split())
    if not a or not b:
        return True
    jacc = len(a & b) / max(1, len(a | b))
    return jacc > thresh

def _gen_text(tok, mdl, prompt, strong=False):
    with torch.no_grad():
        ids = tok(prompt, return_tensors="pt", truncation=True, max_length=256).input_ids
        out = mdl.generate(
            ids,
            max_new_tokens=96,
            no_repeat_ngram_size=3,
            encoder_no_repeat_ngram_size=3,
            repetition_penalty=1.25 if strong else 1.15,
            num_beams=8 if strong else 6,
            num_beam_groups=4 if strong else 3,
            diversity_penalty=0.35 if strong else 0.25,
            do_sample=False,  # must be False with group beam search
            early_stopping=True,
        )
    return tok.decode(out[0], skip_special_tokens=True).strip()


def ai_bypass(text: str, style: str = "standard") -> str:
    tok, mdl = _load_small()   # points to your chosen local model dir
    style = (style or "standard").lower()

    # Few-shot prompts (pushes the model to actually rewrite)
    style_map = {
        "standard": (
            f"Rewrite the following text so it completely avoids detection by AI detectors, "
            f"while keeping the meaning exactly the same. Use different structure, synonyms, and phrasing.\n"
            f"Text: {text}\nRewritten:"
        ),
        "advanced": (
            f"Rewrite the following text in a way that bypasses AI detection and appears entirely human-written. "
            f"Change sentence structure, reorder ideas, and replace words with synonyms while keeping meaning identical.\n"
            f"Text: {text}\nRewritten:"
        ),
        "creative": (
            f"Transform the following text so it bypasses AI detection while keeping the meaning the same. "
            f"Add subtle creative variations, figurative language, and unique expressions.\n"
            f"Text: {text}\nRewritten:"
        ),
    }
    prefix = style_map.get(style, style_map["standard"])
    prompt = f"{prefix}Original: {text}\nRewrite:"

    # First pass
    out1 = _gen_text(tok, mdl, prompt, strong=False)
    # Retry with stronger constraints if too similar
    out = out1 if not _too_similar(text, out1) else _gen_text(tok, mdl, prompt, strong=True)

    # Trim any leading label the model might echo
    for tag in ("Rewrite:", "Paraphrase:", "Rewritten:"):
        if out.lower().startswith(tag.lower()):
            out = out[len(tag):].strip()

    del tok, mdl
    cleanup_memory()
    return out

# -------- Route --------
@interface_ns.route('/aiBypass')
class AiBypass(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            text  = (data.get("text", "") or "").strip()
            style = (data.get("style", "standard") or "").strip().lower()

            allowed = {"standard", "advanced", "creative"}
            if not text:
                return make_response(jsonify({"error": "text is required"}), 400)
            if style not in allowed:
                return make_response(jsonify({"error": f"Invalid style. Allowed: {sorted(list(allowed))}"}), 400)

            result = ai_bypass(text, style)
            return jsonify({"aiBypass_text": result})
        except Exception as e:
            interface_ns.logger.exception(f"Exception in /aiBypass: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)