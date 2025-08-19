import numpy as np
from numpy import linalg as LA

#######################################################################

class Params():

  # initialize class objects
  def __init__(self, app):
    self.Lx          = app.value_Lx;                  # period in x dir
    self.Ly          = app.value_Ly;                  # period in y dir
    self.r           = app.value_r;                   # circle diameter
    self.r2          = app.value_r2;                  # for ring
    self.ax          = app.value_ax;                  # ellipse length (x axis)
    self.ay          = app.value_ay;                  # ellipse width (y axis)
    self.er1         = app.eps1;                      # hole epsilon
    self.er2         = app.eps2;                      # material epsilon
    self.Mode        = 'E';                           # or H mode
    self.Harmonics   = [app.P, app.Q];                # harmonics in x, y, z dirs or P, Q, R
    self.dim         = [app.Nx, app.Ny];              # Nx, Ny, Nz ([1024, 1024] is optimal)
    self.norm        = 2 * np.pi/self.Lx;             # normalization constant
    self.is_magnetic = 0;                             # magnetic constant
    self.x           = np.linspace(-self.Lx/2, self.Lx/2,self.dim[0])
    self.y           = np.linspace(-self.Ly/2, self.Ly/2,self.dim[1])
    
    # for anisotropic materials
    self.erxx1 = app.erxx1
    self.eryy1 = app.eryy1
    self.erzz1 = app.erzz1
    
    self.erxx2 = app.erxx2
    self.eryy2 = app.eryy2
    self.erzz2 = app.erzz2

#######################################################################

