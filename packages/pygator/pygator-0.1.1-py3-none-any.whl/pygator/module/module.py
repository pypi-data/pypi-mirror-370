import numpy as np 
import pandas as pd
import math
import matplotlib.pyplot as plt
from scipy import integrate
from scipy.special import hermite




def waist_size_mismatch_calculator(q1,q2):
    """A function to calculate the waist size mismatch between two q-parameters 
    calculated as gamma=zR1-zR2/2*zR1
    zR1: Rayleigh range of the first q-parameter
    zR2: Rayleigh range of the second q-parameter, to which q1 is measured to"""
    gamma=(np.imag(q1)-np.imag(q2))/(2*np.imag(q1))
    return gamma

def waist_location_mismatch_calculator(q1,q2):
    """A function to calculate the waist size mismatch between two q-parameters 
    calculated as beta=z1-z2/2*zR1
    zR1: Rayleigh range of the first q-parameter
    zR2: Rayleigh range of the second q-parameter, to which q1 is measured to"""
    beta=(np.real(q1)-np.real(q2))/(2*np.imag(q1))
    return beta


#Define some constants

wavelength=1064e-9 #m

import numpy as np

def diagonalize_qpd(QPD1_lateral, QPD2_lateral, QPD1_tilt, QPD2_tilt):
    # Define matrix A
    A = np.array([[QPD1_lateral, QPD2_lateral],
                  [QPD1_tilt, QPD2_tilt]])
    
    # Compute eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(A)
    
    # Extract transformation coefficients
    a, b = eigenvectors[:, 0]  # First eigenvector
    c, d = eigenvectors[:, 1]  # Second eigenvector
    
    # Print results
    print("Diagonalized Matrix (Eigenvalues):")
    print(np.diag(eigenvalues))
    print("\nTransformation Coefficients:")
    print(f"QPD1 = {a:.4f} * QPD1_lateral + {b:.4f} * QPD2_lateral")
    print(f"QPD2 = {c:.4f} * QPD1_tilt + {d:.4f} * QPD2_tilt")
    
    return eigenvalues, eigenvectors



import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf, erfc
from sympy import Symbol
# Define symbolic variables
x, y, a, w1,zR,w01,w02,w0, w ,k, Rc, gouy,z,z1, z2 , R, A, delta_z,epsilon , E0, Omega, omega= sp.symbols('x y a w1 zR w01 w02 w0 w k Rc gouy z,z1 z2 R A delta_z epsilon E0 Omega omega', real=True, positive=True)


def HG_mode_sym(x, y, q, n, m):
    """
    Calculate symbolically the amplitude of the HG_nm mode at position (x, y) with beam waist radius w_z.
    
    Parameters:
        x (float): x-coordinate.
        y (float): y-coordinate.
        q (complex): Complex beam parameter.
        n (int): Mode index in the x-direction.
        m (int): Mode index in the y-direction.
        gouy (float): Gouy phase in degrees.
        
    Returns:
        dict: Dictionary containing the mode amplitude and other parameters like beam waist (w), Rayleigh range (zR), etc.
    """
    wavelength = 1064e-9
    w0 = sp.sqrt(sp.im(q) * wavelength / np.pi)
    zR = sp.im(q)
    if sp.re(q) == 0:
        Rc = sp.oo
    else:
        Rc = sp.re(q) + (zR ** 2 / sp.re(q))
    k = 2 * sp.pi / wavelength
    z = sp.re(q)
    w = w0 * sp.sqrt(1 + (z / zR) ** 2)

    normalization_factor = 1 / sp.sqrt((2 ** (n + m-1)) * sp.pi * sp.factorial(n) * sp.factorial(m))
    exponent = - (x ** 2 + y ** 2) / (w ** 2)
    hermite_x = sp.hermite(n, sp.sqrt(2) * x / w)
    hermite_y = sp.hermite(m, sp.sqrt(2) * y / w)
    wavefront = sp.exp(-1j * k * (x ** 2 + y ** 2) / (2 * Rc))
    Gouy_phase = sp.atan(z / zR)
    # gouy_phase = gouy_00 * np.pi / 180
    Gouy_term = sp.exp(-1j * (n + m + 1) * (Gouy_phase))
    # print("Gouy phase",Gouy_term )
    
    amplitude = (normalization_factor * hermite_x * hermite_y * sp.exp(exponent) * wavefront ) / w
    return {"U": amplitude, "w": w, "w0": w0, "zR": zR, "Rc": Rc, "Gouy": Gouy_phase, 'z': z}


