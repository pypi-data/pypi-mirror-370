# === defines global constants ===

import astropy.constants as apc

# define Newtons's constant in CGS units
g_n = apc.G.cgs.value
# define Boltzmann's constant in CGS units
k_b = apc.k_B.cgs.value
# define Stefan-Boltzmann constant in CGS units
sigma_sb = apc.sigma_sb.cgs.value
# define speed of light in CGS units
speed_of_light = apc.c.cgs.value
# define solar mass in CGS units
m_sol = apc.M_sun.cgs.value
# define solar radius in CGS units
r_sol = apc.R_sun.cgs.value
# define solar luminosity in CGS units
l_sol = apc.L_sun.cgs.value
# define parsec in CGS units
pc = apc.pc.cgs.value
# define AU in CGS units
au = apc.au.cgs.value
# define proton mass in CGS units
m_p = apc.m_p.cgs.value
# define electron charge in CGS units
ec = apc.e.gauss.value
# define ideal gas constant
ideal_gas_const = apc.R.cgs.value
# define year in CGS units
year = 31557600.0
# Hubble constant
H0 = 70e5/(1e6*pc)
