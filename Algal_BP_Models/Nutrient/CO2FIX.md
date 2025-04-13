# Carbon Fixation

### PBR Volume

Sources: [Lessons in Bioreactor Scale-Up: Part 1 — Exploring Introductory Principles](https://www.bioprocessintl.com/bioreactors/lessons-in-bioreactor-scale-up-part-1-mdash-exploring-introductory-principles) | [Lab-scale photobioreactor systems: principles, applications, and scalability](https://link.springer.com/article/10.1007/s00449-022-02711-1#:~:text=The%20design%20can%20also%20be,the%20illumination%20of%20the%20culture.)

- Lab scale around 1 - 3L
- Development scale around 10-50L
- Production scale around 200 - 2000L

Source: [Different large-scale systems currently used for the industrial production of microalgal biomass](https://www.researchgate.net/figure/Different-large-scale-systems-currently-used-for-the-industrial-production-of-microalgal_fig1_323999015)

- 1 $m^3$ Flat panel photobioreactor (1,000 Liters)
- 100 $m^3$ Tubular PBR (100,000 Liters)

### Cholorophyll Concentration in Systems

#### Natural Systems

Source: [A Mathematical Model for the Effects of Nitrogen
and Phosphorus on Algal Blooms](https://sci-hub.se/https://www.worldscientific.com/doi/abs/10.1142/S0218127419501293)

- Model assumes mass action kinetics. 
- A model was developed to account for the change in population of the algae and detritious cells based on Nitrogen (N) and Phosphorus (P).
- Assume we have a steady rate of input N and P. In addition, detritious cells contribute back to N and P supply.
- A(t) is affected by supply and overpopulation can kill some of the culture by a rate. This will cause in decrease of A(t) and increase of D(t).
- Check out `C_ALGAE_NAT.md` to see the model steady-state results.

#### Synthetic Systems

Source: [Population balance modeling of a microalgal culture in photobioreactors: Comparison between experiments and simulations](https://aiche.onlinelibrary.wiley.com/doi/full/10.1002/aic.14893?casa_token=MISas9j_5lIAAAAA%3AG0DqJoueqMiEwkcU6ep2rF1jrma-UILKvqpoBa5yN6wlnzCSCgki_b-RyFUuWQbzO5ft9FapQc5b1IDa)

- Study demonstrates the steady-state concentration of the algal biomass in PBRs
- Wet biomass concentration (g/L) seems to be upper-bounded by 16 g/L. Taking steady state as 15 g/L is a safe approach, graph clearly shows the concentration exceeds that amount upon steady-state.

Source: [Extraction of chlorophylls and carotenoids from dry and wet biomass of isolated Chlorella Thermophila: Optimization of process parameters and modelling by artificial neural network](https://www.sciencedirect.com/science/article/abs/pii/S1359511320302981)

- Chlorophyll makes up about 7% of algae composition. Could be used to convert algal concentration into Chl concentration.

As a summary of the 2 articles in `Synthetic Systems` section, we can say that a humble approximation of the chlorophyll concentration would be $15 \space g/L \times 0.07 = 1.05 g \space Chlorophyll/L$

### Chlamydomonas reinhardtii Fixation Rates


Source: [Estimated photosynthetic Vmax and apparent K0.5(CO2)for cells in high, low, and very low CO2 states](https://bionumbers.hms.harvard.edu/bionumber.aspx?id=116809&ver=0&trm=chlamydomonas+reinhardtii+carbon+fixation&org=)

- High CO2: $97 \space \mu mol \space CO_2/mg \space Chlorophyll/h$
- Low CO2: $93 \space \mu mol \space CO_2/mg \space Chlorophyll/h$
- Very Low CO2: $49 \space \mu mol \space CO_2/mg \space Chlorophyll/h$

### Chlorella Vulgaris Fixation Rates

Source: [Carbon dioxide biofixation by Chlorella vulgaris at different CO2 concentrations and light intensities](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/full/10.1002/elsc.201200212?casa_token=_tSqMc2AObYAAAAA%3A0-B-pmRJmfUJcAcQXupRU-EuLujfed-7ec6VnDqWcDtKrvM688OvaaW0XSa7z8M3SESjS6dYTbyup9v3)

Source: [Chlorella vulgaris oxygen production rate](https://bionumbers.hms.harvard.edu/bionumber.aspx?id=107311&ver=0&trm=chlorella+carbon+sequestration+rate&org=)

- Each mol of chlorophyll is reported to procude 50-400 mol of O2 per h.
- Chlorella vulgaris has both type and and b chlorophylls. We assume that all of the chlorophyll population is the lighter one (Chl a with $893.509 \space g/mol$) and take its molar mass to compute: $400 \space mol \space O^2/mol \space Chl/h \approx 0.4476732 \space mol \space O^2/g \space Chl/h = 447.6732 \space {\mu}mol \space O^2/mg \space Chl/h \approx 447 \space {\mu}mol \space O^2/mg \space Chl/h$
- Due to the 1:1 molar ratio of O2 and CO2 in photosynthesis, we assume that all CO2 is being used up. That's why we're assuming to directly convert the O2 production rate into CO2 fixation rate. Thus, that gets us $\approx 447 \space {\mu}mol \space CO^2/mg \space Chl/h$

### Computation

$CO_2 \space fixed \space (g/h)=(\frac{R_{fixation}\times C_{Chl}\times V\times Mm_{CO_2}}{10^6})$ where,

- $R_{fixation}$ is the determined chlorophyl-based fixation rate ($\mu$ mol CO2/mg Chl/h)
- $C_{Chl}$ is the concentration of chlorophyl (mg Chl/L)
- $V$ as volume in L
- $Mm_{CO_2}$ as the molar mass of CO2 (44.009 g/mol)

### Carbon Tax and Benefits

Source: [Canada's Carbon Pricing (a.k.a "carbon tax") Explained](https://davidsuzuki.org/what-you-can-do/carbon-pricing-explained/#:~:text=Effective%20carbon%20levies%20rise%20regularly,will%20reach%20%24170%20per%20tonne.) | [Industrial Carbon Pricing Explained](https://climateinstitute.ca/large-emitter-trading-systems-explained/)

- Increasing by \$15 a year and it's estimated that it will reach \$170 per tonne.
- Sits at \$80 per tonne in April 2024.