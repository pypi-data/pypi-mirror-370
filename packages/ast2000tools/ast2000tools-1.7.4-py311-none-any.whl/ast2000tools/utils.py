# -*- coding: utf-8 -*-
"""Module containing various utility functions."""
from __future__ import division, print_function, absolute_import
from six.moves import urllib
#from distutils.version import StrictVersion
from packaging.version import Version as StrictVersion
import sys
import os
import subprocess
import json
import hashlib
import numpy as np
import ast2000tools.constants as const


def check_for_newer_version(verbose=False):
    """Informs about whether a newer version of ast2000tools than the one currently installed is available.

    Parameters
    ----------
    verbose : bool, optional
        Whether to print a confirmation message when the package is up to date.
        Default is False.

    Raises
    ------
    RuntimeError
        When ast2000tools is not installed through pip.
    """
    json_url = 'https://pypi.python.org/pypi/ast2000tools/json'
    connection = urllib.request.urlopen(json_url)
    json_data = json.loads(connection.read().decode('utf-8'))
    latest_version = sorted(json_data['releases'].keys(), key=StrictVersion)[-1]

    def has_pip_command(pip):
        try:
            subprocess.check_call([sys.executable, '-m', pip, '--version'], stdout=open(os.devnull, 'wb'),
                                                                            stderr=open(os.devnull, 'wb'))
        except subprocess.CalledProcessError:
            return False
        return True

    if sys.version_info[0] == 3 and has_pip_command('pip3'):
        pip = 'pip3'
    elif has_pip_command('pip'):
        pip = 'pip'
    else:
        raise RuntimeError('Could not find pip.')

    try:
        pip_show_message = subprocess.check_output([sys.executable, '-m', pip, 'show', 'ast2000tools']).decode('utf-8')
    except subprocess.CalledProcessError:
        raise RuntimeError('Could not find a copy of ast2000tools installed through pip.')

    pip_show_entries = [(line.split(':', 1) + [''])[:2] for line in pip_show_message.splitlines()]
    current_version = dict(pip_show_entries)['Version'].strip()

    if StrictVersion(latest_version) > StrictVersion(current_version):
        print('A newer version (v{} > v{}) of ast2000tools is available.'.format(latest_version, current_version))
        print('Please upgrade using the following command:\npip install --upgrade ast2000tools')
        return 1
    elif verbose:
        print('Your version of ast2000tools (v{}) is up to date.'.format(current_version))

    return 0


def get_seed(username):
    """Turns a username into a 5-digit seed.

    Parameters
    ----------
    username : str
        Your username.

    Returns
    -------
    int
        The 5-digit integer you should use as a seed.
    """
    username = str(username)

    tohash = username.lower().strip().encode('utf-8')
    hexstr = hashlib.sha224(tohash).hexdigest()
    num = int(hexstr, 16)
    seed = int(str(num)[-5:])
    return seed


def yr_to_s(yr):
    """Converts a given time from years to seconds.

    Parameters
    ----------
    yr : float or array_like
        A time in years.

    Returns
    -------
    float
        The corresponding time in seconds.
    """
    yr = float(yr) if np.isscalar(yr) else np.asarray(yr, dtype=float)
    return yr*const.yr


def s_to_yr(s):
    """Converts a given time from seconds to years.

    Parameters
    ----------
    s : float or array_like
        A time in seconds.

    Returns
    -------
    float
        The corresponding time in years.
    """
    s = float(s) if np.isscalar(s) else np.asarray(s, dtype=float)
    return s/const.yr


def day_to_s(day):
    """Converts a given time from days to seconds.

    Parameters
    ----------
    day : float or array_like
        A time in days.

    Returns
    -------
    float
        The corresponding time in seconds.
    """
    day = float(day) if np.isscalar(day) else np.asarray(day, dtype=float)
    return day*const.day


def s_to_day(s):
    """Converts a given time from seconds to days.

    Parameters
    ----------
    s : float or array_like
        A time in seconds.

    Returns
    -------
    float
        The corresponding time in days.
    """
    s = float(s) if np.isscalar(s) else np.asarray(s, dtype=float)
    return s/const.day


def day_to_yr(day):
    """Converts a given time from days to years.

    Parameters
    ----------
    day : float or array_like
        A time in days.

    Returns
    -------
    float
        The corresponding time in years.
    """
    day = float(day) if np.isscalar(day) else np.asarray(day, dtype=float)
    return day*const.day/const.yr


def yr_to_day(yr):
    """Converts a given time from years to days.

    Parameters
    ----------
    s : float or array_like
        A time in years.

    Returns
    -------
    float
        The corresponding time in days.
    """
    yr = float(yr) if np.isscalar(yr) else np.asarray(yr, dtype=float)
    return yr*const.yr/const.day


def AU_to_m(AU):
    """Converts a given distance from astronomical units to meters.

    Parameters
    ----------
    AU : float or array_like
        A distance in astronomical units.

    Returns
    -------
    float
        The corresponding distance in meters.
    """
    AU = float(AU) if np.isscalar(AU) else np.asarray(AU, dtype=float)
    return AU*const.AU


