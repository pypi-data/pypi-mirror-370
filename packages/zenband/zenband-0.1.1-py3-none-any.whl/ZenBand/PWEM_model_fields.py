import numpy as np
from scipy.linalg import eig
import copy

###############################################################################

def field(V, P, Q, m, Nx, Ny, ER, X0=0, Y0=0):
    
    s = V[:,m]
    s = np.reshape(s, (P,Q))
    
    nxc = np.ceil(Nx/2)
    nx1 = int(nxc - np.floor(P/2))
    nx2 = int(nxc + np.floor(P/2))
    nyc = np.ceil(Ny/2)
    ny1 = int(nyc - np.floor(Q/2))
    ny2 = int(nyc + np.floor(Q/2))
    
    sf = np.zeros((Nx, Ny), dtype = 'complex')
    sf[nx1-1:nx2,ny1-1:ny2] = s
    
    Ez = np.fft.ifft2(np.fft.ifftshift(sf))
        
    # az_max = np.array([max(abs(sublist)) for sublist in Ez])
    # az = az/max(abs(az_max))

    return Ez

def calc_E_mode_field(P, Q, T1, T2, beta_x, beta_y, ERC, URC, norm, Bloch_mode):
    
    # P, Q - spatial harmonics
    # bx, by - Bloch wave vectors
    # ERC, URC - convolution matrices

    # Harmonic axes
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)

    #######################################################################
        
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
  
    # if not is_magnetic:
    A  = Kx**2 + Ky**2;
    # else:
        # A  = Kx @ np.linalg.inv(URC) @ Kx + Ky @ np.linalg.inv(URC) @ Ky; # Operator for dielectric matrix
        
    master = eig(A, ERC)
    s  = master[1]                     # Get vectors
    k0 = master[0]
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    
    # find the correct Bloch_mode
    mode = 0

    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process unit wanted Bloch mode is found
    
    Bloch_place = k0_place

    return s, Bloch_place, k0

def calc_E_mode_H_field(P, Q, T1, T2, beta_x, beta_y, ERC, URC, norm, Bloch_mode, fc):

    # Harmonic axes
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)

    #######################################################################   
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
    # if not is_magnetic:
    A  = Kx**2 + Ky**2;
    
    master = eig(A, ERC)
    s  = master[1]  # Get vectors
    k0 = master[0]  # Get eigen-values
    
    # find the correct Bloch_mode
    k0_og = copy.copy(k0)
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    mode = 0
    
    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process until wanted Bloch mode is found
        
    Bloch_place = k0_place
    
    # get transverse electric field array
    if fc == 'x':
        ux = -1j/k0_og[Bloch_place] * Ky @ s
        return ux, Bloch_place, k0
    else:
        uy =  1j/k0_og[Bloch_place] * Kx @ s
        return uy, Bloch_place, k0

def calc_H_mode_field(P, Q, T1, T2, beta_x, beta_y, ERC, URC, norm, Bloch_mode):
    
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)
    
    ERC_inv = np.linalg.inv(ERC)

    #######################################################################
        
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
  
    A = Kx @ ERC_inv @ Kx + Ky @ ERC_inv @ Ky;
    
    master = eig(A)
    s  = master[1]                                       # Get vectors
    k0 = master[0]
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    
    # find the correct Bloch_mode
    mode = 0
    
    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process unit wanted Bloch mode is found
        
    Bloch_place = k0_place

    return s, Bloch_place, k0

def calc_H_mode_E_field(P, Q, T1, T2, beta_x, beta_y, ERC, URC, norm, Bloch_mode, fc):

    # Harmonic axes
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)
    
    ERC_inv = np.linalg.inv(ERC)

    #######################################################################   
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
  
    A = Kx @ ERC_inv @ Kx + Ky @ ERC_inv @ Ky;
    
    master = eig(A)
    u  = master[1]  # Get vectors
    k0 = master[0]  # Get eigen-values
    
    # find the correct Bloch_mode
    k0_og = copy.copy(k0)
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    mode = 0
    
    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process until wanted Bloch mode is found
        
    Bloch_place = k0_place
    
    # get transverse electric field array    
    if fc == 'x':
        sx = -1j/k0_og[Bloch_place] * ERC_inv @ Ky @ u
        return sx, Bloch_place, k0
    else:
        sy =  1j/k0_og[Bloch_place] * ERC_inv @ Kx @ u
        return sy, Bloch_place, k0


