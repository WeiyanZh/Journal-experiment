import os
import subprocess
import re

# Base prompt (same style as you type manually, but reusable)
base_prompt = """
You are a technical document extraction system.

Task:
1. First, briefly describe what is shown in the image.
2. Then extract ALL performance-related values of RSD core that have explicit numbers with units.
   Examples: number of cycles, frequency in GHz, bandwidth in GB/s, memory capacity (KB/MB), 
   power (W/mW), latency (cycles), throughput, or any other metric that appears in the image.

Rules:
- Only include values you can directly read from the image.
- Do NOT guess, infer, or invent any missing values.
- If the image contains no performance numbers, clearly state: "No explicit performance values found."
"""

# Folder with your images (adjust if needed)
#image_folder = "/home/weiyan/test/images"
#raw_output_file = "swerv-img-summaries-cpm-thinking.txt"   # with <think>...</think>
#clean_output_file = "swerv-img-summaries-cpm.txt"          # without thinking content

image_folder = "/home/weiyan/Journal/Doc-rsd/images-paper"

raw_output_file = "/home/weiyan/Journal/Doc-rsd/rsd-img-paper-phi.txt"   # with <think>...</think>
# clean_output_file = "/home/weiyan/Journal/RSD/rsd-img-phi.txt"          # without thinking content

# --------------------------------------
# Helper: remove <think>...</think> blocks
# --------------------------------------
def strip_thinking(text: str) -> str:
    # Remove everything from <think> ... </think>, including the tags
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Collapse excessive blank lines and strip edges
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned).strip()
    return cleaned
    
    
# Make sure the folder exists
images = sorted(os.listdir(image_folder))

for idx, name in enumerate(images, start=1):
    full_path = os.path.join(image_folder, name)

    # skip non-image files
    if not name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
        continue

    print(f"[{idx}] Processing {name} ...")

    # This is exactly what you type at the >>> prompt
    user_prompt = f"{base_prompt}  {full_path}\n"

    # Equivalent to: echo "<prompt>" | ollama run openbmb/minicpm-v4.5
    result = subprocess.run(
        #["ollama", "run", "openbmb/minicpm-v4.5"],
        ["ollama", "run", "phi3:medium-128k"],
        input=user_prompt,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        # If something goes wrong, show the error from Ollama
        print("Error from ollama:", result.stderr.strip())
        summary = ""
    else:
        summary = result.stdout.strip()

    # --- Save raw (with thinking) ---
    with open(raw_output_file, "a") as f_raw:
        f_raw.write(f"--- Table {idx}: {name} ---\n")
        f_raw.write(summary + "\n\n\n")

    # --- Save cleaned (without <think>...</think>) ---
    #cleaned = strip_thinking(summary)
    #with open(clean_output_file, "a") as f_clean:
        #f_clean.write(f"--- Table {idx}: {name} ---\n")
        #f_clean.write(cleaned + "\n\n\n")

    print(summary)
    print("-" * 60)

print("✓ Done!")

