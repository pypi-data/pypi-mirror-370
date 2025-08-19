# Sequence Tokenizer (seqtok)

A Python implementation mimicking C's `strtok()` behavior for generic sequences, but without global state.

## Features

- Splits any sequence type (lists, tuples, strings) using separator elements
- Memory efficient (yields tokens one at a time)
- Follows C's `strtok()` conventions:
  - Skips leading/trailing separators
  - Treats consecutive separators as single delimiter
  - Never returns empty tokens
- But with crucial differences:  
  - State is encapsulated in the generator instance (no global state)
    - No thread safety concerns from global state
  - Each iterator maintains independent state (safe for separate instances)
    - Multiple tokenizers can operate simultaneously
  - Original sequence is never modified
  - Immutable tokens via COWList (Copy-On-Write List)

## Installation

```bash
pip install seqtok
```

## Examples

```python
from seqtok import seqtok

# Tokenize a list of numbers
numbers = [1, 2, 0, 3, 4, 0, 0, 5]
for token in seqtok(numbers, {0}):
    print(token)
# Output: COWList([1, 2])
#         COWList([3, 4])
#         COWList([5])

# Tokenize a string
text = "..Hello...world.!"
for token in seqtok(text, {'.', '!'}):
    print(''.join(token))
# Output: Hello
#         world
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).