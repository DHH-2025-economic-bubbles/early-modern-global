# How are colonial systems represented in Early Modern Newspaper discourses? A study of newspaper representations of geographical places, people, and trade goods

Repository for the Helsinki Digital Humanities hackathon 2025. Please follow the instructions to reproduce our research results.

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

## Advertisements: How do advertisements of colonial goods reveal the historical contexts of slave trading and and Britain's attitudes toward its colonies?
### Extracting N-grams Related to Colonial Goods
To analyze the discourse surrounding colonial goods, we extracted tri-grams containing these terms from newspaper advertisements.
```sh
python -m src.EDA.count_ngrams
```

### Categorizing Surrounding Words
To further examine the context in which colonial goods appeared, we identified and extracted associated nouns and adjectives from the tri-grams.
```sh
python -m src.EDA.generate_advertisement_noun_adj_list
```

### Secondary Literature
Burke, Edmund. 1784. Mr. Burke’s Speech, On the 1st December 1783, upon the Question for the Speaker’s Leaving the Chair, in Order for the House to Resolve Itself into a Committee on Mr. Fox’s East India Bill. London: Printed for J. Dodsley, in Pall-Mall.

Goodman, Rob. 2020. "‘The Low Principles of Jurisprudence’: Legal Indeterminacy in Edmund Burke’s Impeachment of Warren Hastings." The Review of Politics 82 (3): 459–83. https://doi.org/10.1017/S0034670520000364.

Greaves, I. "The Character of British Colonial Trade. Journal of Political Economy", 1954, 62 (1), pp. 1-11, Stable URL: https://www.jstor.org/stable/1824983. 

Ashworth, W. "Customs and Excise: Trade, Production and Consumption in England 1640– 1845", Oxford: Oxford University Press, 2003.

Rive, A. "The Consumption of Tobacco Since 1600", The Economic Journal, Volume 36, Issue Supplement_1, 1 January 1926, Pages 57–75, https://doi.org/10.1093/ej/36.Supplement_1.57

Austen, R. A., & Smith, W. D. (2006). The Economic Value of British Colonial Empire in the Seventeenth and Eighteenth Centuries: The Economic Value of British Colonial Empire. History Compass, 4(1), 54–76. https://doi.org/10.1111/j.1478-0542.2005.00300.x

Berg, M. (2004). In Pursuit of Luxury: Global History and British Consumer Goods in the Eighteenth Century. Past & Present, 182(1), 85–142. https://doi.org/10.1093/past/182.1.85

Greaves, I. (1954). The Character of British Colonial Trade. Journal of Political Economy, 62(1), 1–11. https://doi.org/10.1086/257456

McCants, A. E. C. (2007). Exotic Goods, Popular Consumption, and the Standard of Living: Thinking about Globalization in the Early Modern World. Journal of World History, 18(4), 433–462. https://doi.org/10.1353/jwh.2008.0008

Ng, Su Fang. 2019. "Indian Interpreters in the Making of Colonial Historiography: New Light on Mark Wilks’s Historical Sketches of the South of India (1810–1817)." The English Historical Review 134 (569): 821–54. https://doi.org/10.1093/ehr/cez213.

Richardson, D. (1987). The slave trade, sugar, and British economic growth, 1748-1776. The Journal of Interdisciplinary History, 17(4), 739-769.

## Geography: How is a colonial geography being created? How is the world being organised through a colonial lens?
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
We downloaded the DK Atlas of World History Gazetteer from the World Historical Gazetteers website. From this, we generated a geodataset (gpkg file) of locations pertaining to the British colonies in the early modern period. Using QGIS, we combined the CSV containing co-occurrence frequencies with this geodataset and represented these on a map. We did this for location co-occurrences with sugar and tobacco separately.

### Secondary Literature
Ardanuy, Mariona Coll, et al. “Resolving Places, Past and Present: Toponym Resolution in Historical British Newspapers Using Multiple Resources.” *Proceedings of the 13th Workshop on Geographic Information Retrieval*, Association for Computing Machinery, 2019, https://doi.org/10.1145/3371140.3371143.

Menzin, Marion. “The Sugar Revolution in New England: Barbados, Massachusetts Bay, and the Atlantic Sugar Economy, 1600–1700.” *Business History Review*, 2024/03/21 ed., vol. 97, no. 4, 2023, pp. 699–750. Cambridge Core, *Cambridge University Press*, https://doi.org/10.1017/S0007680523000867.

Merritt, J. E. “The Triangular Trade.” *Business History*, vol. 3, no. 1, Dec. 1960, pp. 1–7, https://doi.org/10.1080/00076796000000012.