def size_mismatch_scattering(x, y, q, n, m):
    # Compute A coefficients
    A_n = np.sqrt((n+2)*(n+1))
    A_m = np.sqrt((n+2)*(n+1))
    # print(A_n,A_m)
    # Compute B coefficients with safeguards
    B_n = np.sqrt(m*(m-1)) if m >= 2 else 0  # Set to 0 if n-2 < 0
    B_m = np.sqrt(m*(m-1)) if m >= 2 else 0  # Set to 0 if m-2 < 0

    # Start with the original mode
    size_mismatched_scattered_beam = HG_mode_sym(x, y,q, n, m)['U']

    # Add contributions only if indices are valid
    if n + 2 >= 0:
        size_mismatched_scattered_beam -= 1j * (epsilon / 2) * A_n * HG_mode_sym(x, y, q, n+2, m)['U']
    if n - 2 >= 0:
        size_mismatched_scattered_beam -= 1j * (epsilon / 2) * B_n * HG_mode_sym(x, y, q, n-2, m)['U']
    
    if m + 2 >= 0:
        size_mismatched_scattered_beam -= 1j * (epsilon / 2) * A_m * HG_mode_sym(x, y, q, n, m+2)['U']
    
    if m - 2 >= 0:
        size_mismatched_scattered_beam -= 1j * (epsilon / 2) * B_m * HG_mode_sym(x, y, q, n, m-2)['U']

    return size_mismatched_scattered_beam


# x_sym=sp.symbols('x_sym')
# y_sym=sp.symbols('y_sym')
def HG_mode_num(x, y, q, n, m, wavelength):
        """
    Calculate numerically the amplitude of the HG_nm mode at position (x, y) with beam waist radius w_z.
    
    Parameters:
        x (float): x-coordinate.
        y (float): y-coordinate.
        q (complex): Complex beam parameter.
        n (int): Mode index in the x-direction.
        m (int): Mode index in the y-direction.
        gouy (float): Gouy phase in degrees.
        
    Returns:
        dict: Dictionary containing the mode amplitude and other parameters like beam waist (w), Rayleigh range (zR), etc.
    """
    # Constants
    w0 = np.sqrt(1 * np.imag(q) * wavelength / np.pi)
    zR = np.imag(q)
    if np.real(q)==0:
        Rc = np.inf 
    else:
        Rc= (np.abs(q) ** 2) / np.real(q)
    k = 2 * np.pi / wavelength
    z = np.real(q)
    w = w0 * np.sqrt(1 + (z / zR) ** 2)

    # Hermite polynomials
    normalization_factor = 1 / np.sqrt(((2 ** (n + m - 1)) * np.pi * math.factorial(n) *math.factorial(m)))
    exponent = - (x ** 2 + y ** 2) / (w ** 2)
    hermite_x = np.polynomial.hermite.hermval(np.sqrt(2) * x / w, [0]*n + [1])
    hermite_y = np.polynomial.hermite.hermval(np.sqrt(2) * y / w, [0]*m + [1])
    
    # Wavefront
    wavefront = np.exp(-1j * k * (x ** 2 + y ** 2) / (2 * Rc))
    
    # Gouy phase
    Gouy_phase = np.arctan(z / zR)
    # gouy_phase = gouy * np.pi / 180
    Gouy_term = np.exp(1j * (n + m + 1) * Gouy_phase)
    
    # Amplitude
    amplitude = (normalization_factor * hermite_x * hermite_y * np.exp(exponent) * wavefront * Gouy_term) / w
    
    return {"U": amplitude, "w": w, "w0": w0, "zR": zR, "Rc": Rc, "Gouy": Gouy_phase_z, 'z': z}


def mismatch_calculator(q1,q2,percentage=True):
    """Calculate the power mismatch between two q-parameters"""
    MM=(np.abs(q1 -q2))**2/(np.abs(q1-np.conjugate(q2)))**2
    if percentage==True:
        return 100*MM
    else:
        return MM



