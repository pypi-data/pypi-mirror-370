import numpy as np
class Constants:
    def __init__(self):
        self.atomic_weights = {
            "C": 12.011,
            "H": 1.00784,
            "N": 14.00674,
            "O":   15.9994
        }
        self.substrates = {
            "hexane": {
                "formula": u'C\u2086H\u2081\u2084',
                "C": 6,
                "H": 14,
                "N": 0,
                "O": 0
            },
            "glucose": {
                "formula": u'C\u2086H\u2081\u2082O\u2086',
                "C": 6,
                "H": 12,
                "N": 0,
                "O": 6
            }
        }
    def get_molar_weight(self, compound):
        return round(compound['C']*self.atomic_weights['C']+compound['H']*self.atomic_weights['H']+compound['N']*self.atomic_weights['N']+compound['O']*self.atomic_weights['O'],3)

class CellComposition:
    def __init__(self, values, dry_weights=False, molecular_formula=False):
        self.atomic_weights = Constants().atomic_weights
        if dry_weights==True:
            self.percentage_dry_weights = {
                "C": values['C'],
                "H": values['H'],
                "N": values['N'],
                "O": values['O']
            }
            n_moles_100g = {
                "C": self.percentage_dry_weights['C']/self.atomic_weights['C'],
                "H": self.percentage_dry_weights['H']/self.atomic_weights['H'],
                "N": self.percentage_dry_weights['N']/self.atomic_weights['N'],
                "O": self.percentage_dry_weights['O']/self.atomic_weights['O']
            }
            moles_100g_norm = {
                "C": 1,
                "H": round(n_moles_100g["H"]/n_moles_100g["C"],3),
                "N": round(n_moles_100g["N"]/n_moles_100g["C"],3),
                "O": round(n_moles_100g["O"]/n_moles_100g["C"],3),    
            }
        
        elif molecular_formula==True:
            moles_100g_norm = {
                "C": 1,
                "H": round(values['H'],3),
                "N": round(values['N'],3),
                "O": round(values['O'],3),    
            }
        else:
            return None
        
        moles_100g_norm['formula'] = f"C(H-{moles_100g_norm['H']:.3f})(N-{moles_100g_norm['N']:.3f})(O-{moles_100g_norm['O']:.3f})"
        self.ash_fraction = values['ash_fraction']  
        self.biomass_composition = moles_100g_norm
        molar_weight = (self.atomic_weights["C"]*self.biomass_composition["C"] + self.atomic_weights["N"]*self.biomass_composition["N"] + self.atomic_weights["O"]*self.biomass_composition["O"] + self.atomic_weights["H"]*self.biomass_composition["H"])
        p = 1 - (self.ash_fraction/100)
        self.biomass_molar_weight = round(molar_weight/p,3)

