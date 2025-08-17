from datetime import datetime
import logging
import pytz
import subprocess
import sys
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace
from logging.handlers import RotatingFileHandler
from transformers import AutoTokenizer, T5ForConditionalGeneration
from unsloth import FastLanguageModel


# Create Namespace
interface_ns = Namespace("/api/interface", description="A namespace for our Interface")

# Set up logging
log_handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=3)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]  - %(message)s')
log_handler.setFormatter(formatter)
interface_ns.logger = logging.getLogger("interface_ns")
interface_ns.logger.setLevel(logging.INFO)
interface_ns.logger.addHandler(log_handler)

# Load Grammar Model
tokenizer = AutoTokenizer.from_pretrained("grammarly/coedit-large")
model = T5ForConditionalGeneration.from_pretrained("grammarly/coedit-large")

def correct_grammar(input_text):
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_length=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def install_packages():
    packages = [
        "unsloth", "transformers", "ipywidgets", "ipython", "torch",
        "flask", "pycloudflared", "unsloth"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            interface_ns.logger.info(f"Successfully installed: {package}")
        except subprocess.CalledProcessError:
            interface_ns.logger.info(f"Failed to install: {package}")
    
    # Install Unsloth from GitHub
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--no-deps", "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"])
        interface_ns.logger.info("Successfully installed: unsloth from GitHub")
    except subprocess.CalledProcessError:
        interface_ns.logger.info("Failed to install: unsloth from GitHub")



# Load Llama-3.1 Model for Paraphrasing
paraphrase_model, paraphrase_tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-Instruct",
    max_seq_length=8192,
    load_in_4bit=True
)
FastLanguageModel.for_inference(paraphrase_model)

def paraphrase_text(input_text, style):
    prompt_templates = {
        "Shortened": f"Paraphrase this sentence in a more concise form: '{input_text}'",
        "Expanded": f"Paraphrase this sentence by expanding it: '{input_text}'",
        "Academic": f"Paraphrase this sentence in a more formal, academic tone: '{input_text}'"
    }
    paraphrase_prompt = prompt_templates.get(style, input_text)
    messages = [{"from": "human", "value": paraphrase_prompt}]
    inputs = paraphrase_tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
    outputs = paraphrase_model.generate(
        inputs,
        max_new_tokens=256,
        eos_token_id=[paraphrase_tokenizer.eos_token_id, paraphrase_tokenizer.convert_tokens_to_ids("<|eot_id|>")],
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    return paraphrase_tokenizer.decode(outputs[0][inputs.shape[-1]:], skip_special_tokens=True)


#############################################################################################################
# Route: Grammar Checking
@interface_ns.route('/grammar_check')
class GrammarCheck(Resource):
    def post(self):
        try:
            data = request.get_json()
            input_text = data.get("text", "")
            corrected_text = correct_grammar(input_text)
            return jsonify({"corrected_text": corrected_text})
        except Exception as e:
            interface_ns.logger.info(f"Exception in /grammar_check: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)
        

#############################################################################################################
# Route: Install Required Packages
@interface_ns.route('/install_packages')
class InstallPackages(Resource):
    def post(self):
        try:
            install_packages()
            return jsonify({"message": "Packages installed successfully"})
        except Exception as e:
            interface_ns.logger.info(f"Exception in /install_packages: {e}")
            return make_response(jsonify({"error": "Failed to install packages"}), 500)



#############################################################################################################
# Route: Paraphrasing
@interface_ns.route('/paraphrase')
class ParaphraseText(Resource):
    def post(self):
        try:
            data = request.get_json()
            input_text = data.get("text", "")
            style = data.get("style", "Shortened")
            paraphrased_text = paraphrase_text(input_text, style)
            return jsonify({"paraphrased_text": paraphrased_text})
        except Exception as e:
            interface_ns.logger.info(f"Exception in /paraphrase: {e}")
            return make_response(jsonify({"error": "خطأ في معالجة النص"}), 500)