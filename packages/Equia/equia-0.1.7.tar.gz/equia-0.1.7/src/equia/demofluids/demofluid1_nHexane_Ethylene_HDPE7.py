from equia.models import (
  ApiFluid, ApiFluidStandardComponent, 
  ApiFluidPolymerComponent, ApiFluidComponentBlock, ApiFluidPseudoComponent, 
  ApiFluidKij
)

def demofluid1_nHexane_Ethylene_HDPE7() -> ApiFluid:
    """ Predefined fluid with 2 solvents and a HDPE polymer with 7 pseudo components."""   
    fluid = ApiFluid()
    fluid.name = "n-Hexane + Ethylene + HDPE(7)"
    fluid.eos = "PC-SAFT"
    fluid.solvent_cp = "DIPPR"
    fluid.polymer_cp = "Polynomial"

    fluid.standards = [
      ApiFluidStandardComponent(name="n-Hexane", is_alkane=True, molar_mass=86.17536,         
        acentric_factor = 0.301261,
        critical_pressure = 30.25,
        critical_temperature = 507.6,
        pc_saftdm = 0.03548,
        pc_saft_sigma_0 = 3.7983,
        pc_saft_epsilon = 236.77,
        ideal_gas_enthalpy_of_formation = -1937.212679,
        cp_ig_dippr_c0 = 1.21148319,
        cp_ig_dippr_c1 = 4.088175553,
        cp_ig_dippr_c2 = 1694.6,
        cp_ig_dippr_c3 = 2.749045667,
        cp_ig_dippr_c4 = 761.6,
        cp_ig_dippr_c5 = 200,
        cp_ig_dippr_c6 = 1500
      ),
      
      ApiFluidStandardComponent(name="Ethylene", is_alkane=True, molar_mass=28.05316,         
        acentric_factor = 0.087,
        critical_pressure = 50.41,
        critical_temperature = 282.34,
        pc_saftdm = 0.0567914,
        pc_saft_sigma_0 = 3.445,
        pc_saft_epsilon = 176.47,
        ideal_gas_enthalpy_of_formation = 1871.80339,
        cp_ig_dippr_c0 = 1.189883778,
        cp_ig_dippr_c1 = 3.37894198,
        cp_ig_dippr_c2 = 1596,
        cp_ig_dippr_c3 = 1.964128105,
        cp_ig_dippr_c4 = 740.8,
        cp_ig_dippr_c5 = 60,
        cp_ig_dippr_c6 = 1500
      )
    ]

    fluid.polymers = [
      ApiFluidPolymerComponent(short_name="HDPE",
        blocks=[
          ApiFluidComponentBlock(block_massfraction=1, monomer_name="Ethylene", monomer_molar_mass=28.054, 
            pc_saftdm = 0.0263, 
            pc_saft_sigma_0 = 4.0217, 
            pc_saft_epsilon = 252.0,
            sle_c=0.4, 
            sle_hu=8220.0, 
            sle_density_amorphous=0.853, 
            sle_density_crystalline=1.004,
            ideal_gas_enthalpy_of_formation = -1613.2549,
            cp_ig_poly_c0 = 0.81694,
            cp_ig_poly_c1 = -0.00030569,
            cp_ig_poly_c2 = 0.000015706,
            cp_ig_poly_c3 = -2.1058E-08,
            cp_ig_poly_c4 = 8.5078E-12,
            cp_ig_poly_c5 = 0,
            cp_ig_poly_c6 = 200,
            cp_ig_poly_c7 = 1000
          )
        ],
        pseudo_components=[
          ApiFluidPseudoComponent(name= "HDPE(17.3)", melting_temperature = 415.82, molar_mass = 17300,  massfraction = 0.00498),
          ApiFluidPseudoComponent(name= "HDPE(25.6)", melting_temperature = 416.38, molar_mass = 25600,  massfraction = 0.03067),
          ApiFluidPseudoComponent(name= "HDPE(36)",   melting_temperature = 416.72, molar_mass = 36000,  massfraction = 0.23902),
          ApiFluidPseudoComponent(name= "HDPE(50)",   melting_temperature = 416.95, molar_mass = 50000,  massfraction = 0.45515),
          ApiFluidPseudoComponent(name= "HDPE(69.2)", melting_temperature = 417.12, molar_mass = 69200,  massfraction = 0.23902),
          ApiFluidPseudoComponent(name= "HDPE(97.6)", melting_temperature = 417.24, molar_mass = 97600,  massfraction = 0.03067),
          ApiFluidPseudoComponent(name= "HDPE(144)",  melting_temperature = 417.34, molar_mass = 144000, massfraction = 0.0005)
        ]                            
      )
    ]
    
    fluid.kij = [
      ApiFluidKij(index_i=0, index_j=1, kija=0.0001),
      ApiFluidKij(index_i=0, index_j=2, kija=0.0002),
      ApiFluidKij(index_i=1, index_j=2, kija=0.0003),
      ]

    return fluid
