# early-modern-global
Repository for the Helsinki Digital Humanities hackathon 2025.

## Downloading data
From project root, run 

```sh
bash scripts/get_data.sh
```

## uv
UV is the package manager for this project. To add a dependency, f.e. `pandas`, simply run:
```sh
uv add pandas
```
this modifies `pyproject.toml` and `uv.lock`, so be sure to commit those as well. After pulling changes to the forementioned files, run:
```sh
uv sync
```
Then, to run the project, run:
```sh
uv run path/to/python.py
```

