# Mobile Monitoring of Cognitive Change (M2C2) Platform

## 📘 M2C2 DataKit (m2c2-datakit): Universal Loading, Assurance, and Scoring

This is the documentation for the **M2C2 DataKit** Python package 🐍, which is part of the M2C2 Platform. The M2C2 Platform is a comprehensive system designed to facilitate the collection, processing, and analysis of mobile cognitive data (aka, ambulatory cognitive assessments, cognitive activities, and brain games). 

🚀 **A set of R, Python, and NPM packages for scoring M2C2kit Data!** 🚀

[![PyPI version](https://img.shields.io/pypi/v/m2c2_datakit.svg)](https://pypi.org/project/m2c2-datakit/)

## Documentation

See [here for documentation](https://m2c2-project.github.io/datakit/site/index.html)

## 🔧 Installation

```bash
pip install m2c2-datakit
# or
pip3 install m2c2-datakit
```

---

### 🛠️ Setup for Developers of this Package
```bash
!make clean
!make dev-install
```
---

Developers: 
- [Dr. Nelson Roque](https://www.linkedin.com/in/nelsonroque/) | ORCID: https://orcid.org/0000-0003-1184-202X
- [Dr. Scott Yabiku](https://www.linkedin.com/in/scottyabiku) | ORCID: [Coming soon!]

---

## Changelog

[Source: https://github.com/m2c2-project/datakit](https://github.com/m2c2-project/datakit)

See [CHANGELOG.md](CHANGELOG.md)

---

## 🎯 Purpose

Enable researchers to plug in data from varied sources (e.g., MongoDB, UAS, MetricWire, CSV bundles) and apply a consistent pipeline for:

- Input validation

- Scoring via predefined rules

- Inspection and summarization

- Tidy export and codebook generation

---

## 🧠 L.A.S.S.I.E. Pipeline Summary

| Step | Method           | Purpose                                                                 |
|------|------------------|-------------------------------------------------------------------------|
| L    | `LASSIE.load()`         | Load raw data from a supported source (e.g., MongoDB, UAS, MetricWire). |
| A    | `LASSIE.assure()`       | Validate that required columns exist before processing.                 |
| S    | `LASSIE.score()`        | Apply scoring logic based on predefined or custom rules.                |
| S    | `LASSIE.summarize()`    | Aggregate scored data by participant, session, or custom groups.        |
| I    | `LASSIE.inspect()`      | Visualize distributions or pairwise plots for quality checks.           |
| E    | `LASSIE.export()`       | Save scored and summarized data to tidy files and optionally metadata.  |

---

## 🔌 Supported Sources

You may have used M2C2kit tasks via our various integrations, including the ones listed below. Each integration has its own loader class, which is responsible for reading the data and converting it into a format that can be processed by the `m2c2_datakit` package. Keep in mind that you are responsible for ensuring that the data is in the correct format for each loader class.

In the future we anticipate creating loaders for downloading data via API.

| Source Type   | Loader Class          | Key Arguments                            | Notes                                 |
|---------------|------------------------|-------------------------------------------|----------------------------------------|
| `mongodb`     | `MongoDBImporter`      | `source_path` (URL, to JSON)                      | Expects flat or nested JSON documents. |
| `multicsv`    | `MultiCSVImporter`     | `source_map` (dict of CSV paths)          | Each activity type is its own file.    |
| `metricwire`  | `MetricWireImporter`   | `source_path` (glob pattern or default)   | Processes JSON files from unzipped export. |
| `qualtrics`    | `QualtricsImporter`     | `source_path` (URL to CSV)         | Each activity's trial saves data to a new column.    |
| `uas`         | `UASImporter`          | `source_path` (URL, to pseudo-JSON)                       | Parses newline-delimited JSON.         |


---

## 🧪 Example: Full Pipeline

For a full pipeline, [go to our repo](https://github.com/m2c2-project/datakit-notebooks)

### MetricWire
```python
mw = m2c2.core.pipeline.LASSIE().load(source_name="metricwire", source_path="data/metricwire/unzipped/*/*/*.json")
mw.assure(required_columns=m2c2.core.config.settings.STANDARD_GROUPING_FOR_AGGREGATION_METRICWIRE)
mw_scored = mw.score()
mw.inspect()
mw.export(file_basename="metricwire", directory="tidy/metricwire_scored")
mw.export_codebook(filename="codebook_metricwire.md", directory="tidy/metricwire_scored")
```
# -----------------------------------------------------------------------------------------------------

### MongoDB
```python
mdb = m2c2.core.pipeline.LASSIE().load(source_name="mongodb", source_path="data/production-mongo-export/data_exported_120424_1010am.json")
mdb.assure(required_columns=m2c2.core.config.settings.STANDARD_GROUPING_FOR_AGGREGATION)
mdb.score()
mdb.inspect()
mdb.export(file_basename="mongodb_export", directory="tidy/mongodb_scored")
mdb.export_codebook(filename="codebook_mongo.md", directory="tidy/mongodb_scored")
```
# -----------------------------------------------------------------------------------------------------

### Understanding American Study (UAS) Datasets
```python
uas = m2c2.core.pipeline.LASSIE().load(source_name="UAS", source_path= "https://uas.usc.edu/survey/uas/m2c2_ess/admin/export_m2c2.php?k=<INSERT KEY HERE>")
uas.assure(required_columns=m2c2.core.config.settings.STANDARD_GROUPING_FOR_AGGREGATION)
uas.score()
uas.inspect()
uas.export(file_basename="uas_export", directory="tidy/uas_scored")
uas.export_codebook(filename="codebook_uas.md", directory="tidy/uas_scored")
```
# -----------------------------------------------------------------------------------------------------

### MultiCSV
```python
source_map = {
    "Symbol Search": "data/reboot/m2c2kit_manualmerge_symbol_search_all_ts-20250402_151939.csv",
    "Grid Memory": "data/reboot/m2c2kit_manualmerge_grid_memory_all_ts-20250402_151940.csv"
}

mcsv = m2c2.core.pipeline.LASSIE().load(source_name="multicsv", source_map=source_map)
mcsv.assure(required_columns=m2c2.core.config.settings.STANDARD_GROUPING_FOR_AGGREGATION)
mcsv.score()
uas.inspect()
mcsv.export(file_basename="uas_export", directory="tidy/uas_scored")
mcsv.export_codebook(filename="codebook_uas.md", directory="tidy/uas_scored")
```

---


## **💡 Contributions Welcome!**

📌 Have ideas? Found a bug? Want to improve the package?  [Open an issue!](https://github.com/m2c2-project/datakit).

📜 **[Code of Conduct](https://docs.github.com/en/site-policy/github-terms/github-community-code-of-conduct) - Please be respectful and follow community guidelines.**

---

## Acknowledgements
The development of `m2c2-datakit` was made possible with support from NIA (1U2CAG060408-01).

---

## 🌎 **More Resources:**  

📌 [M2C2 Official Website](https://m2c2.io)

📌 [M2C2kit Official Documentation Website](https://m2c2-project.github.io/m2c2kit-docs/)

📌 [Pushing to PyPI](https://docs.astral.sh/uv/guides/publish/#publishing-your-package)

  - https://docs.astral.sh/uv/guides/integration/github/#setting-up-python

📌 [What is JSON?](https://www.w3schools.com/whatis/whatis_json.asp)

---

## What is What? 🧠 Summary

| Thing                         | Type            | Description                       |
| ----------------------------- | --------------- | --------------------------------- |
| `m2c2_datakit`                | Library/Package | Top-level Python package     |
| `core/`, `loaders/`, `tasks/` | Subpackages     | Contain logically grouped modules |
| `log.py`, `export.py`, etc.   | Modules         | Individual Python files           |
| `__init__.py`                 | Special Module  | Marks the directory as a package  |

---

## 🎬 Inspired by:
<img src="https://m.media-amazon.com/images/M/MV5BNDNkZDk0ODktYjc0My00MzY4LWE3NzgtNjU5NmMzZDA3YTA1XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg" alt="Inspiration for Package, Lassie Movie" width="250"/>

---

🚀 Let's go study some brains!