from pathlib import Path

p = Path(r"path\\around_the_world\\dir.csv")

if p.suffix != ".csv":
    p = p.with_suffix(".csv")

print(p)