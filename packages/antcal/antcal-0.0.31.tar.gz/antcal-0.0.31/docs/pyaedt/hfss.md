# HFSS module

Source: [`pyaedt/pyaedt/hfss.py`](https://github.com/pyansys/pyaedt/blob/main/pyaedt/hfss.py)

## HFSS Instance Initialization Sequence

`HFSS` → `FieldAnalysis3D` → `Analysis` → `Design` → `AedtObjects`

## Problems

- Command execution will become increasingly slow
  if the script is running for a long time.