def calc_E_mode_field_anisotropic(P, Q, T1, T2, beta_x, beta_y, ERCzz, URCxx, URCyy, norm, Bloch_mode):
    
    # P, Q - spatial harmonics
    # bx, by - Bloch wave vectors
    # ERC, URC - convolution matrices

    # Harmonic axes
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)

    #######################################################################
        
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
  
    # if not is_magnetic:
    A  = Kx**2 + Ky**2;
    # else:
        # A  = Kx @ np.linalg.inv(URC) @ Kx + Ky @ np.linalg.inv(URC) @ Ky; # Operator for dielectric matrix
        
    master = eig(A, ERCzz)
    s  = master[1]    # Get vectors
    k0 = master[0]
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    
    # find the correct Bloch_mode
    mode = 0

    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10           # set it to a bigger value, so it is not found again
        mode = mode + 1                  # repeat the process until wanted Bloch mode is found
    
    Bloch_place = k0_place

    return s, Bloch_place, k0

def calc_E_mode_H_field_anisotropic(P, Q, T1, T2, beta_x, beta_y, ERCzz, URCxx, URCyy, norm, Bloch_mode, fc):

    # Harmonic axes
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)

    #######################################################################   
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
    # if not is_magnetic:
    A  = Kx**2 + Ky**2;
    
    master = eig(A, ERCzz)
    s  = master[1]  # Get vectors
    k0 = master[0]  # Get eigen-values
    
    # find the correct Bloch_mode
    k0_og = copy.copy(k0)
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    mode = 0
    
    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process until wanted Bloch mode is found
        
    Bloch_place = k0_place
    
    # get transverse electric field array    
    if fc == 'x':
        ux = -1j/k0_og[Bloch_place] * Ky @ s
        return ux, Bloch_place, k0
    else:
        uy =  1j/k0_og[Bloch_place] * Kx @ s
        return uy, Bloch_place, k0
    

def calc_H_mode_field_anisotropic(P, Q, T1, T2, beta_x, beta_y, ERCxx, ERCyy, URCzz, norm, Bloch_mode):
    
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)

    #######################################################################
        
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
  
    A = Kx @ np.linalg.inv(ERCyy) @ Kx + Ky @ np.linalg.inv(ERCxx) @ Ky;

    master = eig(A)
    s  = master[1]                                       # Get vectors
    k0 = master[0]
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    
    # find the correct Bloch_mode
    mode = 0
    
    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process unit wanted Bloch mode is found
        
    Bloch_place = k0_place

    return s, Bloch_place, k0

def calc_H_mode_E_field_anisotropic(P, Q, T1, T2, beta_x, beta_y, ERCxx, ERCyy, URCzz, norm, Bloch_mode, fc):

    # Harmonic axes
    p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
    q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
    [Q, P] = np.meshgrid(q, p)

    #######################################################################   
    # Solve generalized eigen-value problem
        
    Kx = beta_x - P * T1[0] - Q * T2[0]
    Ky = beta_y - P * T1[1] - Q * T2[1]
        
    Kx, Ky = Kx.flatten(), Ky.flatten();
    Kx, Ky = np.diag(Kx), np.diag(Ky);

  #######################################################################
    ERCxx_inv = np.linalg.inv(ERCxx)
    ERCyy_inv = np.linalg.inv(ERCyy)
    
    A = Kx @ ERCyy_inv @ Kx + Ky @ ERCxx_inv @ Ky;

    master = eig(A)
    u  = master[1]  # Get vectors
    k0 = master[0]  # Get eigen-values
    
    # find the correct Bloch_mode
    k0_og = copy.copy(k0)
    k0 = np.real(np.sqrt(k0)) / norm;
    k0_find = copy.copy(k0)
    mode = 0
    
    while mode < Bloch_mode:
        k0_place = np.argmin(k0_find)    # find minimum k0_place in array
        k0_find[k0_place] = 10            # set it to a bigger value, so it is not found again
        mode = mode + 1             # repeat the process until wanted Bloch mode is found
        
    Bloch_place = k0_place
    
    # get transverse electric field array
    if fc == 'x':
        sx = -1j/k0_og[Bloch_place] * ERCxx_inv @ Ky @ u
        return sx, Bloch_place, k0
    else:
        sy =  1j/k0_og[Bloch_place] * ERCyy_inv @ Kx @ u
        return sy, Bloch_place, k0
