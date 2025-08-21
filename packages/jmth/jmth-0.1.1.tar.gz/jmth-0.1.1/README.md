# JMTH

**jmth** is a simple Python library for basic math operations.  
This is my first Python package, built for learning and sharing.  
Feedback and contributions are very welcome! 🚀

---

## Features
- 🧊 Volume of Cube
- ✖️ Solve SPLDV (two-variable linear equations)
---

## Installation

You can install via pip:

```bash
pip install jmth
```

## Usage

```python
import jmth

# Volume of cube
print(jmth.volume_cube(5))  
# Output: 125

# SPLDV example:
#  1x + 2y = 17
#  1x + 1y = 6
print(jmth.spldv(1, 2, 17, 1, 1, 6))
# Output: (x=5.0, y=6.0)
```

## Contributing
This is my first package, so any feedback or contribution is very much appreciated.
If you want to help improve this library, feel free to make a pull request or open an issue.