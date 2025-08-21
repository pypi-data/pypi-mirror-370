# Decision Tree algorithm from scratch
This repository contains Decision Tree implementation from scratch for classification problem.

## About
This Decision Tree implementation is based on **Leaf-wise algorithm**. 

- Supports **bins** hyperparameter for speeding up the algorithm.
- Supports **Feature Importance** calculation, which can help to understand the importance of features.
- Supports classification heuristics:
  - **Entropy** and **Information Gain**,
  - **Gini Impurity** and **Gini Gain**,
- Supports regression heuristics:
  - **MSE** and **MSE Gain**.

## Dependencies
To install all required dependencies, execute the following command:
```console
pip install requirements.txt
```

## Usage
To start main script, execute the following command:
```console
python main.py [OPTIONS]
```

### Available options
- **-e, --example** (required) - type of example to run. Available examples: classification.
- **-c, --config** (required) - path to configuration file.

## Tests
Test cases are placed in *tests/* folder. To run tests use pytest module with the following command:
```console
pytest tests/
```