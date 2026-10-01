from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "ibm-granite/granite-3.3-8b-instruct"

print("=" * 80)
print("GRANITE LLM TEST")
print("=" * 80)

print()
print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Tokenizer loaded successfully!")

print()
print("Loading Granite model...")
print("This may take some time on CPU.")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
)

print("Granite model loaded successfully!")

prompt = "Explain what Retrieval Augmented Generation is in simple terms."

messages = [
    {
        "role": "user",
        "content": prompt,
    }
]

input_text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer(
    input_text,
    return_tensors="pt",
)

print()
print("Generating response...")

outputs = model.generate(
    **inputs,
    max_new_tokens=150,
)

generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

response = tokenizer.decode(
    generated_tokens,
    skip_special_tokens=True,
)

print()
print("=" * 80)
print("GRANITE RESPONSE")
print("=" * 80)
print(response)
print()
print("=" * 80)
print("GRANITE TEST COMPLETE")
print("=" * 80)