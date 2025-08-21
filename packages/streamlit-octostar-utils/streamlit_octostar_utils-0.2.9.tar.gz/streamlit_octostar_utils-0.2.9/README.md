## How To Install
Base Package:
`pip install streamlit-octostar-utils`

NLP Additional Dependencies:
`pip install streamlit-octostar-utils[nlp]`

## Code formatting
This project uses `black` for code formatting. To format the code, run:
`black .` \
You can also install the Microsoft official Black extension for VSCode [here](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter). \
This will format the code automatically when you save a file.


## Developer Guide
Local Development Setup (MacOS):
```bash
pyenv local
python -m venv venv
. venv/bin/activate
pip install poetry
poetry install
```