class BiomassEquation:
    def __init__(self,biomass_composition, substrate='glucose'):
        self.biomass_composition = biomass_composition
        if substrate == 'glucose':
            self.substrate = Constants().substrates['glucose']
        elif substrate == 'hexane':
            self.substrate = Constants().substrates['hexane']
        self.biomass_equation_string = f"{self.substrate['formula']} + aNH3 +bO2 -> cCpHqNrOs + dCO2 + eH2O"
        self.biomass_equation_coeff = {
            'a':None, 'b':None, 'c':None, 'd':None, 'e':None, 'p':1, 'q':self.biomass_composition['H'],'r':self.biomass_composition['N'], 's':self.biomass_composition['O']   
        }
        self.rq=None
        self.biomass_equation_solution = None
        self.inlet_O2=None
        self.inlet_N2=None
        self.outlet_CO2=None
        self.outlet_N2=None
        self.outlet_O2=None

    def set_gas_io_values(self, inlet_N2=None, inlet_O2=None, outlet_CO2=None, outlet_N2 = None, outlet_O2=None):
        self.inlet_O2 = inlet_O2
        self.inlet_N2 = inlet_N2
        if self.inlet_N2 == None and self.inlet_O2 != None:
            self.inlet_N2 = 100 - self.inlet_O2
        elif self.inlet_O2 == None and self.inlet_N2 != None:
            self.inlet_O2 = 100 - self.inlet_N2
        self.outlet_O2 = outlet_O2
        self.outlet_N2 = outlet_N2
        self.outlet_CO2 = outlet_CO2
        
        if self.outlet_CO2 == None and self.outlet_N2!=None and self.outlet_O2!=None:
            self.outlet_CO2 = 100 - (self.outlet_N2+self.outlet_O2)
        elif self.outlet_CO2 != None and self.outlet_N2==None and self.outlet_O2!=None:
            self.outlet_N2 = 100 - (self.outlet_CO2+self.outlet_O2)
        elif self.outlet_CO2 != None and self.outlet_N2!=None and self.outlet_O2==None:
            self.outlet_O2 = 100 - (self.outlet_CO2+self.outlet_N2)

    def rq_from_gas_io(self):
        if self.inlet_O2!=None and self.inlet_N2!=None and self.outlet_CO2!=None and self.outlet_N2!=None and self.outlet_O2!=None:
            inlet_air_moles = (self.outlet_N2/self.inlet_N2)*100 # Assume nitrogen content is constant in gaseous inlet and outlet. N2 moles remain same though fraction of gaseous outlet occupied by nitrogen is changed. Gasoues output is assumed as 100 moles. Here, number of moles of gaseous input is determined.
            moles_o2_used = ((self.inlet_O2/100)*inlet_air_moles) - self.outlet_O2
            self.rq = self.outlet_CO2/moles_o2_used
            return round(self.rq,3)
        else:
            return None
    def set_rq (self,rq):
        self.rq=rq

    def solve_biomass_equation(self, rq=None, biomass_yield_mol=None, biomass_yield_gram=None,biomass_molar_weight=None):
        use_rq = False
        use_yield = False
        if rq == None:
            rq2 = self.rq_from_gas_io()
            if rq2==None:
                if self.rq == None:
                    use_rq = False
                    if biomass_yield_mol !=None or biomass_yield_gram!=None:
                        use_yield=True
                    else:
                        return 'unable to determine respiratory quotient or yield coefficient. use function like set_rq()'
            else:
                use_rq=True
                self.rq=rq2   
        else:
            self.rq=rq
            use_rq=True
        if use_rq == True:
            eq5 = [0,self.rq,0,-1,0]
            c5=0
        elif use_yield == True:
            if biomass_yield_mol!=None:
                ceq=biomass_yield_mol
            else:
                ceq=(Constants().get_molar_weight(self.substrate)*biomass_yield_gram)/biomass_molar_weight
            eq5 = [0,0,1,0,0] # using biomass yield coefficient to estimate c
            c5=ceq
        else:
            print('unable to determine respiratory quotient and yield. no exact solution possible.')
            return None
        
        a = np.array([
            [0,0,1*self.biomass_composition['C'],1,0],
            [-3,0,1*self.biomass_composition['H'],0,2],
            [-1,0,1*self.biomass_composition['N'],0,0],
            [0,-2,self.biomass_composition['O'],2,1],
            eq5
        ])
        b=np.array([self.substrate['C'],self.substrate['H'],0+self.substrate['N'],self.substrate['O'],c5])
        x=(np.linalg.solve(a,b))
        
        self.biomass_equation_coeff['a'] = round(x[0],3)
        self.biomass_equation_coeff['b'] = round(x[1],3)
        self.biomass_equation_coeff['c'] = round(x[2],3)
        self.biomass_equation_coeff['d'] = round(x[3],3)
        self.biomass_equation_coeff['e'] = round(x[4],3)
        
        self.biomass_equation_string = f"{self.substrate['formula']} + {self.biomass_equation_coeff['a']}NH3 + {self.biomass_equation_coeff['b']}O2 -> {self.biomass_equation_coeff['c']}{self.biomass_composition['formula']} + {self.biomass_equation_coeff['d']}CO2 + {self.biomass_equation_coeff['e']}H2O"
        self.biomass_equation_solution = {
            "string": self.biomass_equation_string,
            "molar_coeff": {
                "NH3": float(self.biomass_equation_coeff['a']),
                "O2": float(self.biomass_equation_coeff['b']),
                "biomass": float(self.biomass_equation_coeff['c']),
                "CO2": float(self.biomass_equation_coeff['d']),
                "H2O": float(self.biomass_equation_coeff['e'])
            },
            "biomass_composition": self.biomass_composition,
            "rq": round(float(self.biomass_equation_coeff['d']/self.biomass_equation_coeff['b']),3)
        }
        return self.biomass_equation_solution['string']