def m_to_AU(m):
    """Converts a given distance from meters to astronomical units.

    Parameters
    ----------
    m : float or array_like
        A distance in meters.

    Returns
    -------
    float
        The corresponding distance in astronomical units.
    """
    m = float(m) if np.isscalar(m) else np.asarray(m, dtype=float)
    return m/const.AU


def AU_to_km(AU):
    """Converts a given distance from astronomical units to kilometers.

    Parameters
    ----------
    AU : float or array_like
        A distance in astronomical units.

    Returns
    -------
    float
        The corresponding distance in kilometers.
    """
    AU = float(AU) if np.isscalar(AU) else np.asarray(AU, dtype=float)
    return AU*(const.AU*1e-3)


def km_to_AU(km):
    """Converts a given distance from kilometers to astronomical units.

    Parameters
    ----------
    km : float or array_like
        A distance in kilometers.

    Returns
    -------
    float
        The corresponding distance in astronomical units.
    """
    km = float(km) if np.isscalar(km) else np.asarray(km, dtype=float)
    return km/(const.AU*1e-3)


def kg_to_m(kg):
    """Converts a given mass from kilograms to meters.

    Parameters
    ----------
    kg : float or array_like
        A mass in kilograms.

    Returns
    -------
    float
        The corresponding mass in meters.
    """
    kg = float(kg) if np.isscalar(kg) else np.asarray(kg, dtype=float)
    return kg*(const.G/const.c**2)


def m_to_kg(m):
    """Converts a given mass from meters to kilograms.

    Parameters
    ----------
    m : float or array_like
        A mass in meters.

    Returns
    -------
    float
        The corresponding mass in kilograms.
    """
    m = float(m) if np.isscalar(m) else np.asarray(m, dtype=float)
    return m/(const.G/const.c**2)


def AU_pr_yr_to_m_pr_s(AU_pr_yr):
    """Converts a given speed from astronomical units per year to meters per second.

    Parameters
    ----------
    AU_pr_yr : float or array_like
        A speed in astronomical units per year.

    Returns
    -------
    float
        The corresponding speed in meters per second.
    """
    AU_pr_yr = float(AU_pr_yr) if np.isscalar(AU_pr_yr) else np.asarray(AU_pr_yr, dtype=float)
    return AU_pr_yr*(const.AU/const.yr)


def m_pr_s_to_AU_pr_yr(m_pr_s):
    """Converts a given speed from meters per second to astronomical units per year.

    Parameters
    ----------
    m_pr_s : float or array_like
        A speed in meters per second.

    Returns
    -------
    float
        The corresponding speed in astronomical units per year.
    """
    m_pr_s = float(m_pr_s) if np.isscalar(m_pr_s) else np.asarray(m_pr_s, dtype=float)
    return m_pr_s/(const.AU/const.yr)


def rad_to_deg(rad):
    """Converts a given angle from radians to degrees.

    Parameters
    ----------
    rad : float or array_like
        An angle in radians.

    Returns
    -------
    float
        The corresponding angle in degrees.
    """
    rad = float(rad) if np.isscalar(rad) else np.asarray(rad, dtype=float)
    return rad*(180/const.pi)


def deg_to_rad(deg):
    """Converts a given angle from degrees to radians.

    Parameters
    ----------
    deg : float or array_like
        An angle in degrees.

    Returns
    -------
    float
        The corresponding angle in radians.
    """
    deg = float(deg) if np.isscalar(deg) else np.asarray(deg, dtype=float)
    return deg*(const.pi/180)


def _convert_temperature_to_RGB(temperature):
    """Converts a temperature to an RGB-tripple.

    Algorithm shamelessly stolen from:
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/

    Parameters
    ----------
    temperature : float
        Input temperature in kelvin.

    Returns
    -------
    list of floats
        List of length 3 with the red, green and blue color components.
    """
    temp = temperature/100.0

    # Calculate the red value.
    if temp <= 66:
        red = 255
    else:
        red = temp - 60
        red = 329.698727446*red**(-0.1332047592)

    # Calculate the green value.
    if temp <= 66:
        green = temp
        green =  99.4708025861*np.log(green) - 161.1195681661
    else:
        green = temp - 60
        green = 288.1221695283*green**(-0.0755148492)

    # Calculate the blue value.
    if temp >= 66:
        blue = 255
    else:
        if temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231*np.log(blue) - 305.0447927307

    rgb = [red, green, blue]
    for i, c in enumerate(rgb):
        rgb[i] = max(0.0, min(255.0, c))

    return rgb


def _convert_relative_speed_to_doppler_shift(reference_wavelength, relative_speed):
    """Computes the Doppler shift of a spectral line corresponding to a given relative speed.

    Parameters
    ----------
    reference_wavelength : float
        Wavelength of the spectral line center in nanometers.
    relative_speed : float
        Input relative speed in meters per second.

    Returns
    -------
    float
        The Doppler shift in nanometers.
    """
    return relative_speed*reference_wavelength/const.c
