<div align="center">  
  <img src="https://github.com/cldunlap73/BubbleID/blob/main/Images/header.png?raw=true" alt="Logo" style="width: 85%; max-width: 100%;">
</div>

[![bpypiv](https://img.shields.io/pypi/v/bubbleid)](https://pypi.org/project/bubbleid/)
![bpyv](https://img.shields.io/badge/python-3.10-blue)
[![boldv](https://img.shields.io/badge/tag-v1.0.0-blue)](https://github.com/cldunlap73/BubbleID/tree/v1.0.0)
[![blicense](https://img.shields.io/github/license/cldunlap73/seqreg)](https://github.com/cldunlap73/BubbleID/blob/main/LICENSE)
[![bpaper](https://img.shields.io/badge/paper-BubbleID-purple)](https://pubs.aip.org/aip/jap/article/136/1/014902/3300686/BubbleID-A-deep-learning-framework-for-bubble)

---


This package is for analyzing pool boiling images and is from the paper: [**BubbleID:A deep learning framework for bubble interface dynamics analysis**](https://pubs.aip.org/aip/jap/article/136/1/014902/3300686/BubbleID-A-deep-learning-framework-for-bubble). It combines tracking, segmentation, and classification models and is trained on manually labeled pool boiling data. It is used for departure classification, velocity interface prediction, bubble statistics extraction.

<p align="center">
  <img src="https://github.com/cldunlap73/BubbleID/blob/main/Images/Data.jpg?raw=true" alt="Example plots generated from framework" width="80%" />
</p>

* This is an updated version of BubbleID for the past version please see [here](https://github.com/cldunlap73/BubbleID/tree/v1.0.0).

## Installation:

* First download and install the latest [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
* Create a new enviroment with python 3.10, we used anaconda
* Update dependences:
  ```bash
  pip install --upgrade pip setuptools wheel
  ```
* Install [detectron2](https://github.com/facebookresearch/detectron2):
  ```bash
  pip install git+https://github.com/facebookresearch/detectron2
  ```
* Install Additional Dependencies:
  ```bash
  pip install numpy==1.23 opencv-python filterpy super-gradients
* Install BubbleID:
  ```bash
  pip install bubbleid
  ```

## Using the BubbleID Framework:
The BubbleID framework has pretrained models for our in lab pool boiling images. This section goes over how to use these models to analyze image data. These models may need finetuning with your own data. More on this is provided later. 

|Model|Weights|Description|
|----|-------|----------|
|Instance Segmentation|[Link](https://osf.io/uy2ad)|Model weights for the instance segmentation model.|
|Classification|Link|Model weights for the departure classification model.|

For the model both an avi video and corresponding .jpg images of each frame must be provided.

## Tutorials
* For convience, tutorials are provided in the github to demonstrate how to use BubbleID to generate your own data.
* The tutorials use the testing data found here: [![data1](https://img.shields.io/badge/testing%20data-red)](https://osf.io/3nwyx/)

## Training your own model:
1. Annotate image data, Lableme was used for our dataset.
2. Convert labelme dataset to yolo format
3. Run training
4. See Using the BubbleID Framework but use your new model weights
   

<p align="center">
  <img src="https://github.com/cldunlap73/BubbleID/blob/main/Images/velocityFigure.jpg?raw=true" alt="Example plots generated from framework" width="67%" />
</p>