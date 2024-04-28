# Deep DETER 🌳🫸 🔥

#### Using Satellite 🛰️ remote sensing  and Deep Learning to automatically detect illegal deforestation in the Amazon rainforest.

#### Project created and submitted by Vitor Luiz Schipani as the final project for the [CS7643 - Deep Learning](https://omscs.gatech.edu/cs-7643-deep-learning) course from the Georgia Institute of Technology (Georgia Tech). This is part of the Master's in Computer Science degree program.

## What is this project about?
The Amazon Rainforest covers over 5 million square kilometers and represents half of Earth's remaining Rainforests. However rampant deforestation, man-made wildfires, illegal expansion of soy and cattle farms and mining activities are a significant cause for concern, see \cite{Oliveira2020Forest} for a review of these unsustainable practices. Keeping as much of the original tree coverage intact is important to keep it functioning as a forest (i.e.: regulating the climate, being the ancestral home of Indigenous tribes and hosting wildlife).

The repercussions of the degradation of the Amazon Rainforest can go beyond the forest given its complex interactions with the world climate. The loss of a significant tract of the forest can have irreversible negative consequences such as the acceleration of desertification, reduction in crop yields and perturbations in rainfall patterns in unexpected ways across distant regions.

## Why Deep Learning?
Deep Learning is an efficient way of intepreting satellite imagery without requiring Human labeling.

## Which sources of data are used to train the model?
Two sources of data are leveraged for training this model:
1. For the **labels (model targets)** we use data made available by the **PRODES** and the **DETER** program from INPE (See section below for more information about these programs).
2. For the **features (the actual satellite pictures)** Sentinel-2 data was used. Sentinel-2 data is made available by the Copernicus
Programme of the European Union. The data is accessed through Google's Earth Engine API through its Python Client.

## How can I run the project myself?
See the **SETUP** section at the bottom of this README for the necessary steps.


## Project Structure
```
├── LICENSE
├── Makefile                                <- Make sure you first configure and activate the Conda environment and are in the project root directory first.
├── README.md                               <- The top-level README.
├── data
│   ├── external                            <- Data from PRODES and DETER programs.
│   ├── raw                                 <- Original data pulled from Earth Engine API.
│   ├── processed                           <- Processed data with all .tif bands joined together and Labels.
│   ├── model_inputs                        <- These are the data_files split into train/test.
│   ├── images                              <- .png files including model features (satellite images).
│   └── model_result                        <- Model results as .tif files.
│
├── environment.yaml                        <- Used to install necessary packages. See setup section on how to use this file.
│
└── deep_deter                              <- Source code for use in this project.
    │
    ├── data_extraction                     <- All scripts related to extracting data.
    │   ├── main.py                         <- USE THIS ONE. Do not run directly the other scripts.
    │   ├── custom_error.py
    │   ├── fetch_sentinel_img.py
    │   ├── mask_feature_bands.py
    │   ├── mask_label.py
    │   ├── mask_sentinel_img.py
    │   ├── plotting_utils.py
    │   ├── save_to_disk.py
    │   ├── train_test_split.py
    │   └── utils.py
    │
    └── deep_model                          <- Scripts to train the deep learning model.
        ├── train.py                        <- USE THIS ONE. Do not run directly the other scripts.
        ├── dataset.py
        ├── model.py
        └── utils.py
```

## SETUP
### Setting up the environment
First activate Conda and install the environment:

> make install_env

or

> conda env create -f environment.yaml
