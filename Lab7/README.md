# Lab 7: Fuzzing for Input Validation Bugs

L6_L7_46 — Photo Print Order

Property-based fuzzing of `photo_print_order.py` with Hypothesis, followed by input hardening of the three functions.

## Files

| File | Description |
|------|-------------|
| `photo_print_order.py` | Fixed script |
| `test_photo_print_order.py` | Hypothesis tests for `extra_print_charge`, `order_valid` and `dispatch_status` |
| `Lab7_Report.pdf` | Output of Steps 2, 4, 5 and 6 |

## Bugs found

| Function | Input | Original behaviour |
|----------|-------|--------------------|
| `extra_print_charge` | `None` or non-numeric `copies`, unhashable `print_size` | `TypeError` |
| `extra_print_charge` | `nan`, float or bool `copies` | Returned `nan`, a fractional price, or accepted the value |
| `extra_print_charge` | Unknown `finish` (e.g. `"sepia"`) | Silently charged the non-matte rate |
| `extra_print_charge` | Non-bool `is_member` | Accepted |
| `order_valid` | Negative or `nan` `file_mb`, negative or float `copies` | Returned `True` |
| `order_valid` | `None` or text values | `TypeError` |
| `dispatch_status` | `nan` hours | Returned `"missed"` |
| `dispatch_status` | `None` hours | `TypeError` |
| `dispatch_status` | Non-bool flags | Accepted |

## Fix

Inputs are validated before use. `extra_print_charge` and `dispatch_status` raise `ValueError` for invalid input. `order_valid` returns `False`. Valid inputs give the same results as before.

## Run

```
pip install hypothesis pytest
python photo_print_order.py
python -m pytest test_photo_print_order.py
```

## Results

| Script | Tests |
|--------|-------|
| Original | 10 failed, 6 passed |
| Fixed | 16 passed |

The Lab 6 coverage tests also pass against the fixed script.
