# -*- coding: utf-8 -*-
"""Module containing the SpaceMissionShortcuts class."""
from __future__ import division, print_function, absolute_import
from six.moves import range, map

import numpy as np

import ast2000tools.constants as const
import ast2000tools.utils as utils
from ast2000tools.space_mission import SpaceMission


class SpaceMissionShortcuts(object):
    """Provides a set of shortcuts allowing you to proceed with the space mission when you are stuck.

    When you have been unable to proceed with a part of the mission for too long,
    it is important that you make use of the shortcuts so that you can continue
    without loosing a lot of time. Simply identify the shortcut method(s) that you
    require in order to proceed, and ask the project group teacher for the
    necessary code(s). Specify the name of the method and the seed value you are using.

    Parameters
    ----------
    mission : :class:`ast2000tools.space_mission.SpaceMission`
        The :class:`ast2000tools.space_mission.SpaceMission` instance to apply shortcuts to.
    codes : list(int)
        List of codes for unlocking shortcuts.
    """
    def __init__(self, mission, codes):

        if not isinstance(mission, SpaceMission):
            raise ValueError('Argument "mission" is an instance of %s but must be a SpaceMission instance.' % mission.__class__.__name__)

        self._mission = mission
        self._system = self._mission.system

        try:
            codes = list(codes)
        except TypeError:
            raise TypeError('Argument "codes" is not iterable.')

        if len(codes) < 1:
            raise ValueError('Argument "codes" is empty but must contain at least one element.')

        try:
            codes = map(int, codes)
        except ValueError:
            raise ValueError('Elements of argument "codes" can not be converted to integers.')

        self._codes = tuple(codes)

    @property
    def mission(self):
        """:class:`ast2000tools.space_mission.SpaceMission`: The mission to apply shortcuts to."""
        return self._mission

    @property
    def system(self):
        """:class:`ast2000tools.solar_system.SolarSystem`: The system associated with the mission to apply shortcuts to."""
        return self._system

    @property
    def codes(self):
        """tuple(int): The provided codes for unlocking shortcuts."""
        return self._codes

    def compute_engine_performance(self, number_density, temperature, hole_area):
        """Computes the thrust and mass loss rate for a single simulation box of the rocket combustion chamber.

        Parameters
        ----------
        number_density : float
            The number density of particles in the box, in particles per cubic meter.
        temperature : float
            The temperature in the box, in kelvin.
        hole_area : float
            The area of the nozzle hole that the particles can escape through, in square meters.

        Returns
        -------
        float
            The thrust per box in Newtons.
        float
            The mass loss rate per box in kilograms per second.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        """
        self._verify_code('engine_parameters')

        number_density = float(number_density)
        if number_density < 0:
            raise ValueError('Argument "number_density" is %g but must be a positive value.' % number_density)

        temperature = float(temperature)
        if temperature < 0:
            raise ValueError('Argument "temperature" is %g but must be a positive value.' % temperature)

        hole_area = float(hole_area)
        if hole_area < 0:
            raise ValueError('Argument "hole_area" is %g but must be a positive value.' % hole_area)

        thrust_per_box = 0.5*hole_area*number_density*const.k_B*temperature
        mass_loss_rate_per_box = number_density*hole_area*np.sqrt(const.m_H2*const.k_B*temperature/(2*const.pi))
        return thrust_per_box, mass_loss_rate_per_box

    def get_launch_results(self):
        """Returns the results of the previous launch.

        Returns
        -------
        float
            The total mass of fuel burned during the launch, in kilograms.
        float
            The time when the launch was completed, in years since the initial solar system time.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the x and y-position of the spacecraft, in astronomical units relative to the star.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the x and y-velocity of the spacecraft, in astronomical units per year relative to the star.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        RuntimeError
            When called before :meth:`~ast2000tools.space_mission.SpaceMission.launch_rocket` has been called successfully.
        """
        self._verify_code('launch_results')

        if self.mission.rocket_launched == False:
            print('You need to perform the rocket launch before you can obtain the results.')
            print('Please call launch_rocket before proceeding.')
            raise RuntimeError('Launch results not ready.')

        return self.mission._get_launch_results()

    def place_spacecraft_on_escape_trajectory(self, rocket_thrust, rocket_mass_loss_rate, time, height_above_surface, direction_angle, remaining_fuel_mass):
        """Places the spacecraft on an escape trajectory pointing directly away from the home planet.

        Parameters
        ----------
        rocket_thrust : float
            The total thrust of the rocket, in Newtons.
        rocket_mass_loss_rate : float
            The total mass loss rate of the rocket, in kilograms per second.
        time : float
            The time at which the spacecraft should be placed on the escape trajectory, in years from the initial system time.
        height_above_surface : float
            The heigh above the home planet surface to place the spacecraft, in meters.
        direction_angle : float
            The angle of the direction of motion of the spacecraft with respect to the x-axis, in degrees.
        remaining_fuel_mass : float
            The mass of fuel carried by the spacecraft after placing it on the escape trajectory, in kilograms.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        """
        self._verify_code('escape_trajectory')

        time = float(time)
        if time < 0:
            raise ValueError('Argument "time" is %g but must be positive.' % time)

        rocket_thrust = float(rocket_thrust)
        if rocket_thrust < 0:
            raise ValueError('Argument "rocket_thrust" is %g but must be positive.' % rocket_thrust)

        rocket_mass_loss_rate = float(rocket_mass_loss_rate)
        if rocket_mass_loss_rate < 0:
            raise ValueError('Argument "rocket_mass_loss_rate" is %g but must be positive.' % rocket_mass_loss_rate)

        height_above_surface = float(height_above_surface)
        if height_above_surface < 0 or height_above_surface > 4e7:
            raise ValueError('Argument "height_above_surface" is %g but must be in the range [0, %g] m.' % 4e7)

        remaining_fuel_mass = float(remaining_fuel_mass)
        if remaining_fuel_mass < 0:
            raise ValueError('Argument "remaining_fuel_mass" is %g but must be positive.' % remaining_fuel_mass)

        planet_radius = utils.km_to_AU(self.system.radii[0]) # [AU]
        planet_mass = self.system.masses[0] # [m_sun]

        direction_angle_rad = utils.deg_to_rad(direction_angle)
        direction_of_motion = np.asarray([np.cos(direction_angle_rad), np.sin(direction_angle_rad)], dtype=float)

        distance_from_center = planet_radius + utils.m_to_AU(height_above_surface) # [AU]
        spacecraft_position = self.system._compute_single_planet_position(time, 0) + distance_from_center*direction_of_motion

        escape_speed = np.sqrt(2*const.G_sol*planet_mass/distance_from_center) # [AU/yr]
        spacecraft_velocity = self.system._compute_single_planet_velocity(time, 0) + escape_speed*direction_of_motion

        self.mission._time_after_launch = time
        self.mission._position_after_launch = spacecraft_position
        self.mission._velocity_after_launch = spacecraft_velocity

        self.mission._rocket_thrust = rocket_thrust
        self.mission._rocket_mass_loss_rate = rocket_mass_loss_rate
        self.mission._fuel_needed_for_launch = None
        self.mission._remaining_fuel_mass_after_launch = remaining_fuel_mass

        # Make sure the results are not altered by mistake
        self.mission._position_after_launch.setflags(write=False)
        self.mission._velocity_after_launch.setflags(write=False)

        self.mission._launch_parameters_set = True
        self.mission._rocket_launched = True

        self.mission.verify_launch_result(self.mission._position_after_launch)

    def compute_planet_trajectories(self, times):
        """Computes the evolution of positions of each planet in the system over the given times.

        Parameters
        ----------
        times : 1-D array_like
            Array of times for which to obtain the positions, in years.

        Returns
        -------
        3-D :class:`numpy.ndarray`
            Array of shape (2, `number_of_planets`, len(`times`)) containing the positions of the planets in astronomical units.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        """
        self._verify_code('planet_trajectories')

        times = np.asarray(times, dtype=float)
        if times.ndim != 1:
            raise ValueError('Argument "times" has %d dimensions but must have 1 dimension.' % times.ndim)

        number_of_times = len(times)
        if number_of_times < 1:
            raise ValueError('The number of provided times is %d but must be at least 1.' % number_of_times)

        return self.system._compute_planet_trajectories(times)

    def get_orientation_data(self):
        """Returns the orientation data for the spacecraft directly after the previous launch.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the x and y-position of the spacecraft, in astronomical units relative to the star.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the x and y-velocity of the spacecraft, in astronomical units per year relative to the star.
        float
            The azimuthal angle of the spacecraft's pointing, in degrees.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        RuntimeError
            When called before :meth:`~ast2000tools.space_mission.SpaceMission.verify_launch_result` has been called successfully.
        """
        self._verify_code('orientation_data')

        if self.mission.launch_result_verified == False:
            print('You need to verify the launch results before you can obtain orientation data.')
            print('Please call verify_launch_result with the correct final position before proceeding.')
            raise RuntimeError('Orientation data not ready.')

        return self.mission._get_orientation_data()

    def place_spacecraft_in_unstable_orbit(self, time, planet_idx):
        """Places the spacecraft in a randomized elliptical orbit around the specified planet.

        Parameters
        ----------
        time : float
            The time at which the spacecraft should be placed in orbit, in years from the initial system time.
        planet_idx : int
            The index of the planet that the spacecraft should orbit.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        RuntimeError
            When called before :meth:`~ast2000tools.space_mission.SpaceMission.verify_manual_orientation` has been called successfully.
        """
        self._verify_code('unstable_orbit')

        time = float(time)
        if time < 0:
            raise ValueError('Argument "time" is %g but must be positive.' % time)

        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        # Create random state with offset seed to generate the same independent set of random numbers every time
        random_state = np.random.RandomState(self.system.seed + utils.get_seed('unstable_orbit'))

        max_spacecraft_distance = self.system._compute_force_balance_distance(planet_idx, k=10)

        spacecraft_distance = random_state.uniform(0.6, 0.95)*max_spacecraft_distance
        spacecraft_distance = max(utils.m_to_AU(self.system.radii[planet_idx]*1e3 + 1e4), spacecraft_distance)

        orbital_angle = random_state.uniform(0, 2*const.pi)
        radial_direction = np.array([np.cos(orbital_angle), np.sin(orbital_angle)])
        tangential_direction = np.array([-np.sin(orbital_angle), np.cos(orbital_angle)])

        eccentricity = random_state.uniform(0.5, 0.75)

        # Compute speed at periapsis
        spacecraft_speed = np.sqrt((1 + eccentricity)*const.G_sol*self.system.masses[planet_idx]/spacecraft_distance)

        planet_position = self.system._compute_single_planet_position(time, planet_idx)
        planet_velocity = self.system._compute_single_planet_velocity(time, planet_idx)

        spacecraft_position = planet_position + spacecraft_distance*radial_direction
        spacecraft_velocity = planet_velocity + spacecraft_speed*tangential_direction

        travel = self.mission.begin_interplanetary_travel()
        travel._move_to(time, spacecraft_position, spacecraft_velocity)
        travel.record_destination(planet_idx)

    def place_spacecraft_in_stable_orbit(self, time, orbital_height, orbital_angle, planet_idx):
        """Places the spacecraft in a circular orbit around the specified planet.

        Note
        ----
            This shortcut is meant for students who are having problems achieving a low, stable
            orbit around the destination planet after getting there. If your problem is just about
            getting close enough to the destination planet, but you believe you can stabilize
            the orbit once you get there, please consider using :meth:`place_spacecraft_in_unstable_orbit`
            instead.

        Parameters
        ----------
        time : float
            The time at which the spacecraft should be placed in orbit, in years from the initial system time.
        orbital_height : float
            The height of the orbit above the planet surface, in meters.
        orbital_angle : float
            The angle of the initial position of the spacecraft in orbit, in radians relative to the x-axis.
        planet_idx : int
            The index of the planet that the spacecraft should orbit.

        Raises
        ------
        RuntimeError
            When none of the provided codes are valid for unlocking this method.
        RuntimeError
            When called before :meth:`~ast2000tools.space_mission.SpaceMission.verify_manual_orientation` has been called successfully.
        """
        self._verify_code('stable_orbit')

        time = float(time)
        if time < 0:
            raise ValueError('Argument "time" is %g but must be positive.' % time)

        orbital_height = float(orbital_height)
        if orbital_height < 0:
            raise ValueError('Argument "orbital_height" is %g but must be positive.' % orbital_height)

        orbital_angle = float(orbital_angle)

        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        planet_radius = self.system.radii[planet_idx]*1e3
        spacecraft_distance = utils.m_to_AU(planet_radius + orbital_height)

        max_spacecraft_distance = self.system._compute_force_balance_distance(planet_idx, k=10)

        if spacecraft_distance >= max_spacecraft_distance:
            raise ValueError('Argument "orbital_height" is %g but must be smaller than %g meters.' % (utils.AU_to_m(spacecraft_distance) - planet_radius, utils.AU_to_m(max_spacecraft_distance) - planet_radius))

        spacecraft_orbital_speed = np.sqrt(const.G_sol*self.system.masses[planet_idx]/spacecraft_distance)

        radial_direction = np.array([np.cos(orbital_angle), np.sin(orbital_angle)])
        tangential_direction = np.array([-np.sin(orbital_angle), np.cos(orbital_angle)])

        planet_position = self.system._compute_single_planet_position(time, planet_idx)
        planet_velocity = self.system._compute_single_planet_velocity(time, planet_idx)

        spacecraft_position = planet_position + spacecraft_distance*radial_direction
        spacecraft_velocity = planet_velocity + spacecraft_orbital_speed*tangential_direction

        travel = self.mission.begin_interplanetary_travel()
        travel._move_to(time, spacecraft_position, spacecraft_velocity)
        travel.record_destination(planet_idx)

    def _verify_code(self, shortcut_name):
        valid_code = utils.get_seed(shortcut_name + 'this_string_adds_extra_entropy' + str(self.mission.seed))
        if valid_code not in self.codes:
            raise RuntimeError('None of the provided codes are valid for unlocking the requested shortcut.')