def split_integral(x,y,x_split,y_split,signal,phase,gap_size=2e-5,plot=False):
    """A function that numerically calculates the integral in 4 regions (4 QPD quandrants for example)
    This started as calculating a signal on a QPD. 
    x,y are the spatial axes
    x_split: is the integral limit in x-direction
    y_split: is the integral limit in y-direction
    signal: is the signal to be integrated
    phase: Demodulation phase
    gap_size: realistic gap size between the quadrants of the QPD. Default to 4e-5 (from -2e-5 to 2e-5)

    returns

    x_motion: the signal Left - Right in the x-direction 
    y_motion: the signal Up - Bottom in the y-direction 

    Optional: 
    Plot the signal. Default to No
    """
    # Define regions for integrals
    # x_split = 0  # Example split point for x
    # y_split = 0  # Example split point for y
    dx=(x[1]-x[0])
    dy=(y[1]-y[0])
    X, Y = np.meshgrid(x, y)

    mask1 = (X <= x_split-gap_size) & (Y <= y_split-gap_size)
    mask2 = (X > x_split+gap_size) & (Y <= y_split-gap_size)
    mask3 = (X <= x_split-gap_size) & (Y > y_split+gap_size)
    mask4 = (X > x_split+gap_size) & (Y > y_split+gap_size)

    # Now calculate the integrals
    integral1 = np.sum(signal[mask1]) * dx * dy
    integral2 = np.sum(signal[mask2]) * dx * dy
    integral3 = np.sum(signal[mask3]) * dx * dy
    integral4 = np.sum(signal[mask4]) * dx * dy

    # print(integral1,integral2,integral3,integral4)
    # Calculate QPD2 signals
    phi = phase * np.pi / 180

    x_motion =-np.real(( -integral1 - integral2 + (integral3 + integral4))/2)
    y_motion =-np.real( -(integral3 - integral4 + integral1 - integral2)/2)

    # Optionally plot np.abs(RF)**2 and the gap size
    if plot and -1e-8< x_split <1e-8:
        plt.figure(figsize=(6, 6))
        
        # Plot the intensity of RF^2
        plt.imshow(np.abs(signal), extent=[x.min(), x.max(), y.min(), y.max()], origin='lower', cmap='jet')
        
        # Mark the split regions with a gap size
        plt.axvline(x=x_split - gap_size, color='red', linestyle='--', label=f'x_split - gap_size: {x_split - gap_size}')
        plt.axvline(x=x_split + gap_size, color='red', linestyle='--', label=f'x_split + gap_size: {x_split + gap_size}')
        plt.axhline(y=y_split - gap_size, color='blue', linestyle='--', label=f'y_split - gap_size: {y_split - gap_size}')
        plt.axhline(y=y_split + gap_size, color='blue', linestyle='--', label=f'y_split + gap_size: {y_split + gap_size}')

        # Add labels for the integral regions
        # Choose approximate centers of the regions to place the labels
        label_x_offset = 0.15 * (x.max() - x.min())
        label_y_offset = 0.15 * (y.max() - y.min())

        plt.text(x_split - label_x_offset, y_split - label_y_offset, "Region 1", color='red', fontsize=12, ha='center', va='center')
        plt.text(x_split + label_x_offset, y_split - label_y_offset, "Region 2", color='blue', fontsize=12, ha='center', va='center')
        plt.text(x_split - label_x_offset, y_split + label_y_offset, "Region 3", color='green', fontsize=12, ha='center', va='center')
        plt.text(x_split + label_x_offset, y_split + label_y_offset, "Region 4", color='purple', fontsize=12, ha='center', va='center')

        plt.colorbar(label="Intensity")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Intensity Plot of np.abs(RF)**2 with Gap Size and Splits")
        plt.legend()
        plt.show()

    return x_motion*np.cos(phi),y_motion*np.cos(phi)


import scipy
def calculate_rms(f,data,name):
    rms=scipy.integrate.cumulative_trapezoid(np.flip(data),f, initial=0)
    rms=np.flip(rms)
    # ax.semilogy(rms, '--',color='lime', label=rf"RMS",linewidth=2)
    return rms


def func_shot_noise(P):
    """A function to calculate the shot noise given some DC power"""
    c=299792458 #m/s
    # P=1.5e-3 #W
    wavelength=1064e-9 #m
    nu=c/wavelength
    h=6.626e-34 # J/Hz.
    #then the energy of each photon is 
    E=h*nu
    print('The energy of each photon is ', E, "J")
    #the number of photons on the PD is 
    N=P/E
    print("The number of photons is ", N, "photons/second")

    #The statistical error of counting the number of photon is sqrt(N)

    err_N=np.sqrt(N)
    print("The error in N is ", err_N, "sqrt(Hz)")

    #then shot noise is

    shot_noise=err_N*E

    print("The shot noise on the PD is ", shot_noise, "W/sqrt(Hz)")
    return shot_noise



