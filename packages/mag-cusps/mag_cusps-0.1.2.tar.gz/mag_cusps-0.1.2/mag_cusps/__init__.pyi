"""
MagCUSPS
-----------------------

.. currentmodule:: mag_cusps
    
    preprocess
    get_bowshock_radius
    get_bowshock
    get_interest_points
    process_interest_points
    process_points
    Shue97
    Liu12
    Rolland25
    fit_to_Shue97
    fit_to_Liu12
    fit_to_Rolland25
"""

# __init__.pyi for topology_analysis

from typing import Optional
import numpy as np
from numpy.typing import NDArray

def preprocess(
    mat: NDArray[np.float64],
    X: NDArray[np.float64],
    Y: NDArray[np.float64],
    Z: NDArray[np.float64],
    new_shape: NDArray[np.int32],
) -> NDArray[np.float64]:
    """
    Transform a matrix from a non uniform grid to a uniform grid, of shape `new_shape`,
    using X, Y and Z containing the actual position of the center of each grid of each matrix indices. 

    Parameters
    ----------
    mat : np.ndarray
        Input matrix array of doubles, shape (x, y, z, i).
    X, Y, Z : np.ndarray
        Input matrices used in orthonormalisation.
    new_shape : np.ndarray
        Integer array of shape (4,) specifying new shape dimensions.

    Returns
    -------
    np.ndarray
        Orthonormalised matrix as a NumPy array with shape matching `new_shape`.
    """



def get_bowshock_radius(
    theta: float,
    phi: float,
    Rho: NDArray[np.float64],
    earth_pos: NDArray[np.float64],
    dr: float
) -> float:
    """
    Calculate bowshock radius given angles and input data.

    Parameters
    ----------
    theta : float
        Polar angle in radians.
    phi : float
        Azimuthal angle in radians.
    Rho : np.ndarray
        Density matrix array.
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    dr : float
        Step size for radius calculation.

    Returns
    -------
    float
        Computed bowshock radius.
    """

def get_bowshock(
    Rho: NDArray[np.float64],
    earth_pos: NDArray[np.float64],
    dr: float,
    nb_phi: int,
    max_nb_theta: int
) -> NDArray[np.float64]:
    """
    Find the bow shock by finding the radius at which dRho_dr * r**3 is minimum,
    casting rays from the earth_pos at angles (theta, phi)

    Parameters
    ----------
    Rho : np.ndarray
        Density matrix array of shape (x,y,z,).
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    dr : float
        Step size for radius calculation.
    nb_phi : int
        Number of divisions in phi.
    max_nb_theta : int
        Maximum number of divisions in theta.

    Returns
    -------
    np.ndarray
        Array of points with shape (N, 3) representing bowshock coordinates.
    """


def get_interest_points(
    J_norm: NDArray[np.float64],
    earth_pos: NDArray[np.float64],
    Rho: NDArray[np.float64],
    theta_min: float,
    theta_max: float,
    nb_theta: int,
    nb_phi: int,
    dx: float,
    dr: float,
    alpha_0_min: float,
    alpha_0_max: float,
    nb_alpha_0: int,
    r_0_mult_min: float,
    r_0_mult_max: float,
    nb_r_0: int,
    avg_std_dev: Optional[float] = ...
) -> NDArray[np.float64]:
    """
    Calculate interest points from inputs.

    Parameters
    ----------
    J_norm : np.ndarray
        Normalized current density matrix of shape (x,y,z,i,).
    earth_pos : np.ndarray
        Earth position vector of shape (3,).
    Rho : np.ndarray
        Density matrix array of shape (x,y,z,).
    theta_min, theta_max : float
        Angle bounds for theta.
    nb_theta, nb_phi : int
        Number of divisions for theta and phi.
    dx, dr : float
        Step sizes.
    alpha_0_min, alpha_0_max : float
        Bounds for alpha_0.
    nb_alpha_0 : int
        Number of alpha_0 divisions.
    r_0_mult_min, r_0_mult_max : float
        Multiplicative range for r_0 where r_0 = r_0_mult * r_I with r_I the inner radius in the simulation.
    nb_r_0 : int
        Number of r_0 divisions.
    avg_std_dev : Optional[float]
        Optional output parameter for average standard deviation.

    Returns
    -------
    np.ndarray
        Interest points array with shape (nb_theta*nb_phi, 4).
    """

