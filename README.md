### Setup

You can set up the project environment to run the scripts with the following process (run from the root directory):

```
// Create virtual environmnet
python -m venv venv

// For Windows
venv/Scripts/activate
// For Linux
venv/bin/activate

// Install modules
pip3 install -r requirements.txt
```

### Appendix

Below is the project folder hierarchy to ease the navigation:
```
.
├── README.md
├── build
│   ├── fba.sh
│   ├── fva.sh
│   ├── genome.sh
│   ├── manim.sh
│   ├── memote.sh
│   ├── pfba.sh
│   └── setup.sh
├── data
│   ├── altered
│   │   ├── tables
│   │   │   └── stable
│   │   └── xmls
│   │       ├── MNL_iCre1355_auto_GAPFILL
│   │       │   └── h
│   │       ├── MNL_iCre1355_hetero_GAPFILL
│   │       └── MNL_iCre1355_mixo_GAPFILL
│   ├── escher
│   │   ├── mep
│   │   ├── mva
│   │   ├── pyruv+sterol
│   │   │   └── img
│   │   ├── sqs_sqe
│   │   └── sterol
│   ├── fill
│   │   ├── tables
│   │   │   └── stable
│   │   └── xmls
│   ├── gecko
│   │   └── prev
│   │       └── xmls
│   └── raw
│       └── iCre1355
├── notebooks
│   ├── dxs.ipynb
│   ├── epsilon.ipynb
│   ├── fba.ipynb
│   ├── gecko.ipynb
│   ├── kinetic.ipynb
│   ├── mva.ipynb
│   ├── sensitivity.ipynb
│   └── temp
├── requirements.txt
├── results
│   ├── bench
│   ├── fluxes
│   │   ├── (MODEL_NAME)
│   │   │   ├── (MODEL_CONSTRUCT)
│   ├── fva
│   ├── gecko
│   │   ├── iter1
│   │   ├── iter2
│   │   ├── iter3
│   │   └── iter4
│   ├── other
│   ├── pfba
│   ├── plots
│   ├── ranges
│   └── variant_compare_eps
└── scripts
    ├── helpers
    │   ├── model.py
    │   └── tools.py
    ├── mod
    │   ├── alter.py
    │   └── fill.py
    ├── opt
    │   ├── _fba.py
    │   └── _fva.py
    ├── other
    │   ├── benchmark.py
    │   ├── json.py
    │   └── manim.py
    └── val
        ├── __init__.py
        └── completeness.py (DEPRECATED)

91 directories, 28 files

```

- `build`: contains build scripts to run the essential commands that gap-fill the original model, alter, get visuals, and other internal tools.
- `data`: contains the data being used to get escher visuals, build the COBRApy model from the GSMMs (.xml files), gap-fill and alter model with associated reactions and genes. Some important ones:
  - `escher`: information for escher maps and visualization
  - `raw`: original models stored here (iRC1080, iBD1106, and iCre1355)
  - `fill`: the pathway information and gap-filled version of the original model(s)
  - `altered`: the pathway information and altered versions of the original model(s)
  - `gecko`: enzyme parameters added. GECKO didn't work due to ID incompatability, so this was done manually.
- `notebooks`: the experiments that were used in the project. some important ones:
  - `sensitivity.ipynb`: sensitivity analysis.
  - `gecko.ipynb`: final flux analysis.
  - `mva.ipynb`: troubleshooting the mva pathway.
  - `dxs.ipynb`: troubleshooting the initial SS inactivity.
- `results`: results of certain scripts and experiments recorded here
- `scripts`: including scripts from formating, benchmarks, visuals, model alterations, and other tools used in the notebooks
