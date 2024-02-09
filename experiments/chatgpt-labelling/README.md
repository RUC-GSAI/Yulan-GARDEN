# ChatGPT labelling

## Quick Start

Install the dependencies simply run the following command:
```bash
pip install -r ../../requirements.txt
```

You should first prepare OpenAI API key to initialize an object of class ``GPTEvaluator``. 

Then you should move the raw and refined data into the directory corresponding to the variables in code ``raw_path`` and ``refined_path``.

Therefore, you can simply run out ChatGPT labelling code by:

```
python GPTEvaluator.py
```