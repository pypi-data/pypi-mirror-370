from equia.models import (
  ApiFluid, ApiFluidStandardComponent, 
  ApiFluidKij
)

def demofluid_Methane_nHexane_Toluene(is_volume_shift=True) -> ApiFluid:
    """ Predefined fluid with 3 solvents using PR78 with volume shift."""   
    fluid = ApiFluid()
    fluid.name = "Methane + n-Hexane + Toluene"
    fluid.eos = "PR78"
    fluid.solvent_cp = "DIPPR"
    fluid.polymer_cp = "Polynomial"

    fluid.standards = [
      ApiFluidStandardComponent(name="Methane", is_alkane=True, molar_mass=16.04246,         
        acentric_factor = 0.0115478,
        critical_pressure = 45.99,
        critical_temperature = 190.564,
        critical_volume = 98.6278,
        volume_shift=-0.21013 if is_volume_shift else 0,
        pc_saftdm = 0.06233458,
        pc_saft_sigma_0 = 3.7039,
        pc_saft_epsilon = 150.03,
        ideal_gas_enthalpy_of_formation = -4645.16129,
        cp_ig_dippr_c0 = 2.075611657,
        cp_ig_dippr_c1 = 4.982577528,
        cp_ig_dippr_c2 = 2086.9,
        cp_ig_dippr_c3 = 2.593236715,
        cp_ig_dippr_c4 = 991.96,
        cp_ig_dippr_c5 = 50,
        cp_ig_dippr_c6 = 1500
      ),
      ApiFluidStandardComponent(name="n-Hexane", is_alkane=True, molar_mass=86.17536,         
        acentric_factor = 0.301261,
        critical_pressure = 30.25,
        critical_temperature = 507.6,
        critical_volume = 369.566,
        volume_shift = 0.011898058 if is_volume_shift else 0,
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
      
      ApiFluidStandardComponent(name="Toluene", is_alkane=False, molar_mass=92.141,         
        acentric_factor = 0.2621,
        critical_pressure = 41.05992975,
        critical_temperature = 591.8,
        critical_volume = 316.0,
        volume_shift=0.065471176 if is_volume_shift else 0,
        pc_saftdm = 0.030549918,
        pc_saft_sigma_0 = 3.7169,
        pc_saft_epsilon = 285.69,
        ideal_gas_enthalpy_of_formation = -1753.282643,
        cp_ig_dippr_c0 = 1.175133721,
        cp_ig_dippr_c1 = 3.762255267,
        cp_ig_dippr_c2 = 1614.1,
        cp_ig_dippr_c3 = 2.658107495,
        cp_ig_dippr_c4 = 742,
        cp_ig_dippr_c5 = 200,
        cp_ig_dippr_c6 = 1500
      )
    ]
    
    fluid.kij = [
      ApiFluidKij(index_i=0, index_j=1, kija=0.0),
      ApiFluidKij(index_i=0, index_j=2, kija=0.0),
      ApiFluidKij(index_i=1, index_j=2, kija=0.0),
      ]

    return fluid
