<p align="center">
  <img width="270" alt="ChatGPT Image Aug 16, 2025, 07_57_39 PM" src="https://github.com/user-attachments/assets/7af38c8f-4cd2-4ad8-9512-9d81c8afa1a8" />
</p>


<div align="center">
  
  <a href="https://www.python.org/">![Static Badge](https://img.shields.io/badge/python-3.9+-pink)</a>
  <a href="https://github.com/dross20/llmify/blob/main/LICENSE">![GitHub license](https://img.shields.io/badge/license-MIT-yellow.svg)</a>
  <a href="https://github.com/openai/openai-python">![OpenAI API](https://img.shields.io/badge/-OpenAI%20API-eee?style=flat-square&logo=openai&logoColor=412991)</a>
 
</div>

---
Replace a function call with LLM inference. Sends the source code and arguments to an LLM, which then predicts what the output should be.

> [!CAUTION]
> Please, for the love of all things good and holy, do not use this in any sort of production setting. This library should only be used for experimentation or prototyping.

## 📦 Installation
```bash
pip install git+https://github.com/dross20/llmify
```
## 💻 Quickstart
To use `llmify`, simply apply it as a decorator to a function like so:
```python
from llmify import llmify

@llmify()
def add(a, b):
  return a + b

result = add(1, 2)
print(result) # Output: 3 (probably)
```
To change the model used for inference, pass in a value for the `model` keyword argument:
```python
@llmify(model="gpt-5")
def add(a, b):
  ...
```
You can also use `llmify` on function stubs, so long as they have docstrings or comments:
```python
@llmify()
def greet_user(name):
  """Greet the user in a friendly manner."""
  ...

greeting = greet_user("Mortimer")
print(greeting) # Output: "Hello, Mortimer!"
```
