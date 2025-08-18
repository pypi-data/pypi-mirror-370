# doteval-datasets

Standard datasets for [dotevals](https://github.com/dottxt-ai/dotevals) LLM evaluations.

## Installation

```bash
pip install dotevals-datasets
```

## Usage

Once installed, the datasets are automatically available in doteval:

```python
from dotevals import foreach

@foreach.bfcl("simple")
def eval_bfcl(question: str, schema: list, answer: list):
    # Your evaluation logic here
    pass

@foreach.gsm8k("test")
def eval_gsm8k(question: str, reasoning: str, answer: str):
    # Your evaluation logic here
    pass

@foreach.sroie("test")
def eval_sroie(image: Image, entities: dict):
    # Your evaluation logic here
    pass
```

## Available Datasets

- **BFCL** (Berkeley Function Calling Leaderboard): Tests function calling capabilities
  - Variants: `simple`, `multiple`, `parallel`
  - Columns: `question`, `schema`, `answer`

- **GSM8K**: Grade school math word problems
  - Splits: `train`, `test`
  - Columns: `question`, `reasoning`, `answer`

- **SROIE**: Scanned receipts OCR and information extraction
  - Splits: `train`, `test`
  - Columns: `image`, `address`, `company`, `date`
