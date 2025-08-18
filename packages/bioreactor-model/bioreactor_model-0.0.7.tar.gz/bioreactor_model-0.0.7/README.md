# Bioreactor-model
Bioreactor-model is a Python package for bioreactor and biomass growth calculations

## Installation

```bash
pip install bioreactor-model
```
## Documentation

[Documentation here](https://matrixdex.github.io/bioreactor-model)

## Classes
`calc.CellComposition()` calculates biomass formula and biomass molecular weight

`calc.BiomassEquation()` solves biomass growth equation

`bioreactor.time_to_titer()` calculates bioreactor production time for titer to reach specified value

## Getting Started
1. Calculate biomass composition and molecular weight from dry weight values
```bash
from bioreactor_model import calc
expt = calc.CellComposition(values={'C':47,'H':4.15,'N':10,'O':31,'ash_fraction':7.85}, dry_weights=True)
print(expt.biomass_composition)		# biomass composition
print(expt.biomass_molar_weight)	# molecular weight = 25.545
```

2. Solve biomass equation with above biomass composition and gas inlet-outlet values
```bash
from bioreactor_model import calc
expt = calc.CellComposition(values={'C':47,'H':4.15,'N':10,'O':31,'ash_fraction':7.85}, dry_weights=True)
be = calc.BiomassEquation(expt.biomass_composition)
be.set_gas_io_values(79,21,10,83,7)
be.solve_biomass_equation()
print(be.biomass_equation_solution['string'])			# biomass equation string 
print(be.biomass_equation_solution['molar_coeff'])		# molar coefficients of biomass equation
print(be.biomass_equation_solution['biomass_composition'])	# biomass composition
print(be.biomass_equation_solution['rq'])			# respiratory quotient = 0.664
```

## Tutorials

See [tutorials](https://matrixdex.github.io/bioreactor-model/tutorials.html) in documentation.

See [tests/test.py](https://github.com/matrixdex/bioreactor-model/blob/main/tests/test.py) for usage.


## Future development

Scale up parameters, fed-batch yield estimation, yield coefficient calculation, gas transfer estimation, oxygen transport and uptake rates will be added soon.




