def process_interest_points(
    interest_points: NDArray[np.float64],
    nb_theta: int,
    nb_phi: int,
    shape_sim: NDArray[np.int32],
    shape_real: NDArray[np.int32],
    earth_pos_sim: NDArray[np.float64],
    earth_pos_real: NDArray[np.float64],
) -> NDArray[np.float64]:
    """
    Transform interest points from simulation coordinates to real coordinates.

    Parameters
    ----------
    interest_points : np.ndarray
        Interest points array with shape (N, 4).
    nb_theta, nb_phi : int
        Number of divisions in theta and phi.
    shape_sim, shape_real : np.ndarray
        Shape arrays of shape (4,) describing simulation and real data shapes.
    earth_pos_sim, earth_pos_real : np.ndarray
        Earth position vectors of shape (3,) for simulation and real.

    Returns
    -------
    np.ndarray
        Processed interest points array of shape (N, 4).
    """

def process_points(
    points: NDArray[np.float64],
    shape_sim: NDArray[np.int32],
    shape_real: NDArray[np.int32],
    earth_pos_sim: NDArray[np.float64],
    earth_pos_real: NDArray[np.float64],
) -> NDArray[np.float64]:
    """
    Transform points from simulation coordinates to real coordinates.

    Parameters
    ----------
    points : np.ndarray
        Points array with shape (N, 3).
    shape_sim, shape_real : np.ndarray
        Shape arrays of shape (4,) describing simulation and real data shapes.
    earth_pos_sim, earth_pos_real : np.ndarray
        Earth position vectors of shape (3,) for simulation and real.

    Returns
    -------
    np.ndarray
        Processed points array of shape (N, 3).
    """



def Shue97(
    params: NDArray[np.float64],
    theta: float
) -> float:
    """
    Analytical approximation of the Magnetopause topology as written by Shue in his 1997 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (2,).
    theta : float
        Angle at which the radius should be calculated. 
    
    Returns
    -------
    float
        Radius at this angle.
    """
    
def Liu12(
    params: NDArray[np.float64],
    theta: float, phi: float
) -> float:
    """
    Analytical approximation of the Magnetopause topology as written by Liu in his 2012 paper.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (10,).
    theta, phi : float
        Angle at which the radius should be calculated. 
    
    Returns
    -------
    float
        Radius at this angle.
    """
    
def Rolland25(
    params: NDArray[np.float64],
    theta: float, phi: float
) -> float:
    """
    Analytical approximation of the Magnetopause topology as written by Rolland in his 2025 thesis.

    Parameters
    ----------
    params : np.ndarray
        Parameters array with shape (11,).
    theta, phi : float
        Angle at which the radius should be calculated. 
    
    Returns
    -------
    float
        Radius at this angle.
    """


def fit_to_Shue97(
    interest_points: NDArray[np.float64],
    nb_interest_points: int,
    initial_params: NDArray[np.float64],
    lowerbound: NDArray[np.float64],
    upperbound: NDArray[np.float64],
    radii_of_variation: NDArray[np.float64],
    nb_runs: int = 10,
    max_nb_iterations_per_run: int = 50,
) -> tuple[NDArray[np.float64], float]:
    """
    Analytical fitting of the Shue97 function to an array of interest points.

    Parameters
    ----------
    interest_points : np.ndarray
        Interest point array to fit to of shape (`nb_interest_points`, 4).
    nb_interest_points : int
        Number of interest points to fit to.
    initial_parameters : np.ndarray
        Parameters array with shape (11,).
    lowerbound, upperbound : np.ndarray
        Parameters array with shape (11,) corresponding to the lower and upper bounds
        that the parameters can take during fitting.
    radii_of_variation : np.ndarray
        Parameters array with shape (11,) corresponding to the maximum distance each 
        of the parameters will randomly move away for the initial_params at the 
        beginning of a run.
    nb_runs : int
        Number of times the fitting algorithm will start again with other randomly 
        selected initial parameters.
    max_nb_iterations_per_run : int
        Maximum number of iterations the fitting algorithm will do before stopping
        even if it hasn't converged.
    
    Returns
    -------
    float
        Array of the final parameters after fit and the fitting cost of these parameters. 
    """

