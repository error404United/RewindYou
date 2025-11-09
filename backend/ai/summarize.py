from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model & tokenizer
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

with open("input.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

# Prepare input
inputs = tokenizer("Summarize the following notes in concise, meaningful sentences:\n " + text, return_tensors="pt", max_length=20000, truncation=True)

# Generate summary
outputs = model.generate(
    **inputs,
    max_length=1000,
    min_length=100,
    num_beams=4,
    repetition_penalty=2.5,
    length_penalty=0.6,
    early_stopping=False
)


# Decode summary
summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Summary:", summary)
with open("summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)



