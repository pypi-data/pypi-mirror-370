from bioreactor_model import calc, bioreactor

expt = calc.CellComposition(values={'C':47,'H':4.15,'N':10,'O':31,'ash_fraction':7.85}, dry_weights=True)
assert expt!=None
biomass = expt.biomass_composition

assert biomass['C'] == 1
assert biomass['H'] == 1.052
assert biomass['N'] == 0.182
assert biomass['O'] == 0.495

assert expt.biomass_molar_weight == 25.545

be = calc.BiomassEquation(biomass)
be.set_gas_io_values(79,21,10,83,7)

assert be.rq_from_gas_io() == 0.664

be.solve_biomass_equation()
sol = be.biomass_equation_solution
assert sol['molar_coeff']['NH3'] == 0.881
assert sol['molar_coeff']['O2'] == 1.744
assert sol['molar_coeff']['biomass'] == 4.842
assert sol['molar_coeff']['CO2'] == 1.158
assert sol['molar_coeff']['H2O'] == 4.775

yeast = calc.CellComposition(values={'C':1,'H':1.66,'N':0.194,'O':0.269,'ash_fraction':8}, molecular_formula=True)
ysol_hex=calc.BiomassEquation(yeast.biomass_composition,substrate='hexane')
ysol_glu=calc.BiomassEquation(yeast.biomass_composition,substrate='glucose')
ysol_hex.solve_biomass_equation(biomass_yield_gram=1.4, biomass_molar_weight=yeast.biomass_molar_weight) # yield unit g cells / g substrate; conversion to moles necessary; biomass_molar_weight input used for (gram cells per biomass molar weight) * moles of cell / gram substrate per substrate molar weight substate ) * 1 mol substrate is yield per mole of substrate, or c in biomass molecular equation (BiomassEquation.biomass_equation_coeff['c'])
ysol_glu.solve_biomass_equation(biomass_yield_mol=0.4)  # yield unit is molar; no conversion necessary; biomass_yield_mol = c in biomass molecular equation (BiomassEquation.biomass_equation_coeff['c']) 
yeast_hexane_sol = ysol_hex.biomass_equation_solution
yeast_glucose_sol = ysol_glu.biomass_equation_solution

assert yeast_glucose_sol['rq'] == 1.01  # respiratory quotient ~ 1 in glucose substrate 
assert yeast_hexane_sol['rq'] == 0.187  # respiratory quotient < 1 in hexane substrate, glucose needs less O2 for respiration because it contains O

assert bioreactor.time_to_titer(titer=5,qp=0.000000000004,cell_seed_volume=500000,doubling_time=15,seed_unit='cell/ml')['value'] == 103