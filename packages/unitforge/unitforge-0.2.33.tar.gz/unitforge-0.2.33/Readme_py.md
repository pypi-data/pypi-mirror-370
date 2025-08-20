# Unitforge

**Unitforge** is a Python library for working with physical quantities that respect units, dimensional analysis, and arithmetic correctness — powered by high-performance Rust under the hood.

Built for scientific computing, simulation, and engineering workflows where unit safety is non-negotiable.

---

## Features

- **Strong unit enforcement**: Prevent unit mismatch bugs at runtime.
- **Arithmetic support**: Add, subtract, multiply, and divide quantities with automatic unit resolution.
- **Unit conversion**: Convert between compatible units on the fly.
- **Scientific formatting**: Values display with 4 significant digits and the configured unit.
- **3D Vectors & Matrices**: Perform vector/matrix math with quantities and units.
- **NumPy integration**: Convert to/from NumPy arrays easily.
- **Constants**: Built-in constants like the speed of light.
- **Serialization-ready**: Optional serde-based serialization support (if compiled with feature).

---

## Installation

```bash
pip install unitforge
```

---

## Example Usage

```python
from unitforge import Force, ForceUnit, Distance, DistanceUnit

f = Force(12.0, ForceUnit.N)
print(f.to(ForceUnit.mN))  # → 12000.0

d = Distance(2.0, DistanceUnit.m)
work = f * d
print(work)  # → 24 Nm
```

### Unit Conversion

```python
f = Force(1.0, ForceUnit.N)
print(f.to(ForceUnit.kN))  # → 0.001
```

### Arithmetic

```python
f1 = Force(5.0, ForceUnit.N)
f2 = Force(3.0, ForceUnit.N)
f_sum = f1 + f2
print(f_sum.to(ForceUnit.N))  # → 8.0
```

---

## Vector and Matrix Support

```python
from unitforge import Vector3, Distance, DistanceUnit

v = Vector3.from_list([
    Distance(3., DistanceUnit.m),
    Distance(4., DistanceUnit.m),
    Distance(12., DistanceUnit.m)
])

print(v.norm())  # → 13.0 m
```

---

## NumPy Interoperability

```python
import numpy as np
from unitforge import Vector3, ForceUnit

arr = np.array([1.0, 2.0, 3.0])
vec = Vector3.from_array(arr, ForceUnit.N)
arr_back = vec.to_array(ForceUnit.N)

print(arr_back)  # → [1. 2. 3.]
```

---

## Quantities Available

Examples include:

- `Acceleration`, `AreaOfMoment`, `Density`, `Stiffness`, `Time`, `Volume`, `Angle`, `Area`, `Distance`, `ForcePerVolume`, `Strain`, `Velocity`, `AngularAcceleration`, `Charge`, `ForceArea`, `Force`, `Stress`, `VelocitySquared`, `AngularVelocity`, `Compliance`, `ForceDistance`, `ForceVolume`, `Mass`, `Voltage`
- Each with associated unit enums (e.g., `ForceUnit`, `DistanceUnit`, ...)

---

```python
from math import isclose
from unitforge import Force, ForceUnit

f = Force(12., ForceUnit.N)
assert isclose((f * 2).to(ForceUnit.N), 24.)
```

---

## Contributing

Contributions are welcome! While the core is implemented in Rust, Python usage feedback, bug reports, and API improvements are highly valued.

---

## Repository

[GitLab – Unitforge Crate](https://gitlab.com/henrikjstromberg/unitforge)