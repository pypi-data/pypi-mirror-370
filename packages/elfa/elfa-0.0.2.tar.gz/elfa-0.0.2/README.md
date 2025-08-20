# Explainable Layer Factor Analysis for CNNs (ELFA-CNNs)

**Convolutional Neural Networks (CNNs) interpretability through the analysis of the encoded features.**

---

**ELFA** (Explainable Layer Factor Analysis) is an explanatory method which identifies the *essential features* underlying convolutional layers. Given a convolution and relying on factor analysis, ELFA provides:

- A mathematically well-founded identification of the **essential underlying features**.
- A quantification of their **impact** on the original channels.
- **Insights** into how channels are related, their importance, and redundancy.
- A visualization of the essential features through the **Essential Attribution Maps (EFAM)** and the **intrinsic features inversion**.


As a result, ELFA obtains an *accurate and well-founded summary* of the features encoded in the convolutional layer. Moreover, it analyzes the layer as a whole, *avoiding* the choice of channels, and *guarantees* that the relevant features are being evaluated.

---

### Layer Factor Analysis

**Layer Factor Analysis** is a statistical method that describes convolutional layers by a factor analysis model. As part of the ELFA strategy, this proposal applies the mathematical concepts of factor analysis on convolutional layers to explain the encoded knowledge.

The adequacy of the data and the quality of the estimated models can be verified, for which novel validity metrics are defined.

The parameters of the factorial model are used to provide explanations.

---

### Citation

For a detailed description of technical details and experimental results, please refer to:

Clara I. López-González, María J. Gómez-Silva, Eva Besada-Portas, Gonzalo Pajares: [Layer factor analysis in convolutional neural networks for explainability](https://www.sciencedirect.com/science/article/pii/S1568494623011122)

If you use this, please cite:

 ```
@article{
LopezGonzalez2024ELFA,
title = {Layer factor analysis in convolutional neural networks for explainability},
author = {Clara I. López-González and María J. Gómez-Silva and Eva Besada-Portas and Gonzalo Pajares},
journal = {Applied Soft Computing},
volume = {150},
pages = {111094},
year = {2024},
issn = {1568-4946},
doi = {https://doi.org/10.1016/j.asoc.2023.111094},
}
```

## Project status

Project is under development but should be stable. Please expect interfaces to change in future releases.

## Installation

### Using `pip`

```bash
pip install elfa
```

## Documentation

Still under development.