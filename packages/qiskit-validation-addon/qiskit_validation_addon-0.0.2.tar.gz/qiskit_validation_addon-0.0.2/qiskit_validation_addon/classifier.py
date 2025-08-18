import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
from typing import Literal

ADAPTER_MODEL_NAME = "justinwoodring/Malicious-Qubits-QASM-Validator-Qwen-7B"

class ClassificationResult:
    def __init__(self, label: Literal["Malicious", "Benign"], raw_response: str):
        self.label = label
        self.raw_response = raw_response

    def __repr__(self):
        return f"ClassificationResult(label={self.label!r}, raw_response={self.raw_response!r})"

# Load adapter config and base model
peft_config = PeftConfig.from_pretrained(ADAPTER_MODEL_NAME)
base_model_name = peft_config.base_model_name_or_path

# Load tokenizer and base model
_tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
_base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
    low_cpu_mem_usage=True
)

# Load and merge adapter
_model = PeftModel.from_pretrained(_base_model, ADAPTER_MODEL_NAME)
_model = _model.merge_and_unload()


def classify_quantum_circuit(circuit_code: str) -> ClassificationResult:
    """
    Classifies a quantum circuit as 'Malicious' or 'Benign'.
    Returns a ClassificationResult with the label and raw model response.
    """
    escaped_string = circuit_code.replace("\n\n", "\n").replace("\n", "\\n")
    prompt = f"<|user|>\nClassify this program as malicious or benign: {escaped_string}<|endoftext|>\n<|assistant|>\n"

    original_padding_side = _tokenizer.padding_side
    _tokenizer.padding_side = 'left'
    inputs = _tokenizer(
        prompt,
        return_tensors="pt",
        max_length=8192,
        truncation=True,
        padding=True
    ).to("cuda")
    _tokenizer.padding_side = original_padding_side

    with torch.amp.autocast('cuda', enabled=torch.cuda.is_bf16_supported()):
        with torch.no_grad():
            outputs = _model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=10,
                use_cache=True,
                temperature=0.1,
                do_sample=False,
                pad_token_id=_tokenizer.pad_token_id
            )
    response = _tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True).strip()
    label = "Malicious" if "malicious" in response.lower() else "Benign" if "benign" in response.lower() else "Malicious"
    return ClassificationResult(label, response)
