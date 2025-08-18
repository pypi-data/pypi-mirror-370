# Sparx-AI

A Python library containing a collection of Generative AI code examples and utilities for learning and development.

## Installation

```bash
pip install sparx-ai
```

## Usage

### Basic Usage

```python
from sparx import show_code

# Display a specific code example
show_code('prac1.txt')
```

### List Available Examples

```python
from sparx import list_examples

# Show all available code examples
list_examples()
```

### Advanced Usage

```python
from sparx import show_code, get_file_description

# Show code without line numbers
show_code('prac2.txt', line_numbers=False)

# Get description of a file
description = get_file_description('prac1.txt')
print(description)
```

## Available Examples

The library includes the following code examples:

- `prac1.txt` - Basic Data Preprocessing for Generative AI
- `prac2.txt` - Visualizing Data Distributions for Generative AI
- `prac3.txt` - TensorFlow Computation Graph with Eager Execution
- `prac4.txt` - [Description automatically extracted]
- `prac5.txt` - GloVe Pre-trained Embeddings
- And more...

## Features

- 📁 Easy access to curated AI/ML code examples
- 🔍 Search and display specific examples
- 📝 Line-numbered code display
- 📚 List all available examples
- 🏷️ Get descriptions from code files

## Requirements

- Python 3.7+
- Dependencies: numpy, matplotlib, scikit-learn, tensorflow, torch, spacy, transformers, and more

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
