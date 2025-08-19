<!--
IMPORTANT NOTE:
- This file will get rendered in the public facing PyPi page here: https://pypi.org/project/orca_sdk/
- Only content suitable for public consumption should be placed in this file everything else should go into CONTRIBUTING.md
-->

# OrcaSDK

OrcaSDK is a Python library for building and using retrieval-augmented models with [OrcaCloud](https://orcadb.ai). It enables you to create, deploy, and maintain models that can adapt to changing circumstances without retraining by accessing external data called "memories."

## Documentation

You can find the documentation for all things Orca at [docs.orcadb.ai](https://docs.orcadb.ai). This includes tutorials, how-to guides, and the full interface reference for OrcaSDK.

## Features

- **Labeled Memorysets**: Store and manage labeled examples that your models can use to guide predictions
- **Classification Models**: Build retrieval-augmented classification models that adapt to new data without retraining
- **Embedding Models**: Use pre-trained or fine-tuned embedding models to represent your data
- **Telemetry**: Collect feedback and monitor memory usage to optimize model performance
- **Datasources**: Easily ingest data from various sources into your memorysets

## Installation

Orca SDK is compatible with Python 3.10 or higher and is available on [PyPI](https://pypi.org/project/orca_sdk/). You can install it with your favorite python package manager:

- Pip: `pip install orca_sdk`
- Conda: `conda install orca_sdk`
- Poetry: `poetry add orca_sdk`

## Quick Start

```python
from dotenv import load_dotenv
from orca_sdk import OrcaCredentials, LabeledMemoryset, ClassificationModel

# Load your API key from environment variables
load_dotenv()
assert OrcaCredentials.is_authenticated()

# Create a labeled memoryset
memoryset = LabeledMemoryset.from_disk("my_memoryset", "./data.jsonl")

# Create a classification model using the memoryset
model = ClassificationModel("my_model", memoryset)

# Make predictions
prediction = model.predict("my input")

# Get Action Recommendation
action, rationale = prediction.recommend_action()
print(f"Recommended action: {action}")
print(f"Rationale: {rationale}")

# Generate and add synthetic memory suggestions
if action == "add_memories":
    suggestions = prediction.generate_memory_suggestions(num_memories=3)

    # Review suggestions
    for suggestion in suggestions:
        print(f"Suggested: '{suggestion['value']}' -> {suggestion['label']}")

    # Add suggestions to memoryset
    model.memoryset.insert(suggestions)
    print(f"Added {len(suggestions)} new memories to improve model performance!")
```

For a more detailed walkthrough, check out our [Quick Start Guide](https://docs.orcadb.ai/quickstart-sdk/).

## Support

If you have any questions, please reach out to us at support@orcadb.ai.
