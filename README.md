# EOB PDF Extraction

## Overview
This project extracts Explanation of Benefits (EOB) details from PDF documents and converts them into a structured JSON format using **LlamaParser** and **Vertex AI Gemini-2.0-Pro Exp** model.

## Project Structure
The project consists of three main Python files:

- **code.py**: The main script to run for data extraction.
- **parser.py**: Handles PDF conversion using LlamaParser.
- **prompts.py**: Contains designed prompts.

## Workflow
1. **Initialize Model**: The script initializes the Gemini model via Vertex AI.
2. **User Input**: User provides the path to the PDF document and an output folder where the JSON file will be saved.
3. **PDF Parsing**:
   - The PDF is saved temporarily and processed using LlamaParser.
   - LlamaParser converts the PDF into markdown text (using **GPT-4o** for improved accuracy).
4. **Data Extraction**:
   - The text is passed to the **Gemini model** with a carefully crafted prompt to extract **EOB details and unique claim numbers**.
   - For each extracted claim number, another prompt extracts **patient details** and **service line items**.
5. **JSON Generation**: All responses are aggregated into a structured JSON file representing the entire PDF.

## Requirements
- Python 3.11.9
- Google Vertex AI SDK
- LlamaParser

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python code.py 
```

## Output
The extracted data is saved as a JSON file in the specified output folder.

## Notes
- **GPT-4o mode** is used for PDF conversion, which is more accurate but incurs higher costs than the standard mode.
- Ensure you have the necessary API access for both **Vertex AI Gemini** and **LlamaParser**.

