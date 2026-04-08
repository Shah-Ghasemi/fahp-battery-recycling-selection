# Fuzzy AHP for Lithium-Ion Battery Recycling Technology Selection

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Research%20Project-orange)
![Method](https://img.shields.io/badge/Method-FAHP-purple)
![Domain](https://img.shields.io/badge/Domain-Circular%20Economy-blueviolet)
![Focus](https://img.shields.io/badge/Focus-Sustainability-brightgreen)


## 📌 Overview
This project presents a Fuzzy Analytic Hierarchy Process (FAHP) model for evaluating and prioritizing lithium-ion battery recycling technologies based on expert judgments.

The methodology is implemented in Python and includes consistency checking, criteria weighting, and ranking analysis.

## 🎯 Objectives
- Evaluate alternative lithium-ion battery recycling methods
- Handle uncertainty in expert judgments using fuzzy logic
- Compute criteria weights and ensure consistency
- Provide a structured decision-making framework

## 🧠 Methodology
- Fuzzy AHP based on established methods from the literature
- Expert-based pairwise comparisons
- Consistency ratio calculated using Python
- Hierarchical decision structure (AHP)

This implementation is informed by a comprehensive review of FAHP methods:

Liu, Y., Eckert, C. M., & Earl, C. (2020).
## 📂 Project Structure
```text
project-root
│
├── src/                # Python implementation
├── data/               # Expert input data (Excel files) 
├── results/            # Output results (charts, weights)
├── docs/               # AHP structure and documentation 
├── requirements.txt    # Required Python libraries
└── README.md
```
## ⚙️ Requirements
Install dependencies using:

```bash
pip install -r requirements.txt
```
## ▶️ How to Run
1. Place input Excel files in the data/ folder
2. Run the main script:
```bash
python src/fahp_main.py
```
## 📊 Outputs
- Criteria weights
- Consistency ratio
- Ranking results (not publicly shared)
### ⚠️ Note
The ranking of alternatives is not included because the compiled methods from the systematic literature review are novel.
## 📷 Decision Hierarchy
The hierarchical decision structure used in the FAHP model is available in:

`docs/ahp_structure.png`

The structure illustrates the relationship between decision criteria and evaluated alternatives.
## 👤 Author
Shahrokh Ghasemi
## Acknowledgment
This code was developed as part of a collaborative research project on lithium-ion battery recycling technology selection.
## 📄 License
MIT License
## 📚 References
Liu, Y., Eckert, C. M., & Earl, C. (2020). 
A review of fuzzy AHP methods for decision-making with subjective judgements. 
Expert Systems with Applications, 161, 113738.
