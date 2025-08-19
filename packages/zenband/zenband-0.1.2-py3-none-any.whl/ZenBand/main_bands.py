from .Device import device
from .Params import Params, pwem_params
from .PWEM_model_v2 import PWEM_2D
from .create_fig import plot_band_diagram, plot_device, Plot_Contours, Plot_Contours3D, Bands
from .Band_Gaps import Band_Gaps
import numpy as np

import customtkinter as tk
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

#######################################################################

class Main_Bands():
    
    def __init__(self, app, gaps=0):
        
        app.get_params()
        self.app = app
        
        params = Params(app);
        Device = device();
    
        Pwem_params    = pwem_params(app, params)
        if gaps == 1:
            Pwem_params.N_Points = self.app.beta_pt_num # overwrite number of Beta vectors to match 2nd tab
        Pwem_params.Symmetry(params);
        
        if app.sel_anisotropy == 'No':
            if app.device_selection == 'Square':
                Device.Ellipse(params)
            elif app.device_selection == 'Frame':
                Device.Frame(params)
            elif app.device_selection == 'Ring':
                Device.Ring(params)
            elif app.device_selection == 'Hex':
                Device.oblique(params, Pwem_params.t1, Pwem_params.t2)
            elif app.device_selection == 'Honeycomb':
                Device.honeycomb(params, Pwem_params.t1, Pwem_params.t2)
        else:
            if app.device_selection == 'Square':
                Device.Ellipse_anisotropic(params)
            elif app.device_selection == 'Frame':
                Device.Frame_anisotropic(params)
            elif app.device_selection == 'Ring':
                Device.Ring_anisotropic(params)
            elif app.device_selection == 'Hex':
                Device.oblique_anisotropic(params, Pwem_params.t1, Pwem_params.t2)
            elif app.device_selection == 'Honeycomb':
                Device.honeycomb_anisotropic(params, Pwem_params.t1, Pwem_params.t2)
         
        # self.anisotropy = app.sel_anisotropy
        if app.sel_import == 'Yes':
            app.sel_anisotropy = 'No'
            Device.imported_uc(params, app.imported_data)
            
        self.params = params
        self.Pwem_params = Pwem_params
        self.Device = Device
        
    def Band_diagram(self):
         
        #######################################################################
        if self.app.sel_anisotropy == 'Yes':
            for mode in ['E', 'H']:
                if mode == 'E':
                    WE = PWEM_2D.calc_E_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCzz, self.Device.URC, 
                                                 self.Device.URC, self.app.device_selection, self.params.norm)
                else:
                    WH = PWEM_2D.calc_H_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCxx, self.Device.ERCyy,
                                                 self.Device.URC, self.app.device_selection, self.params.norm)
        else:
            for mode in ['E', 'H']:
                if mode == 'E':
                    WE = PWEM_2D.calc_E_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                                 self.app.device_selection, self.params.norm)
                else:
                    WH = PWEM_2D.calc_H_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC,
                                                 self.app.device_selection, self.params.norm)

        fig = plot_band_diagram(self.app.device_selection, self.Device.ER, self.params, WH, WE, self.app.NBANDS, self.Pwem_params, 
                                self.Pwem_params.KT, self.app.omega_Lo, self.app.omega_Hi, self.app.FontSize, self.app.background,
                                self.app.sel_import)
        
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
    
    def Contours(self):
         
        #######################################################################
        if self.app.sel_anisotropy == 'Yes':
            # for mode in ['E', 'H']:
            if self.app.sel_mode == 'E':
                W = PWEM_2D.calc_E_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCzz, self.Device.URC, 
                                             self.Device.URC, self.app.device_selection, self.params.norm)
            else:
                W = PWEM_2D.calc_H_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCxx, self.Device.ERCyy,
                                             self.Device.URC, self.app.device_selection, self.params.norm)
        else:
            # for mode in ['E', 'H']:
            if self.app.sel_mode == 'E':
                W = PWEM_2D.calc_E_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                             self.app.device_selection, self.params.norm)
            else:
                W = PWEM_2D.calc_H_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC,
                                             self.app.device_selection, self.params.norm)
        
        """
        Plot Contours for each Bloch mode sheet. 
        Args are WH, WE, Bloch mode - 1, number of contours
        """
        self.params.Mode = self.app.sel_mode
        i = self.app.Bloch_Mo - 1
        if self.app.sel_import == 'No':
            fig = Plot_Contours(W, self.params, self.Pwem_params, self.app.background, self.app.FontSize, self.app.device_selection, self.app.sel_import, i,
                                self.app.Line_num, self.Pwem_params.X0, self.Pwem_params.Y0)
        else:
            fig = Plot_Contours(W, self.params, self.Pwem_params, self.app.background, self.app.FontSize, self.app.device_selection, self.app.sel_import, i,
                                self.app.Line_num, self.Device.X0, self.Device.Y0)     # need this for imported values
            
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
    
    def Contours3D(self):
         
        #######################################################################
        if self.app.sel_anisotropy == 'Yes':
            # for mode in ['E', 'H']:
            if self.app.sel_mode == 'E':
                W = PWEM_2D.calc_E_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCzz, self.Device.URC, 
                                             self.Device.URC, self.app.device_selection, self.params.norm)
            else:
                W = PWEM_2D.calc_H_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCxx, self.Device.ERCyy,
                                             self.Device.URC, self.device_selection, self.params.norm)
        else:
            # for mode in ['E', 'H']:
            if self.app.sel_mode == 'E':
                W = PWEM_2D.calc_E_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                             self.app.device_selection, self.params.norm)
            else:
                W = PWEM_2D.calc_H_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                             self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC,
                                             self.app.device_selection, self.params.norm)

        self.params.Mode = self.app.sel_mode
        i = self.app.Bloch_Mo - 1
        if self.app.sel_import == 'No':
            fig = Plot_Contours3D(W, self.params, self.Pwem_params, self.app.background, self.app.FontSize, self.app.device_selection, self.app.sel_import, i,
                                  self.app.Line_num, self.Pwem_params.X0, self.Pwem_params.Y0)
        else:
            fig = Plot_Contours3D(W, self.params, self.Pwem_params, self.app.background, self.app.FontSize, self.app.device_selection, self.app.sel_import, i,
                                self.app.Line_num, self.Device.X0, self.Device.Y0)     # need this for imported values
            
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

    
    def Plot_device(self):
        
        if self.app.sel_import == 'Yes':
            fig = plot_device(self.app.device_selection, self.params, self.Device.ER, np.max([self.params.er1, self.params.er2]),\
                              self.app.FontSize, self.app.background, 1, self.Device.X0, self.Device.Y0)
        else:
            if self.app.sel_anisotropy == 'Yes':
                self.Device.ER = self.Device.ERxx
                
            if self.app.device_selection == 'Square' or self.app.device_selection == 'Frame' or self.app.device_selection == 'Ring':
                fig = plot_device(self.app.device_selection, self.params, self.Device.ER, np.max([self.params.er1, self.params.er2]),\
                                  self.app.FontSize, self.app.background, 0)
            else:
                fig = plot_device(self.app.device_selection, self.params, self.Device.ER, np.max([self.params.er1, self.params.er2]),\
                                  self.app.FontSize, self.app.background, 0, self.Device.X0, self.Device.Y0)
                    
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

    
    def Gaps(self):
        
        if self.app.sel_anisotropy == 'Yes':
            for mode in ['E', 'H']:
                if mode == 'E':
                    WE = PWEM_2D.calc_E_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCzz, self.Device.URC, 
                                                 self.Device.URC, self.app.device_selection, self.params.norm)
                else:
                    WH = PWEM_2D.calc_H_mode_anisotropic(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERCxx, self.Device.ERCyy,
                                                 self.Device.URC, self.app.device_selection, self.params.norm)
        else:
            for mode in ['E', 'H']:
                if mode == 'E':
                    WE = PWEM_2D.calc_E_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC, 
                                                 self.app.device_selection, self.params.norm)
                else:
                    WH = PWEM_2D.calc_H_mode(self.params.Harmonics[0], self.params.Harmonics[1], self.Pwem_params.T1, self.Pwem_params.T2, 
                                                 self.Pwem_params.beta[0,:], self.Pwem_params.beta[1,:], self.Device.ERC, self.Device.URC,
                                                 self.app.device_selection, self.params.norm)
            
        gap_E, gap_E_min, gap_E_max = Band_Gaps.find_gaps(WE, self.app.Bloch_mode_num)
        gap_H, gap_H_min, gap_H_max = Band_Gaps.find_gaps(WH, self.app.Bloch_mode_num)
        gap_CPBG, CPBG_min, CPBG_max = Band_Gaps.complete_BGs(gap_E_min, gap_E_max, gap_H_min, gap_H_max)
        
        gap_window = Toplevel()
        gap_output = tk.CTkTextbox(gap_window, width = 400)
        gap_output.grid(row = 1, column = 1)
        
        for mode in ['E', 'H']:
            if mode == 'E':
                gap_output.insert('end', 'Gaps for E mode:\n')
                for gap in range(len(gap_E)):
                    if gap_E[gap] != 0:
                        gap_output.insert('end', r'gap ({lo}-{up}), width = {ga}, '.format(up = gap+2, lo = gap+1, ga = round(gap_E[gap], 3)))
                        gap_output.insert('end', r'gap span: {lo} - {hi}'.format(lo = round(gap_E_min[gap], 3), hi = round(gap_E_max[gap], 3)))
                        gap_output.insert('end', '\n')
            else:
                gap_output.insert('end', 'Gaps for H mode:\n')
                for gap in range(len(gap_H)):
                    if gap_H[gap] != 0:
                        gap_output.insert('end', r'gap ({lo}-{up}), width = {ga}, '.format(up = gap+2, lo = gap+1, ga = round(gap_H[gap], 3)))
                        gap_output.insert('end', r'gap span: {lo} - {hi}'.format(lo = round(gap_H_min[gap], 3), hi = round(gap_H_max[gap], 3)))
                        gap_output.insert('end', '\n')
                        
        if len(gap_CPBG) != 0:
            gap_output.insert('end', 'Complete photonic band gap:\n')
            for gap in range(len(gap_CPBG)):
                gap_output.insert('end', r'width = {ga}, '.format(ga = round(gap_CPBG[gap], 3)))
                gap_output.insert('end', r'gap span: {lo} - {hi}'.format(lo = round(CPBG_min[gap], 3), hi = round(CPBG_max[gap], 3)))
                gap_output.insert('end', '\n')
               
        fig = Bands(self.app.device_selection, self.params, WH, WE, self.app.no_of_bands, self.Pwem_params, self.Pwem_params.KT, self.app.lower_freq_lim, 
                    self.app.upper_freq_lim, CPBG_min, CPBG_max, gap_E_min, gap_H_min, gap_E_max, gap_H_max, gap_E, gap_H, self.app.background, 
                    font_size=self.app.FontSize)
        
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
        