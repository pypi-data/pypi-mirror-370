# -*- coding: utf-8 -*-
"""Module containing the StarPopulation class."""
from __future__ import division, print_function, absolute_import

import numpy as np

import ast2000tools.constants as const
import ast2000tools.utils as utils


class StarPopulation:
    """Represents a population of stars of different types.

    An instance of this class contains all information required to plot a detailed Hertzsprung–Russell diagram.

    Parameters
    ----------
    number_of_stars : int, optional
        The total number of stars in the star population.
        Default is 50000.
    giant_star_fraction : float, optional
        The proportion of giants in the star population.
        Default is 1/100.
    supergiant_star_fraction : float, optional
        The proportion of supergiants in the star population.
        Default is 1/1000.
    white_dwarf_star_fraction : float, optional
        The proportion of white dwarfs in the star population.
        Default is 1/100.
    temperature_variance_offset : float, optional
        The component of the variance in temperature that is the same for all stars.
        Larger values increases horizontal spread uniformly in the HR diagram.
        Default is 0.
    temperature_variance_scale : float, optional
        The component of the variance in temperature that is proportional to the mean.
        Larger values increases horizontal spread more for larger temperatures in the HR diagram.
        Default is 0.08.
    luminosity_variance_offset : float, optional
        The component of the variance in luminosity that is the same for all stars.
        Larger values increases vertical spread uniformly in the HR diagram.
        Default is 0.
    luminosity_variance_scale : float, optional
        The component of the variance in luminosity that is proportional to the mean.
        Larger values increases vertical spread more for larger luminosities in the HR diagram.
        Default is 0.4.
    seed : int
        The seed to use when generating the mass distribution of stars in the population.
        By default a different seed is used each time.

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from ast2000tools.star_population import StarPopulation
    ...
    >>> stars = StarPopulation()
    >>> T = stars.temperatures # [K]
    >>> L = stars.luminosities # [L_sun]
    >>> r = stars.radii        # [R_sun]
    ...
    >>> c = stars.colors
    >>> s = np.maximum(1e3*(r - r.min())/(r.max() - r.min()), 1.0) # Make point areas proportional to star radii
    ...
    >>> fig, ax = plt.subplots()
    >>> ax.scatter(T, L, c=c, s=s, alpha=0.8, edgecolor='k', linewidth=0.05)
    ...
    >>> ax.set_xlabel('Temperature [K]')
    >>> ax.invert_xaxis()
    >>> ax.set_xscale('log')
    >>> ax.set_xticks([35000, 18000, 10000, 6000, 4000, 3000])
    >>> ax.set_xticklabels(list(map(str, ax.get_xticks())))
    >>> ax.set_xlim(40000, 2000)
    >>> ax.minorticks_off()
    ...
    >>> ax.set_ylabel(r'Luminosity [$L_\odot$]')
    >>> ax.set_yscale('log')
    >>> ax.set_ylim(1e-4, 1e6)
    ...
    >>> plt.savefig('HR_diagram.png')
    """
    def __init__(self, number_of_stars=50000,
                       giant_star_fraction=1e-2, supergiant_star_fraction=1e-3, white_dwarf_star_fraction=1e-2,
                       temperature_variance_offset=0, temperature_variance_scale=0.08,
                       luminosity_variance_offset=0, luminosity_variance_scale=0.4,
                       seed=None):
        self._set_star_numbers(number_of_stars, giant_star_fraction, supergiant_star_fraction, white_dwarf_star_fraction)
        self._set_variances(temperature_variance_offset, temperature_variance_scale,
                            luminosity_variance_offset, luminosity_variance_scale)
        self._set_seed(seed)

        self._initialize_mass_ranges()
        self._initialize_coefficients()

        self._generate_star_properties()

    @property
    def number_of_stars (self):
        """int: The total number of stars in the star population."""
        return self._number_of_stars

    @property
    def main_sequence_star_fraction(self):
        """float: The proportion of main sequence stars in the star population."""
        return self._main_sequence_star_fraction

    @property
    def giant_star_fraction(self):
        """float: The proportion of giants in the star population."""
        return self._giant_star_fraction

    @property
    def supergiant_star_fraction(self):
        """float: The proportion of supergiants in the star population."""
        return self._supergiant_star_fraction

    @property
    def white_dwarf_star_fraction(self):
        """float: The proportion of white dwarfs in the star population."""
        return self._white_dwarf_star_fraction

    @property
    def number_of_main_sequence_stars (self):
        """int: The number of main sequence stars in the star population."""
        return self._number_of_main_sequence_stars

    @property
    def number_of_giant_stars (self):
        """int: The number of giants in the star population."""
        return self._number_of_giant_stars

    @property
    def number_of_supergiant_stars (self):
        """int: The number of supergiants in the star population."""
        return self._number_of_supergiant_stars

    @property
    def number_of_white_dwarf_stars (self):
        """int: The number of white dwarfs in the star population."""
        return self._number_of_white_dwarf_stars

    @property
    def temperature_variance_offset (self):
        """float: The component of the variance in temperature that is the same for all stars."""
        return self._temperature_variance_offset

    @property
    def temperature_variance_scale (self):
        """float: The component of the variance in temperature that is proportional to the mean."""
        return self._temperature_variance_scale

    @property
    def luminosity_variance_offset (self):
        """float: The component of the variance in luminosity that is the same for all stars."""
        return self._luminosity_variance_offset

    @property
    def luminosity_variance_scale (self):
        """float: The component of the variance in luminosity that is proportional to the mean."""
        return self._luminosity_variance_scale

    @property
    def masses(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_stars`,) containing the masses of all the stars in solar masses."""
        return self._masses

    @property
    def main_sequence_star_masses(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_main_sequence_stars`,) containing the masses of the main sequence stars in solar masses."""
        return self._masses[self._total_number_of_non_main_sequence:]

    @property
    def giant_star_masses(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_giant_stars`,) containing the masses of the giant stars in solar masses."""
        return self._masses[:self.number_of_giant_stars]

    @property
    def supergiant_star_masses(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_supergiant_stars`,) containing the masses of the supergiant stars in solar masses."""
        return self._masses[self.number_of_giant_stars:self._total_number_of_giants]

    @property
    def white_dwarf_star_masses(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_white_dwarf_stars`,) containing the masses of the white dwarf stars in solar masses."""
        return self._masses[self._total_number_of_giants:self._total_number_of_non_main_sequence]

    @property
    def radii(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_stars`,) containing the radii of all the stars in solar radii."""
        return self._radii

    @property
    def main_sequence_star_radii(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_main_sequence_stars`,) containing the radii of the main sequence stars in solar radii."""
        return self.radii[self._total_number_of_non_main_sequence:]

    @property
    def giant_star_radii(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_giant_stars`,) containing the radii of the giant stars in solar radii."""
        return self.radii[:self.number_of_giant_stars]

    @property
    def supergiant_star_radii(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_supergiant_stars`,) containing the radii of the supergiant stars in solar radii."""
        return self.radii[self.number_of_giant_stars:self._total_number_of_giants]

    @property
    def white_dwarf_star_radii(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_white_dwarf_stars`,) containing the radii of the white dwarf stars in solar radii."""
        return self.radii[self._total_number_of_giants:self._total_number_of_non_main_sequence]

    @property
    def temperatures(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_stars`,) containing the temperatures of all the stars in kelvin."""
        return self._temperatures

    @property
    def main_sequence_star_temperatures(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_main_sequence_stars`,) containing the temperatures of the main sequence stars in kelvin."""
        return self.temperatures[self._total_number_of_non_main_sequence:]

    @property
    def giant_star_temperatures(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_giant_stars`,) containing the temperatures of the giant stars in kelvin."""
        return self.temperatures[:self.number_of_giant_stars]

    @property
    def supergiant_star_temperatures(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_supergiant_stars`,) containing the temperatures of the supergiant stars in kelvin."""
        return self.temperatures[self.number_of_giant_stars:self._total_number_of_giants]

    @property
    def white_dwarf_star_temperatures(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_white_dwarf_stars`,) containing the temperatures of the white dwarf stars in kelvin."""
        return self.temperatures[self._total_number_of_giants:self._total_number_of_non_main_sequence]

    @property
    def luminosities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_stars`,) containing the luminosities of all the stars in solar luminosities."""
        return self._luminosities

    @property
    def main_sequence_star_luminosities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_main_sequence_stars`,) containing the luminosities of the main sequence stars in solar luminosities."""
        return self.luminosities[self._total_number_of_non_main_sequence:]

    @property
    def giant_star_luminosities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_giant_stars`,) containing the luminosities of the giant stars in solar luminosities."""
        return self.luminosities[:self.number_of_giant_stars]

    @property
    def supergiant_star_luminosities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_supergiant_stars`,) containing the luminosities of the supergiant stars in solar luminosities."""
        return self.luminosities[self.number_of_giant_stars:self._total_number_of_giants]

    @property
    def white_dwarf_star_luminosities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_white_dwarf_stars`,) containing the luminosities of the white dwarf stars in solar luminosities."""
        return self.luminosities[self._total_number_of_giants:self._total_number_of_non_main_sequence]

    @property
    def colors(self):
        """2-D :class:`numpy.ndarray`: Array of shape (`number_of_stars`, 3) containing the colors of all the stars as RGB floats."""
        return self._colors

    @property
    def main_sequence_star_colors(self):
        """2-D :class:`numpy.ndarray`: Array of shape (`number_of_main_sequence_stars`, 3) containing the colors of the main sequence stars as RGB floats."""
        return self.colors[self._total_number_of_non_main_sequence:, :]

    @property
    def giant_star_colors(self):
        """2-D :class:`numpy.ndarray`: Array of shape (`number_of_giant_stars`, 3) containing the colors of the giant stars as RGB floats."""
        return self.colors[:self.number_of_giant_stars, :]

    @property
    def supergiant_star_colors(self):
        """2-D :class:`numpy.ndarray`: Array of shape (`number_of_supergiant_stars`, 3) containing the colors of the supergiant stars as RGB floats."""
        return self.colors[self.number_of_giant_stars:self._total_number_of_giants, :]

    @property
    def white_dwarf_star_colors(self):
        """2-D :class:`numpy.ndarray`: Array of shape (`number_of_white_dwarf_stars`, 3) containing the colors of the white dwarf stars as RGB floats."""
        return self.colors[self._total_number_of_giants:self._total_number_of_non_main_sequence, :]

    def _set_star_numbers(self, number_of_stars, giant_star_fraction, supergiant_star_fraction, white_dwarf_star_fraction):
        self._giant_star_fraction = float(giant_star_fraction)
        self._supergiant_star_fraction = float(supergiant_star_fraction)
        self._white_dwarf_star_fraction = float(white_dwarf_star_fraction)
        self._main_sequence_star_fraction = 1 - (self.giant_star_fraction + self.supergiant_star_fraction + self.white_dwarf_star_fraction)
        assert self.main_sequence_star_fraction >= 0

        self._number_of_stars = max(1, int(number_of_stars))
        self._number_of_giant_stars = int(self.giant_star_fraction*number_of_stars)
        self._number_of_supergiant_stars = int(self.supergiant_star_fraction*number_of_stars)
        self._number_of_white_dwarf_stars = int(self.white_dwarf_star_fraction*number_of_stars)
        self._total_number_of_giants = self.number_of_giant_stars + self.number_of_supergiant_stars
        self._total_number_of_non_main_sequence = self.number_of_giant_stars + self.number_of_supergiant_stars + self.number_of_white_dwarf_stars
        self._number_of_main_sequence_stars = self.number_of_stars - self._total_number_of_non_main_sequence
        assert self.number_of_main_sequence_stars >= 0

    def _set_variances(self, temperature_variance_offset, temperature_variance_scale,
                             luminosity_variance_offset, luminosity_variance_scale):
        self._temperature_variance_offset = max(0.0, float(temperature_variance_offset))
        self._temperature_variance_scale = max(0.0, float(temperature_variance_scale))
        self._luminosity_variance_offset = max(0.0, float(luminosity_variance_offset))
        self._luminosity_variance_scale = max(0.0, float(luminosity_variance_scale))

    def _set_seed(self, seed):
        self._seed = None if seed is None else int(seed)
        self._random_generator = np.random.RandomState(seed=self._seed)

    def _initialize_mass_ranges(self):
        self._mass_ranges = {'main sequence':  (0.1, 50),
                             'giant':      (3,   8),
                             'supergiant': (16,  35),
                             'white dwarf': (5.28e-3, 0.24)} # [solar masses]

    def _initialize_coefficients(self):
        '''
        From Zaninetti (2008).
        '''
        self._temperature_coefs = {'main sequence':  (1/10**(-7.76),   1/2.06),
                                   'giant':      (1/10**(5.8958), -1/1.4563),
                                   'supergiant': (1/10**(3.73),  -1/0.64),
                                   'white dwarf': (6.32685e7,  0.622131)}

        self._luminosity_coefs = {'main sequence':  (10**0.062, 3.43),
                                  'giant':      (10**0.32,  2.79),
                                  'supergiant': (10**1.29,  2.43),
                                  'white dwarf': (1.89596,  2.28976)}

    def _generate_star_properties(self):
        self._masses = np.empty(self.number_of_stars)
        self._luminosities = np.empty(self.number_of_stars)
        self._temperatures = np.empty(self.number_of_stars)

        self._masses[:self.number_of_giant_stars] = self._generate_masses_for_star_type(self.number_of_giant_stars, 'giant')
        self._masses[self.number_of_giant_stars:self._total_number_of_giants] = self._generate_masses_for_star_type(self.number_of_supergiant_stars, 'supergiant')
        self._masses[self._total_number_of_giants:self._total_number_of_non_main_sequence] = self._generate_masses_for_star_type(self.number_of_white_dwarf_stars, 'white dwarf')
        self._masses[self._total_number_of_non_main_sequence:] = self._generate_masses_for_star_type(self.number_of_main_sequence_stars, 'main sequence')
        self._masses.setflags(write=False)

        self._temperatures[:self.number_of_giant_stars] = self._generate_temperatures_for_star_type(self.giant_star_masses, 'giant')
        self._temperatures[self.number_of_giant_stars:self._total_number_of_giants] = self._generate_temperatures_for_star_type(self.supergiant_star_masses, 'supergiant')
        self._temperatures[self._total_number_of_giants:self._total_number_of_non_main_sequence] = self._generate_temperatures_for_star_type(self.white_dwarf_star_masses, 'white dwarf')
        self._temperatures[self._total_number_of_non_main_sequence:] = self._generate_temperatures_for_star_type(self.main_sequence_star_masses, 'main sequence')
        self._temperatures.setflags(write=False)

        self._luminosities[:self.number_of_giant_stars] = self._generate_luminosities_for_star_type(self.giant_star_masses, 'giant')
        self._luminosities[self.number_of_giant_stars:self._total_number_of_giants] = self._generate_luminosities_for_star_type(self.supergiant_star_masses, 'supergiant')
        self._luminosities[self._total_number_of_giants:self._total_number_of_non_main_sequence] = self._generate_luminosities_for_star_type(self.white_dwarf_star_masses, 'white dwarf')
        self._luminosities[self._total_number_of_non_main_sequence:] = self._generate_luminosities_for_star_type(self.main_sequence_star_masses, 'main sequence')
        self._luminosities.setflags(write=False)

        self._radii = self._compute_radii(self._temperatures, self._luminosities)
        self._radii.setflags(write=False)

        self._colors = self._compute_colors(self._temperatures)
        self._colors.setflags(write=False)

    def _generate_masses_for_star_type(self, number_of_stars, star_type):
        '''
        Generates masses using the initial mass function (IMF) of Maschberger (2012).
        The IMF describes the probability distribution of masses for a population of
        stars as they enter the main sequence. The returned masses are in units of the
        solar mass.
        '''
        # Parameters for the Maschberger IMF
        mu = 0.2 # [solar masses]
        alpha = 2.3 # [solar masses]
        beta = 1.4 # [solar masses]

        # Helper function
        def G(m):
            return (1 + (m/mu)**(1 - alpha))**(1 - beta)

        mass_range = self._mass_ranges[star_type]

        random_fractions = self._random_generator.random_sample(size=number_of_stars)
        return mu*((random_fractions*(G(mass_range[1]) - G(mass_range[0])) + G(mass_range[0]))**(1/(1 - beta)) - 1)**(1/(1 - alpha))

    def _generate_temperatures_for_star_type(self, masses, star_type, min_temperature=2000):
        temperatures = self._compute_mean_temperatures_for_star_type(masses, star_type)
        if self.temperature_variance_offset > 0 or self.temperature_variance_scale > 0:
            temperatures = np.maximum(min_temperature, self._random_generator.normal(loc=temperatures, scale=(self.temperature_variance_offset + temperatures*self.temperature_variance_scale)))
        return temperatures

    def _generate_luminosities_for_star_type(self, masses, star_type, min_luminosity=1e-5):
        luminosities = self._compute_mean_luminosities_for_star_type(masses, star_type)
        if self.luminosity_variance_offset > 0 or self.luminosity_variance_scale > 0:
            luminosities = np.maximum(min_luminosity, self._random_generator.normal(loc=luminosities, scale=(self.luminosity_variance_offset + luminosities*self.luminosity_variance_scale)))
        return luminosities

    def _compute_mean_temperatures_for_star_type(self, masses, star_type):
        return (self._temperature_coefs[star_type][0]*masses)**self._temperature_coefs[star_type][1]

    def _compute_mean_luminosities_for_star_type(self, masses, star_type):
        return self._luminosity_coefs[star_type][0]*(masses**self._luminosity_coefs[star_type][1])

    def _compute_radii(self, temperatures, luminosities):
        return np.sqrt(const.L_sun*luminosities/(4*np.pi*const.sigma*temperatures**4))/const.R_sun

    def _compute_colors(self, temperatures):
        return np.array([np.array(utils._convert_temperature_to_RGB(T))/255.0 for T in temperatures])
