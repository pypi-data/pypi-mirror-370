import customtkinter as tk
from tkinter import filedialog
from tkinter import messagebox 
import os
from scipy.io import loadmat
import numpy as np
###############################################################################
from .main_bands import Main_Bands
from .main_gif import Main_Gif
from .main_fields import Fields
from . import Get_Data

def create_entries(app, frame, ENTRY_NAME, pad_x, pad_y):
    
    # Init dictionary
    if not hasattr(app, "entries"):
        app.entries = {}
        
    for name in ENTRY_NAME:
        
        row   = tk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)

        label = tk.CTkLabel(row, text=name, width=100, anchor="w")
        label.pack(side="left")
        entry = tk.CTkEntry(row)
        entry.pack(side="right", fill="x")
        
        # Save entry to dictionary
        app.entries[name] = entry
        
def create_anisotropic_entries(app, frame, ENTRY_NAME, pad_x, pad_y):
    
    components = ['xz', 'xy', 'xx', 'yz', 'yy', 'yx', 'zz', 'zy', 'zx']
    
    # Init dictionary
    if not hasattr(app, "entries"):
        app.entries = {}
        
    for name in ENTRY_NAME:
        for i in range(3):

            row   = tk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=pad_x, pady=pad_y)

            for j in range(3):
                
                if i == 1 and j == 0:
                    label_anisotropic = tk.CTkLabel(row, text=name+' =')
                    label_anisotropic.pack(side='left', fill='x')
                    
                entry = tk.CTkEntry(row, width=40)
                entry.pack(side='right', fill='x')
                app.entries[name+components[i*3+j]] = entry
    

