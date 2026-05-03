import gradio as gr
from transformers import AutoProcessor, Gemma4ForConditionalGeneration
import torch
import os

# Optimization: Contextual Intelligence with Memory Offloading
model_id = "google/gemma-4-E2B"
token = os.environ.get("HUGGINGFACE_TOKEN")

print("BOOT: Starting Gemma 4-E2B (Text-Optimized Mode)...")

try:
    # Processor is essential for any-to-any models
    processor = AutoProcessor.from_pretrained(model_id, token=token)
    
    # Critical Fix: Load with explicit CPU offloading to bypass 16GB limit
    model = Gemma4ForConditionalGeneration.from_pretrained(
        model_id,
        token=token,
        torch_dtype=torch.float16,
        device_map="cpu",
        low_cpu_mem_usage=True,
        offload_folder="offload",
        offload_state_dict=True
    )
    print("BOOT: SUCCESS. Gemma 4 is now running on CPU-Basic.")
except Exception as e:
    print(f"BOOT FAIL: {str(e)}")
    def chat(message, history):
        return f"CRITICAL BOOT ERROR: {str(e)}"
else:
    def chat(message, history):
        try:
            messages = []
            for user_msg, bot_msg in history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})
            messages.append({"role": "user", "content": message})
            
            # Apply Gemma's chat template
            if hasattr(processor, "apply_chat_template"):
                prompt = processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
            elif hasattr(processor, "tokenizer") and hasattr(processor.tokenizer, "apply_chat_template"):
                prompt = processor.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
            else:
                prompt = message
                
            inputs = processor(text=prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs, 
                    max_new_tokens=3000,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            
            full_text = processor.decode(outputs[0], skip_special_tokens=True)
            return full_text.split(message)[-1].strip()
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            print(f"RUNTIME ERROR: {err}")
            return f"Runtime Error during generation: {str(e)}"


# Premium UI Aesthetics
interface = gr.ChatInterface(
    chat, 
    title="Gemma 4-E2B: Quantum Lead",
    description="Optimized for High-Intelligence Storytelling on CPU-Basic Tier."
)

if __name__ == "__main__":
    interface.launch()