def make_thermal_lens(self, model):
        thermal_opts = self.options.thermal
        rpts = thermal_opts.rpts
        s_max = thermal_opts.s_max
        r_tm = thermal_opts.r_tm
        r_ap = thermal_opts.r_ap
        h_tm = thermal_opts.h_tm
        r_m = np.linspace(0, r_tm, rpts)
        x, y, x_msh, y_msh, r_msh = maps.make_coordinates(rpts, r_tm)

        f0 = model.ITMYlens.f
        Rc0_i = model.ITMY.Rc
        Rc0_e = model.ETMY.Rc
        if thermal_opts.ITM_df_m:
            model.ITMYlens.f = 1 / (1 / f0 + 1 / thermal_opts.ITM_df_m)
        if thermal_opts.HR_dRc_m:
            model.ITMY.Rc = 1 / (1 / Rc0_i + 1 / thermal_opts.HR_dRc_m)
            model.ETMY.Rc = 1 / (1 / Rc0_e + 1 / thermal_opts.HR_dRc_m)
        model.beam_trace()
        w_m = model.ITMY.p1.o.qx.w

        do_interpolation = True
        if thermal_opts.custom_map_path:
            print("using custom maps")
            thermal_data = np.load(thermal_opts.custom_map_path)
            Z_coat_W = thermal_data["itm_tl"] + thermal_data["cp_tl"]
            Uz_itm_W = thermal_data["itm_td"]
            try:
                Uz_etm_W = thermal_data["etm_td"]
            except KeyError:
                Uz_etm_W = Uz_itm_W
            x, y = thermal_data["x"], thermal_data["y"]
            do_interpolation = False

        elif thermal_opts.hom_order is None:
            Z_coat_W, _ = hv.thermal_lenses_HG00(
                r_m, r_tm, h_tm, w_m, FusedSilica, s_max=s_max,
            )
            Uz_itm_W = hv.surface_deformation_coating_heating_HG00(
                r_m, r_tm, h_tm, w_m, FusedSilica, s_max=s_max,
            )
            Uz_etm_W = Uz_itm_W

        else:
            from scipy.special import eval_hermite
            hom_order = thermal_opts.hom_order
            rat = r_m / w_m
            I = (eval_hermite(hom_order, np.sqrt(2) * rat) * np.exp(-rat**2))**2
            I_data = hv.get_p_n_s_numerical(
                I, r_tm, s_max=s_max, material=FusedSilica,
            )
            I_fit = hv.eval_p_n_s_numerical(I_data)
            Z_coat_W, _ = hv.thermal_lenses(I_data, h_tm)
            Uz_itm_W = hv.surface_deformation_coating_heating(I_data, h_tm)
            Uz_etm_W = Uz_itm_W

        if thermal_opts.include_apertures:
            print("apertures", r_ap)
            aperture = maps.circular_aperture(x, y, r_ap)
        else:
            aperture = None
        if thermal_opts.include_lens_opd:
            print("adding lens OPD")
            opd = Z_coat_W * thermal_opts.Pabs_coat
            if do_interpolation:
                opd_msh = np.interp(r_msh, r_m, opd)
            else:
                opd_msh = opd
            opd_map = Map(x, y, amplitude=aperture, opd=opd_msh)
            opd_curvature_D = np.array(opd_map.remove_curvatures(w_m))
            if thermal_opts.remove_piston:
                opd_map.remove_piston(w_m)
            opd_map.opd[:] *= (1 - thermal_opts.opd_correction)
            model.ITMYlens.OPD_map = opd_map
            if thermal_opts.include_curvatures:
                print("adding OPD curvature", opd_curvature_D)
                f0_m = model.ITMYlens.f
                model.ITMYlens.f = 1 / (1 / f0_m + 2 * np.average(opd_curvature_D))

        include_srf = thermal_opts.include_itm_srf or thermal_opts.include_etm_srf
        if include_srf:
            print("adding surface distortions")

            def add_surface_map(component, Uz_W):
                srf = Uz_W * thermal_opts.Pabs_coat
                if do_interpolation:
                    srf_msh = np.interp(r_msh, r_m, srf)
                else:
                    srf_msh = srf
                srf_map = Map(x, y, amplitude=aperture, opd=srf_msh)
                srf_curvature_D = np.array(srf_map.remove_curvatures(w_m))
                if thermal_opts.remove_piston:
                    srf_map.remove_piston(w_m)
                srf_map.opd[:] *= (1 - thermal_opts.srf_correction)
                component.surface_map = srf_map
                if thermal_opts.include_curvatures:
                    print("adding surface curvature", srf_curvature_D)
                    Rc0_m = component.Rc
                    component.Rc = 1 / (1 / Rc0_m - 2 * srf_curvature_D)

            if thermal_opts.include_itm_srf:
                add_surface_map(model.ITMY, Uz_itm_W)
            if thermal_opts.include_etm_srf:
                add_surface_map(model.ETMY, Uz_etm_W)

        if thermal_opts.include_sec_apertures:
            sec_aperture = maps.circular_aperture(x, y, thermal_opts.r_sec_ap)
            sec_srf_map = Map(x, y, amplitude=sec_aperture, opd=None)
            model.BS.surface_map = sec_srf_map


import numpy as np
from scipy.optimize import curve_fit

def fit_QPD_slope_gamma(MM_values, QPD1y_slope):
    """
    Fit the model y = a * x^2 / (x + 1)^2 to the given data.

    Parameters:
    - MM_values: array-like, independent variable (e.g., mode-matching values)
    - QPD1y_slope: array-like, dependent variable (e.g., slope values)

    Returns:
    - fitted_values: array of model predictions using the optimal fit
    - popt: optimal parameters found (for diagnostics)
    """
    # Define the model
    def model(x, a):
        return a * x**2 / (x + 1)**2

    # Fit the model to data
    popt, _ = curve_fit(model, QPD1y_slope, MM_values)

    # Return fitted values using the model
    fitted_values = model(QPD1y_slope, *popt)
    return fitted_values, popt




#there is 1.54 mW incident on each QPDs
def process_RF_data(file_path):
    QPD1 = []
    QPD2 = []

    RFJ_I = []
    RFJ_Q = []

    # Read the Excel file
    df = pd.read_csv(file_path)
    # df = pd.read_excel(file_path)

    # Get the number of columns
    num_columns = len(df.columns)

    # Name each column
    num_columns_to_name = min(8, len(df.columns))
    df.columns = ['A1', 'B1', 'C1', 'D1', 
                      'A2', 'B2', 'C2', 'D2','I','Q','time','MM']

    # Perform the specified calculation
    QPD1_raw_data= df["A1"] + df['D1'] - df["C1"] - df["B1"]
    QPD2_raw_data= df["A2"] + df['D2'] - df["C2"] - df["B2"]
    I=df['I']
    Q=df['Q']


    vertical_QPD1=df["A1"] + df['B1']- df["C1"] - df["D1"]
    vertical_QPD2=df["A2"] + df['B2']- df["C2"] - df["D2"]

    # print(vertical_QPD1,vertical_QPD2)

    # Save the constant values in lists
    QPD1.append(np.mean(QPD1_raw_data))
    QPD2.append(np.mean(QPD2_raw_data))
    RFJ_I.append(np.mean(I))
    RFJ_Q.append(np.mean(Q))

    return QPD1, QPD2, RFJ_I, RFJ_Q, np.std(QPD1_raw_data), np.std(QPD2_raw_data), np.std(I), np.std(Q)


