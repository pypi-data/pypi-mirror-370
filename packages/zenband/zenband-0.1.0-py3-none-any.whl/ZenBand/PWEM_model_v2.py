import numpy as np
from scipy.linalg import eigvals
from tqdm import tqdm
#from numba import jit

#@jit(nopython=True)
def Calc_Conv2D(A,C,p,p_0,q,q_0,P,Q):
    for q_row in range(Q):
      for p_row in range(P):
          
        row = (q_row) * P + p_row
        
        for q_col in range(Q):
          for p_col in range(P):
              
            col   = (q_col) * P + p_col
            
            p_fft = int(p[p_row] - p[p_col]); 
            q_fft = int(q[q_row] - q[q_col]);
            
            C[row, col] = A[p_0 + p_fft, q_0 + q_fft];

    return C

def Conv_Mat(A, P, Q):
    
    Nx, Ny = np.shape(A); # Extract shape of an array
    
    # Spatial harmonic indices
    
    NH = P * Q;           # Total num of spatial harmonics
    
    p  = np.array(np.arange(-np.floor(P/2), np.floor(P/2) + 1))  # Spatial harmonic idx in x dir
    q  = np.array(np.arange(-np.floor(Q/2), np.floor(Q/2) + 1))  # Idx in y dir
        
    # Array indices for the zeroth harmonic
    
    p_0 = int(np.floor(Nx/2)); # add +1 in matlab
    
    q_0 = int(np.floor(Ny/2));
    
    # Fourier coefficients of A
    
    A  = np.fft.fftshift(np.fft.fftn(A) / (Nx * Ny)); # Ordered Fourier coeffs
    
    """
    Shifting is performed so that a component of zeroth frequency (DC component)
    is centered in the grid. The FFT is normalised to the grid resolution. 
    """
    
    # Init Convolution matrix;
    
    C = np.zeros((NH, NH), dtype = 'complex'); 
    
    C = Calc_Conv2D(A,C,p,p_0,q,q_0,P,Q)
            
    return C      