class pwem_params():

    # initialize class objects
    def __init__(self, app, params):
        
        self.N_Points  = app.NBETA;   # 200 for publication
        self.BC        = app.BC;
        self.beta      = [];
        self.device_sel= app.device_selection
        self.import_dev = app.sel_import
        self.imported_data = app.imported_data;
        
        #######################################################################
        
        if self.device_sel == 'Square' or self.device_sel == 'Frame' or self.device_sel == 'Ring':
            
            #######################################################################
            ################ Rectangular Symmetry #################################
            
            self.T1    = 2*np.pi/params.Lx * np.array([[1],[0]])
            self.T2    = 2*np.pi/params.Ly * np.array([[0],[1]])
        
        elif self.device_sel == 'Hex':
            
            #######################################################################
            ################ Hexagonal Symmetry ###################################
            
            # direct lattice vectors
            self.t1 = params.Lx/2 * np.array([[1],[0]]) - params.Ly/2 * np.sqrt(3) * np.array([[0],[1]])
            self.t2 = params.Lx/2 * np.array([[1],[0]]) + params.Ly/2 * np.sqrt(3) * np.array([[0],[1]])
            
            # reciprocal lattice vectors
            self.T1 = 2*np.pi/params.Lx * np.array([[1],[0]]) - 2*np.pi/params.Ly/np.sqrt(3) * np.array([[0],[1]])
            self.T2 = 2*np.pi/params.Lx * np.array([[1],[0]]) + 2*np.pi/params.Ly/np.sqrt(3) * np.array([[0],[1]])
            
        elif self.device_sel == 'Honeycomb':
            
            #######################################################################
            ################# Honeycomb lattice ###################################
            # direct lattice vectors
            self.t1 = params.Lx/2 * np.sqrt(3) * np.array([[1],[0]]) - params.Ly/2 * 3 * np.array([[0],[1]])
            self.t2 = params.Lx/2 * np.sqrt(3) * np.array([[1],[0]]) + params.Ly/2 * 3 * np.array([[0],[1]])
            
            # reciprocal lattice vectors
            self.T1 = 2*np.pi/params.Lx/np.sqrt(3) * np.array([[1],[0]]) - 2*np.pi/params.Ly/3 * np.array([[0],[1]])
            self.T2 = 2*np.pi/params.Lx/np.sqrt(3) * np.array([[1],[0]]) + 2*np.pi/params.Ly/3 * np.array([[0],[1]])
            
        if self.import_dev == 'Yes':
            
            self.t1 = self.imported_data['t1']
            self.t2 = self.imported_data['t2']
            
            self.T1 = self.imported_data['T1']
            self.T2 = self.imported_data['T2']
            
            self.N_Points = int(np.sqrt(len(self.imported_data['beta'][0,:])))
            
    
    # Key points of symmetry
    def Symmetry(self, params):
        
        """
        Here only the photonic diagram's wavevector components are calculated.
        Consider it for finding only the band gaps, phase & group velocity
        """
        
        if self.import_dev == 'Yes':
            try:
                self.KP = self.imported_data['KP']
                self.KT = np.squeeze(self.imported_data['KT'])
                self.beta = self.imported_data['beta']
            except:
                self.beta = self.imported_data['beta']
            
        else:
            
            if self.BC != 0:
            ################### set key points of symmetry ##########################
            
                if self.device_sel == 'Square' or self.device_sel == 'Frame' or self.device_sel == 'Ring':
                    self.KP = ['$\Gamma$', '$X$', '$M$', '$\Gamma$']
                    
                    Gamma =  np.array([[0],[0]])
                    X     =  self.T1/2
                    M     = (self.T1 + self.T2)/2
                
                else:
                    self.KP = ['$\Gamma$', '$M$', '$K$', '$\Gamma$']
                    
                    if self.device_sel == 'Hex' or self.device_sel == 'Honeycomb':
                        Gamma = np.array([[0],[0]])
                        K     = 1/3 * (self.T1 + self.T2) 
                        M     = 1/2 * self.T2
                    else:
                        Gamma = np.array([[0],[0]])
                        K     = 1/3 * (self.T2 - self.T1)
                        M     = 1/2 * (self.T2)
      
                #######################################################################
                    
                if self.device_sel == 'Square' or self.device_sel == 'Frame' or self.device_sel == 'Ring':
                    KP  = [Gamma, X, M, Gamma]
                else:
                    KP  = [Gamma, M, K, Gamma]
                
                NKP = len(KP)
                L   = 0
                
                for i in range(NKP-1):
                    L = L + LA.norm(KP[i+1] - KP[i])
    
                res     = L/self.N_Points
                beta_x  = KP[0][0]
                beta_y  = KP[0][1]
                self.KT = [0]
                
            #######################################################################
            
                for nkp in range(NKP-1):
                    kp1 = KP[nkp]
                    kp2 = KP[nkp+1]
                    
                    L   = LA.norm(kp2 - kp1)
                    NB  = round(L/res)
                    
                    bx  = kp1[0] + (kp2[0] - kp1[0]) * list(range(1, NB+1))/NB
                    by  = kp1[1] + (kp2[1] - kp1[1]) * list(range(1, NB+1))/NB
                    
                    beta_x = np.concatenate((beta_x, bx))
                    beta_y = np.concatenate((beta_y, by))
                    self.KT.append(len(beta_x) - 1)
    
                self.beta = np.stack((beta_x, beta_y), axis = 0) 
    
            else:
                
                """
                This section here is for ISO-freq contour analysis. Keep in mind
                that Poynting vector will always be perpendicular (normal) to the
                tangent of a ISO-contour. ISO-contour is spatial dispersion which
                must be repeated by the incident beam.
                """
                
            #######################################################################
                if self.device_sel == 'Square' or self.device_sel == 'Frame' or self.device_sel == 'Ring':
                    bx    = np.linspace(-np.pi/params.Lx,  np.pi/params.Lx, self.N_Points)
                    by    = np.linspace( np.pi/params.Ly, -np.pi/params.Ly, self.N_Points)
                    beta  = np.zeros((2, self.N_Points**2))
                    
                    idx   = int(0);
                    
                    for nx in range(0, self.N_Points):
                        for ny in range(0, self.N_Points):
                            beta[:,idx] = np.array(([bx[nx], by[ny]]))
                            idx = idx + 1
                            
                    self.X0 = 0
                    self.Y0 = 0
                    
                else:
                    bx    = np.linspace(-params.Lx/2,  params.Lx/2, self.N_Points)
                    by    = np.linspace( params.Ly/2, -params.Ly/2, self.N_Points)
                    X, Y  = np.meshgrid(bx, by)
                    beta  = np.zeros((2, self.N_Points**2))
                    
                    if self.device_sel == 'Hex':
                        self.X0 = X * 8 * np.pi/3;
                        self.Y0 = Y * 4 * np.pi/np.sqrt(3);
                    else:
                        self.X0 = 2 * X * 4 * np.pi/3/np.sqrt(3);
                        self.Y0 = 2 * Y * 2 * np.pi/3;
                       
                    if self.device_sel == 'Hex':
                        ER       = np.ones((self.N_Points, self.N_Points))
                        # ER[:,:]  = abs(self.Y0) <= -abs(self.X0)*np.sqrt(3) + params.Lx/2 * 8 * np.sqrt(3) * np.pi/3
                    else:
                        ER       = np.ones((self.N_Points, self.N_Points))
                        # ER[:,:]  = abs(self.Y0) <= -abs(self.X0)*np.sqrt(3) + params.Lx/2 * 2 * 4 * np.pi/3
                    
                    vienas = []
                    du = []
    
                    for i in range(int(np.shape(self.X0)[0])):
                        for j in range(int(np.shape(self.X0)[1])):
                            vienas.append(self.X0[i][j]*ER[i][j])
                    for i in range(int(np.shape(self.Y0)[0])):
                        for j in range(int(np.shape(self.Y0)[1])):
                            du.append(self.Y0[i][j]*ER[i][j])
                        
                    beta[0,:] = vienas
                    beta[1,:] = du
    
            #######################################################################
            
                self.beta = np.array(beta)
    
        return self