def process_DC_data(file_path):
    QPD1 = []
    QPD2 = []

    RFJ_I = []
    RFJ_Q = []

    # Read the Excel file
    df = pd.read_csv(file_path)
    # df = pd.read_excel(file_path)

    # Get the number of columns
    num_columns = len(df.columns)

    # Name each column
    num_columns_to_name = min(8, len(df.columns))
    df.columns = ['A1', 'B1', 'C1', 'D1', 
                      'A2', 'B2', 'C2', 'D2','I','Q']

    # Perform the specified calculation
    total_power_QPD1= np.mean(df["A1"]) + np.mean(df['D1']) + np.mean(df["C1"]) + np.mean(df["B1"])
    total_power_QPD2= np.mean(df["A2"]) + np.mean(df['D2']) + np.mean(df["C2"]) + np.mean(df["B2"])

    QPD1_data=df["A1"] + df['D1']- df["C1"]- df["B1"]
    QPD2_data=df["A2"] + df['D2']- df["C2"]- df["B2"]

    I=df['I']
    Q=df['Q']

    vertical_QPD1=np.mean(np.mean(df["A1"]) + np.mean(df['B1']) + np.mean(df["C1"]) + np.mean(df["D1"]))
    vertical_QPD2=np.mean(np.mean(df["A2"]) + np.mean(df['B2']) + np.mean(df["C2"]) + np.mean(df["D2"]))
    
    x1_axis=np.mean(df["A1"] + df['D1']-( df["C1"] + df["B1"]))/total_power_QPD1
    y1_axis=np.mean(df["A1"] - df['D1']- df["C1"] + df["B1"])/total_power_QPD1

    x2_axis=np.mean(df["A2"] + df['D2']-( df["C2"] + df["B2"]))/total_power_QPD2
    y2_axis=np.mean(df["A2"] - df['D2']- df["C2"] + df["B2"])/total_power_QPD2

    # print(vertical_QPD1,vertical_QPD2)

    # Save the constant values in lists
    QPD1.append(np.mean(QPD1_data))
    QPD2.append(np.mean(QPD2_data))
    RFJ_I.append(np.mean(I))
    RFJ_Q.append(np.mean(Q))

    return QPD1, QPD2, RFJ_I, RFJ_Q,x1_axis,y1_axis,x2_axis,y2_axis,np.std(QPD1_data), np.std(QPD2_data), np.std(I), np.std(Q)



# uf_optics/module/module.py
import subprocess
import sys
from pathlib import Path

def add_git_repo_to_path():
    """Add the top-level Git repository to sys.path if available."""
    try:
        repo_path = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            stderr=subprocess.DEVNULL
        ).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        # Not in a Git repo
        return
    
    sys.path.append(str(Path(repo_path)))


