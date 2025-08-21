# -*- coding: utf-8 -*-
"""Module defining common physical and mathematical constants."""
from __future__ import absolute_import
import numpy as np
import scipy.constants as sc

pi = sc.pi
"""float: Equal to :py:data:`numpy.pi`."""

day = 60*60*24
"""float: Duration of a day [s]."""

yr = day*365.2425
"""float: Duration of a year [s]."""

AU = sc.astronomical_unit
"""float: Astronomical unit [m]."""

c = sc.speed_of_light
"""float: Speed of light [m/s]."""

c_km_pr_s = c*1e-3
"""float: Speed of light [km/s]."""

c_AU_pr_s = c/AU
"""float: Speed of light [AU/s]."""

c_AU_pr_yr = c*yr/AU
"""float: Speed of light [AU/yr]."""

m_sun = 1.9884754153381438e30 # Same as defined in astropy.constants
"""float: Solar mass [kg]."""

L_sun = 3.828e26 # Same as defined in astropy.constants
"""float: Solar luminosity [W]."""

R_sun = 695700000.0 # Same as defined in astropy.constants
"""float: Solar radius [m]."""

G = sc.gravitational_constant
"""float: Gravitational constant [m^3/kg/s^2]."""

G_sol = 4*pi**2
"""float: Gravitational constant in solar system units [AU^3/yr^2/m_sun]."""

k_B = sc.Boltzmann
"""float: Boltzmann constant [m^2*kg/s^2/K]."""

sigma = sc.Stefan_Boltzmann
"""float: Stefan-Boltzmann constant [W/m^2/K^4]."""

N_A = sc.Avogadro
"""float: Avogadro constant."""

m_p = sc.proton_mass
"""float: Proton mass [kg]."""

m_H2 = 2.01588e-3/N_A
"""float: Mass of a H2 molecule [kg]."""
