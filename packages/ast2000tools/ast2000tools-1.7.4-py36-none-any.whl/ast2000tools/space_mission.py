# -*- coding: utf-8 -*-
"""Module containing classes for performing a space mission."""
from __future__ import division, print_function, absolute_import
from six.moves import range, zip, input

import sys
import os
import pickle
import numpy as np
from scipy import interpolate
from scipy import integrate
from PIL import Image

import ast2000tools.constants as const
import ast2000tools.utils as utils
from ast2000tools.solar_system import SolarSystem


class SpaceMission(object):
    """Represents a mission to launch a rocket from your home planet and land it safely on another planet.

    This class is used to keep track of your mission's progress and verify your results.

    Parameters
    ----------
    seed : int
        The seed to use when generating random solar system and mission properties.
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

        self._system = SolarSystem(seed, data_path=data_path, has_moons=has_moons, verbose=verbose)

        self._seed = self._system.seed
        self._verbose = bool(verbose)

        # Define hidden attributes
        self._position_after_launch = None
        self._velocity_after_launch = None
        self._fuel_needed_for_launch = None
        self._remaining_fuel_mass_after_launch = None
        self._angle_after_launch = None
        self._reference_star_radial_speeds = None
        self._ongoing_interplanetary_travel = None
        self._ongoing_landing_sequence = None

        # Initialize exposed attributes

        self._spacecraft_mass = 1100.0 # [kg]
        self._spacecraft_area = 16.0   # [m^2]

        self._lander_mass = 90.0 # [kg]
        self._lander_area = 0.3  # [m^2]

        self._launch_parameters_set = False
        self._rocket_launched = False
        self._launch_result_verified = False
        self._manual_orientation_verified = False
        self._destination_recorded = False
        self._landing_completed = False

        self._rocket_thrust = None
        self._rocket_mass_loss_rate = None
        self._initial_fuel_mass = None
        self._estimated_launch_duration = None
        self._launch_position = None
        self._time_of_launch = None

        self._time_after_launch = None

        self._destination_planet_idx = None
        self._initial_landing_time = None
        self._initial_landing_position = None
        self._initial_landing_velocity = None

        self._landing_site_polar_angle = None
        self._landing_site_azimuth_angle = None

        self._init_mean_molecular_masses()
        self._init_orientation_data()

    @property
    def seed(self):
        """int: The seed used to generate random solar system and mission properties."""
        return self._system.seed

    @property
    def data_path(self):
        """str: The path to the directory where output XML files will be stored."""
        return self._system.data_path

    @property
    def verbose(self):
        """bool: Whether non-essential status messages will be printed."""
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        self._verbose = bool(verbose)

    @property
    def system(self):
        """:class:`ast2000tools.solar_system.SolarSystem`: The randomized solar system where the space mission takes place."""
        return self._system

    @property
    def spacecraft_mass(self):
        """float: The mass of the spacecraft in kilograms."""
        return self._spacecraft_mass

    @property
    def spacecraft_area(self):
        """float: The cross-sectional area of the spacecraft in square meters."""
        return self._spacecraft_area

    @property
    def lander_mass(self):
        """float: The mass of the lander in kilograms."""
        return self._lander_mass

    @property
    def lander_area(self):
        """float: The cross-sectional area of the lander in square meters."""
        return self._lander_area

    @property
    def rocket_thrust(self):
        """float: The thrust of the rocket engine in Newtons.
        Only available after calling :meth:`~set_launch_parameters`."""
        return self._rocket_thrust

    @property
    def rocket_mass_loss_rate(self):
        """float: The mass loss rate of the rocket engine in kilograms per second.
        Only available after calling :meth:`~set_launch_parameters`."""
        return self._rocket_mass_loss_rate

    @property
    def initial_fuel_mass(self):
        """float: The initial mass of fuel contained in the rocket in kilograms.
        Only available after calling :meth:`~set_launch_parameters`."""
        return self._initial_fuel_mass

    @property
    def estimated_launch_duration(self):
        """float: The estimated duration of the launch (the time required to reach escape velocity) in seconds.
        Only available after calling :meth:`~set_launch_parameters`."""
        return self._estimated_launch_duration

    @property
    def launch_position(self):
        """1-D :class:`numpy.ndarray`: Array of shape (2,) containing the x and y-position of the launch site, in astronomical units relative to the star.
        Only available after calling :meth:`~set_launch_parameters`."""
        return self._launch_position

    @property
    def time_of_launch(self):
        """float: The time of the start of the launch in years.
        Only available after calling :meth:`~set_launch_parameters`."""
        return self._time_of_launch

    @property
    def time_after_launch(self):
        """float: The time of the end of the launch in years.
        Only available after calling :meth:`~launch_rocket`."""
        return self._time_after_launch

    @property
    def reference_wavelength(self):
        """float: The central wavelength of the spectral line (H-alpha) used to measure Doppler shifts, in nanometers."""
        return self._reference_wavelength

    @property
    def star_direction_angles(self):
        """tuple: Tuple (:math:`\\phi_0`, :math:`\\phi_1`) containing the azimuthal angles of the reference stars relative to the solar system x-axis, in degrees."""
        return self._star_direction_angles

    @property
    def star_doppler_shifts_at_sun(self):
        """tuple: Tuple (:math:`\\Delta\\lambda_0`, :math:`\\Delta\\lambda_1`) containing the Doppler shifts of the stars relative to your sun, in nanometers."""
        return self._star_doppler_shifts_at_sun

    @property
    def ongoing_interplanetary_travel(self):
        """:class:`~InterplanetaryTravel`: The object representing the ongoing interplanetary travel.
        Only available after calling :meth:`~begin_interplanetary_travel`."""
        return self._ongoing_interplanetary_travel

    @property
    def ongoing_landing_sequence(self):
        """:class:`~LandingSequence`: The object representing the ongoing landing sequence.
        Only available after calling :meth:`~begin_landing_sequence`."""
        return self._ongoing_landing_sequence

    @property
    def destination_planet_idx(self):
        """int: The index of the planet to land on after the interplanetary travel.
        Only available after calling :meth:`~InterplanetaryTravel.record_destination`."""
        return self._destination_planet_idx

    @property
    def initial_landing_time(self):
        """float: The initial time for the landing sequence, in years.
        Only available after calling :meth:`~InterplanetaryTravel.record_destination`."""
        return self._initial_landing_time

    @property
    def initial_landing_position(self):
        """1-D :class:`numpy.ndarray`: Array of shape (2,) containing the initial x and y-position for the landing sequence, in astronomical units relative to the star.
        Only available after calling :meth:`~InterplanetaryTravel.record_destination`."""
        return self._initial_landing_position

    @property
    def initial_landing_velocity(self):
        """1-D :class:`numpy.ndarray`: Array of shape (2,) containing the initial x and y-velocity for the landing sequence, in astronomical units per year relative to the star.
        Only available after calling :meth:`~InterplanetaryTravel.record_destination`."""
        return self._initial_landing_velocity

    @property
    def landing_site_polar_angle(self):
        """float: The polar angle of the landing site in degrees.
        Only available after completing a successful landing with :class:`~LandingSequence`."""
        return self._landing_site_polar_angle

    @property
    def landing_site_azimuth_angle(self):
        """float: The azimuthal angle of the landing site in degrees.
        Only available after completing a successful landing with :class:`~LandingSequence`."""
        return self._landing_site_azimuth_angle

    @property
    def launch_parameters_set(self):
        """bool: Whether the launch parameters have been specified."""
        return self._launch_parameters_set

    @property
    def rocket_launched(self):
        """bool: Whether the rocket has been successfully launched."""
        return self._rocket_launched

    @property
    def launch_result_verified(self):
        """bool: Whether the launch result has been successfully verified."""
        return self._launch_result_verified

    @property
    def manual_orientation_verified(self):
        """bool: Whether the manually inferred orientation data has been successfully verified."""
        return self._manual_orientation_verified

    @property
    def destination_recorded(self):
        """bool: Whether the destination state after the interplanetary travel has been recorded."""
        return self._destination_recorded

    @property
    def landing_completed(self):
        """bool: Whether the landing sequence has been successfully completed."""
        return self._landing_completed

    @staticmethod
    def save(filename, mission, verbose=True):
        """Saves the given instance of :class:`SpaceMission` as a binary file.

        Parameters
        ----------
        filename : str
            The name/path to use for the written binary file.
            Warning: If there exists a file with the same name it will be overwritten.
        mission : :class:`SpaceMission`
            The instance of :class:`SpaceMission` to save.
        verbose : bool, optional
            Set to False to mute the message saying that the file was successfully saved.
        """
        filename = str(filename)
        verbose = bool(verbose)

        if not isinstance(mission, SpaceMission):
            raise ValueError('Argument "mission" is an instance of %s but must be a SpaceMission instance.' % mission.__class__.__name__)

        with open(filename, 'wb') as f:
            pickle.dump(mission, f)

        if verbose:
            print('SpaceMission instance saved as %s.' % filename)

    @staticmethod
    def load(filename, verbose=True):
        """Loads an instance of :class:`SpaceMission` from the specified binary file.

        Parameters
        ----------
        filename : str
            The name/path of the binary file to read.
        verbose : bool, optional
            Set to False to mute the message saying that the file was successfully loaded.

        Returns
        -------
        :class:`SpaceMission`
            The loaded :class:`SpaceMission` instance.

        Raises
        ------
        ValueError
            When `filename` does not point to a valid file.
        """
        filename = str(filename)
        verbose = bool(verbose)

        if not os.path.isfile(filename):
            raise ValueError('Argument "filename" (%s) does not point to a valid file.' % filename)

        with open(filename, 'rb') as f:
            mission = pickle.load(f)

        if not isinstance(mission, SpaceMission):
            raise ValueError('The content of the file is an instance of %s but must be a SpaceMission instance.' % mission.__class__.__name__)

        if verbose:
            print('SpaceMission instance loaded from %s.' % filename)

        return mission

    def set_launch_parameters(self, thrust, mass_loss_rate, initial_fuel_mass, estimated_launch_duration, launch_position, time_of_launch):
        """Used to specify various parameters required to perform a launch.

        Note
        ----
            Any existing launch results will be cleared.

        Parameters
        ----------
        thrust : float
            The total thrust of the rocket engine in Newtons.
        mass_loss_rate : float
            The total rate of mass loss of the rocket engine in kilograms per second.
        initial_fuel_mass : float
            The total mass of rocket fuel contained in the rocket before launch, in kilograms.
        estimated_launch_duration : float
            The estimated duration of the launch, i.e. the time required to reach escape velocity, in seconds.
        launch_position : 1-D array_like
            Array of shape (2,) containing the x and y-position of the launch site, in astronomical units relative to the star.
            Must be close to the surface of your home planet (maximum 1% deviation).
        time_of_launch : float
            The time of the start of the launch in years.
        """
        thrust = float(thrust)
        if thrust < 0:
            raise ValueError('Argument "thrust" is %g but must be a positive value.' % thrust)

        mass_loss_rate = float(mass_loss_rate)
        if mass_loss_rate < 0:
            raise ValueError('Argument "mass_loss_rate" is %g but must be a positive value.' % mass_loss_rate)

        initial_fuel_mass = float(initial_fuel_mass)
        if initial_fuel_mass < 0:
            raise ValueError('Argument "initial_fuel_mass" is %g but must be a positive value.' % initial_fuel_mass)

        estimated_launch_duration = float(estimated_launch_duration)
        if estimated_launch_duration < 1e-2 or estimated_launch_duration > const.day:
            raise ValueError('Argument "estimated_launch_duration" is %g but must be between 0.01 s (max simulation time step) and %g s (24 hours).' % (estimated_launch_duration, const.day))
        if estimated_launch_duration > 3600:
            print('WARNING: Do you really need a launch lasting more than one hour?')

        launch_position = np.asarray(launch_position, dtype=float)
        if launch_position.shape != (2,):
            raise ValueError('Argument "launch_position" has shape %s but must have shape (2,).' % str(launch_position.shape))

        time_of_launch = float(time_of_launch)
        if time_of_launch < 0:
            raise ValueError('Argument "time_of_launch" is %g but must be a positive value.' % time_of_launch)

        planet_position_at_launch = self.system._compute_single_planet_position(time_of_launch, 0)   # [AU]
        launch_displacement_from_center = utils.AU_to_m(launch_position - planet_position_at_launch) # [m]
        launch_distance_from_center = np.linalg.norm(launch_displacement_from_center)                # [m]
        planet_radius = self.system.radii[0]*1e3                                                     # [m]
        deviation = launch_distance_from_center - planet_radius                                      # [m]
        max_deviation = planet_radius*1e-2                                                           # [m]

        if abs(deviation) > max_deviation:
            raise ValueError('Launch position deviation from home planet surface is %g m but must not exceed %g m.' % (abs(deviation), max_deviation))
        else:
            launch_displacement_from_center *= planet_radius/launch_distance_from_center
            if self.verbose:
                if deviation < 0:
                    print('Rocket was moved up by %g m to stand on planet surface.' % -deviation)
                elif deviation > 0:
                    print('Rocket was moved down by %g m to stand on planet surface.' % deviation)

        self._rocket_thrust = thrust
        self._rocket_mass_loss_rate = mass_loss_rate
        self._initial_fuel_mass = initial_fuel_mass
        self._estimated_launch_duration = estimated_launch_duration
        self._launch_position = planet_position_at_launch + utils.m_to_AU(launch_displacement_from_center)
        self._time_of_launch = time_of_launch

        # Make readonly to avoid modification by students
        self._launch_position.setflags(write=False)

        self._launch_parameters_set = True

        if self.verbose:
            print('New launch parameters set.')

        if self.rocket_launched:

            self._time_after_launch = None
            self._position_after_launch = None
            self._velocity_after_launch = None
            self._fuel_needed_for_launch = None
            self._remaining_fuel_mass_after_launch = None

            self._rocket_launched = False
            self._launch_result_verified = False

            if self.verbose:
                print('Note: Existing launch results were cleared.')

    def launch_rocket(self, time_step=1e-2):
        """Simulates a rocket launch based on the previously specified launch parameters.

        Note
        ----
            Any existing launch result verification will be cleared.

        Parameters
        ----------
        time_step : float, optional
            The time step duration to use for the simulation, in seconds.
            Not allowed to exceed the default of 0.01.
            Decrease if you suspect that higher accuracy is needed.

        Raises
        ------
        RuntimeError
            When called before :meth:`~set_launch_parameters`.
        RuntimeError
            When the rocket runs out of fuel.
        RuntimeError
            When the rocket is unable to overcome gravity.
        RuntimeError
            When the rocket reaches escape velocity too quickly.
        RuntimeError
            When the rocket hasn't reached escape velocity at the time the simulation is completed.
        """
        if self.launch_parameters_set == False:
            print('You need to specify the engine parameters before you can launch the rocket.')
            print('Please call set_launch_parameters before proceeding.')
            raise RuntimeError('Launch not ready.')

        time_step = float(time_step)
        if time_step < 0 or time_step > 1e-2:
            raise ValueError('Argument "time_step" is %g but must be a positive value not exceeding 0.01 s.' % time_step)

        n_time_steps = int(np.ceil(1.01*self.estimated_launch_duration/time_step)) # Number of time steps needed
        dt = self.estimated_launch_duration/n_time_steps # Recompute the time step duration so it fits with the number of time steps

        accelerating_upward = False
        reached_escape_velocity = False

        planet_position_AU = self.system._compute_single_planet_position(self.time_of_launch, 0)
        launch_position_relative_to_planet = utils.AU_to_m(self._launch_position - planet_position_AU)

        planet_radius = self.system.radii[0]*1e3 # [m]
        planet_angular_velocity = 2.0*const.pi/utils.day_to_s(self.system.rotational_periods[0]) # [rad/sec]
        surface_speed = planet_angular_velocity*planet_radius # [m/s]

        current_mass = self.spacecraft_mass + self.initial_fuel_mass # Total mass
        current_dist_from_center = np.linalg.norm(launch_position_relative_to_planet)
        current_speed = 0.0 # At launch the rocket is not moving in the radial direction

        for i in range(n_time_steps):
            gravitational_acceleration = -const.G*self.system.masses[0]*const.m_sun/current_dist_from_center**2
            total_acceleration = self.rocket_thrust/current_mass + gravitational_acceleration

            if total_acceleration > 0:
                current_speed += total_acceleration*dt
                current_dist_from_center += current_speed*dt

                accelerating_upward = True

            current_mass -= self.rocket_mass_loss_rate*dt

            if current_mass < self.spacecraft_mass:
                print('You ran out of fuel. Try a larger amount.')
                raise RuntimeError('Ran out of fuel while launching.')

            if accelerating_upward == True:

                squared_speed_relative_to_center = current_speed**2 + surface_speed**2
                kin_energy = 0.5*current_mass*squared_speed_relative_to_center
                pot_energy = const.G*self.system.masses[0]*const.m_sun*current_mass/np.linalg.norm(current_dist_from_center)

                if kin_energy >= pot_energy:
                    # If the kinetic energy of the rocket with respect to the home planet is larger then
                    # the potential energy from the home planet then the launch sequence is done
                    fuel_mass_used = self.spacecraft_mass + self.initial_fuel_mass - current_mass
                    reached_escape_velocity = True
                    time_to_reach_escape_velocity = dt*(i+1) # Store time spent to reach escape
                    break

        if accelerating_upward == False:
            print('You have a too weak rocket engine. The thrust is too low to overcome gravity.')
            raise RuntimeError('Not enough lift.')

        if reached_escape_velocity == True:
            if time_to_reach_escape_velocity < 5*60:
                print('Reached escape velocity in only %g s. Realistically it should take at least %g s (5 minutes).' % (time_to_reach_escape_velocity, 5*60))
                raise RuntimeError('Too strong acceleration.')

            if self.verbose:
                print('Launch completed, reached escape velocity in %g s.' % time_to_reach_escape_velocity)
        else:
            print('Escape velocity not reached after %g s. Try with a longer estimated launch duration.' % self.estimated_launch_duration)
            raise RuntimeError('Escape velocity not reached.')

        planet_position = utils.AU_to_m(planet_position_AU)                                                          # Position of planet at launch [m]
        planet_velocity = utils.AU_pr_yr_to_m_pr_s(self.system._compute_single_planet_velocity(self.time_of_launch, 0)) # Velocity of planet at launch [m/s]

        launch_direction = launch_position_relative_to_planet/planet_radius # Unit vector in launch direction

        final_displacement_from_center = current_dist_from_center*launch_direction # [m]

        final_radial_velocity = current_speed*launch_direction # [m/s]

        surface_tangent_vector = np.array([-launch_direction[1], launch_direction[0]])
        surface_velocity = surface_speed*surface_tangent_vector # [m/s]

        correct_final_velocity = utils.m_pr_s_to_AU_pr_yr(planet_velocity + surface_velocity + final_radial_velocity) # [AU/yr]
        correct_final_position = utils.m_to_AU(planet_position + (planet_velocity + surface_velocity)*time_to_reach_escape_velocity + final_displacement_from_center) # [AU]

        self._time_after_launch = self.time_of_launch + utils.s_to_yr(time_to_reach_escape_velocity)
        self._position_after_launch = correct_final_position
        self._velocity_after_launch = correct_final_velocity
        self._fuel_needed_for_launch = fuel_mass_used
        self._remaining_fuel_mass_after_launch = self.initial_fuel_mass - fuel_mass_used

        # Make sure the results are not altered by mistake
        self._position_after_launch.setflags(write=False)
        self._velocity_after_launch.setflags(write=False)

        self._rocket_launched = True

        if self._launch_result_verified:

            self._launch_result_verified = False

            if self.verbose:
                print('Note: Existing launch result verification was cleared.')

    def verify_launch_result(self, position_after_launch):
        """Verifies that your computation of the final spacecraft position after launch gives a resonable result.

        Parameters
        ----------
        position_after_launch : 1-D array_like
            Array of shape (2,) containing your values for the x and y-position of the spacecraft after launch, in astronomical units relative to the star.

        Raises
        ------
        RuntimeError
            When called before :meth:`~launch_rocket`.
        RuntimeError
            When the input position is too far from the correct position.
        """
        if self.rocket_launched == False:
            print('You need to perform the rocket launch before you can verify the results.')
            print('Please call launch_rocket before proceeding.')
            raise RuntimeError('Launch result verification not ready.')

        position_after_launch = np.asarray(position_after_launch, dtype=float)
        if position_after_launch.shape != (2,):
            raise ValueError('Argument "position_after_launch" has shape %s but must have shape (2,).' % str(position_after_launch.shape))

        displacement = position_after_launch - self._position_after_launch # [AU]
        deviation = np.linalg.norm(displacement)
        max_deviation = 1.5e-2*utils.km_to_AU(self.system.radii[0]) # Use planet radius as distance scale

        # If the distance between the students calculated position and
        # the actual position deviates by more than 1.5% of the actual
        # spacecraft-planet distance the test fails
        if deviation > max_deviation:
            print('Your spacecraft position deviates too much from the correct position.')
            print('The deviation is approximately %g AU.' % deviation)
            print('Make sure you have included the rotation and orbital velocity of your home planet.')
            print('Note that units are AU and relative the the reference system of the star.')
            raise RuntimeError('Incorrect spacecraft position after launch.')
        else:
            self._launch_result_verified = True
            if self.verbose:
                print('Your spacecraft position was satisfyingly calculated. Well done!')
                print('*** Achievement unlocked: No free launch! ***')

    def verify_planet_positions(self, simulation_duration, planet_positions, filename='planet_trajectories.npz'):
        """Calls :meth:`~ast2000tools.solar_system.SolarSystem.verify_planet_positions` for the :class:`ast2000tools.solar_system.SolarSystem` instance associated with the mission.

        Note
        ----
        The exact trajectories will be needed in later stages of the mission.
        By default, this wrapper causes the trajectories to be stored in the file "planet_trajectories.npz" in the working directory.
        The syntax for loading the data is::

            with np.load('planet_trajectories.npz') as f:
                times = f['times']
                exact_planet_positions = f['planet_positions']
        """
        self.system.verify_planet_positions(simulation_duration, planet_positions, filename=filename)

    def generate_orbit_video(self, times, planet_positions, number_of_frames=None, reduce_other_periods=True, filename='orbit_video.xml'):
        """Calls :meth:`~ast2000tools.solar_system.SolarSystem.generate_orbit_video` for the :class:`ast2000tools.solar_system.SolarSystem` instance associated with the mission.
        """
        self.system.generate_orbit_video(times, planet_positions, number_of_frames=number_of_frames, reduce_other_periods=reduce_other_periods, filename=filename)

    @staticmethod
    def get_sky_image_pixel(polar_angle, azimuth_angle):
        """Finds the index of the pixel in the full-sky image correspnding to the given spherical coordinates.

        Parameters
        ----------
        polar_angle : float
            The polar angle of the point in radians.
            Must be in the range [0, pi].
        azimuth_angle : float
            The azimuthal angle of the point in radians.

        Returns
        -------
        int
            The index of the pixel.
        """
        polar_angle = float(polar_angle)
        if polar_angle < 0 or polar_angle > const.pi:
            raise ValueError('Argument "polar_angle" is %g but must be in the range [0, pi] rad.' % polar_angle)

        azimuth_angle = float(azimuth_angle)

        nside = 512

        z = np.cos(polar_angle)
        za = np.abs(z)
        tt = (azimuth_angle%(2.0*const.pi)) / (const.pi/2.0)  #in [0,4)
        ipix = 0
        if ( za <= 2.0/3.0 ): #Equatorial region
            temp1 = nside*(.5+tt)
            temp2 = nside*.75*z
            jp = int(np.floor(temp1-temp2)) # index of  ascending edge line
            jm = int(np.floor(temp1+temp2)) # index of descending edge line
            ir = nside + 1 + jp - jm # in {1,2n+1} (ring number counted from z=2/3)
            kshift = 1 - ir%2 # kshift=1 if ir even, 0 otherwise
            nl4 = 4*nside
            ip = int(np.floor( ( jp+jm - nside + kshift + 1 ) // 2 )) # in {0,4n-1} #Rob, I hope this is integer div
            if (ip >= nl4):
                ip = ip - nl4
            ipix = 2*nside*(nside-1) + nl4*(ir-1) + ip
        else: # North & South polar caps
            tp = tt - int(np.floor(tt))      #MODULO(tt,1.0_dp)
            tmp = nside * np.sqrt( 3.0*(1.0 - za) )
            jp = int(np.floor(tp          * tmp )) # increasing edge line index
            jm = int(np.floor((1.0 - tp) * tmp )) # decreasing edge line index
            ir = jp + jm + 1        # ring number counted from the closest pole
            ip = int(np.floor( tt * ir ))     # in {0,4*ir-1}
            if (ip >= 4*ir):
                ip = ip - 4*ir

            if (z>0.0):
                ipix = 2*ir*(ir-1) + ip
            else:
                ipix = 12*nside**2 - 2*ir*(ir+1) + ip
        return ipix

    def take_picture(self, filename='sky_picture.png', full_sky_image_path='himmelkule.npy'):
        """Generates a picture of the sky in the direction that the spacecraft is pointing directly after launch.

        Note
        ----
            You can safely assume that the spacecraft is looking along the solar system plane.

        Parameters
        ----------
        filename : str, optional
            The name/path to use for the generated image.
            By default the image is stored as "sky_picture.png" in the working directory.
        full_sky_image_path : str, optional
            The name/path to use when looking for the sky data file.
            This file must be downloaded from the course website.
            By default the file is assumed to be named "himmelkule.npy" and reside in the working directory.

        Raises
        ------
        RuntimeError
            When called before :meth:`~verify_launch_result`.
        ValueError
            When `full_sky_image_path` does not point to a valid file.
        """
        if self.launch_result_verified == False:
            print('You need to verify the launch results before you can take a picture.')
            print('Please call verify_launch_result with the correct final position before proceeding.')
            raise RuntimeError('Picture taking not ready.')

        filename = str(filename)

        full_sky_image_path = str(full_sky_image_path)
        if not os.path.isfile(full_sky_image_path):
            raise ValueError('Argument "full_sky_image_path" (%s) does not point to a valid file.' % full_sky_image_path)

        SpaceMission._generate_picture(self._angle_after_launch, filename, full_sky_image_path)

        if self.verbose:
            print('Picture written to %s.' % filename)

    def measure_star_doppler_shifts(self):
        """Returns the Doppler shifts of the two reference stars as measured by your spacecraft directly after launch.

        Note
        ----
            The Doppler shifts are computed for the H-alpha spectral line, which has a central wavelength of 656.3 nm.

        Returns
        -------
        tuple(float)
            Tuple (:math:`\\Delta\\lambda_0`, :math:`\\Delta\\lambda_1`) containing the Doppler shifts of the stars relative to your spacecraft, in nanometers.

        Raises
        ------
        RuntimeError
            When called before :meth:`~verify_launch_result`.
        """
        if self.launch_result_verified == False:
            print('You need to verify the launch results before you can measure star Doppler shifts.')
            print('Please call verify_launch_result with the correct final position before proceeding.')
            raise RuntimeError('Doppler shift measurements not ready.')
        
        # Rotation matrix from orthogonal cartesian (x, y) coordinates
        # to non-orthogonal basis defined by reference star directions
        rotation_matrix = np.array([
            [np.sin(utils.deg_to_rad(self.star_direction_angles[1])), -np.cos(utils.deg_to_rad(self.star_direction_angles[1]))],
            [-np.sin(utils.deg_to_rad(self.star_direction_angles[0])), np.cos(utils.deg_to_rad(self.star_direction_angles[0]))],
        ]) / np.sin(utils.deg_to_rad(self.star_direction_angles[1] - self.star_direction_angles[0]))

        # Performing rotation as matrix product
        v_rotated = -np.matmul(rotation_matrix, self._velocity_after_launch) + self._reference_star_radial_speeds
        v_rotated = utils.AU_pr_yr_to_m_pr_s(v_rotated)
        dl1 = utils._convert_relative_speed_to_doppler_shift(self.reference_wavelength, v_rotated[0])
        dl2 = utils._convert_relative_speed_to_doppler_shift(self.reference_wavelength, v_rotated[1])

        return dl1, dl2

    def measure_distances(self):
        """Returns the distances to the bodies of the solar system as measured by your spacecraft directly after launch.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (`number_of_planets+1`,) containing the distances to the planets and sun (last entry) in your system, in astronomical units.

        Raises
        ------
        RuntimeError
            When called before :meth:`~verify_launch_result`.
        """
        if self.launch_result_verified == False:
            print('You need to verify the launch results before you can measure distances.')
            print('Please call verify_launch_result with the correct final position before proceeding.')
            raise RuntimeError('Distance measurements not ready.')

        planet_positions = self.system._compute_planet_positions(self.time_after_launch)

        distances = np.zeros(self.system.number_of_planets + 1)

        distances[:-1] = np.linalg.norm(planet_positions - self._position_after_launch[:, np.newaxis], axis=0)
        distances[-1] = np.linalg.norm(self._position_after_launch)

        return distances

    def verify_manual_orientation(self, position_after_launch, velocity_after_launch, angle_after_launch):
        """Verifies that your manually inferred values of the position, velocity and pointing angle of the spacecraft directly after launch are reasonable.

        Parameters
        ----------
        position_after_launch : 1-D array_like
            Array of shape (2,) containing your inferred values for the x and y-position of the spacecraft, in astronomical units relative to the star.
        velocity_after_launch : 1-D array_like
            Array of shape (2,) containing your inferred values for the x and y-velocity of the spacecraft, in astronomical units per year relative to the star.
        angle_after_launch : float
            Your inferred value for the azimuthal angle of the spacecraft's pointing, in degrees.

        Raises
        ------
        RuntimeError
            When called before :meth:`~verify_launch_result`.
        RuntimeError
            When any of the inputted values are too far from the correct values.
        """
        if self.launch_result_verified == False:
            print('You need to verify the launch results before you can verify your manual orientation.')
            print('Please call verify_launch_result with the correct final position before proceeding.')
            raise RuntimeError('Manual orientation verification not ready.')

        position_after_launch = np.asarray(position_after_launch, dtype=float)
        if position_after_launch.shape != (2,):
            raise ValueError('Argument "position_after_launch" has shape %s but must have shape (2,).' % str(position_after_launch.shape))

        velocity_after_launch = np.asarray(velocity_after_launch, dtype=float)
        if velocity_after_launch.shape != (2,):
            raise ValueError('Argument "velocity_after_launch" has shape %s but must have shape (2,).' % str(velocity_after_launch.shape))

        angle_after_launch = float(angle_after_launch)

        success = True

        angle_deviation = abs(angle_after_launch - self._angle_after_launch) % 360

        if angle_deviation > 180:
            angle_deviation = 360 - angle_deviation

        if abs(angle_deviation) < 2.0:
            if self.verbose:
                print('Pointing angle after launch correctly calculated. Well done!')
        else:
            print('Pointing angle incorrect.')
            print('Continuing other tests...')
            success = False

        velocity_deviation = np.linalg.norm(velocity_after_launch - self._velocity_after_launch)/np.linalg.norm(self._velocity_after_launch)

        if velocity_deviation < 0.01:
            if self.verbose:
                print('Velocity after launch correctly calculated. Well done!')
        else:
            print('Velocity incorrect.')
            print('Continuing other tests...')
            success = False

        position_deviation = np.linalg.norm(position_after_launch - self._position_after_launch)

        if position_deviation < 0.01:
            if self.verbose:
                print('Position after launch correctly calculated. Well done!')
        else:
            print('Position incorrect.')
            success = False

        if success:
            self._manual_orientation_verified = True
            if self.verbose:
                print('Your manually inferred orientation was satisfyingly calculated. Well done!')
                print('*** Achievement unlocked: Well-oriented! ***')
        else:
            raise RuntimeError('Manual orientation verification failed.')

    def begin_interplanetary_travel(self):
        """Initiates an interplanetary travel process allowing you to guide your spacecraft to a different planet.

        Note
        ----
            Any ongoing interplanetary travel or landing sequence will be terminated.
            Any recorded destination state will be cleared.

        Returns
        -------
        :class:`InterplanetaryTravel`
            A new instance of :class:`InterplanetaryTravel` associated with your system.
        """
        self._ongoing_interplanetary_travel = InterplanetaryTravel(self, verbose=self.verbose)
        return self.ongoing_interplanetary_travel

    def begin_landing_sequence(self, assume_uniform_gravity_atmosphere=True):
        """Initiates a landing sequence process allowing you to land on a planet.

        Note
        ----
            Any ongoing interplanetary travel or landing sequence will be terminated.
            Any recorded landing site coordinates will be cleared.

        Parameters
        ----------
        assume_uniform_gravity_atmosphere : bool, optional
            Whether to neglect the change of gravitational force with height when modelling the atmosphere.
            Default is True.

        Returns
        -------
        :class:`~LandingSequence`
            A new instance of :class:`~LandingSequence` associated with your system.
        """
        self._ongoing_landing_sequence = LandingSequence(self, assume_uniform_gravity_atmosphere=assume_uniform_gravity_atmosphere, verbose=self.verbose)
        return self.ongoing_landing_sequence

    def _init_mean_molecular_masses(self):

        # Choose one of Frode's mu values and use it for all the planets
        muList = [31.333333, 27.600000, 27.600000, 31.000000, 30.800000, 22.000000, 23.500000, 27.500000, 30.333333, 30.800000, 30.333333, 26.500000, 26.500000, 30.333333, 22.000000, 30.333333, 23.500000, 27.600000, 23.500000, 25.333333, 27.500000, 31.333333, 30.333333, 27.600000, 27.600000, 30.500000, 25.000000, 27.600000, 31.333333, 23.500000, 27.600000, 34.666667, 30.333333, 23.500000, 30.333333, 30.333333, 27.600000, 22.000000, 30.333333, 30.333333, 27.600000, 34.500000, 30.000000, 30.333333, 30.500000, 30.333333, 30.000000, 27.600000, 26.000000, 30.333333, 27.600000, 27.600000, 30.333333, 30.333333, 27.600000, 27.600000, 27.600000, 27.600000, 30.333333, 40.000000, 30.500000, 27.600000, 31.000000, 31.333333, 30.800000, 27.600000, 30.666667, 26.000000, 30.333333, 27.600000, 30.333333, 30.333333, 27.500000, 30.000000, 27.500000, 27.500000, 30.333333, 30.500000, 34.500000, 30.333333, 30.333333, 30.800000, 27.600000, 30.800000, 31.333333, 30.333333, 25.000000, 31.333333, 27.600000, 27.600000, 27.500000, 30.333333, 30.333333, 30.333333, 30.333333, 27.500000, 30.333333, 30.333333, 27.600000, 30.50000]

        self._system._mean_molecular_masses.setflags(write=True)

        if (self.seed < 100):
            self._system._mean_molecular_masses[:] = muList[self.seed]
        else:
            idx = int(str(self.seed)[-2:])
            self._system._mean_molecular_masses[:] = muList[idx]

        self._system._mean_molecular_masses.setflags(write=False)

    def _init_orientation_data(self):

        self._angle_after_launch = self.system._random_state.randint(0, 360) # [deg]

        phi_1 = self.system._random_state.uniform(0, 360)
        phi_2 = (phi_1 + self.system._random_state.uniform(40, 140)) % 360
        self._star_direction_angles = (phi_2, phi_1)  # [deg]

        self._reference_wavelength = 656.3  # Rest wavelength of spectral line [nm]
        self._reference_star_radial_speeds = [self.system._random_state.uniform(-2, 2), self.system._random_state.uniform(-2, 2)]  # [AU/yr]
        self._star_doppler_shifts_at_sun = (utils._convert_relative_speed_to_doppler_shift(self.reference_wavelength, utils.AU_pr_yr_to_m_pr_s(self._reference_star_radial_speeds[0])),
                                            utils._convert_relative_speed_to_doppler_shift(self.reference_wavelength, utils.AU_pr_yr_to_m_pr_s(self._reference_star_radial_speeds[1])))

    def _get_launch_results(self):
        return self._fuel_needed_for_launch, self.time_after_launch, self._position_after_launch, self._velocity_after_launch

    def _get_orientation_data(self):
        return self._position_after_launch, self._velocity_after_launch, self._angle_after_launch

    def _compute_fuel_mass_needed_for_boost(self, remaining_fuel_mass, delta_v):
        """Calculates the amount of fuel needed for a boost.

        Parameters
        ----------
        remaining_fuel_mass : float
            The mass of fuel contained in the spacecraft prior to the boost, in kilograms.
        delta_v : 1-D array_like
            Array of shape (2,) or (3,) containing the x and y-component of the change in velocity, in astronomical units per year.

        Returns
        -------
        float
            The mass of the fuel needed to perform the boost, in kilograms.

        Raises
        ------
        RuntimeError
            When called before :meth:`~set_launch_parameters`.
        """
        if not self.launch_parameters_set:
            print('You need to specify the engine parameters before you can compute the fuel usage of a boost.')
            print('Please call set_launch_parameters before proceeding.')
            raise RuntimeError('Boost fuel usage computation not ready.')

        delta_v_magnitude = utils.AU_pr_yr_to_m_pr_s(np.linalg.norm(delta_v)) # [m/s]

        total_mass = self.spacecraft_mass + remaining_fuel_mass
        fuel_mass_needed = total_mass*(1 - np.exp(-(self.rocket_mass_loss_rate/self.rocket_thrust)*delta_v_magnitude))

        return fuel_mass_needed

    @staticmethod
    def _generate_picture(azimuth_angle, filename, full_sky_image_path):
        """Uses stereographic projection to create an image of the sky in the specified direction within the solar system plane.

        Parameters
        ----------
        azimuth_angle : float
            The azimuthal angle of the direction to point the camera, in degrees.
        filename : str
            The name/path to use for storing the image.
        full_sky_image_path : str
            The name/path to use when looking for the full-sky image file.
        """
        FOV = utils.deg_to_rad(70)
        xresolution = 640
        yresolution = 480

        outpic = np.zeros([yresolution, xresolution, 3], dtype=np.uint8)

        full_sky_image = np.load(full_sky_image_path)

        xymaxmin = 2*np.sin(FOV/2.)/(1. + np.cos(FOV/2.))
        xarray = np.linspace(-xymaxmin, xymaxmin, xresolution)
        yarray = np.linspace(xymaxmin, -xymaxmin, yresolution) # y from bottom and up

        for i in range(xresolution):
            x = xarray[i]
            for j in range(yresolution):
                y = yarray[j]
                rho = np.sqrt(x**2 + y**2)
                c = 2*np.arctan(rho/2.)
                theta = const.pi/2. - np.arcsin(y*np.sin(c)/rho)
                phi0 = utils.deg_to_rad(azimuth_angle)
                phi = phi0 + np.arctan(x*np.sin(c)/(rho*np.cos(c)))
                pixnum = SpaceMission.get_sky_image_pixel(theta, phi)
                pix = full_sky_image[pixnum]
                rgb = [pix[2], pix[3], pix[4]]
                outpic[j, i] = rgb

        img = Image.fromarray(outpic)
        img.save(filename)


class _Atmosphere(object):
    """Represents the atmosphere of a planet.

    Parameters
    ----------
    planet_mass : float
        The mass of the planet in kilograms.
    planet_mass : float
        The radius of the planet in meters.
    surface_density : float
        The density of the atmosphere at the surface of the planet, in kilograms per cubic meter.
    surface_temp : float
        The temperature of the atmosphere at the surface of the planet, in kelvin.
    mean_molecular_mass : float
        The mean molecular mass of the atmosphere, in kilograms.
    isothermal_temp_frac : float, optional
        The fraction of the surface temperature for which the overlying atmosphere should be considered isothermal.
        By default the atmosphere is considered isothermal above where the temperature drops below half the surface temperature.
    adiabatic_index : float, optional
        The adiabatic index to use.
        Default is 7/5, corresponding to a diatomic gas.
    """
    def __init__(self, planet_mass, planet_radius, surface_density, surface_temp, mean_molecular_mass,
                 isothermal_temp_frac=0.5, adiabatic_index=1.4):

        self._gamma = adiabatic_index
        self._mu = mean_molecular_mass # [kg]

        self._M = planet_mass # [kg]
        self._R = planet_radius # [m]
        self._rho0 = surface_density # [kg/m3]
        self._T0 = surface_temp # [K]
        self._P0 = self._ideal_gas_pressure(surface_density, surface_temp) # [Pa]
        self._T_iso = isothermal_temp_frac*surface_temp # [K]
        self._h_iso = self._isothermal_height() # [m]
        self._P_iso = self._adiabatic_pressure(self._h_iso) # [Pa]

    def _ideal_gas_pressure(self, rho, T):
        return rho*const.k_B*T/self._mu

    def _ideal_gas_density(self, P, T):
        return self._mu*P/(const.k_B*T)

    def _isothermal_height(self):
        tmp = const.k_B*(self._T0 - self._T_iso)*self._gamma/(self._mu*const.G*self._M*(self._gamma - 1))
        return tmp*self._R**2/(1 - tmp*self._R)

    def _isothermal_pressure(self, h):
        return self._P_iso*np.exp(-self._mu*const.G*self._M*((h - self._h_iso)/((self._R + self._h_iso)*(self._R + h)))/(const.k_B*self._T_iso))

    def _adiabatic_pressure(self, h):
        return self._P0*(1 - self._mu*const.G*self._M*(self._gamma - 1)*(h/(self._R*(self._R + h)))/(const.k_B*self._T0*self._gamma))**(self._gamma/(self._gamma - 1))

    def _adiabatic_temperature(self, h):
        return self._T0*(self._adiabatic_pressure(h)/self._P0)**((self._gamma - 1)/self._gamma)

    def _pressure(self, h):
        return self._adiabatic_pressure(h) if h < self._h_iso else self._isothermal_pressure(h)

    def _pressures(self, h):
        P = np.zeros(h.shape)
        P[h < self._h_iso] = self._adiabatic_pressure(h[h < self._h_iso])
        P[h >= self._h_iso] = self._isothermal_pressure(h[h >= self._h_iso])
        return P

    def _temperature(self, h):
        return self._adiabatic_temperature(h) if h < self._h_iso else self._T_iso

    def _temperatures(self, h):
        T = np.zeros(h.shape)
        T[h < self._h_iso] = self._adiabatic_temperature(h[h < self._h_iso])
        T[h >= self._h_iso] = self._T_iso
        return T

    def _density(self, h):
        return self._ideal_gas_density(self._pressure(h), self._temperature(h))

    def _densities(self, h):
        return self._ideal_gas_density(self._pressures(h), self._temperatures(h))


class _UniformGravityAtmosphere(_Atmosphere):
    """Represents the atmosphere of a planet.

    Neglects the change of gravitational force with height in the atmosphere.

    Parameters
    ----------
    *args
        Arguments to the parent constructor.
    **kwargs
        Keyword arguments to the parent constructor.
    """
    def __init__(self, *args, **kwargs):
        super(_UniformGravityAtmosphere, self).__init__(*args, **kwargs)

    def _isothermal_height(self):
        return const.k_B*self._R**2*self._gamma*(self._T0 - self._T_iso)/(self._mu*const.G*self._M*(self._gamma - 1))

    def _isothermal_pressure(self, h):
        return self._P_iso*np.exp(-self._mu*const.G*self._M*(h - self._h_iso)/(const.k_B*self._T_iso*self._R**2))

    def _adiabatic_pressure(self, h):
        return self._P0*(1 - self._mu*const.G*self._M*(self._gamma - 1)*h/(const.k_B*self._T0*self._R**2*self._gamma))**(self._gamma/(self._gamma - 1))


class _Camera(object):
    """Represents a camera on the spacecraft.

    Note
    ----
        For this class, the reference direction is fixed at [0, 0, 1].
        Subclasses can implement other methods for providing the reference direction.

    Parameters
    ----------
    system : :class:`ast2000tools.solar_system.SolarSystem`
        The system the spacecraft resides in.
    n_dims : int
        The number of dimensions to consider the camera orientation in.
        Must be 2 or 3.
    relative_polar_angle : float, optional
        The polar angle to offset the camera with relative to the reference direction, in radians.
        Default is pi/2.
    relative_azimuth_angle : float, optional
        The azimuthal angle to offset the camera with relative to the reference direction, in radians.
        Default is 0.
    up_x : float, optional
        The x-component of the camera up-vector.
        Default is 0.
    up_y : float, optional
        The y-component of the camera up-vector.
        Default is 0.
    up_z : float, optional
        The z-component of the camera up-vector.
        Default is 1.
    """
    def __init__(self, system, n_dims, relative_polar_angle=const.pi/2, relative_azimuth_angle=0, up_x=0, up_y=0, up_z=1):
        self._system = system
        self._set_n_dims(n_dims)
        self._set_relative_angles(relative_polar_angle, relative_azimuth_angle)
        self._set_up_vector(up_x, up_y, up_z)

    def _set_n_dims(self, n_dims):
        self._n_dims = int(n_dims)
        assert self._n_dims == 2 or self._n_dims == 3, \
            'The number of dimensions is %d but must be 2 or 3' % self._n_dims

    def _set_relative_angles(self, relative_polar_angle, relative_azimuth_angle):
        self._relative_polar_angle = float(relative_polar_angle)
        self._relative_azimuth_angle = float(relative_azimuth_angle)

    def _set_up_vector(self, up_x, up_y, up_z):
        self._up_vector = np.array([float(up_x), float(up_y), float(up_z)])
        self._up_vector /= np.linalg.norm(self._up_vector)

    def _get_up_vector(self):
        return self._up_vector[0], self._up_vector[1], self._up_vector[2]

    def _compute_reference_directions(self, times, spacecraft_positions, spacecraft_velocities):
        return np.repeat(np.array([0, 0, 1], dtype='float')[:, np.newaxis], len(times), axis=1)

    def _compute_orientations(self, *args):
        reference_directions = self._compute_reference_directions(*args)
        reference_polar_angles = np.arccos(reference_directions[2, :])
        reference_azimuth_angles = np.arctan2(reference_directions[1, :], reference_directions[0, :])
        polar_angles = reference_polar_angles + self._relative_polar_angle
        azimuth_angles = reference_azimuth_angles + self._relative_azimuth_angle
        return polar_angles, azimuth_angles

    def _compute_orientation(self, time, spacecraft_position, spacecraft_velocity):
        times = np.array([time])
        spacecraft_positions = spacecraft_position[:, np.newaxis]
        spacecraft_velocities = spacecraft_velocity[:, np.newaxis]
        polar_angles, azimuth_angles = self._compute_orientations(times, spacecraft_positions, spacecraft_velocities)
        return polar_angles[0], azimuth_angles[0]


class _PlanetRelativeCamera(_Camera):
    """Represents a camera on the spacecraft tracking a planet.

    Parameters
    ----------
    planet_idx : int
        The index of the planet defining the reference direction.
    *args
        Arguments to the parent constructor.
    **kwargs
        Keyword arguments to the parent constructor.
    """
    def __init__(self, planet_idx, *args, **kwargs):
        super(_PlanetRelativeCamera, self).__init__(*args, **kwargs)
        self._set_planet_idx(planet_idx)

    def _set_planet_idx(self, planet_idx):
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self._system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self._system.number_of_planets - 1))
        self._planet_idx = planet_idx

    def _compute_reference_directions(self, times, spacecraft_positions, spacecraft_velocities):

        reference_planet_positions = np.pad(self._system._compute_single_planet_trajectory(times, self._planet_idx), ((0, 1), (0, 0)), 'constant')

        displacements_to_planet = reference_planet_positions - np.pad(spacecraft_positions, ((0, 3 - self._n_dims), (0, 0)), 'constant')

        return displacements_to_planet/np.linalg.norm(displacements_to_planet, axis=0)


class _MotionRelativeCamera(_Camera):
    """Represents a camera on the spacecraft following the direction of motion.

    Parameters
    ----------
    *args
        Arguments to the parent constructor.
    **kwargs
        Keyword arguments to the parent constructor.
    """
    def __init__(self, *args, **kwargs):
        super(_MotionRelativeCamera, self).__init__(*args, **kwargs)

    def _compute_reference_directions(self, times, spacecraft_positions, spacecraft_velocities):
        velocities = np.pad(spacecraft_velocities, ((0, 3 - self._n_dims), (0, 0)), 'constant')
        return velocities/np.linalg.norm(velocities, axis=0)


class _SpacecraftJourneyEvents(object):
    """Represents a set of events happening during a spacecraft journey.

    Note
    ----
        Events have a name and a time, and optionally hold a tag and/or an arbitrary piece of data.
    """
    def __init__(self):
        self._events = {}

    def _add(self, name, time, tag=None, data=None, never_outdated=False):
        self._events[name] = [float(time), data, tag, never_outdated]

    def _add_if_absent(self, name, time, tag=None, data=None, never_outdated=False):
        if not self._has(name):
            self._add(name, time, tag=tag, data=data, never_outdated=never_outdated)

    def _add_if_tag_absent(self, other_tag, name, time, data=None, tag=None, never_outdated=False):
        if not self._has_tag(other_tag):
            self._add(name, time, tag=tag, data=data, never_outdated=never_outdated)

    def _update_data(self, name, data):
        assert name in self._events, \
            'Trying to update data of non-existing event %s.' % name
        self._events[name][1] = data

    def _remove_all_outdated(self, latest_time):
        # If the solver has not moved forward in time after recording an event,
        # the record of the event is no longer valid and must be cleared.
        self._events = {name: event for name, event in self._events.items() if (event[3] or latest_time > event[0])}

    def _remove(self, name):
        self._events.pop(name, None)

    def _clear(self):
        self._events = {}

    def _has(self, name):
        return name in self._events

    def _has_tag(self, tag):
        return sum([event[2] == tag for event in self._events.values()]) > 0

    def _get_history(self, start_time):
        return sorted([(name, event) for name, event in self._events.items() if event[0] >= start_time],
                      key=lambda item: item[1][0])

    def __str__(self):
        return str(self._events)


class _SpacecraftJourney(object):
    """Represents a spacecraft journey inside your solar system.

    Note
    ----
        This is the common base class for the :class:`InterplanetaryTravel` and :class:`~LandingSequence` classes,
        and is not usable on its own.

    Parameters
    ----------
    mission : :class:`SpaceMission`
        The mission that the spacecraft journey is associated with.
    verbose : bool, optional
            Whether to print non-critical messages during the journey.
            Default is True.
    """
    def __init__(self, mission, verbose=True):

        if not isinstance(mission, SpaceMission):
            raise ValueError('Argument "mission" is an instance of %s but must be a SpaceMission instance.' % mission.__class__.__name__)

        self._absolute_error_tolerance = 1e-6 # For the adaptive ODE solver

        self._mission = mission
        self._system = mission.system

        self._verbose = bool(verbose)

        self._n_dims = None

        self._planet_idx = None

        self._current_time = None
        self._current_position = None
        self._current_velocity = None

        self._events = _SpacecraftJourneyEvents()

        self._video_active = False
        self._recorded_trajectories = []

    @property
    def mission(self):
        """:class:`SpaceMission`: The mission that the spacecraft journey is associated with."""
        return self._mission

    @property
    def system(self):
        """:class:`ast2000tools.solar_system.SolarSystem`: The solar system in which the spacecraft journey takes place."""
        return self._system

    @property
    def verbose(self):
        """bool: Whether non-essential messages will be printed during the journey."""
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        self._verbose = bool(verbose)

    @property
    def video_active(self):
        """bool: Whether video is currently being recorded as the spacecraft moves."""
        return self._video_active

    def orient(self):
        """Returns the current time, spacecraft position and spacecraft velocity.

        Note
        ----
            When performing an interplanetary travel, the vectors are 2D and the units are years and astronomical units and relative to the star.
            When performing a landing sequence, the vectors are 3D and the units are SI and relative to the planet.

        Returns
        -------
        float
            The current time.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) or (3,) containing the current position.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) or (3,) containing the current velocity.
        """
        if self.verbose:
            print('Performed automatic orientation:')
            self._print_state()

        return self._current_time, self._current_position.copy(), self._current_velocity.copy()

    def take_picture(self, filename='journey_picture.xml'):
        """Generates a picture viewable in MCAst, with framing decided by the current spacecraft/lander camera orientation.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "journey_picture.xml".
        """
        filename = str(filename)

        theta, phi = self._camera._compute_orientation(self._current_time, self._current_position, self._current_velocity)

        self.system._generate_spacecraft_picture(self._convert_to_output_time(self._current_time),
                                                 self._convert_to_output_position(self._current_time, self._current_position),
                                                 (theta, phi),
                                                 planet_idx=self._planet_idx,
                                                 filename=filename)

        if self.verbose:
            print('Picture saved to %s.' % filename)

    def start_video(self):
        """Starts recording what the spacecraft/lander camera sees.

        Raises
        ------
        RuntimeError
            When called while video mode is active.
        """
        if self.video_active:
            print('Make sure to call finish_video before starting a new one.')
            raise RuntimeError('Video mode is already active.')

        self._video_active = True

        if self.verbose:
            print('Video recording started.')

    def finish_video(self, filename='journey_video.xml', number_of_frames=1000, radial_camera_offset=0):
        """Ends the recording and generates a corresponding video viewable in MCAst.

        Note
        ----
            The radial camera offset is only applied during a landing sequence.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "journey_video.xml".
        number_of_frames : int, optional
            The number of video frames to generate.
            Default is 1000, but must be at least 100.
        radial_camera_offset : float, optional
            The distance from the planet surface to offset the camera in order to avoid clipping during landing, in meters.
            Default is no offset.

        Raises
        ------
        RuntimeError
            When called while video mode is not active.
        """
        filename = str(filename)

        number_of_frames = int(number_of_frames)
        if number_of_frames < 100:
            raise ValueError('Argument "number_of_frames" is %d but must be at least 100.' % number_of_frames)

        if not self.video_active:
            print('You have to start a video before you can finish it.')
            raise RuntimeError('Video mode is already inactive.')

        n_trajectory_segments = len(self._recorded_trajectories)
        if n_trajectory_segments == 0:
            print('WARNING: No video produced because the spacecraft did not move during the recording.')
            self._video_active = False
            return

        # Combine the time arrays for all trajectory segments into a single array, removing dupicate times at endpoints
        all_times = np.concatenate([self._recorded_trajectories[0]['times']] +
                                   [trajectory['times'][1:] for trajectory in self._recorded_trajectories[1:]])

        all_positions = np.concatenate([self._recorded_trajectories[0]['positions']] +
                                       [trajectory['positions'][:, 1:] for trajectory in self._recorded_trajectories[1:]],
                                       axis=1)

        all_velocities = np.concatenate([self._recorded_trajectories[0]['velocities']] +
                                        [trajectory['velocities'][:, 1:] for trajectory in self._recorded_trajectories[1:]],
                                        axis=1)

        # Uniformly sample number_of_frames times for the video frames
        local_frame_times = np.linspace(all_times[0], all_times[-1], number_of_frames)

        # Create interpolators for positions and velocities
        position_interpolator = interpolate.interp1d(all_times, all_positions, axis=1, kind='cubic', bounds_error=True, assume_sorted=True, copy=False)
        velocity_interpolator = interpolate.interp1d(all_times, all_velocities, axis=1, kind='linear', bounds_error=True, assume_sorted=True, copy=False)

        # Compute interpolated position and velocities at the frame times
        local_frame_positions = position_interpolator(local_frame_times)
        local_frame_velocities = velocity_interpolator(local_frame_times)

        # Offset positions in the radial direction to avoid clipping the planet surface
        if self._planet_idx is not None:
            local_frame_positions += radial_camera_offset*local_frame_positions/np.linalg.norm(local_frame_positions, axis=0)[np.newaxis, :]

        # Convert to system coordinates
        frame_times = self._convert_to_output_times(local_frame_times)
        frame_positions = self._convert_to_output_positions(local_frame_times, local_frame_positions)
        frame_velocities = self._convert_to_output_velocities(local_frame_times, local_frame_velocities)

        # Compute orientation angles for each frame

        frame_orientations = np.zeros((2, number_of_frames))

        segment_end_times = [trajectory['times'][-1] for trajectory in self._recorded_trajectories]
        segment_end_frame_indices = np.searchsorted(local_frame_times, segment_end_times)

        segment_start_frame_idx = 0

        for segment_idx in range(n_trajectory_segments):

            segment_end_frame_idx = segment_end_frame_indices[segment_idx] + 1

            polar_angles, azimuth_angles = self._recorded_trajectories[segment_idx]['camera']._compute_orientations(frame_times[segment_start_frame_idx:segment_end_frame_idx],
                                                                                                                    frame_positions[:, segment_start_frame_idx:segment_end_frame_idx],
                                                                                                                    frame_velocities[:, segment_start_frame_idx:segment_end_frame_idx])

            frame_orientations[0, segment_start_frame_idx:segment_end_frame_idx] = polar_angles
            frame_orientations[1, segment_start_frame_idx:segment_end_frame_idx] = azimuth_angles

            segment_start_frame_idx = segment_end_frame_idx

        self.system._generate_spacecraft_video(frame_times, frame_positions, frame_orientations,
                                               planet_idx=self._planet_idx,
                                               filename=filename)

        if self.verbose:
            print('Video with %d frames saved to %s.' % (number_of_frames, filename))

        self._video_active = False
        self._recorded_trajectories = []

    def look_in_fixed_direction(self, polar_angle=const.pi/2, azimuth_angle=0):
        """Orients the camera in a fixed direction specified by the given spherical angles.

        Parameters
        ----------
        polar_angle : float, optional
            The polar angle to use for the camera direction.
            Default is pi/2. Must be in the range [0, pi].
        azimuth_angle : float, optional
            The azimuthal angle to use for the camera direction.
            Default is 0.
        """
        polar_angle = float(polar_angle)
        if polar_angle < 0 or polar_angle > const.pi:
            raise ValueError('Argument "polar_angle" is %g but must be in the range [0, pi] rad.' % polar_angle)

        azimuth_angle = float(azimuth_angle)

        self._camera = _Camera(self.system, self._n_dims,
                               relative_polar_angle=polar_angle,
                               relative_azimuth_angle=azimuth_angle)

        if self.verbose:
            print('Camera pointing with fixed polar angle %g rad and azimuthal angle %g rad.'
                  % (polar_angle, azimuth_angle))

    def look_in_direction_of_planet(self, planet_idx=None, relative_polar_angle=0, relative_azimuth_angle=0):
        """Makes the camera point towards a given angle relative to the direction of the planet.

        Parameters
        ----------
        planet_idx : int, optional
            The index of the planet to track.
            If performing a landing, the default is to use the planet being landed on.
            Otherwise, `planet_idx` must be specified or an error is raised.
        relative_polar_angle : float, optional
            The polar angle to offset the camera with relative to the direction towards the planet.
            Default is 0. Must be in the range [0, pi].
        relative_azimuth_angle : float, optional
            The azimuthal angle to offset the camera with relative to the direction towards the planet.
            Default is 0.
        """
        if planet_idx is None:
            if self._planet_idx is None:
                raise ValueError('Argument "planet_idx" not set and no appropriate default is available.')
            else:
                planet_idx = self._planet_idx
        else:
            planet_idx = int(planet_idx)
            if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
                raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        relative_polar_angle = float(relative_polar_angle)
        if relative_polar_angle < 0 or relative_polar_angle > const.pi:
            raise ValueError('Argument "relative_polar_angle" is %g but must be in the range [0, pi] rad.' % relative_polar_angle)

        relative_azimuth_angle = float(relative_azimuth_angle)

        self._camera = _PlanetRelativeCamera(planet_idx, self.system, self._n_dims,
                                             relative_polar_angle=relative_polar_angle,
                                             relative_azimuth_angle=relative_azimuth_angle)

        if self.verbose:
            print('Camera pointing towards planet %d' % planet_idx, end='')
            if relative_polar_angle == 0 and relative_azimuth_angle == 0:
                print('.')
            else:
                print(' with polar angle offset %g rad and azimuthal angle offset %g rad.'
                      % (relative_polar_angle, relative_azimuth_angle))

    def look_in_direction_of_motion(self, relative_polar_angle=0, relative_azimuth_angle=0):
        """Makes the camera point towards a given angle relative to the direction of motion.

        Parameters
        ----------
        relative_polar_angle : float, optional
            The polar angle to offset the camera with relative to the direction of motion.
            Default is 0. Must be in the range [0, pi].
        relative_azimuth_angle : float, optional
            The azimuthal angle to offset the camera with relative to the direction of motion.
            Default is 0.
        """
        relative_polar_angle = float(relative_polar_angle)
        if relative_polar_angle < 0 or relative_polar_angle > const.pi:
            raise ValueError('Argument "relative_polar_angle" is %g but must be in the range [0, pi] rad.' % relative_polar_angle)

        relative_azimuth_angle = float(relative_azimuth_angle)

        self._camera = _MotionRelativeCamera(self.system, self._n_dims,
                                             relative_polar_angle=relative_polar_angle,
                                             relative_azimuth_angle=relative_azimuth_angle)

        if self.verbose:
            print('Camera pointing towards direction of motion', end='')
            if relative_polar_angle == 0 and relative_azimuth_angle == 0:
                print('.')
            else:
                print(' with polar angle offset %g rad and azimuthal angle offset %g rad.'
                      % (relative_polar_angle, relative_azimuth_angle))

    def set_camera_up_vector(self, up_x, up_y, up_z):
        """Specifies the up-vector to use for the camera.

        Parameters
        ----------
        up_x : float
            The x-component of the camera up-vector.
        up_y : float
            The y-component of the camera up-vector.
        up_z : float
            The z-component of the camera up-vector.
        """
        self._camera._set_up_vector(float(up_x), float(up_y), float(up_z))

        if self.verbose:
            print('Camera up-vector set to (%g, %g, %g).' % self._camera._get_up_vector())

    def restart(self):
        """Resets the spacecraft and system to the initial state.

        Raises
        ------
        RuntimeError
            When called while video recording is active.
        """
        if self.video_active:
            raise RuntimeError('Video mode is active, make sure to call finish_video before restarting.')

        self._move_to_initial_state()

        if self.verbose:
            print('The spacecraft and system were reset to initial state.')

    def _compute_trajectory(self, start_time, start_position, start_velocity, end_time, tolerance=1e-9):

        start_pos_vel = np.concatenate((start_position, start_velocity))

        result = integrate.solve_ivp(self._compute_derivatives,
                                     (start_time, end_time),
                                     start_pos_vel,
                                     method = 'RK45',
                                     atol=self._absolute_error_tolerance,
                                     rtol=tolerance)

        if result.success == False:
            print('Unsuccessful termination of trajectory solver: %s' % result.message)
            print('Possible reason: You are moving too fast close to a planet and/or have decreased the tolerance too much.')
            print('Ask a group teacher if in doubt.')
            raise RuntimeError('Trajectory solver failed.')

        return (result.t,                   # Output times produced by the solver
                result.y[:self._n_dims, :], # Output positions produced by the solver
                result.y[self._n_dims:, :]) # Output velocities produced by the solver

    def _advance_until_time(self, end_time, tolerance=1e-9):

        end_time = float(end_time)
        if end_time < self._current_time:
            raise ValueError('Duration of advancement must be positive (end time %g < current time %g).'
                             % (end_time, self._current_time))
        elif end_time == self._current_time:
            return

        start_time = self._current_time

        output_times, output_positions, output_velocities = self._compute_trajectory(self._current_time,
                                                                                     self._current_position,
                                                                                     self._current_velocity,
                                                                                     end_time,
                                                                                     tolerance=tolerance)

        self._current_time = output_times[-1]
        self._current_position[:] = output_positions[:, -1]
        self._current_velocity[:] = output_velocities[:, -1]

        # Process events detected during the integration
        self._process_new_events(start_time)

        if self.video_active:
            # Store relevant trajectory data required when generating a video
            self._recorded_trajectories.append({'times': output_times,
                                                'positions': output_positions,
                                                'velocities': output_velocities,
                                                'camera': self._camera})


class InterplanetaryTravel(_SpacecraftJourney):
    """Represents a journey with your spacecraft through interplanetary space.

    Note
    ----
        Do not create instances of this class directly, use :meth:`~SpaceMission.begin_interplanetary_travel` instead.

    Raises
    ------
    RuntimeError
        When initialized with a system where :meth:`~SpaceMission.verify_manual_orientation` has not been called successfully.
    """
    def __init__(self, *args, **kwargs):

        super(InterplanetaryTravel, self).__init__(*args, **kwargs)

        self._n_dims = 2
        self._camera = _Camera(self.system, self._n_dims)

        self._current_time = 0               # Current time [yr]
        self._current_position = np.zeros(2) # Current position of the spacecraft [AU]
        self._current_velocity = np.zeros(2) # Current velocity of the spacecraft [AU/yr]

        self._remaining_fuel_mass = 0

        self._move_to_initial_state()

    @property
    def mission(self):
        return self._mission

    @property
    def system(self):
        return self._system

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        self._verbose = bool(verbose)

    @property
    def video_active(self):
        return self._video_active

    @property
    def remaining_fuel_mass(self):
        """float: The remaining fuel mass in kilograms."""
        return self._remaining_fuel_mass

    def coast(self, duration, tolerance=1e-9):
        """Integrates the spacecraft trajectory for a given duration and updates the current position and velocity.

        Parameters
        ----------
        duration : float
            The duration to coast, in years.
        tolerance : float, optional
            The relative error tolerance to use when integrating the trajectory.
            Default is 10^-9, which should be fine for the majority of cases.
        """
        self._advance_until_time(self._current_time + duration, tolerance=tolerance)

        if self.verbose:
            print('Spacecraft coasted for %g yr.' % duration)

    def coast_until_time(self, end_time, tolerance=1e-9):
        """Integrates the spacecraft trajectory until a given end time and updates the current position and velocity.

        Parameters
        ----------
        end_time : float
            The time to stop coasting, in years.
        tolerance : float, optional
            The relative error tolerance to use when integrating the trajectory.
            Default is 10^-9, which should be fine for the majority of cases.
        """
        self._advance_until_time(end_time, tolerance=tolerance)

        if self.verbose:
            print('Spacecraft coasted until time %g yr.' % end_time)

    def boost(self, delta_v):
        """Adds the given velocity difference to the current spacecraft velocity and updates the amount of remaining fuel.

        Parameters
        ----------
        delta_v : 1-D array_like
            Array of shape (2,) containing the x and y-component of the change in velocity, in astronomical units per year.

        Raises
        ------
        RuntimeError
            When running out of fuel.
        """
        delta_v = np.asarray(delta_v, dtype=float)
        if delta_v.shape != (2,):
            raise ValueError('Argument "delta_v" has shape %s but must have shape (2,).' % str(delta_v.shape))


        if self.remaining_fuel_mass > 0:    
            # Compute the fuel needed to perform the given boost
            fuel_mass_used = self.mission._compute_fuel_mass_needed_for_boost(self.remaining_fuel_mass, delta_v)

            # Update the current remaining fuel amount
            self._remaining_fuel_mass -= fuel_mass_used

        if self.verbose:
            if self.remaining_fuel_mass > 0:    
                print('Spacecraft boosted with delta-v (%g, %g) AU/yr (%g kg of fuel was used).'
                      % (delta_v[0], delta_v[1], fuel_mass_used))
            else:
                print('Spacecraft boosted with delta-v (%g, %g) AU/yr).'
                      % (delta_v[0], delta_v[1]))
                      

        if self.remaining_fuel_mass < 0:
            if self.verbose:
                print('You ran out of fuel. Luckily a NASA refueling rocket was close by to help you out!')
            
        # Update the current velocity
        self._current_velocity += delta_v

    def orient(self):
        """Returns the current time, spacecraft position and spacecraft velocity.

        Returns
        -------
        float
            The current time in years.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the current position in astronomical units relative to the star.
        1-D :class:`numpy.ndarray`
            Array of shape (2,) containing the current velocity in astronomical units per second relative to the star.
        """
        return super(InterplanetaryTravel, self).orient()

    def take_picture(self, filename='travel_picture.xml'):
        """Generates a picture viewable in MCAst, with framing decided by the current spacecraft camera orientation.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "travel_picture.xml".
        """
        super(InterplanetaryTravel, self).take_picture(filename=filename)

    def start_video(self):
        super(InterplanetaryTravel, self).start_video()

    def finish_video(self, filename='travel_video.xml', number_of_frames=1000):
        """Ends the recording and generates a corresponding video viewable in MCAst.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "travel_video.xml".
        number_of_frames : int, optional
            The number of video frames to generate.
            Default is 1000, but must be at least 100.

        Raises
        ------
        RuntimeError
            When called while video mode is not active.
        """
        super(InterplanetaryTravel, self).finish_video(filename=filename, number_of_frames=number_of_frames, radial_camera_offset=0)

    def look_in_fixed_direction(self, polar_angle=const.pi/2, azimuth_angle=0):
        super(InterplanetaryTravel, self).look_in_fixed_direction(polar_angle=polar_angle, azimuth_angle=azimuth_angle)

    def look_in_direction_of_planet(self, planet_idx, relative_polar_angle=0, relative_azimuth_angle=0):
        """Makes the camera point towards a given angle relative to the direction of the planet.

        Parameters
        ----------
        planet_idx : int
            The index of the planet to track.
        relative_polar_angle : float, optional
            The polar angle to offset the camera with relative to the direction towards the planet.
            Default is 0. Must be in the range [0, pi].
        relative_azimuth_angle : float, optional
            The azimuthal angle to offset the camera with relative to the direction towards the planet.
            Default is 0.
        """
        super(InterplanetaryTravel, self).look_in_direction_of_planet(planet_idx, relative_polar_angle=relative_polar_angle, relative_azimuth_angle=relative_azimuth_angle)

    def look_in_direction_of_motion(self, relative_polar_angle=0, relative_azimuth_angle=0):
        super(InterplanetaryTravel, self).look_in_direction_of_motion(relative_polar_angle=relative_polar_angle, relative_azimuth_angle=relative_azimuth_angle)

    def set_camera_up_vector(self, up_x, up_y, up_z):
        super(InterplanetaryTravel, self).set_camera_up_vector(up_x, up_y, up_z)

    def record_destination(self, planet_idx):
        """Saves the current time, spacecraft position and velocity, and destination planet index.

        Note
        ----
            The last recorded state is used as initial conditions for the landing procedure.
            You will only be able to initiate a landing sequence if the recorded position is sufficiently close to the specified planet.

        Parameters
        ----------
        planet_idx : int
            The index of the destination planet.
        """
        if self._events._has_tag('failure'):
            print('WARNING: The current journey has failed, ignoring "record_destination" call.')
            return

        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        self._mission._destination_planet_idx = planet_idx
        self._mission._initial_landing_time = self._current_time
        self._mission._initial_landing_position = self._current_position.copy()
        self._mission._initial_landing_velocity = self._current_velocity.copy()

        # Make sure the arrays are not altered by mistake
        self._mission._initial_landing_position.setflags(write=False)
        self._mission._initial_landing_velocity.setflags(write=False)

        self._mission._destination_recorded = True

        if self.verbose:
            print('Recorded interplanetary travel destination:')
            print('Time: %g yr' % self._current_time)
            print('Position: (%g, %g) AU' % (self._current_position[0], self._current_position[1]))
            print('Velocity: (%g, %g) AU/yr' % (self._current_velocity[0], self._current_velocity[1]))

    def restart(self):
        """Resets the spacecraft and system to the initial state after launch.

        Note
        ----
            If a new launch has been performed since the interplanetary travel began,
            the new post-launch state will be used as initial condition.
            But the new launch result must have been verified first.

            Also be aware that any recorded destination state will be cleared.

        Raises
        ------
        RuntimeError
            When called while video recording is active.
        """
        super(InterplanetaryTravel, self).restart()

    def _convert_to_output_time(self, time):
        return time

    def _convert_to_output_times(self, times):
        return times

    def _convert_to_output_position(self, time, position):
        return position

    def _convert_to_output_positions(self, times, positions):
        return positions

    def _convert_to_output_velocities(self, times, velocities):
        return velocities

    def _print_state(self):
        print('Time: %g yr' % self._current_time)
        print('Position: (%g, %g) AU' % (self._current_position[0], self._current_position[1]))
        print('Velocity: (%g, %g) AU/yr' % (self._current_velocity[0], self._current_velocity[1]))

    def _move_to_initial_state(self):
        """Resets the spacecraft position, velocity and time to the values right after launch.
        """
        if self.mission.launch_result_verified == False:
            print('You need to verify the launch results before you can begin an interplanetary travel.')
            print('Please call verify_launch_result with the correct final position before proceeding.')
            raise RuntimeError('Interplanetary travel not ready.')

        if self.mission.manual_orientation_verified == False:
            print('You need to verify your manual orientation before you can begin an interplanetary travel.')
            print('Please call verify_manual_orientation with the correct final orientation data before proceeding.')
            raise RuntimeError('Interplanetary travel not ready.')

        self._current_time = self.mission.time_after_launch
        self._current_position = self.mission._position_after_launch.copy()
        self._current_velocity = self.mission._velocity_after_launch.copy()
        self._remaining_fuel_mass = self.mission._remaining_fuel_mass_after_launch

        self._events._clear()

        if self.mission.ongoing_landing_sequence is not None:
            self.mission._ongoing_landing_sequence = None
            if self.verbose:
                print('Note: Ongoing landing sequence was terminated.')

        if self.mission.destination_recorded:

            self._mission._destination_planet_idx = None
            self._mission._initial_landing_time = None
            self._mission._initial_landing_position = None
            self._mission._initial_landing_velocity = None

            self._mission._destination_recorded = False

            if self.verbose:
                print('Note: Existing recorded destination was cleared.')

    def _move_to(self, time, position, velocity):
        self._current_time = time
        self._current_position[:] = position
        self._current_velocity[:] = velocity

    def _compute_derivatives(self, time, pos_vel):
        """Computes the acceleration of the spacecraft due to the gravity from the planets and star.

        Parameters
        ----------
        time : float
            The time to get the acceleration, in years.
        pos_vel : 1-D :class:`numpy.ndarray`
            Array of shape (4,) with concatenated position and velocity at the given time, in astronomical units [per year] relative to the star.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (4,) with concatenated velocity and acceleration at the given time.
        """
        planet_positions = self.system._compute_planet_positions(time) # May be changed later for speed.
        acceleration = np.zeros(2)

        self._events._remove_all_outdated(time)

        # Compute the acceleration on the spacecraft from all the planets
        for j in range(self.system.number_of_planets):

            rij = pos_vel[0:2] - planet_positions[:, j]
            acceleration += self.system._compute_gravitational_acceleration(rij, self.system.masses[j])

            if np.linalg.norm(rij) < utils.km_to_AU(self.system.radii[j]):
                self._events._add_if_absent('crashed', time, data={'planet': j}, tag='failure')

        # Add the acceleration on the spacecraft from the star
        acceleration += self.system._compute_gravitational_acceleration(pos_vel[0:2], self.system.star_mass)

        if np.linalg.norm(pos_vel[0:2]) < utils.km_to_AU(self.system.star_radius):
            self._events._add_if_absent('burned', time, tag='failure')

        dxv    = np.zeros(4)
        dxv[0] = pos_vel[2]
        dxv[1] = pos_vel[3]
        dxv[2] = acceleration[0]
        dxv[3] = acceleration[1]

        return dxv

    def _process_new_events(self, start_time):
        """Treats events that occurred during the last coasting period.

        Parameters
        ----------
        start_time : float
            The time at the beginning of the last coasting period.
        """
        history = self._events._get_history(start_time)

        for name, event in history:

            time = event[0]
            data = event[1]

            if name == 'crashed':
                raise RuntimeError('FAILURE: You collided with planet %d at time %g.' % (data['planet'], time))

            elif name == 'burned':
                raise RuntimeError('FAILURE: You were swallowed by the sun at time %g.' % time)

            else:
                raise ValueError('Untreated interplanetary travel event: %s.' % name)


class LandingSequence(_SpacecraftJourney):
    """Represents a landing process with your spacecraft at the destination planet.

    Note
    ----
        Do not create instances of this class directly, use :meth:`~SpaceMission.begin_landing_sequence` instead.

    Raises
    ------
    RuntimeError
        When called before the destination of the interplanetary travel has been recorded.
    RuntimeError
        When the recorded position is not sufficiently close to the destination planet.
    """
    def __init__(self, mission, assume_uniform_gravity_atmosphere=True, verbose=True):

        super(LandingSequence, self).__init__(mission, verbose=verbose)

        self._n_dims = 3
        self._camera = _Camera(self.system, self._n_dims)

        self._assume_uniform_gravity_atmosphere = bool(assume_uniform_gravity_atmosphere)

        self._drag_coefficient = 1.0

        self._max_landing_thruster_height = 500.0    # [m]
        self._max_impact_speed = 3.0                 # [m/s]
        self._max_drag_for_orbital_decay = 1e3       # [N]
        self._max_drag_for_parachute_failure = 2.5e5 # [N]
        self._max_drag_per_area_for_burn = 1e7       # [N/m^s]

        self._initial_time_in_system = 0               # System time when the landing sequence begins [yr]
        self._initial_position_in_system = np.zeros(2) # Position relative to system center when landing begins [AU]
        self._initial_velocity_in_system = np.zeros(2) # Velocity relative to system center when landing begins [AU/yr]
        self._initial_position = np.zeros(3)           # Position relative to planet center when landing begins [m]
        self._initial_velocity = np.zeros(3)           # Velocity relative to planet center when landing begins [m/s]

        self._current_time = 0               # Time elapsed after landing sequence began [s]
        self._current_position = np.zeros(3) # Position relative to planet center [m]
        self._current_velocity = np.zeros(3) # Velocity relative to planet center [m/s]

        self._lander_launched = False       # Whether the landing module has been launched from the spacecraft

        self._parachute = {'area': 0,       # Cross-sectional area of the parachute [m^2]
                           'min_height': 0} # Height where the parachute should be deployed [m]

        self._landing_thruster = {'force': 0,      # Downward force excerted by the landing thruster [N]
                                  'min_height': 0} # Height where the landing thruster should be activated [m]

        self._move_to_initial_state()

    @property
    def mission(self):
        return self._mission

    @property
    def system(self):
        return self._system

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        self._verbose = bool(verbose)

    @property
    def video_active(self):
        return self._video_active

    @property
    def lander_launched(self):
        """bool: Whether the landing module has been launched."""
        return self._lander_launched

    @property
    def parachute_deployed(self):
        """bool: Whether the parachute has been deployed."""
        return self._events._has('deployed_parachute')

    @property
    def parachute_broken(self):
        """bool: Whether the parachute was destroyed."""
        return self._events._has('broke_parachute')

    @property
    def landing_thruster_activated(self):
        """bool: Whether the landing thruster has been activated."""
        return self._events._has('activated_thruster')

    @property
    def reached_surface(self):
        """bool: Whether the surface has been reached."""
        return self._events._has('reached_surface')

    def _adjust_parachute(self, area=None, min_height=None):
        """Modifies parachute parameters.

        Note
        ----
            The default area and minimum height are both zero.

        Parameters
        ----------
        area : float, optional
            The area to use for the parachute, in square meters.
            By default, the area remains at the previous value.
        min_height : float, optional
            The height below which the parachute will be automatically deployed, in meters.
            By default, the minimum height remains at the previous value.

        Raises
        ------
        RuntimeError
            When the parachute has already been deployed.
        """
        if self.parachute_deployed:
            print('Parachute properties cannot be adjusted after it has been deployed.')
            raise RuntimeError('Parachute has already been deployed.')

        if area is not None:
            area = float(area)
            if area < 0:
                raise ValueError('Argument "area" is %g but must be positive.' % area)
            self._parachute['area'] = area

        if min_height is not None:
            min_height = float(min_height)
            if min_height < 0:
                raise ValueError('Argument "min_height" is %g but must be positive.' % min_height)
            self._parachute['min_height'] = min_height

        if self.verbose:
            print('Parachute properties:\n  Area: %g m^2\n  Minimum deployment height: %g m'
                  % (self._parachute['area'], self._parachute['min_height']))

    def adjust_parachute_area(self, area):
        """Sets the parachute area.

        Parameters
        ----------
        area : float
            The area to use for the parachute, in square meters.

        Raises
        ------
        RuntimeError
            When the parachute has already been deployed.
        """
        if self.parachute_deployed:
            print('Parachute area cannot be adjusted after it has been deployed.')
            raise RuntimeError('Parachute has already been deployed.')

        area = float(area)
        if area < 0:
            raise ValueError('Argument "area" is %g but must be positive.' % area)
        self._parachute['area'] = area

        if self.verbose:
            print('Parachute area: %g m^2' % self._parachute['area'])

    def adjust_landing_thruster(self, force=None, min_height=None):
        """Modifies landing thruster parameters.

        Note
        ----
            The default force and minimum height are both zero.

        Parameters
        ----------
        force : float, optional
            The force to use for the landing thruster, in Newtons.
            By default, the force remains at the previous value.
        min_height : float, optional
            The height below which the thruster will be automatically activated, in meters.
            Cannot exceed 500 m.
            By default, the minimum height remains at the previous value.

        Raises
        ------
        RuntimeError
            When the landing thrusted has already been activated.
        """
        if self.landing_thruster_activated:
            print('Landing thruster properties cannot be adjusted after it has been activated.')
            raise RuntimeError('Landing thruster is already activated.')

        if force is not None:
            force = float(force)
            if force < 0:
                raise ValueError('Argument "force" must be positive.')
            self._landing_thruster['force'] = force

        if min_height is not None:
            min_height = float(min_height)
            if min_height < 0:
                raise ValueError('Argument "min_height" must be positive.')
            if min_height > self._max_landing_thruster_height:
                raise ValueError('Argument "min_height" cannot exceed %g m.' % self._max_landing_thruster_height)
            self._landing_thruster['min_height'] = min_height

        if self.verbose:
            print('Landing thruster properties:\n  Force: %g N\n  Minimum activation height: %g m'
                  % (self._landing_thruster['force'], self._landing_thruster['min_height']))

    def fall(self, duration, tolerance=1e-9):
        """Integrates the spacecraft/lander trajectory for a given duration and updates the current position and velocity.

        Parameters
        ----------
        duration : float
            The duration to coast, in seconds.
        tolerance : float, optional
            The relative error tolerance to use when integrating the trajectory.
            Default is 10^-9, which should be fine for the majority of cases.
        """
        self._advance_until_time(self._current_time + duration, tolerance=tolerance)

        if self.verbose:
            print('%s %s for %g s.' % ('Lander' if self.lander_launched else 'Spacecraft',
                                       'rested on surface' if self.reached_surface else 'fell',
                                       duration))

    def fall_until_time(self, end_time, tolerance=1e-9):
        """Integrates the spacecraft/lander trajectory until a given end time and updates the current position and velocity.

        Parameters
        ----------
        end_time : float
            The time to stop coasting, in seconds.
        tolerance : float, optional
            The relative error tolerance to use when integrating the trajectory.
            Default is 10^-9, which should be fine for the majority of cases.
        """
        self._advance_until_time(end_time, tolerance=tolerance)

        if self.verbose:
            print('%s %s until time %g s.' % ('Lander' if self.lander_launched else 'Spacecraft',
                                              'rested on surface' if self.reached_surface else 'fell',
                                              end_time))

    def boost(self, delta_v):
        """Adds the given velocity difference to the current spacecraft velocity.

        Parameters
        ----------
        delta_v : 1-D array_like
            Array of shape (3,) containing the x, y and z-component of the change in velocity, in meters per second.

        Raises
        ------
        RuntimeError
            When the landing module has been launched.
        RuntimeError
            When the lander has already been able to land.
        """
        if self.lander_launched:
            print('You cannot boost after the landing module has been launched.')
            raise RuntimeError('Landing module has been launched.')

        if self.reached_surface:
            print('You cannot boost after landing is completed.')
            raise RuntimeError('Landing is completed.')

        delta_v = np.asarray(delta_v, dtype=float)
        if delta_v.shape != (3,):
            raise ValueError('Argument "delta_v" has shape %s but must have shape (3,).' % str(delta_v.shape))

        # Update the current spacecraft velocity
        self._current_velocity += delta_v

        if self.verbose:
            print('Spacecraft boosted with delta-v (%g, %g, %g) m/s.' % (delta_v[0], delta_v[1], delta_v[2]))

    def launch_lander(self, delta_v):
        """Launches the landing module from the spacecraft with the given boost.

        Parameters
        ----------
        delta_v : 1-D array_like
            Array of shape (3,) containing the x and y-component of the change in velocity, in meters per seconds.

        Raises
        ------
        RuntimeError
            When the landing module has already been launched.
        RuntimeError
            When the spacecraft has already been able to land.
        """
        if self.lander_launched:
            print('You cannot launch the landing module when it has already been launched.')
            raise RuntimeError('Landing module has already been launched.')

        if self.reached_surface:
            print('You cannot launch the landing module after landing is completed.')
            raise RuntimeError('Landing is completed.')

        delta_v = np.asarray(delta_v, dtype=float)
        if delta_v.shape != (3,):
            raise ValueError('Argument "delta_v" has shape %s but must have shape (3,).' % str(delta_v.shape))

        self._lander_launched = True

        # Update the current lander velocity
        self._current_velocity += delta_v

        if self.verbose:
            print('Landing module launched at time %g s with delta-v (%g, %g, %g) m/s.'
                  % (self._current_time, delta_v[0], delta_v[1], delta_v[2]))

    def deploy_parachute(self):
        """Deploys the parachute.

        Raises
        ------
        RuntimeError
            When the parachute has already been deployed.
        RuntimeError
            When the lander has already been able to land.
        """
        if self.parachute_deployed:
            print('You cannot deploy the parachute when it has already been deployed.')
            raise RuntimeError('Parachute has already been deployed.')

        if self.reached_surface:
            print('You cannot deploy the parachute after landing is completed.')
            raise RuntimeError('Landing is completed.')

        self._events._add_if_absent('deployed_parachute', self._current_time, never_outdated=True)

    def activate_landing_thruster(self):
        """Activates the landing thruster.

        Note
        ----
            Does nothing if the lander is farther than 500 m from the surface.

        Raises
        ------
        RuntimeError
            When the landing thruster has already been activated.
        RuntimeError
            When the lander has already been able to land.
        """
        if self.landing_thruster_activated:
            print('You cannot activate the landing thruster when it has already been launched.')
            raise RuntimeError('Landing thruster is already activated.')

        if self.reached_surface:
            print('You cannot activate the landing thruster after landing is completed.')
            raise RuntimeError('Landing is completed.')

        distance_from_center = np.linalg.norm(self._current_position)
        height = distance_from_center - self._planet_radius
        if height > self._max_landing_thruster_height:
            print('WARNING: You cannot activate the landing thruster until the lander is within %g m of the surface.'
                  % self._max_landing_thruster_height)
            return

        self._events._add_if_absent('activated_thruster', self._current_time, never_outdated=True)

    def orient(self):
        """Returns the current time, position and velocity for the spacecraft/lander.

        Returns
        -------
        float
            The current time after the initial landing sequence time, in seconds.
        1-D :class:`numpy.ndarray`
            Array of shape (3,) containing the current position in meters relative to the planet center.
        1-D :class:`numpy.ndarray`
            Array of shape (3,) containing the current velocity in meters per second relative to the planet center.
        """
        return super(LandingSequence, self).orient()

    def take_picture(self, filename='landing_picture.xml'):
        """Generates a picture viewable in MCAst, with framing decided by the current spacecraft/lander camera orientation.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "landing_picture.xml".
        """
        super(LandingSequence, self).take_picture(filename=filename)

    def start_video(self):
        super(LandingSequence, self).start_video()

    def finish_video(self, filename='landing_video.xml', number_of_frames=1000, radial_camera_offset=1e5):
        """Ends the recording and generates a corresponding video viewable in MCAst.

        Parameters
        ----------
        filename : str, optional
            Name of the XML file to generate inside the data directory.
            Default is "landing_video.xml".
        number_of_frames : int, optional
            The number of video frames to generate.
            Default is 1000, but must be at least 100.
        radial_camera_offset : float, optional
            The distance from the planet surface to offset the camera in order to avoid clipping during landing, in meters.
            Default is 10^5 meters.

        Raises
        ------
        RuntimeError
            When called while video mode is not active.
        """
        super(LandingSequence, self).finish_video(filename=filename, number_of_frames=number_of_frames, radial_camera_offset=radial_camera_offset)

    def look_in_fixed_direction(self, polar_angle=const.pi/2, azimuth_angle=0):
        super(LandingSequence, self).look_in_fixed_direction(polar_angle=polar_angle, azimuth_angle=azimuth_angle)

    def look_in_direction_of_planet(self, planet_idx=None, relative_polar_angle=0, relative_azimuth_angle=0):
        """Makes the camera point towards a given angle relative to the direction of the planet.

        Parameters
        ----------
        planet_idx : int, optional
            The index of the planet to track.
            By default the planet being landed on is used.
        relative_polar_angle : float, optional
            The polar angle to offset the camera with relative to the direction towards the planet.
            Default is 0. Must be in the range [0, pi].
        relative_azimuth_angle : float, optional
            The azimuthal angle to offset the camera with relative to the direction towards the planet.
            Default is 0.
        """
        super(LandingSequence, self).look_in_direction_of_planet(planet_idx=planet_idx, relative_polar_angle=relative_polar_angle, relative_azimuth_angle=relative_azimuth_angle)

    def look_in_direction_of_motion(self, relative_polar_angle=0, relative_azimuth_angle=0):
        super(LandingSequence, self).look_in_direction_of_motion(relative_polar_angle=relative_polar_angle, relative_azimuth_angle=relative_azimuth_angle)

    def set_camera_up_vector(self, up_x, up_y, up_z):
        super(LandingSequence, self).set_camera_up_vector(up_x, up_y, up_z)

    def restart(self):
        """Resets the spacecraft and system to the state at the beginning of the landing sequence.

        Note
        ----
            If a new interplanetary travel destination has been recorded since the landing sequence began,
            the new destination state will be used as initial condition.

            Also be aware that any recorded landing site coordinates will be cleared.

        Raises
        ------
        RuntimeError
            When called while video recording is active.
        """
        super(LandingSequence, self).restart()

    def _convert_to_output_time(self, time):
        """Converts from seconds after initial time to global system time in years.

        Parameters
        ----------
        time : float
            The time after the initial landing sequence time, in seconds.

        Returns
        -------
        float
            The time after the initial solar system time, in years.
        """
        return self._initial_time_in_system + utils.s_to_yr(time)

    def _convert_to_output_times(self, times):
        """Converts from seconds after initial time to global system times in years.

        Parameters
        ----------
        times : 1-D array_like
            The times after the initial landing sequence time, in seconds.

        Returns
        -------
        float
            The times after the initial solar system time, in years.
        """
        return self._initial_time_in_system + utils.s_to_yr(np.asarray(times, dtype=float))

    def _convert_to_output_position(self, time, position):
        """Converts from position relative to planet center in meters to position relative to star in astronomical units.

        Parameters
        ----------
        time : float
            The time after the initial landing sequence time, in seconds.
        position : 1-D array_like
            Array of shape (3,) containing the x, y and z-position in meters relative to the planet.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (3,) containing the x, y and z-position in astronomical units relative to the star.
        """
        output_time = self._convert_to_output_time(time)
        planet_position = self.system._compute_single_planet_position(output_time, self._planet_idx)
        return np.pad(planet_position, (0, 1), 'constant') + utils.m_to_AU(np.asarray(position, dtype=float))

    def _convert_to_output_positions(self, times, positions):
        """Converts from positions relative to planet center in meters to positions relative to star in astronomical units.

        Parameters
        ----------
        times : 1-D array_like
            The times after the initial landing sequence time, in seconds.
        positions : 2-D array_like
            Array of shape (3, len(`times`)) containing the x, y and z-position for each time, in meters relative to the planet.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (3, len(`times`)) containing the x, y and z-position for each time, in astronomical units relative to the star.
        """
        output_times = self._convert_to_output_times(times)
        planet_positions = self.system._compute_single_planet_trajectory(output_times, self._planet_idx)
        return np.pad(planet_positions, ((0, 1), (0, 0)), 'constant') + utils.m_to_AU(positions)

    def _convert_to_output_velocities(self, times, velocities, relative_to_system=False):
        """Converts from velocities relative to planet center in meters per second to velocities in astronomical units per year.

        Parameters
        ----------
        times : 1-D array_like
            The times after the initial landing sequence time, in seconds.
        velocities : 2-D array_like
            Array of shape (3, len(`times`)) containing the x, y and z-velocity for each time, in meters per second relative to the planet.
        relative_to_system : bool, optional
            Whether the output velocities should be relative to the star instead of relative to the planet.
            Default is relative to the planet.

        Returns
        -------
        2-D :class:`numpy.ndarray`
            Array of shape (3, len(`times`)) containing the x, y and z-velocity for each time, in astronomical units per year relative to the specified object.
        """
        output_velocities = utils.m_pr_s_to_AU_pr_yr(velocities)

        if relative_to_system:
            output_times = self._convert_to_output_times(times)
            planet_velocities = self.system._compute_single_planet_velocity_evolution(output_times, self._planet_idx)
            output_velocities += np.pad(planet_velocities, ((0, 1), (0, 0)), 'constant')

        return output_velocities

    def _print_state(self):
        print('Time: %g s' % self._current_time)
        print('Position: (%g, %g, %g) m' % (self._current_position[0], self._current_position[1], self._current_position[2]))
        print('Velocity: (%g, %g, %g) m/s' % (self._current_velocity[0], self._current_velocity[1], self._current_velocity[2]))

    def _compute_initial_conditions(self):
        """Computes the initial conditions of the landing sequence from the recorded state.

        Raises
        ------
        RuntimeError
            When called before the destination of the interplanetary travel has been recorded.
        RuntimeError
            When the recorded position is not sufficiently close to the destination planet.
        """
        if self.mission.destination_recorded == False:
            print('You need to complete the interplanetary travel and call record_destination before you can initiate a landing.')
            raise RuntimeError('No recorded initial conditions for landing.')

        self._planet_idx = self.mission.destination_planet_idx
        self._initial_time_in_system = self.mission.initial_landing_time
        self._initial_position_in_system = self.mission.initial_landing_position.copy()
        self._initial_velocity_in_system = self.mission.initial_landing_velocity.copy()

        planet_position = self.system._compute_single_planet_position(self._initial_time_in_system, self._planet_idx)
        planet_velocity = self.system._compute_single_planet_velocity(self._initial_time_in_system, self._planet_idx)

        self._initial_position[:2] = utils.AU_to_m(self._initial_position_in_system - planet_position)
        self._initial_velocity[:2] = utils.AU_pr_yr_to_m_pr_s(self._initial_velocity_in_system - planet_velocity)

        distance_to_planet = np.linalg.norm(self._initial_position)

        maximum_distance_to_planet = utils.AU_to_m(self.system._compute_force_balance_distance(self._planet_idx, k=10))

        if distance_to_planet > maximum_distance_to_planet:
            print('The spacecraft is not close enough to planet %d to initiate the landing:' % self._planet_idx)
            print('Distance is %g m, while upper distance limit is %g m (difference is %g m).'
                  % (distance_to_planet, maximum_distance_to_planet, abs(maximum_distance_to_planet - distance_to_planet)))
            raise RuntimeError('Not close enough to target planet.')

    def _compute_planet_properties(self):
        """Computes relvant properties of the destination planet.
        """
        self._planet_mass         = self.system.masses[self._planet_idx]*const.m_sun                 # [kg]
        self._planet_radius       = self.system.radii[self._planet_idx]*1e3                          # [m]
        self._surface_density     = self.system.atmospheric_densities[self._planet_idx]              # [kg/m^3]
        self._mean_molecular_mass = self.system._mean_molecular_masses[self._planet_idx]
        self._rotation_period     = utils.day_to_s(self.system.rotational_periods[self._planet_idx]) # [s]
        self._surface_gravity     = self._planet_mass*const.G/self._planet_radius**2                 # [m/s^2]
        self._escape_velocity     = np.sqrt(2*self._planet_mass*const.G/self._planet_radius)         # [m/s]
        self._surface_temperature = self.system._compute_single_planet_temperature(self._planet_idx) # [K]

        atmosphere_parameters = (self._planet_mass,
                                 self._planet_radius,
                                 self._surface_density,
                                 self._surface_temperature,
                                 self._mean_molecular_mass*const.m_p)

        self._atmosphere = _UniformGravityAtmosphere(*atmosphere_parameters) \
                               if self._assume_uniform_gravity_atmosphere else \
                               _Atmosphere(*atmosphere_parameters)

    def _move_to_initial_state(self):
        """Resets the spacecraft position, velocity and time as well as landing data to the initial values.
        """
        self._compute_initial_conditions()
        self._compute_planet_properties()

        self._current_time = 0
        self._current_position[:] = self._initial_position
        self._current_velocity[:] = self._initial_velocity

        self._lander_launched = False

        self._events._clear()

        if self.mission.ongoing_interplanetary_travel is not None:
            self.mission._ongoing_interplanetary_travel = None
            if self.verbose:
                print('Note: Ongoing interplanetary travel was terminated.')

        if self.mission.landing_completed:

            self._mission._landing_site_polar_angle = None
            self._mission._landing_site_azimuth_angle = None

            self._mission._landing_completed = False

            if self.verbose:
                print('Note: Existing landing site coordinates were cleared.')

    def _compute_derivatives(self, time, pos_vel):
        """Computes the acceleration of the spacecraft/lander due to gravity and drag, and also detects important events.

        Parameters
        ----------
        time : float
            The time to get the acceleration, in seconds.
        pos_vel : 1-D :class:`numpy.ndarray`
            Array of shape (4,) with concatenated position and velocity at the given time, in meters [per second] relative to the planet.

        Returns
        -------
        1-D :class:`numpy.ndarray`
            Array of shape (4,) with concatenated velocity and acceleration at the given time.
        """
        distance_from_center = np.linalg.norm(pos_vel[0:3])  # Distance from planet center [m]
        height = distance_from_center - self._planet_radius # Height above surface [m]

        atm_vel = 2*const.pi/self._rotation_period*np.array([-pos_vel[1], pos_vel[0], 0]) # Velocity of rotating atmosphere [m/s]
        rel_vel  = pos_vel[3:6] - atm_vel                                                 # Velocity relative to atmosphere [m/s]
        radial_vel = np.dot(pos_vel[3:6], pos_vel[0:3]/distance_from_center)              # Velocity in radial direction [m/s]

        self._events._remove_all_outdated(time)

        if height < 0 and not self.reached_surface:

            self._events._add('reached_surface', time)

            if (abs(radial_vel) > self._max_impact_speed):

                self._events._add_if_absent('crashed', time,
                                            data={'rel_vel': np.linalg.norm(rel_vel)},
                                            tag='failure')

            elif abs(radial_vel) < self._escape_velocity:

                self._events._add_if_tag_absent('failure', 'landed_successfully', time,
                                                 data={'position': pos_vel[0:3],
                                                       'radial_vel': abs(radial_vel)})

            elif radial_vel < 0: # In some cases, landing on an asteroid etc, the escape velocity is so small, lander bounces.
                self._events._add('bounced', time, data={'rel_vel': np.linalg.norm(rel_vel)})
                self._events._remove('reached_surface')
                pos_vel[3:] *= -1

            acceleration = np.zeros(3)

        elif self.reached_surface:

            pos_vel[3:6] = atm_vel # Should now follow planet rotation
            acceleration = np.zeros(3)

        else:

            if self.lander_launched:

                mass = self.mission.lander_mass
                area = self.mission.lander_area

                if height < self._parachute['min_height'] and height > 0:
                    self._events._add_if_absent('deployed_parachute', time)

                if height < self._landing_thruster['min_height'] and height > 0:
                    self._events._add_if_absent('activated_thruster', time)

            else:
                mass = self.mission.spacecraft_mass
                area = self.mission.spacecraft_area

            if self.parachute_deployed and not self.parachute_broken:
                area = max(self._parachute['area'], area)

            drag_force = -0.5*area*self._drag_coefficient*self._atmosphere._density(height)*rel_vel*np.linalg.norm(rel_vel)
            drag_force_magnitude = np.linalg.norm(drag_force)

            acceleration = drag_force/mass

            acceleration += (-const.G*self._planet_mass/distance_from_center**3)*pos_vel[0:3]

            if self.landing_thruster_activated:
                acceleration += self._landing_thruster['force']*pos_vel[0:3]/(distance_from_center*mass)

            if not self.lander_launched and drag_force_magnitude > self._max_drag_for_orbital_decay:
                self._events._add_if_absent('orbital_decay', time, tag='failure')

            if self.parachute_deployed and drag_force_magnitude > self._max_drag_for_parachute_failure:
                self._events._add_if_absent('broke_parachute', time)

            if not self.parachute_deployed and drag_force_magnitude/self.mission.lander_area > self._max_drag_per_area_for_burn:
                self._events._add_if_absent('burned', time, tag='failure')

        dxv  = np.zeros(6)
        dxv[0] = pos_vel[3]
        dxv[1] = pos_vel[4]
        dxv[2] = pos_vel[5]
        dxv[3] = acceleration[0]
        dxv[4] = acceleration[1]
        dxv[5] = acceleration[2]
        return dxv

    def _process_new_events(self, start_time):
        """Treats events that occurred during the last falling period.

        Parameters
        ----------
        start_time : float
            The time at the beginning of the last falling period.
        """
        history = self._events._get_history(start_time)

        for name, event in history:

            time = event[0]
            data = event[1]
            tag = event[2]

            if name == 'crashed':

                raise RuntimeError('FAILURE: You collided with planet %d at time %g s with velocity %g m/s.'
                                    % (self._planet_idx, time, data['rel_vel']))

            elif name == 'orbital_decay':

                raise RuntimeError('FAILURE: Orbital decay of the spacecraft due to air resistance at time %g s!' % time)

            elif name == 'broke_parachute':

                print('WARNING: Parachute failed due to extreme drag at time %g s!' % time)

            elif name == 'burned':

                raise RuntimeError('FAILURE: Lander module burned up due to reentry heating at time %g s!' % time)

            elif name == 'bounced':

                print('WARNING: Tried to land on planet %d at time %g s... \nBut bounced off because %g m/s is larger than escape velocity!'
                      % (self._planet_idx, time, data['rel_vel']))

            elif name == 'deployed_parachute':

                if self.verbose:
                    print('Parachute with area %g m^2 deployed at time %g s.' % (self._parachute['area'], time))

            elif name == 'activated_thruster':

                if self.verbose:
                    print('Landing engine with thrust %g N activated at time %g s.' % (self._landing_thruster['force'], time))

            elif name == 'reached_surface':

                if self.verbose:
                    print('Lander reached the surface at time %g s.' % time)

            elif name == 'landed_successfully':

                if self.verbose:
                    print('Successfully landed on planet %d at time %g s with velocity %g m/s. Well done!'
                          % (self._planet_idx, time, data['radial_vel']))
                    print('*** Achievement unlocked: Touchdown! ***')

                self._mission._landing_completed = True

                position = data['position']

                rotation = self.system._compute_single_planet_rotational_angle(self._initial_time_in_system + utils.s_to_yr(time), self._planet_idx)
                rotation -= self.system._compute_single_planet_rotational_angle(self._initial_time_in_system, self._planet_idx)
                phi = np.arctan2(position[1], position[0]) - rotation
                while phi < 0:
                    phi += 2*const.pi
                theta = np.arccos(position[2]/np.linalg.norm(position))

                self._mission._landing_site_polar_angle = theta
                self._mission._landing_site_azimuth_angle = phi

                if self.verbose:
                    print('Landing site coordinates recorded:\n  theta = %g deg\n  phi = %g deg' % (utils.rad_to_deg(theta), utils.rad_to_deg(phi)))

            else:
                raise ValueError('Untreated landing event: %s.' % name)