def fit_beam_profile_curve_fit(zx_data, wx_data, zy_data, wy_data, w0guess, z0guess, zRguess, wx_std, wy_std, z_std, show_plot=1, plotpts=1000, title='Beam scan fit', saveplot=False, filename='beamfit.pdf',print_results=True):
    """
    Fits beam radius data to the Gaussian propagation function using curve_fit, with zR as a free parameter, including standard deviations.
    """

    def zw0z02w_zR_free(z, w0, z0, zR):
        w = w0 * np.sqrt(1 + ((z - z0) / zR)**2)
        return w

    try:
        popt_x, pcov_x = curve_fit(zw0z02w_zR_free, zx_data, wx_data, p0=[w0guess, z0guess, zRguess], sigma=wx_std, absolute_sigma=False,bounds=([0, -np.inf, 0], [np.inf, np.inf, np.inf]))
        w0out_x, z0out_x, zRout_x = popt_x
        w0out_x_err, z0out_x_err, zRout_x_err = np.sqrt(np.diag(pcov_x))

        popt_y, pcov_y = curve_fit(zw0z02w_zR_free, zy_data, wy_data, p0=[w0guess, z0guess, zRguess], sigma=wy_std, absolute_sigma=False,bounds=([0, -np.inf, 0], [np.inf, np.inf, np.inf]))
        w0out_y, z0out_y, zRout_y = popt_y
        w0out_y_err, z0out_y_err, zRout_y_err = np.sqrt(np.diag(pcov_y))

    except (RuntimeError, ValueError) as e:
        print(f"Fit failed: {e}")
        return None, None


    if show_plot == 1:
        z_min = min(np.min(zx_data), np.min(zy_data))
        z_max = max(np.max(zx_data), np.max(zy_data))
        z_span = z_max - z_min
        z_extrapolate_min = z_min - 1.3 * z_span
        z_extrapolate_max = z_max + 1.3 * z_span

        z_fit = np.linspace(z_extrapolate_min, z_extrapolate_max, plotpts)
        w_fit_x = zw0z02w_zR_free(z_fit, w0out_x, z0out_x, zRout_x)
        w_fit_y = zw0z02w_zR_free(z_fit, w0out_y, z0out_y, zRout_y)

        plt.figure(figsize=(5.5, 4))
        plt.errorbar(zx_data, wx_data * 1e6, xerr=z_std, yerr=wx_std * 1e6, fmt='o', color='blue', label='Data X')
        plt.plot(z_fit, w_fit_x * 1e6, color='blue', label='Fit X')
        plt.errorbar(zy_data, wy_data * 1e6, xerr=z_std, yerr=wy_std * 1e6, fmt='o', color='green', label='Data Y')
        plt.plot(z_fit, w_fit_y * 1e6, color='green', label='Fit Y')
        plt.tight_layout()
        plt.xlabel('Position [m]')
        plt.ylabel('Beam size [$\\mu$m]')
        plt.xlim((z_extrapolate_min, z_extrapolate_max))
        plt.legend(loc='best')
        plt.title(title)
        plt.grid(True)

        if saveplot:
            plt.savefig(filename)
        plt.show()
    sol_x=(w0out_x, z0out_x, zRout_x, w0out_x_err, z0out_x_err, zRout_x_err)
    sol_y=(w0out_y, z0out_y, zRout_y, w0out_y_err, z0out_y_err, zRout_y_err)

    if print_results:
        # Print the results with errors
        print(f"Waist size for x data: {sol_x[0]:.2e} ± {sol_x[2]:.2e} m")
        print(f"Waist location for x data: {sol_x[1]:.2e} ({sol_x[1]/0.0254:.2e} inches)± {sol_x[3]:.2e} m")
        print(f"Waist size for y data: {sol_y[0]:.2e} ± {sol_y[2]:.2e} m")
        print(f"Waist location for y data: {sol_y[1]:.2e} ({sol_y[1]/0.0254:.2e} inches)± {sol_y[3]:.2e} m")
        print(f"Rayleigh range is {np.pi*sol_x[0]**2/1064e-9:.2e} m ({(np.pi*sol_x[0]**2/1064e-9)/0.0254:.2e} inches) ")
        print(f"Rayleigh range beam size is {np.sqrt(2)*sol_x[0]:.2e}")

    return sol_x, sol_y

import numpy as np
import matplotlib.pyplot as plt
from scipy.odr import Model, RealData, ODR

