# vcdiff-py

A Python library and CLI tool for working with [VCDIFF (RFC 3284)](https://www.rfc-editor.org/rfc/rfc3284) delta encoding.

---

## 🚀 Quick Start

### Library Usage

```python
import vcdiff

# Read the source file
with open("original.txt", "rb") as f:
    source = f.read()

# Read the VCDIFF delta file
with open("changes.vcdiff", "rb") as f:
    delta_data = f.read()

# Apply the delta to reconstruct the target
try:
    result = vcdiff.decode(source, delta_data)
    print(f"Decoded result: {result}")
except vcdiff.VCDIFFError as e:
    print(f"Decoding failed: {e}")
