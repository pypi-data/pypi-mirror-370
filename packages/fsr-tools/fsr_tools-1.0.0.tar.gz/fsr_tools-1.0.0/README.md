# FSR-Tools: Feedback/Feedforward Shift Registers in Python

Designed to test FSR Mathematically for verification of Verilog Design.
This package provides an abstract base class for Feedback/Feedforward Shift Registers (FSRs) and two concrete implementations:  
- **Fibonacci LFSR** (linear feedback)
- **Galois LFSR** (linear feedforward)

Supports:
- Custom characteristic polynomials
- Arbitrary initial states
- State table generation
- Algebraic polynomial form
- Bitwise access to register positions

## Installation

Clone the repo and place the module in your project:

```bash
git clone https://github.com/anubhav-narayan/fsr-tools.git
```

Use `poetry`

```bash
poetry install
```

## Usage

General Usage
```python3
from fsr_tools import Galois_LFSR as LFSR

lfsr = LFSR(poly=0b10011, state=0b1010)

# Get full cycle of states
print(lfsr.state_table)
# Access bits
print(lfsr[0]) # Read a bit
lfsr[4] = lfsr[3] & 0b1 # Write a bit
```
Usage with CoCoTB
```python3
from fsr_tools import Galois_LFSR as LFSR
from cocotb import BinaryValue

lfsr = LFSR(poly=0b10011, state=0b1010)

# Assign state
dut.lfsr.value = BinaryValue(lfsr.state, n_bits=lfsr.field_order)
```

Extend the `FSR` Abstract Class to create custom Feedback/Feedforward Shift Registers. Just override the `round` function.
