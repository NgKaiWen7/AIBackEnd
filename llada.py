import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download

model_path = snapshot_download(
repo_id="inclusionAI/LLaDA2.2-mini",
local_dir="./models/LLaDA2.2-mini",
)

print(f"Model downloaded to: {model_path}")

model_path = "./models/LLaDA2.2-mini"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    local_files_only=True,
)
model.eval()

tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    trust_remote_code=True,
    local_files_only=True,
)
prompt = "Calculate 1+5-28*0.5-200=?"
input_ids = tokenizer.apply_chat_template(
    [{"role": "user", "content": prompt}],
    add_generation_prompt=True,
    tokenize=True,
    return_tensors="pt",
).input_ids

generated_tokens = model.generate(
    inputs=input_ids,
    eos_early_stop=True,
    gen_length=512,
    block_length=32,
    threshold=0.5,
    editing_threshold=0.0,
    temperature=0.0,
)

generated_answer = tokenizer.decode(
    generated_tokens[0],
    skip_special_tokens=True,
)
print(generated_answer)
