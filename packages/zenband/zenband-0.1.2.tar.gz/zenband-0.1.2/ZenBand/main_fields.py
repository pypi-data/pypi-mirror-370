from .Device import device
from .Params import Params, pwem_params
from .PWEM_model_fields import calc_E_mode_field, calc_E_mode_H_field, calc_H_mode_field, calc_H_mode_E_field,\
                   calc_E_mode_field_anisotropic, calc_E_mode_H_field_anisotropic, calc_H_mode_field_anisotropic,\
                   calc_H_mode_E_field_anisotropic, field
from .create_fig import gif_field, single_field

import customtkinter as tk
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from tqdm import tqdm
import imageio
import os
import shutil

#######################################################################
class Fields():
    def __init__(self, app):
        
        app.get_params()
        self.app = app
        
        self.params = Params(app);
        self.Device = device();        

    def field_view(self):
        # define lattice and beta (Bloch wave) vectors 
        Pwem_params    = pwem_params(self.app, self.params)
        Pwem_params.Symmetry(self.params);
        
        # calculate device's unit cell grid
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
        
        # use imported device    
        if self.app.sel_import == 'Yes':
            self.app.sel_anisotropy = 'No'
            self.Device.imported_uc(self.params, self.app.imported_data)
        
        ####################### fields ########################################
        
        # define beta vector and Bloch mode of interest
        beta_x = self.app.beta_x_val * np.pi /self.params.Lx
        beta_y = self.app.beta_y_val * np.pi /self.params.Ly
    
        
        # get eigen vectors
        if self.app.sel_anisotropy == 'No':
            if self.app.sel_mode == 'E':
                if self.app.field_comp == 'z':
                    V, m, WE = calc_E_mode_field(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERC, self.Device.URC, self.params.norm, self.app.Bloch_mode_no)
                else:
                    V, m, WE = calc_E_mode_H_field(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERC, self.Device.URC, self.params.norm, self.app.Bloch_mode_no,
                                                 self.app.field_comp)
            elif self.app.sel_mode == 'H': 
                if self.app.field_comp == 'z':
                    V, m, WE = calc_H_mode_field(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERC, self.Device.URC, self.params.norm, self.app.Bloch_mode_no)
                else:
                    V, m, WE = calc_H_mode_E_field(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERC, self.Device.URC, self.params.norm, self.app.Bloch_mode_no,
                                                 self.app.field_comp)
                    
        else:
            if self.app.sel_mode == 'E': 
                if self.app.field_comp == 'z':
                    V, m, WE = calc_E_mode_field_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERCzz, self.Device.URC, self.Device.URC, self.params.norm,
                                                 self.app.Bloch_mode_no)
                else:
                    V, m, WE = calc_E_mode_H_field_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERCzz, self.Device.URC, self.Device.URC, self.params.norm, 
                                                 self.app.Bloch_mode_no, self.app.field_comp)
            elif self.app.sel_mode == 'H': 
                if self.app.field_comp == 'z':
                    V, m, WE = calc_H_mode_field_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERCxx, self.Device.ERCyy, self.Device.URC, self.params.norm,
                                                 self.app.Bloch_mode_no)
                else:
                    V, m, WE = calc_H_mode_E_field_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                 beta_x, beta_y, self.Device.ERCxx, self.Device.ERCyy, self.Device.URC, self.params.norm,
                                                 self.app.Bloch_mode_no, self.app.field_comp)
                
        if self.app.sel_anisotropy == 'Yes':
            self.Device.ER = self.Device.ERxx # not true, but need to draw field
        
        # change params if device is imported
        if self.app.sel_import == 'Yes':
            a = field(V, self.params.Harmonics[0], self.params.Harmonics[1], m, np.shape(self.Device.ER)[1], np.shape(self.Device.ER)[0], 
                      self.Device.ER, self.params.x, self.params.y)
        else:
            a = field(V, self.params.Harmonics[0], self.params.Harmonics[1], m, self.params.dim[0], self.params.dim[1],
                      self.Device.ER, self.params.x, self.params.y) 
        
        if self.app.sel_import == 'Yes':
            # if np.min(self.Device.X0) != 0:
            #     field_fig = single_field(self.app.background, self.app.device_selection, self.Device.ER, self.app.Bloch_mode_no, self.params, 
            #                              WE, a, beta_x, beta_y, self.app.phase, self.app.sel_import, self.app.sel_field, self.app.FontSize, self.Device.X0, self.Device.Y0)
            # else:
            field_fig = single_field(self.app.background, self.app.device_selection, self.Device.ER, self.app.Bloch_mode_no, self.params, 
                                     WE, a, beta_x, beta_y, self.app.phase, self.app.sel_import, self.app.sel_field, self.app.FontSize, self.Device.X0, self.Device.Y0)
        else: 
            if self.app.device_selection == 'Square' or self.app.device_selection == 'Frame' or self.app.device_selection == 'Ring':
                field_fig = single_field(self.app.background, self.app.device_selection, self.Device.ER, self.app.Bloch_mode_no, self.params,
                                         WE, a, beta_x, beta_y, self.app.phase, self.app.sel_import, self.app.sel_field, self.app.FontSize)
            else:
                field_fig = single_field(self.app.background, self.app.device_selection, self.Device.ER, self.app.Bloch_mode_no, self.params, 
                                         WE, a, beta_x, beta_y, self.app.phase, self.app.sel_import, self.app.sel_field, self.app.FontSize,
                                         self.Device.X0, self.Device.Y0)
                
        plot_window = Toplevel()
        
        canvas = FigureCanvasTkAgg(field_fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar
        color = "#505050"
 
        toolbar = NavigationToolbar2Tk(canvas, plot_window)
        toolbar.config(background=color)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM)
    
    
    def Field_gif(self):
            
            t = 0
            
            name = 'field_img'               # make a folder for gif images
            if not os.path.exists('./field_img'):
                os.mkdir(name)
            
            self.app.NBETA = self.app.Frame_num # need this to get wanted amount of frames (beta_x length = no. of frames)
            Pwem_params    = pwem_params(self.app, self.params)
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
                
            if self.app.sel_import == 'Yes':
                self.app.sel_anisotropy = 'No'
                self.Device.imported_uc(self.params, self.app.imported_data)
            
            ########################### create beta vector arrays #########################
            
            beta_x = Pwem_params.beta[0,:]
            beta_y = Pwem_params.beta[1,:]
            W = np.empty((self.params.Harmonics[0]*self.params.Harmonics[1], len(beta_x)))
            
            ###############################################################################
            
            for i in tqdm(range(len(beta_x))):
                
                if self.app.sel_anisotropy == 'No':
                    if self.app.sel_mode == 'E':
                        V, m, WE = calc_E_mode_field(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     beta_x[i], beta_y[i], self.Device.ERC, self.Device.URC, self.params.norm, self.app.Bloch_mode_no)                         
                    elif self.app.sel_mode == 'H': 
                        V, m, WE = calc_H_mode_field(self.params.Harmonics[0], self.params.Harmonics[1], Pwem_params.T1, Pwem_params.T2, 
                                                     beta_x[i], beta_y[i], self.Device.ERC, self.Device.URC, self.params.norm, self.app.Bloch_mode_no)
                        
                if self.app.sel_anisotropy == 'Yes':
                    self.Device.ER = self.Device.ERxx # not true, but need for field
                    
                # change params if device is imported
                if self.app.sel_import == "Yes":
                    self.params.x = np.linspace(-self.params.Lx/2, self.params.Lx/2, np.shape(self.Device.ER)[1])
                    self.params.y = np.linspace(-self.params.Lx/2, self.params.Lx/2, np.shape(self.Device.ER)[0])
                    a = field(V, self.params.Harmonics[0], self.params.Harmonics[1], m, np.shape(self.Device.ER)[1], np.shape(self.Device.ER)[0], 
                              self.Device.ER)
                else:
                    a = field(V, self.params.Harmonics[0], self.params.Harmonics[1], m, self.params.dim[0], self.params.dim[1], self.Device.ER) 
                
                W[:,t] = WE
                
                if self.app.sel_import == 'No':
                    if self.app.device_selection == 'Square' or self.app.device_selection == 'Frame' or self.app.device_selection == 'Ring':        
                        gif_field(t, self.app.BC, self.Device.ER, self.app.Bloch_mode_no, self.params, W, 15, Pwem_params, 
                                     Pwem_params.KT, 0, 1, a) # create image for gif
                    else:
                        gif_field(t, self.app.BC, self.Device.ER, self.app.Bloch_mode_no, self.params, W, 15, Pwem_params, 
                                     Pwem_params.KT, 0, 1, a, self.Device.X0, self.Device.Y0)
                else:
                    gif_field(t, self.app.BC, self.Device.ER, self.app.Bloch_mode_no, self.params, W, 15, Pwem_params, 
                                 Pwem_params.KT, 0, 1, a, self.Device.X0, self.Device.Y0, import_dev=1)
                    
                t = t + 1 # iteration number
                    
            ########################## make a gif #########################################
                 
            frames = []
            for t in range(0, len(beta_x)):
                image = imageio.v2.imread(f'./{name}/img_{t}.png')
                frames.append(image)
             
            imageio.mimsave('./fields.gif', # output gif
                            frames,           # array of input frames
                            fps = self.app.FPS_val_beta,         # optional: frames per second
                            loop = 0)       # to make it loop
            
            shutil.rmtree(f'./{name}')    # delete images
            
            save_window = Toplevel()
            save_window.title('Gif has been saved')
            save_window.geometry('400x200')
            gif_place = tk.CTkLabel(master=save_window, text=f'Your gif is here: {os.getcwd()}', wraplength=300, justify='center')
            if self.app.background == 'Light':
                gif_place.configure(text_color='black')
                save_window.configure(bg='white')
            else:
                gif_place.configure(text_color='white')
                save_window.configure(bg='black')
            gif_place.pack(pady=20)
            
   