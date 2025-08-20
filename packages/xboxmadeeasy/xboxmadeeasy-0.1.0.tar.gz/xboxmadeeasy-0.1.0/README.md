# xboxmadeeasy

Plug-and-play Xbox controller input for Python. Supports Xbox 360, One, Series S/X via USB. Tracks input states like `A = True`, `LT = 0.8`, `LX = -0.5` with no GUI or assets.

## Features
- State-based input tracking
- Supports buttons, sticks, triggers
- Mutation-ready for automation, games, or demos

## Example
```python
if controller_state.get_button("A"):
    print("Jump!")