def fit_beam_profile_ODR(
    zx_data, wx_data, zy_data, wy_data,
    w0guess, z0guess, zRguess,
    wx_std, wy_std, z_std,
    show_plot=1, plotpts=1000,
    title='Beam scan fit',
    saveplot=False, filename='beamfit.pdf',
    print_results=True,
    weight_mode='measured+relative',   # 'measured' | 'measured+relative' | 'measured+distance'
    frac_err=0.05,                     # dimensionless; used by +relative/+distance
    sigma_floor=0.0,                   # optional extra floor (meters)
    iters=2,                           # reweighting passes
    p=1.0,                             # exponent for distance mode
    plot_error='measured'              # 'measured' | 'fit'
):
    """
    Fit Gaussian beam radii with ODR using measured uncertainties, with optional
    extra heteroscedastic weighting near the waist.

    weight_mode:
      - 'measured': use wx_std/wy_std only.
      - 'measured+relative': sy_fit^2 = sy_meas^2 + (frac_err * w(z))^2
      - 'measured+distance': sy_fit^2 = sy_meas^2 + (frac_err * w_scale * (1 + |z-z0|/zR)^p)^2

    plot_error:
      - 'measured': plot error bars from your measured σ only.
      - 'fit': plot the σ actually used by the last ODR pass.
    """

    def as_array(val, like):
        """Broadcast scalar or array 'val' to array shaped like 'like'."""
        if np.ndim(val) == 0:
            return np.full_like(like, val, dtype=float)
        return np.asarray(val, dtype=float)

    # Gaussian beam model
    def w_of_z(beta, z):
        w0, z0, zR = beta
        return w0 * np.sqrt(1 + ((z - z0)/zR)**2)

    def run_fit(z, w, sx, sy, beta0):
        model = Model(w_of_z)
        data = RealData(z, w, sx=sx, sy=sy)
        odr = ODR(data, model, beta0=beta0)
        return odr.run()

    # Prepare z-uncertainties (allow scalar or array)
    sx_x = as_array(z_std, zx_data)
    sx_y = as_array(z_std, zy_data)
    # Measured σ arrays (absolute, meters)
    sy_x_meas = as_array(wx_std, zx_data)
    sy_y_meas = as_array(wy_std, zy_data)

    # Helper to build fit σ from measured σ and current params
    def build_sy_fit(z, w_meas, sy_meas, beta, mode):
        w_pred = w_of_z(beta, z)
        if mode == 'measured':
            sy = sy_meas
        elif mode == 'measured+relative':
            sy = np.sqrt(sy_meas**2 + (frac_err * w_pred)**2)
        elif mode == 'measured+distance':
            # Scale by a representative radius so units are meters
            w_scale = np.median(w_meas)
            z0, zR = beta[1], beta[2]
            dist = np.abs(z - z0) / np.abs(zR)
            sy = np.sqrt(sy_meas**2 + (frac_err * w_scale * (1 + dist**p))**2)
        else:
            raise ValueError("weight_mode must be 'measured', 'measured+relative', or 'measured+distance'.")

        if sigma_floor > 0:
            sy = np.maximum(sy, sigma_floor)
        return sy

    # ---- X axis iterative weighting ----
    beta_x = [w0guess, z0guess, zRguess]
    sy_x_fit = sy_x_meas.copy()
    for _ in range(max(1, iters)):
        sy_x_fit = build_sy_fit(zx_data, wx_data, sy_x_meas, beta_x, weight_mode)
        out_x = run_fit(zx_data, wx_data, sx_x, sy_x_fit, beta_x)
        beta_x = out_x.beta

    w0out_x, z0out_x, zRout_x = out_x.beta
    w0out_x_err, z0out_x_err, zRout_x_err = out_x.sd_beta

    # ---- Y axis iterative weighting ----
    beta_y = [w0guess, z0guess, zRguess]
    sy_y_fit = sy_y_meas.copy()
    for _ in range(max(1, iters)):
        sy_y_fit = build_sy_fit(zy_data, wy_data, sy_y_meas, beta_y, weight_mode)
        out_y = run_fit(zy_data, wy_data, sx_y, sy_y_fit, beta_y)
        beta_y = out_y.beta

    w0out_y, z0out_y, zRout_y = out_y.beta
    w0out_y_err, z0out_y_err, zRout_y_err = out_y.sd_beta

    # ---- Plot ----
    if show_plot:
        z_min = min(np.min(zx_data), np.min(zy_data))
        z_max = max(np.max(zx_data), np.max(zy_data))
        z_span = z_max - z_min if z_max > z_min else 1.0
        z_extrapolate_min = z_min - 0.3 * z_span
        z_extrapolate_max = z_max + 0.3 * z_span

        z_fit = np.linspace(z_extrapolate_min, z_extrapolate_max, plotpts)
        w_fit_x = w_of_z(out_x.beta, z_fit)
        w_fit_y = w_of_z(out_y.beta, z_fit)

        # choose which σ to show on the plot
        sy_x_plot = sy_x_meas if plot_error == 'measured' else sy_x_fit
        sy_y_plot = sy_y_meas if plot_error == 'measured' else sy_y_fit

        plt.figure(figsize=(5.5, 4))
        plt.errorbar(zx_data, wx_data * 1e6, xerr=sx_x, yerr=sy_x_plot * 1e6,
                     fmt='o', label='Data X',color='blue')
        plt.plot(z_fit, w_fit_x * 1e6, label='Fit X',color='blue')

        plt.errorbar(zy_data, wy_data * 1e6, xerr=sx_y, yerr=sy_y_plot * 1e6,
                     fmt='o', label='Data Y',color='green')
        plt.plot(z_fit, w_fit_y * 1e6, label='Fit Y',color='green')

        plt.xlabel('Position [m]')
        plt.ylabel('Beam size [$\\mu$m]')
        plt.xlim((z_extrapolate_min, z_extrapolate_max))
        plt.legend(loc='best')
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()

        if saveplot:
            plt.savefig(filename)
        plt.show()

    # ---- Results ----
    sol_x = (w0out_x, z0out_x, zRout_x, w0out_x_err, z0out_x_err, zRout_x_err)
    sol_y = (w0out_y, z0out_y, zRout_y, w0out_y_err, z0out_y_err, zRout_y_err)

    if print_results:
        print(f"Waist size for x data: {sol_x[0]:.3e} ± {sol_x[3]:.2e} m")
        print(f"Waist location for x data: {sol_x[1]:.3e} ({sol_x[1]/0.0254:.2e} inches) ± {sol_x[4]:.2e} m")
        print(f"Waist size for y data: {sol_y[0]:.3e} ± {sol_y[3]:.2e} m")
        print(f"Waist location for y data: {sol_y[1]:.3e} ({sol_y[1]/0.0254:.2e} inches) ± {sol_y[4]:.2e} m")
        print(f"Rayleigh range (x) is {np.pi*sol_x[0]**2/1064e-9:.2e} m "
              f"({(np.pi*sol_x[0]**2/1064e-9)/0.0254:.2e} inches)")
        print(f"Rayleigh range beam size (x) is {np.sqrt(2)*sol_x[0]:.2e}")

    return sol_x, sol_y



encoding = 'latin1'
import re
import itertools

