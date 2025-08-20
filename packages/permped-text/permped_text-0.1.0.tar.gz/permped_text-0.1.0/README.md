# permped-text

**A Python library for preprocessing text before sending it to LLMs.**  

This library helps you:

- Reduce the size of your text by cleaning and minimizing it.  
- Extract unique words to avoid repetition.  
- Prepare text efficiently before sending it to large language models (LLMs).  

## Features

- `get_unique_text(text)` – Returns only the unique words from your text.  
- `minimize_text(text)` – Minimizes and simplifies your text.  
- `clean_and_filter_text(text)` – Cleans your text and removes unnecessary characters.  

## Installation

```bash
pip install permped-text
```
```bash
from permped_text import get_unique_text, minimize_text, clean_and_filter_text

text = "This is an example text. Some words repeat words."

unique_text = get_unique_text(text)
clean_text = minimize_text(unique_text)
filtered_text = clean_and_filter_text(clean_text)

print(filtered_text)

```