class PWEM_2D():
    
    def calc_E_mode_anisotropic(P, Q, T1, T2, bx, by, ERCzz, URCxx, URCyy, BC, norm, is_sweep=0, is_magnetic=0):
            
        M      = int(P*Q);
        Nbx    = np.shape(bx);
    
        # Harmonic axes
        p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
        q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
        [Q, P] = np.meshgrid(q, p)
    
        # Initialize normalized frequency arrays
        W  = np.zeros((M,Nbx[0]));

        #######################################################################
        if is_sweep == 0: # make sure that you don't get too many progress bars
            a = tqdm(range(0,Nbx[0]))
        else:
            a = range(0,Nbx[0])
            
        # Solve generalized eigen-value problem
        for nbeta in a:
            
            if BC == 1:
                Kx = bx[nbeta] - P * T1[0];
                Ky = by[nbeta] - Q * T2[1];
            else:
                Kx = bx[nbeta] - P * T1[0] - Q * T2[0]
                Ky = by[nbeta] - P * T1[1] - Q * T2[1]
                
            Kx, Ky = Kx.flatten(), Ky.flatten();
            Kx, Ky = np.diag(Kx), np.diag(Ky);
    
          #######################################################################
          
            if not is_magnetic:
                A  = Kx**2 + Ky**2;
            else:
                A  = Kx @ np.linalg.inv(URCyy) @ Kx + Ky @ np.linalg.inv(URCxx) @ Ky; # Operator for dielectric matrix
    
        #######################################################################
              
            k0           = eigvals(A, ERCzz);                    # Eigen values in general form (eig (A,B))
            k0           = np.sort(abs(k0))                                      # Sort eig vals (from lowest to highest).
            k0         = np.real(np.sqrt(k0)) / norm;                    # Normalize eig-vals
            W[:,nbeta] = k0;                                             # Append eig-vals
            
        return W
    
    
    def calc_H_mode_anisotropic(P, Q, T1, T2, bx, by, ERCxx, ERCyy, URCzz, BC, norm, is_sweep=0, is_magnetic=0):

        M      = int(P*Q); 
        Nbx    = np.shape(bx);
    
        # Harmonic axes
        p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
        q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
        [Q, P] = np.meshgrid(q, p)
    
        # Initialize normalized frequency arrays
        W  = np.zeros((M,Nbx[0]));

        #######################################################################
        if is_sweep == 0: # make sure that you don't get too many progress bars
            a = tqdm(range(0,Nbx[0]))
        else:
            a = range(0,Nbx[0])
            
        # Solve generalized eigen-value problem
        for nbeta in a:
            
            if BC == 1:
                Kx = bx[nbeta] - P * T1[0];
                Ky = by[nbeta] - Q * T2[1];
            else:
                Kx = bx[nbeta] - P * T1[0] - Q * T2[0]
                Ky = by[nbeta] - P * T1[1] - Q * T2[1]

            Kx, Ky = Kx.flatten(), Ky.flatten();
            Kx, Ky = np.diag(Kx), np.diag(Ky);
    
          #######################################################################
              
            A = Kx @ np.linalg.inv(ERCyy) @ Kx + Ky @ np.linalg.inv(ERCxx) @ Ky;
            
            if not is_magnetic:            
                k0 = np.linalg.eigvals(A)
            else:
                k0 = eigvals(A, np.linalg.inv(URCzz))
                
            k0           = np.sort(k0)
            k0           = np.real(np.sqrt(k0)) / norm;
            W[:,nbeta]   = k0;

        return W
    
    def calc_E_mode_dispersion(P, Q, Lx, Ly, bx, by, ERCzz, URCxx, URCyy, norm):
        pass
    
    def calc_H_mode_dispersion(P, Q, Lx, Ly, bx, by, ERCxx, ERCyy, URCzz, norm):
        pass
    
    def calc_E_mode(P, Q, T1, T2, bx, by, ERC, URC, BC, norm, is_sweep=0, is_magnetic=0):
        
        # P, Q - spatial harmonics
        # bx, by - Bloch wave vectors
        # ERC, URC - convolution matrices
            
        M      = int(P*Q);
    
        Nbx    = np.shape(bx);
    
        # Harmonic axes
        p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
        q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
        [Q, P] = np.meshgrid(q, p)
    
        # Initialize normalized frequency arrays
        W  = np.zeros((M,Nbx[0]));

        #######################################################################
        if is_sweep == 0: # make sure that you don't get too many progress bars
            a = tqdm(range(0,Nbx[0]))
        else:
            a = range(0,Nbx[0])
            
        # Solve generalized eigen-value problem
        for nbeta in a:
            
            Kx = bx[nbeta] - P * T1[0] - Q * T2[0]
            Ky = by[nbeta] - P * T1[1] - Q * T2[1]
                
            Kx, Ky = Kx.flatten(), Ky.flatten();
            Kx, Ky = np.diag(Kx), np.diag(Ky);
    
          #######################################################################
          
            if not is_magnetic:
                A  = Kx**2 + Ky**2;
            else:
                A  = Kx @ np.linalg.inv(URC) @ Kx + Ky @ np.linalg.inv(URC) @ Ky; # Operator for dielectric matrix
    
        #######################################################################
              
            k0           = eigvals(A, ERC);                    # Eigen values in general form (eig (A,B))
            k0           = np.sort(abs(k0))                                      # Sort eig vals (from lowest to highest).
            '''
            abs(k0), because sometimes the value is slightly negative, when it  should be zero
            '''
            k0         = np.real(np.sqrt(k0)) / norm;                    # Normalize eig-vals
            W[:,nbeta] = k0;                                             # Append eig-vals

        return W
    
    # @jit(nopython=True)
    def calc_H_mode(P, Q, T1, T2, bx, by, ERC, URC, BC, norm, is_sweep=0):
        
        #######################################################################

        M      = int(P*Q);
    
        Nbx    = np.shape(bx);
    
        # Harmonic axes
        p      = np.arange( -np.floor(P/2), np.floor(P/2) + 1);
        q      = np.arange( -np.floor(Q/2), np.floor(Q/2) + 1);
        [Q, P] = np.meshgrid(q, p)

        ERC_inv = np.linalg.inv(ERC)
    
        # Initialize normalized frequency arrays
        W  = np.zeros((M,Nbx[0]));

        #######################################################################
        if is_sweep == 0: # make sure that you don't get too many progress bars
            a = tqdm(range(0,Nbx[0]))
        else:
            a = range(0,Nbx[0])
            
        # Solve generalized eigen-value problem
        for nbeta in a:
            
            Kx = bx[nbeta] - P * T1[0] - Q * T2[0]
            Ky = by[nbeta] - P * T1[1] - Q * T2[1]

            Kx, Ky = Kx.flatten(), Ky.flatten();
            Kx, Ky = np.diag(Kx), np.diag(Ky);
    
          #######################################################################
              
            A = Kx @ ERC_inv @ Kx + Ky @ ERC_inv @ Ky;
            
            k0           = np.linalg.eigvals(A)
            k0           = np.sort(k0)
            k0           = np.real(np.sqrt(k0)) / norm;
            W[:,nbeta]   = k0;

        return W