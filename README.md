# early-modern-global
Repository for the Helsinki Digital Humanities hackathon 2025.

**All code should be ran from project root!**

## Downloading data
From the project root, run the following command to download data files. For example to download `bl_newspapers_meta.txt` and `json_res.tar` run:

```bash
bash scripts/get_data.sh bl_newspapers_meta.csv json_res.tar
```

These are the two files that are necessary for this study. If you are interested, there are also some other metadata available.
### Available file names:
- `bl_newspapers_meta.csv`: Metadata for Burney and Nichols collections.
- `bln-places.csv`: Contains publication title, collection, city, and 'Latitude,Longitude' for Burney and Nichols collections.
- `burney-titles.csv`: List of all newspaper titles and issue dates in the Burney collection.
- `nichols-titles.csv`: List of all newspaper titles and issue dates in the Nichols collection.
- `chunks_for_blast.tar`: Text reuse across the newspapers.
- `json_res.tar`: Newspaper details with OCRed texts.
- `nichols_XML`: Newspaper details in XML format, including layout details (to be published later today).

## uv
UV is the package manager for this project. **All python code is made to be ran through uv!** 

[Install uv here before proceeding.](https://docs.astral.sh/uv/getting-started/installation/) 

### Working with uv
To add a dependency, f.e. `pandas`, simply run:
```sh
uv add pandas
```
this modifies `pyproject.toml` and `uv.lock`, so be sure to commit those as well. After pulling changes to the forementioned files, run:
```sh
uv sync
```
<!-- Then, to run the project, run:
```sh
uv run path/to/python.py
``` -->

## Preprocess data
The original data has poor OCR quality, significant noise, and inaccurate segmentation. As a first step, we apply preprocessing techniques to clean the data. This includes correcting spelling errors, joining hyphenated words, and segmenting articles into coherent paragraphs.
```sh
python -m src.preprocessing.clean_dataset
```

## Famous Figures Exploration: extract famous individuals from newspaper. Who are they? How are they related?

### Article Extraction Based on Keywords
Using pre-defined lists of goods and locations associated with colonial trade, we extract articles that contain at least one keyword. These articles are saved along with their metadata
```sh
python -m src.preprocessing.detect_words
```

### Article Filtering Based on Country
From the articles extracted in the previous step, we further filter them by identifying country mentions within the text
```sh
python -m src.preprocessing.extract_country_paragraphs
```

### Famous Figures Extraction
We then Named Entity Recognition (NER) to extract mentions of historically significant individuals related to each country
```sh
python -m src.preprocessing.ner
```

## Advertisement

## Geography
### Article Extraction Based on Keywords
Using pre-defined lists of goods and locations associated with colonial trade, we extract articles that contain at least one keyword. These articles are saved along with their metadata
```sh
python -m src.preprocessing.detect_words
```

### Count Co-occurence Between Goods and Locations
We analyze the co-occurrence of goods and locations to further explore the representation of colonial goods in relation to specific geographic regions.
```sh
python -m src.EDA.get_cooccurence_frequencies
```

### Use Co-occurence Data to Generate Geographic Maps
