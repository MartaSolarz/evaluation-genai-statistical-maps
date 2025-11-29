# Evaluating Multimodal Large Language Models in Statistical Map Understanding: A Systematic Assessment in Reading, Analysis, and Interpretation

## Abstract
Statistical maps remain invaluable tools for visualizing the spatial distribution of quantitative phenomena. The recent development of Multimodal Large Language Models (MLLMs), which can handle both visual input and text, holds promise to automate analytical procedures and support human capability in cartography. Maps thus serve as sources of information acquired, analyzed, and interpreted by both human users and AI models. However, the extent to which MLLMs can effectively extract and interpret cartographic information remains largely unexplored, presenting a critical challenge for integrating these technologies into cartographic workflows. In this study, we systematically evaluate the capability of twelve multimodal generative AI models to acquire information from statistical maps in the three map use levels , i.e., map reading, map analysis, and map interpretation. We explored models' performance across map properties (graphical complexity, spatial units aggregation, map source, map types), task types, and the modes used to test model–user interactions. The study points out that there exists an inverse hierarchy in capability of MLLMs to acquire information from statistical maps and thus understand maps , i.e., MLLMs excelled in interpretation tasks (mean = 3.69/5), scored worse in analytical discernment of patterns (3.03/5), and collected worst scores in accurate value extraction in map reading (2.83/5). Commercial and US-based models generally outperformed free or Chinese models, and made with a single map type, country-level maps yielded superior scores over more complex maps with smaller enumeration units. The findings reveal that MLLMs compensate for visual processing limitations through extensive pre-trained geographic knowledge, enabling strong contextual reasoning despite weak quantitative extraction. This represents a different cognitive pathway than human map reading, which proceeds hierarchically from symbol recognition through pattern analysis to interpretation. Our results have practical implications for cartographic workflows: MLLMs currently suit qualitative description and preliminary pattern analysis but require human verification for quantitative data retrieving. The systematic evaluation framework provides a foundation for assessing future model iterations and expanding evaluation to other cartographic contexts.

**Keywords:** Multimodal Large Language Models, Generative Artificial Intelligence, Statistical maps, Map understanding, Spatial data interpretation, GeoAI.

## Repository Structure

```
data/
├── cleaned_data/          # Experimental data (batch and iterative modes)
└── models.csv            # Model metadata

descriptive_analysis/
└── tables.ipynb          # Descriptive statistics tables

statistical_analysis/
├── batch_only/           # Batch-only analysis
│   ├── tests.ipynb      # Statistical tests (main effects, map characteristics, interactions)
│   └── visualizations.ipynb
└── batch_vs_iterative/   # Comparative analysis
    ├── tests.ipynb      # Statistical tests (overall effects, moderation, intercorrelations)
    └── visualizations.ipynb

results/
├── plots/                # Figures
├── tables/               # Statistical tables
└── *.csv                 # Summary statistics
```

## Requirements

- pandas, numpy
- matplotlib, seaborn
- scipy, statsmodels
- scikit-learn, scikit-posthocs

## Usage

Run the Jupyter notebooks in order:
1. `descriptive_analysis/tables.ipynb`
2. `statistical_analysis/batch_only/tests.ipynb` and `visualizations.ipynb`
3. `statistical_analysis/batch_vs_iterative/tests.ipynb` and `visualizations.ipynb`

Results are saved in the `results/` directory.

