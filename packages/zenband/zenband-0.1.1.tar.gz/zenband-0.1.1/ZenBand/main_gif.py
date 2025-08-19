from .Device import device
from .Params import Params, pwem_params
from .PWEM_model_v2 import PWEM_2D
from .create_fig import create_frame
from .Band_Gaps import Band_Gaps
import numpy as np
import customtkinter as tk
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tqdm import tqdm
import imageio
import os
import shutil

#######################################################################
class Main_Gif():
    def __init__(self, app):
        
        app.get_params()
        self.app = app
        
        self.params = Params(app);
        self.Device = device();
        
    def band_sweep(self):

        t  = 0                                               
        R  = np.linspace(self.app.min_R_lim, self.app.max_R_lim, self.app.no_of_steps)
        R2 = np.linspace(self.app.min_R2_lim, self.app.max_R2_lim, self.app.no_of_steps)
        
        gaps      = []                                           # for storing omnidirectional band gaps
        omega_max = []
        omega_min = []
        
        gaps_h      = []                                         # for storing omnidirectional band gaps
        omega_max_h = []
        omega_min_h = []
            
        ################### create images for a gif #############################
        
        for r in tqdm(R):
            self.params.r  = r
            self.params.r2 = R2[t]
        
            Pwem_params    = pwem_params(self.app, self.params)
            Pwem_params.N_Points = self.app.beta_pt_num # overwrite number of Beta vectors to match 2nd tab
            Pwem_params.BC = 1
            Pwem_params.Symmetry(self.params);
            
            if self.app.sel_anisotropy == 'No':
                if self.app.device_selection == 'Square':
                    self.Device.Ellipse(self.params)
                elif self.app.device_selection == 'Frame':
                    self.Device.Frame(self.params)
                elif self.app.device_selection == 'Ring':
                    self.Device.Ring(self.params)
                elif self.app.device_selection == 'Hex':
                    self.Device.oblique(self.params, Pwem_params.t1, Pwem_params.t2)
                elif self.app.device_selection == 'Honeycomb':
                    self.Device.honeycomb(self.params, Pwem_params.t1, Pwem_params.t2)
            else:
                if self.app.device_selection == 'Square':
                    self.Device.Ellipse_anisotropic(self.params)
                elif self.app.device_selection == 'Frame':
                    self.Device.Frame_anisotropic(self.params)
                elif self.app.device_selection == 'Ring':
                    self.Device.Ring_anisotropic(self.params)
                elif self.app.device_selection == 'Hex':
                    self.Device.oblique_anisotropic(self.params, Pwem_params.t1, Pwem_params.t2)
                elif self.app.device_selection == 'Honeycomb':
                    self.Device.honeycomb_anisotropic(self.params, Pwem_params.t1, Pwem_params.t2)

            #######################################################################
            if self.app.sel_anisotropy == 'No':
                for mode in ['E', 'H']:
                    if mode == 'E':
                        WE = PWEM_2D.calc_E_mode(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                                     self.app.device_selection, self.params.norm, 1)
                    else:
                        WH = PWEM_2D.calc_H_mode(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                                     self.app.device_selection, self.params.norm, 1)
            else:
                for mode in ['E', 'H']:
                    if mode == 'E':
                        WE = PWEM_2D.calc_E_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERCzz, self.Device.URC, self.Device.URC, 
                                                     self.app.device_selection, self.params.norm, 1)
                    else:
                        WH = PWEM_2D.calc_H_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERCxx, self.Device.ERCyy, self.Device.URC,
                                                     self.app.device_selection, self.params.norm, 1)

            t = t + 1
            
            # print("Iter {} out of".format(int(t)), " {}".format(len(R)))
            
        ####################### append omnidirectional band gap width #########
            
            # for E mode
            # gaps = Band_Gaps.find_gaps(WE, self.app.Bloch_mode_num)
            # print(gaps[0])
            gaps.extend(Band_Gaps.find_gaps(WE, self.app.Bloch_mode_num)[0])
            omega_min.extend(Band_Gaps.find_gaps(WE, self.app.Bloch_mode_num)[1])
            omega_max.extend(Band_Gaps.find_gaps(WE, self.app.Bloch_mode_num)[2])
            
            # for H mode
            # gaps = Band_Gaps.find_gaps(WH, self.app.Bloch_mode_num)
            gaps_h.extend(Band_Gaps.find_gaps(WH, self.app.Bloch_mode_num)[0])
            omega_min_h.extend(Band_Gaps.find_gaps(WH, self.app.Bloch_mode_num)[1])
            omega_max_h.extend(Band_Gaps.find_gaps(WH, self.app.Bloch_mode_num)[2])
            
        ####################### plot omnidirectional band gap width ###########
        
        fig = Band_Gaps.Plot_Gaps(R, gaps, gaps_h, omega_min, omega_min_h, omega_max, omega_max_h, self.app.lower_freq_lim,
                                  self.app.upper_freq_lim, self.app.min_R_lim, self.app.max_R_lim, self.app.background, self.app.FontSize,
                                  self.app.Bloch_mode_num)
            
        
        plot_window = Toplevel()
        
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar
        color = "#505050"

        toolbar = NavigationToolbar2Tk(canvas, plot_window)
        toolbar.config(background=color)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM)
        
        
    def make_gif(self):
        
        name = 'img_er{}'.format(self.params.er1)                # make a folder for gif images
        if not os.path.exists(f'./img_er{self.params.er1}'):
            os.mkdir(name)
    
        t = 0                                               # to help number figures for a gif
        R = np.linspace(self.app.min_R_lim, self.app.max_R_lim, self.app.no_of_steps)
            
        ################### create images for a gif #############################
        
        for r in tqdm(R):
            self.params.r = r
        
            Pwem_params    = pwem_params(self.app, self.params)
            Pwem_params.N_Points = self.app.beta_pt_num # overwrite number of Beta vectors to match 2nd tab
            Pwem_params.BC = 1
            Pwem_params.Symmetry(self.params);
            
            if self.app.sel_anisotropy == 'No':
                if self.app.device_selection == 'Square':
                    self.Device.Ellipse(self.params)
                elif self.app.device_selection == 'Frame':
                    self.Device.Frame(self.params)
                elif self.app.device_selection == 'Ring':
                    self.Device.Ring(self.params)
                elif self.app.device_selection == 'Hex':
                    self.Device.oblique(self.params, Pwem_params.t1, Pwem_params.t2)
                elif self.app.device_selection == 'Honeycomb':
                    self.Device.honeycomb(self.params, Pwem_params.t1, Pwem_params.t2)
            else:
                if self.app.device_selection == 'Square':
                    self.Device.Ellipse_anisotropic(self.params)
                elif self.app.device_selection == 'Frame':
                    self.Device.Frame_anisotropic(self.params)
                elif self.app.device_selection == 'Ring':
                    self.Device.Ring_anisotropic(self.params)
                elif self.app.device_selection == 'Hex':
                    self.Device.oblique_anisotropic(self.params, Pwem_params.t1, Pwem_params.t2)
                elif self.app.device_selection == 'Honeycomb':
                    self.Device.honeycomb_anisotropic(self.params, Pwem_params.t1, Pwem_params.t2)

            #######################################################################
            
            if self.app.sel_anisotropy == 'No':
                for mode in ['E', 'H']:
                    if mode == 'E':
                        WE = PWEM_2D.calc_E_mode(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                                     self.app.device_selection, self.params.norm, 1)
                    else:
                        WH = PWEM_2D.calc_H_mode(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                                     self.app.device_selection, self.params.norm, 1)
            else:
                for mode in ['E', 'H']:
                    if mode == 'E':
                        WE = PWEM_2D.calc_E_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERCzz, self.Device.URC, self.Device.URC, 
                                                     self.app.device_selection, self.params.norm, 1)
                    else:
                        WH = PWEM_2D.calc_H_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     Pwem_params.beta[0,:], Pwem_params.beta[1,:], self.Device.ERCxx, self.Device.ERCyy, self.Device.URC,
                                                     self.app.device_selection, self.params.norm, 1)
            
            if self.app.sel_anisotropy == 'Yes': # not true, but need this to make a figure
                self.Device.ER = self.Device.ERxx
                
            if self.app.device_selection == 'Hex' or self.app.device_selection == 'Honeycomb':
                create_frame(t, self.app.device_selection, self.Device.ER, self.params, WH, WE, self.app.Bloch_mode_num, Pwem_params,
                             Pwem_params.KT, self.app.lower_freq_lim, self.app.upper_freq_lim, max([self.params.er1, self.params.er2]),
                             self.Device.X0, self.Device.Y0)
            else:
                create_frame(t, self.app.device_selection, self.Device.ER, self.params, WH, WE, self.app.Bloch_mode_num, Pwem_params,
                             Pwem_params.KT, self.app.lower_freq_lim, self.app.upper_freq_lim, max([self.params.er1, self.params.er2]))
            
            t = t + 1
            
        ################## make a gif #########################################
        
        frames = []
        for t in range(0, len(R)):
            image = imageio.v2.imread(f'./{name}/img_{t}.png')
            frames.append(image)
         
        imageio.mimsave('./bands.gif', # output gif
                        frames,           # array of input frames
                        fps = self.app.FPS_val,         # optional: frames per second
                        loop = 0)       # to make it loop
        
        shutil.rmtree(f'./{name}')        
            
        save_window = Toplevel()
        save_window.title('Gif has been saved')
        save_window.geometry('400x200')
        gif_place = tk.CTkLabel(master=save_window, text=f'Your gif is here: {os.getcwd()}', wraplength=300, justify='center')
        if self.app.background == 'Light':
            gif_place.configure(text_color='black')
        else:
            gif_place.configure(text_color='white')
            save_window.configure(bg='black')
        gif_place.pack(pady=20)
            