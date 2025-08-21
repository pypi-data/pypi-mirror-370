# llm-from-scratch-lab
Lab and python package for building a small GPT model. This code was adapted from the [Build a Large Language Model (From Scratch)](https://github.com/rasbt/LLMs-from-scratch) repository. This lab is intended to be a learning exercise, not a production-ready implementation.
It is still very much a work in progress, and in some regards, a little incomplete. However, it is a good starting point for understanding how to build a small GPT model from scratch.

## Usage
There is a `run_lab.py` script that can be used to run the lab. It will send a piece of text to the lab and the lab will perform the preprocessing, tokenization, and model inference steps. The output will be printed to the console.

## Package Usage
Install the package using pip:
```bash
pip install llm-from-scratch-lab
```

Then, you can use the package in your Python scripts:
```python
from llm_scratch_lab.lab import GPTLab

gpt_lab = GPTLab()
print("Running GPT Lab...")

gpt_lab.run("Hello, I am", with_manual_seed=True)
```