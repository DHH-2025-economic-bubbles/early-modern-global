# early-modern-global
Repository for the Helsinki Digital Humanities hackathon 2025.

## Downloading data
From the project root, run the following command to download data files. For example to download `bl_newspapers_meta.txt` and `json_res.tar` run:

```bash
bash scripts/get_data.sh bl_newspapers_meta.txt json_res.tar
```

### Available file names:
- `bl_newspapers_meta.txt`: Metadata for Burney and Nichols collections.
- `bln-places.csv`: Contains publication title, collection, city, and 'Latitude,Longitude' for Burney and Nichols collections.
- `burney-titles.csv`: List of all newspaper titles and issue dates in the Burney collection.
- `nichols-titles.csv`: List of all newspaper titles and issue dates in the Nichols collection.
- `chunks_for_blast.tar`: Text reuse across the newspapers.
- `json_res.tar`: Newspaper details with OCRed texts.
- `nichols_XML`: Newspaper details in XML format, including layout details (to be published later today).

Make sure to navigate back to the project root after running the script.

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

