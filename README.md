# Karpin Chat

This repository contains a chatbot that answers questions related to electoral bonds. The chatbot can be run as a Python script or deployed as a Streamlit application.

## Block Diagram

![Block diagram of the Chat Application](block_diagram.drawio.svg)

## Setup Instructions

### Create a Conda Environment

First, create and activate a new conda environment:

```bash
conda create -n electoral_bonds_chatbot python=3.10
conda activate electoral_bonds_chatbot
```

### Install Requirements

Install the required packages using the requirements.txt file:

```bash
pip install -r requirements.txt
```

### Running the PDF to CSV script

Change the _pdf_path_ and _csv_path_ in *pdf_2_csv.py* to generate the csv from pdf file.

```bash
python pdf_2_csv.py
```

### Setting Up Groq
1. Go to https://groq.com/.
2. Sign In using your favourite Email Id.
3. Click on GroqCloud.
4. Create an API Key with name "chatbot".
5. Copy the API Key and add it in _script.py_ and *chat_app.py*

Additional documentation can be found at https://console.groq.com/docs/quickstart.

### Running the Python Script

To run the Python script, make sure that questions.txt is present in the existing directory. This script will read the questions from questions.txt and generate answers in answers.txt.

```bash
python script.py
```

### Deploying the Application Locally

To deploy the chatbot as a Streamlit application locally, run the following command:

```bash
streamlit run chat_app.py
```

### Screenshot of the Application

![Screenshot of the Chat Application](screenshot.png)