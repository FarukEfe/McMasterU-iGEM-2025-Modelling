For setup:

- `python -m venv venv`
- `venv/Scripts/activate`
- `pip3 install -r requirements.txt`


EscherFBA: https://pmc.ncbi.nlm.nih.gov/articles/PMC6158907/
GNU Linear Programming Kit: https://en.wikipedia.org/wiki/GNU_Linear_Programming_Kit

SBML Diff: https://github.com/jamesscottbrown/sbml-diff?tab=readme-ov-file

QUESTIONS:
===

- SS no flux even though precursor does. Why?
- What goal to optimize for?
- If SS no flux caused by infeasibility, how to systematically remove them or detect them?
- Using iBD1106 as model, valid?
- If I wanted to add a new reaction/pathway to the model (say from KEGG or somewhere else), how would I go about making identifiers? Because many models use different id labels for the same metabolites/rxns so even different met or rxn ids may refer to the same thing.

### Modifications
Gapfill: `python -m scripts.other.gapfill ./path/to/model.xml`
Alter: `nothing so far`

### Analyses
FBA: `python -m scripts.opt._fba ./path/to/model.xml -d ./dest/path/results.xml`
FVA: `python -m scripts.opt_fva ./path/to/model.xml`

### Validation
Completeness: `python -m scripts.val.completeness ./path/to/model.xml` // Make this more usable w/ CLI input source and destination. Implement pathfinding if you can to show the path from src to dest.