import sys

try:
    import torch
    from langchain_huggingface import HuggingFacePipeline
    from transformers import pipeline
    
    print("🚀 Initializing model (GPT-2)...")
    # GPT-2 small model hai, jaldi load hoga
    pipe = pipeline("text-generation", model="gpt2", max_new_tokens=20)
    hf_pipe = HuggingFacePipeline(pipeline=pipe)
    
    response = hf_pipe.invoke("The future of AI is")
    print(f"\n✅ SUCCESS! Output: {response}")

except ImportError as e:
    print(f"❌ Missing Library: {e}")
    print("Try running: pip install torch")
except Exception as e:
    print(f"❌ Error: {e}")