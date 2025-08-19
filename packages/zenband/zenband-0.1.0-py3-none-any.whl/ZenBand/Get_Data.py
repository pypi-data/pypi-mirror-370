from tkinter import messagebox
import csv

def save_params(app):
    filename = 'saved_params.csv' # save params in .csv file
    app.get_params()             # extract parameters

    params = [app.value_Lx, app.value_Ly, app.value_r, app.value_r2, app.value_ax, app.value_ay, app.eps1,
              app.eps2, app.P, app.Q, app.Nx, app.Ny, app.FontSize, app.device_selection, app.sel_mode,
              app.NBETA, app.NBANDS, app.omega_Lo, app.omega_Hi, app.Bloch_Mo, app.Line_num,
              app.Bloch_mode_num, app.no_of_bands, app.lower_freq_lim, app.upper_freq_lim, app.beta_pt_num,
              app.min_R_lim, app.max_R_lim, app.min_R2_lim, app.max_R2_lim, app.no_of_steps, app.FPS_val, app.Bloch_mode_no, app.Frame_num,
              app.FPS_val_beta, app.beta_x_val, app.beta_y_val, app.phase, app.sel_field, app.sel_anisotropy, app.sel_import,
              app.erxx1, app.eryy1, app.erzz1, app.erxx2, app.eryy2, app.erzz2]
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for item in params:
            writer.writerow([item])
            

def load_params(app):
    filename = 'saved_params.csv'
    params = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                params.append(row[0])
                
        app.entries["Lx"].delete(0, "end")
        app.entries['Lx'].insert(0, str(params[0]))    
        
        app.entries["Ly"].delete(0, "end")  
        app.entries['Ly'].insert(0, str(params[1]))  
        
        app.entries["r"].delete(0, "end")  
        app.entries['r'].insert(0, str(params[2]))  
        
        app.entries['r2'].delete(0, 'end')
        app.entries['r2'].insert(0, str(params[3]))
        
        app.entries["Ellipse_length"].delete(0, "end")  
        app.entries['Ellipse_length'].insert(0, str(params[4]))  
        
        app.entries["Ellipse_width"].delete(0, "end")  
        app.entries['Ellipse_width'].insert(0, str(params[5]))  
        
        app.entries["eps1"].delete(0, "end")  
        app.entries['eps1'].insert(0, str(params[6]))  
        
        app.entries["eps2"].delete(0, "end")  
        app.entries['eps2'].insert(0, str(params[7]))  
        
        app.entries["P"].delete(0, "end")  
        app.entries['P'].insert(0, str(params[8]))  
        
        app.entries["Q"].delete(0, "end")  
        app.entries['Q'].insert(0, str(params[9]))  
        
        app.entries["Nx"].delete(0, "end")  
        app.entries['Nx'].insert(0, str(params[10]))  
        
        app.entries["Ny"].delete(0, "end")  
        app.entries['Ny'].insert(0, str(params[11]))  
        
        app.entries["Fontsize"].delete(0, "end")  
        app.entries['Fontsize'].insert(0, str(params[12]))  
        
        app.select_device.set(str(params[13]))
        app.select_mode.set(str(params[14]))
        
        # --------------------------------------------------------------------
        """
        MID COLUMN Calc bands
        """
        
        app.entries["Enter N_beta"].delete(0, "end")
        app.entries['Enter N_beta'].insert(0, str(params[15])) 
        
        app.entries["Enter no. of bands"].delete(0, "end")
        app.entries['Enter no. of bands'].insert(0, str(params[16])) 
        
        app.entries["Lower omega limit"].delete(0, "end")
        app.entries['Lower omega limit'].insert(0, str(params[17])) 
        
        app.entries["Upper omega limit"].delete(0, "end")
        app.entries['Upper omega limit'].insert(0, str(params[18])) 
        
        app.entries["Bloch mode"].delete(0, "end")
        app.entries['Bloch mode'].insert(0, str(params[19])) 
        
        app.entries["No. of lines"].delete(0, "end")
        app.entries['No. of lines'].insert(0, str(params[20])) 
        
        """
        MID COLUMN Calc OBG
        """
        
        app.entries["no. of Bloch modes"].delete(0, "end")
        app.entries['no. of Bloch modes'].insert(0, str(params[21])) 
        
        app.entries["no. of bands"].delete(0, "end")
        app.entries['no. of bands'].insert(0, str(params[22])) 
        
        app.entries["Lower freq. limit"].delete(0, "end")
        app.entries['Lower freq. limit'].insert(0, str(params[23])) 
        
        app.entries["Upper freq. limit"].delete(0, "end")
        app.entries['Upper freq. limit'].insert(0, str(params[24])) 
        
        app.entries["Enter beta pt num"].delete(0, "end")
        app.entries['Enter beta pt num'].insert(0, str(params[25]))
        
        app.entries["min R"].delete(0, "end")
        app.entries['min R'].insert(0, str(params[26]))
        
        app.entries["max R"].delete(0, "end")
        app.entries['max R'].insert(0, str(params[27]))
        
        app.entries["min R2"].delete(0, "end")
        app.entries['min R2'].insert(0, str(params[28]))
        
        app.entries["max R2"].delete(0, "end")
        app.entries['max R2'].insert(0, str(params[29]))
        
        app.entries["No. of steps"].delete(0, "end")
        app.entries['No. of steps'].insert(0, str(params[30]))
        
        app.entries["FPS val"].delete(0, "end")
        app.entries["FPS val"].insert(0, str(params[31]))  
        
        # --------------------------------------------------------------------
        
        app.entries["Bloch mode no."].delete(0, "end")
        app.entries["Bloch mode no."].insert(0, str(params[32]))  
        
        app.entries["Frame Number"].delete(0, "end")
        app.entries["Frame Number"].insert(0, str(params[33]))  
        
        app.entries["FPS value"].delete(0, "end")
        app.entries["FPS value"].insert(0, str(params[34]))  
        
        app.entries["beta_x (*pi/a)"].delete(0, "end")
        app.entries["beta_x (*pi/a)"].insert(0, str(params[35]))  
        
        app.entries["beta_y (*pi/a)"].delete(0, "end")
        app.entries["beta_y (*pi/a)"].insert(0, str(params[36]))
        
        app.entries['Phase'].delete(0, 'end')
        app.entries['Phase'].insert(0, str(params[37]))
        
        app.select_field.set(str(params[38]))
        
        # --------------------------------------------------------------------
        
        app.select_mode_mat.set(str(params[39]))
        app.select_import.set(str(params[40]))
        
        # --------------------------------------------------------------------
        
        app.entries['eps1xx'].delete(0, 'end')
        app.entries['eps1xx'].insert(0, str(params[41]))
        
        app.entries['eps1yy'].delete(0, 'end')
        app.entries['eps1yy'].insert(0, str(params[42]))
        
        app.entries['eps1zz'].delete(0, 'end')
        app.entries['eps1zz'].insert(0, str(params[43]))
        
        app.entries['eps2xx'].delete(0, 'end')
        app.entries['eps2xx'].insert(0, str(params[44]))
        
        app.entries['eps2yy'].delete(0, 'end')
        app.entries['eps2yy'].insert(0, str(params[45]))
        
        app.entries['eps2zz'].delete(0, 'end')
        app.entries['eps2zz'].insert(0, str(params[46]))   

        
    except:
        messagebox.showerror('Error', 'No parameters are saved')
    pass