class App(tk.CTk):
    
    def __init__(self):
        super().__init__()
        
        # Set the name and current color of the app --------------------------
        self.title("ZenBand")
        self.background = 'Dark'
        tk.set_appearance_mode(self.background)
        
        # Geometry of the root window ----------------------------------------
        self.geometry("850x680")
        
        # Fill panels --------------------------------------------------------
        self.create_parameter_panel()
        self.create_tabbed_panel()
        self.create_extra_panel()
        
        # Get entries --------------------------------------------------------
        self.pack_params()
        
        # Initialise imported_data (otherwise won't work) --------------------
        self.imported_data = 0
    
    def create_parameter_panel(self):
        
        # LEFT panel ---------------------------------------------------------
        self.left_frame = tk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        label = tk.CTkLabel(self.left_frame, text="PWEM parameters", 
                            font=tk.CTkFont(size=16, weight="bold"))
        label.pack(pady=10)
        
        # Create entries and dropdown ----------------------------------------
        self.populate_params()
        
        
    def create_tabbed_panel(self):
        
        self.center_frame = tk.CTkFrame(self)
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        zen_tab = tk.CTkTabview(self.center_frame)
        zen_tab.pack(pady = 10)

        # Init tabs ----------------------------------------------------------
        tab1 = zen_tab.add("Calc Bands")
        tab2 = zen_tab.add("Calc OBG")
        tab3 = zen_tab.add("Calc Fields")
        
        # Populate tabs ------------------------------------------------------
        self.populate_tab1(tab1)
        self.populate_tab2(tab2)
        self.populate_tab3(tab3)
        
    def create_extra_panel(self):
        
        self.right_frame = tk.CTkFrame(self)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        
        label = tk.CTkLabel(self.right_frame, text="EXTRA parameters", 
                            font=tk.CTkFont(size=16, weight="bold"))
        
        label.pack(pady=10)
        
        self.populate_right_frame()
    
    def populate_params(self):
        pad_x, pad_y = 5, 5
        
        ENTRY_NAME = ["Lx", "Ly", "r", 'r2', 
                      "Ellipse_length", 'Ellipse_width', 
                      'eps1', 'eps2', 'P', 'Q', 'Nx', 
                      'Ny', 'Fontsize']
        
        create_entries(self, self.left_frame, ENTRY_NAME, pad_x, pad_y)
        
        # Device selection dropdown ------------------------------------------ 
        row   = tk.CTkFrame(self.left_frame, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)
        
        dropdown        = 'Device selection'
        label_selection = tk.CTkLabel(row, 
                                      text=dropdown)
        
        label_selection.pack(side="left")
        self.select_device   = tk.CTkComboBox(row,
                            values = ['Square', 'Frame', 'Ring',
                                      'Hex','Honeycomb'])
        self.select_device.pack(side="right", fill="x")
        
        # -------------------------------------------------------------------
        row   = tk.CTkFrame(self.left_frame, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)
        
        dropdown_mode   = 'Select Mode'
        label_selection = tk.CTkLabel(row, 
                                      text=dropdown_mode)
        label_selection.pack(side='left')
        
        self.select_mode   = tk.CTkComboBox(row,
                            values = ['E','H'])
        self.select_mode.pack(side='right')
    
    
    def get_entry_values(self):
        return {name: entry.get() for name, entry in self.entries.items()}
    
    def populate_tab1(self,tab):
        
        pad_x, pad_y = 5, 5
        
        label = tk.CTkLabel(tab, text="Bands and iso-freq contours", 
                            font=tk.CTkFont(size=16, weight="bold"))
        label.pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        ENTRY_NAME =  ["Enter N_beta","Enter no. of bands", 
                     "Lower omega limit", "Upper omega limit"]
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
            
        # -------------------------------------------------------------------
        
        tk.CTkButton(tab, text="Plot Device", command=self.plot_device).pack(pady=pad_y)
        tk.CTkButton(tab, text="Calc Bands", command=self.calc_bands).pack(pady=pad_y)

        # -------------------------------------------------------------------

        label = tk.CTkLabel(tab, text="Parameters for iso-freq contours", 
                            font=tk.CTkFont(size=16, weight="bold"))
        label.pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        ENTRY_NAME = ["Bloch mode","No. of lines"]
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
        
        # -------------------------------------------------------------------

        tk.CTkButton(tab, text="Calc Iso-Freq Contours", command=self.plot_contours).pack(pady=pad_y)
        tk.CTkButton(tab, text="Calc 3D Iso-Freq Contours", command=self.plot_contours3d).pack(pady=pad_y)
        
    def plot_device(self):
        self.BC = 1 
        Main_Bands(self).Plot_device()
        
    def calc_bands(self):
        self.BC = 1 
        Main_Bands(self).Band_diagram()
        
    def plot_contours(self):
        self.BC = 0 # need this for correct pwem parameters
        Main_Bands(self).Contours()
        
    def plot_contours3d(self):
        self.BC = 0 # need this for correct pwem parameters
        Main_Bands(self).Contours3D()
        

    def populate_tab2(self,tab):
        
        # -------------------------------------------------------------------
        
        pad_x, pad_y = 5, 5
        
        label = tk.CTkLabel(tab, text="Parameters for gaps and sweeps", 
                            font=tk.CTkFont(size=16, weight="bold"))
        
        label.pack(pady=pad_y)
        
        ENTRY_NAME = ["no. of Bloch modes","no. of bands", 
                     "Lower freq. limit", "Upper freq. limit",
                     "Enter beta pt num"]
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
            
        # -------------------------------------------------------------------
        
        tk.CTkButton(tab, text="Calc Gap", command=self.calc_gap).pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        label = tk.CTkLabel(tab, text="Parameters for parameter sweep", 
                            font=tk.CTkFont(size=16, weight="bold"))
        label.pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        ENTRY_NAME = ["min R","max R", 'min R2', 'max R2',
                     "No. of steps", "FPS val"]
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
        
        # -------------------------------------------------------------------
        
        tk.CTkButton(tab, text="Param sweep for R", command=self.param_sweep).pack(pady=pad_y)
        tk.CTkButton(tab, text="Make gif", command=self.band_gif).pack(pady=pad_y)
        
    def calc_gap(self):
        self.BC = 1 
        Main_Bands(self, 1).Gaps()
        
    def param_sweep(self):
        self.BC = 1 
        Main_Gif(self).band_sweep()        
        
    def band_gif(self):
        self.BC = 1 
        Main_Gif(self).make_gif()        


    def populate_tab3(self, tab):
        
        # -------------------------------------------------------------------

        pad_x, pad_y = 5, 5
        
        label = tk.CTkLabel(tab, text="gif and field parameters", 
                            font=tk.CTkFont(size=16, weight="bold"))
        
        label.pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        ENTRY_NAME = ['Bloch mode no.']
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
        
        # -------------------------------------------------------------------
        
        ENTRY_NAME = ['Frame Number', 'FPS value']
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
        
        tk.CTkButton(tab, text="Get field gif", command=self.field_gif).pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        label = tk.CTkLabel(tab, text="Field parameters", 
                            font=tk.CTkFont(size=16, weight="bold"))
        
        label.pack(pady=pad_y)
        
        ENTRY_NAME = ['beta_x (*pi/a)', 'beta_y (*pi/a)', 'Phase']
        
        create_entries(self, tab, ENTRY_NAME, pad_x, pad_y)
        
        # -------------------------------------------------------------------
        
        row   = tk.CTkFrame(tab, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)
        
        dropdown_mode   = 'Field type'
        label_selection = tk.CTkLabel(row, 
                                      text=dropdown_mode)
        
        self.select_field   = tk.CTkComboBox(row,
                            values = ['Re(f)','Intensity'])
        
        label_selection.pack(side='left')
        self.select_field.pack(side='right')
        
        # -------------------------------------------------------------------
        
        tk.CTkButton(tab, text="Calc Fz", command=self.field_z).pack(pady=pad_y)
        tk.CTkButton(tab, text="Calc Fx", command=self.field_x).pack(pady=pad_y)
        tk.CTkButton(tab, text="Calc Fy", command=self.field_y).pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        ENTRY_NAME = 1
        
    def field_gif(self):
        self.BC = 1
        Fields(self).Field_gif()
        
    def field_z(self):
        self.BC = 1
        self.field_comp = 'z'
        Fields(self).field_view()
        
    def field_x(self):
        self.BC = 1
        self.field_comp = 'x'
        Fields(self).field_view()
        
    def field_y(self):
        self.BC = 1
        self.field_comp = 'y'
        Fields(self).field_view()
        
    
    def populate_right_frame(self):
        
        # -------------------------------------------------------------------

        pad_x, pad_y = 5, 5
        
        # -------------------------------------------------------------------
        
        dropdown_mode   = 'Is material diagonally anisotropic?'
        label_selection = tk.CTkLabel(self.right_frame, 
                                      text=dropdown_mode)
        
        self.select_mode_mat   = tk.CTkComboBox(self.right_frame,
                            values = ['No','Yes'])
        
        label_selection.pack()
        self.select_mode_mat.pack()
        
        # -------------------------------------------------------------------
        
        label_anisotropic = tk.CTkLabel(self.right_frame, 
                                      text='Anisotropic parameters')
        label_anisotropic.pack()
        ENTRY_NAME = ['eps1', 'eps2']
        create_anisotropic_entries(self, self.right_frame, ENTRY_NAME, pad_x, pad_y)
        
        # -------------------------------------------------------------------
        
        dropdown_mode   = 'Use imported data'
        label_import = tk.CTkLabel(self.right_frame, 
                                      text=dropdown_mode)
        
        self.select_import   = tk.CTkComboBox(self.right_frame,
                            values = ['No','Yes'])
        
        label_import.pack()
        self.select_import.pack()
        
        tk.CTkButton(self.right_frame, text="Import .mat or .npy file with params", 
                     command = self.import_device).pack(pady=pad_y)
        
        # -------------------------------------------------------------------
        
        row   = tk.CTkFrame(self.right_frame, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)
        
        dropdown_mode   = 'Background'
        label_selection = tk.CTkLabel(row, 
                                      text=dropdown_mode)
        label_selection.pack(side='left')
        
        tk.CTkButton(row, text='Change', command=self.change_background, width=60).pack(side='right')
        
        self.select_background = tk.CTkComboBox(row, values=['Dark', 'Light'], width=100)
        self.select_background.pack(side='right', fill='x')
        
        # -------------------------------------------------------------------
        
        row   = tk.CTkFrame(self.right_frame, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)
        
        tk.CTkButton(row, text='Save parameters', command=self.save_params).pack()
        
        row   = tk.CTkFrame(self.right_frame, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=pad_y)
        
        tk.CTkButton(row, text='Load parameters', command=self.load_params).pack()
    
        
    def change_background(self):
        self.background = self.select_background.get()
        tk.set_appearance_mode(self.background)
        
    
    def save_params(self):
        Get_Data.save_params(self)
        
    def load_params(self):
        Get_Data.load_params(self)
        
    def import_device(self):
        global imported_data
        file_path = filedialog.askopenfilename(title='select a .mat file',
                                               filetypes=[('MATLAB & NumPy files', '*.mat; *.npy')])
        
        if file_path:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.mat':
                    self.imported_data = loadmat(file_path)
                elif ext == '.npy':
                    self.imported_data = np.load(file_path, allow_pickle=True).item()
                    
                try:
                    self.imported_data['er'], self.imported_data['KP'], self.imported_data['KT'],
                    self.imported_data['beta'], self.imported_data['t1'], self.imported_data['t2'], 
                    self.imported_data['T1'], self.imported_data['T2']
                    messagebox.showinfo('Nice', 'You can calculate bands and fields')
                except:
                    try:
                        self.imported_data['er'], self.imported_data['beta'], self.imported_data['t1'],
                        self.imported_data['t2'], self.imported_data['T1'], self.imported_data['T2']
                        messagebox.showinfo('Nice', 'You can calculate iso-frequency contours')
                    except:
                        messagebox.showerror('Error', 'Variables are not defined')
            except Exception as e:
                messagebox.showerror('Error', f'Could not load file: {e}')
            
        
    def pack_params(self):
        
        # -------------------------------------------------------------------
        
        """
        LEFT COLUMN
        """
        
        self.entries["Lx"].delete(0, "end")
        self.entries['Lx'].insert(0, "1.0")    
        
        self.entries["Ly"].delete(0, "end")  
        self.entries['Ly'].insert(0, "1.0")  
        
        self.entries["r"].delete(0, "end")  
        self.entries['r'].insert(0, "0.4")  
        
        self.entries['r2'].delete(0, 'end')
        self.entries['r2'].insert(0, '0.1')
        
        self.entries["Ellipse_length"].delete(0, "end")  
        self.entries['Ellipse_length'].insert(0, "1.0")  
        
        self.entries["Ellipse_width"].delete(0, "end")  
        self.entries['Ellipse_width'].insert(0, "1.0")  
        
        self.entries["eps1"].delete(0, "end")  
        self.entries['eps1'].insert(0, "1.0")  
        
        self.entries["eps2"].delete(0, "end")  
        self.entries['eps2'].insert(0, "12.0")  
        
        self.entries["P"].delete(0, "end")  
        self.entries['P'].insert(0, "11")  
        
        self.entries["Q"].delete(0, "end")  
        self.entries['Q'].insert(0, "11")  
        
        self.entries["Nx"].delete(0, "end")  
        self.entries['Nx'].insert(0, "1024")  
        
        self.entries["Ny"].delete(0, "end")  
        self.entries['Ny'].insert(0, "1024")  
        
        self.entries["Fontsize"].delete(0, "end")  
        self.entries['Fontsize'].insert(0, "16")  
        
        
        # --------------------------------------------------------------------
        """
        MID COLUMN Calc bands
        """
        
        self.entries["Enter N_beta"].delete(0, "end")
        self.entries['Enter N_beta'].insert(0, "50") 
        
        self.entries["Enter no. of bands"].delete(0, "end")
        self.entries['Enter no. of bands'].insert(0, "30") 
        
        self.entries["Lower omega limit"].delete(0, "end")
        self.entries['Lower omega limit'].insert(0, "0.0") 
        
        self.entries["Upper omega limit"].delete(0, "end")
        self.entries['Upper omega limit'].insert(0, "1.0") 
        
        self.entries["Bloch mode"].delete(0, "end")
        self.entries['Bloch mode'].insert(0, "2") 
        
        self.entries["No. of lines"].delete(0, "end")
        self.entries['No. of lines'].insert(0, "10") 
        
        """
        MID COLUMN Calc OBG
        """
        
        self.entries["no. of Bloch modes"].delete(0, "end")
        self.entries['no. of Bloch modes'].insert(0, "5") 
        
        self.entries["no. of bands"].delete(0, "end")
        self.entries['no. of bands'].insert(0, "15") 
        
        self.entries["Lower freq. limit"].delete(0, "end")
        self.entries['Lower freq. limit'].insert(0, "0.0") 
        
        self.entries["Upper freq. limit"].delete(0, "end")
        self.entries['Upper freq. limit'].insert(0, "1.0") 
        
        self.entries["Enter beta pt num"].delete(0, "end")
        self.entries['Enter beta pt num'].insert(0, "50")
        
        self.entries["min R"].delete(0, "end")
        self.entries['min R'].insert(0, "0")
        
        self.entries["max R"].delete(0, "end")
        self.entries['max R'].insert(0, "0.5")
        
        self.entries["min R2"].delete(0, "end")
        self.entries['min R2'].insert(0, "0")
        
        self.entries["max R2"].delete(0, "end")
        self.entries['max R2'].insert(0, "0.5")
        
        self.entries["No. of steps"].delete(0, "end")
        self.entries['No. of steps'].insert(0, "5")
        
        self.entries["FPS val"].delete(0, "end")
        self.entries["FPS val"].insert(0, "10")  
        
        # --------------------------------------------------------------------
        
        self.entries["Bloch mode no."].delete(0, "end")
        self.entries["Bloch mode no."].insert(0, "5")  
        
        self.entries["Frame Number"].delete(0, "end")
        self.entries["Frame Number"].insert(0, "5")  
        
        self.entries["FPS value"].delete(0, "end")
        self.entries["FPS value"].insert(0, "10")  
        
        self.entries["beta_x (*pi/a)"].delete(0, "end")
        self.entries["beta_x (*pi/a)"].insert(0, "1")  
        
        self.entries["beta_y (*pi/a)"].delete(0, "end")
        self.entries["beta_y (*pi/a)"].insert(0, "1")  
        
        self.entries['Phase'].delete(0, 'end')
        self.entries['Phase'].insert(0, '0')
        
        # --------------------------------------------------------------------
        
        self.entries['eps1xx'].delete(0, 'end')
        self.entries['eps1xx'].insert(0, '1.0')
        
        self.entries['eps1xy'].delete(0, 'end')
        self.entries['eps1xy'].insert(0, '0')
        self.entries['eps1xy'].configure(state='disabled')
        
        self.entries['eps1xz'].delete(0, 'end')
        self.entries['eps1xz'].insert(0, '0')
        self.entries['eps1xz'].configure(state='disabled')
        
        self.entries['eps1yx'].delete(0, 'end')
        self.entries['eps1yx'].insert(0, '0')
        self.entries['eps1yx'].configure(state='disabled')
        
        self.entries['eps1yy'].delete(0, 'end')
        self.entries['eps1yy'].insert(0, '1.0')
        
        self.entries['eps1yz'].delete(0, 'end')
        self.entries['eps1yz'].insert(0, '0')
        self.entries['eps1yz'].configure(state='disabled')
        
        self.entries['eps1zx'].delete(0, 'end')
        self.entries['eps1zx'].insert(0, '0')
        self.entries['eps1zx'].configure(state='disabled')
        
        self.entries['eps1zy'].delete(0, 'end')
        self.entries['eps1zy'].insert(0, '0')
        self.entries['eps1zy'].configure(state='disabled')
        
        self.entries['eps1zz'].delete(0, 'end')
        self.entries['eps1zz'].insert(0, '1.0')
        
        self.entries['eps2xx'].delete(0, 'end')
        self.entries['eps2xx'].insert(0, '12.0')
        
        self.entries['eps2xy'].delete(0, 'end')
        self.entries['eps2xy'].insert(0, '0')
        self.entries['eps2xy'].configure(state='disabled')
        
        self.entries['eps2xz'].delete(0, 'end')
        self.entries['eps2xz'].insert(0, '0')
        self.entries['eps2xz'].configure(state='disabled')
        
        self.entries['eps2yx'].delete(0, 'end')
        self.entries['eps2yx'].insert(0, '0')
        self.entries['eps2yx'].configure(state='disabled')
        
        self.entries['eps2yy'].delete(0, 'end')
        self.entries['eps2yy'].insert(0, '12.0')
        
        self.entries['eps2yz'].delete(0, 'end')
        self.entries['eps2yz'].insert(0, '0')
        self.entries['eps2yz'].configure(state='disabled')
        
        self.entries['eps2zx'].delete(0, 'end')
        self.entries['eps2zx'].insert(0, '0')
        self.entries['eps2zx'].configure(state='disabled')
    
        self.entries['eps2zy'].delete(0, 'end')
        self.entries['eps2zy'].insert(0, '0')
        self.entries['eps2zy'].configure(state='disabled')
        
        self.entries['eps2zz'].delete(0, 'end')
        self.entries['eps2zz'].insert(0, '12.0')   
        
        # --------------------------------------------------------------------
        
    def get_params(self):
        """
        GET VALUES
        """
        
        self.value_Lx = float(self.entries['Lx'].get())
        self.value_Ly = float(self.entries['Ly'].get())
        
        self.value_r  = float(self.entries['r'].get())
        self.value_r2 = float(self.entries['r2'].get())
        self.value_ax = float(self.entries['Ellipse_length'].get())
        self.value_ay = float(self.entries['Ellipse_width'].get())
        self.eps1     = float(self.entries['eps1'].get())
        self.eps2     = float(self.entries['eps2'].get())
        self.P        = int(  self.entries['P'].get())
        self.Q        = int(  self.entries['Q'].get())
        self.Nx       = int(  self.entries['Nx'].get())
        self.Ny       = int(  self.entries['Ny'].get())
        self.FontSize = float(self.entries['Fontsize'].get())        
        self.device_selection = self.select_device.get()
        self.sel_mode         = self.select_mode.get()
        
        # --------------------------------------------------------------------
        
        self.NBETA    = int(  self.entries['Enter N_beta'].get())
        self.NBANDS   = int(  self.entries['Enter no. of bands'].get())
        self.omega_Lo = float(self.entries['Lower omega limit'].get())
        self.omega_Hi = float(self.entries['Upper omega limit'].get())
        self.Bloch_Mo = int(  self.entries['Bloch mode'].get())
        self.Line_num = int(  self.entries['No. of lines'].get())
        
        # --------------------------------------------------------------------
        
        # Gif code - sweep R
        self.Bloch_mode_num = int(self.entries['no. of Bloch modes'].get())
        self.no_of_bands    = int(self.entries['no. of bands'].get())
        self.lower_freq_lim = float(self.entries['Lower freq. limit'].get())
        self.upper_freq_lim = float(self.entries['Upper freq. limit'].get())
        self.beta_pt_num    = int(self.entries['Enter beta pt num'].get())
        self.min_R_lim      = float(self.entries['min R'].get())
        self.max_R_lim      = float(self.entries['max R'].get())
        self.min_R2_lim      = float(self.entries['min R2'].get())
        self.max_R2_lim      = float(self.entries['max R2'].get())
        self.no_of_steps    = int(self.entries['No. of steps'].get())
        self.FPS_val        = int(self.entries['FPS val'].get())
        
        # --------------------------------------------------------------------
        
        # Gif code - sweep beta
        self.Bloch_mode_no = int(self.entries['Bloch mode no.'].get())
        self.Frame_num     = int(self.entries['Frame Number'].get())
        self.FPS_val_beta  = int(self.entries['FPS value'].get())
        self.beta_x_val    = float(self.entries['beta_x (*pi/a)'].get())
        self.beta_y_val    = float(self.entries['beta_y (*pi/a)'].get())
        self.phase         = float(self.entries['Phase'].get())
        self.sel_field     = self.select_field.get()
        
        # --------------------------------------------------------------------
        # Extra params
        self.sel_anisotropy = self.select_mode_mat.get()
        self.sel_import = self.select_import.get()
        
        # --------------------------------------------------------------------
        # Anisotropic params
        self.erxx1 = float(self.entries['eps1xx'].get())
        self.eryy1 = float(self.entries['eps1yy'].get())
        self.erzz1 = float(self.entries['eps1zz'].get())
        self.erxx2 = float(self.entries['eps2xx'].get())
        self.eryy2 = float(self.entries['eps2yy'].get())
        self.erzz2 = float(self.entries['eps2zz'].get())
        
        
        
def run():
    app = App()
    app.mainloop()
