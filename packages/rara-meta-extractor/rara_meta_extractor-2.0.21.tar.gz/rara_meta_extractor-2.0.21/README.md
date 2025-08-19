# RaRa Meta Extractor

![Py3.10](https://img.shields.io/badge/python-3.10-green.svg)
![Py3.11](https://img.shields.io/badge/python-3.11-green.svg)
![Py3.12](https://img.shields.io/badge/python-3.12-green.svg)

**`rara-meta-extractor`** is a  Python library for extracting relevant meta information for cataloging.


---

## ✨ Features  

- Extracts relevant **metainformation** for cataloging (authors, titles, publication dates, publisher, ISBN, ISSN etc).
- Detects and extracts **summaries, conclusions and abstracts**.
- Uses **Llama** for extracting metadata from plaintext and **custom parsers** for extrating metadata from **EPUB and METS/ALTO mark-ups**.
- Supports extracting **custom set of user-defined** fields.¹

¹ Might not work well with fine-tuned Llama instances.

---


## ⚡ Quick Start  

Get started with `rara-meta-extractor` in just a few steps:

1. **Install the Package**  
   Ensure you"re using Python 3.10 or above, then run:  
   ```bash
   pip install rara-meta-extractor
   ```

2. **Import and Use**  
   Extracting user-defined fields:

   ```python
    from rara_meta_extractor.llama_extractor import LlamaExtractor
    from pprint import pprint

    text = """
       JUMALAL EI OLE AEGA

       Toimetanud Milvi Teesalu
       Kaane kujundanud Piret Tuur
       Autoriõigus: Marje Ernits ja OÜ Eesti Raamat, 2019
       ISBN 978-9949-683-96-3
       ISBN 978-9949-683-97-0 (epub)
    """

    fields = [
      "editor", "designer", "isbn", "author",
      "copyright year", "title"
    ]

    llama_extractor = LlamaExtractor(
        llama_host_url="http://local-llama:8080",
        fields=fields,
        temperature=0.3
    )

    extracted_info = llama_extractor.extract(text)
    pprint(extracted_info)
   ```
   **Out:**

   ```JSON
   {
     "editor": ["Milvi Teesalu"],
     "designer": ["Piret Tuur"],
     "isbn": ["978-9949-683-96-3", "978-9949-683-97-0"],
     "author": ["Marje Ernits ja OÜ Eesti Raamat"],
     "copyright year": ["2019"],
     "title": ["JUMALAL EI OLE AEGA"]
   }
   ```
   Extracting predefined metadata:

   ```python
   from rara_meta_extractor.meta_extractor import MetaExtractor
   from pprint import pprint

   text = """
      JUMALAL EI OLE AEGA

      Toimetanud Milvi Teesalu
      Kaane kujundanud Piret Tuur
      Autoriõigus: Marje Ernits ja OÜ Eesti Raamat, 2019
      ISBN 978-9949-683-96-3
      ISBN 978-9949-683-97-0 (epub)
   """

   meta_extractor = MetaExtractor(
      meta_extractor_config = {
         "llama_host_url"="http://local-llama:8080"
      text_classifier_config = {
         "llama_host_url"="http://local-llama:8080"
      }
   )

    extracted_info = meta_extractor.extract_simple(text)
    pprint(extracted_info)
   ```
   **Out:**

   ```JSON
   {
      "extractor": "Llama-Extractor",
      "meta": {
         "authors": [
            {
            "name": "Marje Ernits",
            "role": "Autor"
            },
            {
            "name": "Milvi Teesalu",
            "role": "Toimetaja"
            },
            {
            "name": "Piret Tuur",
            "role": "Kujundaja"
            },
            {
            "name": "Eesti Raamat",
            "role": "Väljaandja"
            }
         ],
         "isbn": [
            "9789949683963",
            "9789949683970"
         ],
         "publication_place": "Tallinn",
         "titles": [
            {
            "title": "Jumalal ei ole aega",
            "title_type": "main_title"
            },
            {
            "title": "jutustused] /",
            "title_type": "additional_title_part"
            }
         ],
         "udc": [
            "821.511.113-32"
         ],
         "udk": [
            "821.511.113"
         ]
      }
   }

   ```
---


## ⚙️ Installation Guide

Follow the steps below to install the `rara-meta-extractor` package, either via `pip` or locally.

---

### Installation via `pip`

<details><summary>Click to expand</summary>

1. **Set Up Your Python Environment**  
   Create or activate a Python environment using Python **3.10** or above.

2. **Install the Package**  
   Run the following command:  
   ```bash
   pip install rara-meta-extractor
   ```
</details>

---

### Local Installation

Follow these steps to install the `rara-meta-extractor` package locally:  

<details><summary>Click to expand</summary>


1. **Clone the Repository**  
   Clone the repository and navigate into it:  
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above. E.g:
   ```bash
   conda create -n py310 python==3.10
   conda activate py310
   ```

3. **Install Build Package**  
   Install the `build` package to enable local builds:  
   ```bash
   pip install build
   ```

4. **Build the Package**  
   Run the following command inside the repository:  
   ```bash
   python -m build
   ```

5. **Install the Package**  
   Install the built package locally:  
   ```bash
   pip install .
   ```

</details>

---

## 🚀 Testing Guide

Follow these steps to test the `rara-meta-extractor` package.


### How to Test

<details><summary>Click to expand</summary>

1. **Clone the Repository**  
   Clone the repository and navigate into it:  
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above.

3. **Install Build Package**  
   Install the `build` package:  
   ```bash
   pip install build
   ```

4. **Build the Package**  
   Build the package inside the repository:  
   ```bash
   python -m build
   ```

5. **Install with Testing Dependencies**  
   Install the package along with its testing dependencies:  
   ```bash
   pip install .[testing]
   ```

6. **Run Tests**  
   Run the test suite from the repository root:  
   ```bash
   python -m pytest -v tests
   ```

---

</details>


## 📝 Documentation

<details><summary>Click to expand</summary>

### 🔍 `MetaExtractor` Class

#### Overview

`MetaExtractor` class wraps the logic of different types of meta extractors (`EPUBMetaExtractor`, `MetsAltoMetsExtrator` and `LlamaMetaExtractor`) along with all text part classifiers (`EPUBTextPartClassifier`, `MetsAltoTextPartClassifier`, and `RegexTextPartClassifier`).

#### Importing

```python
from rara_meta_extractor.meta_extractor import MetaExtractor
```

#### Class Parameters

| Name                   | Type   | Optional | Default                                          | Description                                                          |
| ---------------------- | ------ |----------|--------------------------------------------------|----------------------------------------------------------------------|
| meta_extractor_config  | dict   | True*    | rara_meta_extractor.config.META_EXTRACTOR_CONFIG | Configuration for Llama's meta extractor agent.  |
| text_classifier_config | dict   | True*    | rara_meta_extractor.config.TEXT_CLASSIFIER_CONFIG| Configuration for Llama's text classifier agent. NB! Text classifier is used only for filtering the input passed to the meta extractor agent. However, this behaviour is disabled by default. |

* Although both params have default values, it is stronly recommended to ensure that correct `llama_host_url` is used.

All possible configuration parameters are listed in the table below:

##### Configuration Parameters

The following table lists all possible configuration params for `meta_extractor_config` and `text_classifier_config`.

| Name             | Type       | Required | Description                                    |
| ---------------- | ---------- |----------|------------------------------------------------|
| llama_host_url   |  str       | True     | Llama server URL, e.g. "http://localhost:8080" |
| instructions     |  str       | False    | Instructions for Llama.                        |
| fields           |  List[str] | False    | List of fields to extract. This is necessary to define only, if you wish to use a custom set of fields to extract opposed to the predefined ones. NB! If fields is defined, the JSON schema will be generated automatically. |
| json_schema      |  dict      | False    | JSON schema to use for generating grammars for Llama. NB! This is only necessary, if fields are not defined or you wish to use more advanced restrictions for them. The schema is not necessary for extracting default/predefined fields. Read more about the correct structure from here: https://github.com/ggml-org/llama.cpp/tree/master/grammars|
| temperature      |  float     | False    | Temperature in range [0, 2]. The lower the temperature, the more deterministic are the Llama outputs. By default = 0.0 |
| n_predict        |  int       | False    | Number of tokens Llama is allowed to predict. By default = 500. |

#### Key Functions

##### Function: `extract`

The main function for extracting meta information.

###### Parameters

| Name                   | Type       | Required | Default | Description    |
| ---------------------- | -----------| -------- | --------|----------------|
| texts                  | List[dict] | True     | -       | List of texts from where to extract meta information. For EPUB and METS/ALTO, expects content of `texts` from digitizer output. Otherwise, must minimally contain keys `text` and `lang`. |
| epub_metadata          | dict       | False    | {}      | Expects the content of `doc_meta.epub_metadata` from digitizer output. |
| mets_alto_metadata     | List[str]  | False    | []      | Expects the content of `doc_meta.mets_alto_metadata` from digitizer output. |
| verify_texts_with_llm  | bool       | False    | False   | If enabled, each text is passed to text classifier agent first and only texts classified as metadata blocks are passed to meta extractor(s). |
| n_trials               | int        | False    | 1       | Indicates how many trials to run for predicting metadata with LlamaExtractor for the same text. NB! Setting it higher than 1 has purpose only if temperature > 0.|
| merge_texts            | bool       | False    | True    | If enabled, texts are merged into a single text block before passing it to LlamaExtractor. Otherwise texts are passed one by one to LlamaExtractor and results are merged afterwards. |
| min_ratio              | float      | False    | 0.8     | Relevant only if n_trials > 1. Indicates the ratio of times a meta value has to be predicted during trials. E.g. if min_ratio = 0.7 and a value is predicted 2 out of 3 trials, it will not be returned as 2/3 = 0.66 < 0.7.|
| add_missing_keys       | bool       | False    | False   | If enabled, all possible meta keys are added to the output, even if the content has not been extracted. |
| detect_text_parts      | bool       | False    | True    | If enabled, runs text part detection for detecting conclusions, abstracts etc. |
| max_length_per_text    | int        | False    | 1500    | If verify_texts_with_llm is set to False, this param is used for dummy metadata detection -  if a text is longer than the threshold set with this param, it will not be included into Llama input. |
| n_first_pages          | int        | False    | 5       | How many first pages to consider for possible Llama input? NB! Not all of them are actually added to the input as the pages are passed through prefiltering. |
| n_last_pages           | int        | False    | 0       | How many last pages to consider for possible Llama input? NB! Not all of them are actually added to the input as the pages are passed through prefiltering. |
| n_strict_include       | int        | False    | 3       | Number of pages (out of n_first_pages + n_list_pages set) to pass to Llama  without additional prefiltering. |
| simple                 | bool       | False    | False   | If enabled, the outputs of titles and authors are simplified (some fields necessary mostly for constructing final MARC files are removed). |

###### Result

Function `extract` returns a dictionary with two keys:
- `extractor`- Indicates which extractor was used (possible values are: "Llama-Extractor", "EPUB-Extractor", and "METS/ALTO-Extractor")
- `meta` - Extracted metainformation formatted as dict.

##### Function: `extract_from_digitizer_output`

This function allows passing raw digitizer output to the meta extractor.

###### Parameters

| Name                   | Type       | Required | Default | Description    |
| ---------------------- | -----------| -------- | --------|----------------|
| digitizer_output       | dict       | True     | -       | Output of rara-digitizer. |
| verify_texts_with_llm  | bool       | False    | False   | If enabled, each text is passed to text classifier agent first and only texts classified as metadata blocks are passed to meta extractor(s). |
| n_trials               | int        | False    | 1       | Indicates how many trials to run for predicting metadata with LlamaExtractor for the same text. NB! Setting it higher than 1 has purpose only if temperature > 0.|
| merge_texts            | bool       | False    | True    | If enabled, texts are merged into a single text block before passing it to LlamaExtractor. Otherwise texts are passed one by one to LlamaExtractor and results are merged afterwards. |
| min_ratio              | float      | False    | 0.8     | Relevant only if n_trials > 1. Indicates the ratio of times a meta value has to be predicted during trials. E.g. if min_ratio = 0.7 and a value is predicted 2 out of 3 trials, it will not be returned as 2/3 = 0.66 < 0.7.|
| add_missing_keys       | bool       | False    | False   | If enabled, all possible meta keys are added to the output, even if the content has not been extracted. |
| detect_text_parts      | bool       | False    | True    | If enabled, runs text part detection for detecting conclusions, abstracts etc. |
| max_length_per_text    | int        | False    | 1500    | If verify_texts_with_llm is set to False, this param is used for dummy metadata detection -  if a text is longer than the threshold set with this param, it will not be included into Llama input. |
| n_first_pages          | int        | False    | 5       | How many first pages to consider for possible Llama input? NB! Not all of them are actually added to the input as the pages are passed through prefiltering. |
| n_last_pages           | int        | False    | 0       | How many last pages to consider for possible Llama input? NB! Not all of them are actually added to the input as the pages are passed through prefiltering. |
| n_strict_include       | int        | False    | 3       | Number of pages (out of n_first_pages + n_list_pages set) to pass to Llama  without additional prefiltering. |
| simple                 | bool       | False    | False   | If enabled, the outputs of titles and authors are simplified (some fields necessary mostly for constructing final MARC files are removed). |

###### Result

Function `extract` returns a dictionary with two keys:
- `extractor`- Indicates which extractors were used (possible values are a combination of the following: "Llama-Extractor", "EPUB-Extractor", and "METS/ALTO-Extractor")
- `meta` - Extracted metainformation formatted as dict.

</details>

## 🔍 Usage Examples

<details><summary>Click to expand</summary>

### Example 1: Simple meta extraction


```python
from rara_meta_extractor.meta_extractor import MetaExtractor
from pprint import pprint

test_text = """
Original title:\nHilarious Stories of Animals\n   \n \nCopyright © 2021 Creative Arts Management OÜ\nAll rights reserved.\n \nEditor: KRISTO VILLEM\n \n \nISBN   978-9916-665-46-6\n \n \n\nLiza Moonlight\n\nGreetings, friends! This story will teach you the ever\nchanging flow of time. As time passes, so do the seasons.\nThere are many lovely  things to each season and each of\nthem holds many secrets and surprises.  \nEnjoy these tales and hopefully you will also discover\nsomething new!\n\nEverything that surrounds us has patterns. As the day\nalways follo ws the night and the sun always sets and then\nrises, the seasons also follow one another. The first season of\nour book's cycle is Spring. It a time of many new beginnings.\nBirds return  to their homeplaces and the sun start to give\nmore and more warmth. Chippy the Bird will be Your guide!\n\nIt is probably no surprise that the thrilly easter rabbit\nfamily comes out to enjoy the sun and play around on the\nwarm grass. They have been sitting snugly in their\nburrows for the whole winter and are so very happy to be\noutside and hop around and flop their ears.
"""

meta_extractor = MetaExtractor(
   meta_extractor_config = {
      "llama_host_url"="http://local-llama:8080"
   text_classifier_config = {
      "llama_host_url"="http://local-llama:8080"
   }
)
texts = [{"text": test_text, "lang": "en"}]

extracted_info = meta_extractor.extract(texts=texts, simple=True)

pprint(extracted_info)
```

**Output:**

```JSON
{
  "extractor": ["Llama-Extractor"],
  "meta": {
    "authors": [
      {
        "name": "Liza Moonlight",
        "role": "Autor"
      },
      {
        "name": "Kristo Villem",
        "role": "Toimetaja"
      }
    ],
    "distributer_name": "Creative Arts Management OÜ",
    "distribution_place": "Tallinn",
    "isbn": [
      "9789916665466",
      "9789916665473",
      "9789916665480",
      "9789916665497"
    ],
    "titles": [
      {
        "title": "Hilarious stories of animals",
        "title_type": "main_title"
      },
      {
        "title": "4 books in 1 /",
        "title_type": "additional_title_part"
      }
    ],
    "udc": [
      "821-9-32",
      "821.111",
      "474.2)-93-322.4"
    ],
    "udk": [
      "821-93"
    ]
  }
}
```

### Example 2: Run multiple trials


```python
from rara_meta_extractor.meta_extractor import MetaExtractor
from pprint import pprint

test_text = """
1KUMMITUS
KURGUSDoireann Ní Ghríofa
kummitus
kurgusDoireann Ní Ghríofa
Inglise keelest tõlkinud Krista Kaer
kummitus
kurgusDoireann Ní Ghríofa
Inglise keelest tõlkinud Krista Kaer
Raamatu väljaandmist on toetanud Iiri Kirjandusfond
ja Eesti Kultuurkapital
Originaali tiitel:
Doireann Ní Ghríofa
A Ghost in the Throat
Tramp Press
2020
Copyright © Doireann Ní Ghríofa, 2020
Kõik õigused kaitstud
Tõlge eesti keelde © Krista Kaer, 2024
Poeemi „Itk Art O’Leary surma puhul” gaeli keelest tõlkinud Indrek Õis
Toimetanud ja korrektuuri lugenud Eha Kõrge
Kujundanud Britt Urbla Keller
ISBN 978-9985-3-6045-3
Kirjastus Varrak
Tallinn, 2024
www.varrak.ee
www.facebook.com/kirjastusvarrak
Trükikoda OÜ Greif
"""

meta_extractor = MetaExtractor(
   meta_extractor_config = {
      "llama_host_url"="http://local-llama:8080",
      "temperature": 0.1  #Raise temperature a bit to make the output less deterministic
   text_classifier_config = {
      "llama_host_url"="http://local-llama:8080"
   }
)
texts = [{"text": test_text, "lang": "et"}]

extracted_info = meta_extractor.extract(texts=texts, n_trials=7, min_ratio=0.7)

pprint(extracted_info)
```

**Output:**

```JSON
{"extractor": ["Llama-Extractor"],
 "meta": {"authors": [{"is_primary": false,
                       "name": "Krista Kaer",
                       "name_order": 0,
                       "role": "Tõlkija",
                       "type": ""},
                      {"is_primary": false,
                       "name": "Indrek Õis",
                       "name_order": 0,
                       "role": "Tõlkija",
                       "type": ""},
                      {"is_primary": false,
                       "name": "Eha Kõrge",
                       "name_order": 0,
                       "role": "Toimetaja",
                       "type": ""},
                      {"is_primary": false,
                       "name": "Britt Urbla Keller",
                       "name_order": 0,
                       "role": "Kujundaja",
                       "type": ""},
                      {"is_primary": false,
                       "name": "Varrak",
                       "name_order": 0,
                       "role": "Väljaandja",
                       "type": ""}],
          "edition_info/number": "est",
          "host_entry": {"name": "",
                         "part_number": "",
                         "publication_date": "2024"},
          "isbn": ["9789985360453"],
          "issue_type": "Raamat",
          "manufacture_place": "([Lohkva (Tartumaa)]",
          "manufacturer": "Greif",
          "publication_date": "2024",
          "publication_place": "Tallinn",
          "series": {"issn": "", "name": "", "volume": ""},
          "table_of_contents": {"content": [], "language": ""},
          "text_parts": [],
          "titles": [{"author_from_title": "",
                      "part_number": "",
                      "part_title": "[romaan]",
                      "skip": 0,
                      "title": "Kummitus kurgus",
                      "title_language": "et",
                      "title_type": "väljaandes esitatud kujul põhipealkiri",
                      "title_type_int": 245,
                      "version": ""}],
          "udk": ["821"]}
}
```

</details>
