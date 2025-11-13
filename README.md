# bias-detection-project
Bias detection project for Natural Language Processing.

## Setup

Set environment variables `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GOOGLE_API_KEY` to API key values from each model:

- **OpenAI API Key**: [Get your OpenAI API key](https://platform.openai.com/account/api-keys)  
- **Anthropic API Key**: [Get your Anthropic API key](https://console.anthropic.com/)  
- **Google API Key**: [Get your Google Cloud API key](https://console.cloud.google.com/apis/credentials)  

You can set them in your shell (Linux/Mac):

```bash
export OPENAI_API_KEY="your_openai_key_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"
export GOOGLE_API_KEY="your_google_key_here"
```

You can set them in your shell (Windows):

```bash
setx OPENAI_API_KEY="your_openai_key_here"
setx ANTHROPIC_API_KEY="your_anthropic_key_here"
setx GOOGLE_API_KEY="your_google_key_here"
```

## Install Dependencies

Before running the project, install the required Python packages:

```bash
pip install -r requirements.txt
python -m nltk.downloader punkt
```

## Running the Script

Once you have set your API keys, you can run the main script with:

```bash
python run-prompts.py [topic]
```

## Web scraping for sources

The tool can be ran with:

```bash
python source-scraping.py [topic]
```

## Quantifying the Bias

- **OpenAI API Key**: [Google doc]([https://platform.openai.com/account/api-keys](https://docs.google.com/document/d/1K_Mu3mVgmBHQOv3zoLz93A0RZUJ5Id2zbY-ZgI1PGYY/edit?tab=t.0))
