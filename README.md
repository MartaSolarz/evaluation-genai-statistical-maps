# Evaluating Multimodal Large Language Models in Statistical Map Understanding: A Systematic Assessment in Reading, Analysis, and Interpretation

## Abstract
Statistical maps remain invaluable tools for visualizing the spatial distribution of quantitative phenomena. The recent development of Multimodal Large Language Models (MLLMs), capable of processing both images and text, holds promise to automate analytical procedures and support cartographic work. However, their ability to extract and interpret cartographic information remains largely unexplored, presenting a challenge for integrating these technologies into cartographic workflows. In this study, we evaluate the capability of twelve MLLMs to acquire information from statistical maps across three map use levels: map reading, analysis, and interpretation. We explored models' performance across map properties (cartographic method multiplicity, spatial units aggregation, map source, map types), task types, and prompting procedures. The study points out that MLLMs excelled in interpretation tasks (M=3.79/5), scored worse in analytical pattern discernment (3.03/5), and performed weakest in accurate value extraction during map reading (2.83/5). Moreover, model selection and map characteristics significantly affected response quality. The findings reveal that MLLMs compensate for visual processing limitations through extensive pre-trained geographic knowledge, enabling strong contextual reasoning despite weak data extraction. This represents a different cognitive pathway than human map reading, which proceeds hierarchically from symbol recognition through pattern analysis to interpretation. Our results have practical implications for cartographic workflows: MLLMs currently suit qualitative description and preliminary pattern analysis but require human verification for quantitative data retrieving. The systematic evaluation framework provides a foundation for assessing future model iterations and expanding evaluation to other cartographic contexts.

**Keywords:** Multimodal Large Language Models, Generative Artificial Intelligence, Statistical maps, Map understanding, Spatial data interpretation, GeoAI.

## Repository Structure

```
data/
├── cleaned_data/         # Analysis-ready extracts (batch and iterative modes)
├── raw_data/             # NOT DISTRIBUTED - see "Data" below
└── models.csv            # Model metadata

descriptive_analysis/
└── tables.ipynb          # Descriptive statistics tables

statistical_analysis/
├── batch_only/           # Batch-only analysis
│   ├── tests.ipynb       # Statistical tests (main effects, map characteristics, interactions)
│   └── visualizations.ipynb
└── batch_vs_iterative/   # Comparative analysis
    ├── tests.ipynb       # Statistical tests (overall effects, moderation, intercorrelations)
    └── visualizations.ipynb

cld_analysis/
└── cld_task_type.py      # Compact letter display for task-type comparisons

sensitive_analysis/
└── sensitivity_analysis_weights.py   # RQI robustness under alternative weighting schemes

results/                  # All generated output
├── plots/                # Figures
├── tables/               # Statistical tables
└── *.csv, *.txt          # Summary statistics
```

Code lives in the directory of the analysis it belongs to; every generated artefact is
written to `results/`. Both scripts resolve their paths relative to their own location, so
they can be run from any working directory.

## Data

The analysis-ready extracts in `data/cleaned_data/` are included here, so every notebook
and `cld_analysis/cld_task_type.py` run out of the box.

The full response-level dataset is **not** distributed with this code. It is archived
separately in the University of Warsaw Research Data Repository under a CC BY 4.0 licence:

    https://doi.org/10.58132/GH6PGQ

Only one script needs it - `sensitive_analysis/sensitivity_analysis_weights.py`, which
recomputes the Response Quality Index under alternative weighting schemes. To run it,
download `data.tsv` from the repository above and place it at:

    data/raw_data/data.tsv

The accompanying `CODEBOOK.md`, which documents all 34 variables, is available from the
same record.

## Requirements

Python 3.11.5. Install pinned dependencies with:

    pip install -r requirements.txt

## Usage

Run the Jupyter notebooks in order:
1. `descriptive_analysis/tables.ipynb`
2. `statistical_analysis/batch_only/tests.ipynb` and `visualizations.ipynb`
3. `statistical_analysis/batch_vs_iterative/tests.ipynb` and `visualizations.ipynb`

Then run the supporting scripts, from anywhere:
4. `python cld_analysis/cld_task_type.py`
5. `python sensitive_analysis/sensitivity_analysis_weights.py` (requires `data/raw_data/data.tsv`, see "Data")

Results are saved in the `results/` directory.
