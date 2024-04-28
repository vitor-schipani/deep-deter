# Deep DETER 🌳🫸 🔥🪓

#### Using Satellite 🛰️ remote sensing  and Deep Learning to automatically detect illegal deforestation in the Amazon rainforest.

#### Project created and submitted by Vitor Luiz Schipani as the final project for the [CS7643 - Deep Learning](https://omscs.gatech.edu/cs-7643-deep-learning) course from the Georgia Institute of Technology (Georgia Tech). This is part of the Master's in Computer Science degree program.

## What is this project about?
This project is an application of a **Semantic Segmentation** deep neural network architecture
(more specifically the uNet model proposed by <add citation here>) to detect deforestation in the Brazilian 
Legal Amazon region.

## Why Deep Learning?
The Legal Amazon region covers over 5 million square kilometers

## Which sources of data are used to train the model?
Two sources of data are leveraged for training this model:
1. For the **labels (model targets)** we use data made available by the **PRODES** and the **DETER** program from INPE (See section below for more information about these programs).
2. For the **features (the actual satellite pictures)** Sentinel-2 data was used. Sentinel-2 data is made available by the Copernicus
Programme of the European Union. The data is accessed through Google's Earth Engine API through its Python Client.

## What is currently being done by the Brazilian authorities? What is the novel contribution this brings?
DETER is the Near Real-Time deforestation detection program from INPE (Brazil's National Institute for Spatial Research).

## How can I run the project myself?
See the **SETUP** section at the bottom of this README for the necessary steps.


## Project Structure
```
├── LICENSE
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── data           <- Scripts to download or generate data
│   │   └── make_dataset.py
│   │
│   ├── features       <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   │
│   ├── models         <- Scripts to train models and then use trained models to make
│   │   │                 predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   │
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
│
└── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
```

## SETUP