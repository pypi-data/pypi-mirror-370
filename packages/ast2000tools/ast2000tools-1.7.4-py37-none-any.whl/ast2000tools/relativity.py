# -*- coding: utf-8 -*-
"""Module containing the RelativityExperiments class."""
from __future__ import division, print_function, absolute_import
from six.moves import range

import os
import itertools
import numpy as np
from copy import copy
from scipy import interpolate
from lxml import etree

import ast2000tools.constants as const
import ast2000tools.utils as utils
from ast2000tools.solar_system import SolarSystem


class RelativityExperiments(object):
    """Represents a set of experiments with relativity taking place in your solar system.

    This class is used to run various experiments with special and general relativity and observe the results.

    Parameters
    ----------
    seed : int
        The seed to use when generating random solar system and experiment properties.
    data_path : str, optional
        Specifies the path to the directory where output XML files should be stored (e.g. the MCAst data folder).
        By default, a folder called "XMLs" is created in the working directory.
    solution_path : str, optional
        Specifies the path to the directory where output solution text files should be stored.
        By default, a folder called "Solutions" is created in the working directory.
    """
    def __init__(self, seed, data_path=None, solution_path=None):

        self._system = SolarSystem(seed, data_path=data_path, has_moons=False)

        self._set_solution_path(solution_path=solution_path)
        self._set_debugging(False)
        self._set_test_mode(False)

        self._ruler_height = 0.28

    @property
    def seed(self):
        """int: The seed used to generate random solar system and experiment properties."""
        return self._system.seed

    @property
    def data_path(self):
        """str: The path to the directory where output XML files will be stored."""
        return self._system.data_path

    @property
    def solution_path(self):
        """str: The path to the directory where output solution files will be stored."""
        return self._solution_path

    @property
    def system(self):
        """SolarSystem: The randomized solar system where the experiments take place."""
        return self._system

    def crash_landing(self, planet_idx, increase_height=False, filename_1='crash_landing_frame_1.xml', filename_2='crash_landing_frame_2.xml', number_of_video_frames=1000, write_solutions=False):
        """A spaceship's failed landing attempt is observed from both the spaceship the surface of the planet.

        Generates the XML files used in Exercise 2 in Part 2A of the lecture notes.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.001 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1000, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        ### SETUP ###
        sat_color = [0,0,1]   # RGB
        planet_radius = utils.km_to_AU(self.system.radii[planet_idx])
        start_radius = planet_radius*2      # Distance from planet center when spacecraft begins to fall.
        if increase_height is False:
            end_radius = planet_radius*1.001   # Distance from planet center when the spacecraft is considered to have crashed.
        elif increase_height is True:
            end_radius = planet_radius*1.1
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                end_radius = planet_radius*(1.001+0.003*increase_height)
            else:
                end_radius = planet_radius*(1.001-0.001*increase_height)

        random_state = np.random.RandomState(self.seed + utils.get_seed('crash_landing'))

        ### Scene 1 ###
        atmos_frame = random_state.randint( int(0.6*N), int(0.7*N) )    # Pick a random frame at which to enter atmosphere/send message.
        crash_frame = random_state.randint( int(0.9*N), int(0.95*N) )    # Pick a random frame at which to crash into planet.
        cam_speed = utils.km_to_AU(random_state.uniform(0.95*const.c_km_pr_s, 0.99*const.c_km_pr_s))    # Pick a random velocity for camera/spacecraft
        cam_start_pos = [-start_radius, 0, 0]
        cam_end_pos = [-end_radius, 0, 0]
        cam_pos = np.zeros( shape=(N,3) )
        cam_pos[:crash_frame,0] = np.linspace(cam_start_pos[0], cam_end_pos[0], crash_frame)
        cam_pos[crash_frame:] += cam_end_pos
        cam_dir = np.zeros(shape=(N,3)) + np.array([1,0,0])
        cam_dir[crash_frame:] += np.array([-1,1,0])   # Changig dir_vec to [-1,1,0] after crash (looks like rocket fell).
        camera_messages = ['' for i in range(N)]
        distance_to_planet_in_sat_frame = utils.AU_to_km((cam_pos[crash_frame,0] - cam_pos[atmos_frame, 0]) * np.sqrt(1 - (cam_speed/const.c_AU_pr_s)**2))
        distance_to_planet_in_planet_frame = utils.AU_to_km((cam_pos[crash_frame,0] - cam_pos[atmos_frame,0]))

        expl_vis = np.zeros(N)
        expl_vis[crash_frame:crash_frame+10] += 1
        expl_sound = ['' for i in range(N)]
        expl_sound[crash_frame] = 'explosion'
        expl_pos = cam_pos + np.array([0, utils.km_to_AU(10), 0])
        other_objects = [['Exp0', 'explosion', expl_pos, 130, [100,0,0], None, expl_sound, expl_vis, None]]

        crash_time = (cam_end_pos[0] - cam_start_pos[0])/cam_speed * np.sqrt(1 - (cam_speed/const.c_AU_pr_s)**2)

        end_time = N/float(crash_frame+1) * crash_time
        time_array = np.linspace(0, end_time, N)
        dt_in_sat_frame = distance_to_planet_in_sat_frame*1000/utils.AU_to_km(cam_speed)


        for i in range( atmos_frame, N):
            camera_messages[i] = 'Spaceship has entered the atmosphere and sent message.\nDistance to the ground %f km in our frame of reference.\
            \nTime when entering the atmosphere: %f ms'% (distance_to_planet_in_sat_frame,crash_time*1000-dt_in_sat_frame)
        for i in range( crash_frame, N ):
            camera_messages[i] += '\n\nSpaceship has crashed....BOOM\nTime of the crash: %g ms'%(crash_time*1000)

        self._write_to_xml(time_array, cam_pos, cam_dir, other_objects=other_objects, camera_messages=camera_messages, planet_idx=planet_idx, filename=filename_1, use_obj_scaling = 0, play_speed=0.501)


        ### Scene 2 ###
        sat_speed = cam_speed##random_state.uniform(0.98*const.c_km_pr_s, 0.99*const.c_km_pr_s)*km_to_AU
        cam_pos = np.zeros( shape=(3) ) + np.array([-end_radius*1.01, 0, 0])
        sat_pos = np.zeros( shape = (N,3) )
        sat_start_pos = [-start_radius, 0, 0]
        sat_end_pos = [-end_radius, 0, 0]
        sat_pos[:crash_frame,0] = np.linspace(sat_start_pos[0], sat_end_pos[0], crash_frame)
        sat_pos[crash_frame:] += sat_end_pos
        cam_dir = [-1,0,0]
        camera_messages = ['' for i in range(N)]

        expl_vis = np.zeros(N)
        expl_vis[crash_frame:] += 1
        expl_sound = ['' for i in range(N)]
        expl_sound[crash_frame] = 'explosion'
        expl_pos = sat_end_pos * np.array([1.01,0,0]) - np.array([utils.km_to_AU(10), 0, 0])

        other_objects = [['Sat0', 'Satellite', sat_pos, 0.05, sat_color, None, None, None, None],
                         ['Exp0', 'explosion', expl_pos, 100, [100,0,0], None, expl_sound, expl_vis, None]]

        crash_time = (sat_pos[crash_frame,0] - sat_pos[0,0])/sat_speed
        end_time = N/float(crash_frame+1) * crash_time
        time_array = np.linspace(0, end_time, N)
        dt_in_planet_frame = distance_to_planet_in_planet_frame*1000/utils.AU_to_km(cam_speed)

        for i in range( atmos_frame, N ):
            camera_messages[i] = 'Spaceship has entered the atmosphere and sent message.\nDistance to ground %f km in our frame of reference.\
            \nTime when entering the atmosphere: %g ms' % (distance_to_planet_in_planet_frame,crash_time*1000 - dt_in_planet_frame)
        for i in range( crash_frame, N ):
            camera_messages[i] += '\n\nSpaceship has crashed....BOOM\nTime of the crash: %g ms'%(crash_time*1000)

        self._write_to_xml(time_array, cam_pos, cam_dir, other_objects=other_objects, camera_messages=camera_messages, planet_idx=planet_idx, filename=filename_2, use_obj_scaling = 0, play_speed=0.5002)

        if write_solutions:

            #Solution writing
            solution_name='Solutions_crash_landing.txt'
            solution_2A=self._get_new_solution_file_handle(solution_name)
            solution_2A.write('Solutions to 2A.2\n')
            solution_2A.write('\n')
            solution_2A.write('Answers for spaceship frame:\n')
            solution_2A.write('3) v = %fc\n'%(utils.AU_to_km(cam_speed)/const.c_km_pr_s))
            solution_2A.write('4) Delta s\'^2 = %f ms^2\n'%(distance_to_planet_in_sat_frame*1000/utils.AU_to_km(cam_speed))**2)
            solution_2A.write('5) Delta t = %f ms\n'%(dt_in_planet_frame))
            solution_2A.write('\n')
            solution_2A.write('Answers for planet fram:\n')
            solution_2A.write('3) v=%fc\n'%(utils.AU_to_km(cam_speed)/const.c_km_pr_s))
            solution_2A.write('4) Delta s^2 = %f ms^2\n'%((distance_to_planet_in_planet_frame*1000/utils.AU_to_km(cam_speed))**2-(distance_to_planet_in_planet_frame/const.c_km_pr_s*1000)**2))
            solution_2A.write('5) Delta t = %f ms\n'%(dt_in_sat_frame))
            solution_2A.close()


        ## BUG: Time between time[atmos_frame] and crash_time is NOT equal distance_to_planet_in_..._frame/(cam_speed*AU_to_km). fixed by using the latter alternativ

    def lightning_strikes(self, planet_idx, increase_height=False, filename_1='lightning_strikes_frame_1.xml', filename_2='lightning_strikes_frame_2.xml', field_of_view=70, number_of_video_frames=1000, write_solutions=False):
        """A spaceship is struck by a yellow and a blue lightning bolt while traveling through the atmosphere of a planet.

        Generates the XML files used in Exercise 3 in Part 2A of the lecture notes.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.01 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        field_of_view : float, optional
            The field of view of the camera, in degrees.
            Default is 70.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1000, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        low_sat_speed = [0.80, 0.84]  # Possible speed interval (in c's) of fastest and slowest spaceship.
        high_sat_speed = [0.86, 0.90]

        distance_to_events = utils.km_to_AU(2.*400)  # Events are in the middle, with the spacecrafts this far on each side.
        cam_dir = np.array([0,0,-1])
        planet_radius = utils.km_to_AU(self.system.radii[planet_idx])  # in AU


        if increase_height is False:
            event_radius = planet_radius*1.01 # Radius away from planets at which the spaceships fly, and events are happening
        elif increase_height is True:
            event_radius = planet_radius*1.1
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                event_radius = planet_radius*(1.005+0.005*increase_height)
            else:
                event_radius = planet_radius*(1.005-0.005*increase_height)

        random_seed = self.seed + utils.get_seed('lightning_strikes')
        random_state = np.random.RandomState(random_seed)

        v_cam_planframe = random_state.uniform(low_sat_speed[0], low_sat_speed[1]) #* const.c_AU_pr_s
        v_friend_planframe = random_state.uniform(high_sat_speed[0], high_sat_speed[1]) #* const.c_AU_pr_s


        v_friend_camframe = self._velocity_transformation(v_cam_planframe, v_friend_planframe)

        v_cam_planframe = v_cam_planframe * const.c_AU_pr_s
        v_friend_planframe = v_friend_planframe * const.c_AU_pr_s
        v_friend_camframe = v_friend_camframe * const.c_AU_pr_s


        if self._debug: print('Our velocity in planet frame = %gc\nFriend velocity in planet frame = %gc\nFriend velocity in our frame = %gc' % (v_cam_planframe, v_friend_planframe, v_friend_camframe))



        sat_movement_length_planframe = utils.km_to_AU(2000)  # Total moment of fastest spacecraft in relation to planet.
        end_time_planframe = sat_movement_length_planframe/(max([v_cam_planframe, v_friend_planframe]))
        time_array_planframe = np.linspace(0, end_time_planframe, N)  # Own-time of planet frame.

        # 1D (z-axis in 3D)
        cam_pos_1D_camframe = np.zeros(N)
        friend_pos_1D_camframe = np.linspace(0, end_time_planframe*v_friend_camframe, N)
        cam_pos_1D_planframe = np.linspace(0, end_time_planframe*v_cam_planframe, N)
        friend_pos_1D_planframe = np.linspace(0, end_time_planframe*v_friend_planframe, N)

        end_time_camframe, _ = self._lorentz_transform(time_array_planframe[-1], cam_pos_1D_planframe[-1], v_cam_planframe)   # Lorentz transforming end position of cam to get end time of cam.
        end_time_friendframe, _ = self._lorentz_transform(time_array_planframe[-1], cam_pos_1D_planframe[-1], v_friend_planframe)   # Lorentz transforming end position of cam to get end time of cam.
        time_array_camframe = np.linspace(0, end_time_camframe, N)
        time_array_friendframe = np.linspace(0, end_time_friendframe, N)

        planet_pos_1D_camframe = np.linspace(0, -end_time_planframe*v_cam_planframe, N)



        # 3D
        cam_pos = np.zeros( shape = (N,3) )
        cam_pos[:,2] += distance_to_events
        friend_pos_camframe = np.zeros( shape = (N,3) )
        friend_pos_camframe[:,1] = friend_pos_1D_camframe
        friend_pos_camframe[:,2] -= distance_to_events
        cam_pos_camframe = np.zeros( shape = (N,3) )
        cam_pos_camframe[:,1] = cam_pos_1D_camframe
        #cam_pos_camframe[:,2] -= distance_to_events
        planet_pos_camframe = np.zeros( shape=(N,3) )
        planet_pos_camframe[:,0] += event_radius   # Moving planet away from events.
        planet_pos_camframe[:,1] = planet_pos_1D_camframe

        # Events
        ball1_pos_camframe = np.zeros( shape = (N,3) )
        ball1_visibility = np.zeros( shape = (N) )
        # ball1_visibility[100:110] += 1

        ### Simultaneous events in planet frame ###
        random_state.seed(random_seed)  # seed_for_random is shared across both users.
        events_index_planframe = random_state.randint( N//4, (3*N)//5 )  # Same index for both events.
        events_time_planframe = time_array_planframe[events_index_planframe]
        avg_sat_pos_at_event = (cam_pos_1D_planframe[events_index_planframe] + friend_pos_1D_planframe[events_index_planframe]) / 2.0
        event1_pos_1D_planframe = avg_sat_pos_at_event + utils.km_to_AU(110)
        event2_pos_1D_planframe = cam_pos_1D_planframe[events_index_planframe]# - 110*km_to_AU   # Events happening at +/- 20 km from midway between spacecrafts.
        # Lorentz transforming events to cam and friend frame:
        event1_time_camframe, event1_pos_1D_camframe = self._lorentz_transform(events_time_planframe, event1_pos_1D_planframe, v_cam_planframe)
        event2_time_camframe, event2_pos_1D_camframe = self._lorentz_transform(events_time_planframe, event2_pos_1D_planframe, v_cam_planframe)
        event1_time_friendframe, event1_pos_1D_friendframe = self._lorentz_transform(events_time_planframe, event1_pos_1D_planframe, v_friend_planframe)
        event2_time_friendframe, event2_pos_1D_friendframe = self._lorentz_transform(events_time_planframe, event2_pos_1D_planframe, v_friend_planframe)
        # Finding indexes for events in cam and friend frame
        event1_index_camframe = (np.abs(event1_time_camframe - time_array_planframe)).argmin()
        event2_index_camframe = (np.abs(event2_time_camframe - time_array_planframe)).argmin()
        event1_visibility = np.zeros( shape = (N) )
        event2_visibility = np.zeros( shape = (N) )
        event1_visibility[event1_index_camframe : event1_index_camframe+N//32] += 1
        event2_visibility[event2_index_camframe : event2_index_camframe+N//32] += 1
        camera_messages = ['' for i in range(N)]
        #event1_messages = ['' for i in range(N)]
        event2_messages = ['' for i in range(N)]
        #event1_messages[event1_index_camframe : event1_index_camframe+N//32] = ['\n\nPosition of event 1 = %fkm and %fs' % (event1_pos_1D_camframe*AU_to_km, event1_time_camframe)]*(N//32)
        #event1_messages[event1_index_camframe : event1_index_camframe+N//32] = ['\n\nPosition of event X = %fkm' % (event1_pos_1D_camframe*AU_to_km)]*(N//32)
        event2_messages[event2_index_camframe : event2_index_camframe+N//32] = ['\n\nEvent B']*(N//32)
        event1_pos_camframe = np.zeros( shape=(N,3) )
        event2_pos_camframe = np.zeros( shape=(N,3) )
        event1_pos_camframe[:,1] = event1_pos_1D_camframe
        event2_pos_camframe[:,1] = event2_pos_1D_camframe


        ### Couple of other events ###
        event3_index_planframe = random_state.randint( N//8, N//4 )
        event4_index_planframe = 0#random_state.randint( (3*N)//4, (7*N)//8 )
        #event3_time_planframe = time_array_planframe[event3_index_planframe]
        event3_time_camframe = event1_time_camframe
        event3_index_camframe = event1_index_camframe
        event3_pos_1D_camframe = cam_pos_1D_camframe[event3_index_camframe]
        event3_time_planframe, event3_pos_1D_planframe = self._lorentz_transform(event3_time_camframe, event3_pos_1D_camframe, -v_cam_planframe)
        event3_index_planframe=(np.abs(event3_time_planframe - time_array_planframe)).argmin()
        #dff=(time_array_planframe-event3_time_planframe)**2
        #wdff=np.where(dff == min(dff))[0]
        #event3_index_planframe = wdff[0]
        event4_time_planframe = time_array_planframe[event4_index_planframe]
        #avg_sat_pos_at_event3 = (cam_pos_1D_planframe[event3_index_planframe] + friend_pos_1D_planframe[event3_index_planframe]) / 2.0
        avg_sat_pos_at_event4 = (cam_pos_1D_planframe[event4_index_planframe] + friend_pos_1D_planframe[event4_index_planframe]) / 2.0
        #event3_pos_1D_planframe = avg_sat_pos_at_event3 - 70*km_to_AU
        event4_pos_1D_planframe = 0#avg_sat_pos_at_event4 + 90*km_to_AU
        #event3_time_camframe, event3_pos_1D_camframe = self._lorentz_transform(event3_time_planframe, event3_pos_1D_planframe, v_cam_planframe)
        event4_time_camframe, event4_pos_1D_camframe = self._lorentz_transform(event4_time_planframe, event4_pos_1D_planframe, v_cam_planframe)
        #event3_index_camframe = (np.abs(event3_time_camframe - time_array_planframe)).argmin()
        event4_index_camframe = (np.abs(event4_time_camframe - time_array_planframe)).argmin()
        event3_visibility = np.zeros( shape = (N) )
        event4_visibility = np.zeros( shape = (N) )
        event3_visibility[event3_index_camframe : event3_index_camframe+N//32] += 1
        #event4_visibility[event4_index_camframe : event4_index_camframe+N//32] += 1
        event3_messages = ['' for i in range(N)]
        event4_messages = ['' for i in range(N)]
        event3_messages[event3_index_camframe : event3_index_camframe+N//32] = ['\n\nEvent Y']*(N//32)
        #event4_messages[event4_index_camframe : event4_index_camframe+N//32] = ['\nPosition of event 0 = %fkm' % (event4_pos_1D_camframe*AU_to_km)]*(N//32)
        event3_pos_camframe = np.zeros( shape=(N,3) )
        event4_pos_camframe = np.zeros( shape=(N,3) )
        event3_pos_camframe[:,1] = event3_pos_1D_camframe
        event4_pos_camframe[:,1] = event4_pos_1D_camframe

        camera_messages = [ (camera_messages[i] + 'Velocity of planet relative to our spacecraft frame = %fc' %(-v_cam_planframe/const.c_AU_pr_s)) for i in range(N)]

        for i in range(event3_index_camframe,N):
            camera_messages[i] += '\nTime of event Y = %f ms' % (time_array_planframe[event3_index_camframe]*1000)
            if i>=event2_index_camframe:
                camera_messages[i] += '\nTime of event B = %f ms' % (time_array_planframe[event2_index_camframe]*1000)

        # Messages, sounds, and other.
        ruler_length = utils.AU_to_km(self._get_ruler_length(distance_to_events, field_of_view=field_of_view))
        #ruler = [-ruler_length/2.0, ruler_length/2.0, 20, 'km']  #TODO: Are we sure FOV is always pi/2 (90 degrees)?
        # Note: Ruler is only accurate for friends spaceship, and not for the events in between.
        ruler = [-ruler_length/5.,ruler_length*4./5.,20,'km', utils.AU_to_km(distance_to_events)]
        cam_pos[:,1] = utils.km_to_AU(ruler_length)*3./10.
        planet_pos_camframe[:,1] +=  utils.km_to_AU(ruler_length)*3./10.#*np.sqrt(1.-(v_cam_planframe/const.c_AU_pr_s)**2)/2.

        other_objects = [['Friend', 'Satellite', cam_pos_camframe, 0.08, [1,1,1], None, None, None, [0,-1,0]],
                         ['Ball2', 'Sphere01', event2_pos_camframe, 5, [250,250,250], None, None, event2_visibility, None],
                         ['Ball3', 'Sphere01', event3_pos_camframe, 5, [250,250,250], None, None, event3_visibility, None],
                         ['Ball4', 'Sphere01', event4_pos_camframe, 5, [250,250,250], None, None, event4_visibility, None],
                         ['Event2', 'explosion', event2_pos_camframe, 800, [0,1,1], event2_messages, None, event2_visibility, None],
                         ['Event3', 'explosion', event3_pos_camframe, 800, [1,1,0], event3_messages, None, event3_visibility, None],
                         ['Event4', 'explosion', event4_pos_camframe, 800, [0,1,0], None, None, event4_visibility, None]]
        '''
        other_objects = [['Friend', 'Satellite', cam_pos_camframe, 0.08, [1,1,1], None, None, None, [0,-1,0]],
                         ['Ball1', 'Sphere01', event1_pos_camframe, 5, [250,250,250], None, None, event1_visibility, None],
                         ['Ball2', 'Sphere01', event2_pos_camframe, 5, [250,250,250], None, None, event2_visibility, None],
                         ['Ball3', 'Sphere01', event3_pos_camframe, 5, [250,250,250], None, None, event3_visibility, None],
                         ['Ball4', 'Sphere01', event4_pos_camframe, 5, [250,250,250], None, None, event4_visibility, None],
                         ['Event1', 'explosion', event1_pos_camframe, 800, [1,0,1], event1_messages, None, event1_visibility, None],
                         ['Event2', 'explosion', event2_pos_camframe, 800, [0,1,1], event2_messages, None, event2_visibility, None],
                         ['Event3', 'explosion', event3_pos_camframe, 800, [1,1,0], event3_messages, None, event3_visibility, None],
                         ['Event4', 'explosion', event4_pos_camframe, 800, [0,1,0], event4_messages, None, event4_visibility, None]]
        '''
        # We can't use the self._write_to_xml, because it only works for one of the two users. setting up a new solar system.

        self._write_to_xml(time_array_planframe, cam_pos, cam_dir, planet_pos_camframe, ruler=ruler, other_objects=other_objects, camera_messages=camera_messages, planet_idx=planet_idx, up_vec=[-1,0,0], filename=filename_1, play_speed=0.501, field_of_view=field_of_view, use_obj_scaling = 1)

        if write_solutions:

            #Solution writing
            solution_name='Solutions_part2A_3.txt'
            solution_2A=self._get_new_solution_file_handle(solution_name)
            solution_2A.write('Solutions to 2A.3\n')
            solution_2A.write('\n')
            solution_2A.write('Answers for spaceship frame:\n')
            solution_2A.write('1a) Check the video for time, x\'(B) = 0 km , x\'(Y) = 0 km\n')
            #solution_2A.write('3. No numerical answers\n')
            #solution_2A.write('4.\n')
            #solution_2A.write('a) No numerical answer\n')
            #solution_2A.write('b) No numerical answer\n')
            solution_2A.write('1b/2d/3d) Delta t\' = %f ms\n' %(abs(time_array_planframe[event3_index_camframe]*1000-time_array_planframe[event2_index_camframe]*1000)))
            #solution_2A.write('5. See the other video\n')
            #solution_2A.write('\n')

        ### PLANET FRAME ###

        cam_pos_planframe = np.zeros( shape = (N,3) )
        cam_pos_planframe[:,1] = cam_pos_1D_planframe

        event1_pos_planframe = np.zeros( shape = (N,3) )
        event2_pos_planframe = np.zeros( shape = (N,3) )
        event3_pos_planframe = np.zeros( shape = (N,3) )
        event4_pos_planframe = np.zeros( shape = (N,3) )
        event1_pos_planframe[:,1] = event1_pos_1D_planframe
        event2_pos_planframe[:,1] = event2_pos_1D_planframe
        event3_pos_planframe[:,1] = event3_pos_1D_planframe
        event4_pos_planframe[:,1] = event4_pos_1D_planframe



        event1_visibility = np.zeros( shape = (N) )
        event2_visibility = np.zeros( shape = (N) )
        event1_visibility[events_index_planframe : events_index_planframe+N//32] += 1
        event2_visibility[events_index_planframe : events_index_planframe+N//32] += 1
        camera_messages = ['' for i in range(N)]
        event1_messages = ['' for i in range(N)]
        event2_messages = ['' for i in range(N)]
        event1_messages[events_index_planframe : events_index_planframe+N//32] = ['\n\nPosition of event X = %fkm' % (utils.AU_to_km(event1_pos_1D_planframe))]*(N//32)
        event2_messages[events_index_planframe : events_index_planframe+N//32] = ['\n\nEvent B']*(N//32)
        event3_visibility = np.zeros( shape = (N) )
        event4_visibility = np.zeros( shape = (N) )
        event3_visibility[event3_index_planframe : event3_index_planframe+N//32] += 1
        #event4_visibility[event4_index_planframe : event4_index_planframe+N//32] += 1
        event3_messages = ['' for i in range(N)]
        event4_messages = ['' for i in range(N)]
        event3_messages[event3_index_planframe : event3_index_planframe+N//32] = ['\nEvent Y']*(N//32)
        #event4_messages[event4_index_planframe : event4_index_planframe+N//32] = ['\nPosition of event 0 = %fkm' % (event4_pos_1D_planframe*AU_to_km)]*(N//32)

        other_objects = [['Friend', 'Satellite', cam_pos_planframe, 0.08, [1,1,1], None, None, None, [0,-1,0]],
                    ['Ball2', 'Sphere01', event2_pos_planframe, 5, [200,200,200], None, None, event2_visibility, None],
                    ['Ball3', 'Sphere01', event3_pos_planframe, 5, [200,200,200], None, None, event3_visibility, None],
                    ['Ball4', 'Sphere01', event4_pos_planframe, 5, [200,200,200], None, None, event4_visibility, None],
                    ['Event2', 'explosion', event2_pos_planframe, 800, [0,1,1], event2_messages, None, event2_visibility, None],
                    ['Event3', 'explosion', event3_pos_planframe, 800, [1,1,0], event3_messages, None, event3_visibility, None],
                    ['Event4', 'explosion', event4_pos_planframe, 800, [0,1,0], None, None, event4_visibility, None]]

        '''
        other_objects = [['Friend', 'Satellite', cam_pos_planframe, 0.08, [1,1,1], None, None, None, [0,-1,0]],
                         ['Ball1', 'Sphere01', event1_pos_planframe, 5, [200,200,200], None, None, event1_visibility, None],
                         ['Ball2', 'Sphere01', event2_pos_planframe, 5, [200,200,200], None, None, event2_visibility, None],
                         ['Ball3', 'Sphere01', event3_pos_planframe, 5, [200,200,200], None, None, event3_visibility, None],
                         ['Ball4', 'Sphere01', event4_pos_planframe, 5, [200,200,200], None, None, event4_visibility, None],
                         ['Event1', 'explosion', event1_pos_planframe, 800, [1,0,1], event1_messages, None, event1_visibility, None],
                         ['Event2', 'explosion', event2_pos_planframe, 800, [0,1,1], event2_messages, None, event2_visibility, None],
                         ['Event3', 'explosion', event3_pos_planframe, 800, [1,1,0], event3_messages, None, event3_visibility, None],
                         ['Event4', 'explosion', event4_pos_planframe, 800, [0,1,0], event4_messages, None, event4_visibility, None]]

        '''

        ruler_length = utils.AU_to_km(self._get_ruler_length(distance_to_events, field_of_view=field_of_view))
        ruler = [-ruler_length/5., ruler_length*4./5., 20, 'km', utils.AU_to_km(distance_to_events)]  #TODO: Are we sure FOV is always pi/2 (90 degrees)?
        cam_pos[:,1] = utils.km_to_AU(ruler_length)*3./10.

        # Note: Ruler is only accurate for friends spaceship, and not for the events in between.
        planet_pos_camframe[:,1]=0
        camera_messages = [ (camera_messages[i] + 'Velocity of spacecraft relative to planet frame = %fc' %(v_cam_planframe/const.c_AU_pr_s)) for i in range(N) ]

        for i in range(event3_index_planframe,N):
            camera_messages[i] += '\nTime of event Y = %f ms' % (time_array_planframe[event3_index_planframe]*1000)
            if i>=events_index_planframe:
                camera_messages[i] += '\nTime of event B = %f ms' % (time_array_planframe[events_index_planframe]*1000)

        self._write_to_xml(time_array_planframe, cam_pos, cam_dir, planet_pos_camframe, ruler=ruler, other_objects=other_objects, camera_messages=camera_messages, planet_idx=planet_idx, up_vec=[-1,0,0], filename=filename_2, play_speed=0.501, field_of_view=field_of_view)

        if write_solutions:
            #Solution writing
            solution_2A.write('Answers for planet frame:\n')
            solution_2A.write('1a) Check the video for time, x(B) = %f km , x(Y) = %f km\n' %(abs(time_array_planframe[event3_index_planframe]*1000)*v_cam_planframe/const.c_AU_pr_s*3e2,abs(time_array_planframe[events_index_planframe]*1000*v_cam_planframe/const.c_AU_pr_s*3e2)))
            #solution_2A.write('2. Check the video\n')
            #solution_2A.write('3. No numerical answers\n')
            #solution_2A.write('4.\n')
            #solution_2A.write('a) No numerical answer\n')
            #solution_2A.write('b) No numerical answer\n')
            solution_2A.write('1b/2d/3d) Delta t = %f ms\n' %(abs(time_array_planframe[event3_index_planframe]*1000-time_array_planframe[events_index_planframe]*1000)))
            #solution_2A.write('5. See the other video\n')
            solution_2A.close()

    def spaceship_duel(self, planet_idx, increase_height=False, filename_1='spaceship_duel_frame_1.xml', filename_2='spaceship_duel_frame_2.xml', number_of_video_frames=400, write_solutions=False):
        """Two spaceships are moving with equal speed relative to a planet, firing lasers at each other and exploding simultaneously in their frame of reference.

        Generates the XML files used in Exercise 4 in Part 2A of the lecture notes and Exercise 1 in Part 8 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.02 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
            Default is "spaceship_duel_frame_1.xml".
        filename_2 : str, optional
            The filename to use for frame of reference 2.
            Default is "spaceship_duel_frame_2.xml".
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 400, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        factor=0.4                                       # Scaling factor for the distance and spaceships in the second video
        standard_height_factor = 1.02                    # Number of planet radiuses for the scenes to take place
        increase_height_factor     = 1.1                 # Same, but for the safe height
        spaceship_distance = utils.km_to_AU(1200.)     # Distance between spaceships     [AU]
        cam_dist_s1 = utils.km_to_AU(650)              # Camera distance from axis of movement, scene 1 [AU]
        cam_dist_s2 = utils.km_to_AU(4000)*factor      # Camera distance from axis of movement, scene 2 [AU]
        ticks_s1 = 14                                    # Number of ruler ticks scene 1
        ticks_s2 = 14                                    # Number of ruler ticks scene 2
        moveback_dist = utils.km_to_AU(-300)/factor    # Distance to move all objects back in scene 2 [AU]
        print_positions = False                          # Print object positions
        ref_frame_movement_dist = 2000                   # Referance frame movement distance [km]!

        random_state = np.random.RandomState(self.seed + utils.get_seed('spaceship_duel'))

        ref_frame_speed_int = random_state.randint(570, 620)                                     # Original random_state.randint(870,920)
        ref_frame_speed = ref_frame_speed_int*const.c_AU_pr_s/1000.0
        ref_frame_movement = utils.km_to_AU(np.linspace(-ref_frame_movement_dist/2, ref_frame_movement_dist/2, N))                   # Movement of the reference frame [AU]


        if increase_height is False:
            events_radius = utils.km_to_AU(self.system.radii[planet_idx])*standard_height_factor                     # Distance from planet center     [AU]
        elif increase_height is True:
            events_radius = utils.km_to_AU(self.system.radii[planet_idx])*increase_height_factor
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                events_radius = utils.km_to_AU(self.system.radii[planet_idx])*(standard_height_factor + 0.01*increase_height)
            else:
                events_radius = utils.km_to_AU(self.system.radii[planet_idx])*(standard_height_factor - 0.02*increase_height)



        dist_from_star = np.hypot(self.system.initial_positions[0, planet_idx], self.system.initial_positions[1, planet_idx]) # Planet distance from star       [AU]
        #planet_pos = np.array([0, 0, 0])                                  # Planet stationary on x axis     [AU]


        # 1D Position arrays
        rocket1_pos_1D = np.zeros(N) - spaceship_distance/2.0
        rocket2_pos_1D = np.zeros(N) + spaceship_distance/2.0
        cam_pos_1D = np.zeros(N)
        laser1_pos_1D = np.zeros(N)
        laser2_pos_1D = np.zeros(N)

        end_time = (ref_frame_movement[-1] - ref_frame_movement[0])/(ref_frame_speed)
        time_array = np.linspace(0, end_time, N)
        dt = time_array[1] - time_array[0]

        # Lasers
        dx = utils.km_to_AU((time_array[-1] - time_array[-2])*const.c_km_pr_s)  # Laser distance in one timestep
        laser1_pos_1D[0] = rocket1_pos_1D[0]
        laser2_pos_1D[0] = rocket2_pos_1D[0]
        for i in range(N-1):
            # Check if lasers have passed the rockets
            if laser1_pos_1D[i] > rocket2_pos_1D[i] or laser2_pos_1D[i] < rocket1_pos_1D[i]:
                laser1_pos_1D[i:] = laser1_pos_1D[i] # Make sure lasers stay where they hit
                laser2_pos_1D[i:] = laser2_pos_1D[i] # Stays where it hits
                expl_index = i+1                # Save index for explosions
                lasers_visible = np.ones(N)     # Array for laser visibility
                lasers_visible[expl_index:] = 0 # Lasers invisible after they hit
                ball3_visible = np.copy(lasers_visible)
                ball3_visible[10:] = 0
                ball4_visible = np.copy(lasers_visible)
                ball4_visible[10:] = 0
                explosions_visible = np.copy(lasers_visible)
                # Explosions visible when the ships and lasers dissapear
                explosions_visible = 1 - explosions_visible
                break
            else: # No crash yet, continue forwarding positions
                laser1_pos_1D[i+1] = laser1_pos_1D[i] + dx # One step to the right
                laser2_pos_1D[i+1] = laser2_pos_1D[i] - dx # One step to the left

        # 3D. Initialize 3D arrays.
        cam_pos = np.zeros( shape=(N,3) )
        rocket1_pos = np.zeros( shape=(N,3) )
        rocket2_pos = np.zeros( shape=(N,3) )
        laser1_pos = np.zeros( shape=(N,3))
        laser2_pos = np.zeros( shape = (N,3))

        # Making all objects move in the reference frame (which moves in the z direction)
        cam_pos[:,2] = cam_pos_1D               + ref_frame_movement
        rocket1_pos[:,2] = rocket1_pos_1D       + ref_frame_movement
        rocket2_pos[:,2] = rocket2_pos_1D       + ref_frame_movement
        laser1_pos[:,2]   = laser1_pos_1D        + ref_frame_movement
        laser2_pos[:,2]  = laser2_pos_1D         + ref_frame_movement

        # Moving lasers back a little so it looks better
        # laser1_pos[:,2] -= 50*km_to_AU
        # laser2_pos[:,2] -= 50*km_to_AU

        # Translating every position to outside the planet (negtive x direction)
        cam_pos[:,0] -= events_radius
        rocket1_pos[:,0] -= events_radius
        rocket2_pos[:,0] -= events_radius
        laser1_pos[:,0] -= events_radius
        laser2_pos[:,0] -= events_radius
        middle_observer = np.zeros_like(rocket1_pos)
        middle_observer[:,0] = rocket1_pos[:,0]
        middle_observer[:,2] = (rocket2_pos[:,2]+rocket1_pos[:,2])/2

        # Move lasers outside spaceship towards cam by a couple of kilometers
        laser1_pos[:,1] -= utils.km_to_AU(10)
        laser2_pos[:,1] -= utils.km_to_AU(10)

        # Camera position and orientation
        cam_pos[:,1] -= cam_dist_s1 # Moving camera to the side of the events.
        cam_dir = [0,1,0]
        up_vec = [-1,0,0]

        if print_positions:
            sat1_msg_list = ['x = 0 km' for i in range(N)]
            sat2_msg_list = ['x = %.2f km'%(utils.AU_to_km(spaceship_distance)) for i in range(N)]

            l1_msg_list = ['x = %.3fkm'%(utils.AU_to_km(laser1_pos[i,2]-laser1_pos[0,2]-(ref_frame_movement[i] - ref_frame_movement[0]))) for i in range(N)]
            l2_msg_list = ['x = %.3fkm'%(utils.AU_to_km(laser2_pos[i,2]-laser1_pos[0,2]-(ref_frame_movement[i] - ref_frame_movement[0]))) for i in range(N)]

        else:
            sat1_msg_list = None
            sat2_msg_list = None

            l1_msg_list = None
            l2_msg_list = None

            ball3_pos_s1 = np.copy(rocket1_pos)
            ball3_pos_s1[0:9,2] =  ball3_pos_s1[0:9,2]# + 12./AU_to_km
            #ball3_pos_s1[:,:]=0
            ball4_pos_s1 = np.copy(rocket2_pos)
            #ball4_pos_s1[0:9,2] =  ball4_pos_s1[0,2]
            ball3_pos_s1[:,1] -= utils.km_to_AU(2)
            ball4_pos_s1[:,1] -= utils.km_to_AU(2)

            other_objects = [self._object_list('lsr1', 'Laser', laser1_pos, 4, [1,1,0], visible = lasers_visible, msg_list = l1_msg_list),
                             self._object_list('lsr1', 'Laser', laser2_pos, 4, [1,0,0], visible = lasers_visible, msg_list = l2_msg_list),
                             self._object_list('rocket1', 'Satellite', rocket1_pos, 0.1, [1,1,1], visible = lasers_visible, msg_list = sat1_msg_list),
                             self._object_list('rocket2', 'Satellite', rocket2_pos, 0.1, [1,1,1], visible = lasers_visible, msg_list = sat2_msg_list, orient = [0,0,1]),
                             self._object_list('middle_observer', 'Sphere01', middle_observer, 20, [1,1,1], visible = [1]*N,msg_list=['\n\nDeath Star']*len(lasers_visible)),
                             self._object_list('boom1', 'explosion', rocket1_pos, 1000, [1,0.6,0], visible = explosions_visible, msg_list = ['\n\nEvent C' if i >= expl_index else '' for i in range(N)]),
                             self._object_list('boom2', 'explosion', rocket2_pos, 1000, [1,0.6,0], visible = explosions_visible, msg_list = ['\n\nEvent D' if i >= expl_index else '' for i in range(N)]),
                             self._object_list('ball1', 'Sphere01', rocket1_pos, 5, [255,255,255], visible = explosions_visible),
                             self._object_list('ball2', 'Sphere01', rocket2_pos, 5, [255,255,255], visible = explosions_visible),
                             self._object_list('ball3', 'Sphere01', ball3_pos_s1, 5, [255,255,255], visible = ball3_visible, msg_list = ['\n\nEvent A' if i < 15 else '' for i in range(N)]),
                             self._object_list('ball4', 'Sphere01', ball4_pos_s1, 5, [255,255,255], visible = ball3_visible, msg_list = ['\n\nEvent B' if i < 15 else '' for i in range(N)])]


        ruler_length = utils.AU_to_km(self._get_ruler_length(cam_dist_s1))

        ruler_start = -(ruler_length-utils.AU_to_km(spaceship_distance))/2.
        ruler_end = -ruler_start+utils.AU_to_km(spaceship_distance)

        dltax=abs(ruler_start)/4.
        fct=np.rint(ruler_length/dltax)
        ruler_end = ruler_start+dltax*fct

        rulerUnit = 'km'
        ruler_s1 = [ruler_start, ruler_end, ticks_s1, rulerUnit, utils.AU_to_km(cam_dist_s1), self._ruler_height]

        planet_pos = np.array([0, 0, -spaceship_distance/2.])

        global_messages_s1 = ['\nThe planet is moving relative to the spacecrafts with v = %.3fc' % (ref_frame_speed/const.c_AU_pr_s) for i in range(N)]

        for i in range(N):
            global_messages_s1[i] += '\nPosition of event A: %f km. Time of event A: %f ms' %(0,0)
            global_messages_s1[i] += '\nPosition of event B: %f km. Time of event B: %f ms' %(utils.AU_to_km(spaceship_distance),0)

        for i in range(N):
            if explosions_visible[i]==1:
                global_messages_s1[i] += '\nPosition of event C: %f km. Time of event C: %f ms' %(0,time_array[expl_index]*1000)
                global_messages_s1[i] += '\nPosition of event D: %f km. Time of event D: %f ms' %(utils.AU_to_km(spaceship_distance),time_array[expl_index]*1000)

        self._write_to_xml(time_array, cam_pos, cam_dir, planet_pos, other_objects, ruler = ruler_s1, play_speed=0.501, cheat_light_speed = True,

                             planet_idx=planet_idx, up_vec=up_vec, laser_scale = 0.2, filename = filename_1, camera_messages = global_messages_s1)

        rocket1_s2_func = self._ref_sys_interpolate_func(time_array, rocket1_pos_1D, -ref_frame_speed)
        rocket2_s2_func = self._ref_sys_interpolate_func(time_array, rocket2_pos_1D, -ref_frame_speed)

        laser1_s2_func = self._ref_sys_interpolate_func(time_array, laser1_pos_1D, -ref_frame_speed)
        laser2_s2_func = self._ref_sys_interpolate_func(time_array, laser2_pos_1D, -ref_frame_speed)

        t1 = self._lorentz_transform(time_array, rocket1_pos_1D, -ref_frame_speed)[0]
        gamma = 1/np.sqrt(1 - ref_frame_speed**2 / const.c_AU_pr_s**2)
        startTime = 0
        endTime = t1[-1] - t1[0]
        endTime *= 1.5 # Makes sure the first laser has time to hit the second ship, if this isnt done it doesnt have time to reach
        times_s2 = np.linspace(startTime, endTime, N)
        t2 = self._lorentz_transform(time_array, rocket2_pos_1D, -ref_frame_speed)[0]

        rocket1_pos_1D_s2 = rocket1_s2_func(times_s2)
        rocket2_pos_1D_s2 = rocket2_s2_func(times_s2)
        laser1_pos_1D_s2 = laser1_s2_func(times_s2)
        laser2_pos_1D_s2 = laser2_s2_func(times_s2)
        time_diff_ticks = (t2[0] - t1[0]) # Simultaneous events in rocket frame is separated by this time in the planet frame of reference
        # Light is emitted from rocket 1 first.
        dist_between_rockets_s2 = rocket2_pos_1D_s2[0] - rocket1_pos_1D_s2[0]
        dist_movement_s2 = ref_frame_speed * endTime

        # Camera stands still on planet, ref sys moves past. rockets separated on each side of ref sys movement.
        # Laser emmission events happen with correct time spacing.
        ref_frame_movement_s2 = np.linspace(-dist_movement_s2/2, dist_movement_s2/2, N)

        # Make 3D Arrays for scene 2
        rocket1_s2 = np.zeros(shape = (N,3))
        rocket2_s2 = np.zeros(shape = (N,3))
        cam_pos_s2 = np.zeros(shape = (N,3))
        pos_of_ref_frame = np.zeros(shape = (N,3))

        # Translate in x-dir, movement along y axis. y = 0.
        rocket1_s2[:,0] -= events_radius
        rocket2_s2[:,0] -= events_radius
        cam_pos_s2[:,0] -= events_radius

        cam_pos_s2[:,1] -= cam_dist_s2

        rocket1_s2[:,2] = ref_frame_movement_s2 - dist_between_rockets_s2/2
        rocket2_s2[:,2] = ref_frame_movement_s2 + dist_between_rockets_s2/2

        pos_of_ref_frame[:] = .5*rocket1_s2 + .5*rocket2_s2 # Position between the ships (equally weighted lin.comb.)

        cam_dir_s2 = pos_of_ref_frame - cam_pos_s2 # Focus on the point between the spaceships
        cam_dir_s2[:] = cam_dir_s2[int(N/2),:]

        # MAKE LASERS
        laser1_s2 = np.zeros(shape = (N,3))
        laser2_s2 = np.zeros(shape = (N,3))
        laser1_s2[0] = rocket1_s2[0]
        laser2_s2[0] = rocket2_s2[0]

        dt = times_s2[1] - times_s2[0]
        dx = const.c_AU_pr_s*dt

        # Find index of laser emmission from second spaceship
        index_laser2_emission = np.argmin(np.abs(times_s2 - time_diff_ticks))


        # Make visibility arrays
        rocket1_visible = np.ones(N)
        rocket2_visible = np.ones(N)
        laser2_visible = np.zeros(N)

        # Make sure x components are correct, somehow i got wrong values
        laser1_s2[:,0] = rocket2_s2[:,0]
        laser2_s2[:,0] = rocket2_s2[:,0]

        #Make sure second laser starts at second rocket
        laser2_s2[:,2] = rocket2_s2[:,2]

        for i in range(N-1):
            laser1_s2[i+1,2] = laser1_s2[i,2] + dx
            if laser1_s2[i+1,2] > rocket2_s2[i+1,2]:
                rocket2_visible[i+1] = 0

            if i >= index_laser2_emission:
                laser2_s2[i+1,2] = laser2_s2[i,2] - dx
                laser2_visible[i+1] = 1

            if laser2_s2[i+1,2] < rocket1_s2[i+1,2]:
                rocket1_visible[i+1] = 0

        laser2_visible = laser2_visible - (1 - rocket1_visible) # Visible only from emission to when the rocket it hits explodes

        ship_scale_s2 = 0.6
        lasers_scale_s2 = 25

        if print_positions:
            r1_s2_msg = ['x = %.2f km'%(utils.AU_to_km(rocket1_s2[i,2] - rocket1_s2[0,2])) for i in range(N)]
            r2_s2_msg = ['x = %.2f km'%(utils.AU_to_km(rocket2_s2[i,2] - rocket1_s2[0,2])) for i in range(N)]

        else:
            r1_s2_msg = None
            r2_s2_msg = None

        l1_s2_msg = None
        l2_s2_msg = None

        laser1_s2[:,1] -= utils.km_to_AU(20)
        laser2_s2[:,1] -= utils.km_to_AU(20)

        # Move all objects linearly back so they start on ruler 0
        rocket1_s2[:,2] -= moveback_dist
        rocket2_s2[:,2] -= moveback_dist
        laser1_s2[:,2] -= moveback_dist
        laser2_s2[:,2] -= moveback_dist

        ball3_visible_s2 = np.copy(rocket2_visible)
        ball3_visible_s2[10:]=0
        ball4_visible_s2 = np.copy(laser2_visible)
        #ball4_visible_s2[index_laser2_emission+10:]=0
        ball3_pos_s2 = np.copy(rocket1_s2)
        ball4_pos_s2 = np.copy(rocket2_s2)
        ball3_pos_s2[:,1] -= utils.km_to_AU(2)
        ball4_pos_s2[:,1] -= utils.km_to_AU(2)

        middle_observer[:,0] = rocket1_s2[:,0]
        middle_observer[:,2] = (rocket2_s2[:,2]+rocket1_s2[:,2])/2


        other_objects_s2 = [self._object_list('rocket1', 'Satellite', rocket1_s2, ship_scale_s2*factor, [1,1,1], visible = rocket1_visible, msg_list = r1_s2_msg),
                            self._object_list('rocket2', 'Satellite', rocket2_s2, ship_scale_s2*factor, [1,1,1], visible = rocket2_visible, msg_list = r2_s2_msg, orient = [0,0,1]),
                            self._object_list('death_star', 'Sphere01', middle_observer, 130*factor, [1,1,1], visible = [1]*N, msg_list = ['\n\nDeath Star']*len(lasers_visible)),
                            self._object_list('laser1', 'Laser', laser1_s2, lasers_scale_s2*factor, [1,1,0], visible = rocket2_visible, msg_list = l1_s2_msg),
                            self._object_list('laser2', 'Laser', laser2_s2, lasers_scale_s2*factor, [1,0,0], visible = laser2_visible, msg_list = l2_s2_msg),
                            self._object_list('Boom1', 'explosion', rocket1_s2, 10000*factor, [1,0.6,0], visible = 1 - rocket1_visible),
                            self._object_list('Boom2', 'explosion', rocket2_s2, 10000*factor, [1,0.6,0], visible = 1 - rocket2_visible),
                            self._object_list('Ball1', 'Sphere01', rocket1_s2, 50*factor, [255,255,255], visible = 1 - rocket1_visible),
                            self._object_list('Ball2', 'Sphere01', rocket2_s2, 50*factor, [255,255,255], visible = 1 - rocket2_visible),
                            self._object_list('ball3', 'Sphere01', ball3_pos_s2, 35*factor, [255,255,255], visible = ball3_visible_s2),
                            self._object_list('ball4', 'Sphere01', ball4_pos_s2, 55*factor, [255,255,255], visible = ball4_visible_s2)]

        sat_messages_s2 = ['\nThe spacecrafts are moving relative to the planet with v = %.3fc' % (ref_frame_speed/const.c_AU_pr_s) for i in range(N)]

        for i in range(N):
            sat_messages_s2[i] += '\nPosition of event A: %f km. Time of event A: %f ms' %(0,0)

        ruler_length = utils.AU_to_km(self._get_ruler_length(cam_dist_s2))
        ruler_start = -(ruler_length/2.+utils.AU_to_km(rocket1_s2[0,2]))
        ruler_end = ruler_length + ruler_start
        rulerUnit = 'km'

        dltax=abs(ruler_start)/2.
        fct=np.rint(ruler_length/dltax)
        ruler_end = ruler_start+dltax*fct
        #ticks_s2=np.rint((ruler_end-ruler_start)/dltax)

        ruler_s2 = [ruler_start, ruler_end, ticks_s2, rulerUnit, utils.AU_to_km(cam_dist_s2), self._ruler_height]

        self._write_to_xml(times_s2, cam_pos_s2, cam_dir_s2, planet_pos, other_objects_s2, field_of_view = 70, ruler = ruler_s2, play_speed=0.5005, cheat_light_speed = True,
                          planet_idx=planet_idx, up_vec=up_vec, laser_scale = 0.2, filename = filename_2, camera_messages = sat_messages_s2, use_obj_scaling = 1)

        for i in range(N):
            if 1-rocket1_visible[i] == 1:
                explosion_1_t = times_s2[i]
                break

        if write_solutions:
            # Writing the numerical solutions
            solution_name='Solutions_spaceship_duel.txt'
            solution_2A=self._get_new_solution_file_handle(solution_name)
            solution_2A.write('Solutions to 2A.4\n')
            solution_2A.write('\n NOTE: None of these answers are relevant for the project!\n')
            solution_2A.write('Quick jump to part 1, exercise 7:\n')
            solution_2A.write('7) L\' = 1200 km. The rest is given in the spaceship frame in mcast\n')
            #solution_2A.write('8. No numerical answer\n')
            #solution_2A.write('9. No numerical answer\n')
            solution_2A.write('10) tC = %f km = %f ms. xC = %f km\n' %(utils.AU_to_km(spaceship_distance/np.sqrt(1.-(ref_frame_speed/const.c_AU_pr_s)**2)), utils.AU_to_m(spaceship_distance/np.sqrt(1.-(ref_frame_speed/const.c_AU_pr_s)**2))/const.c_km_pr_s, utils.AU_to_km(spaceship_distance/np.sqrt(1.-(ref_frame_speed/const.c_AU_pr_s)**2)*ref_frame_speed/const.c_AU_pr_s)))
            #solution_2A.write('11. No numerical answer\n')
            solution_2A.write('12) L = %f km' %(utils.AU_to_km(dist_between_rockets_s2)))
            solution_2A.close()

    def cosmic_pingpong(self, planet_idx, filename_1='cosmic_pingpong_frame_1.xml', filename_2='cosmic_pingpong_frame_2.xml', filename_3='cosmic_pingpong_frame_3.xml', number_of_video_frames=1000, write_solutions=False):
        """Two spaceships are playing cosmic ping-pong with a laser beam.

        Generates the XML files used in Exercise 5 in Part 2A of the lecture notes and Exercise 2 in Part 8 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        filename_3 : str, optional
            The filename to use for frame of reference 3.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1000, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)
        filename_3 = str(filename_3)

        planet_radius = utils.km_to_AU(self.system.radii[planet_idx])
        events_radius = planet_radius*1.5   # Distance from planets events and spaceships are.
        sat1_color = [1,0,0]
        sat2_color = [0,0,1]
        spacecraft_distance = 400    # Distance between the two spacecrafts (km)
        distance_to_events = 400    # Distance between camera and the two spacecrafts (km)

        sat1_messages_satframe = ['' for i in range(N)]
        sat2_messages_satframe = ['' for i in range(N)]
        sat1_messages_planframe = ['' for i in range(N)]
        sat2_messages_planframe = ['' for i in range(N)]
        sat1_sounds_satframe = ['' for i in range(N)]
        sat2_sounds_satframe = ['' for i in range(N)]
        sat1_sounds_planframe = ['' for i in range(N)]
        sat2_sounds_planframe = ['' for i in range(N)]

        # SCENE 1
        random_state = np.random.RandomState(self.seed + utils.get_seed('cosmic_pingpong'))
        sat_frame_speed = utils.km_to_AU(0.65*const.c_km_pr_s)
        sat_frame_movement = utils.km_to_AU(np.linspace(0,1400,N))

        global_messages = ['Velocity of spacecrafts in planet frame = %f c\n' % (sat_frame_speed/const.c_AU_pr_s)]*N

        # 1D
        sat1_pos_1D_satframe = np.zeros(N) - utils.km_to_AU(spacecraft_distance/2.0)
        sat2_pos_1D_satframe = np.zeros(N) + utils.km_to_AU(spacecraft_distance/2.0)
        cam_pos_1D_satframe = np.zeros(N)
        laser_pos_1D_satframe = np.zeros( shape=(N) )

        end_time = (sat_frame_movement[-1] - sat_frame_movement[0])/(sat_frame_speed)
        time_array = np.linspace(0, end_time, N)

        # Laser
        dx = utils.km_to_AU((time_array[-1] - time_array[-2])*const.c_km_pr_s)
        laser_pos_1D_satframe[0] = sat2_pos_1D_satframe[0]
        laser_moving_forward = False   # Is the laser moving in positive x-direction?
        explvisible_satframe = np.copy(sat1_pos_1D_satframe)
        explvisible_satframe[:] = 0
        first_time_hit = 0
        sat2_messages_satframe[0:(int(N/32))] = ['\nEmitting!']*(int(N/32))
        for i in range(N):
            global_messages[i] += 'Laser emitted at [%g ms, %g km]\n' % (0, 0)

        for i in range(1, N):
            if laser_moving_forward:   # Move laser in moving direction.
                laser_pos_1D_satframe[i] = laser_pos_1D_satframe[i-1] + dx
            else:
                laser_pos_1D_satframe[i] = laser_pos_1D_satframe[i-1] - dx

            if laser_pos_1D_satframe[i] > sat2_pos_1D_satframe[i]:  # Laser in front of of first spaceship.
                if self._debug: print('Laser bounced backwards at frame %d, [%es, %em] in spacecraft frame' % (i, time_array[i], laser_pos_1D_satframe[i]))
                for j in range(i, N):
                    global_messages[j] += 'Laser bounced forwards at [%g ms, %g km]\n' % (time_array[i]*1000, 0)

                laser_moving_forward = False
                laser_pos_1D_satframe[i] -= abs(laser_pos_1D_satframe[i] - sat2_pos_1D_satframe[i]) # Correcting over-movement of laser.
                # sat2_messages_satframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                sat2_messages_satframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                sat2_sounds_satframe[i] = 'laser'


            if laser_pos_1D_satframe[i] < sat1_pos_1D_satframe[i]:  # Laser behind last spaceship.
                if self._debug: print('Laser bounced forwards at frame %d, [%es, %em] in spacecraft frame' % (i, time_array[i], laser_pos_1D_satframe[i]))
                for j in range(i, N):
                    global_messages[j] += 'Laser bounced backwards at [%g ms, %g km]\n' % (time_array[i]*1000, spacecraft_distance)

                laser_moving_forward = True
                laser_pos_1D_satframe[i] += abs(laser_pos_1D_satframe[i] - sat1_pos_1D_satframe[i]) # Correcting over-movement of laser.
                # sat2_messages_satframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                sat1_messages_satframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                if (first_time_hit == 0):
                    explvisible_satframe[i:(i+int(N/32))] = 1
                    first_time_hit = 1
                    expltime_satframe = time_array[i]
                    explpos_satframe =  - sat_frame_movement[i]
                    explind = i
                    for j in range(i, N):
                        global_messages[j] += 'Explosion at [%g ms, %g km]\n' % (time_array[i]*1000, utils.AU_to_km(sat_frame_movement[i]))
                sat1_sounds_satframe[i] = 'laser'


        # 3D
        cam_pos_satframe = np.zeros( shape=(N,3) )
        sat1_pos_satframe = np.zeros( shape=(N,3) )
        sat2_pos_satframe = np.zeros( shape=(N,3) )
        laser_pos_satframe = np.zeros( shape=(N,3))

        cam_pos_satframe[:,1] = cam_pos_1D_satframe               + sat_frame_movement
        sat1_pos_satframe[:,1] = sat1_pos_1D_satframe       + sat_frame_movement
        sat2_pos_satframe[:,1] = sat2_pos_1D_satframe       + sat_frame_movement
        laser_pos_satframe[:,1]   = laser_pos_1D_satframe         + sat_frame_movement

        # Moving relative to planet.
        cam_pos_satframe[:,0] -= (events_radius + utils.km_to_AU(1200))
        sat1_pos_satframe[:,0] -= events_radius
        sat2_pos_satframe[:,0] -= events_radius
        laser_pos_satframe[:,0] -= events_radius  + utils.km_to_AU(10)  # Moving laser slighty upwards(towards camera) for visibility
        cam_pos_satframe[:,0] -= utils.km_to_AU(distance_to_events) # Moving camera above events.

        cam_dir = [1,0,0]
        up_vec = [0,0,1]


        ruler_length = self._get_ruler_length(distance_to_events + 1200., field_of_view=70)
        ruler_start = -(ruler_length/2.-utils.AU_to_km(abs(sat1_pos_satframe[0,1]-sat2_pos_satframe[0,1])/2.))
        ruler_end = ruler_length + ruler_start
        rulerUnit = 'km'


        dltax=abs(ruler_start)/5.
        fct=np.rint(ruler_length/dltax)
        ruler_end = ruler_start+dltax*fct
        ticks_s2=np.rint((ruler_end-ruler_start)/dltax)

        ruler = [ruler_start, ruler_end, ticks_s2, rulerUnit, distance_to_events + 1200., self._ruler_height]

        ball_pos_satframe = np.copy(sat2_pos_satframe)
        ball_pos_satframe[:,1] = sat2_pos_satframe[0,1]
        ball_pos_satframe[:,0] += utils.km_to_AU(50)


        other_objects = [['lsr', 'Laser', laser_pos_satframe, 8, [1,0,0], None, None, None, None],
                         ['sat1', 'Satellite', sat1_pos_satframe, 0.1, sat1_color, sat1_messages_satframe, sat1_sounds_satframe, None, [0,-1,0]],
                         ['sat2', 'Satellite', sat2_pos_satframe, 0.1, sat2_color, sat2_messages_satframe, sat2_sounds_satframe, None, [0,1,0]],
                         ['ball', 'Sphere01', ball_pos_satframe, 50, [1,1,1], None, None, None, [0,1,0]],
                         ['ball', 'explosion', ball_pos_satframe, 1000, [50,50,0], None, None, explvisible_satframe , [0,1,0] ]]


        self._write_to_xml(time_array, cam_pos_satframe, cam_dir, other_objects=other_objects, planet_idx=planet_idx, up_vec=up_vec, laser_scale = 0.1, ruler=ruler, filename=filename_1, play_speed=0.6, camera_messages=global_messages, field_of_view=70,cheat_light_speed=True)

        # SCENE 2
        # 1D
        time_array_planframe1, sat1_pos_1D_planframe = self._lorentz_transform(time_array, sat1_pos_1D_satframe, -sat_frame_speed)
        time_array_planframe2, sat2_pos_1D_planframe = self._lorentz_transform(time_array, sat2_pos_1D_satframe, -sat_frame_speed)

        expltime_planframe, explpos_planframe = self._lorentz_transform(expltime_satframe, explpos_satframe, -sat_frame_speed)

        time_array_planframe = np.linspace(0, (time_array_planframe1[-1] - time_array_planframe1[0]), N)

        sat1_pos_1D_planframe = interpolate.interp1d(time_array_planframe1, sat1_pos_1D_planframe, kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array_planframe)
        sat2_pos_1D_planframe = interpolate.interp1d(time_array_planframe2, sat2_pos_1D_planframe, kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array_planframe)


        # Laser
        laser_pos_1D_planframe = np.zeros( shape=(N) )
        dx = utils.km_to_AU((time_array_planframe[-1] - time_array_planframe[-2])*const.c_km_pr_s)
        laser_pos_1D_planframe[0] = sat2_pos_1D_planframe[0]
        laser_moving_forward = False   # Does the laser move in positive x-direction?
        sat2_messages_planframe[0:(int(N/32))] = ['\nStart position!']*(int(N/32))
        bouncing_backwards_indexes = []
        bouncing_forward_indexes = []
        for i in range(1, N):
            if laser_moving_forward:   # Move laser in moving direction.
                laser_pos_1D_planframe[i] = laser_pos_1D_planframe[i-1] + dx
            else:
                laser_pos_1D_planframe[i] = laser_pos_1D_planframe[i-1] - dx

            if laser_pos_1D_planframe[i] > sat2_pos_1D_planframe[i]:  # Laser in front of of first spaceship.
                if self._debug: print('Laser bounced backwards at frame %d, [%es, %em] in planet frame' % (i, time_array_planframe[i], laser_pos_1D_planframe[i]))
                laser_moving_forward = False
                laser_pos_1D_planframe[i] -= abs(laser_pos_1D_planframe[i] - sat2_pos_1D_planframe[i]) # Correcting over-movement of laser.
                # sat2_messages_planframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                sat2_messages_planframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                sat2_sounds_planframe[i] = 'laser'
                bouncing_backwards_indexes.append(i)

            if laser_pos_1D_planframe[i] < sat1_pos_1D_planframe[i]:  # Laser behind last spaceship.
                if self._debug: print('Laser bounced forwards at frame %d, [%es, %em] in planet frame' % (i, time_array_planframe[i], laser_pos_1D_planframe[i]))
                laser_moving_forward = True
                laser_pos_1D_planframe[i] += abs(laser_pos_1D_planframe[i] - sat1_pos_1D_planframe[i]) # Correcting over-movement of laser.
                # sat1_messages_planframe[i:(i+int(N/32))] = ['\nBounce!']*(int(N/32))
                sat1_messages_planframe[i:(i+int(N/32))] = ['\nBounce!'] * (int(N/32))
                sat1_sounds_planframe[i] = 'laser'
                bouncing_forward_indexes.append(i)

        # 3D
        cam_pos_planframe = np.zeros( shape=(N,3) )
        sat1_pos_planframe = np.zeros( shape=(N,3) )
        sat2_pos_planframe = np.zeros( shape=(N,3) )
        laser_pos_planframe = np.zeros( shape=(N,3) )

        sat1_pos_planframe[:,1] = sat1_pos_1D_planframe
        sat2_pos_planframe[:,1] = sat2_pos_1D_planframe
        laser_pos_planframe[:,1]   = laser_pos_1D_planframe

        # Moving relative to planet.
        cam_pos_planframe[:,0] -= (events_radius + utils.km_to_AU(1200) + utils.km_to_AU(distance_to_events))  # Moving camera a bit above planet surface
        cam_pos_planframe[:,2] += 0
        sat1_pos_planframe[:,0] -= events_radius
        sat2_pos_planframe[:,0] -= events_radius
        laser_pos_planframe[:,0] -= events_radius  + utils.km_to_AU(10)   # Moving laser slighty upwards(towards camera) for visibility

        cam_dir_planframe = ((sat1_pos_planframe+sat2_pos_planframe)/2 - cam_pos_planframe)
        cam_dir_planframe[:,1] = cam_dir_planframe[0,1]

        up_vec_planframe = [0,0,1]

        ball_pos_planframe = np.copy(sat2_pos_planframe)
        ball_pos_planframe[:,1] = sat2_pos_planframe[0,1]
        ball_pos_planframe[:,0] +=utils.km_to_AU(50)

        explind_planframe= np.fabs(time_array_planframe-expltime_planframe).argmin()
        explvisible_planframe = np.copy(explvisible_satframe)
        explvisible_planframe[:] = 0
        explvisible_planframe[explind_planframe:explind_planframe+(int(N/32))] = 1



        other_objects_planframe = [['lsr', 'Laser', laser_pos_planframe, 8, [1,0,0], None, None, None, None],
                                   ['sat1', 'Satellite', sat1_pos_planframe, 0.1, sat1_color, sat1_messages_planframe, sat1_sounds_planframe, None, [0,-1,0]],
                                   ['sat2', 'Satellite', sat2_pos_planframe, 0.1, sat2_color, sat2_messages_planframe, sat2_sounds_planframe, None, [0,1,0]],
                                   ['ball', 'Sphere01', ball_pos_planframe, 50, [1,1,1], None, None, None, [0,1,0]],
                                   ['ball', 'explosion', ball_pos_planframe, 1000, [50,50,0], None, None, explvisible_planframe, [0,1,0] ]]


        ruler_length = self._get_ruler_length(distance_to_events + 1200., field_of_view=70)*np.sqrt(1.-(sat_frame_speed/const.c_AU_pr_s)**2)

        ruler_start = -(ruler_length/2.-utils.AU_to_km(abs(sat1_pos_planframe[0,1]-sat2_pos_planframe[0,1])/2.))
        ruler_end = ruler_length + ruler_start
        rulerUnit = 'km'


        dltax=abs(ruler_start)/7.
        fct=np.rint(ruler_length/dltax)
        ruler_end = ruler_start+dltax*fct
        ticks_s2=np.rint((ruler_end-ruler_start)/dltax)

        ruler = [ruler_start, ruler_end, ticks_s2, rulerUnit, distance_to_events + 1200., self._ruler_height]
        global_messages2 = ['Velocity of spacecrafts in planet frame = %f c\n' % (sat_frame_speed/const.c_AU_pr_s)]*N

        self._write_to_xml(time_array_planframe, cam_pos_planframe, cam_dir_planframe, other_objects=other_objects_planframe, planet_idx=planet_idx, up_vec=up_vec_planframe, laser_scale = 0.1, filename=filename_2, play_speed=0.6, camera_messages=global_messages2, field_of_view=70, ruler=ruler,cheat_light_speed=True)

        if write_solutions:
            # Writing the numerical solutions
            solution_name='Solutions_cosmic_pingpong.txt'
            solution_2A=self._get_new_solution_file_handle(solution_name)
            solution_2A.write('Solutions to 2A.5\n')
            solution_2A.write('\n')
            solution_2A.write('Quick jump to exercise 12:\n')
            solution_2A.write('12) tC = %f ms\n' %(time_array_planframe[explind_planframe]*1000))
            solution_2A.write('13) tB = %f ms\n' %(time_array_planframe[bouncing_forward_indexes[0]]*1000))
            solution_2A.write('14) tD = %f ms\n' %(time_array_planframe[bouncing_backwards_indexes[0]]*1000))
            solution_2A.write('15) tB - tA = %f ms\n' %(time_array_planframe[bouncing_forward_indexes[0]]*1000))
            solution_2A.write('16) tD - tB = %f ms\n' %(abs(time_array_planframe[bouncing_forward_indexes[0]]*1000-time_array_planframe[bouncing_backwards_indexes[0]]*1000)))
            #solution_2A.write('15. No numerical solution\n')
            solution_2A.close()

        N = 2048
        time_array = np.linspace(0, 18, N)/1000
        dt = time_array[1]

        ruler_length = self._get_ruler_length(distance_to_events + 1200., field_of_view=70)
        ruler_start = -(ruler_length/2.-utils.AU_to_km(abs(sat1_pos_satframe[0,1]-sat2_pos_satframe[0,1])/2.))
        ruler_end = ruler_length + ruler_start
        rulerUnit = 'km'


        dltax=abs(ruler_start)/5.
        fct=np.rint(ruler_length/dltax)
        ruler_end = ruler_start+dltax*fct
        ticks_s2=np.rint((ruler_end-ruler_start)/dltax)

        ruler = [ruler_start, ruler_end, ticks_s2, rulerUnit, distance_to_events + 1200.]

        dx_spaceship = 400
        start_pos = ruler_start + 200
        ships = np.zeros((2, N, 3))  #Position of ships in km
        laser_pos = np.zeros((N, 3))  #Position of laser in km
        laser_pos[0] = start_pos
        c_to_use = const.c_km_pr_s  #Make a uniqe variable that can be turned negative when whised
        v_to_use = 0
        counter = 0  #Counting number of time the laser turns at the leftmost spaceship
        ships[0, 0, 1] = start_pos
        ships[1, 0, 1] = start_pos + dx_spaceship
        global_messages = []
        message = 'Spaceships velocity 0c'
        global_messages += [message]
        sound_list = []
        sound_list += [0]
        variable = 0

        for i in range(1, N):
            #Checking if the light hits the ships
            if laser_pos[i-1, 1] < ships[0, i-1, 1]:
                c_to_use = const.c_km_pr_s
                sound_list += ['explosion']
                if variable < i-5:
                    counter += 1
                    variable = i

            elif laser_pos[i-1, 1] > ships[1, i-1, 1]:
                c_to_use = -const.c_km_pr_s
                sound_list += ['explosion']  #TODO change to bell sound
            else:
                sound_list += [0]

            #Changing the velocity based in the total reflections
            if counter == 1:
                message = 'Spaceships velocity 0.3c'
                v_to_use = 0.3*const.c_km_pr_s
            elif counter == 2:
                message = 'Spaceships velocity 0.6c'
                v_to_use = 0.6*const.c_km_pr_s
            elif counter == 3:
                message = 'Spaceships velocity 0.8c'
                v_to_use = 0.8*const.c_km_pr_s
            else:
                pass

            laser_pos[i, 1] = c_to_use*dt + laser_pos[i-1, 1]
            ships[0, i, 1] = v_to_use*dt + ships[0, i-1, 1]
            ships[1, i, 1] = v_to_use*dt + ships[1, i-1, 1]
            global_messages += [message]

        laser_pos[:, 0] -= utils.AU_to_km(events_radius) + 10
        ships[:, :, 0] -= utils.AU_to_km(events_radius)
        ships[:, :, 1], laser_pos[:, 1] = -ships[:, :, 1], -laser_pos[:, 1]

        # 3D
        cam_pos_planframe = np.zeros( shape=(N,3) )

        # Moving relative to planet.
        cam_pos_planframe[:,0] -= (events_radius + utils.km_to_AU(1200) + utils.km_to_AU(distance_to_events))  # Moving camera a bit above planet surface
        cam_pos_planframe[:,2] += 0


        other_objects_planframe = [['lsr', 'Laser', utils.km_to_AU(laser_pos), 10, [1,0,0], None, None, None, None],
                                   ['sat1', 'Satellite', utils.km_to_AU(ships[0]), 0.15, sat1_color, None, sound_list, None, [0,1,0]],
                                   ['sat2', 'Satellite', utils.km_to_AU(ships[1]), 0.15, sat2_color, None, None, None, [0,-1,0]]]

        self._write_to_xml(time_array, cam_pos_planframe, cam_dir_planframe[0], other_objects=other_objects_planframe, planet_idx=planet_idx, up_vec=up_vec_planframe, laser_scale = 0.1, filename=filename_3, play_speed=0.6, camera_messages=global_messages, field_of_view=70, ruler=ruler,cheat_light_speed=True)

    def more_lightning_strikes(self, planet_idx, increase_height=False, filename_1='more_lightning_strikes_frame_1.xml', filename_2='more_lightning_strikes_frame_2.xml', field_of_view=70, number_of_video_frames=1000, write_solutions=False):
        """The unfortunate spaceship flying through the atmosphere is this time struck by a green, a pink, a blue and a yellow lightning bolt.

        Generates the XML files used in Exercise 6 in Part 2A of the lecture notes.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.01 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        field_of_view : float, optional
            The field of view of the camera, in degrees.
            Default is 70.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1000, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        low_sat_speed = [0.80, 0.84]  # Possible speed interval (in c's) of fastest and slowest spaceship.
        high_sat_speed = [0.86, 0.90]
        factor = 1.7

        distance_to_events = utils.km_to_AU(4.5*400)  # Events are in the middle, with the spacecrafts this far on each side.
        cam_dir = np.array([0,0,-1])

        planet_radius = utils.km_to_AU(self.system.radii[planet_idx])

        if increase_height is False:
            event_radius = planet_radius*1.01   # Distance from planet center when the spacecraft is considered to have crashed.
        elif increase_height is True:
            event_radius = planet_radius*1.1
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                event_radius = planet_radius*(1.005+0.005*increase_height)
            else:
                event_radius = planet_radius*(1.005-0.005*increase_height)

        random_seed = self.seed + utils.get_seed('more_lightning_strikes')
        random_state = np.random.RandomState(random_seed)

        v_cam_planframe = random_state.uniform(low_sat_speed[0], low_sat_speed[1]) #* const.c_AU_pr_s
        v_friend_planframe = random_state.uniform(high_sat_speed[0], high_sat_speed[1]) #* const.c_AU_pr_s



        v_friend_camframe = self._velocity_transformation(v_cam_planframe, v_friend_planframe)

        v_cam_planframe = v_cam_planframe * const.c_AU_pr_s
        v_friend_planframe = v_friend_planframe * const.c_AU_pr_s
        v_friend_camframe = v_friend_camframe * const.c_AU_pr_s


        if self._debug: print('Our velocity in planet frame = %gc\nFriend velocity in planet frame = %gc\nFriend velocity in our frame = %gc' % (v_cam_planframe, v_friend_planframe, v_friend_camframe))


        sat_movement_length_planframe = utils.km_to_AU(2000)  # Total moment of fastest spacecraft in relation to planet.
        end_time_planframe = sat_movement_length_planframe/(max([v_cam_planframe, v_friend_planframe]))
        time_array_planframe = np.linspace(0, end_time_planframe, N)  # Own-time of planet frame.

        # 1D (z-axis in 3D)
        cam_pos_1D_camframe = np.zeros(N)
        friend_pos_1D_camframe = np.linspace(0, end_time_planframe*v_friend_camframe, N)
        cam_pos_1D_planframe = np.linspace(0, end_time_planframe*v_cam_planframe, N)
        friend_pos_1D_planframe = np.linspace(0, end_time_planframe*v_friend_planframe, N)

        end_time_camframe, _ = self._lorentz_transform(time_array_planframe[-1], cam_pos_1D_planframe[-1], v_cam_planframe)   # Lorentz transforming end position of cam to get end time of cam.
        end_time_friendframe, _ = self._lorentz_transform(time_array_planframe[-1], cam_pos_1D_planframe[-1], v_friend_planframe)   # Lorentz transforming end position of cam to get end time of cam.
        time_array_camframe = np.linspace(0, end_time_camframe, N)
        time_array_friendframe = np.linspace(0, end_time_friendframe, N)

        planet_pos_1D_camframe = np.linspace(0, -end_time_planframe*v_cam_planframe, N)





        # 3D
        cam_pos = np.zeros( shape = (N,3) )
        cam_pos[:,2] += distance_to_events
        friend_pos_camframe = np.zeros( shape = (N,3) )
        friend_pos_camframe[:,1] = friend_pos_1D_camframe
        friend_pos_camframe[:,2] -= distance_to_events
        cam_pos_camframe = np.zeros( shape = (N,3) )
        cam_pos_camframe[:,1] = cam_pos_1D_camframe
        #cam_pos_camframe[:,2] -= distance_to_events
        planet_pos_camframe = np.zeros( shape=(N,3) )
        planet_pos_camframe[:,0] += event_radius   # Moving planet away from events.
        planet_pos_camframe[:,1] = planet_pos_1D_camframe

        # Events
        ball1_pos_camframe = np.zeros( shape = (N,3) )
        ball1_visibility = np.zeros( shape = (N) )
        # ball1_visibility[100:110] += 1

        ### Simultaneous events in planet frame ###
        random_state.seed(random_seed)  # seed_for_random is shared across both users.
        events_index_planframe = random_state.randint( N//4, (3*N)//4 )  # Same index for both events.  Previous (N/4, 3*N/4)
        events_time_planframe = time_array_planframe[events_index_planframe]
        avg_sat_pos_at_event = (cam_pos_1D_planframe[events_index_planframe] + friend_pos_1D_planframe[events_index_planframe]) / 2.0
        event1_pos_1D_planframe = avg_sat_pos_at_event + utils.km_to_AU(110)
        event2_pos_1D_planframe = cam_pos_1D_planframe[events_index_planframe]# - 110*km_to_AU   # Events happening at +/- 20 km from midway between spacecrafts.
        # Lorentz transforming events to cam and friend frame:
        event1_time_camframe, event1_pos_1D_camframe = self._lorentz_transform(events_time_planframe, event1_pos_1D_planframe, v_cam_planframe)
        event2_time_camframe, event2_pos_1D_camframe = self._lorentz_transform(events_time_planframe, event2_pos_1D_planframe, v_cam_planframe)
        event1_time_friendframe, event1_pos_1D_friendframe = self._lorentz_transform(events_time_planframe, event1_pos_1D_planframe, v_friend_planframe)
        event2_time_friendframe, event2_pos_1D_friendframe = self._lorentz_transform(events_time_planframe, event2_pos_1D_planframe, v_friend_planframe)
        # Finding indexes for events in cam and friend frame
        event1_index_camframe = (np.abs(event1_time_camframe - time_array_planframe)).argmin()
        event2_index_camframe = (np.abs(event2_time_camframe - time_array_planframe)).argmin()
        event1_visibility = np.zeros( shape = (N) )
        event2_visibility = np.zeros( shape = (N) )
        event1_visibility[event1_index_camframe : event1_index_camframe+N//32] += 1
        event2_visibility[event2_index_camframe : event2_index_camframe+N//32] += 1
        camera_messages = ['' for i in range(N)]


        event1_pos_camframe = np.zeros( shape=(N,3) )
        event2_pos_camframe = np.zeros( shape=(N,3) )
        event1_pos_camframe[:,1] = event1_pos_1D_camframe
        event2_pos_camframe[:,1] = event2_pos_1D_camframe


        ### Couple of other events ###
        event3_index_planframe = N//8
        event4_index_planframe = 0#random_state.randint( (3*N)//4, (7*N)//8 )
        #event3_time_planframe = time_array_planframe[event3_index_planframe]
        event3_time_camframe = event1_time_camframe
        event3_index_camframe = event1_index_camframe
        #event3_pos_1D_camframe = cam_pos_1D_camframe[event3_index_camframe]
        event3_pos_1D_camframe = planet_pos_1D_camframe[event3_index_camframe]
        event3_time_planframe, event3_pos_1D_planframe = self._lorentz_transform(event3_time_camframe, event3_pos_1D_camframe, -v_cam_planframe)
        event3_index_planframe=(np.abs(event3_time_planframe - time_array_planframe)).argmin()
        #dff=(time_array_planframe-event3_time_planframe)**2
        #wdff=np.where(dff == min(dff))[0]
        #event3_index_planframe = wdff[0]
        event4_time_planframe = time_array_planframe[event4_index_planframe]
        #avg_sat_pos_at_event3 = (cam_pos_1D_planframe[event3_index_planframe] + friend_pos_1D_planframe[event3_index_planframe]) / 2.0
        avg_sat_pos_at_event4 = (cam_pos_1D_planframe[event4_index_planframe] + friend_pos_1D_planframe[event4_index_planframe]) / 2.0
        #event3_pos_1D_planframe = avg_sat_pos_at_event3 - 70*km_to_AU
        event4_pos_1D_planframe = 0#avg_sat_pos_at_event4 + 90*km_to_AU
        #event3_time_camframe, event3_pos_1D_camframe = self._lorentz_transform(event3_time_planframe, event3_pos_1D_planframe, v_cam_planframe)
        event4_time_camframe, event4_pos_1D_camframe = self._lorentz_transform(event4_time_planframe, event4_pos_1D_planframe, v_cam_planframe)
        #event3_index_camframe = (np.abs(event3_time_camframe - time_array_planframe)).argmin()
        event4_index_camframe = (np.abs(event4_time_camframe - time_array_planframe)).argmin()
        event3_visibility = np.zeros( shape = (N) )
        event4_visibility = np.zeros( shape = (N) )
        event3_visibility[event3_index_camframe : event3_index_camframe+N//32] += 1
        event4_visibility[event4_index_camframe : event4_index_camframe+N//32] += 1

        event1_messages = ['' for i in range(N)]
        event2_messages = ['' for i in range(N)]
        event3_messages = ['' for i in range(N)]
        event4_messages = ['' for i in range(N)]
        #event1_messages[event1_index_camframe : event1_index_camframe+N//32] = ['\n\nPosition of event 1 = %fkm and %fs' % (event1_pos_1D_camframe*AU_to_km, event1_time_camframe)]*(N//32)
        event1_messages[event1_index_camframe : event1_index_camframe+N//32] = ['\n\n Event P']*(N//32)
        event2_messages[event2_index_camframe : event2_index_camframe+N//32] = ['\n\n Event B']*(N//32)
        event3_messages[event3_index_camframe : event3_index_camframe+N//32] = ['\n\n Event Y']*(N//32)
        event4_messages[event4_index_camframe : event4_index_camframe+N//32] = ['\n\n Event G']*(N//32)

        event3_pos_camframe = np.zeros( shape=(N,3) )
        event4_pos_camframe = np.zeros( shape=(N,3) )
        event3_pos_camframe[:,1] = event3_pos_1D_camframe
        event4_pos_camframe[:,1] = event4_pos_1D_camframe

        #Setting up the camera messages

        camera_messages = [ (camera_messages[i] + 'Velocity of planet relative to our spacecraft frame = %fc' %(-v_cam_planframe/const.c_AU_pr_s)) for i in range(N) ]

        for i in range(event4_index_camframe,N):
            camera_messages[i] += '\nPosition of event G = %f km. Time of event G = %f ms' % (utils.AU_to_km(event4_pos_1D_camframe), event4_time_camframe*1000)
        for i in range(event3_index_camframe,N):
            camera_messages[i] += '\nPosition of event Y = %f km. Time of event Y = %f ms' % (utils.AU_to_km(event3_pos_1D_camframe), event3_time_camframe*1000)
        for i in range(event1_index_camframe,N):
            camera_messages[i] += '\nPosition of event P = %f km. Time of event P = %f ms' % (utils.AU_to_km(event1_pos_1D_camframe), event1_time_camframe*1000)
        for i in range(event2_index_camframe,N):
            camera_messages[i] += '\nPosition of event B = %f km. Time of event B = %f ms' % (utils.AU_to_km(event2_pos_1D_camframe), event2_time_camframe*1000)

        # Messages, sounds, and other.
        ruler_length = utils.AU_to_km(self._get_ruler_length(distance_to_events, field_of_view=field_of_view))
        #ruler = [-ruler_length/2.0, ruler_length/2.0, 20, 'km']  #TODO: Are we sure FOV is always pi/2 (90 degrees)?
        # Note: Ruler is only accurate for friends spaceship, and not for the events in between.
        ruler = [-ruler_length/5.,ruler_length*4./5.,20,'km',utils.AU_to_km(distance_to_events), self._ruler_height]
        cam_pos[:,1] = utils.km_to_AU(ruler_length)*3./10.
        planet_pos_camframe[:,1] +=  utils.km_to_AU(ruler_length)*3./10.*np.sqrt(1.-(v_cam_planframe/const.c_AU_pr_s)**2)/2.
        other_objects = [['Friend', 'Satellite', cam_pos_camframe, 0.08*factor, [1,1,1], None, None, None, [0,-1,0]],
                         ['Ball1', 'Sphere01', event1_pos_camframe, 5*factor, [250,250,250], None, None, event1_visibility, None],
                         ['Ball2', 'Sphere01', event2_pos_camframe, 5*factor, [250,250,250], None, None, event2_visibility, None],
                         ['Ball3', 'Sphere01', event3_pos_camframe, 5*factor, [250,250,250], None, None, event3_visibility, None],
                         ['Ball4', 'Sphere01', event4_pos_camframe, 5*factor, [250,250,250], None, None, event4_visibility, None],
                         ['Event1', 'explosion', event1_pos_camframe, 800*factor, [5,0,5], event1_messages, None, event1_visibility, None],
                         ['Event2', 'explosion', event2_pos_camframe, 800*factor, [0,5,5], event2_messages, None, event2_visibility, None],
                         ['Event3', 'explosion', event3_pos_camframe, 800*factor, [5,5,0], event3_messages, None, event3_visibility, None],
                         ['Event4', 'explosion', event4_pos_camframe, 800*factor, [0,5,0], event4_messages, None, event4_visibility, None]]

        # We can't use the self._write_to_xml, because it only works for one of the two users. setting up a new solar system.

        self._write_to_xml(time_array_planframe, cam_pos, cam_dir, planet_pos_camframe, other_objects=other_objects, camera_messages=camera_messages, planet_idx=planet_idx, ruler=ruler, up_vec=[-1,0,0], filename=filename_1, play_speed=0.501, field_of_view=field_of_view)

        ### PLANET FRAME ###

        cam_pos_planframe = np.zeros( shape = (N,3) )
        cam_pos_planframe[:,1] = cam_pos_1D_planframe

        event1_pos_planframe = np.zeros( shape = (N,3) )
        event2_pos_planframe = np.zeros( shape = (N,3) )
        event3_pos_planframe = np.zeros( shape = (N,3) )
        event4_pos_planframe = np.zeros( shape = (N,3) )
        event1_pos_planframe[:,1] = event1_pos_1D_planframe
        event2_pos_planframe[:,1] = event2_pos_1D_planframe
        event3_pos_planframe[:,1] = event3_pos_1D_planframe
        event4_pos_planframe[:,1] = event4_pos_1D_planframe



        event1_visibility = np.zeros( shape = (N) )
        event2_visibility = np.zeros( shape = (N) )
        event1_visibility[events_index_planframe : events_index_planframe+N//32] += 1
        event2_visibility[events_index_planframe : events_index_planframe+N//32] += 1
        camera_messages = ['' for i in range(N)]
        event1_messages = ['' for i in range(N)]
        event2_messages = ['' for i in range(N)]
        #event1_messages[events_index_planframe : events_index_planframe+N//32] = ['\n\nPosition of event 1 = %fkm' % (event1_pos_1D_planframe*AU_to_km)]*(N//32)
        #event2_messages[events_index_planframe : events_index_planframe+N//32] = ['\nPosition of event 2a = %fkm' % (event2_pos_1D_planframe*AU_to_km)]*(N//32)
        event3_visibility = np.zeros( shape = (N) )
        event4_visibility = np.zeros( shape = (N) )
        event3_visibility[event3_index_planframe : event3_index_planframe+N//32] += 1
        event4_visibility[event4_index_planframe : event4_index_planframe+N//32] += 1
        event3_messages = ['' for i in range(N)]
        event4_messages = ['' for i in range(N)]
        #event3_messages[event3_index_planframe : event3_index_planframe+N//32] = ['\nPosition of event 2b = %fkm' % (event3_pos_1D_planframe*AU_to_km)]*(N//32)
        #event4_messages[event4_index_planframe : event4_index_planframe+N//32] = ['\nPosition of event 0 = %fkm' % (event4_pos_1D_planframe*AU_to_km)]*(N//32)

        event1_messages[events_index_planframe : events_index_planframe+N//32] = ['\n\n Event P']*(N//32)
        event2_messages[events_index_planframe : events_index_planframe+N//32] = ['\n\n Event B']*(N//32)
        event3_messages[event3_index_planframe : event3_index_planframe+N//32] = ['\n\n Event Y']*(N//32)
        event4_messages[event4_index_planframe : event4_index_planframe+N//32] = ['\n\n Event G']*(N//32)


        ruler_length = utils.AU_to_km(self._get_ruler_length(distance_to_events, field_of_view=field_of_view))
        ruler = [-ruler_length/5., ruler_length*4./5., 20, 'km', utils.AU_to_km(distance_to_events), self._ruler_height]  #TODO: Are we sure FOV is always pi/2 (90 degrees)?
        cam_pos[:,1] = utils.km_to_AU(ruler_length)*3./10.



        # Note: Ruler is only accurate for friends spaceship, and not for the events in between.
        planet_pos_camframe[:,1]=0
        camera_messages = [ (camera_messages[i] + 'Velocity of spacecraft relative to planet frame = %fc' %(v_cam_planframe/const.c_AU_pr_s)) for i in range(N) ]

        for i in range(event4_index_planframe,N):
            camera_messages[i] += '\nPosition of event G = %f km. Time of event G = %f ms' % (utils.AU_to_km(event4_pos_1D_planframe), event4_time_planframe*1000)
        for i in range(event3_index_planframe,N):
            #camera_messages[i] += '\nPosition of event Y = %f km. Time of event Y = %f ms' % (event3_pos_1D_planframe*AU_to_km, event3_time_planframe*1000)
            camera_messages[i] += '\nPosition of event Y = %f km. Time of event Y = %f ms' % (0, event3_time_planframe*1000)
        for i in range(events_index_planframe,N):
            camera_messages[i] += '\nPosition of event B = %f km. Time of event B = %f ms' % (utils.AU_to_km(event2_pos_1D_planframe), events_time_planframe*1000)
        for i in range(events_index_planframe,N):
            camera_messages[i] += '\nPosition of event P = %f km. Time of event P = %f ms' % (utils.AU_to_km(event1_pos_1D_planframe), events_time_planframe*1000)



        other_objects = [['Friend', 'Satellite', cam_pos_planframe, 0.08*factor, [1,1,1], None, None, None, [0,-1,0]],
                         ['Ball1', 'Sphere01', event1_pos_planframe, 5*factor, [200,200,200], None, None, event1_visibility, None],
                         ['Ball2', 'Sphere01', event2_pos_planframe, 5*factor, [200,200,200], None, None, event2_visibility, None],
                         ['Ball3', 'Sphere01', event3_pos_planframe, 5*factor, [200,200,200], None, None, event3_visibility, None],
                         ['Ball4', 'Sphere01', event4_pos_planframe, 5*factor, [200,200,200], None, None, event4_visibility, None],
                         ['Event1', 'explosion', event1_pos_planframe, 800*factor, [5,0,5], event1_messages, None, event1_visibility, None],
                         ['Event2', 'explosion', event2_pos_planframe, 800*factor, [0,5,5], event2_messages, None, event2_visibility, None],
                         ['Event3', 'explosion', event3_pos_planframe, 800*factor, [5,5,0], event3_messages, None, event3_visibility, None],
                         ['Event4', 'explosion', event4_pos_planframe, 800*factor, [0,5,0], event4_messages, None, event4_visibility, None]]


        self._write_to_xml(time_array_planframe, cam_pos, cam_dir, planet_pos_camframe, other_objects=other_objects, camera_messages=camera_messages, planet_idx=planet_idx, ruler=ruler, up_vec=[-1,0,0], filename=filename_2, play_speed=0.501, field_of_view=field_of_view)

        if write_solutions:

            #Solution writing
            solution_name='Solutions_more_lightning_strikes.txt'
            solution_2A=self._get_new_solution_file_handle(solution_name)
            solution_2A.write('Solutions to 2A.6\n')
            solution_2A.write('\n')
            solution_2A.write('Answers for planet frame:\n')
            #solution_2A.write('1. No numerical answer + read from mcast\n')
            solution_2A.write('3a) Time of event B: tB\' = %f ms\n' %(event2_time_camframe*1000))
            #solution_2A.write('3. No numerical answer\n')
            solution_2A.write('3c) Time of event P: tP\' = %f ms\n' %(event1_time_camframe*1000))
            solution_2A.write('3d) Position of event P: xP\' = %f km\n' %(utils.AU_to_km(event1_pos_1D_camframe)))
            #solution_2A.write('6. No numerical answer\n')
            #solution_2A.write('7. No numerical answer\n')
            #solution_2A.write('8. No numerical answer\n')

            solution_2A.write('\n')

            solution_2A.write('Answers for spaceship frame:\n')
            #solution_2A.write('1. No numerical answer + read from mcast\n')
            solution_2A.write('2a) Time of event Y: tY = %f ms\n' %(event3_time_planframe*1000))
            #solution_2A.write('3. No numerical answer\n')
            solution_2A.write('2c) Time of event P: tP = %f ms\n' %(events_time_planframe*1000))
            solution_2A.write('2d) Position of event P: xP = %f km\n' %(utils.AU_to_km(event1_pos_1D_planframe)))
            #solution_2A.write('6. No numerical answer\n')
            #solution_2A.write('7. No numerical answer\n')
            #solution_2A.write('8. No numerical answer\n')
            solution_2A.close()

    def twin_paradox(self, planet_idx, filename_1='twin_paradox_frame_1.xml', filename_2='twin_paradox_frame_2.xml', filename_3='twin_paradox_frame_3.xml', number_of_video_frames=1500):
        """An astronaut is traveling at close to the speed of light to a distant planet and back again, while an observer remains at the home planet.

        Generates the XML files used in Exercise 8 in Part 2A of the lecture notes.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        filename_3 : str, optional
            The filename to use for frame of reference 3.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1500, but must be at least 100.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)
        filename_3 = str(filename_3)

        self._twin_paradox_single_frame(planet_idx, 0, filename_1, N)
        self._twin_paradox_single_frame(planet_idx, 1, filename_2, N)
        self._twin_paradox_single_frame(planet_idx, 2, filename_3, N)

    def _twin_paradox_single_frame(self, planet_idx, reference_system, filename, N):
        """
        @ filenames = output xml filename for given frame
        @ reference_system = 0, 1 or 2

        """

        radius = self.system.radii[planet_idx] # [km]
        dt = 2e-5
        planet_pos0 = np.array((0, utils.AU_to_km(1), 0))  #[AU]
        planet_pos = np.zeros((N, 3))
        planet2_pos = np.zeros((N, 3))
        planet3_pos = np.zeros((N, 3))

        vel = np.array([0.,0.,0.99*const.c_km_pr_s])
        cam_pos = np.zeros((N, 3))
        cam_dir = np.zeros((N, 3))
        time_planframe = np.zeros((N))



        # distance between camera and ships in y-direction
        cam_dist = 5000

        distance_to_planet = 200.*365.*24.*3600.*const.c_km_pr_s
        time_of_arrival = 2*distance_to_planet/vel[2]
        ruler_length = self._get_ruler_length(cam_dist)
        nships = np.ceil(distance_to_planet*2./ruler_length)*4
        dist_between_ships = distance_to_planet*2./nships
        nships = int(np.ceil(ruler_length/dist_between_ships))*6
        ships = np.zeros((nships,N,3))
        ships_visibility = np.ones((nships,N))
        ships2 =np.copy(ships)
        ships2_visibility = np.copy(ships_visibility)
        ypos = 0.
        dist_above_surf = -1.5*radius
        ship1 = np.zeros((N,3))
        ship2 = np.zeros((N,3))
        ship1_visibility = np.ones((N))
        ship2_visibility = np.ones((N))
        n_dec_t = 3 ##decimals for real_time
        delta_t = N/2*dt

        ball_pos = np.zeros((N,3))
        ball_visibility = np.zeros(N)

        if (reference_system == 0):
                ###reference system =0

            N *= 2
            N = int(N)
            planet_pos = np.zeros((N, 3))
            planet2_pos = np.zeros((N, 3))
            planet3_pos = np.zeros((N, 3))
            cam_pos = np.zeros((N, 3))
            cam_dir = np.zeros((N, 3))
            time_planframe = np.zeros((N))
            ships = np.zeros((nships,N,3))
            ships_visibility = np.ones((nships,N))
            ships2 =np.copy(ships)
            ships2_visibility = np.copy(ships_visibility)
            ship1 = np.zeros((N,3))
            ship2 = np.zeros((N,3))
            ship1_visibility = np.zeros((N))
            ship2_visibility = np.ones((N))
            ball_pos = np.zeros((N,3))
            ball_visibility = np.zeros(N)

            for i in range(N):
                planet3_pos[i,:] = [0,0,dist_between_ships*1e6]

            gamma1 = 1./np.sqrt(1.-(vel[2]/const.c_km_pr_s)**2)

                #outgoing elevator
            for i in range(nships):
                ypos = ypos - dist_between_ships
                if (ypos < -ruler_length/2.):
                    break
            shp=0
            ypos = ypos + dist_between_ships
            for i in range(nships):
                ships[shp,0,:] = np.array((ruler_length/8.,dist_above_surf,ypos))
                ypos = ypos + dist_between_ships
                shp = shp +1

            cam_pos[0,:] = np.array((0, dist_above_surf-cam_dist, 0))
            cam_dir[0,:] = np.array((0, dist_above_surf, 0)) - cam_pos[0, :]
            time_array = np.linspace(0, dt*N, N)
            real_time = np.copy(time_array)
            real_time[int(N/4):int(N/2)] += time_of_arrival/2./gamma1**2 - int(3*N/8)*dt
            real_time[int(N/2):int(3*N/4)] += time_of_arrival - time_of_arrival/2./gamma1**2 - int(7*N/8)*dt
            real_time[int(3*N/4):N-1] += time_of_arrival-2*delta_t



            for i in range(1,N):
                cam_pos[i,:] = cam_pos[0,:]
                cam_dir[i,:] = cam_dir[0,:]
                for shp in range (nships):
                    ships[shp,i,:] = ships[shp,i-1,:] + vel*dt
                    ships_visibility[:,i] = ships_visibility[:,i-1]
                for shp in range (nships):
                    if (ships[shp,i,2] > ruler_length/2.):
                        ships_visibility[shp,i] = 0
                    if (ships[shp,i-1,2] < (-ruler_length/2.+dist_between_ships)) and (ships[shp,i,2] >= (-ruler_length/2.+dist_between_ships)):
                        vshp = shp -1
                        if (vshp < 0):
                            vshp = nships -1
                        ships_visibility[vshp,i] = 1
                        ships[vshp,i,:] = np.array((ruler_length/8.,dist_above_surf,-ruler_length/2.))



            ballshp = np.argmin(np.abs(ships[:,int(3*N/8),2]))
            ball_pos = np.copy(ships[ballshp,:,:])
            ball_pos[:,1] += 50
            ball_visibility[int(3*N/8)-50:int(3*N/8)+50] = 1


            #incoming elevator
            ypos=0.
            for i in range(nships):
                ypos = ypos + dist_between_ships
                if (ypos > ruler_length/2.):
                    break
            shp=0
            ypos = ypos - dist_between_ships
            for i in range(nships):
                ships2[shp,-1,:] = np.array((-ruler_length/8.,dist_above_surf,ypos))
                ypos = ypos - dist_between_ships
                shp = shp +1

            for i in range(N-2,-1,-1):
                for shp in range (nships):
                    ships2[shp,i,:] = ships2[shp,i+1,:] + vel*dt
                    ships2_visibility[:,i] = ships2_visibility[:,i+1]
                for shp in range (nships):
                    if (ships2[shp,i,2] > ruler_length/2.):
                        ships2_visibility[shp,i] = 0
                    if (ships2[shp,i+1,2] < (-ruler_length/2.+dist_between_ships)) and (ships2[shp,i,2] >= (-ruler_length/2.+dist_between_ships)):
                        vshp = shp +1
                        if (vshp == nships):
                            vshp = 0#nships -1
                        ships2_visibility[vshp,i] = 1
                        ships2[vshp,i,:] = np.array((-ruler_length/8.,dist_above_surf,-ruler_length/2.))


            ballshp = np.argmin(np.abs(ships2[:,int(5*N/8),2]))
            ball_pos[int(3*N/8)+50:N,:] = np.copy(ships2[ballshp,int(3*N/8)+50:N,:])
            ball_visibility[int(5*N/8)-50:int(5*N/8)+50] = 1

            shp = np.argmin(np.abs(ships[:,0,2]))
            ship1 = np.copy(ships[shp,:,:])
            ship1_visibility[0:int(4*dist_between_ships/vel[2]/dt)] = 1
            ships_visibility[shp,0:int(4*dist_between_ships/vel[2]/dt)] = 0

            arrivalship = np.argmin(np.abs(ships2[:,-1,2]))
            ship2 = np.copy(ships2[arrivalship,:,:])
            ship2_visibility[N-int(4*dist_between_ships/vel[2]/dt):N-1] = 1
            ships2_visibility[arrivalship,N-int(4*dist_between_ships/vel[2]/dt):N-1] = 0

        elif reference_system == 1:
            ###reference system =1

            for i in range(N):
                planet3_pos[i,:] = [0,0,dist_between_ships*1e6]


            ship1 = np.zeros((N,3))
            ship2 = np.zeros((N,3))
            ship2_visibility = np.zeros((N))
            ship1_visibility = np.ones((N))


            gamma1 = 1./np.sqrt(1.-(vel[2]/const.c_km_pr_s)**2)
            dist_between_ships = dist_between_ships*gamma1
            dt = dt*gamma1
            delta_t = int(N/2)*dt

            for i in range(1,N):
                planet_pos[i,:] = planet_pos[i-1,:] - vel*dt

            planet2_pos[N-1,:] = np.array([0,0,0])
            for i in range(N-2,N-500,-1):
                planet2_pos[i,:] = planet2_pos[i+1,:] + vel*dt
            planet2_pos[0:N-500] = np.array([0,0,-dist_between_ships*1e6])

            for i in range(N-30,N):
                ball_pos[i,:] = np.array((ruler_length/8.-(i-N+30)*ruler_length/4./29.,dist_above_surf,0))
                ball_visibility[i] = 1
            ball_visibility[N-2:N] = 0


            vel[2] = 2.*vel[2]/(1.+(vel[2]/const.c_km_pr_s)**2)
            gamma2 = 1./np.sqrt(1.-(vel[2]/const.c_km_pr_s)**2)

                #outgoing elevator
            for i in range(nships):
                ypos = ypos - dist_between_ships
                if (ypos < -ruler_length/2.):
                    break
            shp=0
            ypos = ypos + dist_between_ships
            for i in range(nships):
                for j in range(N):
                    ships[shp,j,:] = np.array((ruler_length/8.,dist_above_surf,ypos))
                ypos = ypos + dist_between_ships
                shp = shp +1

            cam_pos[0,:] = np.array((0, dist_above_surf - cam_dist, 0))
            cam_dir[0,:] = np.array((0, dist_above_surf, 0)) - cam_pos[0, :]
            time_array = np.linspace(0, dt*N, N)
            real_time = np.copy(time_array)
            real_time[int(N/2):N-1] += time_of_arrival/2./gamma1-2*delta_t

            for i in range(1,N):
                cam_pos[i,:] = cam_pos[0,:]
                cam_dir[i,:] = cam_dir[0,:]

            dist_between_ships = dist_between_ships/gamma1**2

            #incoming elevator
            ypos=0.
            for i in range(nships):
                ypos = ypos + dist_between_ships
                if (ypos > ruler_length/2.):
                    break
            shp=0
            ypos = ypos - dist_between_ships
            for i in range(nships):
                ships2[shp,-1,:] = np.array((-ruler_length/8.,dist_above_surf,ypos))
                ypos = ypos - dist_between_ships
                shp = shp +1

            for i in range(N-2,-1,-1):
                for shp in range (nships):
                    ships2[shp,i,:] = ships2[shp,i+1,:] + vel*dt
                    ships2_visibility[:,i] = ships2_visibility[:,i+1]
                for shp in range (nships):
                    if (ships2[shp,i,2] > ruler_length/2.):
                        ships2_visibility[shp,i] = 0
                    if (ships2[shp,i+1,2] < (-ruler_length/2.+dist_between_ships)) and (ships2[shp,i,2] >= (-ruler_length/2.+dist_between_ships)):
                        vshp = shp +1
                        if (vshp == nships):
                            vshp = 0#nships -1
                        ships2_visibility[vshp,i] = 1
                        ships2[vshp,i,:] = np.array((-ruler_length/8.,dist_above_surf,-ruler_length/2.))


            ships_visibility[:,int(N/2)-100:int(N/2)] = 0
            ships2_visibility[:,int(N/2)-100:int(N/2)] = 0



            arrivalship = np.argmin(np.abs(ships[:,0,2]))
            ship1 = np.copy(ships[arrivalship,:,:])
            ships_visibility[arrivalship,:] = 0

            arrivalship = np.argmin(np.abs(ships2[:,-1,2]))
            ship2 = np.copy(ships2[arrivalship,:,:])
            ship2_visibility[N-int(10*dist_between_ships/vel[2]/dt):N-1] = 1
            ships2_visibility[arrivalship,N-int(10*dist_between_ships/vel[2]/dt):N-1] = 0




        elif reference_system == 2:
            ###reference system =2


            N *= 3/2
            N = int(N)
            planet_pos = np.zeros((N, 3))
            planet2_pos = np.zeros((N, 3))
            planet3_pos = np.zeros((N, 3))
            cam_pos = np.zeros((N, 3))
            cam_dir = np.zeros((N, 3))
            time_planframe = np.zeros((N))
            ships = np.zeros((nships,N,3))
            ships_visibility = np.ones((nships,N))
            ships2 =np.copy(ships)
            ships2_visibility = np.copy(ships_visibility)
            ship1 = np.zeros((N,3))
            ship2 = np.zeros((N,3))
            ship1_visibility = np.zeros((N))
            ship2_visibility = np.ones((N))
            ball_pos = np.zeros((N,3))
            ball_visibility = np.zeros(N)



            gamma1 = 1./np.sqrt(1.-(vel[2]/const.c_km_pr_s)**2)
            dist_between_ships = dist_between_ships*gamma1
            dt = dt*gamma1

            planet_delta = 400
            for i in range(1,N):
                planet3_pos[i,:] = planet3_pos[i-1,:] + vel*dt
                if (i > int(N/2)-planet_delta):
                    planet3_pos[i,:] = [0,0,dist_between_ships*1e6]


            planet2_pos[int(N/2)-planet_delta,:] = np.array([0,0,-ruler_length*4./3.])
            for i in range(int(N/2)-planet_delta+1,int(N/2)+planet_delta):
                planet2_pos[i,:] = planet2_pos[i-1,:] + vel*dt
            for i in itertools.chain(range(0,int(N/2)-planet_delta+1),range(int(N/2)+planet_delta,N)):
                planet2_pos[i,:] = [0,0,dist_between_ships*1e6]

            planet_middle_index = np.argmin(np.abs(planet2_pos[int(N/2)-planet_delta:int(N/2)+planet_delta,2]))+int(N/2)-planet_delta

            planet_pos[N-1,:] = np.array([0,0,0])
            for i in range(N-2,int(2*N/3),-1):
                planet_pos[i,:] = planet_pos[i+1,:] - vel*dt
            for i in range(0,int(2*N/3)):
                planet_pos[i,:] = [0,0,dist_between_ships*1e6]

            i1 = planet_middle_index-20
            i2 = planet_middle_index+20
            for i in range(i1,i2):
                ball_pos[i,:] = np.array((ruler_length/8.-(i-i1)*ruler_length/4./(i2-i1),dist_above_surf,0))
                ball_visibility[i] = 1
            ball_visibility[-1] = 0


            vel[2] = 2.*vel[2]/(1.+(vel[2]/const.c_km_pr_s)**2)
            gamma2 = 1./np.sqrt(1.-(vel[2]/const.c_km_pr_s)**2)

                #outgoing elevator
            for i in range(nships):
                ypos = ypos - dist_between_ships
                if (ypos < -ruler_length/2.):
                    break
            shp=0
            ypos = ypos + dist_between_ships
            for i in range(nships):
                for j in range(N):
                    ships2[shp,j,:] = np.array((-ruler_length/8.,dist_above_surf,ypos))
                ypos = ypos + dist_between_ships
                shp = shp +1

            cam_pos[0,:] = np.array((0, dist_above_surf - cam_dist, 0))
            cam_dir[0,:] = np.array((0, dist_above_surf, 0)) - cam_pos[0, :]
            time_array = np.linspace(0, dt*N, N)
            real_time = np.copy(time_array)
            real_time[planet_middle_index - planet_delta:planet_middle_index + planet_delta] += time_of_arrival/2./gamma1-planet_middle_index*dt

            real_time[planet_middle_index+planet_delta:N-1] += time_of_arrival/gamma1-N*dt


            for i in range(1,N):
                cam_pos[i,:] = cam_pos[0,:]
                cam_dir[i,:] = cam_dir[0,:]

            dist_between_ships = dist_between_ships/gamma1**2

            #incoming elevator
            ypos=0.
            for i in range(nships):
                ypos = ypos - dist_between_ships
                if (ypos < -ruler_length/2.):
                    break
            shp=0
            ypos = ypos + dist_between_ships
            for i in range(nships):
                ships[shp,0,:] = np.array((ruler_length/8.,dist_above_surf,ypos))
                ypos = ypos + dist_between_ships
                shp = shp +1

            for i in range(1,N):
                for shp in range (nships):
                    ships[shp,i,:] = ships[shp,i-1,:] + vel*dt
                    ships_visibility[:,i] = ships_visibility[:,i-1]
                for shp in range (nships):
                    if (ships[shp,i,2] > ruler_length/2.):
                        ships_visibility[shp,i] = 0
                    if (ships[shp,i-1,2] < (-ruler_length/2.+dist_between_ships)) and (ships[shp,i,2] >= (-ruler_length/2.+dist_between_ships)):
                        vshp = shp - 1
                        if (vshp < 0):
                            vshp = nships -1
                        ships_visibility[vshp,i] = 1
                        ships[vshp,i,:] = np.array((ruler_length/8.,dist_above_surf,-ruler_length/2.))



            arrivalship = np.argmin(np.abs(ships2[:,0,2]))
            ship2 = np.copy(ships2[arrivalship,:,:])
            ships2_visibility[arrivalship,:] = 0

            shp = np.argmin(np.abs(ships[:,planet_middle_index,2]))
            ship1 = np.copy(ships[shp,:,:])
            ship1_visibility[planet_middle_index-int(10*dist_between_ships/vel[2]/dt):planet_middle_index+int(10*dist_between_ships/vel[2]/dt)] = 1
            ships_visibility[shp,planet_middle_index-int(10*dist_between_ships/vel[2]/dt):planet_middle_index+int(10*dist_between_ships/vel[2]/dt)] = 0


        km_to_AU = 1e3/const.AU

        planet_pos *= km_to_AU
        planet2_pos *= km_to_AU
        planet3_pos *= km_to_AU
        ships *= km_to_AU
        ships2 *= km_to_AU
        ship1 *= km_to_AU
        ship2 *= km_to_AU
        cam_pos *= km_to_AU
        cam_dir *= km_to_AU
        ball_pos *= km_to_AU

        camera_messages = ['t = %.16f yr (Real time)'%(real_time[i]/3600./24./365.) for i in range(N)]

        if (reference_system == 0):
            for i in itertools.chain(range(int(N/4)-100,int(N/4)),range(int(N/2)-100,int(N/2)),range(int(3*N/4)-100,int(3*N/4))):
                camera_messages[i] = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n ****************FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...*****************************'
                ships_visibility[:,i] = 0
                ships2_visibility[:,i] = 0
                ship1_visibility[i] = 0
                ship2_visibility[i] = 0

        elif (reference_system == 1):
            for i in range(int(N/2)-100,int(N/2)):
                camera_messages[i] = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n ****************FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...*****************************'
                ships_visibility[:,i] = 0
                ships2_visibility[:,i] = 0
                ship1_visibility[i] = 0
                ship2_visibility[i] = 0


        elif (reference_system == 2):
            for i in itertools.chain(range(planet_middle_index - planet_delta - 50,planet_middle_index - planet_delta + 50),range(planet_middle_index + planet_delta - 50,planet_middle_index + planet_delta + 50)):
                camera_messages[i] = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n ****************FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...FAST FORWARD IN TIME...*****************************'
                ships_visibility[:,i] = 0
                ships2_visibility[:,i] = 0
                ship1_visibility[i] = 0
                ship2_visibility[i] = 0


        other_objects = []
        for shp in range(nships):
            message = []
            for i in range(N):
            #    message.append('sat '+str(shp))
                message.append('')
            other_objects.append(['satellite', 'satellite', ships[shp, :, :], 1., [1, 1, 1], message, None, ships_visibility[shp,:], [0,0,1]])
            other_objects.append(['satellite', 'satellite', ships2[shp, :, :], 1., [1, 1, 1], message, None, ships2_visibility[shp,:], [0,0,-1]])

        other_objects.append(['ship1', 'satellite', ship1, 1., [10, 10, 0], message, None, ship1_visibility, [0,0,1]])
        other_objects.append(['ship2', 'satellite', ship2, 1., [10, 0, 0], message, None, ship2_visibility, [0,0,1]])
        if (reference_system == 0):
            other_objects.append(['ball', 'Sphere01', ball_pos, 150., [0, 100, 250], message, None, ball_visibility, [0,0,1]])
        else:
            other_objects.append(['ball', 'Sphere01', ball_pos, 150., [1, 1, 1], message, None, ball_visibility, [0,0,1]])


        self._write_to_xml(time_array, cam_pos, cam_dir, planet_pos, other_objects, planet2_pos = planet2_pos, planet3_pos = planet3_pos, planet_idx = planet_idx, chosen_planet3 = 3, filename=filename,cheat_light_speed=True,use_obj_scaling = 1, camera_messages = camera_messages, toggle_clock = False)

    def spaceship_race(self, planet_idx, filename_1='spaceship_race_frame_1.xml', filename_2='spaceship_race_frame_2.xml', filename_3='spaceship_race_frame_3.xml', number_of_video_frames=1500):
        """Three spaceships are traveling with different velocities with respect to a space station.

        Generates the XML files used in Exercise 1 in Part 2B of the lecture notes and Exercise 4 in Part 8 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        filename_3 : str, optional
            The filename to use for frame of reference 3.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1500, but must be at least 100.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)
        filename_3 = str(filename_3)

        self._spaceship_race_single_frame(planet_idx, 0, filename_1, N)
        self._spaceship_race_single_frame(planet_idx, 1, filename_2, N)
        self._spaceship_race_single_frame(planet_idx, 2, filename_3, N)

    def _spaceship_race_single_frame(self, planet_idx, reference_system, filename, N):

        radius = self.system.radii[planet_idx] # [km]
        dt = 2e-5
        ships = np.zeros((4, N, 3))
        planet_pos0 = np.array((0, utils.AU_to_km(1), 0))  #[AU]
        planet_pos = np.zeros((N, 3))

        vel = np.zeros((4, 3))
        vel[0, 0] = 0.4*const.c_km_pr_s
        vel[1, 0] = 0.8*const.c_km_pr_s
        vel[2, 0] = 0.1*const.c_km_pr_s
        vel[3, 0] = 0.2*const.c_km_pr_s
        cam_pos = np.zeros((N, 3))
        cam_dir = np.zeros((N, 3))
        time_planframe = np.zeros((N))

        # Setting initial conditions
        for i in range(4):
            if i == 0:                                                          # student 1
                ships[0, 0, :] = np.array((200*0, -1.5*radius, 0))
            if i == 1:                                                          # student 2
                ships[1, 0, :] = np.array((800*0, -1.5*radius, 0))
            if i == 2:                                                          # ship behind travelling slow
                ships[2, 0, :] = np.array((-400*0, -1.5*radius, 0))
            else:                                                               # ship behind travelling fast
                ships[3, 0, :] = np.array((-800*0, -1.5*radius, 0))

        # distance between camera and ships in y-direction
        cam_dist = 5000
        ships_center = np.array((0., ships[0, 0, 1], ships[0, 0, 2]))

        # In the planet system

        cam_pos[0, :] = ships_center + np.array((0, -cam_dist, 0))
        cam_dir[0, :] = ships_center - cam_pos[0, :]
        acc = 2.5e2
        for i in range(N-1):
            time_planframe[i+1] = (i+1)*dt
            planet_pos[i+1, :] = planet_pos[0, :]
            cam_pos[i+1, :] = ships_center + np.array((0, -cam_dist, 0))
            cam_dir[i+1, :] = ships_center - cam_pos[i+1, :]
            for ship in range(0, 4):
                ships[ship, i+1, :] = ships[ship, i, :] + vel[ship,:]*dt

            vel[2,0] = vel[2,0] + acc*dt*const.c_km_pr_s
            if acc > 0 and vel[2,0] > const.c_km_pr_s:
                acc=-0.1*acc
                vel[2,0] = 0.999*const.c_km_pr_s
            if vel[2,0] < 0:
                vel[2,0] = 0.


        ships_planframe = np.copy(ships)
        planet_pos_planframe = np.copy(planet_pos)
        cam_pos_planframe = np.copy(cam_pos)

        if reference_system == 0:
            time_array = np.linspace(0, dt*N, N)

                    # In the refenrece system of student 1
        elif reference_system == 1 or reference_system == 2:
            v = utils.km_to_AU(vel[reference_system-1, 0])

            time_array1, sat1_pos_1D = self._lorentz_transform(time_planframe, utils.km_to_AU(ships_planframe[0, :, 0]), v)
            time_array2, sat2_pos_1D  = self._lorentz_transform(time_planframe, utils.km_to_AU(ships_planframe[1, :, 0]), v)
            time_array3, sat3_pos_1D  = self._lorentz_transform(time_planframe, utils.km_to_AU(ships_planframe[2, :, 0]), v)
            time_array4, sat4_pos_1D  = self._lorentz_transform(time_planframe, utils.km_to_AU(ships_planframe[3, :, 0]), v)
            time_arrayp, planet_pos_1D = self._lorentz_transform(time_planframe, utils.km_to_AU(planet_pos_planframe[:,0]), v)

            if reference_system == 1:
                time_array = np.linspace(0, (time_array1[-1] - time_array1[0]), N)
            if reference_system == 2:
                time_array = np.linspace(0, (time_array2[-1] - time_array2[0]), N)


            sat1_pos_1D  = interpolate.interp1d(time_array1, sat1_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)
            sat2_pos_1D  = interpolate.interp1d(time_array2, sat2_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)
            sat3_pos_1D  = interpolate.interp1d(time_array3, sat3_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)
            sat4_pos_1D  = interpolate.interp1d(time_array4, sat4_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)
            planet_pos_1D  = interpolate.interp1d(time_arrayp, planet_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)


            ships[0, :, 0] = utils.AU_to_km(sat1_pos_1D)
            ships[1, :, 0] = utils.AU_to_km(sat2_pos_1D)
            ships[2, :, 0] = utils.AU_to_km(sat3_pos_1D)
            ships[3, :, 0] = utils.AU_to_km(sat4_pos_1D)
            planet_pos[:,0] = utils.AU_to_km(planet_pos_1D)
            cam_pos[:,0] = 0.#cam_pos_1D*AU_to_km
            for i in range(N-1):
                cam_dir[i,:] = ships_center - cam_pos[i,:]

        else:
            print ('You can only choose the reference system as 0 (planet system) 1 (student nr. 1) or 2 (student nr. 2)')
            raise ValueError('reference system invalid')


        object_name = ['student 1', 'student 2', 'ship 3', 'ship 4']
        object_string = ['satellite', 'satellite', 'satellite', 'satellite']


        km_to_AU = 1e3/const.AU

        planet_pos *= km_to_AU
        ships *= km_to_AU
        cam_pos *= km_to_AU
        cam_dir *= km_to_AU


        other_objects = []
        message1 = []
        message2 = []
        message3 = []
        message4 = []

        for i in range(N):
            message1.append('sat 1')
            message2.append('sat 2')
            message3.append('sat 3')
            message4.append('sat 4')
        ruler_length = self._get_ruler_length(cam_dist)
        ruler = [-ruler_length/2.0, ruler_length/2.0, 10, 'km', cam_dist]

        ships[0,:,2] -= 1.5*1e-6
        ships[1,:,2] += 0
        ships[2,:,2] += 1.5*1e-6
        ships[3,:,2] += 3*1e-6

        #print(planet_pos[-1]*AU_to_km, ships[3, -1, 0]*AU_to_km)
        ship_5 = np.copy(ships[0])
        ship_5[:,0] = planet_pos[:,0]
        ship_5[:,2] = ship_5[:,2]*3


        other_objects.append([object_name[0], object_string[0], ships[0, :, :], 0.2, [50, 50, 0], message1, None, None, [0,1,0]])
        other_objects.append([object_name[1], object_string[1], ships[1, :, :], 0.2, [50, 0, 0], message2, None, None, [0,1,0]])
        other_objects.append([object_name[2], object_string[2], ships[2, :, :], 0.2, [0, 50, 0], message3, None, None, [0,1,0]])
        #other_objects.append([object_name[3], object_string[3], ships[3, :, :], 0.2, [50, 0, 50], message4, None, None, [0,1,0]])
        other_objects.append(['sphere01', 'sphere01', ship_5, 200, [1, 1, 1], ['\nSpace Station']*len(message4), None, None, [0,1,0]])  # Bug testing the planet pos
        self._write_to_xml(time_array, cam_pos, cam_dir, planet_pos, other_objects, planet_idx = planet_idx, ruler = ruler,filename=filename,cheat_light_speed=True,use_obj_scaling = 1)

    def laser_chase(self, planet_idx, increase_height=False, filename_1='laser_chase_frame_1.xml', filename_2='laser_chase_frame_2.xml', number_of_video_frames=400, write_solutions=False):
        """A fast moving spaceship emits two successive laser beams, which are observed from the frame of reference of a planet and the spaceship.

        Generates the XML files used in Exercise 3 in Part 2B of the lecture notes and Exercise 5 in Part 8 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.02 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 400, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        standard_height_factor = 1.02
        increase_height_factor     = 1.1          # Number of planet radiuses from planet center for scene 1 to take place
        cam_away_dist = utils.km_to_AU(700)          # Distance to move camera away from movement axis
        ruler_ticks = 21                      # Number of ruler ticks, scene 1
        ref_frame_movement_dist = 2000        # In [km] !!!!!!
        nbeam = 2

        random_state = np.random.RandomState(self.seed + utils.get_seed('laser_chase'))

        light_speed_int = random_state.randint(890, 930)
        ref_frame_speed = light_speed_int*const.c_AU_pr_s/1000.0
        ref_frame_movement = utils.km_to_AU(np.linspace(-ref_frame_movement_dist/2, ref_frame_movement_dist/2, N))                   # Movement of the ship reference frame [AU]


        if increase_height is False:
            events_radius = utils.km_to_AU(self.system.radii[planet_idx])*standard_height_factor                     # Distance from planet center     [AU]
        elif increase_height is True:
            events_radius = utils.km_to_AU(self.system.radii[planet_idx])*increase_height_factor
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                events_radius = utils.km_to_AU(self.system.radii[planet_idx])*(standard_height_factor + 0.01*increase_height)
            else:
                events_radius = utils.km_to_AU(self.system.radii[planet_idx])*(standard_height_factor - 0.01*increase_height)


        dist_from_star = np.hypot(self.system.initial_positions[0, planet_idx], self.system.initial_positions[1, planet_idx]) # Planet distance from star       [AU]
        planet_pos = np.array([0, 0, 0])                                  # Planet stationary on x axis     [AU]

        rocket_pos_1D = np.zeros(N)
        laser_pos_1D = np.zeros((N,nbeam))
        laser_visibility =np.zeros((N,nbeam))
        i_emit = np.zeros(nbeam)
        i_emit[0] = N/10
        i_emit[1] = 6*N/10

        end_time = (ref_frame_movement[-1] - ref_frame_movement[0])/(ref_frame_speed)
        time_array = np.linspace(0, end_time, N)
        dt = time_array[1] - time_array[0]

        dx = (time_array[-1] - time_array[-2])*const.c_AU_pr_s
        for i in range(0,nbeam):
            laser_pos_1D[0:int(i_emit[i])+1,i] = ref_frame_movement[0:int(i_emit[i])+1]

        for j in range(nbeam):
            for i in range(int(i_emit[j]),N-1):
                laser_pos_1D[i+1,j] = laser_pos_1D[i,j] + dx
                laser_visibility[i,j] = 1

        # 3D arrays
        cam_pos = np.zeros(shape = (N,3))
        rocket_pos = np.zeros(shape = (N,3))
        laser_pos = np.zeros(shape = (N,nbeam,3))

        # All objects move with the ref frame (except the laser and camera,
        # which now are stationary
        rocket_pos[:,2] = rocket_pos_1D + ref_frame_movement
        laser_pos[:,:,2] = laser_pos_1D# + rocket_pos[0,2] # Starts out at rocket then moves with speed of light relative to planet
        cam_pos[:,2] = np.average(rocket_pos[:,2]) #- 100.*km_to_AU# Camera in the middle of the movement
        cam_pos[:,1] -= cam_away_dist # Moving camera away from movement


        # Translating every position to outside the planet (negtive x direction)
        cam_pos[:,0] -= events_radius
        rocket_pos[:,0] -= events_radius
        laser_pos[:,:,0] -= events_radius

        cam_dir = [0,1,0]
        cam_upvec = [-1,0,0]


        sat_message_list = None
        light_message_list = None

        ruler_length = utils.AU_to_km(self._get_ruler_length(cam_away_dist))


        ruler = [-ruler_length/2., ruler_length/2., ruler_ticks, 'km', utils.AU_to_km(cam_away_dist)]
        planet_pos = np.zeros((N,3))

        other_objects = [self._object_list('lsr1', 'Laser', laser_pos[:,0,:], 4, [50,50,0], msg_list = light_message_list, visible = laser_visibility[:,0]),
                         self._object_list('lsr2', 'Laser', laser_pos[:,1,:], 4, [50,0,0], msg_list = light_message_list, visible = laser_visibility[:,1]),
                         self._object_list('rocket1', 'Satellite', rocket_pos, 0.1, [3,3,3], msg_list = sat_message_list, orient = [0,0,-1])]



        global_messages = ['']*N

        for i in range(N):
            if laser_visibility[i,0] == 1:
                global_messages[i] += 'First laser emission: Time = %f ms, Spaceship position = %f km\n' %(time_array[int(i_emit[0])]*1000, utils.AU_to_km(rocket_pos[int(i_emit[0]),2]))
                if laser_visibility[i,1] == 1:
                    global_messages[i] += 'Second laser emission: Time = %f ms, Spaceship position = %f km, First laser position = %f km' %(time_array[int(i_emit[1])]*1000, utils.AU_to_km(rocket_pos[int(i_emit[1]),2]), utils.AU_to_km(laser_pos[int(i_emit[1]),0,2]))



        self._write_to_xml(time_array, cam_pos, cam_dir, planet_pos, other_objects, camera_messages = global_messages, ruler = ruler,
                             planet_idx=planet_idx, up_vec=cam_upvec, laser_scale = 0.2, filename = filename_1)



        global_messages = ['' for i in range(N)]
        rocket_pos_shipframe = np.copy(rocket_pos)
        planet_pos_shipframe = np.copy(planet_pos)
        laser_pos_shipframe = np.copy(laser_pos)
        time_laser_shipframe = np.zeros((N,nbeam))
        time_shipframe, rocket_pos_shipframe[:,2] = self._lorentz_transform(time_array, rocket_pos[:,2], ref_frame_speed)
        time_planet_shipframe, planet_pos_shipframe[:,2] = self._lorentz_transform(time_array, planet_pos[:,2], ref_frame_speed)
        for i in range(nbeam):
            time_laser_shipframe[:,i], laser_pos_shipframe[:,i,2] = self._lorentz_transform(time_array, laser_pos[:,i,2], ref_frame_speed)

        time_emit_shipframe = np.zeros(nbeam)
        for i in range(nbeam):
            time_emit_shipframe[i] = time_laser_shipframe[int(i_emit[i]),i]


        i_sametime = np.argmin(np.abs(time_laser_shipframe[:,0] - time_laser_shipframe[int(i_emit[1]),1]))

        time_shipframe0 = time_shipframe
        gamma = 1./np.sqrt(1.-(ref_frame_speed/const.c_AU_pr_s)**2)
        t2 = time_shipframe[-1] + (time_shipframe[-1] - time_shipframe[0])*4.
        time_shipframe = np.linspace(0,t2,N)

        i_sametime = np.argmin(np.abs(time_shipframe - time_laser_shipframe[int(i_emit[1]),1]))

        planet_pos_shipframe[:,2] = interpolate.interp1d(time_planet_shipframe, planet_pos_shipframe[:,2], kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_shipframe)
        rocket_pos_shipframe[:,2] = interpolate.interp1d(time_shipframe0, rocket_pos_shipframe[:,2], kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_shipframe)
        for i in range(nbeam):
            laser_pos_shipframe[:,i,2] = interpolate.interp1d(time_laser_shipframe[:,i], laser_pos_shipframe[:,i,2], kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_shipframe)



        laser_visibility[:,:] = 1
        i_emit_shipframe = np.copy(i_emit)
        for i in range(nbeam):
            i_emit_shipframe[i] = np.argmin(np.abs(time_emit_shipframe[i] - time_shipframe))
            laser_visibility[0:int(i_emit_shipframe[i]),i] = 0


        other_objects = [self._object_list('lsr1', 'Laser', laser_pos_shipframe[:,0,:], 4, [50,50,0], msg_list = light_message_list, visible = laser_visibility[:,0]),
                         self._object_list('lsr2', 'Laser', laser_pos_shipframe[:,1,:], 4, [50,0,0], msg_list = light_message_list, visible = laser_visibility[:,1]),
                         self._object_list('rocket1', 'Satellite', rocket_pos_shipframe, 0.1, [3,3,3], msg_list = sat_message_list, orient = [0,1,-1])]

        cam_pos[:,2] = np.average(rocket_pos_shipframe[:,2])

        for i in range(N):
            if laser_visibility[i,0] == 1:
                global_messages[i] += 'First laser emission: Time = %f ms, Planet position = %f km\n' %(time_shipframe[int(i_emit_shipframe[0])]*1000, utils.AU_to_km(planet_pos_shipframe[int(i_emit_shipframe[0]),2])-utils.AU_to_km(rocket_pos_shipframe[int(i_emit_shipframe[0]),2]))
                if laser_visibility[i,1] == 1:
                    global_messages[i] += 'Second laser emission: Time = %f ms, Planet position = %f km, First laser position = %f km' %(time_shipframe[int(i_emit_shipframe[1])]*1000, utils.AU_to_km(planet_pos_shipframe[int(i_emit_shipframe[1]),2])-utils.AU_to_km(rocket_pos_shipframe[int(i_emit_shipframe[1]),2]), utils.AU_to_km(laser_pos_shipframe[int(i_emit_shipframe[1]),0,2])-utils.AU_to_km(rocket_pos_shipframe[int(i_emit_shipframe[1]),2]))


        self._write_to_xml(time_shipframe, cam_pos, cam_dir, planet_pos_shipframe, other_objects, camera_messages = global_messages, ruler = ruler,
                             planet_idx=planet_idx, up_vec=cam_upvec, laser_scale = 0.2, filename = filename_2)

        light_beam_distance_planet = utils.AU_to_km(laser_pos[int(i_emit[1]),0,2]) - utils.AU_to_km(rocket_pos[int(i_emit[1]),2])
        light_beam_distance_spaceship = utils.AU_to_km(laser_pos_shipframe[int(i_emit_shipframe[1]),0,2])-utils.AU_to_km(rocket_pos_shipframe[int(i_emit_shipframe[1]),2])

        if write_solutions:
            #Solution writing
            solution_name='Solutions_laser_chase.txt'
            solution_2B=self._get_new_solution_file_handle(solution_name)
            solution_2B.write('Solutions to 2B.3\n')
            solution_2B.write('1) The velocity for the planet/spaceship v = %f\n' %(light_speed_int/1000))
            #solution_2B.write('2. No numerical answer\n')
            #solution_2B.write('3. No numerical answer\n')
            #solution_2B.write('4. No numerical answer\n')
            #solution_2B.write('5. The light beam always has the speed of light\n')
            #solution_2B.write('6. No numerical answer\n')
            solution_2B.write('6) Planet frame: L = %f km. Spaceship frame: L\' = %f km. Ratio r = L/L\' = %f\n' %(light_beam_distance_planet, light_beam_distance_spaceship, light_beam_distance_planet/light_beam_distance_spaceship))
            #solution_2B.write('8. No numerical answer\n')
            solution_2B.close()

    def neutron_decay(self, planet_idx, increase_height=False, filename_1='neutron_decay_frame_1.xml', filename_2='neutron_decay_frame_2.xml', number_of_video_frames=1200, write_solutions=False):
        """A fast moving neutron disintegrates spontaneously, and a proton and an electron are seen to continue in the same direction.

        Generates the XML files used in Exercise 4 in Part 2B of the lecture notes and Exercise 6 in Part 8 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.05 planet radii to be used. Using True increases this to 1.2.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1200, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        self._neutron_decay_single_frame(planet_idx, 0, increase_height, filename_1, N, write_solutions)
        self._neutron_decay_single_frame(planet_idx, 1, increase_height, filename_2, N, write_solutions)

    def _neutron_decay_single_frame(self, planet_idx, reference_system, increase_height, filename, N, write_solutions):

        random_state = np.random.RandomState(self.seed + utils.get_seed('neutron_decay'))

        radius = self.system.radii[planet_idx] # [km]
        dt = 1e-5/2
        ships = np.zeros((4, N, 3))
        planet_pos0 = np.array((0, 0, 0))  #[AU]
        planet_pos = np.zeros((N, 3))

        if increase_height is False:
            height = 1.05*radius
        elif increase_height is True:
            height = 1.2*radius
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                height = radius*(1.05 + 0.01*increase_height)
            else:
                height = radius*(1.05 - 0.05*increase_height)

        masselectron = 9.10938188e-31
        massproton = 1.67262158e-27
        massneutron = 1.67492747e-27

        gammapp = (massneutron**2+massproton**2-masselectron**2)/(2.*massproton*massneutron)
        vproton_shipframe = -np.sqrt(1.-1./gammapp**2)
        cc = (vproton_shipframe*gammapp*massproton/masselectron)**2
        velectron_shipframe = np.sqrt(cc/(1.+cc))*const.c_km_pr_s
        vproton_shipframe *= const.c_km_pr_s

        v = random_state.randint(800,900)/1000.*const.c_km_pr_s
        vel = np.zeros((4, 3))
        #vel[0, 2] = random_state.randint(99900,99999)/100000.*const.c_km_pr_s
        #vel[1, 2] = random_state.randint(990.,998.)/1000.*const.c_km_pr_s
        #vel[0, 2] = random_state.randint(990,999)/1000.*const.c_km_pr_s
        #vel[1, 2] = random_state.randint(700.,900.)/1000.*const.c_km_pr_s
        vel[0,2] = self._velocity_transformation(-v/const.c_km_pr_s,velectron_shipframe/const.c_km_pr_s)*const.c_km_pr_s
        vel[1,2] = self._velocity_transformation(-v/const.c_km_pr_s,vproton_shipframe/const.c_km_pr_s)*const.c_km_pr_s
        cam_pos = np.zeros((N, 3))
        cam_dir = np.zeros((N, 3))
        time_planframe = np.zeros((N))
        gamma1 = 1./np.sqrt(1.-(vel[0,2]/const.c_km_pr_s)**2)
        gamma2 = 1./np.sqrt(1.-(vel[1,2]/const.c_km_pr_s)**2)


        # Setting initial conditions
        for i in range(2):
            if i == 0:                                                          # student 1
                ships[0, 0, :] = np.array((-height, 0, -500))
            if i == 1:                                                          # student 2
                ships[1, 0, :] = np.array((-height, 0, -475))

            # distance between camera and ships in y-direction
        cam_dist = 500*(1.+reference_system)
        ships_center = np.array((-height, 0,0))

        # In the planet system

        cam_pos[0, :] = ships_center + np.array((0, -cam_dist,0))
        cam_dir[0, :] = ships_center - cam_pos[0, :]
        for i in range(N-1):
            time_planframe[i+1] = (i+1)*dt
            planet_pos[i+1, :] = planet_pos[0, :]
            cam_pos[i+1, :] = ships_center + np.array((0, -cam_dist,0 ))
            cam_dir[i+1, :] = ships_center - cam_pos[i+1, :]
            for ship in range(0, 4):
                ships[ship, i+1, :] = ships[ship, i, :] + vel[ship,:]*dt

        ihit = np.argmin(np.abs(ships[0, :, 2] - ships[1, :, 2]))
                #v_cons = ((masselectron*gamma1*vel[0,2]/const.c_km_pr_s+massproton*gamma2*vel[1,2]/const.c_km_pr_s)/(massneutron))**2
        #v = np.sqrt(v_cons/(1.+v_cons))*const.c_km_pr_s

        gammatot = 1./np.sqrt(1.-(v/const.c_km_pr_s)**2)
        masstot = (masselectron*gamma1 + massproton*gamma2)/gammatot
        newvel = np.array([0,0,v])

        ships_planframe = np.copy(ships)
        planet_pos_planframe = np.copy(planet_pos)
        cam_pos_planframe = np.copy(cam_pos)
        s2orient= [0,0,1]

        if reference_system == 0:
            factor = 1
            time_array = np.linspace(0, dt*N, N)

        # In the refenrece system of student 1
        elif reference_system == 1:
            factor = 2
            s2orient = [0,0,-1]
            v = utils.km_to_AU(newvel[2])

            time_array1, sat1_pos_1D = self._lorentz_transform(time_planframe, utils.km_to_AU(ships_planframe[0, :, 2]), v)
            time_array2, sat2_pos_1D  = self._lorentz_transform(time_planframe, utils.km_to_AU(ships_planframe[1, :, 2]), v)
            time_arrayp, planet_pos_1D = self._lorentz_transform(time_planframe, utils.km_to_AU(planet_pos_planframe[:,2]), v)


            if reference_system == 1:
                time_array = np.linspace(0, (time_array1[-1] - time_array1[0]), N) + time_array1[0]
            if reference_system == 2:
                time_array = np.linspace(0, (time_array2[-1] - time_array2[0]), N)


            sat1_pos_1D  = interpolate.interp1d(time_array1, sat1_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)
            sat2_pos_1D  = interpolate.interp1d(time_array2, sat2_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)
            planet_pos_1D  = interpolate.interp1d(time_arrayp, planet_pos_1D , kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)(time_array)

            time_array -= time_array1[0]

            ships[0, :, 2] = utils.AU_to_km(sat1_pos_1D)
            ships[1, :, 2] = utils.AU_to_km(sat2_pos_1D)
            planet_pos[:,2] = utils.AU_to_km(planet_pos_1D)
            cam_pos[:,2] = 0#cam_pos_1D*AU_to_km
            for i in range(N-1):
                cam_dir[i,:] = ships_center - cam_pos[i,:]

        else:
                print ('You can only choose the reference system as 0 (planet system) 1 (student nr. 1) or 2 (student nr. 2)')
                raise ValueError('Reference system invalid')


        object_name = ['Electron', 'Proton', 'Neutron', 'Crash']
        object_string = ['sphere01', 'sphere01', 'sphere01', 'explosion']
        explosion_rgb = [50,50,0]
        neutron_expl_pos = np.zeros((N,3))
        neutron = np.zeros((N, 3))

        if reference_system == 0:
            visual_hit = ihit + 20*2
            neutron_expl_pos[visual_hit, :] = (ships[0, visual_hit, :] + 2*ships[1, visual_hit, :])/3
            for i in range(visual_hit+1,N):
                neutron_expl_pos[i] = newvel*dt + neutron_expl_pos[i-1]

            neutron[visual_hit] = neutron_expl_pos[visual_hit]
            for i in range(N-visual_hit, N):
                neutron[-i-1] = neutron[-i] - newvel*dt
            for i in range(visual_hit+1, N):
                neutron[i] = neutron[-i] + newvel*dt

        else:
            visual_hit = np.argmin(np.abs(sat1_pos_1D - sat2_pos_1D)) + 20*factor*2
            #visual_hit=np.int(N/2)
            neutron_expl_pos[visual_hit:, :] = (ships[0, visual_hit, :] + 2*ships[1, visual_hit, :])/3
            neutron[:, :] = neutron_expl_pos[visual_hit]
            cam_pos[:,2] = neutron_expl_pos[visual_hit,2]

        ships_visible = np.zeros(N)
        expl_visible = np.zeros(N)
        ships_visible[:visual_hit] = 1
        expl_visible[visual_hit : visual_hit+int(N/16)] = 1


        #for i in range(N):
        #    ships[:, i, :] -= planet_pos[i, :]
        #    cam_pos[i, :] -=planet_pos[i, :]

        km_to_AU = 1e3/const.AU

        planet_pos *= km_to_AU
        ships *= km_to_AU
        cam_pos *= km_to_AU
        cam_dir *= km_to_AU
        neutron_expl_pos *= km_to_AU
        neutron *= km_to_AU



        ruler_length = self._get_ruler_length(cam_dist)
        ruler = [-ruler_length/2.0, ruler_length/2.0, 10, 'km', cam_dist]

        other_objects = [self._object_list(object_name[0], object_string[0], ships[0, :, :], 15*factor, [0, 0, 255], visible = [1 if i > visual_hit else 0 for i in range(N)], msg_list = ['\nElectron' if i > visual_hit else '' for i in range(N)]),
                         self._object_list(object_name[1], object_string[1], ships[1, :, :], 30*factor, [255, 0, 0], visible = [1 if i > visual_hit else 0 for i in range(N)], msg_list = ['\n\nProton' if i > visual_hit else '' for i in range(N)]),
                         self._object_list(object_name[2], object_string[2], neutron, 35*factor, [1, 1, 1], visible = [1 if i <= visual_hit else 0 for i in range(N)], msg_list = ['\n\nNeutron' if i <= visual_hit else '' for i in range(N)]),
                         self._object_list(object_name[3], object_string[3], neutron_expl_pos, 1000*factor, explosion_rgb, visible = expl_visible)]

        # Adding messages
        if reference_system == 0:
            global_messages = ['Mass of small ship: %g kg, mass of large ship: %g kg, mass of combined ships: %g kg\n' %(masselectron, massproton, masstot)]*N
            for i in range(N):
                if i >= visual_hit:
                    global_messages[i] += 'Initial neutron position: %f km, time: %f ms. ' %(utils.AU_to_km(neutron_expl_pos[visual_hit, 2]), time_array[visual_hit]*1000)
                if i >= visual_hit+150:
                    global_messages[i] += 'Second neutron position: %f km, time: %f ms.\n' %(utils.AU_to_km(neutron_expl_pos[visual_hit+150, 2]), time_array[visual_hit+150]*1000)

        else:
            global_messages = ['Mass of small ship: %g kg, mass of large ship: %g kg, mass of combined ships: %g kg\n' %(masselectron, massproton, masstot)]*N
            for i in range(N):
                if i >= visual_hit:
                    global_messages[i] += 'Planet position when fusion: %f km, time: %f ms. ' %(utils.AU_to_km(planet_pos[visual_hit, 2]), time_array[visual_hit]*1000)
                if i >= visual_hit+150:
                    global_messages[i] += 'Planet position a bit later: %f km, time: %f ms.\n' %(utils.AU_to_km(planet_pos[visual_hit+150, 2]), time_array[visual_hit+150]*1000)
        global_messages = ['']*N  #To avoid deleting the other text incase of change in exercise

        for i in range(N):
            if reference_system == 0:
                global_messages[i] += 'Velocity of neutron: %f c\nElectron mass: 9.10938188e-31 kg, Proton mass 1.67262158e-27 kg,  Neutron mass: 1.67492747e-27 kg'%(v/const.c_km_pr_s)
            else:
                global_messages[i] += 'Velocity of labframe (planet): %f c\nElectron mass: 9.10938188e-31 kg, Proton mass 1.67262158e-27 kg,  Neutron mass: 1.67492747e-27 kg'%(-utils.AU_to_km(v)/const.c_km_pr_s)

        self._write_to_xml(time_array, cam_pos, cam_dir, planet_pos, other_objects, planet_idx = planet_idx, ruler = ruler,filename=filename,cheat_light_speed=True,use_obj_scaling = 1, up_vec = [-1,0,0], camera_messages = global_messages, show_clock = 0, toggle_clock = False)

        if write_solutions:

            #Soultion writing
            if reference_system == 0:
                v = v/const.c_km_pr_s
                vel = vel/const.c_km_pr_s

                momenergy_electron =  1/np.sqrt(1-vel[0,2]**2)*masselectron*np.array([1.0, vel[0,2]])
                momenergy_proton =  1/np.sqrt(1-vel[1,2]**2)*massproton*np.array([1.0, vel[1,2]])
                print('Electron momenergy: (%g, %g)' % tuple(momenergy_electron))
                print('Proton momenergy: (%g, %g)' % tuple(momenergy_proton))


                solution_name='Solutions_neutron_decay.txt'
                solution_2B=self._get_new_solution_file_handle(solution_name)
                solution_2B.write('Solutions to 2B.4\n')
                solution_2B.write('\n')
                #solution_2B.write('1. No numerical solution\n')
                #solution_2B.write('2. No numerical solution\n')
                #solution_2B.write('3. The velocity of the neutron: v_n = %f\n' %(v))
                #solution_2B.write('4. No numerical solution\n')
                #solution_2B.write('5. No numerical solution\n')
                #solution_2B.write('6. No numerical solution\n')
                solution_2B.write('4) The velocity of the electron: v_e\' = %f. The velocity of the proton: v_p\' = %f\n' %(velectron_shipframe/const.c_km_pr_s, vproton_shipframe/const.c_km_pr_s))
                solution_2B.write('5) Electron: E = %g [kg], p = %g [kg]. Proton: E = %g [kg], p = %g [kg]\n' %(momenergy_electron[0], momenergy_electron[1], momenergy_proton[0], momenergy_proton[1]))
                solution_2B.write('6) The velocity of the electron: v_e = %f. The velocity of the proton: v_p = %f\n' %(vel[0,2], vel[1,2]))
                #solution_2B.write('10. No numerical solution\n')
                #solution_2B.write('11. No numerical solution\n')
                #solution_2B.write('12. The answer is still the same as earlier\n')
                #solution_2B.write('13. The answer is still the same as earlier\n')
                solution_2B.close()

    def antimatter_spaceship(self, planet_idx, increase_height=False, filename_1='antimatter_spaceship_frame_1.xml', filename_2='antimatter_spaceship_frame_2.xml', number_of_video_frames=400, write_solutions=False):
        """An antimatter spaceship and an ordinary spaceship travel towards each other close to the speed of light, before annihilating and producing photons with identical wavelengths.

        Generates the XML files used in Exercise 5 in Part 2B of the lecture notes and Exercise 7 in Part 8 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.015 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 400, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        standard_height_factor = 1.015
        increase_height_factor     = 1.10
        m_rest                 = 1000000                   # Rest mass of a spaceship [kg]
        cam_away_dist          = utils.km_to_AU(1000)
        ruler_ticks            = 10
        ship_travel_dist = 1000                # Distance the ships move before they crash [km]

        random_state = np.random.RandomState(self.seed + utils.get_seed('antimatter_spaceship'))

        if increase_height is False:
            events_radius = utils.km_to_AU(self.system.radii[planet_idx])*standard_height_factor                     # Distance from planet center     [AU]
        elif increase_height is True:
            events_radius = utils.km_to_AU(self.system.radii[planet_idx])*increase_height_factor                     # Distance from planet center     [AU]
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                events_radius = utils.km_to_AU(self.system.radii[planet_idx])*(standard_height_factor + 0.01 * increase_height)
            else:
                events_radius = utils.km_to_AU(self.system.radii[planet_idx])*(standard_height_factor - 0.01 * increase_height)

        deltalambda = random_state.randint(75,250)
        lambda_m = random_state.randint(380+deltalambda, 680)
        deltalambda *= 1e-9
        lambda_m *= 1e-9
        dlamlam = ((deltalambda/lambda_m)+1.)**2
        ship_speeds = (dlamlam-1.)/(dlamlam+1.)
                #Calculating stuff for the task after photon wavelengths are chosen
        gamma                  = 1 / np.sqrt(1 - ship_speeds**2)
        h = 6.626069934e-34              # Plancks constant [Js]
        n_photons = 2.*gamma*m_rest*const.c**2*lambda_m/(h*const.c)
        explosion_rgb = self._lambda_to_RGB(lambda_m)
        ship_speeds *= const.c_AU_pr_s

        dist_from_star = np.hypot(self.system.initial_positions[0, planet_idx], self.system.initial_positions[1, planet_idx]) # Planet distance from star       [AU]
        planet_pos = np.array([0, 0, 0])                                  # Planet stationary on x axis     [AU]

        rocket_pos_1D = utils.km_to_AU(np.linspace(-ship_travel_dist, ship_travel_dist, N))
        rocket2_pos_1D = utils.km_to_AU(np.linspace(ship_travel_dist, -ship_travel_dist, N))

        end_time = np.abs(rocket_pos_1D[-1] - rocket_pos_1D[0])/ship_speeds # seconds
        time_array = np.linspace(0, end_time, N)
        dt = time_array[1] - time_array[0]
        i_crash = np.argmin(np.abs(rocket_pos_1D - rocket2_pos_1D)) # Index where the spaceships are closest togehter, this is when they crash

        # Visibility of spacehips and explosions
        ships_visible = np.ones(N)
        ships_visible[i_crash:] = 0
        explosions_visible = 1 - ships_visible

        # 3D arrays
        cam_pos = np.zeros(shape = (3,))
        rocket_pos = np.zeros(shape = (N,3))
        rocket2_pos = np.zeros(shape = (N,3))
        expl_pos = np.zeros(shape = (N,3))
        planet_pos = np.zeros(shape = (N,3))

        # Cast positions to 3d array z axis
        rocket_pos[:,2] = rocket_pos_1D
        rocket2_pos[:,2] = rocket2_pos_1D
        cam_pos[2] = 0
        cam_pos[1] -= cam_away_dist # Moving camera away from movement

        # Translating every position to outside the planet (negtive x direction)
        cam_pos[0] -= events_radius
        rocket_pos[:,0] -= events_radius
        rocket2_pos[:,0] -= events_radius
        expl_pos[:,0] -= events_radius

        rocket3_pos = np.copy(rocket_pos)
        rocket3_pos[:,2] -= utils.km_to_AU(100)

        cam_dir = [0,1,0]
        cam_upvec = [-1,0,0]



        #Print info to student
        global_messages_s1 = ['' for i in range(N)]
        for i in range (N):
            global_messages_s1[i] += 'Spaceship rest mass = %g kg\n'%(m_rest)
            global_messages_s1[i] += 'Leftmost spaceship velocity = %gc\n'%(utils.AU_to_km(ship_speeds)/const.c_km_pr_s)
        for i in range (i_crash,N):
            global_messages_s1[i] += 'Number of photons emitted = %g'%(n_photons)


        other_objects = [self._object_list('rocket2', 'Satellite', rocket2_pos, 0.08, [5,5,0], visible = ships_visible),
                         self._object_list('rocket1', 'Satellite', rocket_pos, 0.08, [5,5,5], visible = ships_visible),
                         self._object_list('rocket3', 'Satellite', rocket3_pos, 0.04, [5,0,0], visible = ships_visible),
                         self._object_list('Expl', 'explosion', expl_pos, 3000, explosion_rgb, visible = 1 - ships_visible)]

        self._write_to_xml(time_array, cam_pos, cam_dir, planet_pos, other_objects, camera_messages = global_messages_s1,
                             planet_idx=planet_idx, up_vec=cam_upvec, laser_scale = 0.2, filename = filename_1,
                             ruler = [0, utils.AU_to_km(self._get_ruler_length(cam_away_dist)), ruler_ticks, 'km', utils.AU_to_km(cam_away_dist)])

        # SCENE 2 (Same ship positions) Reference system of left rocket (rocket 1)
        rocket1_s2_1D_func = self._ref_sys_interpolate_func(time_array, rocket_pos_1D, ship_speeds) # Callable function. 1D rocket positions. Should be static.
        rocket2_s2_1D_func = self._ref_sys_interpolate_func(time_array, rocket2_pos_1D, ship_speeds) # Callable function. Should move really fast towards rocket 1.

        time_array1_s2 = self._lorentz_transform(time_array, rocket_pos_1D, ship_speeds)[0]
        time_array2_s2 = self._lorentz_transform(time_array, rocket2_pos_1D, ship_speeds)[0]

        ts = time_array1_s2                 # Using the first, the two arrays are very similar

        rocket1_s2_1D = rocket1_s2_1D_func(ts)
        rocket2_s2_1D = rocket2_s2_1D_func(ts)


        # Reference system moves relative to planet with rocket 1 (technically the planet is moving back with rocket 1's speed seen from the planet)
        time_in_s2 = ts[-1] - ts[0]
        dist_ref_frame2 = ship_speeds*time_in_s2
        start = -dist_ref_frame2/2
        stop = -start
        ref_sys_movement = np.linspace(start, stop, N)
        planet_pos[:,2] = np.linspace(0,-ship_speeds*time_in_s2,N)


        #cast to 3D
        rocket1_s2 = np.zeros( shape = (N, 3))
        rocket2_s2 = np.zeros( shape = (N, 3))

        rocket1_s2[:,2] = rocket1_s2_1D - rocket1_s2_1D[0] + utils.km_to_AU(1.)
        rocket2_s2[:,2] = rocket2_s2_1D - rocket1_s2_1D[0] + utils.km_to_AU(1.)
        rocket2_rel2_rocket1 = np.copy(rocket2_s2)
        cam_pos_s2 = np.copy(rocket1_s2) # For now is inside rocket




        global_messages_s2 = ['' for i in range(N)]
        vel = ship_speeds/const.c_AU_pr_s
        for i in range (N):
            global_messages_s2[i] += 'Spaceship rest mass = %g kg\n' % m_rest
            global_messages_s2[i] += 'The velocity of the ground = %gc\n' %(-vel)
        for i in range (i_crash,N):
            global_messages_s2[i] +=  'Number of photons emitted = %g'%(n_photons)


        #Translate positions to outside the planet in negative x dir
        cam_pos_s2[:,0] -= events_radius
        rocket1_s2[:,0] -= events_radius
        rocket2_s2[:,0] -= events_radius

        #rocket2_s2[:,2] = rocket1_s2[:,2] + rocket2_rel2_rocket1[:,2] #making sure its correct

        tiltcamera =  np.linspace(utils.km_to_AU(50), utils.km_to_AU(-50), N)
        # Moving camera above spaceship
        #cam_pos_s2[:,0] -= 100*km_to_AU
        cam_pos_s2[:,2] += utils.km_to_AU(-100)
        cam_pos_s2[:,1] -= tiltcamera
        #cam_pos_s2[:,1] -= cam_away_dist
        # Find crash site, make camera focus on this
        i_crash_s2 = np.argmin(np.abs(rocket1_s2_1D - rocket2_s2_1D))
        crash_site_s2 = rocket1_s2[i_crash_s2]
        cam_dir_s2 = crash_site_s2 - cam_pos_s2 # Point at the crash site
        cam_upvec_s2 = cam_pos_s2/np.linalg.norm(cam_pos_s2)

        expl_rgb_s2 = (random_state.uniform(0.9, 1), 0, 0)

        expl_message_list = [''' ''' for i in range(N)]

        explosion_rgb_shift = self._lambda_to_RGB(lambda_m - deltalambda)


        other_objects_s2 = [['rocket2', 'Satellite', rocket2_s2, 0.05, [1,1,0], None, None, ships_visible, [0,0,1]],
                            ['rocket1', 'Satellite', rocket1_s2, 0.05, [1,1,1], None, None, ships_visible, [0,0,-1]],
                            self._object_list('expl', 'explosion', expl_pos, 1000, color_rgb = explosion_rgb_shift, visible = 1 - ships_visible)]



        self._write_to_xml(ts - ts[0], cam_pos_s2, cam_dir_s2, planet_pos, other_objects_s2, use_obj_scaling = 0,
                             planet_idx = planet_idx, up_vec = cam_upvec_s2, filename = filename_2, camera_messages = global_messages_s2, cheat_light_speed = True)

        #Solution writing

        ship_B_vel = (utils.AU_to_km(rocket2_s2_1D[50]-rocket2_s2_1D[0])/(ts[50] - ts[0])/const.c_km_pr_s)
        electron_mass = 9.10938356e-31
        k = ((lambda_m - deltalambda)*gamma*electron_mass*const.c_km_pr_s*1000/h-2.)**2

        if write_solutions:
            solution_name='Solutions_antimatter_spaceship.txt'
            solution_2B=self._get_new_solution_file_handle(solution_name)
            solution_2B.write('Solutions to 2B.5\n')
            solution_2B.write('1) Spaceship B velocity seen from spaceship A: v_B\' = %gc\n' % ship_B_vel)
            #solution_2B.write('2. No numerical solution\n')
            #solution_2B.write('3. No numerical solution\n')
            #solution_2B.write('4. No numerical solution\n')
            #solution_2B.write('5. No numerical solution\n')
            #solution_2B.write('6. No numerical solution\n')
            solution_2B.write('8) The total energy of a photon: E = 2m*gamma/n = %g kg. The wavelength in the planet frame: lambda = %g nm\n' %(2*m_rest*gamma/n_photons, lambda_m*1e9))
            #solution_2B.write('8. The correct RBG color code: %s\n' %explosion_rgb)
            #solution_2B.write('9. No numerical solution (the energy of the photons must equal the energy of the spaceship)\n')
            #solution_2B.write('10. No numerical solution (E=h/lambda)\n')
            #solution_2B.write('11. No numerical solution\n')
            solution_2B.write('12. The wavelength in the spaceship frame: lambda\' = %g nm\n' % ((lambda_m - deltalambda)*1e9))
            #solution_2B.write('13. No numerical solution\n')
            solution_2B.write('14. The velocity needed: v = %.15f, you might not get exactly this number, depending on precision, but you should get a number very close to 1\n' % ((k-1.)/(k+1.)))

            solution_2B.close()

    def black_hole_descent(self, planet_idx, number_of_light_signals=30, consider_light_travel=False, text_file_dir='.', filename_1='black_hole_descent_frame_1.xml', filename_2='black_hole_descent_frame_2.xml', write_solutions=False):
        """A spaceship is falling towards a black hole while exhanging light signals with a spacecraft near an orbiting planet.

        Generates the XML and text files used in Exercise 5 in Part 2C and Exercise 2 in Part 2E of the lecture notes and Exercise 3 in Part 9 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        number_of_light_signals : int, optional
            The number of light signals sent out by the falling spaceship.
            Default is 30, but must be between 10 and 100.
        consider_light_travel : bool, optional
            Whether to take into account the traveling time of light.
            If True, note that an extra label will be added to the inputted file names to avoid conflicts with existing files.
            Default is False.
        text_file_dir : str, optional
            The path to the directory in which to generate text files containing the time intervals between successive light signals.
            If set to None, no text files will be generated.
            Default is to generate text files in the working directory.
        filename_1 : str, optional
            The filename to use for frame of reference 1.
        filename_2 : str, optional
            The filename to use for frame of reference 2.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        consider_light_travel = bool(consider_light_travel)

        filename_1 = str(filename_1)
        filename_2 = str(filename_2)

        filename_1_base = '.'.join(filename_1.split('.')[:-1]) if '.' in filename_1 else filename_1
        filename_2_base = '.'.join(filename_2.split('.')[:-1]) if '.' in filename_2 else filename_2

        filename_1 = filename_1_base + ('_with_light_travel' if consider_light_travel else '') + '.xml'
        filename_2 = filename_2_base + ('_with_light_travel' if consider_light_travel else '') + '.xml'

        if text_file_dir is None:
            write_text = False
        else:
            write_text = True

            text_file_dir = os.path.abspath(str(text_file_dir))
            if not os.path.isdir(text_file_dir):
                os.mkdir(text_file_dir)

            text_filename_1 = filename_1_base + ('_with_light_travel' if consider_light_travel else '') + '.txt'
            text_filename_2 = filename_2_base + ('_with_light_travel' if consider_light_travel else '') + '.txt'

            text_file_path_1 = os.path.join(text_file_dir, text_filename_1)
            text_file_path_2 = os.path.join(text_file_dir, text_filename_2)

        color_order_space_station = ['violet', 'blue', 'green', 'red']
        color_order_falling = ['red', 'yellow', 'blue', 'violet']

        number_of_light_signals = np.copy(number_of_light_signals)
        number_of_light_signals = int(number_of_light_signals)
        if number_of_light_signals < 10 or number_of_light_signals > 100:
            raise ValueError('number_of_light_signals must be an integer between 10 and 100')

        random_state = np.random.RandomState(self.seed + utils.get_seed('black_hole_descent'))

        nr_of_light_messages = number_of_light_signals #30 #random_state.randint(25, 30)
        M_SM = const.m_sun    # Star mass in m
        M_SM *= random_state.uniform(8e6,3e7)  #May force the skipping of certain wavelengths
        M = utils.kg_to_m(M_SM)
        r_AU = 1   # Orbiting distance of planet, and start distance of spaceship.
        planet_radius = utils.km_to_AU(self.system.radii[planet_idx])
        planet_pos = [r_AU-planet_radius*2, planet_radius*2, 0]
        r_m = utils.AU_to_m(r_AU)
        sat_start_shell_speed = random_state.randint(100, 300) * 0.001   # Interval [0.1, 0.4], see above ^
        gamma = 1/np.sqrt(1-sat_start_shell_speed**2)
        lambda0 = 200e-9
        lambda0_fromshell = 900e-9
        #print('r_AU = %g' % r_AU)
        #print('r_m = %g' % r_m)
        #print('M_SM = %g' % M_SM)
        #print('M_m = %g' % M)

        #print('Welcome to task C2. Your black hole has a mass %g Solar Masses, and your spacecraft has an initial velocity of %g c when it started \
            #falling towards the black hole at a distance of 1 AU from the black hole center.' % (M_SM, sat_far_away_speed))

        ### SCENE 1 ###
        dt = 1e9  # Time in meters between each timestep in observer shell frame. Shell time.
        time_array_sat = [0]
        time_array_obs = [0]
        sat_pos_1D = [r_m]
        energy_per_mass = np.sqrt(1.-2.*M/r_m)*gamma
        transform_faraway_to_shell = 1./np.sqrt(1.-2.*M/r_m)
        while sat_pos_1D[-1] > (2*M * 1.001):   # Outside schwarzschild radius ( with a tolerance )
            time_array_obs.append( time_array_obs[-1] + dt )
            dtau = (1-2*M/sat_pos_1D[-1])/energy_per_mass*transform_faraway_to_shell*dt
            time_array_sat.append( time_array_sat[-1] + dtau )
            sat_pos_1D.append( sat_pos_1D[-1] - np.sqrt((1-2*M/sat_pos_1D[-1])**2*(1.-(1-2*M/sat_pos_1D[-1])/energy_per_mass**2))*transform_faraway_to_shell*dt)
        sat_pos_1D = np.array(sat_pos_1D[:-1])  # Cutting off last frame.
        time_array_sat = np.array(time_array_sat[:-1])
        time_array_obs = np.array(time_array_obs[:-1])
        if self._debug: print('Task C2\nSpacecraft start pos: %e\nend pos: %e\nschwarzschild radius: %e' % (utils.m_to_AU(sat_pos_1D[0]), utils.m_to_AU(sat_pos_1D[-1]), utils.m_to_AU(2*M)))

        N = len(sat_pos_1D)  # Number of frames for last third of video.
        if self._debug: print('In C2_1 with Frames = %d' % N)

        obs_pos = np.zeros( shape=(N,3) )
        obs_pos[:,0] += r_m + 700*1000

        light_interval = (time_array_sat[-1] - time_array_sat[0])/(nr_of_light_messages+0.1)
        send_light_times_sat = np.array([ i*light_interval for i in range(0, int(nr_of_light_messages)+1) ])
        light_indexes = []   # Since there's no SR, everybody agrees on when light was sent out (Their local time will vary, but they will agree on what time index, because they correspond.)
        for i in range(len(send_light_times_sat)):
            light_indexes.append( (np.abs(send_light_times_sat[i] - time_array_sat)).argmin() )

        if consider_light_travel:
            light_indexes_emitted = np.copy(light_indexes)
            recv = []
            #print('consider1:',time_array_obs[light_indexes]/const.c)
            for i in (light_indexes):
                lightpos = np.zeros(N)
                lightpos[i] = sat_pos_1D[i]
                for j in range(i+1,N):
                    lightpos[j] = lightpos[j-1] + (1 - 2*M/lightpos[j-1]) * dt
                ii = (np.argmin(np.abs(lightpos - r_m)))
                if ii < N-1:
                    if np.sign(lightpos[ii] - r_m) != np.sign(lightpos[ii+1] - r_m) or np.sign(lightpos[ii] - r_m) != np.sign(lightpos[ii-1] - r_m):
                        recv.append(ii)
            light_indexes = recv
            #print('consider2:',time_array_obs[light_indexes]/const.c)

        else:
            lie = np.copy(light_indexes)
            recv = []
            #print('consider1:',time_array_obs[light_indexes]/const.c)
            for i in (light_indexes):
                lpsd = np.zeros(N)
                lpsd[i] = sat_pos_1D[i]
                for j in range(i+1,N):
                    lpsd[j] = lpsd[j-1] + (1 - 2*M/lpsd[j-1]) * dt
                iui = (np.argmin(np.abs(lpsd - r_m)))
                if iui < N-1:
                    if np.sign(lpsd[iui] - r_m) != np.sign(lpsd[iui+1] - r_m) or np.sign(lpsd[iui] - r_m) != np.sign(lpsd[iui-1] - r_m):
                        recv.append(iui)


        if self._debug: print ('light indexes ', np.array(light_indexes))
        if self._debug: print ('light intervals ', np.array(light_indexes[1:]) - np.array(light_indexes[:-1]))

        # Making object for sending light from spacecraft to observer.
        light_obj_pos_violet = np.zeros( shape = (N,3) ) + np.array([r_AU-0.000001, 0, 0])   # Simply putting it 0.1 AU from observer.
        light_obj_pos_blue = np.zeros( shape = (N,3) ) + np.array([r_AU-0.000001, 0, 0])
        light_obj_pos_green = np.zeros( shape = (N,3) ) + np.array([r_AU-0.000001, 0, 0])
        light_obj_pos_yellow = np.zeros( shape = (N,3) ) + np.array([r_AU-0.000001, 0, 0])
        light_obj_pos_orange = np.zeros( shape = (N,3) ) + np.array([r_AU-0.000001, 0, 0])
        light_obj_pos_red = np.zeros( shape = (N,3) ) + np.array([r_AU-0.000001, 0, 0])

        light_obj_visibility_violet = np.zeros(N)
        light_obj_visibility_blue = np.zeros(N)
        light_obj_visibility_green = np.zeros(N)
        light_obj_visibility_yellow = np.zeros(N)
        light_obj_visibility_orange = np.zeros(N)
        light_obj_visibility_red = np.zeros(N)

        cnt = 0
        for i in light_indexes:
            ii = i
            if consider_light_travel:
                ii = light_indexes_emitted[cnt]
                cnt += 1
            #print('indexes:',ii,sat_pos_1D[ii])
            lambda_obs = lambda0*energy_per_mass/(1.-2.*M/sat_pos_1D[ii])/transform_faraway_to_shell
            lambda_m=np.copy(lambda_obs)/1e-9
            #print('lambda:',lambda_m)
            if lambda_m <= 450:
                light_obj_visibility_violet[i:i+N//128] += 1
            if 450 < lambda_m <= 495:
                light_obj_visibility_blue[i:i+N//128] += 1
            if 495 < lambda_m <= 570:
                light_obj_visibility_green[i:i+N//128] += 1
            if 570 < lambda_m <= 590:
                light_obj_visibility_yellow[i:i+N//128] += 1
            if 590 < lambda_m <= 620:
                light_obj_visibility_orange[i:i+N//128] += 1
            if lambda_m > 620:
                light_obj_visibility_red[i:i+N//128] += 1


        #ii=np.argmin(np.abs(time_array_obs/const.c-174.766)) ##make the spaceship cover the red ball

        sat_radius_fake = r_m
        sat_visibility = np.zeros(N)
        sat_visibility[:] = 1
        sat_pos_fake = np.zeros( shape=(N,3) )
        sat_pos_fake[:,0] = np.logspace( np.log(utils.m_to_AU(sat_radius_fake)), np.log(utils.m_to_AU(sat_radius_fake) - 0.0001), N)
        #for i in range(ii,N):
        #    sat_pos_fake[i,0] = sat_pos_fake[ii,0]
        sat_pos_fake[:,2] -= 3e-8
        light_obj_pos2 = np.zeros( shape = (N,3)) + np.array([r_AU-0.000001, 0, 0])
        rgb=np.zeros((N,3))
        other_objects = [['rocket1', 'Satellite', sat_pos_fake, 0.2, [1,1,1], None, None, sat_visibility, None],
                         ['light', 'Sphere01', light_obj_pos_violet, 5, [255,1,255], None, None, light_obj_visibility_violet, None],
                         ['light', 'Sphere01', light_obj_pos_blue, 5, [0,1,255], None, None, light_obj_visibility_blue, None],
                         ['light', 'Sphere01', light_obj_pos_green, 5, [1,255,1], None, None, light_obj_visibility_green, None],
                         ['light', 'Sphere01', light_obj_pos_yellow, 5, [255,255,1], None, None, light_obj_visibility_yellow, None],
                         ['light', 'Sphere01', light_obj_pos_orange, 5, [255,50,1], None, None, light_obj_visibility_orange, None],
                         ['light', 'Sphere01', light_obj_pos_red, 5, [255,5,5], None, None, light_obj_visibility_red, None]]

        cam_dir_s1 = [-1,0,0]
        global_messages = ['Black hole mass = %g Solar Masses\nSpacecraft initial shell velocity at 1AU = %g c\nFalling space ship sending light signal every %g seconds measured in falling frame\n' % (M_SM/const.m_sun, sat_start_shell_speed, light_interval/const.c)]*N
        #print(np.shape(global_messages))
        print('The spacecraft will send a light signal every %g seconds to the planet observer, for a total of %d signals.' % (light_interval/const.c, nr_of_light_messages))

        # Writing the txt document and the time messages
        new_line = [12,24,36]
        a = 'Times of the light signals:\n'
        light_number = 0
        light_number_array = []
        time_diffrences_light = []
        b = 0
        for i in range(N):
            if i in np.array(light_indexes):
                light_number += 1 #Finding the light number
                if light_number in new_line:
                    a += '%i. %g  |\n' %(light_number, time_array_obs[i]/const.c)
                else:
                    a += '%i. %g  |' %(light_number, time_array_obs[i]/const.c)

                light_number_array += [light_number]
                time_diffrences_light += [time_array_obs[i]/const.c]#[time_array_obs[i]/const.c - b]
                b = time_array_obs[i]/const.c

            global_messages[i] += a

        if write_text == True:
            np.savetxt(text_file_path_1, np.array([light_number_array[1:len(recv)], time_diffrences_light[1:len(recv)]]))
            print('Text file written to %s.' % os.path.relpath(text_file_path_1))
        else:
            pass

        self._write_to_xml(time_array_obs/const.c, utils.m_to_AU(obs_pos), cam_dir_s1, planet_pos=planet_pos, other_objects=other_objects, camera_messages=global_messages, planet_idx=planet_idx, filename=filename_1, origo_location=np.array([0,0,0]), black_hole=True, play_speed = 0.51)



        ### SCENE 2 ###
        dtau_2 = 1e8  # m
        time_array_sat_2 = [0]
        time_array_obs_2 = [0]
        sat_pos_1D_2 = [r_m]
        while sat_pos_1D_2[-1] > (2*M * 1.001):   # Outside schwarzschild radius ( with a tolerance )
            time_array_sat_2.append( time_array_sat_2[-1] + dtau_2 )
            dt_2 = energy_per_mass/(1-(2*M)/sat_pos_1D_2[-1])*dtau_2/transform_faraway_to_shell
            time_array_obs_2.append( time_array_obs_2[-1] + dt_2 )
            sat_pos_1D_2.append( sat_pos_1D_2[-1] - np.sqrt( energy_per_mass**2 - (1-2*M/sat_pos_1D_2[-1]) )*dtau_2)
        sat_pos_1D_2 = np.array(sat_pos_1D_2[:-1])  # Cutting off last frame.
        time_array_sat_2 = np.array(time_array_sat_2[:-1])
        time_array_obs_2 = np.array(time_array_obs_2[:-1])

        N2 = len(sat_pos_1D_2)  # Number of frames for last third of video.
        if self._debug: print('In C2_2 with Frames = %d' % N2)

        light_interval_2 = (time_array_obs_2[-1] - time_array_obs_2[0])/(nr_of_light_messages+0.1)
        send_light_times_obs = np.array([ i*light_interval_2 for i in range(1, int(nr_of_light_messages)+1) ])
        light_indexes_2 = []   # Since there's no SR, everybody agrees on when light was sent out (Their local time will vary, but they will agree on what time index, because they correspond.)
        for i in range(len(send_light_times_obs)):
            light_indexes_2.append( (np.abs(send_light_times_obs[i] - time_array_obs_2)).argmin() )

        if consider_light_travel:
            recv = []
            #print('consider1:',light_indexes_2,N2)
            for i in (light_indexes_2):
                lightpos = np.zeros(N2)
                lightpos [0:i] = 1e6*r_m
                lightpos[i] = r_m
                for j in range(i+1,N2):
                    lightpos[j] = lightpos[j-1] - (1 - 2*M/lightpos[j-1])/(1 - 2*M/sat_pos_1D_2[j-1])*energy_per_mass*dtau_2
                ii = np.argmin(np.abs(lightpos - sat_pos_1D_2))
                if ii < N2-1:
                    #print(ii,lightpos[ii] - sat_pos_1D_2[ii],lightpos[ii+1] - sat_pos_1D_2[ii+1],lightpos[ii-4:ii+4],sat_pos_1D_2[ii-4:ii+4]),
                    if np.sign(lightpos[ii] - sat_pos_1D_2[ii]) != np.sign(lightpos[ii+1] - sat_pos_1D_2[ii+1]) or np.sign(lightpos[ii] - sat_pos_1D_2[ii]) != np.sign(lightpos[ii-1] - sat_pos_1D_2[ii-1]):
                        recv.append(ii)
            light_indexes_2 = recv

        else:
            recv = []
            #print('consider1:',light_indexes_2,N2)
            for i in (light_indexes_2):
                lightpos = np.zeros(N2)
                lightpos [0:i] = 1e6*r_m
                lightpos[i] = r_m
                for j in range(i+1,N2):
                    lightpos[j] = lightpos[j-1] - (1 - 2*M/lightpos[j-1])/(1 - 2*M/sat_pos_1D_2[j-1])*energy_per_mass*dtau_2
                iunn = np.argmin(np.abs(lightpos - sat_pos_1D_2))
                if iunn < N2-1:
                    #print(iunn,lightpos[iunn] - sat_pos_1D_2[iunn],lightpos[iunn+1] - sat_pos_1D_2[iunn+1],lightpos[iunn-4:iunn+4],sat_pos_1D_2[iunn-4:iunn+4]),
                    if np.sign(lightpos[iunn] - sat_pos_1D_2[iunn]) != np.sign(lightpos[iunn+1] - sat_pos_1D_2[iunn+1]) or np.sign(lightpos[iunn] - sat_pos_1D_2[iunn]) != np.sign(lightpos[iunn-1] - sat_pos_1D_2[iunn-1]):
                        recv.append(iunn)

        light_obj2_visibility_violet = np.zeros(N2)
        light_obj2_visibility_blue = np.zeros(N2)
        light_obj2_visibility_green = np.zeros(N2)
        light_obj2_visibility_yellow = np.zeros(N2)
        light_obj2_visibility_orange = np.zeros(N2)
        light_obj2_visibility_red = np.zeros(N2)

        for i in (light_indexes_2):
            lambda_obs = lambda0_fromshell/(energy_per_mass/(1.-2.*M/sat_pos_1D_2[i])/transform_faraway_to_shell)
            lambda_m=np.copy(lambda_obs)/1e-9
            #print('lambda:',lambda_m)
            if lambda_m <= 450:
                light_obj2_visibility_violet[i:i+N//128] += 1
            if 450 < lambda_m <= 495:
                light_obj2_visibility_blue[i:i+N//128] += 1
            if 495 < lambda_m <= 570:
                light_obj2_visibility_green[i:i+N//128] += 1
            if 570 < lambda_m <= 590:
                light_obj2_visibility_yellow[i:i+N//128] += 1
            if 590 < lambda_m <= 620:
                light_obj2_visibility_orange[i:i+N//128] += 1
            if lambda_m > 620:
                light_obj2_visibility_red[i:i+N//128] += 1


        if self._debug: print ('light indexes ', np.array(light_indexes_2))
        if self._debug: print ('light intervals ', np.array(light_indexes_2[1:]) - np.array(light_indexes_2[:-1]))

        sat_pos_fake_2 = np.zeros( shape=(N2,3) )
        sat_pos_fake_2[:,0] = np.logspace( np.log(utils.m_to_AU(sat_radius_fake)), np.log(utils.m_to_AU(sat_radius_fake) - 0.01), N2)

        light_obj2_pos_violet = np.array([0.000001, 0, 0]) + sat_pos_fake_2   # Simply putting it 0.1 AU from observer.
        light_obj2_pos_blue = np.array([0.000001, 0, 0]) + sat_pos_fake_2   # Simply putting it 0.1 AU from observer.
        light_obj2_pos_green = np.array([0.000001, 0, 0]) + sat_pos_fake_2   # Simply putting it 0.1 AU from observer.
        light_obj2_pos_yellow = np.array([0.000001, 0, 0]) + sat_pos_fake_2   # Simply putting it 0.1 AU from observer.
        light_obj2_pos_orange = np.array([0.000001, 0, 0]) + sat_pos_fake_2   # Simply putting it 0.1 AU from observer.
        light_obj2_pos_red = np.array([0.000001, 0, 0]) + sat_pos_fake_2   # Simply putting it 0.1 AU from observer.

        other_objects_2 = [['light', 'Sphere01', light_obj2_pos_violet, 2, [255,0,255], None, None, light_obj2_visibility_violet, None],
                           ['light', 'Sphere01', light_obj2_pos_blue, 2, [0,0,255], None, None, light_obj2_visibility_blue, None],
                           ['light', 'Sphere01', light_obj2_pos_green, 2, [0,255,0], None, None, light_obj2_visibility_green, None],
                           ['light', 'Sphere01', light_obj2_pos_yellow, 2, [255,255,0], None, None, light_obj2_visibility_yellow, None],
                           ['light', 'Sphere01', light_obj2_pos_orange, 2, [255,50,0], None, None, light_obj2_visibility_orange, None],
                           ['light', 'Sphere01', light_obj2_pos_red, 2, [255,0,0], None, None, light_obj2_visibility_red, None]]

        cam_dir_s2 = [1,0,0]

        global_messages_2 = ['Black hole mass = %g Solar Masses\nSpacecraft initial shell velocity at 1AU = %g c\nPlanet observer sending light every %g seconds measured in planet frame' % (M_SM/const.m_sun, sat_start_shell_speed, light_interval_2/const.c)]*N2

        print('The far-away observer will send a light signal every %g seconds to the spacecraft, for a total of %d signals.' % (light_interval_2/const.c, nr_of_light_messages))

        a = 'Times of the light signals:\n'
        light_number = 0
        time_diffrences_light = []
        b = 0
        light_number_array = []
        for i in range(N2):
            if i in np.array(light_indexes_2):
                light_number += 1 #Finding the light number
                if light_number in new_line:
                    a += '%i. %g  |\n' %(light_number, time_array_sat_2[i]/const.c)
                else:
                    a += '%i. %g  |' %(light_number, time_array_sat_2[i]/const.c)

                time_diffrences_light += [time_array_sat_2[i]/const.c]#[time_array_sat_2[i]/const.c - b]
                b = time_array_sat_2[i]/const.c
                light_number_array += [light_number]

            global_messages_2[i] += a

        if write_text == True:
            np.savetxt(text_file_path_2, np.array([light_number_array[:len(recv)], time_diffrences_light[:len(recv)]]))
            print('Text file written to %s.' % os.path.relpath(text_file_path_2))
        else:
            pass

        self._write_to_xml(time_array_sat_2/const.c, sat_pos_fake_2, cam_dir_s2, camera_messages=global_messages_2, planet_pos=planet_pos, other_objects=other_objects_2, planet_idx=planet_idx, filename=filename_2, origo_location=np.array([0,0,0]), black_hole=True, play_speed = 0.51)

        if write_solutions:

            #Solution writing
            if consider_light_travel:
                pass
            else:
                solution_name='Solutions_black_hole_descent.txt'
                solution_2C=self._get_new_solution_file_handle(solution_name)
                solution_2C.write('Solutons to 2C.5\n')
                #solution_2C.write('1. No numerical solution\n')
                #solution_2C.write('2. No numerical solution\n')
                #solution_2C.write('3. No numerical solution\n')
                solution_2C.write('4. The energy per mass of the spaceship is %f.\n' %energy_per_mass)
                solution_2C.write('7. Distance from black hole (seen from the spacecraft), between two first signals received:')
                r_seen_from_sat=2/(1-(((time_array_sat_2[light_indexes_2[1]]-time_array_sat_2[light_indexes_2[0]])/light_interval_2)*energy_per_mass*np.sqrt(1.-2.*M/r_m)))
                solution_2C.write('AU: %g, SR: %g|\n' %(utils.m_to_AU(r_seen_from_sat*M),r_seen_from_sat))
                solution_2C.write('7. Distance from black hole (seen from the spacecraft), between two last signals received:')
                r_seen_from_sat=2/(1-(((time_array_sat_2[light_indexes_2[-2]]-time_array_sat_2[light_indexes_2[-3]])/light_interval_2)*energy_per_mass*np.sqrt(1.-2.*M/r_m)))
                solution_2C.write('AU: %g, SR: %g|\n' %(utils.m_to_AU(r_seen_from_sat*M),r_seen_from_sat))
                solution_2C.write('7. Distance from black hole (seen from the planet), between two first signals received:')
                r_seen_from_planet=2/(1-((light_interval/(time_array_obs[light_indexes[1]]-time_array_obs[light_indexes[0]]))*energy_per_mass*np.sqrt(1.-2.*M/r_m)))
                solution_2C.write('AU: %g, SR: %g|\n' %(utils.m_to_AU(r_seen_from_planet*M),r_seen_from_planet))
                solution_2C.write('7. Distance from black hole (seen from the planet), between two last signals received:')
                r_seen_from_planet=2/(1-((light_interval/(time_array_obs[light_indexes[-1]]-time_array_obs[light_indexes[-2]]))*energy_per_mass*np.sqrt(1.-2.*M/r_m)))
                solution_2C.write('AU: %g, SR: %g|\n' %(utils.m_to_AU(r_seen_from_planet*M),r_seen_from_planet))
                solution_2C.close()

    def gps(self, planet_idx, angular_position=None, increase_height=False, filename='gps.xml', number_of_video_frames=1000, write_solutions=False):
        """Two GPS satellites are passing above an observer on the equator.

        Generates the XML file used in Exercise 8 in Part 2C of the lecture notes and Exercise 5 in Part 9 of the project.

        Parameters
        ----------
        planet_idx : int
            Index of the planet above which the experiment takes place.
        angular_position : float, optional
            The angular position of the observer on the planet equator, measured in radians from the x-axis.
            By default, the observer is situated at a random angle in the range [pi/2, 3*pi/2].
        increase_height : bool or float, optional
            Determines the height above the planet center where the experiment takes place.
            The default value (False) causes a predetermined height of 1.01 planet radii to be used. Using True increases this to 1.1.
            Optionally, a custom adjustment parameter between 0.5 and 5 can be provided.
            Try modifying this argument if the spaceships interfere with the surface of the planet.
        filename : str, optional
            The filename to use for the XML file.
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1000, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        planet_idx = int(planet_idx)
        if planet_idx < 0 or planet_idx >= self.system.number_of_planets:
            raise ValueError('Argument "planet_idx" is %d but must be in the range [0, %d].' % (planet_idx, self.system.number_of_planets - 1))

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        random_state = np.random.RandomState(self.seed + utils.get_seed('gps'))

        filename = str(filename)

        standard_height_factor = 1.01
        increase_height_factor     = 1.10

        if increase_height is False:
            height_factor = standard_height_factor
        elif increase_height is True:
            height_factor =  increase_height_factor
        else:
            if increase_height < 0.5 or increase_height > 5.:
                print('Increase height needs to be True, False or between 0.5 and 5')
                raise ValueError('Increase_height invalid')
            if increase_height >= 1:
                height_factor = standard_height_factor + 0.01 * increase_height
            else:
                height_factor = standard_height_factor - 0.01 + 0.01 * increase_height

        print_solution = True

        sat_sys_angular_dist = 5*const.pi/4           # Total angular distance for satelltes to move
        ang_dist_between_sats = const.pi/6        # Angular distance between satellites
        # Increase the radius if the GR effect isnt noticable maybe?
        upper_lim_radius      = 3           # Upper limit for satellite orbit radius [planet radiuses]
        lower_lim_radius      = 2.5         # Lower limit for sat orbit radius [planet radiuses]
        # Set this in the range [pi/2 to 3pi/2] if you want only to be on the sunny side of the planet
        if angular_position is None:
            angular_position = random_state.uniform(const.pi/2, 3/2*const.pi)                        # Random place on the planet in the xy-plane, in the sunny side
        if angular_position < 0 or angular_position > 2*const.pi:
             raise ValueError('angular_position is in radians and must be between 0 and 2*pi')
        if angular_position <= const.pi/2 or angular_position >= 3/2*const.pi:
            print('To stay on the sunny side of the planet, angular_position is recommended to be within [pi/2, 3/2*pi]')
        #print('angular_position:',angular_position)
        # Increase the following two variables if GR effects arent noticable
        n_dec_pos         = 3                   # Number of decimals shown for positions
        n_dec_t           = 7                   # Number of decimals shown for time values
        print_solution  = False # Solution printout toggle
        GR              = True  # Bool for whether to include general relativity or not, mostly used for debugging

        def time_diff_shells(M, r1, r2, v2):
            """ Returns t1/t2, the factor at which time runs differently, at the
            shell a distance r1, relative
            to somebody on the shell at a distance r2 moving with tangential velocity v2.
            M = Planet mass in kg
            r1 = Planet radius in meters
            r2 = Orbit distance in meters
            v2 = Object orbit speed in m/s"""
            M_m = utils.kg_to_m(M)
            teller = 1 - 2*M_m/r1                           # Standing still (person)
            nevner = 1 - 2*M_m/r2 - v2**2/const.c**2                   # Moving in orbit at r2 (spaceship)
            return np.sqrt(teller/nevner)

        def sat_speed(M, r):
            """ Speed of orbiting satellite at a radius r in meters, orbiting a planet
            with mass M in kilograms. Returns speed in m/s"""
            return np.sqrt(const.G*M/r)

        M = self.system.masses[planet_idx]*const.m_sun        # Mass of planet [kg]
        R = self.system.radii[planet_idx]                     # Radius of planet [km]
        orbit_radius_factor = random_state.uniform(lower_lim_radius, upper_lim_radius)
        sat_orbit_radius = orbit_radius_factor*R           # Satellite orbit radius from planet center [km]
        # if self._debug: print('Sats are in circular orbits with radius: %g planet radiuses'%orbit_radius_factor)
        v_sat = sat_speed(M, sat_orbit_radius*1e3)/1e3       # km/s -  First converted to m/s, returned as m/s and converted back
        omega_sat = v_sat/sat_orbit_radius               # Satellite angular velocity

        #print('sat.rad:',sat_orbit_radius,v_sat,M,R)

        T_sat = 2*const.pi/omega_sat
        T_sat_hr = T_sat/(60**2)              # Orbital period in hours
        # if self._debug: print('Theta for person position: ', angular_position)
        person_pos0 = R*np.array([np.cos(angular_position), np.sin(angular_position), 0])
        #print('SOlution:',person_pos0)

        # Make 3D position arrays (All in AU)
        person_pos = np.zeros(shape = (N,3))
        person_pos[:] = utils.km_to_AU(person_pos0)
        sat1_pos   = np.zeros(shape = (N,3))
        sat2_pos   = np.zeros(shape = (N,3))
        cam_pos    = np.zeros(shape = (N,3))
        # Fix cam pos if safe height is enabled
        cam_pos[:] = person_pos[:]*height_factor

        # Calculate satellite positions
        tot_time = sat_sys_angular_dist/omega_sat
        times_earth = np.linspace(0, tot_time, N) # Time steps at earth
        times_earth_copy = np.copy(times_earth)
        times_sat = np.copy(times_earth)
        if GR: times_sat/=time_diff_shells(M, R*1e3, sat_orbit_radius*1e3, v_sat*1e3) # Times for sats
        sat1_pos[:,0] = utils.km_to_AU(sat_orbit_radius)*np.cos(angular_position + sat_sys_angular_dist/2 + ang_dist_between_sats/2 - omega_sat*times_earth)
        sat1_pos[:,1] = utils.km_to_AU(sat_orbit_radius)*np.sin(angular_position + sat_sys_angular_dist/2 + ang_dist_between_sats/2 - omega_sat*times_earth)

        sat2_pos[:,0] = utils.km_to_AU(sat_orbit_radius)*np.cos(angular_position + sat_sys_angular_dist/2 - ang_dist_between_sats/2 - omega_sat*times_earth)
        sat2_pos[:,1] = utils.km_to_AU(sat_orbit_radius)*np.sin(angular_position + sat_sys_angular_dist/2 - ang_dist_between_sats/2 - omega_sat*times_earth)

        middle = 0.55*np.copy(sat1_pos) + 0.45*sat2_pos[:]
        cam_dir = middle - np.copy(cam_pos[:])
        cam_up = np.zeros(shape = (N,3))
        sat_normalized = middle/np.linalg.norm(middle, axis = 1)[:,None]
        cam_up[:int(N/2),0] = np.linspace(sat_normalized[0,1], 0, int(N/2))
        cam_up[int(N/2):, 0] = np.linspace(0, sat_normalized[0,1], int(N/2))
        cam_up[:int(N/2),1] = np.linspace(-sat_normalized[0,0], 0, int(N/2))
        cam_up[int(N/2):,1] = np.linspace(0, -sat_normalized[0,0], int(N/2))

        z_upvec = np.zeros(N)
        z_upvec[:int(N/2)] = self._focus_tanhyper(int(N/2))
        z_upvec[int(N/2):] = np.flipud(z_upvec[:int(N/2)])
        cam_up[:, 2] = z_upvec[:]

        # NOW FOR THE NUMBERS
        t_received1 = np.zeros(N)       # Time points in earth time when signals are received, sat 1
        t_received2 = np.zeros(N)       # Time points in earth time when signals are received, sat 2
        for i in range(N):
            dt1 = np.linalg.norm(sat1_pos[i] - person_pos[i])/const.c_AU_pr_s
            dt2 = np.linalg.norm(sat2_pos[i] - person_pos[i])/const.c_AU_pr_s
            t_received1[i] = times_earth[i] - dt1
            t_received2[i] = times_earth[i] - dt2

        # plt.plot(t_received1 - times_sat)
        #timesig1_func = interpolate.interp1d(t_received1, times_sat,
        #                                     fill_value = 'extrapolate')
        #timesig2_func = interpolate.interp1d(t_received2, times_sat,
        #                                     fill_value = 'extrapolate')

        #possig1_func = interpolate.interp1d(t_received1, sat1_pos, axis = 0,
        #                                    fill_value = 'extrapolate')
        #possig2_func = interpolate.interp1d(t_received2, sat2_pos, axis = 0,
        #                                    fill_value = 'extrapolate')

        #pos_sat1_seen_from_plan = possig1_func(times_earth)
        #pos_sat2_seen_from_plan = possig2_func(times_earth)

        #t_sat1_vid = timesig1_func(times_earth)
        #t_sat2_vid = timesig2_func(times_earth)

        #pos_sat1_seen_from_plan = np.zeros(shape = (N,2))
        #pos_sat2_seen_from_plan = np.zeros(shape = (N,2))

        #pos_sat1_seen_from_plan[:,0] = sat_orbit_radius*km_to_AU*np.cos(angular_position + sat_sys_angular_dist/2 + ang_dist_between_sats/2 - omega_sat*t_received1)
        #pos_sat1_seen_from_plan[:,1] = sat_orbit_radius*km_to_AU*np.sin(angular_position + sat_sys_angular_dist/2 + ang_dist_between_sats/2 - omega_sat*t_received1)
        #pos_sat2_seen_from_plan[:,0] = sat_orbit_radius*km_to_AU*np.cos(angular_position + sat_sys_angular_dist/2 - ang_dist_between_sats/2 - omega_sat*t_received2)
        #pos_sat2_seen_from_plan[:,1] = sat_orbit_radius*km_to_AU*np.sin(angular_position + sat_sys_angular_dist/2 - ang_dist_between_sats/2 - omega_sat*t_received2)

        pos_sat1_seen_from_plan = sat1_pos
        pos_sat2_seen_from_plan = sat2_pos

        t_sat1_vid = np.copy(t_received1)
        t_sat2_vid = np.copy(t_received2)


        if GR:
            t_sat1_vid /= time_diff_shells(M, R*1e3, sat_orbit_radius*1e3, v_sat*1e3)
            t_sat2_vid /= time_diff_shells(M, R*1e3, sat_orbit_radius*1e3, v_sat*1e3)


        sat1_messages = []
        sat2_messages = []
        for i in range(N):
            if t_sat1_vid[i] > 0:
                sat1_messages.append('[%.*f, %.*f] , t = %.*f'%(n_dec_pos, utils.AU_to_km(pos_sat1_seen_from_plan[i,0]),n_dec_pos, utils.AU_to_km(pos_sat1_seen_from_plan[i,1]),n_dec_t, t_sat1_vid[i]))
            else:
                sat1_messages.append('')
            if t_sat2_vid[i] > 0:
                sat2_messages.append('[%.*f, %.*f] , t = %.*f'%(n_dec_pos, utils.AU_to_km(pos_sat2_seen_from_plan[i,0]),n_dec_pos, utils.AU_to_km(pos_sat2_seen_from_plan[i,1]),n_dec_t, t_sat2_vid[i]))
            else:
                sat2_messages.append('')


        other_objects = [self._object_list('sat1', 'Satellite', sat1_pos, 1.3, [1,1,1], msg_list = sat1_messages),
                         self._object_list('sat2', 'Satellite', sat2_pos, 1.3, [1,1,1], msg_list = sat2_messages)]

        if print_solution:
            camera_messages = ['Solution position: [%.*f km, %.*f km] \nPlanet radius: %.*f km \nt = %.*f s (Earth clock)'%(n_dec_pos,person_pos0[0], n_dec_pos,person_pos0[1], n_dec_pos,self.system.radii[planet_idx],n_dec_t, times_earth[i]) for i in range(N)]
        else:
            camera_messages = ['t = %.*f s (Earth clock)\nPlanet mass = %.12E kg, Planet radius = %.*f km'%(n_dec_t,times_earth[i],M,7,R) for i in range(N)]

        self._write_to_xml(times_earth_copy, cam_pos, cam_dir, [0,0,0], other_objects, up_vec = cam_up, planet_idx = planet_idx, filename=filename, camera_messages = camera_messages, show_clock = 0, toggle_clock = False)

        if write_solutions:

            #Solution writing

            solution_name='Solutions_gps.txt'
            solution_2C=self._get_new_solution_file_handle(solution_name)
            solution_2C.write('Solutons to 2C.8\n')
            solution_2C.write('1. Hight of the satellites: r=%f km\n' %sat_orbit_radius)
            solution_2C.write('2. Velocity of the satellites: v=%f km/s\n' %(v_sat))
            #solution_2C.write('3. No numerical solution\n')
            #solution_2C.write('4. No numerical solution\n')
            solution_2C.write('5. Your actual position in km: r=[%f,%f]\n' %(person_pos0[0],person_pos0[1]))
            #solution_2C.write('6. No numerical solution\n')
            #solution_2C.write('7. No numerical solution\n')
            solution_2C.close()

    def black_hole_schedules(self, distance, filename='black_hole_schedules.xml', number_of_video_frames=1000, write_solutions=False):
        """Two astronauts living in spaceships orbiting respectively close to and far from a black hole are sending each other messages about their schedule.

        Generates the XML files used in Exercise 2 in Part 2C of the lecture notes.

        Note
        ----
            For each scheduled activity you will be asked to input an associated time and message.

        Parameters
        ----------
        distance : {'close', 'far'}
            Whether the observer should be the one close to or far from the black hole.
        filename : str, optional
            The base filename to use for the XML file.
            Note that an extra label will be added to the inputted file name to indicate whether the observer is close or far.
            Default is "black_hole_schedules.xml".
        number_of_video_frames : int, optional
            The number of video frames to use in the XML files.
            Can be reduced to reduce file size, but be aware that this might lead to errors.
            Default is 1000, but must be at least 100.
        write_solutions : bool, optional
            Whether to write a text file containing the solutions associated with this experiment.
            Default is False.
        """
        distance = str(distance).lower()
        if not distance in ('close', 'far'):
            raise ValueError('Argument "distance" is %s but must be either "close" or "far".' % distance)

        filename = str(filename)
        filename_base = '.'.join(filename.split('.')[:-1]) if '.' in filename else filename
        filename = '%s_%s.xml' % (filename_base, distance)

        N = int(number_of_video_frames)
        if N < 100:
            raise ValueError('Argument "number_of_video_frames" is %d but must be at least 100.' % N)

        nevents = 6
        events_messages_far = ['Finally a new fantastic day!!!',
                               'Egg and bacon directly from the planet, wonderful breakfast!!',
                               'Excellent lunch today, soooo good.',
                               'Had a really nice dinner, yummi!',
                               'Brushing, brushing!',
                               'So sad, the day is already over, good night everbody!']

        events_messages_close = ['Oooh, nooo, another day, do I really need to wake up?',
                                 'Not hungry, no breakfast for me please.',
                                 'I just hate these space lunches, why can\'t somebody invent better space food.',
                                 'Space food again, all dinners are equal here :(',
                                 'Hate the tooth brushing, the space tooth paste tastes almost as bad as the dinner.',
                                 'Finally the boring day out here in space is over, good night!']

        events_messages_sat = ['Wake up!', 'Breakfast', 'Lunch', 'Dinner', 'Brush teeth', 'Good night']

        if self._debug: print('Transforming from ', distance,' observer')

        def transform(dt,black_hole_mass,radius,to_long_dist=False):
            m = black_hole_mass
            r = radius
            if to_long_dist:
                dt_long_dist = dt/(np.sqrt(1-(2*m/r)))
                if self._debug: print('Transform from shell obs to long dist')
                return dt_long_dist
            else:
                dt_shell = dt*(np.sqrt(1-(2*m/r)))
                if self._debug: print('Transform from long dist to shell obs')
                return dt_shell

        def hours_to_sec(time_str):
            dt_array = np.zeros((len(time_str),2))
            seconds = np.zeros(len(time_str))
            for i in range(len(time_str)):
                dt_array[i,:] = time_str[i].split(':')
                seconds[i] = dt_array[i,0]*60*60 + dt_array[i,1]*60
            return seconds

        def sec_to_clockhours(time):
            ttime = np.copy(time)
            days = np.floor(ttime/(60*60*24.))
            ttime -= days*60.*60.*24.
            hours = np.floor(ttime/(60*60))
            sec_left = ttime-hours*60*60
            minutes = str(int(np.floor(sec_left/60)))
            hours = str(int(hours))
            if len(hours) == 1:
                hours = '0'+hours
            if len(minutes) == 1:
                minutes = '0'+minutes
            return 'Day: '+str(int(days))+' Time: '+hours+':'+minutes

        random_state = np.random.RandomState(self.seed + utils.get_seed('black_hole_schedules'))

        upper_mass = 50
        black_hole_mass = random_state.uniform(30,upper_mass)     #Black hole mass in solar masses
        black_hole_mass_kg = black_hole_mass*const.m_sun        # Black hole mass in kg
        black_hole_mass_m = utils.kg_to_m(black_hole_mass_kg)            #Black hole mass in m
        schw_radius = 2*utils.kg_to_m(black_hole_mass_kg)           #Schwarzhild radius
        other_obs_r = schw_radius*random_state.uniform(8,12)
        obs_r = schw_radius*random_state.uniform(1.05,1.1)
        if distance.lower() == 'close':
            close = True
        else:
            obs_r, other_obs_r = other_obs_r, obs_r
            close = False

        mass_scl = 30.
        obs_real = np.copy(obs_r) * mass_scl
        other_obs_real = np.copy(other_obs_r) * mass_scl
        schw_radius_real = np.copy(schw_radius) * mass_scl
        black_hole_mass_m *= mass_scl
        black_hole_mass *= mass_scl
        black_hole_mass_kg *= mass_scl

        other_dt_list = ['09:00','10:00','13:30','19:00','22:30','23:00']
        dt_list = ['06:00','07:00','12:00','18:00','23:15','23:30']
        if self._debug: print('Using set test times:',dt_list)
        if not self._run_in_test_mode:
            dt_listin = []
            ev_messages = []
            print('Good evening captain!')
            print('Let\'s make a schedule for tomorrow...')
            print('Please answer using 24 hours clock format split by ":" as xx:xx.')
            terminal_messesages = ['Wake up at --> ','Breakfast at --> ','Lunch at --> ','Dinner at --> ','Brush your teeth at --> ','Go to bed at --> ']
            for text in terminal_messesages:
                try:
                    t = raw_input(text).strip()
                except:
                    t = input(text).strip()
                if len(t) != 5:
                    raise IndexError ('Format for times must be xx:xx, e.g. 03:10')
                dt_listin.append(t)
            terminal_messesages = ['Write a message you want to send to your colleague when you wake up:  ','Write a message you want to send to your colleague when you have breakfast: ','Write a message you want to send to your colleague when you have lunch:  ','Write a message you want to send to your colleague when you have dinner:  ','Write a message you want to send to your colleague when you brush your teeth:  ','Write a message you want to send to your colleague when you go to bed:  ']
            for text in terminal_messesages:
                try:
                    t = raw_input(text).strip()
                except:
                    t = input(text).strip()
                ev_messages.append(t)
                if close:
                    events_messages_close = ev_messages
                    dt_list = dt_listin
                else:
                    events_messages_far = ev_messages
                    dt_list = dt_listin
        else:
            if close:
                dt_list, other_dt_list = other_dt_list, dt_list


        dt_list.append('24:00')
        print('Given times:',dt_list)#,other_obs_real,obs_real)
        # Time array
        upper_mass_m = upper_mass*utils.kg_to_m(const.m_sun)
        lower_schw_radius = 1.05*2*upper_mass_m


        dt_clock = dt_list
        dt_list = hours_to_sec(dt_list)
        dt_array = np.asarray(dt_list)

        other_dt_list_text = np.copy(other_dt_list)
        other_dt_list = hours_to_sec(other_dt_list)


        dt_long = transform(dt_array,black_hole_mass_m,other_obs_real,to_long_dist=True)
        dt_other_obs = transform(dt_long,black_hole_mass_m,obs_real,to_long_dist=False)

        if close:
            time = np.linspace(0,60*60*24,N)
        else:
            time = np.linspace(0,dt_other_obs[-1]+60*60*3,N)



        length_of_other_day = dt_other_obs[-1]
        indlist = []
        ndays = int(np.ceil(time[-1]/length_of_other_day))
        for d in range(ndays):
            for t in dt_other_obs[0:-1]:
                tt = t + d*length_of_other_day
                if (tt < time[-1]):
                    indlist.append(np.argmin(np.abs(time-tt)))
        indlist = np.array(indlist)

        length_of_day = 60*60*24
        locindlist = []
        ndays = int(np.ceil(time[-1]/length_of_day))
        for d in range(ndays):
            for t in other_dt_list:
                tt = t + d*length_of_day
                if (tt < time[-1]):
                    locindlist.append(np.argmin(np.abs(time-tt)))
        locindlist = np.array(locindlist)

        #print('testtime:',indlist,time[63],time[73],time[126],dt_list,dt_array,dt_long,dt_other_obs)


        cam_message = []
        for i in range(N):
            cam_message.append(sec_to_clockhours( time[i]) + '\nBlack hole of %g solar masses \nYour position r = %f km \nThe other observer in position r= %f km' %(black_hole_mass,obs_real/1e3,other_obs_real/1e3))



        #index_expl = []
        #for times in dt_other_obs:
        #    index_expl.append((np.abs(time-times)).argmin())

        dscl = 5e4

        # Objects
        planet_radius = utils.km_to_AU(self.system.radii[0])
        # Closest observer on a spacecraft, furthest on a spacecraft in orbit around planet
        if close:
            sc_pos = np.array([utils.m_to_AU(obs_r),0,0])
            planet_pos = np.array([utils.m_to_AU(obs_r) + 10*planet_radius,0,0])     #np.array([other_obs_r*m_to_AU,0,0])
        else:
            #sc_pos = np.array([10.,0,0])
            #planet_pos = np.array([9.5,0,0])       #np.array([obs_r*m_to_AU,0,0])
            sc_pos = np.array([utils.m_to_AU(other_obs_r),0,0])*dscl
            planet_pos = np.array([utils.m_to_AU(other_obs_r) + 10*planet_radius,0,0])*dscl    #np.array([obs_r*m_to_AU,0,0])


        sc_plt_pos = planet_pos + np.array([0.1,0,0])*dscl

        # cam pos is at other oberver, dir at observer
        if close:
            cam_pos = sc_plt_pos + np.array([utils.km_to_AU(2000),0,utils.km_to_AU(1000)])
            cam_dir = (sc_pos-sc_plt_pos)/(np.linalg.norm(sc_pos-sc_plt_pos))
        else:
            #cam_pos = sc_pos #+ np.array([-2000*km_to_AU,0,1000*km_to_AU])
            #cam_dir = np.array([-1,0,0])#(sc_plt_pos-sc_pos)/np.linalg.norm(sc_plt_pos-sc_pos)
            cam_pos = sc_pos + np.array([utils.km_to_AU(-2000),0,utils.km_to_AU(1000)])*dscl
            cam_dir = (sc_plt_pos-sc_pos)/np.linalg.norm(sc_plt_pos-sc_pos)


        # Explosions for light messages
        expl_message = ['' for i in range(N)]
        if close:
            planet_pos = cam_pos + cam_dir*utils.km_to_AU(8000.)+ np.array([0.,utils.km_to_AU(10000),0])
            expl_pos = cam_pos + cam_dir*utils.km_to_AU(200) #np.array([value*200*km_to_AU,0,0])
        else:
            planet_pos = cam_pos + cam_dir*utils.m_to_AU(np.abs(obs_real - other_obs_real))
            expl_pos = cam_pos + cam_dir*utils.km_to_AU(200) + np.array([0,utils.km_to_AU(-50),0])
        sc_pos = cam_pos + cam_dir*utils.km_to_AU(2000.) + np.array([0.,utils.km_to_AU(1000),utils.km_to_AU(-1000)])
        expl_color = np.array([1,1,1])
        expl_visible = np.zeros(N)
        cnt = 0
        for index in indlist:
            for i in range(20):
                #expl_message[index:index+15] = [('Light signal registered at time %e seconds' %time[index])][:]
                ii = np.amin([index + i,N-1])
                expl_visible[ii] =1
                if close:
                    expl_message[ii] = events_messages_close[cnt] + '\n ' + str(sec_to_clockhours(time[index]))
                else:
                    expl_message[ii] = events_messages_far[cnt] + '\n ' + str(sec_to_clockhours(time[index]))
            cnt += 1
            if (cnt == nevents):
                cnt = 0

        sat1_messages =  ['' for i in range(N)]
        sat2_messages =  ['' for i in range(N)]

        for index in locindlist:
            for i in range(20):
                ii = np.amin([index + i,N-1])
                sat1_messages[ii] = events_messages_sat[cnt]+' '+ other_dt_list_text[cnt]
            cnt += 1
            if (cnt == nevents):
                cnt = 0

        if close:
            sat1_messages, sat2_messages = sat2_messages, sat1_messages


        obj_list = [['Sat1','Satellite',sc_pos,1.5,[0.7,0.2,0.3],sat1_messages,None,None,None],
                    ['Sat2','Satellite',sc_plt_pos,1.5,[0.2,0.2,0.7],sat2_messages,None,None,None],
                    ['Light','explosion',expl_pos,100,expl_color,expl_message,None,expl_visible,None]]

        #print('positions:',cam_pos,planet_pos)

        self._write_to_xml(time,cam_pos,cam_dir,camera_messages=cam_message,other_objects=obj_list,planet_pos=planet_pos,filename=filename,field_of_view=90,use_obj_scaling=None, origo_location=np.array([0,0,0]),black_hole=True, toggle_clock = False)

        if write_solutions:

            #Solution writing

            solution_name='Solutions_black_hole_schedules.txt'
            solution_2C=self._get_new_solution_file_handle(solution_name)
            solution_2C.write('Solutons to 2C.2\n')
            solution_2C.write('Mass of black hole in meters: %f\n' %black_hole_mass_m)
            solution_2C.write('Times for "close" observer in seconds:\n')
            if not close:
                for time in dt_list:
                    solution_2C.write('%g, ' %float(time))
            else:
                for time in other_dt_list:
                    solution_2C.write('%g, ' %float(time))
            #solution_2C.write('\n3. No numerical solution\n')
            solution_2C.write('\nTimes for "far" observer in seconds:\n')
            if not close:
                for time in other_dt_list:
                    solution_2C.write('%g, ' %float(time))
            else:
                for time in dt_list:
                    solution_2C.write('%g, ' %float(time))
            #solution_2C.write('\n5. No numerical solution\n')
            solution_2C.close()

    def _set_solution_path(self, solution_path=None):
        """Specifies whether and where to write solution text files.

        Parameters
        ----------
        solution_path : str, optional
            Specifies the path to the directory where output solution text files should be stored.
            By default, a folder called "Solutions" is created in the working directory.
        """
        self._solution_path = 'Solutions' if solution_path is None else os.path.abspath(str(solution_path))

    def _get_new_solution_file_handle(self, filename):
        if not os.path.isdir(self._solution_path):
            os.mkdir(self._solution_path)
        return open(os.path.join(self._solution_path, filename), 'w')

    def _set_debugging(self, activate_debugging):
        self._debug = bool(activate_debugging)

    def _set_test_mode(self, activate_test_mode):
        self._run_in_test_mode = bool(activate_test_mode)

    def _lambda_to_RGB(self, lambda_m):

        lambda_m = np.copy(lambda_m)/1e-9

        if lambda_m <= 450:
            rgb = [255,1,255]
        if 450 < lambda_m <= 495:
            rgb = [0,1,255]
        if 495 < lambda_m <= 570:
            rgb = [1,255,1]
        if 570 < lambda_m <= 590:
            rgb = [255,255,1]
        if 590 < lambda_m <= 620:
            rgb = [255,50,1]
        if lambda_m > 620:
            rgb = [255,5,5]

        return rgb

    def _write_to_xml(self, time_array, cam_pos, cam_dir, planet_pos=np.array([0,0,0]), other_objects=[], camera_messages=None,
                      planet_messages=None, ruler=None, up_vec=np.array([0,0,1]), field_of_view=70, filename='test_data.xml', planet_idx=0,
                      c=const.c_AU_pr_s, laser_scale=1, use_obj_scaling=1, cheat_light_speed=False, origo_location=np.array([1,0,0]),
                      black_hole=False, play_speed=None, show_clock=1, planet2_pos=None, planet3_pos=None, chosen_planet2=1, chosen_planet3=2, toggle_clock=True):
        """
        All positions are given relative to a virtual origo, which is then moved to [1,0,0]AU before sent to MCAst.
        @ time_array     =  Array of the timepoints to simulate.
        @ cam_pos        =  Array of camera positions at given timepoints. Shape (nr_frames, 3)
                            or (3,) for static camera position.
        @ cam_dir        =  Array of camera directions. Either direction vector
                            with shape (nr_frames, 3) or direction angles
                            with shape (nr_frames, 2). Can also be (3,) and (2,) for static direction.
                            First angle is upwards/downwards (0 - pi), second angle is in plane (0 - 2pi).
        @ planet_pos     =  Static position of planet. Shape (nr_frames, 3) or (3,). Defaults to [0,0,0].
        @ other_objects  =  Nested list with info about all non-planet/rocket objects. Shape (nr_objects, 7)
                     [Object name, Object string, Object positions array, Size scale, Color, Message list, Sound list, Visibility list, Orientation]
                     @ Object name      =  Name of object (only shows up in SSView)
                     @ Object string    =  Object type. Valid input: "Satellite", "Sphere01", "Explosion", Laser.
                     @ Object positions array  =  Shape (nr_frames, 3)
                     @ Size scale       =  Shape scaling of object, scalar.
                     @ Color            =  RGB. Values between 0 and 1. Shape (3,)
                     @ Message list     =  List of object-specific messages each frame, Shape = (nr_frames). Send None for no messages.
                     @ Sound list       =  List of object specific sounds. Shape = (nr_frames). Send None for no sounds.
                     @ Visibility list  =  Visibility of object each frame, 0 or 1. Shape = (nr_frames). Send None for always visible.
                     @ Orientation      =  3-vector orientation of object. Optional, Auto-orient by default (Value None).
        @ camera_messages  =  messages displayed on screen. Shape = (nr_frames).
        @ planet_messages  =  messages displayed on planet. Shape = (nr_frames).
        @ ruler    = Information about ruler. List with [rulerStart, rulerEnd, ticks, rulerUnit, rulerDistance, rulerHeight (0-1) defult 0.13 not necesarry to enter].
                     If no argument is provided there will be no ruler.
        @ c = Light speed in your system. If you want no componentwise
                     scaling of moving objects, simply set this to a reasonably large value. By default c in AU/s.
        @ laser_scale = Laser scale in the direction it is moving in.
        @ use_obj_scaling = 1 by default, if u dont want any objects scaled change to not 1
        @ origo_location = Location of events are sent relative to a local origo (e.g. center of planet).
                           This variable transitions that origo to a position relative to the sun.
        @ up_vec   = Upward direction vector of camera, Shape = (3,) or (nr_frames, 3)
        @ show_clock    = Toggle whether to show clock or not. 1 (default) is on, 0 off
        """

        self._cheat_light_speed = cheat_light_speed

        if self._debug: print('Entering SR XML writer with seed: %d and chosen planet: %d' % (self.seed, planet_idx))

        nr_frames = len(time_array)

        # Making sure we arent passing any arguments by reference.
        time_array = np.copy(time_array)
        cam_pos = np.copy(cam_pos)
        cam_dir = np.copy(cam_dir)
        planet_pos = np.copy(planet_pos)
        other_objects = copy(other_objects)

        # Making time-array for clock-printing:
        if time_array[-1] - time_array[0] >= 1:
            clock_time_array = np.copy(time_array)
            clockUnit = 'seconds'
        elif time_array[-1] - time_array[0] >= 1e-3:
            clock_time_array = np.copy(time_array)*1e3
            clockUnit = 'milli seconds'
        elif time_array[-1] - time_array[0] >= 1e-6:
            clock_time_array = np.copy(time_array)*1e6
            clockUnit = 'micro seconds'
        else:
            clock_time_array = np.copy(time_array)*1e9
            clockUnit = 'nano seconds'

        if np.shape(planet_pos) == (nr_frames, 3):
            if self._debug: print('Dynamic planet position.')

            planet_pos = np.array(planet_pos, dtype=np.float64)
            planet_pos += origo_location
        elif np.shape(planet_pos) == (3,):
            if self._debug: print('Static planet position. Castig time axis.')
            planet_pos = np.array(planet_pos, dtype=np.float64)
            planet_pos = np.zeros( shape = (nr_frames, 3) ) + planet_pos + origo_location
        else:
            raise IndexError('Parameter "planet_pos" has shape %s, expected %s or %s'\
            % (np.shape(planet_pos), (3,), (nr_frames, 3)))

        if (not planet2_pos is None):
             planet2_pos = np.copy(planet2_pos)
             if np.shape(planet2_pos) == (nr_frames, 3):
                 if self._debug: print('Dynamic planet2 position.')

                 planet2_pos = np.array(planet2_pos, dtype=np.float64)
                 planet2_pos += origo_location
             elif np.shape(planet2_pos) == (3,):
                 if self._debug: print('Static planet position. Castig time axis.')
                 planet2_pos = np.array(planet2_pos, dtype=np.float64)
                 planet2_pos = np.zeros( shape = (nr_frames, 3) ) + planet2_pos + origo_location
             else:
                 raise IndexError('Parameter "planet_pos" has shape %s, expected %s or %s'\
                                  % (np.shape(planet2_pos), (3,), (nr_frames, 3)))

        if (not planet3_pos is None):
            planet3_pos = np.copy(planet3_pos)
            if np.shape(planet3_pos) == (nr_frames, 3):
                if self._debug: print('Dynamic planet3 position.')

                planet3_pos = np.array(planet3_pos, dtype=np.float64)
                planet3_pos += origo_location
            elif np.shape(planet3_pos) == (3,):
                if self._debug: print('Static planet position. Castig time axis.')
                planet3_pos = np.array(planet3_pos, dtype=np.float64)
                planet3_pos = np.zeros( shape = (nr_frames, 3) ) + planet3_pos + origo_location
            else:
                raise IndexError('Parameter "planet_pos" has shape %s, expected %s or %s'\
                % (np.shape(planet3_pos), (3,), (nr_frames, 3)))


        if planet_messages is None:
            planet_messages = ['' for i in range(nr_frames)]

        if camera_messages is None:
            camera_messages = ['' for i in range(nr_frames)]

        # Checking if camera position is static, dynamic, or of wrong length.
        # If static, introduces a time-axis with repeating static values.
        if np.shape(cam_pos) == (nr_frames, 3):
            stat_cam_pos = False
            if self._debug: print('Dynamic camera position.')
            cam_pos += origo_location
        elif np.shape(cam_pos) == (3,):
            stat_cam_pos = True
            if self._debug: print('Stationary camera position. Introducing time-axis manually.')
            cam_pos = np.zeros( shape = (nr_frames, 3) ) + cam_pos + origo_location  # Giving cam_pos a time-axis, with repeating values.
        else:
            raise IndexError('Parameter "cam_pos" has shape %s, expected %s or %s'\
            % (np.shape(cam_pos), (3,), (nr_frames, 3)))


        # Checking if cam_dir is given in angles or direction vectors by looking at its shape.
        # Also checking if static or dynamic. If static, introducing a time-axis with repeating values.
        dir_shape = np.shape(cam_dir)
        if dir_shape == (nr_frames, 2):
            stat_cam_uses_angles = False
            cam_uses_angles = True
            if self._debug: print('Dynamic camera angles.')
        elif dir_shape == (2,):
            stat_cam_uses_angles = True
            cam_uses_angles = True
            if self._debug: print('Static camera angles. Introducing time-axis manually.')
            cam_dir = np.zeros( shape = (nr_frames, 2) ) + cam_dir
        elif dir_shape == (nr_frames, 3):
            stat_cam_dir_vec = False
            cam_uses_angles = False
            if self._debug: print('Dynamic camera vector.')
        elif dir_shape == (3,):
            stat_cam_dir_vec = True
            cam_uses_angles = False
            if self._debug: print('Static camera vector. Introducing time-axis manually.')
            cam_dir = np.zeros( shape = (nr_frames, 3) ) + cam_dir
        else:
            raise IndexError('Parameter "cam_dir" has shape %s. Expected %s or %s for angles or %s or %s for vector. Exiting.'\
            % (np.shape(cam_dir),(nr_frames,2), (2,), (nr_frames,3), (3,)))


        # If camera direction is given in angles, converting to direction vector,
        # because that's what the XML format uses.
        if cam_uses_angles:
            cam_dir_vec = np.zeros( shape = (nr_frames, 3) )
            cam_dir_vec[:,0] = np.cos(cam_dir[:,1]) * np.sin(cam_dir[:,0])
            cam_dir_vec[:,1] = np.sin(cam_dir[:,1]) * np.sin(cam_dir[:,0])
            cam_dir_vec[:,2] = np.cos(cam_dir[:,0])
        else:
            cam_dir_vec = np.array(np.copy(cam_dir), dtype=np.float64)
            # If cam_dir is a vector, set cam_dir_vec as a normalized copy of it.
            #cam_dir_vec /= np.linalg.norm(cam_dir_vec, axis=1)[:,None]
            cam_dir_vec /= np.apply_along_axis(np.linalg.norm, 1, cam_dir_vec)[:,None]


        # DEALING WITH UPVEC
        if str(up_vec) == 'auto':  # AU_to_matic calculation of up vector. Seems not to work for now. Not in use.
            sun_vec = planet_pos
            up_vec = np.zeros( shape = (nr_frames, 3) )
            for i in range(nr_frames):
                up_vec[i] = np.cross(sun_vec, cam_dir_vec[i])
            if up_vec[0,2] < 0:  # Turning vec if first z component is positive.
                up_vec = -up_vec


        if str(up_vec) == 'up':
            up_vec = cam_pos - planet_pos


        if np.shape(up_vec) == (nr_frames, 3):
            up_vec = np.array(up_vec, dtype=np.float64)
            up_vec /= np.apply_along_axis(np.linalg.norm, 1, up_vec)[:,None]
        elif np.shape(up_vec) == (3,):
            up_vec = np.array(up_vec, dtype=np.float64)
            up_vec /= np.linalg.norm(up_vec)
            up_vec = np.zeros( shape = (nr_frames, 3) ) + up_vec
        else:
            raise IndexError('Dust')


        # Unpack ruler settings if one is provided.
        if not ruler is None:
            if len(ruler) > 6 or len(ruler) < 5: # Check that the right amount of elements are entered.
                raise IndexError('Ruler settings list has length %g, expected 5 or 6 if display height is specified.'%len(ruler))
            rulerStart = ruler[0]
            rulerEnd = ruler[1]
            rulerTicks = ruler[2]
            rulerUnit = ruler[3]
            rulerDistance = ruler[4]

            if len(ruler) == 6:
                rulerHeight = ruler[5]
            else:
                rulerHeight = None

        # OBJECTS
        objects = etree.Element('Objects')
        # The star is a subelement of Objects
        star = etree.SubElement(objects, 'SerializedMCAstObject')
        if black_hole is True:
            etree.SubElement(star, 'category').text           = str('black hole')
        else:
            etree.SubElement(star, 'category').text           = str('star')
        etree.SubElement(star, 'pos_x').text              = str(0)
        etree.SubElement(star, 'pos_z').text              = str(0)
        etree.SubElement(star, 'pos_y').text              = str(0)
        etree.SubElement(star, 'rot_y').text              = str(0)
        if  black_hole is True:
            etree.SubElement(star, 'radius').text             = str(514702.474211) #100000
        else:
            etree.SubElement(star, 'radius').text             = str(self.system.star_radius) #100000
        etree.SubElement(star, 'temperature').text        = str(self.system.star_temperature) #4000
        etree.SubElement(star, 'seed').text               = str(int(self.seed * 1000 + 990))
        etree.SubElement(star, 'atmosphereDensity').text  = str(10)
        etree.SubElement(star, 'atmosphereHeight').text   = str(1.025)
        etree.SubElement(star, 'outerRadiusScale').text   = str(1.0025)
        etree.SubElement(star, 'name').text               = str('The star')

        # Star sub-objects:
        star_objects = etree.SubElement(star, 'Objects')


        # PLANET
        # Calculate planet scales first
        planet_pos_array = np.zeros( shape = (nr_frames, 3))
        planet_pos_array[:] = planet_pos
        if use_obj_scaling == 1:
            if self._debug: print('Scaling planet.')
            #planet_scales_array = 1/self._get_lorentz(time_array, cam_pos, planet_pos_array, c, object_name='planet')
            planet_scales_array = 1/self._get_lorentz_3D(time_array, cam_pos, planet_pos_array, c, object_name='planet')
            #print('obj_scaling:',cam_pos[0],cam_pos[100],planet_pos_array[0],planet_pos_array[100],planet_scales_array[0])
        else:
            #planet_scales_array = np.ones(nr_frames)
            planet_scales_array = np.ones([nr_frames,3])


        planet = etree.SubElement(star_objects, 'SerializedMCAstObject')
        etree.SubElement(planet, 'pos_x').text             = str(planet_pos[0,0])
        etree.SubElement(planet, 'pos_z').text             = str(planet_pos[0,1])
        etree.SubElement(planet, 'pos_y').text             = str(planet_pos[0,2])
        etree.SubElement(planet, 'rot_y').text             = str(0)
        etree.SubElement(planet, 'seed').text              = str(int(self.seed * 1000 + planet_idx))
        etree.SubElement(planet, 'radius').text            = str(self.system.radii[planet_idx])
        etree.SubElement(planet, 'temperature').text       = str(self.system.star_temperature*np.sqrt((utils.km_to_AU(self.system.star_radius))/(2*self.system.semi_major_axes[planet_idx])))
        etree.SubElement(planet, 'atmosphereDensity').text = str(np.log(self.system.atmospheric_densities[planet_idx])/np.log(25))
        etree.SubElement(planet, 'atmosphereHeight').text  = str(1.025)
        etree.SubElement(planet, 'outerRadiusScale').text  = str(1.0025) #TODO ?
        etree.SubElement(planet, 'category').text          = str('planet')
        etree.SubElement(planet, 'name').text              = str('planet ' + str(planet_idx) )

        frames = etree.SubElement(planet, 'Frames')
        for i in range(nr_frames):
            frame = etree.SubElement(frames, 'Frame')
            etree.SubElement(frame, 'id').text             = str(i)
            etree.SubElement(frame, 'pos_x').text          = str(planet_pos[i,0])
            etree.SubElement(frame, 'pos_z').text          = str(planet_pos[i,1]) #TODO remove maybe?
            etree.SubElement(frame, 'pos_y').text          = str(planet_pos[i,2])
            etree.SubElement(frame, 'displayMessage').text = str(planet_messages[i])
            etree.SubElement(frame, 'rot_y').text          = str(0)

            if np.amin(np.abs(planet_scales_array[i,:])) != 1:
                scaledir = np.argmin(np.abs(planet_scales_array[i,:]))
                if np.abs(up_vec[i,scaledir]) == 0:
                    leftright = 1 #left/right movement
                if np.abs(up_vec[i,scaledir]) == 1:
                    leftright = 0 #up/down movement
                if np.abs(up_vec[i,0]) == 1 and leftright == 1:
                    if scaledir == 1:
                        etree.SubElement(frame, 'scale_z').text        = str(planet_scales_array[i,scaledir])
                    if scaledir == 2:
                        etree.SubElement(frame, 'scale_y').text        = str(planet_scales_array[i,scaledir])
                if np.abs(up_vec[i,0]) == 1 and leftright == 0:
                    etree.SubElement(frame, 'scale_x').text        = str(planet_scales_array[i,scaledir])
                if np.abs(up_vec[i,1]) == 1 and leftright == 1:
                    etree.SubElement(frame, 'scale_x').text        = str(planet_scales_array[i,scaledir])
                if np.abs(up_vec[i,2]) == 1 and leftright == 1:
                    if scaledir == 1:
                        etree.SubElement(frame, 'scale_z').text        = str(planet_scales_array[i,scaledir])
                    if scaledir == 0:
                        etree.SubElement(frame, 'scale_x').text        = str(planet_scales_array[i,scaledir])
                if np.abs(up_vec[i,0]) != 1 and leftright == 0:
                    etree.SubElement(frame, 'scale_y').text        = str(planet_scales_array[i,scaledir])
            #print('planet scale:',i,planet_scales_array[i])
            #etree.SubElement(frame, 'scale_x').text        = str(planet_scales_array[i,0])  # TODO: Check if works as intended.
            #etree.SubElement(frame, 'scale_y').text        = str(planet_scales_array[i,1])  # TODO: Check if works as intended.
            #etree.SubElement(frame, 'scale_z').text        = str(planet_scales_array[i,2])  # TODO: Check if works as intended.



        if (not planet2_pos is None):
             # PLANET2
            # Calculate planet scales first
            planet2_pos_array = np.zeros( shape = (nr_frames, 3))
            planet2_pos_array[:] = planet2_pos
            if use_obj_scaling == 1:
                if self._debug: print('Scaling planet2.')
                #planet_scales_array = 1/self._get_lorentz(time_array, cam_pos, planet_pos_array, c, object_name='planet')
                planet2_scales_array = 1/self._get_lorentz_3D(time_array, cam_pos, planet2_pos_array, c, object_name='planet2')
                #print('obj_scaling:',cam_pos[0],cam_pos[100],planet_pos_array[0],planet_pos_array[100],planet_scales_array[0])
            else:
                #planet_scales_array = np.ones(nr_frames)
                planet2_scales_array = np.ones([nr_frames,3])


            planet2 = etree.SubElement(star_objects, 'SerializedMCAstObject')
            etree.SubElement(planet2, 'pos_x').text             = str(planet2_pos[0,0])
            etree.SubElement(planet2, 'pos_z').text             = str(planet2_pos[0,1])
            etree.SubElement(planet2, 'pos_y').text             = str(planet2_pos[0,2])
            etree.SubElement(planet2, 'rot_y').text             = str(0)
            etree.SubElement(planet2, 'seed').text              = str(int(self.seed * 1000 + chosen_planet2))
            etree.SubElement(planet2, 'radius').text            = str(self.system.radii[chosen_planet2])
            etree.SubElement(planet2, 'temperature').text       = str(self.system.star_temperature*np.sqrt((utils.km_to_AU(self.system.star_radius))/(2*self.system.semi_major_axes[chosen_planet2])))
            etree.SubElement(planet2, 'atmosphereDensity').text = str(np.log(self.system.atmospheric_densities[chosen_planet2])/np.log(25))
            etree.SubElement(planet2, 'atmosphereHeight').text  = str(1.025)
            etree.SubElement(planet2, 'outerRadiusScale').text  = str(1.0025) #TODO ?
            etree.SubElement(planet2, 'category').text          = str('planet2')
            etree.SubElement(planet2, 'name').text              = str('planet2 ' + str(chosen_planet2) )

            frames = etree.SubElement(planet2, 'Frames')
            for i in range(nr_frames):
                frame = etree.SubElement(frames, 'Frame')
                etree.SubElement(frame, 'id').text             = str(i)
                etree.SubElement(frame, 'pos_x').text          = str(planet2_pos[i,0])
                etree.SubElement(frame, 'pos_z').text          = str(planet2_pos[i,1]) #TODO remove maybe?
                etree.SubElement(frame, 'pos_y').text          = str(planet2_pos[i,2])
                etree.SubElement(frame, 'displayMessage').text = str(planet_messages[i])
                etree.SubElement(frame, 'rot_y').text          = str(0)


                if np.amin(np.abs(planet2_scales_array[i,:])) != 1:
                    scaledir = np.argmin(np.abs(planet2_scales_array[i,:]))
                    if np.abs(up_vec[i,scaledir]) == 0:
                        leftright = 1 #left/right movement
                    if np.abs(up_vec[i,scaledir]) == 1:
                        leftright = 0 #up/down movement
                    if np.abs(up_vec[i,0]) == 1 and leftright == 1:
                        if scaledir == 1:
                            etree.SubElement(frame, 'scale_z').text        = str(planet2_scales_array[i,scaledir])
                        if scaledir == 2:
                            etree.SubElement(frame, 'scale_y').text        = str(planet2_scales_array[i,scaledir])
                    if np.abs(up_vec[i,0]) == 1 and leftright == 0:
                        etree.SubElement(frame, 'scale_x').text        = str(planet2_scales_array[i,scaledir])
                    if np.abs(up_vec[i,1]) == 1 and leftright == 1:
                        etree.SubElement(frame, 'scale_x').text        = str(planet2_scales_array[i,scaledir])
                    if np.abs(up_vec[i,2]) == 1 and leftright == 1:
                        if scaledir == 1:
                            etree.SubElement(frame, 'scale_z').text        = str(planet2_scales_array[i,scaledir])
                        if scaledir == 0:
                            etree.SubElement(frame, 'scale_x').text        = str(planet2_scales_array[i,scaledir])
                    if np.abs(up_vec[i,0]) != 1 and leftright == 0:
                        etree.SubElement(frame, 'scale_y').text        = str(planet2_scales_array[i,scaledir])



                #etree.SubElement(frame, 'scale_z').text        = str(planet_scales_array[i])  # TODO: Check if works as intended.
                #print('planet scale:',i,planet_scales_array[i])
                #etree.SubElement(frame, 'scale_x').text        = str(planet2_scales_array[i,0])  # TODO: Check if works as intended.
                #etree.SubElement(frame, 'scale_y').text        = str(planet2_scales_array[i,1])  # TODO: Check if works as intended.
                #etree.SubElement(frame, 'scale_z').text        = str(planet2_scales_array[i,2])  # TODO: Check if works as intended.

        if (not planet3_pos is None):
             # PLANET3
            # Calculate planet scales first
            planet3_pos_array = np.zeros( shape = (nr_frames, 3))
            planet3_pos_array[:] = planet3_pos
            if use_obj_scaling == 1:
                if self._debug: print('Scaling planet3.')
                #planet_scales_array = 1/self._get_lorentz(time_array, cam_pos, planet_pos_array, c, object_name='planet')
                planet3_scales_array = 1/self._get_lorentz_3D(time_array, cam_pos, planet3_pos_array, c, object_name='planet3')
                #print('obj_scaling:',cam_pos[0],cam_pos[100],planet_pos_array[0],planet_pos_array[100],planet_scales_array[0])
            else:
                #planet_scales_array = np.ones(nr_frames)
                planet3_scales_array = np.ones([nr_frames,3])


            planet3 = etree.SubElement(star_objects, 'SerializedMCAstObject')
            etree.SubElement(planet3, 'pos_x').text             = str(planet3_pos[0,0])
            etree.SubElement(planet3, 'pos_z').text             = str(planet3_pos[0,1])
            etree.SubElement(planet3, 'pos_y').text             = str(planet3_pos[0,2])
            etree.SubElement(planet3, 'rot_y').text             = str(0)
            etree.SubElement(planet3, 'seed').text              = str(int(self.seed * 1000 + chosen_planet3))
            etree.SubElement(planet3, 'radius').text            = str(self.system.radii[chosen_planet3])
            etree.SubElement(planet3, 'temperature').text       = str(self.system.star_temperature*np.sqrt((utils.km_to_AU(self.system.star_radius))/(2*self.system.semi_major_axes[chosen_planet3])))
            etree.SubElement(planet3, 'atmosphereDensity').text = str(np.log(self.system.atmospheric_densities[chosen_planet3])/np.log(25))
            etree.SubElement(planet3, 'atmosphereHeight').text  = str(1.025)
            etree.SubElement(planet3, 'outerRadiusScale').text  = str(1.0025) #TODO ?
            etree.SubElement(planet3, 'category').text          = str('planet3')
            etree.SubElement(planet3, 'name').text              = str('planet3 ' + str(chosen_planet3) )

            frames = etree.SubElement(planet3, 'Frames')
            for i in range(nr_frames):
                frame = etree.SubElement(frames, 'Frame')
                etree.SubElement(frame, 'id').text             = str(i)
                etree.SubElement(frame, 'pos_x').text          = str(planet3_pos[i,0])
                etree.SubElement(frame, 'pos_z').text          = str(planet3_pos[i,1]) #TODO remove maybe?
                etree.SubElement(frame, 'pos_y').text          = str(planet3_pos[i,2])
                etree.SubElement(frame, 'displayMessage').text = str(planet_messages[i])
                etree.SubElement(frame, 'rot_y').text          = str(0)


                if np.amin(np.abs(planet3_scales_array[i,:])) != 1:
                    scaledir = np.argmin(np.abs(planet3_scales_array[i,:]))
                    if np.abs(up_vec[i,scaledir]) == 0:
                        leftright = 1 #left/right movement
                    if np.abs(up_vec[i,scaledir]) == 1:
                        leftright = 0 #up/down movement
                    if np.abs(up_vec[i,0]) == 1 and leftright == 1:
                        if scaledir == 1:
                            etree.SubElement(frame, 'scale_z').text        = str(planet3_scales_array[i,scaledir])
                        if scaledir == 2:
                            etree.SubElement(frame, 'scale_y').text        = str(planet3_scales_array[i,scaledir])
                    if np.abs(up_vec[i,0]) == 1 and leftright == 0:
                        etree.SubElement(frame, 'scale_x').text        = str(planet3_scales_array[i,scaledir])
                    if np.abs(up_vec[i,1]) == 1 and leftright == 1:
                        etree.SubElement(frame, 'scale_x').text        = str(planet3_scales_array[i,scaledir])
                    if np.abs(up_vec[i,2]) == 1 and leftright == 1:
                        if scaledir == 1:
                            etree.SubElement(frame, 'scale_z').text        = str(planet3_scales_array[i,scaledir])
                        if scaledir == 0:
                            etree.SubElement(frame, 'scale_x').text        = str(planet3_scales_array[i,scaledir])
                    if np.abs(up_vec[i,0]) != 1 and leftright == 0:
                        etree.SubElement(frame, 'scale_y').text        = str(planet3_scales_array[i,scaledir])


                #etree.SubElement(frame, 'scale_z').text        = str(planet_scales_array[i])  # TODO: Check if works as intended.
                #print('planet scale:',i,planet_scales_array[i])
                #etree.SubElement(frame, 'scale_x').text        = str(planet3_scales_array[i,0])  # TODO: Check if works as intended.
                #etree.SubElement(frame, 'scale_y').text        = str(planet3_scales_array[i,1])  # TODO: Check if works as intended.
                #etree.SubElement(frame, 'scale_z').text        = str(planet3_scales_array[i,2])  # TODO: Check if works as intended.


        #OTHER OBJECTS
        for other_object in other_objects:

            obj_name         = other_object[0]
            obj_string       = other_object[1]
            obj_pos_array    = other_object[2] + origo_location  # Object position is now relative to star.
            obj_scale        = other_object[3]
            obj_color        = other_object[4]
            obj_message_list = other_object[5]
            obj_sound_list   = other_object[6]
            obj_visible      = other_object[7]
            obj_orientation  = other_object[8]
            if obj_message_list is None:
                obj_message_list = ['' for i in range(nr_frames)]
            if obj_sound_list is None:
                obj_sound_list = ['' for i in range(nr_frames)]
            if obj_visible is None or obj_visible is True:
                obj_visible = [1 for i in range(nr_frames)]
            if np.shape(obj_pos_array) == (3,):    # Casting time axis if doesn't exist.
                obj_pos_array = np.zeros(shape=(nr_frames,3)) + obj_pos_array

            if self._debug: print('Making', obj_string, 'object')

            if obj_string == 'Laser':
                obj_scales_array = laser_scale*np.ones(nr_frames)
            else:                                            # All other physical bodies are scaled
                if use_obj_scaling == 1:     #Is always true if not spesified in key word arg
                    obj_scales_array = 1/self._get_lorentz(time_array, cam_pos, obj_pos_array, c, object_name=obj_name)
                else:
                    obj_scales_array = np.ones(nr_frames)

            obj = etree.SubElement(star_objects, 'SerializedMCAstObject')
            if obj_orientation is None:
                etree.SubElement(obj, 'autoOrient').text = str(1)
            elif np.shape(obj_orientation) == (3,):
                etree.SubElement(obj, 'autoOrient').text = str(0)
            else:
                raise ValueError('Expected shape (3,) or None for Orientation parameter on object %s. Got shape %s' % (obj_name, np.shape(obj_orientation)))
            etree.SubElement(obj, 'pos_x').text          = str(obj_pos_array[0,0])
            etree.SubElement(obj, 'pos_z').text          = str(obj_pos_array[0,1])
            etree.SubElement(obj, 'pos_y').text          = str(obj_pos_array[0,2])
            # Explosion is not a 3dobject, it is an explosion
            if obj_string == 'explosion':
                etree.SubElement(obj, 'category').text       = str('explosion')
            else:
                etree.SubElement(obj, 'category').text       = str('3dobject')
            etree.SubElement(obj, 'name').text           = str(obj_name)

            if obj_string == 'explosion':
                pass # Explosions dont have a material type. No object string.
            elif obj_string == 'Laser': # Lasers have their own material
                etree.SubElement(obj, 'objectMaterial').text = str('LaserMaterial')
                etree.SubElement(obj, 'objectString').text   = str(obj_string)
            else: # Satellite and spheres have HullMaterial as their material type
                etree.SubElement(obj, 'objectMaterial').text = str('HullMaterial')  #TODO change
                etree.SubElement(obj, 'objectString').text   = str(obj_string)
            etree.SubElement(obj, 'objectScale').text    = str(obj_scale)
            etree.SubElement(obj, 'color_r').text        = str(obj_color[0])
            etree.SubElement(obj, 'color_g').text        = str(obj_color[1])
            etree.SubElement(obj, 'color_b').text        = str(obj_color[2])

            frames = etree.SubElement(obj, 'Frames')
            for i in range(nr_frames):
                frame = etree.SubElement(frames, 'Frame')
                etree.SubElement(frame, 'id').text            = str(i)
                etree.SubElement(frame, 'pos_x').text         = str(obj_pos_array[i,0])
                etree.SubElement(frame, 'pos_z').text         = str(obj_pos_array[i,1])
                etree.SubElement(frame, 'pos_y').text         = str(obj_pos_array[i,2])
                if not obj_sound_list is None:
                    etree.SubElement(frame, 'sound').text     = str(obj_sound_list[i])
                if obj_message_list[i] != '':
                    etree.SubElement(frame, 'displayMessage').text= str(obj_message_list[i])
                etree.SubElement(frame, 'time').text          = str(clock_time_array[i])

                if obj_string == 'explosion':
                    etree.SubElement(frame, 'color_r').text        = str(obj_color[0])
                    etree.SubElement(frame, 'color_g').text        = str(obj_color[1])
                    etree.SubElement(frame, 'color_b').text        = str(obj_color[2])

                # TODO: THIS WILL BE FIXED IN THE NEXT MCAST VERSION
                if obj_string == 'explosion':
                    etree.SubElement(frame, 'scale_x').text     = str(obj_scales_array[i])
                else:
                    etree.SubElement(frame, 'scale_z').text      = str(obj_scales_array[i])

                if obj_visible[i] == 0:
                    etree.SubElement(frame, 'visible').text   = str(0)

                if not obj_orientation is None:
                    etree.SubElement(frame, 'rot_x').text     = str(obj_orientation[0])
                    etree.SubElement(frame, 'rot_z').text     = str(obj_orientation[1])
                    etree.SubElement(frame, 'rot_y').text     = str(obj_orientation[2])


        # CAMERA
        cameras = etree.Element('Cameras')
        for i in range(nr_frames):
            camera = etree.SubElement(cameras, 'SerializedCamera')
            etree.SubElement(camera, 'cam_x').text = str(cam_pos[i,0])
            etree.SubElement(camera, 'cam_z').text = str(cam_pos[i,1])
            etree.SubElement(camera, 'cam_y').text = str(cam_pos[i,2])
            etree.SubElement(camera, 'dir_x').text = str(cam_dir_vec[i,0])
            etree.SubElement(camera, 'dir_z').text = str(cam_dir_vec[i,1])
            etree.SubElement(camera, 'dir_y').text = str(cam_dir_vec[i,2])
            etree.SubElement(camera, 'up_x').text = str(up_vec[i,0])
            etree.SubElement(camera, 'up_z').text = str(up_vec[i,1])
            etree.SubElement(camera, 'up_y').text = str(up_vec[i,2])
            etree.SubElement(camera, 'fov').text = str(field_of_view)
            etree.SubElement(camera, 'scale_x').text = str(1)
            etree.SubElement(camera, 'scale_z').text = str(1)
            etree.SubElement(camera, 'scale_y').text = str(1)
            etree.SubElement(camera, 'displayMessage').text = (camera_messages[i])
            etree.SubElement(camera, 'time').text = str(clock_time_array[i])
            etree.SubElement(camera, 'frame').text = str(i)
            #TODO: Check if 'scale' is needed.

        with open(os.path.join(self.system.data_path, filename), 'w') as outfile:
            outfile.write("""<?xml version="1.0" encoding="utf-8"?>\n""")
            outfile.write("""<SerializedWorld xmlns:xsi="http://www.w3.org/2001/""")
            outfile.write("""XMLSchema-instance"\n xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n""")
            outfile.write("""<sun_intensity>0.100</sun_intensity>\n""")
            outfile.write("""<screenshot_width>900</screenshot_width>\n""")
            outfile.write("""<screenshot_height>900</screenshot_height>\n""")
            outfile.write("""<global_radius_scale>0.985</global_radius_scale>\n""")
            outfile.write("""<uuid>5acbd644-37c7-11e6-ac61-9e71128cae77</uuid>\n""")
            outfile.write("""<skybox>000</skybox>\n""")
            if play_speed is None:
                outfile.write("""<defaultPlaySpeed>0.6</defaultPlaySpeed>""")
            else:
                outfile.write("""<defaultPlaySpeed>%f</defaultPlaySpeed>""" % play_speed)

            outfile.write("""<showTime>%g</showTime>"""%(show_clock))

            if not ruler is None: # If ruler settings are provided, create ruler
                outfile.write("""<rulerStart>%g</rulerStart>\n"""%rulerStart)
                outfile.write("""<rulerEnd>%g</rulerEnd>\n"""%rulerEnd)
                outfile.write("""<rulerTicks>%g</rulerTicks>\n"""%rulerTicks)
                outfile.write("""<rulerUnit>%s</rulerUnit>\n"""%rulerUnit)
                outfile.write("""<rulerPlaneDistance>%s</rulerPlaneDistance>\n"""%rulerDistance)
                if rulerHeight == None:
                    outfile.write("""<rulerPosition>0.13</rulerPosition>\n""")
                else:
                    outfile.write("""<rulerPosition>%g</rulerPosition>\n"""%rulerHeight)


            # Add unit for the clock
            outfile.write("""<clockUnit>%s</clockUnit>\n"""%clockUnit)


            outfile.write(etree.tostring(objects, pretty_print = True, encoding="unicode"))
            outfile.write(etree.tostring(cameras, pretty_print = True, encoding="unicode"))
            outfile.write("""<renderClock>%g</renderClock>"""%(int(toggle_clock)))

            outfile.write("""</SerializedWorld>""")

        print('Video file written to %s. Open and view it in MCAst!' %(os.path.join(self.system.data_path, filename)))

    def _get_lorentz(self, time_array, cam_pos_array, obj_pos_array, c=const.c_AU_pr_s, object_name='unknown'):
        """
        Compute lorentz length contraction for an object moving relative
        to the camera for each frame.
        Params:
        @ time_array     = Array with time points, shape (nr_frames)
        @ cam_pos_array  = Array with camera positions, shape (nr_frames, 3)
        @ obj_pos_array  = Array with object positions, shape (nr_frames, 3)
        @ c              = Light speed in the system
        Returns:
        @ lorentz        = Array with lorentz factor for each frame, shape (nr_frames)
        """
        obj_pos_arr = np.copy(obj_pos_array)
        obj_pos_arr = obj_pos_arr - cam_pos_array  # obj pos now relative to camera.

        nr_frames = len(time_array)
        # Velocity of object relative to camera (observer)
        vel_array = np.zeros( shape = (nr_frames, 3) )
        # Symmetric difference quotient for all steps except the first
        vel_array[1:,0] = (obj_pos_arr[1:,0] - obj_pos_arr[:-1,0]) / (time_array[1:] - time_array[:-1])
        vel_array[1:,1] = (obj_pos_arr[1:,1] - obj_pos_arr[:-1,1]) / (time_array[1:] - time_array[:-1])
        vel_array[1:,2] = (obj_pos_arr[1:,2] - obj_pos_arr[:-1,2]) / (time_array[1:] - time_array[:-1])
        # Forward differentiation for the first time step
        vel_array[0,0] = (obj_pos_arr[1,0] - obj_pos_arr[0,0]) / (time_array[1] - time_array[0])
        vel_array[0,1] = (obj_pos_arr[1,1] - obj_pos_arr[0,1]) / (time_array[1] - time_array[0])
        vel_array[0,2] = (obj_pos_arr[1,2] - obj_pos_arr[0,2]) / (time_array[1] - time_array[0])
        absvels = np.apply_along_axis(np.linalg.norm, 1, vel_array) # Absolute velocity in each step
        maxvel = np.max(absvels)                      # Max velocity in video
        if self._cheat_light_speed is False:
            if maxvel > c:
                raise ValueError('Detected maximum speed of %g in object %s, light speed is %g'%(maxvel, object_name, c))

        if self._cheat_light_speed is True:
            for i in range(len(absvels)):
                if absvels[i] > c:
                    absvels[i] = 0
        lorentz = 1 / np.sqrt(1 - absvels**2/c**2)
        return lorentz

    def _get_lorentz_3D(self, time_array, cam_pos_array, obj_pos_array, c=const.c_AU_pr_s, object_name='unknown'):
        """
        Compute lorentz length contraction for an object moving relative
        to the camera for each frame.
        Params:
        @ time_array     = Array with time points, shape (nr_frames)
        @ cam_pos_array  = Array with camera positions, shape (nr_frames, 3)
        @ obj_pos_array  = Array with object positions, shape (nr_frames, 3)
        @ c              = Light speed in the system
        Returns:
        @ lorentz        = Array with lorentz factor for each frame, shape (nr_frames)
        """
        obj_pos_arr = np.copy(obj_pos_array)
        obj_pos_arr = obj_pos_arr - cam_pos_array  # obj pos now relative to camera.

        nr_frames = len(time_array)
        # Velocity of object relative to camera (observer)
        vel_array = np.zeros( shape = (nr_frames, 3) )
        # Symmetric difference quotient for all steps except the first
        vel_array[1:,0] = (obj_pos_arr[1:,0] - obj_pos_arr[:-1,0]) / (time_array[1:] - time_array[:-1])
        vel_array[1:,1] = (obj_pos_arr[1:,1] - obj_pos_arr[:-1,1]) / (time_array[1:] - time_array[:-1])
        vel_array[1:,2] = (obj_pos_arr[1:,2] - obj_pos_arr[:-1,2]) / (time_array[1:] - time_array[:-1])
        # Forward differentiation for the first time step
        vel_array[0,0] = (obj_pos_arr[1,0] - obj_pos_arr[0,0]) / (time_array[1] - time_array[0])
        vel_array[0,1] = (obj_pos_arr[1,1] - obj_pos_arr[0,1]) / (time_array[1] - time_array[0])
        vel_array[0,2] = (obj_pos_arr[1,2] - obj_pos_arr[0,2]) / (time_array[1] - time_array[0])
        #absvels = np.linalg.norm(vel_array, axis = 1) # Absolute velocity in each step
        maxvel = np.max(vel_array)                      # Max velocity in video
        if self._cheat_light_speed is False:
            if maxvel > c:
                raise ValueError('Detected maximum speed of %g in object %s, light speed is %g'%(maxvel, object_name, c))

        if self._cheat_light_speed is True:
        #    for i in range(len(absvels)):
        #        if absvels[i] > c:
        #            absvels[i] = 0
            vel_array[np.abs(vel_array) > c] = 0.999*c
        lorentz = 1 / np.sqrt(1 - vel_array**2/c**2)
        return lorentz

    def _lorentz_transform(self, t, pos, v, c=const.c_AU_pr_s):
        """
        Transformation of position/time 4-vector of event from rest-frame to moving frame.
        To transform an event from moving frame to rest frame, send in negative v.
        This function now only takes in 1-dimmentional movement along the axis of movement.
        All objects must be positioned, and move in the same one-dimmentional axis.
        INPUT
        @ pos  =  Position of events in rest frame along axis of movement. Shape = (nr_events)
        @ t    =  Time of event in rest frame. Shape = (nr_events).
        @ v    =  Speed of moving frame along movement axis. Shape = (nr_events) or scalar.
        RETURNS
        @ pos_marked   =  Poisitions of events in moving frame, along axis of movement. Shape = (nr_events)
        @ t_marked     =  Time of events in moving frame. Shape = (nr_events)
        """

        if np.sum( np.abs(v) >= c) > 0:
            print('Speed v = %f cannot exceed the speed of light, c = %f!' % (v, c))
            raise ValueError('v cannot exceed the speed of light')
        gamma = 1./np.sqrt(1-v**2/c**2)       # Array of Lorentz factors for each event.
        t_marked = -v*gamma*pos/c**2 + gamma*t     # Array of times of events in moving frame.
        pos_marked = gamma*pos - v*gamma*t    # Array of positions of events in moving frame.
        return t_marked, pos_marked

    def _focus_tanhyper(self, NR_frames_used, start=None, time=None):
        """
        Hyperbolic function to change focus or position smoothly
        Returns V array from 0 to 1 of two posible shapes(NR_frames,) or (time,)
        @ NR_frames_used        Number of frames used to change focus
        @ time                  if provided, shape(V) = (len(time),) IF u want V
                                to go over the hole time, otherwise shape(V) = (NR_frames_used,)
        @ start                 if provided, start = indices of time, where change of focus
                                should start, and last over NR_frames_used, otherwise start at begining
        """
        x = np.linspace(-2.5,2.5,NR_frames_used)
        if np.shape(time) == ():
            V = np.tanh(x)
            V += abs(np.min(V))      #Add min value, so V is positive
            V = V/np.max(V)          #Normaliser
        else:
            V = np.zeros([len(time)])
            if not start is None:
                V[start:start+NR_frames_used] = np.tanh(x)
                V[start:start+NR_frames_used] += abs(np.min(V))      #Add min value, so V is positive
                V[start+NR_frames_used:] += V[start+NR_frames_used-1]
            else:
                V[:NR_frames_used] = np.tanh(x)
                V[:NR_frames_used] += abs(np.min(V))      #Add min value, so V is positive
                V[NR_frames_used:] += V[NR_frames_used-1]
            V = V/np.max(V)          #Normaliser
        return V

    def _velocity_transformation(self, v_observer, v_object):
        """
        WARNING: Only takes natural units (fractions of c)
        @ v_observer  =  velocity of new observer relative to rest frame(old observer).
        @ v_object  =  velocity of observed object relative to rest frame(old observer).
        RETURN  =  velocity of object relative to the new observer.
        """

        return (v_object - v_observer)/(1 - v_observer*v_object)

    def _get_ruler_length(self, distance_to_object, field_of_view=70):
        """
        @ distance_to_object  =  distance to object we wish to measure with our ruler.
        @ field_of_view  =  camera field of view in degrees.
        RETURN  =  length of ruler in the same units as distance_to_object
        """
        return 2*distance_to_object*np.tan(utils.deg_to_rad(field_of_view/2))*(16/9)

    def _ref_sys_interpolate_func(self, time_array, pos_array, v):
        """
        @ time_array  =  time of positions in original frame of reference.
        @ pos_array  =  corresponding positions in original frame of reference.
        @ v  =  velocity of new frame of reference relative to original.
        Units in AU and seconds.
        RETURNS  =  Callable function which returns positions of event in new reference frame given a timepoint.
        """
        new_time_array, new_pos_array = self._lorentz_transform(time_array, pos_array, v)
        return interpolate.interp1d(new_time_array, new_pos_array, kind='linear', bounds_error=False, fill_value='extrapolate', assume_sorted=True)

    def _relativistic_doppler_shift(self, v, c=const.c_AU_pr_s):
        """
        wl : Wavelength (lambda in the lecture notes)
        Formula from part 2b.
        delta wl / wl = ( sqrt ([1 + v]/[1 - v]) - 1 )
        @ v      = Speed of object that emits light relative to observer in AU/s.
        @ c      = Speed of light in your system
        RETURNS   = delta wl / wl. (Relative change of wavelength)
        """
        return np.sqrt((1+v)/(1-v)) - 1

    def _object_list(self, obj_name, obj_type, pos, scale=1,
                    color_rgb=[1,1,1], msg_list=None, sound_list=None,
                    visible=None, orient=None):
        """ Formats input about an object to a list which can be sent to the writer"""
        return [obj_name, obj_type, pos, scale, color_rgb, msg_list, sound_list,
                visible, orient]
