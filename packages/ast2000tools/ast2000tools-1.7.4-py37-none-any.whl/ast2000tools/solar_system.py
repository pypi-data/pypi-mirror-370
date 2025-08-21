# -*- coding: utf-8 -*-
"""Module containing the SolarSystem class."""
from __future__ import division, print_function, absolute_import
from six.moves import range, zip

import sys
import os
import traceback
import numpy as np
from scipy import interpolate
from lxml import etree

import ast2000tools.constants as const
import ast2000tools.utils as utils


class SolarSystem(object):
    """Represents a random solar system.

    Given an integer seed, a randomized solar system containing a star and
    multiple planets is generated.

    Parameters
    ----------
    seed : int
        The seed to use when generating random solar system properties.
    data_path : str, optional
        Specifies the path to the directory where output XML files should be stored (e.g. the MCAst data folder).
        By default, a folder called "XMLs" is created in the working directory.
    has_moons : bool, optional
        Whether the generated planets should be visualized with moons.
        Setting to False increases performance. Default is True.
    verbose : bool, optional
        Whether to print non-essential status messages.
        Default is True.
    """
    def __init__(self, seed, data_path=None, has_moons=True, verbose=True):

        self._verbose = bool(verbose)

        # Define hidden attributes
        self._mean_molecular_masses = None

        self._init_seed(seed)
        self._init_path(data_path)

        self._init_star()
        self._init_planets()
        self._init_moons(has_moons)

    @property
    def seed(self):
        """int: The seed used to generate random solar system properties."""
        return self._seed

    @property
    def data_path(self):
        """str: The path to the directory where output XML files will be stored."""
        return self._data_path

    @property
    def has_moons(self):
        """bool: Whether the generated planets will be visualized with moons."""
        return self._has_moons

    @property
    def verbose(self):
        """bool: Whether non-essential status messages will be printed."""
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        self._verbose = bool(verbose)

    @property
    def star_temperature(self):
        """float: The surface temperature of the star in kelvin."""
        return self._star_temperature

    @property
    def star_mass(self):
        """float: The mass of the star in solar masses."""
        return self._star_mass

    @property
    def star_radius(self):
        """float: The radius of the star in kilometers."""
        return self._star_radius

    @property
    def star_color(self):
        """tuple(float): The RGB color of the star."""
        return self._star_color

    @property
    def number_of_planets(self):
        """int: The number of planets in the solar system."""
        return self._number_of_planets

    @property
    def semi_major_axes(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the semi-major axis of the orbit of each planet about the star in astronomical units."""
        return self._semi_major_axes

    @property
    def eccentricities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the eccentricity of each planet."""
        return self._eccentricities

    @property
    def masses(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the mass of each planet in solar masses."""
        return self._masses

    @property
    def radii(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the radius of each planet in kilometers."""
        return self._radii

    @property
    def initial_orbital_angles(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the angle between the x-axis and the initial position of each planet, in radians."""
        return self._initial_orbital_angles

    @property
    def aphelion_angles(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the angle between the x-axis and the aphelion direction of each planet, in radians."""
        return self._aphelion_angles

    @property
    def rotational_periods(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the rotational period of each planet in days."""
        return self._rotational_periods

    @property
    def initial_positions(self):
        """2-D :class:`numpy.ndarray`: Array of shape (2, `number_of_planets`) containing the initial x and y-position of each planet relative to the star, in astronomical units."""
        return self._initial_positions

    @property
    def initial_velocities(self):
        """2-D :class:`numpy.ndarray`: Array of shape (2, `number_of_planets`) containing the initial x and y-velocity of each planet relative to the star, in astronomical units per year."""
        return self._initial_velocities

    @property
    def atmospheric_densities(self):
        """1-D :class:`numpy.ndarray`: Array of shape (`number_of_planets`,) containing the atmospheric density at the surface of each planet, in kilograms per cubic meter."""
        return self._atmospheric_densities

    @property
    def types(self):
        """tuple(str): Tuple of length `number_of_planets` containing strings denoting the type of each planet."""
        return self._types

    def print_info(self):
        """Prints out info about the solar system.
        """
        print('Information about the solar system with seed %d:\n' % self.seed)
        print('Number of planets:', self.number_of_planets)
        print('Star surface temperature: %g K' % self.star_temperature)
        print('Star radius: %g km' % self.star_radius)
        print('Star mass: %g solar masses' % self.star_mass)

        print('\nIndividual planet information. Masses in units of m_sun, radii in km,\n'
              'atmospheric densities in kg/m^3, rotational periods in Earth days.\n'
              'Planet |      Mass      |     Radius     |   Atm. dens.   |  Rot. period   |')
        for pla in range(self.number_of_planets):
            print('%6d |%15.9g |%15.7f |%15.9f |%15.8f |' %(pla, self.masses[pla], self.radii[pla], self.atmospheric_densities[pla], self.rotational_periods[pla]))

        print('\nIndividual planet initial positions (in AU) and velocities (in AU/yr).\n'
              'Planet |       x        |       y        |       vx       |       vy       |')
        for pla in range(self.number_of_planets):
            print('%6d |%15.10f |%15.10f |%15.10f |%15.10f |' %(pla, self.initial_positions[0, pla], self.initial_positions[1, pla],
                                                                     self.initial_velocities[0, pla], self.initial_velocities[1, pla]))

    def verify_planet_positions(self, simulation_duration, planet_positions, filename=None, number_of_output_points=None):
        """Verifies that your simulation of the planet trajectories around the star gives a reasonable result.

        Note
        ----
            If you get an OSError when the output file is being saved after successful verification,
            reduce the number of output points by specifying the `number_of_output_points` argument.

        Parameters
        ----------
        simulation_duration : float
            The total duration of the simulation (starting from time zero), in years.
            Must be at least 20 orbital periods of your home planet.
        planet_positions : 3-D array_like
            Array of shape (2, `number_of_planets`, `number_of_times`) containing the x and y-position of each planet at each time, in astronomical units relative to the star.
            The positions are assumed to be specified at uniformly spaced times over the simulation duration.
            The number of times has to be at least 1000.
        filename : str, optional
            Specifies the filename/path to save the exact trajectories of the planets to after your trajectories have been verified.
            They are stored in the binary NumPy .npz format as a dictionary-like object with keys `'times'` and `'planet_positions'`,
            The `'times'` entry is a 1D array of times with length `number_of_output_points` if this argument was specified, otherwise
            `number_of_times`. The `'planet_positions'` entry is an array of positions with shape (2, `number_of_planets`, `len(times)`).
            By default, no file is generated.
        number_of_output_points : int, optional
            The number of exact trajectory points to include in the output .npz file (if applicable).
            By default, the number of output points will be the same as the number of input points.
            If your trajectories contain a very large number of points, consider modifying this
            argument to reduce the output size.

        Raises
        ------
        RuntimeError
            When the input positions are too far from the correct positions.
        """
        planet_positions = np.asarray(planet_positions, dtype=float)
        if planet_positions.ndim != 3 or planet_positions.shape[:2] != (2, self.number_of_planets):
            raise ValueError('Argument "planet_positions" has shape %s but must have shape (2, %d, <number of times>).' % (str(planet_positions.shape), self.number_of_planets))

        number_of_times = planet_positions.shape[2]
        if number_of_times < 1000:
            raise ValueError('The number of times is %d but must be at least 1000.' % number_of_times)

        home_planet_orbital_period = np.sqrt(self.semi_major_axes[0]**3/self.star_mass)
        time_after_20_orbits = 20*home_planet_orbital_period

        simulation_duration = float(simulation_duration)
        if simulation_duration < time_after_20_orbits:
            raise ValueError('Argument "simulation_duration" is %g but must be at least %g yr (20 orbits).' % (simulation_duration, time_after_20_orbits))

        if filename is not None:
            filename = str(filename)

        if number_of_output_points is not None:
            number_of_output_points = int(number_of_output_points)
            if number_of_output_points <= 0:
                raise ValueError('The number of output points is %d but must be at larger than zero.' % number_of_output_points)

        times = np.linspace(0, simulation_duration, number_of_times)
        correct_planet_positions = self._compute_planet_trajectories(times)

        check_time_limit_idx = np.searchsorted(times, time_after_20_orbits)

        limited_planet_positions         =         planet_positions[:, :, :(check_time_limit_idx+1)]
        limited_correct_planet_positions = correct_planet_positions[:, :, :(check_time_limit_idx+1)]

        deviations = np.abs(np.linalg.norm(limited_planet_positions - limited_correct_planet_positions, axis=0)/np.linalg.norm(limited_correct_planet_positions, axis=0))
        worst_planet_idx, worst_time_idx = np.unravel_index(np.argmax(deviations), deviations.shape)
        worst_deviation = deviations[worst_planet_idx, worst_time_idx]

        max_deviation = 1e-2 # Max relative deviation allowed

        if self.verbose:
            print('The biggest relative deviation was for planet %d, which drifted %g %% from its actual position.' % (worst_planet_idx, 100*worst_deviation))

        if worst_deviation > max_deviation:
            print('Your planets are not where they should be after 20 orbits of your home planet.')
            print('Check your program for flaws or experiment with your time step for more precise trajectories.')
            raise RuntimeError('Incorrect planet positions.')
        elif self.verbose:
            print('Your planet trajectories were satisfyingly calculated. Well done!')
            print('*** Achievement unlocked: Well-behaved planets! ***')

        if filename is not None:

            if number_of_output_points is not None and number_of_output_points != number_of_times:
                times = np.linspace(0, simulation_duration, number_of_output_points)
                correct_planet_positions = self._compute_planet_trajectories(times)

            with open(filename, 'wb') as f:
                np.savez_compressed(f, times=times, planet_positions=correct_planet_positions)

            if self.verbose:
                print('Exact planet trajectories saved to %s.' % filename)

    def generate_system_snapshot(self, filename='system_snapshot.xml'):
        """Generates a snapshot of the initial state of the solar system that can be viewed in SSView.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory. Default is "system_snapshot.xml".
        """
        filename = str(filename)

        output_times = np.zeros(1)
        output_planet_positions = self.initial_positions[:, :, np.newaxis]
        output_rotation_angles = np.zeros((self.number_of_planets, 1))
        planet_indices = range(self.number_of_planets)

        system_xml = _SolarSystemXML(self, visualization_program='SSView')
        objects = system_xml._create_objects_element(output_times, output_planet_positions, output_rotation_angles, planet_indices)
        system_xml._write_to_file(filename, [objects], verbose=self.verbose)

    def generate_orbit_video(self, times, planet_positions, number_of_frames=None, reduce_other_periods=True, filename='orbit_video.xml'):
        """Generates a video of the given planet trajectories that can be played in SSView.

        Note
        ----
            The times and positions for the output frames will be sampled uniformly from `times` and `planet_positions`.

        Parameters
        ----------
        times : 1-D array_like
            Array containing the time of each frame in years.
            Must have a size of at least 100.
        planet_positions : 3-D array_like
            Array of shape (2, `number_of_planets`, len(`times`)) containing the x and y-position of each planet at each time, in astronomical units relative to the star.
        number_of_frames : int, optional
            The number of video frames to generate.
            By default, a suitable number is determined automatically.
            Must be at least 100 if specified.
        reduce_other_periods : bool, optional
            Whether to slow down the rotation of planets that are rotating too fast to be animated properly,
            and also do the same for the orbits and rotations of moons.
            Note that the orbital speeds of the planets are not touched.
            Default is True.
        filename : str, optional
            Name of the XML file to generate inside the data directory. Default is "orbit_video.xml".
        """
        times = np.asarray(times, dtype=float)
        if times.ndim != 1:
            raise ValueError('Argument "times" has %d dimensions but must have 1 dimension.' % times.ndim)

        number_of_times = len(times)
        if number_of_times < 100:
            raise ValueError('The number of provided times is %d but must be at least 100.' % number_of_times)

        planet_positions = np.asarray(planet_positions, dtype=float)
        if planet_positions.shape != (2, self.number_of_planets, number_of_times):
            raise ValueError('Argument "planet_positions" has shape %s but must have shape (2, %d, %d).' % (str(planet_positions.shape), self.number_of_planets, number_of_times))

        if number_of_frames is None:
            frames_per_fastest_orbit = 30
            shortest_planet_orbital_period = np.amin(np.sqrt(self.semi_major_axes**3))
            number_of_frames = max(100, int((times[-1] - times[0])*frames_per_fastest_orbit/shortest_planet_orbital_period))
        else:
            number_of_frames = int(number_of_frames)
            if number_of_frames < 100:
                raise ValueError('Argument "number_of_frames" is %d but must be at least 100.' % number_of_frames)

        filename = str(filename)

        output_times = np.linspace(times.min(), times.max(), number_of_frames)

        position_interpolator = interpolate.interp1d(times, planet_positions, axis=2, kind='cubic', bounds_error=True, assume_sorted=False, copy=False)
        output_planet_positions = position_interpolator(output_times)

        if reduce_other_periods:
            time_step = (output_times[-1] - output_times[0])/(number_of_frames - 1)
            rotational_speed_adjustments = self._compute_planet_rotational_speed_adjustments(time_step)
        else:
            rotational_speed_adjustments = 1.0

        output_rotation_angles = self._compute_planet_rotational_angle_evolutions(output_times, speed_adjustments=rotational_speed_adjustments)

        planet_indices = range(self.number_of_planets)

        if self.verbose:
            print('Generating orbit video with %d frames.' % (number_of_frames))
            if reduce_other_periods:
                print('Note that planet/moon rotations and moon velocities are adjusted for smooth animation.')

        system_xml = _SolarSystemXML(self, adjust_moon_orbital_speeds=reduce_other_periods,
                                           adjust_moon_rotational_speeds=reduce_other_periods,
                                           visualization_program='SSView')

        objects = system_xml._create_objects_element(output_times, output_planet_positions, output_rotation_angles, planet_indices)
        system_xml._write_to_file(filename, [objects], verbose=self.verbose)

    def generate_binary_star_orbit_video(self, times, planet_positions, star_1_positions, star_2_positions, number_of_frames=1000, filename='binary_star_video.xml'):
        """Generates a video of the given trajectories of a planet and two stars that can be played in SSView.

        Note
        ----
            The times and positions for the output frames will be sampled uniformly from `times` and the inputted position arrays.

        Parameters
        ----------
        times : 1-D array_like
            Array containing the time of each frame in years.
            Must have a size of at least 100.
        planet_positions : 2-D array_like
            Array of shape (2, len(`times`)) containing the x and y-position of the planet at each time, in astronomical units relative to the system center.
        star_1_positions : 2-D array_like
            Array of shape (2, len(`times`)) containing the x and y-position of star 1 at each time, in astronomical units relative to the system center.
        star_2_positions : 2-D array_like
            Array of shape (2, len(`times`)) containing the x and y-position of star 2 at each time, in astronomical units relative to the system center.
        number_of_frames : int, optional
            The number of video frames to generate.
            Default is 1000, but must be at least 100.
        filename : str, optional
            Name of the XML file to generate inside the data directory. Default is "binary_star_video.xml".
        """
        times = np.asarray(times, dtype=float)
        if times.ndim != 1:
            raise ValueError('Argument "times" has %d dimensions but must have 1 dimension.' % times.ndim)

        number_of_times = len(times)
        if number_of_times < 100:
            raise ValueError('The number of provided times is %d but must be at least 100.' % number_of_times)

        planet_positions = np.asarray(planet_positions, dtype=float)
        if planet_positions.shape != (2, number_of_times):
            raise ValueError('Argument "planet_positions" has shape %s but must have shape (2, %d).' % (str(planet_positions.shape), number_of_times))

        star_1_positions = np.asarray(star_1_positions, dtype=float)
        if star_1_positions.shape != (2, number_of_times):
            raise ValueError('Argument "star_1_positions" has shape %s but must have shape (2, %d).' % (str(star_1_positions.shape), number_of_times))

        star_2_positions = np.asarray(star_2_positions, dtype=float)
        if star_2_positions.shape != (2, number_of_times):
            raise ValueError('Argument "star_2_positions" has shape %s but must have shape (2, %d).' % (str(star_2_positions.shape), number_of_times))

        number_of_frames = int(number_of_frames)
        if number_of_frames < 100:
            raise ValueError('Argument "number_of_frames" is %d but must be at least 100.' % number_of_frames)

        filename = str(filename)

        output_times = np.linspace(times.min(), times.max(), number_of_frames)

        planet_position_interpolator = interpolate.interp1d(times, planet_positions, axis=1, kind='cubic', bounds_error=True, assume_sorted=False, copy=False)
        star_1_position_interpolator = interpolate.interp1d(times, star_1_positions, axis=1, kind='cubic', bounds_error=True, assume_sorted=False, copy=False)
        star_2_position_interpolator = interpolate.interp1d(times, star_2_positions, axis=1, kind='cubic', bounds_error=True, assume_sorted=False, copy=False)

        output_planet_positions = planet_position_interpolator(output_times)
        output_star_1_positions = star_1_position_interpolator(output_times)
        output_star_2_positions = star_2_position_interpolator(output_times)

        system_xml = _SolarSystemXML(self, visualization_program='SSView')
        objects = system_xml._create_binary_star_orbit_objects(output_times, output_planet_positions, output_star_1_positions, output_star_2_positions)
        system_xml._write_to_file(filename, [objects], verbose=self.verbose)

    def generate_landing_video(self, times, lander_positions, planet_idx, initial_system_time=0, number_of_frames=1000, filename='landing_video.xml'):
        """Generates a video of the given lander trajectory that can be played in SSView.

        Note
        ----
            The times and positions for the output frames will be sampled uniformly from `times` and `lander_positions`.

        Parameters
        ----------
        times : 1-D array_like
            Array containing the time of each frame, in seconds since the initial time of the landing sequence.
            Must have a size of at least 100.
        lander_positions : 2-D array_like
            Array of shape (2, len(`times`)) containing the x and y-position of the lander at each time, in meters relative to the destination planet center.
        planet_idx : int
            The index of the destination planet.
        initial_system_time : float, optional
            The system time when the landing sequence began in years.
            Default is 0.
        number_of_frames : int, optional
            The number of video frames to generate.
            Default is 1000, but must be at least 100.
        filename : str, optional
            Name of the XML file to generate inside the data directory. Default is "landing_video.xml".
        """
        times = np.asarray(times, dtype=float)
        if times.ndim != 1:
            raise ValueError('Argument "times" has %d dimensions but must have 1 dimension.' % times.ndim)

        number_of_times = len(times)
        if number_of_times < 100:
            raise ValueError('The number of provided times is %d but must be at least 100.' % number_of_times)

        lander_positions = np.asarray(lander_positions, dtype=float)
        if lander_positions.shape != (2, number_of_times):
            raise ValueError('Argument "lander_positions" has shape %s but must have shape (2, %d).' % (str(lander_positions.shape), number_of_times))

        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.number_of_planets - 1))

        initial_system_time = float(initial_system_time)
        if initial_system_time < 0:
            raise ValueError('Argument "initial_system_time" is %g but must be positive.' % initial_system_time)

        number_of_frames = int(number_of_frames)
        if number_of_frames < 100:
            raise ValueError('Argument "number_of_frames" is %d but must be at least 100.' % number_of_frames)

        filename = str(filename)

        resampled_times = np.linspace(times.min(), times.max(), number_of_frames)

        position_interpolator = interpolate.interp1d(times, lander_positions, axis=1, kind='cubic', bounds_error=True, assume_sorted=False, copy=False)
        resampled_lander_positions = position_interpolator(resampled_times)

        output_times = initial_system_time + utils.s_to_yr(resampled_times)

        output_planet_trajectories = self._compute_planet_trajectories(output_times)
        output_rotational_angles = self._compute_planet_rotational_angle_evolutions(output_times)

        output_lander_positions = output_planet_trajectories[:, planet_idx, :] + \
                                  resampled_lander_positions*self._compute_lander_position_scales(resampled_lander_positions)

        system_xml = _SolarSystemXML(self, visualization_program='SSView')
        objects = system_xml._create_objects_element(output_times, output_planet_trajectories, output_rotational_angles, [planet_idx])
        system_xml._add_spacecraft_subelement(objects, output_times, output_lander_positions)
        system_xml._write_to_file(filename, [objects], verbose=self.verbose)

    def _compute_lander_position_scales(self, positions):
        """
        Compute scaling factors for lander positions to give the correct trajectory when viewed in SSView.
        Input positions are in meters relative to the planet center.
        """
        distances = np.linalg.norm(positions*1e-3, axis=0) # [km]
        scales = 1e-3*distances**0.75/(50*500*distances)
        return scales[np.newaxis, :]

    def _init_seed(self, seed):

        seed = int(seed)
        if seed < 0 or seed > 99999:
            raise ValueError('Argument "seed" is %d but must be a 5-digit positive integer.' % seed)

        self._seed = seed

        # Set the seed of the random number generator
        self._random_state = np.random.RandomState(seed)

    def _init_path(self, data_path):

        self._data_path = 'XMLs' if data_path is None else os.path.abspath(str(data_path))

        if not os.path.isdir(self._data_path):
            os.mkdir(self._data_path)

    def _init_star(self):

        # Surface temperature of the star [K]
        self._star_temperature  = self._random_state.uniform(3000, 12000)

        # Mass of the star [solar masses]. Gives mostly between 0.15 msol and 5.7 msol
        # 0.075 solar masses is about the limit where we can get fusion
        self._star_mass    = np.amax([self.star_temperature**2/5800.0**2*self._random_state.normal(1, 0.1), 0.1])

        # Radius of star [km]. Found this empirical relation online
        self._star_radius  = np.abs(self.star_mass**0.724*7e5*self._random_state.normal(1, 0.1))

        self._star_color = utils._convert_temperature_to_RGB(self.star_temperature)

    def _init_planets(self):

        eps  = 0.25 # Minimum distance between semi-major axes, factor.

        self._number_of_planets      = self._random_state.randint(7, 9) # Number of planets in the system. Must not be more than 9, because of ID+numbering
        self._semi_major_axes        = np.zeros(self.number_of_planets) # Semi-major axes of planets, [AU].
        self._eccentricities         = np.zeros(self.number_of_planets) # Eccentricity of planets.
        self._masses                 = np.zeros(self.number_of_planets) # Mass of the planets, [solar masses].
        self._radii                  = np.zeros(self.number_of_planets) # Radiuses of planets, [km].
        self._initial_orbital_angles = np.zeros(self.number_of_planets) # Initial angle of planets' orbits.
        self._aphelion_angles        = np.zeros(self.number_of_planets) # Angle of semi-major axis for the planets.
        self._rotational_periods     = np.zeros(self.number_of_planets) # Rotational period of planets , [earth days].
        self._initial_positions      = np.zeros((2, self.number_of_planets)) # Initial position of planets, [AU].
        self._initial_velocities     = np.zeros((2, self.number_of_planets)) # Initial velocity of planets, [AU/yr].
        self._atmospheric_densities  = np.zeros(self.number_of_planets) # Atmosphere density at surface, [kg/m^3].
        self._mean_molecular_masses  = np.zeros(self.number_of_planets) # Mean molecular weight of atmosphere, [m_P].

        self._types = []    #for storing info

        for i in range(self.number_of_planets):
            # All systems have 'home' planets, similar to Earth temperature.
            if i == 0:
                self._types.append('rock')
                self._semi_major_axes[i]        = utils.km_to_AU(self.star_radius)/2*(self.star_temperature/self._random_state.uniform(320, 350))**2
                self._eccentricities[i]         = np.abs(self._random_state.normal(0, 0.02))
                self._initial_orbital_angles[i] = 0
                self._aphelion_angles[i]        = 0
                densi                           = self._random_state.uniform(4500., 6500) # Approx earth density
                self._rotational_periods[i]     = self._random_state.uniform(0.8, 1.3)
                self._masses[i]                 = self._random_state.uniform(1., 11)*1.e-6 # Close to earth mass
                self._radii[i]                  = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                self._mean_molecular_masses[i]  = 28.3
                self._atmospheric_densities[i]  = self._random_state.uniform(1, 1.5)

                R0          = self.semi_major_axes[i]*(1-self.eccentricities[i]*self.eccentricities[i]) / (1-self.eccentricities[i]*np.cos(self.initial_orbital_angles[i]-self.aphelion_angles[i]))
                v           = np.sqrt(self.star_mass*const.G_sol * (2/R0-1/self.semi_major_axes[i]))
                h           = np.sqrt(self.star_mass*const.G_sol*self.semi_major_axes[i]*(1-self.eccentricities[i]*self.eccentricities[i]))
                vPerp       = h/R0
                vParr       = 0
                self._initial_velocities[0, i] = -vPerp*np.sin(self.initial_orbital_angles[i])+vParr*np.cos(self.initial_orbital_angles[i])
                self._initial_velocities[1, i] =  vPerp*np.cos(self.initial_orbital_angles[i])+vParr*np.sin(self.initial_orbital_angles[i])
                self._initial_positions[0, i]  = R0*np.cos(self.initial_orbital_angles[i])
                self._initial_positions[1, i]  = R0*np.sin(self.initial_orbital_angles[i])

            # Manually place another planet in the Habitable zone !!
            elif i == 1:
                self._types.append('rock')
                self._semi_major_axes[i]        = utils.km_to_AU(self.star_radius)/2*(self.star_temperature/self._random_state.uniform(270, 300))**2

                self._eccentricities[i]         = np.abs(self._random_state.normal(0, 0.02))
                self._initial_orbital_angles[i] = self._random_state.uniform(0,2*const.pi)
                self._aphelion_angles[i]        = self._random_state.uniform(0,2*const.pi)
                self._rotational_periods[i]     = self._random_state.uniform(0.6, 2.1)
                densi                           = self._random_state.uniform(3000., 6500) #A wider range og densities
                self._masses[i]                 = 10**(-self._random_state.uniform(5, 7))
                self._radii[i]                  = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                self._mean_molecular_masses[i]  = self._random_state.uniform(20, 35)
                self._atmospheric_densities[i]  = self._random_state.uniform(0.5, 10)


                R0    = self.semi_major_axes[i]*(1-self.eccentricities[i]*self.eccentricities[i]) / (1.0-self.eccentricities[i]*np.cos(self.initial_orbital_angles[i]-self.aphelion_angles[i]))
                v     = np.sqrt(self.star_mass*const.G_sol * (2/R0-1/self.semi_major_axes[i]))
                h     = np.sqrt(self.star_mass*const.G_sol*self.semi_major_axes[i]*(1-self.eccentricities[i]*self.eccentricities[i]))
                vPerp = h/R0

                # In order to find the cartesian velocity components, we compute
                # the polar velocity components first.
                if self.initial_orbital_angles[i] > self.aphelion_angles[i]:
                    if self.initial_orbital_angles[i] > (self.aphelion_angles[i] + const.pi):
                        vParr = np.sqrt(v**2-vPerp**2)
                    else:
                        vParr = -np.sqrt(v**2-vPerp**2)
                else:
                    if self.initial_orbital_angles[i] < (self.aphelion_angles[i] - const.pi):
                        vParr = -np.sqrt(v**2-vPerp**2)
                    else:
                        vParr = np.sqrt(v**2-vPerp**2)

                self._initial_velocities[0, i] = -vPerp*np.sin(self.initial_orbital_angles[i])+vParr*np.cos(self.initial_orbital_angles[i])
                self._initial_velocities[1, i] =  vPerp*np.cos(self.initial_orbital_angles[i])+vParr*np.sin(self.initial_orbital_angles[i])
                self._initial_positions[0, i]  = R0*np.cos(self.initial_orbital_angles[i])
                self._initial_positions[1, i]  = R0*np.sin(self.initial_orbital_angles[i])

            # The other planets are randomly generated here.

            else:
                self._semi_major_axes[i] = self._random_state.uniform(.2*self.semi_major_axes[0], 8*self.semi_major_axes[1])
                #from 0.2 and up to 8 times habitable zone,
                #similar to planets mercury - Jupiter

                # Make sure semi-major axes are not too close to each other
                ok = True
                count = 1.
                while ok:
                    ok = False
                    count = count + 0.01 #Increase the max distance to which we can put planets...
                    #At some point, the loop must end... Right? RIGHT?!
                    for k in range(i):
                        while (np.abs(self.semi_major_axes[i]-self.semi_major_axes[k]) < (eps*(self.semi_major_axes[i]+self.semi_major_axes[k])*0.5)) :
                            self.semi_major_axes[i] = self._random_state.uniform(.2*self.semi_major_axes[0],8*count*self.semi_major_axes[1])
                            ok = True

                self._eccentricities[i]         = np.abs(self._random_state.normal(0, 0.05))
                self._initial_orbital_angles[i] = self._random_state.uniform(0, 2*const.pi)
                self._aphelion_angles[i]        = self._random_state.uniform(0, 2*const.pi)
                self._rotational_periods[i]     = self._random_state.uniform(0.6, 40)
                self._mean_molecular_masses[i]  = self._random_state.uniform(10, 30)

                R0    = self.semi_major_axes[i]*(1-self.eccentricities[i]*self.eccentricities[i]) / (1.0-self.eccentricities[i]*np.cos(self.initial_orbital_angles[i]-self.aphelion_angles[i]))
                v     = np.sqrt(self.star_mass*const.G_sol * (2/R0-1/self.semi_major_axes[i]))
                h     = np.sqrt(self.star_mass*const.G_sol*self.semi_major_axes[i]*(1-self.eccentricities[i]*self.eccentricities[i]))
                vPerp = h/R0
                vParr = np.sqrt(max(0.0, v**2 - vPerp**2))

                # In order to find the cartesian velocity components, we compute cos(a)*sin(b)-sin(a)*cos(b)
                # the polar velocity components first.
                if self.initial_orbital_angles[i] > self.aphelion_angles[i]:
                    if self.initial_orbital_angles[i] < (self.aphelion_angles[i] + const.pi):
                        vParr *= -1
                else:
                    if self.initial_orbital_angles[i] < (self.aphelion_angles[i] - const.pi):
                        vParr *= -1

                self._initial_velocities[0, i] = -vPerp*np.sin(self.initial_orbital_angles[i])+vParr*np.cos(self.initial_orbital_angles[i])
                self._initial_velocities[1, i] =  vPerp*np.cos(self.initial_orbital_angles[i])+vParr*np.sin(self.initial_orbital_angles[i])
                self._initial_positions[0, i]  = R0*np.cos(self.initial_orbital_angles[i])
                self._initial_positions[1, i]  = R0*np.sin(self.initial_orbital_angles[i])

                r_vect = (utils.AU_to_m(self.initial_positions[0, i]), utils.AU_to_m(self.initial_positions[1, i]))
                T_planet = self.star_temperature*np.sqrt(self.star_radius*1000/(2*np.linalg.norm(r_vect)))
                earth_radius = 6371*10**3 #[m]
                #all units now in SI #TODO (I do not think they are SI! -Robert)
                #checks if the planet is located outside the frost zone

                # sannsynlighet avhengig av temp? Laver temp = is-planeter
                if T_planet < 170:
                    R = (self.star_temperature/T_planet)**2*(self.star_radius/2) # distance star --> planet
                    R_max = (self.star_temperature/170)**2*(self.star_radius/2)*4 # max distance to ice-planet = 4*frost zone

                    #Probability of finding a gas planet within frost zone to 4 * frost zone
                    if R < R_max:

                        # there's 30% chance of stone-dwarf, 1% chance of gas dwarf and 69% chance of gas giant
                        prob = self._random_state.uniform(0, 1)
                        if prob < 0.3:
                            self._types.append('rock')
                            self._masses[i]                = 10**(-self._random_state.uniform(7.5, 8.5))
                            densi                           = self._random_state.uniform(2000., 6500)
                            self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                            self._atmospheric_densities[i] = self._random_state.uniform(1, 1.5)
                        #gas dwarf  (GAS)
                        elif prob < 0.31:
                            self._types.append('gas')
                            self._masses[i]                = 10**(-self._random_state.uniform(5, 6.5))
                            densi                           = self._random_state.uniform(400., 2000)
                            self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                            self._atmospheric_densities[i] = self._random_state.uniform(18, 25)

                        #gas giant  (GAS)
                        else:
                            self._types.append('gas')
                            self._masses[i]                = 10**(-self._random_state.uniform(2 - np.log10(self.star_mass), 5))
                            densi                           = self._random_state.uniform(500., 1000) + 1000*max(np.log10(3500*self.masses[i]), 0)
                            self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                            self._atmospheric_densities[i] = self._random_state.uniform(18, 25)
                    # if the planet is too far out, they are all ice planets
                    else:
                        prob = self._random_state.uniform(0, 1)
                        # ice giant (GAS)
                        if prob < 0.4:
                            self._types.append('gas')
                            self._masses[i]                = 10**(-self._random_state.uniform(4, 6))
                            densi                           = self._random_state.uniform(900., 2500)
                            self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                            self._atmospheric_densities[i] = self._random_state.uniform(1.3, 3)

                        else: #ice dwarf
                            self._types.append('rock')
                            self._masses[i]                = 10**(-self._random_state.uniform(6.5, 8.5))
                            densi                           = self._random_state.uniform(1500., 2500)
                            self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                            self._atmospheric_densities[i] = self._random_state.uniform(1, 1.5)

                # all planets within snow zone are mostly stone planets
                else:
                    prob = self._random_state.uniform(0, 1)
                    if prob < 0.96:
                        self._types.append('rock')
                        self._masses[i]                = 10**(-self._random_state.uniform(5.5, 7.5))
                        densi                           = self._random_state.uniform(4000., 6500)
                        self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                        self._atmospheric_densities[i] = self._random_state.uniform(1, 1.5) #TODO 2017 all dwarf rho0 should be down to 0.


                    else:
                        self._types.append('gas') #Some probability for hot jupiters (GAS)
                        self._masses[i]                = 10**(-self._random_state.uniform(2 - np.log10(self.star_mass), 4.5))
                        densi                           = self._random_state.uniform(600., 2500)
                        self._radii[i]                 = (3*self.masses[i]*const.m_sun/(4*const.pi*densi))**(1./3.)*0.001
                        self._atmospheric_densities[i] = self._random_state.uniform(18, 25)

                if self._radii[i] > 15000:
                    self._rotational_periods[i] = self._random_state.uniform(0.2, 0.9)

        # Make the data arrays readonly to avoid modification by students

        arrays = [self._semi_major_axes,
                  self._eccentricities,
                  self._masses,
                  self._radii,
                  self._initial_orbital_angles,
                  self._aphelion_angles,
                  self._rotational_periods,
                  self._initial_positions,
                  self._initial_velocities,
                  self._atmospheric_densities,
                  self._mean_molecular_masses]

        for arr in arrays:
            arr.setflags(write=False)

        self._types = tuple(self._types)

    def _init_moons(self, has_moons):

        self._has_moons = bool(has_moons)

        self._moons = [] # For storing moons!

        if (self._has_moons):
            for i in range(self.number_of_planets):
                self._moons.append(_Moons(self, i))

    def _compute_gravitational_acceleration(self, displacement, mass):
        """Computes the acceleration of a single body due to the gravity of another body at relative position r.

        Parameters
        ----------
        displacement : 1-D array_like
            Displacement vector of shape (2,) or (3,) to the other body in astronomical units.
        mass : float
            Mass of the other body in solar masses.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Acceleration vector of shape (2,) or (3,) for the first body in solar system units.
        """
        displacement = np.asarray(displacement, dtype=float)
        distance = np.linalg.norm(displacement)
        return (-const.G_sol*mass/distance**3)*displacement

    def _compute_single_planet_trajectory(self, times, planet_idx):
        """Computes the evolution of positions of a given planet in the system over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the positions, in years.
        planet_idx : int
            Index of the planet to compute the position of.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (2, len(`times`)) containing the positions of the planet in astronomical units.
        """
        positions = np.zeros((2, len(times)))

        orbital_angles = self._compute_single_planet_orbital_angle_evolution(times, planet_idx)
        distances  = self.semi_major_axes[planet_idx]*(1 - self.eccentricities[planet_idx]**2)\
                     /(1 - self.eccentricities[planet_idx]*np.cos(orbital_angles - self.aphelion_angles[planet_idx]))
        positions[0, :] = distances*np.cos(orbital_angles)
        positions[1, :] = distances*np.sin(orbital_angles)

        # Make sure position matches initial position exactly at time 0
        positions[:, times == 0.0] = self.initial_positions[:, planet_idx:planet_idx+1]

        return positions

    def _compute_planet_trajectories(self, times):
        """Computes the evolution of positions of each planet in the system over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the positions, in years.

        Returns
        -------
        3-D :class:`numpy.ndarray`
            Array of shape (2, `number_of_planets`, len(`times`)) containing the positions of the planets in astronomical units.
        """
        positions = np.zeros((2, self.number_of_planets, len(times)))

        for planet_idx in range(self.number_of_planets):
            positions[:, planet_idx, :] = self._compute_single_planet_trajectory(times, planet_idx)

        return positions

    def _compute_single_planet_position(self, time, planet_idx):
        """Computes the position of a given planet in the system at a given time.

        Parameters
        ----------
        time : float
            Time for which to obtain the position, in years.
        planet_idx : int
            Index of the planet to compute the position of.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the position of the planet in astronomical units.
        """
        return self._compute_single_planet_trajectory(np.array([time]), planet_idx)[:, 0]

    def _compute_planet_positions(self, time):
        """Computes the position of each planet in the system at a given time.

        Parameters
        ----------
        time : float
            Time for which to obtain the positions, in years.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (2, `number_of_planets`) containing the positions of the planets in astronomical units.
        """
        return self._compute_planet_trajectories(np.array([time]))[:, :, 0]

    def _compute_single_planet_velocity_evolution(self, times, planet_idx):
        """Computes the evolution of velocities of a given planet in the system over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the velocities, in years.
        planet_idx : int
            Index of the planet to compute the velocity of.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (2, len(`times`)) containing the velocities of the planet in astronomical units per year.
        """
        velocity_evolution = np.gradient(self._compute_single_planet_trajectory(times, planet_idx), times, axis=1)

        # Make sure velocity matches initial velocity exactly at time 0
        velocity_evolution[:, times == 0.0] = self.initial_velocities[:, planet_idx:planet_idx+1]

        return velocity_evolution

    def _compute_planet_velocity_evolutions(self, times):
        """Computes the evolution of velocities of each planet in the system over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the velocities, in years.

        Returns
        -------
        3-D :class:`numpy.ndarray`
            Array of shape (2, `number_of_planets`, len(`times`)) containing the velocities of the planets in astronomical units per year.
        """
        velocity_evolutions = np.gradient(self._compute_planet_trajectories(times), times, axis=2)

        # Make sure velocities match initial velocities exactly at time 0
        velocity_evolutions[:, :, times == 0.0] = self.initial_velocities[:, :, np.newaxis]

        return velocity_evolutions

    def _compute_single_planet_velocity(self, time, planet_idx, dt=1e-8):
        """Computes the velocity of a given planet in the system at a given time.

        Parameters
        ----------
        time : float
            Time for which to obtain the velocity, in years.
        planet_idx : int
            Index of the planet to compute the velocity of.
        dt : float, optional
            The time interval to use for the finite difference approximation.
            Default is 10^-8.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the velocity of the planet in astronomical units per year.
        """
        if time == 0.0:
            # Make sure velocity match initial velocity exactly at time 0
            velocity = self.initial_velocities[:, planet_idx].copy()
        else:
            velocity = (self._compute_single_planet_position(time + dt, planet_idx) - self._compute_single_planet_position(time - dt, planet_idx))/(2*dt)
        return velocity

    def _compute_planet_velocities(self, time, dt=1e-8):
        """Computes the velocity of each planet in the system at a given time.

        Parameters
        ----------
        time : float
            Time for which to obtain the velocity, in years.
        dt : float, optional
            The time interval to use for the finite difference approximation.
            Default is 10^-8.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (2, `number_of_planets`) containing the velocities of the planets in astronomical units per year.
        """
        if time == 0.0:
            # Make sure velocities match initial velocities exactly at time 0
            velocities = self.initial_velocities.copy()
        else:
            velocities = (self._compute_planet_positions(time + dt) - self._compute_planet_positions(time - dt))/(2*dt)
        return velocities

    def _compute_single_planet_orbital_angle_evolution(self, times, planet_idx):
        """Computes the evolution of orbital angles of a given planet in the system over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the orbital angle, in years.
        planet_idx : int
            Index of the planet to compute the orbital angle of.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (len(`times`),) containing the approximate orbital angles of the planet in radians.

        Raises
        ------
        StopIteration
            When Newton's method has not converged after 50 iterations.
        """
        dx            = 1e-5  # Step size used for the numerical derivative.
        tolerance     = 1e-7  # Tolerance used for Newton's method.
        maxIterations = 50    # Maximum number of iterations for Newton's method.

        times = np.asarray(times, dtype=float)

        # Angular momentum per mass.
        h   = np.sqrt(self.star_mass*const.G_sol*self.semi_major_axes[planet_idx]*(1-self.eccentricities[planet_idx]*self.eccentricities[planet_idx]))
        sqt = np.sqrt(self.star_mass*const.G_sol/self.semi_major_axes[planet_idx]**3)

        iterations = 1
        x0  = times*sqt + self.initial_orbital_angles[planet_idx] # Initial guess.
        x00 = x0
        ff  = self._compute_angle_integral(x0 - self.aphelion_angles[planet_idx], self.eccentricities[planet_idx])  # Function value at initial guess.
        ffo = self._compute_angle_integral(self.initial_orbital_angles[planet_idx] - self.aphelion_angles[planet_idx], self.eccentricities[planet_idx])  # The integral constant used in the optimization equation.
        lenmask = 1
        try :

            while ((lenmask > 0) and (iterations < maxIterations)) :
                mask = (np.abs(ff-times*h/(self.semi_major_axes[planet_idx]*self.semi_major_axes[planet_idx]*(1-self.eccentricities[planet_idx]*self.eccentricities[planet_idx]))-ffo) > tolerance)
                lenmask = np.sum(mask)
                iterations = iterations + 1
                dfdx = (self._compute_angle_integral(x0[mask]+dx-self.aphelion_angles[planet_idx],self.eccentricities[planet_idx])-ff[mask]) / dx
                x0[mask]   = x0[mask] - (ff[mask] - h*times[mask]/(self.semi_major_axes[planet_idx]*self.semi_major_axes[planet_idx]*(1-self.eccentricities[planet_idx]*self.eccentricities[planet_idx]))-ffo)/dfdx
                ff[mask]   = self._compute_angle_integral(x0[mask]-self.aphelion_angles[planet_idx],self.eccentricities[planet_idx])

                # If the maximum number of iterations has been reached, throw a
                # StopIteration exception and exit the program.
                if (iterations == maxIterations) :
                    raise StopIteration()
                    exit()

        except StopIteration as error:
            traceback.print_exc(limit=1, file=sys.stdout)
            print('\nError: Newton\'s method did not converge after %d iterations.' % maxIterations)
            print('time          = ', time)
            print('planet number = ', planet_idx)

        # Make sure orbital angle matches initial orbital angle exactly at time 0
        x0[times == 0.0] = self.initial_orbital_angles[planet_idx]

        return x0

    def _compute_angle_integral(self, theta, eccentricity):
        """Computes the integral of F(theta) of f(theta) = 1/(1 - e*cos(theta))^2.

        Parameters
        ----------
        theta : float
            The orbital angle in radians.
        eccentricity : float
            The eccentricity of the orbit.

        Returns
        -------
        float
            The value of the integral (sans integration constant).
        """
        sq = np.sqrt(1.0-eccentricity**2)
        y = (eccentricity+1)*np.tan(theta/2.0)/sq
        n = np.floor((theta+const.pi)/(2*const.pi))
        return -eccentricity*np.sin(theta)/(eccentricity*np.cos(theta)-1) + 2*(np.arctan(y)+n*const.pi)/sq

    def _compute_planet_rotational_angle_evolutions(self, times, speed_adjustments=1):
        """Computes the evolution of rotational angles of each planet about it's own axis over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the rotation angles, in years.
        speed_adjustments : float or 1-D array_like
            Adjustment factor(s) for rotational speed.
            Either a scalar to use for all planets or an array of shape (`number_of_planets`,) with separate factors for each planet.
            Default is no adjustment.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (`number_of_planets`, len(`times`)) containing the rotation angles of the planets in radians.
        """
        times = np.asarray(times, dtype=float)
        rotation_frequencies = speed_adjustments/utils.day_to_s(self.rotational_periods) # [1/s]
        return np.outer(rotation_frequencies, 2*const.pi*utils.yr_to_s(times))

    def _compute_planet_rotational_angles(self, time):
        """Computes the rotational angle of each planet about it's own axis at a given time.

        Parameters
        ----------
        time : float
            Time for which to obtain the rotation angles, in years.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (`number_of_planets`,) containing the rotation angles of the planets in radians.
        """
        return self._compute_planet_rotational_angle_evolutions(np.array([time]))[:, 0]

    def _compute_single_planet_rotational_angle(self, time, planet_idx):
        """Computes the rotational angle of a given planet about it's own axis at a given time.

        Parameters
        ----------
        time : float
            Time for which to obtain the rotation angle, in years.

        Returns
        -------
        float
            The rotation angle of the planet in radians.
        """
        return self._compute_planet_rotational_angles(time)[planet_idx]

    def _compute_planet_rotational_speed_adjustments(self, time_step, min_steps_per_rotation=5):
        """Computes the factor that the rotational speeds must be multiplied with in order for the shortest rotational period to take at least the given number of time steps.

        Parameters
        ----------
        time_step : float
            The time step in years.
        min_steps_per_rotation : int
            The minimum number of time steps that a full rotation should take.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (`number_of_planets`,) containing the required adjustment factors for rotational speeds.
        """
        current_min_steps_per_rotation = utils.day_to_yr(self._rotational_periods)/time_step
        return np.minimum(1.0, current_min_steps_per_rotation/min_steps_per_rotation)

    def _compute_single_planet_temperature(self, planet_idx):
        """Computes the surface temperature of a given planet assuming it's a blackbody.

        Parameters
        ----------
        planet_idx : int
            Index of the planet to compute the temperature of.

        Returns
        -------
        float
            The surface temperature of the planet in kelvin.
        """
        return self.star_temperature*np.sqrt((utils.km_to_AU(self.star_radius))/(2*self.semi_major_axes[planet_idx]))

    def _compute_force_balance_distance(self, planet_idx, k=10):
        return self.semi_major_axes[planet_idx]*np.sqrt(self.masses[planet_idx]/(k*self.star_mass))

    def _generate_spacecraft_video(self, times, positions, camera_angles, planet_idx=None, last_valid_camera_time=None, filename='spacecraft_video.xml'):
        """Generates a video of the given spacecraft trajectory that can be played in MCAst.

        Parameters
        ----------
        times : 1-D array_like
            Array containing the time of each frame in years.
        positions : 2-D array_like
            Array of shape (2, len(`times`)) containing the position of the spacecraft at each time, in astronomical units.
        camera_angles : 2-D array_like
            Array of shape (2, len(`times`)) containing the theta and phi angle of the camera direction at each time, in radians.
        planet_idx : int, optional
            If provided, only the planet with the given index is rendered.
        last_valid_camera_time : float, optional
            If provided, MCAst is told that the camera status is invalid after the given time. Default is never.
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "spacecraft_video.xml".
        """
        times = np.asarray(times, dtype=float)
        camera_angles = np.asarray(camera_angles, dtype=float)
        positions = np.asarray(positions, dtype=float)

        if last_valid_camera_time is None:
            last_valid_camera_time = np.amax(times) + 1 # Camera is OK until the end if last_valid_camera_time is None

        planet_positions = self._compute_planet_trajectories(times)
        rotation_angles = self._compute_planet_rotational_angle_evolutions(times)

        if planet_idx is None:
            planet_indices = range(self.number_of_planets)
        else:
            assert 0 <= planet_idx < self.number_of_planets, \
                'invalid planet index %d' % planet_idx
            planet_indices = [planet_idx]

        system_xml = _SolarSystemXML(self, visualization_program='MCAst')
        objects = system_xml._create_objects_element(times, planet_positions, rotation_angles, planet_indices)
        cameras = system_xml._create_cameras_element(times, positions, camera_angles, last_valid_camera_time)
        system_xml._write_to_file(filename, [objects, cameras], verbose=self.verbose)

    def _generate_spacecraft_picture(self, time, position, camera_angle, planet_idx=None, filename='spacecraft_picture.xml'):
        """Generates a picture from the given spacecraft state that can be viewed in MCAst.

        Parameters
        ----------
        time : float
            The time of the picture in years.
        position : 1-D array_like
            Array of shape (2,) containing the position of the spacecraft in astronomical units.
        camera_angle : 1-D array_like
            Array of shape (2,) containing the theta and phi angle of the camera direction in radians.
        planet_idx : int, optional
            If provided, only the planet with the given index is rendered.
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "spacecraft_picture.xml".
        """
        self._generate_spacecraft_video(np.asarray([time], dtype=float),
                                        np.asarray(position, dtype=float)[:, np.newaxis],
                                        np.asarray(camera_angle, dtype=float)[:, np.newaxis],
                                        planet_idx=planet_idx,
                                        filename=filename)


class _Moons(object):
    """Represents a randomized set of moons orbiting a planet.

    Parameters
    ----------
    system : SolarSystem
        The instance of SolarSystem that the moons are to belong to.
    planet_idx : int
        The index of the planet that should be the parent of the moons.
    """
    def __init__(self, system, planet_idx):

        number_of_moons = system._random_state.randint(0, max(1, int(system.radii[planet_idx]/2500)))

        # Number of moons must not be < 98 because of ID+numbering
        if number_of_moons > 98:
            number_of_moons = 98

        self._number_of_moons = number_of_moons
        self._inclinations = system._random_state.uniform(-0.1, 0.1)
        self._radii = np.zeros(number_of_moons)   # Radiuses of moons, [km].
        self._orbital_frequencies = np.zeros(number_of_moons)   # angular freq of moons' orbits.
        self._rotational_frequencies = np.zeros(number_of_moons)   # angular freq of moons' self rotation.
        self._initial_orbital_angles = np.zeros(number_of_moons)     # Initial angle of moons' orbits.
        self._distances = np.zeros(number_of_moons) # Orbital distance from planet.

        for moon_idx in range(number_of_moons):
            self._radii[moon_idx] = system._random_state.uniform(400.,min(4000., 0.4*system.radii[planet_idx]))
            self._initial_orbital_angles[moon_idx] = system._random_state.uniform(0.,2.*const.pi)
            self._distances[moon_idx] = utils.km_to_AU(system._random_state.uniform(3., 100.)*system.radii[planet_idx])
            omegao = np.sqrt(const.G_sol*system.masses[planet_idx]/(self._distances[moon_idx]**3))
            self._orbital_frequencies[moon_idx] = omegao
            self._rotational_frequencies[moon_idx] = system._random_state.uniform(omegao, 2*omegao)

    def _compute_orbital_speed_adjustments(self, time_step, min_steps_per_orbit=15):
        orbital_periods = 2*const.pi/self._orbital_frequencies
        current_min_steps_per_orbit = orbital_periods/time_step
        return np.minimum(1.0, current_min_steps_per_orbit/min_steps_per_orbit)

    def _compute_rotational_speed_adjustments(self, time_step, min_steps_per_rotation=5):
        rotational_periods = 2*const.pi/self._rotational_frequencies
        current_min_steps_per_rotation = rotational_periods/time_step
        return np.minimum(1.0, current_min_steps_per_rotation/min_steps_per_rotation)

    def _compute_positions(self, time, speed_adjustments=1.0):
        """Computes the positions of the moons relative to the parent planet at the given time.

        Parameters
        ----------
        time : float
            The time to compute the positions for, in years.
        speed_adjustments : float or 1-D array_like
            Adjustment factor(s) for orbital speed.
            Either a scalar to use for all moons or an array of shape (`number_of_moons`,) with separate factors for each moon.
            Default is no adjustment.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (`number_of_moons`, 3) containing the positions in astronomical units.
        """
        theta = self._initial_orbital_angles + speed_adjustments*self._orbital_frequencies*time #for rotation around orbit
        x = self._distances*np.cos(theta)
        y = self._distances*np.sin(theta)
        z = x*self._inclinations # Some inclination relative to ecliptic
        return np.transpose(np.array([x, y, z]))

    def _compute_rotations(self, time, speed_adjustments=1.0):
        """Computes the rotation angles of the moons at the given time.

        Parameters
        ----------
        time : float
            The time to compute the rotation angles for, in years.
        speed_adjustments : float or 1-D array_like
            Adjustment factor(s) for rotational speed.
            Either a scalar to use for all moons or an array of shape (`number_of_moons`,) with separate factors for each moon.
            Default is no adjustment.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (`number_of_moons`,) containing the rotation angles in radians.
        """
        return self._initial_orbital_angles + speed_adjustments*self._rotational_frequencies*time


class _SolarSystemXML:
    """Represents an XML hierarchy describing the state and time evolution of a SolarSystem.

    Parameters
    ----------
    system : SolarSystem
        The system to describe.
    """
    def __init__(self, system,
                 adjust_moon_orbital_speeds=False,
                 adjust_moon_rotational_speeds=False,
                 visualization_program='MCAst'):
        self._system = system
        self._adjust_moon_orbital_speeds = adjust_moon_orbital_speeds
        self._adjust_moon_rotational_speeds = adjust_moon_rotational_speeds
        self._visualization_program = visualization_program

    def _write_to_file(self, filename, elements, screenshot_size=900, verbose=True):

        # Write the XML hierarchy to file.
        outFile = open(os.path.join(self._system.data_path, filename), 'w')

        outFile.write("""<?xml version="1.0" encoding="utf-8"?>\n""")
        outFile.write("""<SerializedWorld xmlns:xsi="http://www.w3.org/2001/""")
        outFile.write("""XMLSchema-instance"\n xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n""")

        outFile.write('<sun_col_r>%.3f</sun_col_r>\n' % (self._system.star_color[0]/255.0))
        outFile.write('<sun_col_g>%.3f</sun_col_g>\n' % (self._system.star_color[1]/255.0))
        outFile.write('<sun_col_b>%.3f</sun_col_b>\n' % (self._system.star_color[2]/255.0))
        outFile.write('<sun_intensity>%.3f</sun_intensity>\n' % (0.1))
        outFile.write('<screenshot_width>%d</screenshot_width>\n' % screenshot_size)
        outFile.write('<screenshot_height>%d</screenshot_height>\n' % screenshot_size)
        outFile.write('<global_radius_scale>0.985</global_radius_scale>\n')
        outFile.write('<resolution>%.3d</resolution>\n' % 64)
        outFile.write('<uuid>5acbd644-37c7-11e6-ac61-9e71128cae77</uuid> \n')
        outFile.write('<skybox>%.3d</skybox>\n' % 0)

        for element in elements:
            outFile.write(etree.tostring(element, pretty_print=True, encoding='unicode'))

        outFile.write('</SerializedWorld>')

        outFile.close()

        if bool(verbose):
            print('XML file %s was saved in %s/.' % (filename, self._system.data_path))
            print('It can be viewed in %s.' % self._visualization_program)

    def _create_objects_element(self, times, planet_positions, rotation_angles, planet_indices):
        objects = etree.Element('Objects')
        star = self._create_star_subelement(objects)
        planet_objects = self._create_planet_objects_subelement(star, times, planet_positions, rotation_angles, planet_indices)
        return objects

    def _add_spacecraft_subelement(self, objects_element, times, spacecraft_positions):

        planet_objects = objects_element.find('SerializedMCAstObject').find('Objects')
        self._create_spacecraft_subelement(planet_objects, times, spacecraft_positions)

    def _create_binary_star_orbit_objects(self, times, planet_positions, star_1_positions, star_2_positions):

        names = ['planet', 'Star 1', 'Star 2']
        categories = ['planet', 'star', 'star']
        radii = [2000, 40000, 60000]
        temperatures = [367, 500, 5000]
        positions = [planet_positions, star_1_positions, star_2_positions]

        n_frames = len(times)

        objects = etree.Element("Objects")

        for object_idx in range(3):

            obj = etree.SubElement(objects, "SerializedMCAstObject")

            etree.SubElement(obj, "name").text              = str(names[object_idx])
            etree.SubElement(obj, "category").text          = str(categories[object_idx])

            etree.SubElement(obj, "radius").text            = str(radii[object_idx])
            etree.SubElement(obj, "temperature").text       = str(temperatures[object_idx])
            etree.SubElement(obj, "seed").text              = str(object_idx)
            etree.SubElement(obj, "atmosphereDensity").text = str(0)
            etree.SubElement(obj, "atmosphereHeight").text  = str(1.025)
            etree.SubElement(obj, "outerRadiusScale").text  = str(1.0025)

            for dim_idx, dim in zip(range(2), ['x','z']):
                etree.SubElement(obj, "pos_%s" % dim).text  = str(positions[object_idx][dim_idx, 0])
            etree.SubElement(obj, "pos_y").text             = str(0)

            etree.SubElement(obj, "rot_y").text             = str(0.01)

            frames = etree.SubElement(obj, "Frames")

            for frame_idx in range(n_frames):

                frame  = etree.SubElement(frames, "Frame")

                etree.SubElement(frame, "id").text               = str(frame_idx)

                for dim_idx, dim in zip(range(2), ['x','z']):
                    etree.SubElement(frame, "pos_%s" % dim).text = str(positions[object_idx][dim_idx, frame_idx])
                etree.SubElement(frame, "pos_y").text            = str(0)

                etree.SubElement(frame, "rot_y").text            = str(0.01)

        return objects

    def _create_cameras_element(self, times, camera_positions, camera_angles, last_valid_camera_time, field_of_view=70):

        n_frames = len(times)
        zero_time = times[0] if n_frames > 1 else 0

        cameras = etree.Element('Cameras')

        for frame_idx in range(n_frames):
            camera = etree.SubElement(cameras, 'SerializedCamera')

            for dim_idx, dim in zip(range(2), ['x','z']):
                etree.SubElement(camera, 'cam_%s' % dim).text = str(camera_positions[dim_idx, frame_idx])

            if camera_positions.shape[0] == 3:
                etree.SubElement(camera, 'cam_y').text        = str(camera_positions[2, frame_idx])
            else:
                etree.SubElement(camera, 'cam_y').text        = str(0)

            thetai = camera_angles[0, frame_idx]
            phii = camera_angles[1, frame_idx]

            dirvec = [np.sin(thetai)*np.cos(phii), np.sin(thetai)*np.sin(phii), np.cos(thetai)]
            upvec = [0., 0., 1.]

            for dim_idx, dim in zip(range(3), ['x','z','y']):
                etree.SubElement(camera, 'dir_%s' % dim).text = str(dirvec[dim_idx])

            for dim_idx, dim in zip(range(3), ['x','z','y']):
                etree.SubElement(camera, 'up_%s' % dim).text  = str(upvec[dim_idx])

            etree.SubElement(camera, 'fov').text   = str(field_of_view)

            etree.SubElement(camera, 'time').text  = str(times[frame_idx] - zero_time)

            etree.SubElement(camera, 'frame').text = str(frame_idx)

            if times[frame_idx] > last_valid_camera_time:
                etree.SubElement(camera, 'status').text = str(1)

        return cameras

    def _create_star_subelement(self, parent):

        star = etree.SubElement(parent, 'SerializedMCAstObject')

        etree.SubElement(star, 'category').text           = str('star')
        etree.SubElement(star, 'pos_x').text              = str(0)
        etree.SubElement(star, 'pos_z').text              = str(0)
        etree.SubElement(star, 'pos_y').text              = str(0)
        etree.SubElement(star, 'rot_y').text              = str(0)
        etree.SubElement(star, 'radius').text             = str(self._system.star_radius)
        etree.SubElement(star, 'temperature').text        = str(self._system.star_temperature)
        etree.SubElement(star, 'seed').text               = str(int(self._system.seed*1000 + 990))
        etree.SubElement(star, 'atmosphereDensity').text  = str(10)
        etree.SubElement(star, 'atmosphereHeight').text   = str(1.025)
        etree.SubElement(star, 'outerRadiusScale').text   = str(1.0025)
        etree.SubElement(star, 'name').text               = str('The star')

        return star

    def _create_planet_objects_subelement(self, parent, times, planet_positions, rotation_angles, planet_indices):

        planet_objects = etree.SubElement(parent, 'Objects')

        for planet_idx in planet_indices:
            planet = self._create_planet_subelement(planet_objects, times, planet_positions, rotation_angles, planet_idx)
            if self._system.has_moons:
                self._create_moon_objects_subelement(planet, times, planet_idx)

        return planet_objects

    def _create_spacecraft_subelement(self, parent, times, spacecraft_positions):

        n_frames = len(times)

        spacecraft = etree.SubElement(parent, "SerializedMCAstObject")

        # NB! In the xmls, y and z are swapped.
        # This is intentional to get everything right in Unity!
        for dim_idx, dim in zip(range(2), ['x','z']):
            etree.SubElement(spacecraft, "pos_%s" % dim).text = str(spacecraft_positions[dim_idx, 0])

        if spacecraft_positions.shape[0] == 3:
            etree.SubElement(spacecraft, "pos_y").text        = str(spacecraft_positions[2, 0])
        else:
            etree.SubElement(spacecraft, "pos_y").text        = str(0)

        etree.SubElement(spacecraft, "rot_y").text            = str(0)

        frames = etree.SubElement(spacecraft, "Frames")

        for frame_idx in range(n_frames):

            frame  = etree.SubElement(frames, "Frame")
            etree.SubElement(frame, "id").text               = str(frame_idx)

            for dim_idx, dim in zip(range(2), ['x','z']):
                etree.SubElement(frame, "pos_%s" % dim).text = str(spacecraft_positions[dim_idx, frame_idx])

            if spacecraft_positions.shape[0] == 3:
                etree.SubElement(frame, "pos_y").text        = str(spacecraft_positions[2, frame_idx])
            else:
                etree.SubElement(frame, "pos_y").text        = str(0)

            etree.SubElement(frame, "rot_y").text            = str(0)

        etree.SubElement(spacecraft, "radius").text            = str(4000)
        etree.SubElement(spacecraft, "temperature").text       = str(300)
        etree.SubElement(spacecraft, "seed").text              = str(int(self._system.seed*1000 + 950))
        etree.SubElement(spacecraft, "parentPlanet").text      = str(int(self._system.seed*1000 + 990))
        etree.SubElement(spacecraft, "atmosphereDensity").text = str(1)
        etree.SubElement(spacecraft, "atmosphereHeight").text  = str(1.025)
        etree.SubElement(spacecraft, "outerRadiusScale").text  = str(1.0025)
        etree.SubElement(spacecraft, "name").text              = str("Spacecraft")
        etree.SubElement(spacecraft, "category").text          = str("3dobject")
        etree.SubElement(spacecraft, "objectString").text      = str("Satellite")
        etree.SubElement(spacecraft, "objectMaterial").text    = str("HullMaterial")
        etree.SubElement(spacecraft, "color_r").text           = str(0.75)
        etree.SubElement(spacecraft, "color_g").text           = str(0.75)
        etree.SubElement(spacecraft, "color_b").text           = str(0.75)
        etree.SubElement(spacecraft, "objectScale").text       = str(0.001)

        return spacecraft

    def _create_planet_subelement(self, parent, times, planet_positions, rotation_angles, planet_idx):

        n_frames = len(times)

        planet = etree.SubElement(parent, 'SerializedMCAstObject')

        # NB! In the xmls, y and z are swapped.
        # This is intentional to get everything right in Unity!
        for dim_idx, dim in zip(range(2), ['x','z']):
            etree.SubElement(planet, 'pos_%s' % dim).text  = str(planet_positions[dim_idx, planet_idx, 0])
        etree.SubElement(planet, 'pos_y').text             = str(0)

        etree.SubElement(planet, 'rot_y').text             = str(-rotation_angles[planet_idx, 0])

        etree.SubElement(planet, 'radius').text            = str(self._system.radii[planet_idx])
        etree.SubElement(planet, 'temperature').text       = str(self._system._compute_single_planet_temperature(planet_idx))
        etree.SubElement(planet, 'seed').text              = str(int(self._system.seed*1000 + planet_idx))
        etree.SubElement(planet, 'atmosphereDensity').text = str(np.log(self._system.atmospheric_densities[planet_idx])/np.log(25))
        etree.SubElement(planet, 'atmosphereHeight').text  = str(1.025)
        etree.SubElement(planet, 'outerRadiusScale').text  = str(1.0025)
        etree.SubElement(planet, 'category').text          = str('planet')
        etree.SubElement(planet, 'name').text              = str('planet %d' % planet_idx)
        if (self._system.types[planet_idx] == 'gas'):
            etree.SubElement(planet, 'forcePlanetSurface').text = 'gas'

        frames = etree.SubElement(planet, 'Frames')

        for frame_idx in range(n_frames):

            frame  = etree.SubElement(frames, 'Frame')
            etree.SubElement(frame, 'id').text               = str(frame_idx)

            for dim_idx, dim in zip(range(2), ['x','z']):
                etree.SubElement(frame, 'pos_%s' % dim).text = str(planet_positions[dim_idx, planet_idx, frame_idx])
            etree.SubElement(frame, 'pos_y').text            = str(0)

            etree.SubElement(frame, 'rot_y').text            = str(-rotation_angles[planet_idx, frame_idx]) #left hand coordinate system in Unity!

        return planet

    def _create_moon_objects_subelement(self, parent, times, planet_idx):

        n_frames = len(times)

        if self._adjust_moon_orbital_speeds:
            assert n_frames > 1
            time_step = (times[-1] - times[0])/(n_frames - 1)
            orbital_speed_adjustments = self._system._moons[planet_idx]._compute_orbital_speed_adjustments(time_step)
        else:
            orbital_speed_adjustments = 1.0

        if self._adjust_moon_rotational_speeds:
            assert n_frames > 1
            time_step = (times[-1] - times[0])/(n_frames - 1)
            rotational_speed_adjustments = self._system._moons[planet_idx]._compute_rotational_speed_adjustments(time_step)
        else:
            rotational_speed_adjustments = 1.0

        moonPoses = np.zeros([n_frames, 3, self._system._moons[planet_idx]._number_of_moons])
        moonRots = np.zeros([n_frames, self._system._moons[planet_idx]._number_of_moons])

        for frame_idx in range(n_frames):
            moonPos = self._system._moons[planet_idx]._compute_positions(times[frame_idx], speed_adjustments=orbital_speed_adjustments)
            moonRot = self._system._moons[planet_idx]._compute_rotations(times[frame_idx], speed_adjustments=rotational_speed_adjustments)
            moonPoses[frame_idx] = np.transpose(moonPos)
            moonRots[frame_idx] = moonRot

        moon_objects = etree.SubElement(parent, 'Objects')

        for moon_idx in range(self._system._moons[planet_idx]._number_of_moons):
            moon = etree.SubElement(moon_objects, 'SerializedMCAstObject')

            # NB! In the xmls, y and z are swapped.
            # This is intentional to get everything right in Unity!
            for dim_idx, dim in zip(range(3), ['x','z','y']):
                etree.SubElement(moon, 'pos_%s' % dim).text = str(moonPoses[0][dim_idx,moon_idx])

            etree.SubElement(moon, 'rot_y').text        = str(-moonRots[0][moon_idx])

            frames = etree.SubElement(moon, 'Frames')
            for frame_idx in range(n_frames):
                frame  = etree.SubElement(frames, 'Frame')
                etree.SubElement(frame, 'id').text           = str(frame_idx)

                for dim_idx, dim in zip(range(3), ['x','z','y']):
                    etree.SubElement(frame, 'pos_%s' % dim).text = str(moonPoses[frame_idx][dim_idx,moon_idx])

                etree.SubElement(frame, 'rot_y').text        = str(-moonRots[frame_idx][moon_idx]) #left hand coordinate system in Unity!

            etree.SubElement(moon, 'radius').text            = str(self._system._moons[planet_idx]._radii[moon_idx])
            etree.SubElement(moon, 'temperature').text       = str(self._system._compute_single_planet_temperature(planet_idx))
            etree.SubElement(moon, 'seed').text              = str(int(self._system.seed*1000 + planet_idx + 10*(moon_idx + 1)))
            etree.SubElement(moon, 'parentPlanet').text      = str(int(self._system.seed*1000 + planet_idx))
            etree.SubElement(moon, 'atmosphereDensity').text = str(0)
            etree.SubElement(moon, 'atmosphereHeight').text  = str(0)
            etree.SubElement(moon, 'outerRadiusScale').text  = str(1.0025)
            etree.SubElement(moon, 'category').text          = str('moon')
            etree.SubElement(moon, 'name').text              = 'Moon %d of Planet %d' % (moon_idx + 1, planet_idx)

        return moon_objects