def read_files(file_names,folder_path,zero_idx=1,i_range=None):
    """This function reads files for the profile fit"""
    # Arrays to store mean values
    wx_pos = []
    wy_pos= []
    wx_std_pos = []
    wy_std_pos = []
    z_pos=[]
    # print(folder_path,file_names)
    for file_path in folder_path.glob(f'{file_names}*.txt'):
        # print(file_path)
        match = re.match(fr'^{file_names}(\d+).txt$', file_path.name)  # Match the original file_names pattern
        # print(file_path,match)
        if match:
            number = int(match.group(1))
            z_pos.append((number) * 2.54)
            # print(number)
            # print(z_pos)
            # print(file_path)

        # Process each file
        # for i in i_range:
            # filepath = folder_path/f"{file_names}{i}.txt"
            skip_rows = 1
            df = pd.read_csv(file_path, sep=',', skiprows=skip_rows, encoding=encoding)
            # df_selected = df.iloc[:, [-3, -2]]
            wx_mean = df.iloc[:, 1].mean()
            wy_mean = df.iloc[:, 2].mean()
            wx_sd = df.iloc[:, 1].std()
            wy_sd = df.iloc[:, 2].std()
            wx_pos.append((wx_mean * 1e-6) / 2)
            wy_pos.append((wy_mean * 1e-6) / 2)
            wx_std_pos.append((wx_sd * 1e-6) / 1)
            wy_std_pos.append((wy_sd * 1e-6) / 1)

    wx_neg = []
    wy_neg= []
    wx_std_neg = []
    wy_std_neg = []
    z_neg=[]
    file_negative=f'{file_names}neg'
    # print(file_negative)
    for file_path_neg in folder_path.glob(f'{file_negative}*.txt'):
        # print(file_path_neg)
        match_neg = re.match(fr'^{file_negative}(\d+).txt$', file_path_neg.name)  # Match the _neg pattern

        if match_neg:  # Use elif to avoid double-matching if both regex could theoretically match
            number_neg = int(match_neg.group(1))
            z_neg.append(-1 * number_neg * 2.54)
            # print(number_neg)
            # print(file_path_neg)
        # Process each file
        # for i in i_range:
            # filepath = folder_path/f"{file_names}{i}.txt"
            skip_rows = 1
            df = pd.read_csv(file_path_neg, sep=',', skiprows=skip_rows, encoding=encoding)
            # df_selected = df.iloc[:, [-3, -2]]
            wx_mean = df.iloc[:, 1].mean()
            wy_mean = df.iloc[:, 2].mean()
            wx_sd = df.iloc[:, 1].std()
            wy_sd = df.iloc[:, 2].std()
            wx_neg.append((wx_mean * 1e-6) / 2)
            wy_neg.append((wy_mean * 1e-6) / 2)
            wx_std_neg.append((wx_sd * 1e-6) / 1)
            wy_std_neg.append((wy_sd * 1e-6) / 1)
        
    wx=wx_pos+wx_neg
    wy=wy_pos+wy_neg
    wx_std=wx_std_pos+wx_std_neg
    wy_std=wy_std_pos+wy_std_neg
    z=z_pos+z_neg 
    # print(z)
# Convert lists to NumPy arrays
    wx = np.array(wx)
    wy = np.array(wy)
    wx_std = np.array(wx_std)
    wy_std = np.array(wy_std)
    z=np.array(z)-(zero_idx*2.54)
    # print(len(z),len(wx))
    return wx, wy, wx_std, wy_std, z*1e-2


def calculate_q(w0x,w0y,zx,zy):
    """This function calculates the q parameter of the measured beam
    based on the fitted parameters"""
    if not w0x or not w0y or not zx or not zy:
        raise ValueError("Data is invalid")
    wavelength=1064e-9
    zrx=np.pi*w0x**2/wavelength
    zry=np.pi*w0y**2/wavelength

    qx=round(zx,4)+1j*round(zrx,4)
    qy=round(zy,4)+1j*round(zry,4)

    return qx, qy
    
#Let's define a function that calculates the focal length 
def calculate_focal_length(w0x_in,w0y_in,zx_in,zy_in,w0x_out,w0y_out,zx_out,zy_out):
    """This function calculates the focal length of the liquid lens
    from the ABCD matrix since we knwo the input q
    zx_in,zy_in,zx_out,zy_out are taken with respect to the lens
    positive z_in if the beam waist is before the lens"""

    qx_in,qy_in=calculate_q(w0x=w0x_in,w0y=w0y_in,zx=zx_in,zy=zy_in)
    qx_out,qy_out=calculate_q(w0x=w0x_out,w0y=w0y_out,zx=zx_out,zy=zy_out)

    fx=qx_in/(1-(qx_in/qx_out)) #the negative sign is just a convention of the waist location
    fy=qy_in/(1-(qy_in/qy_out))
    print("qx_in:","qy_in:",qx_in,qy_in,"qx_out:",qx_out,"qx_out:",qy_out)
    threshold=0.1*(np.abs(np.real(fx))+np.abs(np.real(fy)))/2
    if np.abs(np.imag(fx)) > np.abs(threshold) or np.abs(np.imag(fy)) > np.abs(threshold):
        raise ValueError(f"Focal length is imaginary. fx: {fx} fy: {fy}. \n Check q-parameters")
    else:
        fx,fy=round(np.real(fx),4),round(np.real(fy),4)
    return fx, fy

