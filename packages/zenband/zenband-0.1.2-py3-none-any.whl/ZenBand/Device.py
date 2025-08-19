import numpy as np
import matplotlib.pyplot as plt
from .PWEM_model_v2 import Conv_Mat

plt.rcParams["figure.figsize"] = (6.4, 4.8)
plt.rcParams.update({'font.size': 18})

class device():
  
    # initialize class objects
    def __init__(self):
        self.ER  = []
        self.UR  = []
        self.ERC = []
        self.URC = []
        
        self.ERxx = []
        self.ERyy = []
        self.ERzz = []
    
        self.ERCxx = []
        self.ERCyy = []
        self.ERCzz = []
    
    # Plot the unit cell
    def Plot_Device(self,params):
        plt.figure()
        plt.imshow(np.real(self.ER), extent = [-params.Lx/2, params.Lx/2, -params.Ly/2, params.Ly/2],
                   aspect = 'auto',  cmap = 'jet')
        plt.xlabel('$x$')
        plt.ylabel('$y$')
        plt.title(r'Unit cell Re ${\varepsilon(x,y)}$')
        plt.colorbar()
        plt.savefig("ER.pdf", format="pdf", bbox_inches="tight")
    
    # Plot convmat
    def Plot_ERC(self, params):
        plt.figure()
        Re = np.real(self.ERC); 
        Im = np.imag(self.ERC);
        plt.subplot(1, 2, 1)
        plt.imshow(Re, aspect = 'auto', cmap = 'jet')
        plt.colorbar()
        plt.subplot(1, 2, 2)
        plt.imshow(Im, aspect = 'auto', cmap = 'jet')
        plt.colorbar()
        plt.savefig("ERC.pdf", format="pdf", bbox_inches="tight")
    
    # Define Ellipse 
    def Ellipse(self, params):
        nx, ny   = params.dim
        ER       = np.zeros((nx,ny))
        X, Y     = np.meshgrid(params.x, params.y)                      # Meshgrid for R
        ER[:,:]  = (X/params.ax)**2 + (Y/params.ay)**2 >= params.r**2;  # Define the circle of ones
        self.ER  = ER*(params.er2 - params.er1) + params.er1
        self.ERC = Conv_Mat(self.ER, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def Ellipse_anisotropic(self, params):
        nx, ny   = params.dim
        ER       = np.zeros((nx,ny))
        X, Y     = np.meshgrid(params.x, params.y)                      # Meshgrid for R
        ER[:,:]  = (X/params.ax)**2 + (Y/params.ay)**2 >= params.r**2;  # Define the circle of ones
        
        self.ERxx  = ER*(params.erxx2 - params.erxx1) + params.erxx1
        self.ERCxx = Conv_Mat(self.ERxx, params.Harmonics[0], params.Harmonics[1])
        
        self.ERyy  = ER*(params.eryy2 - params.eryy1) + params.eryy1
        self.ERCyy = Conv_Mat(self.ERyy, params.Harmonics[0], params.Harmonics[1])
        
        self.ERzz  = ER*(params.erzz2 - params.erzz1) + params.erzz1
        self.ERCzz = Conv_Mat(self.ERzz, params.Harmonics[0], params.Harmonics[1])
        return self
    
    # Define Ring
    def Ring(self, params):
        nx, ny   = params.dim
        ER       = np.zeros((nx,ny))
        X, Y     = np.meshgrid(params.x, params.y)                      # Meshgrid for R
        ER[:,:]  = (X/params.ax)**2 + (Y/params.ay)**2 >= params.r**2;  # Define the circle of ones
        # Inner ellipse
        ER2      = np.zeros((nx, ny))
        ER2[:,:] = (X/params.ax)**2 + (Y/params.ay)**2 <= params.r2**2;
        # Combining the two ellipses to form a ring
        ER       = ER + ER2;
        self.ER  = ER*(params.er2 - params.er1) + params.er1
        self.ERC = Conv_Mat(self.ER, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def Ring_anisotropic(self, params):
        nx, ny   = params.dim
        ER       = np.zeros((nx,ny))
        X, Y     = np.meshgrid(params.x, params.y)                      # Meshgrid for R
        ER[:,:]  = (X/params.ax)**2 + (Y/params.ay)**2 >= params.r**2;  # Define the circle of ones
        # Inner ellipse
        ER2      = np.zeros((nx, ny))
        ER2[:,:] = (X/params.ax)**2 + (Y/params.ay)**2 <= params.r2**2;
        # Combining the two ellipses to form a ring
        ER       = ER + ER2;
        
        self.ERxx  = ER*(params.erxx2 - params.erxx1) + params.erxx1
        self.ERCxx = Conv_Mat(self.ERxx, params.Harmonics[0], params.Harmonics[1])
        
        self.ERyy  = ER*(params.eryy2 - params.eryy1) + params.eryy1
        self.ERCyy = Conv_Mat(self.ERyy, params.Harmonics[0], params.Harmonics[1])
        
        self.ERzz  = ER*(params.erzz2 - params.erzz1) + params.erzz1
        self.ERCzz = Conv_Mat(self.ERzz, params.Harmonics[0], params.Harmonics[1])
        return self
    
    # Define Frame
    def Frame(self, params):
        nx, ny   = params.dim
        ER       = np.zeros((nx,ny))
        ER1      = np.zeros((nx,ny))
        ER2      = np.zeros((nx,ny))
        X, Y     = np.meshgrid(params.x, params.y)                      # Meshgrid for R
        # A quirky way of defining the frame
        ER1[:,:]  = abs((X/params.ax)) >= params.r;
        ER2[:,:]  = abs((Y/params.ay)) >= params.r;
        ER3       = ER1 + ER2
        ER4       = abs(ER1 - ER2)
        ER        = (ER3 + ER4)/2
        self.ER        = ER*(params.er2 - params.er1) + params.er1
        self.ERC = Conv_Mat(self.ER, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def Frame_anisotropic(self, params):
        nx, ny   = params.dim
        ER       = np.zeros((nx,ny))
        ER1      = np.zeros((nx,ny))
        ER2      = np.zeros((nx,ny))
        X, Y     = np.meshgrid(params.x, params.y)                      # Meshgrid for R
        # A quirky way of defining the frame
        ER1[:,:]  = abs((X/params.ax)) >= params.r;
        ER2[:,:]  = abs((Y/params.ay)) >= params.r;
        ER3       = ER1 + ER2
        ER4       = abs(ER1 - ER2)
        ER        = (ER3 + ER4)/2
        
        self.ERxx  = ER*(params.erxx2 - params.erxx1) + params.erxx1
        self.ERCxx = Conv_Mat(self.ERxx, params.Harmonics[0], params.Harmonics[1])
        
        self.ERyy  = ER*(params.eryy2 - params.eryy1) + params.eryy1
        self.ERCyy = Conv_Mat(self.ERyy, params.Harmonics[0], params.Harmonics[1])
        
        self.ERzz  = ER*(params.erzz2 - params.erzz1) + params.erzz1
        self.ERCzz = Conv_Mat(self.ERzz, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def oblique(self, params, t1, t2):
        
        a       = params.Lx
        b       = params.Ly
        
        Q, P    = np.meshgrid(np.linspace(-1/2, 1/2, params.dim[0]), np.linspace(-1/2, 1/2, params.dim[1]))
        self.X0 = P * t1[0] + Q * t2[0]
        self.Y0 = P * t1[1] + Q * t2[1]
        
        b       = params.Ly * np.sqrt(3)
        ER      = np.zeros((params.dim[0], params.dim[1]))

        ER[:,:] = ER + ((((self.X0 - a/2)/params.ax)**2 + (self.Y0/params.ay)**2) <= params.r**2)
        ER[:,:] = ER + ((((self.X0 + a/2)/params.ax)**2 + (self.Y0/params.ay)**2) <= params.r**2)
        ER[:,:] = ER + (((self.X0/params.ax)**2 + ((self.Y0 - b/2)/params.ay)**2) <= params.r**2)
        ER[:,:] = ER + (((self.X0/params.ax)**2 + ((self.Y0 + b/2)/params.ay)**2) <= params.r**2)

        self.ER  = params.er2 + (params.er1 - params.er2) * ER
        self.ERC = Conv_Mat(self.ER, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def oblique_anisotropic(self, params, t1, t2):
        
        a       = params.Lx
        b       = params.Ly
        
        Q, P    = np.meshgrid(np.linspace(-1/2, 1/2, params.dim[0]), np.linspace(-1/2, 1/2, params.dim[1]))
        self.X0 = P * t1[0] + Q * t2[0]
        self.Y0 = P * t1[1] + Q * t2[1]
        
        b       = params.Ly * np.sqrt(3)
        ER      = np.zeros((params.dim[0], params.dim[1]))

        ER[:,:] = ER + ((((self.X0 - a/2)/params.ax)**2 + (self.Y0/params.ay)**2) <= params.r**2)
        ER[:,:] = ER + ((((self.X0 + a/2)/params.ax)**2 + (self.Y0/params.ay)**2) <= params.r**2)
        ER[:,:] = ER + (((self.X0/params.ax)**2 + ((self.Y0 - b/2)/params.ay)**2) <= params.r**2)
        ER[:,:] = ER + (((self.X0/params.ax)**2 + ((self.Y0 + b/2)/params.ay)**2) <= params.r**2)

        self.ERxx  = ER*(params.erxx2 - params.erxx1) + params.erxx1
        self.ERCxx = Conv_Mat(self.ERxx, params.Harmonics[0], params.Harmonics[1])
        
        self.ERyy  = ER*(params.eryy2 - params.eryy1) + params.eryy1
        self.ERCyy = Conv_Mat(self.ERyy, params.Harmonics[0], params.Harmonics[1])
        
        self.ERzz  = ER*(params.erzz2 - params.erzz1) + params.erzz1
        self.ERCzz = Conv_Mat(self.ERzz, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def honeycomb(self, params, t1, t2):
                
        a       = params.Lx
        b       = params.Ly
        
        Q, P    = np.meshgrid(np.linspace(-1/2, 1/2, params.dim[0]), np.linspace(-1/2, 1/2, params.dim[1]))
        self.X0 = P * t1[0] + Q * t2[0]
        self.Y0 = P * t1[1] + Q * t2[1]

        b       = params.Ly * np.sqrt(3) * np.sqrt(3)
        ER      = np.zeros((params.dim[0], params.dim[1]))

        ER = (((self.X0/params.ax)**2 + ((self.Y0 - b/6*params.Ly)/params.ay)**2) <= params.r**2)
        ER = ER + (((self.X0/params.ax)**2 + ((self.Y0 + b/6*params.Ly)/params.ay)**2) <= params.r2**2)
        
        self.ER  = ER*(params.er1 - params.er2) + params.er2
        self.ERC = Conv_Mat(self.ER, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def honeycomb_anisotropic(self, params, t1, t2):
                
        a       = params.Lx
        b       = params.Ly
        
        Q, P    = np.meshgrid(np.linspace(-1/2, 1/2, params.dim[0]), np.linspace(-1/2, 1/2, params.dim[1]))
        self.X0 = P * t1[0] + Q * t2[0]
        self.Y0 = P * t1[1] + Q * t2[1]

        b       = params.Ly * np.sqrt(3) * np.sqrt(3)
        ER      = np.zeros((params.dim[0], params.dim[1]))

        ER = (((self.X0/params.ax)**2 + ((self.Y0 - b/6*params.Ly)/params.ay)**2) <= params.r**2)
        ER = ER + (((self.X0/params.ax)**2 + ((self.Y0 + b/6*params.Ly)/params.ay)**2) <= params.r**2)
        
        self.ERxx  = ER*(params.erxx2 - params.erxx1) + params.erxx1
        self.ERCxx = Conv_Mat(self.ERxx, params.Harmonics[0], params.Harmonics[1])
        
        self.ERyy  = ER*(params.eryy2 - params.eryy1) + params.eryy1
        self.ERCyy = Conv_Mat(self.ERyy, params.Harmonics[0], params.Harmonics[1])
        
        self.ERzz  = ER*(params.erzz2 - params.erzz1) + params.erzz1
        self.ERCzz = Conv_Mat(self.ERzz, params.Harmonics[0], params.Harmonics[1])
        return self
    
    def imported_uc(self, params, imported_data):
        
        t1 = imported_data['t1']
        t2 = imported_data['t2']
        er = imported_data['er']
        
        x = np.linspace(-params.Lx/2, params.Lx/2, np.shape(er)[0])
        y = np.linspace(-params.Ly/2, params.Ly/2, np.shape(er)[1])
        
        Q, P = np.meshgrid(x, y)
        
        self.X0 = P * t1[0] + Q * t2[0]
        self.Y0 = P * t1[1] + Q * t2[1]
        
        self.ER = er
        self.ERC = Conv_Mat(self.ER, params.Harmonics[0], params.Harmonics[1])
    
        return self
        