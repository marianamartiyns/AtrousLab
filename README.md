#  ꫂ❁ AtrousLab

> A web-based image processing project for applying **dilated correlation on 24-bit RGB images** using external masks, configurable parameters, and a manual processing pipeline.

### 📋 Project Overview

This repository contains a complete system for **RGB image filtering through dilated correlation**, combining:

1. **Backend in FastAPI**
   - Handles image upload, configuration parsing, mask loading, processing pipeline execution, and output generation.
   - Applies the filter independently to the **R**, **G**, and **B** channels.

2. **Frontend in React + TypeScript**
   - Provides a web interface for uploading the image and configuration files.
   - Displays the generated output image and execution logs.

https://github.com/user-attachments/assets/5158b5b3-f278-465d-ad92-c092db5ccd01

The project was designed to explore fundamental concepts of **digital image processing**, such as correlation, dilation, stride, activation functions, and edge detection with Sobel operators.

### 🎯 Objective

The goal of AtrousLab is to implement a system capable of:

- opening **24-bit RGB images**;
- loading external masks from `.txt` files;
- reading execution parameters from a `.json` file;
- applying **dilated 2D correlation** independently to each RGB channel;
- allowing configuration of:
  - `stride`
  - `r` (dilation rate)
  - activation function
  - filter type
- applying specific post-processing for Sobel filters;
- displaying and saving the processed image.

### ⚙️ Main Features

* [x] Load `.png`, `.tif`, and `.tiff` images
* [x] Convert input images to **RGB 24 bits**
* [x] Split image into **R, G, B channels**
* [x] Apply **manual dilated correlation** without padding
* [x] Support for activation functions:
  * `relu`
  * `identity`
* [x] Apply Sobel post-processing:
  * absolute value
  * linear expansion to `[0,255]`
* [x] Save processed outputs automatically in `/outputs`
* [x] Return execution logs for analysis/debugging
* [x] FastAPI backend for processing
* [x] React frontend for file upload and result visualization

### 🧱 Project Structure

```text
ATROUSLAB/
├── app/
│   ├── __pycache__/
│   ├── main.py
│   ├── routes.py
│   ├── runner.py
│   └── settings.py
│
├── outputs/
│
├── src/
│   ├── backend/
│   │   ├── activation/
│   │   ├── config/
│   │   ├── io/
│   │   ├── math/
│   │   └── pipeline/
│   │
│   └── frontend/
│       ├── components/
│       │   ├── RunInputCard.tsx
│       │   └── RunOutputCard.tsx
│       ├── node_modules/
│       ├── pages/
│       │   └── RunFilter.tsx
│       ├── public/
│       ├── App.tsx
│       ├── index.css
│       ├── index.html
│       ├── main.tsx
│       ├── package-lock.json
│       ├── package.json
│       ├── styles.css
│       └── tailwind.config.js
```

> [!NOTE]
> The report and project documentation are written in **Portuguese**, while variable names, file names, and code structure remain mostly in **English** for better technical organization and clarity.

<img align="right" width="40px" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg">
<img align="right" width="40px" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/typescript/typescript-original.svg">
<img align="right" width="40px" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/tailwindcss/tailwindcss-original.svg">
<img align="right" width="40px" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg">
<img align="right" width="40px" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg">
<img align="right" width="40px" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/numpy/numpy-original.svg">