def fit_to_Liu12(
    interest_points: NDArray[np.float64],
    nb_interest_points: int,
    initial_params: NDArray[np.float64],
    lowerbound: NDArray[np.float64],
    upperbound: NDArray[np.float64],
    radii_of_variation: NDArray[np.float64],
    nb_runs: int = 10,
    max_nb_iterations_per_run: int = 50,
) -> tuple[NDArray[np.float64], float]:
    """
    Analytical fitting of the Liu12 function to an array of interest points.

    Parameters
    ----------
    interest_points : np.ndarray
        Interest point array to fit to of shape (`nb_interest_points`, 4).
    nb_interest_points : int
        Number of interest points to fit to.
    initial_parameters : np.ndarray
        Parameters array with shape (11,).
    lowerbound, upperbound : np.ndarray
        Parameters array with shape (11,) corresponding to the lower and upper bounds
        that the parameters can take during fitting.
    radii_of_variation : np.ndarray
        Parameters array with shape (11,) corresponding to the maximum distance each 
        of the parameters will randomly move away for the initial_params at the 
        beginning of a run.
    nb_runs : int
        Number of times the fitting algorithm will start again with other randomly 
        selected initial parameters.
    max_nb_iterations_per_run : int
        Maximum number of iterations the fitting algorithm will do before stopping
        even if it hasn't converged.
    
    Returns
    -------
    float
        Array of the final parameters after fit and the fitting cost of these parameters. 
    """

def fit_to_Rolland25(
    interest_points: NDArray[np.float64],
    nb_interest_points: int,
    initial_params: NDArray[np.float64],
    lowerbound: NDArray[np.float64],
    upperbound: NDArray[np.float64],
    radii_of_variation: NDArray[np.float64],
    nb_runs: int = 10,
    max_nb_iterations_per_run: int = 50,
) -> tuple[NDArray[np.float64], float]:
    """
    Analytical fitting of the Rolland25 function to an array of interest points.

    Parameters
    ----------
    interest_points : np.ndarray
        Interest point array to fit to of shape (`nb_interest_points`, 4).
    nb_interest_points : int
        Number of interest points to fit to.
    initial_parameters : np.ndarray
        Parameters array with shape (11,).
    lowerbound, upperbound : np.ndarray
        Parameters array with shape (11,) corresponding to the lower and upper bounds
        that the parameters can take during fitting.
    radii_of_variation : np.ndarray
        Parameters array with shape (11,) corresponding to the maximum distance each 
        of the parameters will randomly move away for the initial_params at the 
        beginning of a run.
    nb_runs : int
        Number of times the fitting algorithm will start again with other randomly 
        selected initial parameters.
    max_nb_iterations_per_run : int
        Maximum number of iterations the fitting algorithm will do before stopping
        even if it hasn't converged.
    
    Returns
    -------
    float
        Array of the final parameters after fit and the fitting cost of these parameters. 
    """



__all__ = [
    "preprocess",
    "get_bowshock_radius",
    "get_bowshock",
    "get_interest_points",
    "process_interest_points",
    "process_points",
    "Shue97",
    "Liu12",
    "Rolland25",
    "fit_to_Shue97",
    "fit_to_Liu12",
    "fit_to_Rolland25",
]
