# Regex to DFA Converter
This Python-based project provides a clean, modular pipeline to convert regular expressions into deterministic finite automata (DFA). It is composed of three main components:

- `regexconv.py`: Parses and expands shorthand and syntactic sugar in regular expressions.
- `shunyard.py`: Converts regular expressions from infix to postfix notation using the Shunting Yard algorithm.
- `re2dfa.py`: Builds a syntax tree from the postfix expression and generates the corresponding DFA.

## Modules Breakdown
### 1. `regexconv.py`
**Purpose:**  
Expands and tokenizes regular expressions into a verbose intermediate form suitable for syntactic processing.

**Key Features:**
- **CharWrapper Class**: Wraps characters for easier handling and hashing while distinguishing them from operators.
- **Verbose Expansion**:
  - Supports escape sequences like `\d`, `\w`, and `\s`.
  - Expands character classes (e.g., `[a-z]`, `[A-Z0-9]`) into equivalent OR-ed expressions.
  - Recognizes quantifiers (`*`, `+`, `?`) and rewrites them in standard notation.
  - Supports grouping with parentheses `()`.
- **Output**: A list representing the verbose form of the regex where all shorthand and regex sugar are expanded.

**Example:**
```python
verbose_regexp(r"(a|b)*abb")
```
Expands into a list of structured elements with quantifiers and groupings preserved for further processing.

### 2. shunyard.py
**Purpose:**  
Transforms the verbose regular expression (from `regexconv.py`) into postfix (Reverse Polish Notation) format using the Shunting Yard algorithm.

**Key Features:**
- **Augmentation:**
  - Adds explicit concatenation (`.`) operators where implicit.
  - Appends a unique end-marker `#` to help with DFA construction.
- **Shunting Yard Implementation:**
  - Handles precedence (`* > . > |`) and parenthesis grouping.
  - Outputs a postfix-formatted list suitable for syntax tree construction.

**Example:**
```python
augmented = augmented_regexp(verbose_regexp(r"(a|b)*abb"))
postfix = shunting_yard(augmented)
```

### 3. re2dfa.py
**Purpose:**  
Builds the syntax tree from postfix notation and constructs a DFA using the position-based method (also known as the followpos algorithm).
**Key Components:**
- **Syntax Tree Construction:**
  - Builds a tree with operators as internal nodes and characters as leaves.
  - Each leaf node is assigned a unique position.
- **Syntax Tree Annotation:**
  - Calculates `nullable`, `firstpos`, `lastpos` for each node.
  - Computes `followpos` for each position based on tree structure.
- **DFA Construction:**
  - Generates DFA states using sets of positions from the syntax tree.
  - Transitions between states are derived from `followpos`.
  - Final states are identified based on the end-marker `#`.

**Example Usage:**
```python
text = r"(a|b)*abb"
root = build_syntax_tree(shunting_yard(augmented_regexp(verbose_regexp(text))))
tree_info = SyntaxTreeInfo(root)
dfa = DFA(tree_info)
dfa.re2dfa()

print(dfa.alphabets)
print(dfa.start_state)
print(dfa.final_states)
print(dfa.transitions)
```

### Concepts Used
- Regular Expression Parsing
- Character Classes and Escape Handling
- Shunting Yard Algorithm
- Syntax Tree Construction
- Nullable, Firstpos, Lastpos, and Followpos
- Subset Construction Algorithm for DFA

| File | Description |
| ---- | ----------- |
| `regexconv.py` | Expands regex into a verbose intermediate form. |
| `shunyard.py` | Converts verbose regex to postfix using Shunting Yard algorithm. |
| `re2dfa.py` | Builds a syntax tree and constructs the DFA using followpos. |

### Example Output
For input regex `(a|b)*abb`, the program will output:
  - The input alphabet
  - Start state
  - Final states
  - DFA transitions (as a dictionary mapping states to transitions)

### Getting Started
1. Close the repo.
2. Run the `re2dfa.py` file and modify the regex string in the `__main__` block to test different patterns.
```bash
python re2dfa.py
```
