# Agentic AI - Article Analyzer

This system is to autonomously summarize and analyze the given research paper, offering both concise section-wise insights and a finalized overview. 
It supports researches, students, and reviewers by automating the often time-consuming initial review process of scientific articles.


## Technical Report
https://discovered-duck-af0.notion.site/Task-2-Automated-Research-Paper-Analysis-and-Summarization-244066d9a43380619131de2c1655e295


## Features
- Parses scientific articles into structured sections
- Builds graph-based semantic relationships between sections
- Generates extractive summaries
- Generates critical analysis
- Modular pipeline (integration -> parsing -> summarize & analyze simultaneously -> finalization


## Modules
- ingester.py	=> Handles file loading (PDF, TXT, etc.)
- parser.py	=> Splits and organizes article sections
- build_graph.py => Builds semantic graph from sections
- summarizer.py => Generates summary from parsed content
- finalizer.py => Cleans and formats the final output


## Installation
1. Clone the git
2. (Optional) Create a virtual environment
   - python -m venv venv
   - source venv/bin/activate  # or venv\Scripts\activate on Windows
3. Install dependencies
   - pip install -r requirements.txt
4. Add OpenAI API key
   - make .env file and add key
   - OPENAI_API_KEY=your_key
4. Run the file
   - python app/main.py
   - It will run the test articles stored in /docs.

