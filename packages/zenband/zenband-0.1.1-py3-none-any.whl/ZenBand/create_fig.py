import matplotlib.pyplot as plt
import numpy as np

plt.rc('text', usetex=True)
plt.rc('font', family='serif')


"""
create_figs_for_an_app
"""

def plot_device(device_selection, params, ER, v_max, font_size, background, import_dev, X0 = 0, Y0 = 0):
    
    fig1, ax1 = plt.subplots(figsize = (5,5))
    
    if background == 'Dark':
        ax1.set_facecolor('black')
    
    if import_dev == 'Yes':
        if np.shape(X0) == np.shape(ER):
            img1 = ax1.pcolor(X0, Y0, ER, cmap = 'jet')
        else:
            img1 = ax1.imshow(np.real(ER), extent = [-params.Lx/2, params.Lx/2, -params.Ly/2, params.Ly/2],
                       aspect = 'auto',  cmap = 'jet', vmin=1, vmax=v_max)
    else:
        if device_selection == 'Square' or device_selection == 'Frame' or device_selection == 'Ring':
            img1 = ax1.imshow(np.real(ER), extent = [-params.Lx/2, params.Lx/2, -params.Ly/2, params.Ly/2],
                           aspect = 'auto',  cmap = 'jet', vmin=1, vmax=v_max)
        else:
            img1 = ax1.pcolor(X0, Y0, ER, cmap = 'jet')
    
    img1.set_rasterized(True)
            
######################################################################################################
    if background == 'Dark':
        fg_color = 'white'
        bg_color = 'black'
    else:
        fg_color = 'black'
        bg_color = 'white'
        
    ax1.set_xlabel(r'$x/a$, a.u.', fontsize=font_size, color = fg_color)
    ax1.set_ylabel(r'$y/a$, a.u.', fontsize=font_size, color = fg_color)
    if import_dev == 1:
        ax1.set_title(r'Device unit cell', fontsize=font_size, color = fg_color)
    else:
        ax1.set_title(r'Device unit cell', fontsize=font_size, color = fg_color)
       
    cb = plt.colorbar(img1, fraction=0.046, pad=0.04) # equalize colorbar size
    ax1.set_aspect('equal')
    
    # set tick and ticklabel color
    img1.axes.tick_params(color=fg_color, labelcolor=fg_color)
    """Maybe the code below can be fixed"""
    ax1.tick_params(axis='both', which='major', labelsize=font_size)
    ax1.tick_params(axis='both', which='minor', labelsize=font_size)
    
    
    # set imshow outline
    for spine in img1.axes.spines.values():
        spine.set_edgecolor(fg_color)    
    
    # COLORBAR
    # set colorbar label plus label color
    cb.set_label(r'$\varepsilon_r$', color=fg_color)
    
    # set colorbar tick color
    cb.ax.yaxis.set_tick_params(color=fg_color, labelsize = font_size)
    
    # set colorbar edgecolor 
    cb.outline.set_edgecolor(fg_color)
    
    # set colorbar ticklabels
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=fg_color)
    
    fig1.patch.set_facecolor(bg_color)
    
    plt.close()

    return fig1

def plot_band_diagram(BC, ER, params, WH, WE, k0_num, pwem_params, 
                 ticks, ymin, ylim, font_size, background, import_dev):
        
    if background == 'Light':
        fg_color = 'white'
        bg_color = 'black'
                
        E_mode_color_bck = 'red'
        H_mode_color_bck = 'blue'

    else:
        fg_color = 'black'
        bg_color = 'white'
        
        E_mode_color_bck = '#8E5B68'
        H_mode_color_bck = '#B7D0E1'
        
########################################## HANDLE X AXIS #############################################            
            
    beta = pwem_params.KP

    fig2, ax2 = plt.subplots(facecolor=fg_color,figsize = (7,5))
        
    for i in range(0,k0_num):
        ax2.plot(WH[i,:], H_mode_color_bck, linestyle = '-')
        ax2.plot(WE[i,:], E_mode_color_bck, linestyle = '--')
        
    for i in range(1,len(ticks) - 1):
        ax2.axvline(x =  ticks[i],   color = 'gray',ls='--')
      
######################################################################################################
    Ticks = ticks
    plt.xticks(Ticks, beta, fontsize=font_size, color = fg_color)
        
######################################################################################################
        
    ax2.text(ticks[-1] * 14/40, ymin+(ylim-ymin)/20, "H mode", 
             bbox=dict(facecolor=H_mode_color_bck, alpha=0.25), fontsize=font_size, color = bg_color)
    ax2.text(ticks[-1] * 21/40, ymin+(ylim-ymin)/20, "E mode", 
             bbox=dict(facecolor=E_mode_color_bck, alpha=0.25), fontsize=font_size, color = bg_color)
    
    
    ax2.set_xlim(0, ticks[-1])
    ax2.set_ylim(ymin, ylim)

    ax2.set_xlabel(r'$\vec{\beta}$', color = bg_color)
    ax2.set_ylabel(r'$a/\lambda_0$', color = bg_color)
    
    ax2.set_facecolor(fg_color)
    fig2.patch.set_facecolor(fg_color)

    
    """
    AXES VALUE COLOR
    """
    [t.set_color(bg_color) for t in ax2.xaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax2.xaxis.get_ticklabels()]
    [t.set_color(bg_color) for t in ax2.yaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax2.yaxis.get_ticklabels()]
    
    ax2.xaxis.set_tick_params(color=bg_color)
    ax2.yaxis.set_tick_params(color=bg_color)

    ax2.set_title(r'Band diagram', color = bg_color, fontsize=font_size) 
    
    fig2.patch.set_facecolor(fg_color)   
    
    """Maybe the code below can be fixed"""
    ax2.tick_params(axis='both', which='major', labelsize=font_size)
    ax2.tick_params(axis='both', which='minor', labelsize=font_size)
    
    if background:
        ax2.set_facecolor(fg_color)
        fig2.patch.set_facecolor(fg_color)
    
    # set imshow outline
    for spine in ax2.axes.spines.values():
        spine.set_edgecolor(bg_color)  
        
    plt.close()

    return fig2
    
"""
create_frame for gifs below
"""

def create_frame(t, device_selection, ER, params, WH, WE, k0_num, pwem_params, 
                 ticks, ymin, ylim, v_max, X0 = 0, Y0 = 0, font_size=16, plt_device_only = 1):
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 6), gridspec_kw={'width_ratios': [4, 5]})
    plt.subplots_adjust(wspace=0.2)
    
    # plot the unit cell
    
    if device_selection == 'Square' or device_selection == 'Frame' or device_selection == 'Ring':
        img1 = ax1.imshow(np.real(ER), extent = [-params.Lx/2, params.Lx/2, -params.Ly/2, params.Ly/2],
                       aspect = 'auto',  cmap = 'jet', vmin=1, vmax=v_max)
    else:
        img1 = ax1.pcolor(X0, Y0, ER, cmap = 'jet', rasterized=True)
        
######################################################################################################
        
    ax1.set_xlabel('$x$, a.u.')
    ax1.set_ylabel('$y$, a.u.')
    ax1.set_title(r'$r = {}a$'.format(f'{params.r:.3f}'))
    ax1.set_aspect('equal')
    plt.colorbar(img1, ax=ax1)
   
###################################################################################################### 

    '''
    Plot band diagram
    '''
        
########################################## HANDLE X AXIS #############################################            
    
    if device_selection == 'Square' or device_selection == 'Frame' or device_selection == 'Ring':
        beta  = ["$\Gamma$", "$X$", "$M$", "$\Gamma$"]
    else:
        beta  = ["$\Gamma$", "$M$", "$K$", "$\Gamma$"]
            
######################################################################################################

    for i in range(0,k0_num):
        ax2.plot(WH[i,:], 'blue')
        ax2.plot(WE[i,:], 'r--')
        
    for i in range(1,len(ticks) - 1):
        ax2.axvline(x =  ticks[i],   color = 'gray',ls='--')
      
######################################################################################################
        
    Ticks = ticks
    plt.xticks(Ticks,beta)
        
######################################################################################################
        
    ax2.text(ticks[-1] * 15/40, ymin+(ylim-ymin)/20, "H mode", bbox=dict(facecolor='blue', alpha=0.25), fontsize=font_size)
    ax2.text(ticks[-1] * 21/40, ymin+(ylim-ymin)/20, "E mode", bbox=dict(facecolor='red', alpha=0.25), fontsize=font_size)
    
    ax2.set_xlim(0, ticks[-1])
    ax2.set_ylim(ymin, ylim)

    ax2.set_xlabel(r'$\vec{\beta}$')
    ax2.set_ylabel(r'$a/\lambda_0$')
       
    ax2.set_title(r'Band Diagram')
 
    plt.savefig(f'./img_er{params.er1}/img_{t}.png', bbox_inches='tight', dpi = 200)
    
    plt.close()
    
def Bands(BC, params, WH, WE, k0_num, pwem_params, ticks, ymin, ylim, BG_min, BG_max, omega_min_E,
          omega_min_H, omega_max_E, omega_max_H, gap_E, gap_H, background, font_size=24):
    
    if background == 'Light':
        fg_color = 'white'
        bg_color = 'black'
                
        E_mode_color_bck = 'red'
        H_mode_color_bck = 'blue'
        
    else:
        fg_color = 'black'
        bg_color = 'white'
        
        E_mode_color_bck = '#8E5B68'
        H_mode_color_bck = '#B7D0E1'
        
    fig = plt.figure(facecolor = fg_color, figsize = (7, 5))
    ax = fig.add_subplot()
    
    colors_e = ['#440a02', '#881405', '#cd1f08', '#f53f27', '#f87c6c', '#fa9a8e']
    colors_h = ['#08203f', '#10407e', '#1860bd', '#3883e5', '#77abed', '#97bef1']
        
########################################## HANDLE X AXIS #############################################            
    
    beta = pwem_params.KP
            
    ######################################################################################################
    
    for i in range(0,k0_num):
        ax.plot(WH[i,:], H_mode_color_bck, linestyle = '-')
        ax.plot(WE[i,:], E_mode_color_bck, linestyle = '--')
        
    for i in range(1,len(ticks) - 1):
        ax.axvline(x =  ticks[i],   color = 'gray', ls='--')

    for n in range(len(omega_min_E)):
        if gap_E[n] > 0.01:
            ax.fill_between([0, ticks[-1]], omega_min_E[n], omega_max_E[n], color = colors_e[n % 6], alpha = 0.5)
    for n in range(len(omega_min_H)):
        if gap_H[n] > 0.01:
            ax.fill_between([0, ticks[-1]], omega_min_H[n], omega_max_H[n], color = colors_h[n % 6], alpha = 0.5)
            
    for i in range(len(BG_min)):
        ax.fill_between([0, ticks[-1]], BG_min[i], BG_max[i], color = 'white')
        ax.fill_between([0, ticks[-1]], BG_min[i], BG_max[i], color = 'yellow', alpha = 0.5)
      
    ######################################################################################################
        
    Ticks = ticks
    plt.xticks(Ticks,beta, fontsize = font_size, color = fg_color)
    plt.yticks(fontsize = font_size)
        
    ######################################################################################################
        
    ax.text(ticks[-1] * 14/40, ymin+(ylim-ymin)/20, "H mode", 
             bbox=dict(facecolor=H_mode_color_bck, alpha=0.25), fontsize=font_size, color = bg_color)
    ax.text(ticks[-1] * 21/40, ymin+(ylim-ymin)/20, "E mode", 
             bbox=dict(facecolor=E_mode_color_bck, alpha=0.25), fontsize=font_size, color = bg_color)
    
    ax.set_xlim(0, ticks[-1])
    ax.set_ylim(ymin, ylim)
    
    ax.set_xlabel(r'$\vec{\beta}$', fontsize = font_size, color = bg_color)
    ax.set_ylabel(r'$a/\lambda_0$', fontsize = font_size, color = bg_color)
    
    """
    AXES VALUE COLOR
    """
    [t.set_color(bg_color) for t in ax.xaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax.xaxis.get_ticklabels()]
    [t.set_color(bg_color) for t in ax.yaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax.yaxis.get_ticklabels()]
    
    ax.xaxis.set_tick_params(color=bg_color)
    ax.yaxis.set_tick_params(color=bg_color)
       
    ax.set_title(r'Band gap diagram', fontsize = font_size, color = bg_color)   
    
    fig.patch.set_facecolor(fg_color)   
    
    """Maybe the code below can be fixed"""
    ax.tick_params(axis='both', which='major', labelsize=font_size)
    ax.tick_params(axis='both', which='minor', labelsize=font_size)
    
    if background:
        ax.set_facecolor(fg_color)
        fig.patch.set_facecolor(fg_color)
    
    # set imshow outline
    for spine in ax.axes.spines.values():
        spine.set_edgecolor(bg_color)
        
    plt.close()
    
    return fig
    
def Plot_Contours(W, params, pwem_params, background, font_size, device_selection, import_dev, m = 1, lines = 10, P=0, Q=0):
    
    if background == 'Light':
        fg_color = 'white'
        bg_color = 'black'
    else:
        fg_color = 'black'
        bg_color = 'white'
     
######################################################################################################
        
    maks = max(W[m,:])
    minimum = min(W[m,:])

    Harmonic = int(params.Harmonics[0] * params.Harmonics[1])
    sheet    = np.zeros((pwem_params.N_Points, pwem_params.N_Points, Harmonic))
    for i in range(0, Harmonic):
        sheet[:,:,i] = np.reshape(W[i,:], (pwem_params.N_Points, pwem_params.N_Points))
        
######################################################################################################
    if import_dev == 'No':
        x    = np.linspace(-np.pi/params.Lx,  np.pi/params.Lx, pwem_params.N_Points)
        y    = np.linspace( np.pi/params.Ly, -np.pi/params.Ly, pwem_params.N_Points)
    else:
        x    = np.linspace(min(pwem_params.beta[0,:]), max(pwem_params.beta[0,:]), pwem_params.N_Points)
        y    = np.linspace(max(pwem_params.beta[1,:]), min(pwem_params.beta[1,:]), pwem_params.N_Points)

    x, y = np.meshgrid(x,y)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    if import_dev == 'Yes':
        grad = ax.imshow(sheet[:,:,m], extent=[np.min(x), np.max(x), np.min(y), np.max(y)],
                         origin='lower', cmap='jet', alpha=0.3, aspect='equal')
        
        contours = ax.contour(x, y, sheet[:,:,m], lines, colors='black')
        ax.clabel(contours, inline=True, fontsize=8)

    elif device_selection == 'Hex' or device_selection == 'Honeycomb':
        grad = ax.imshow(sheet[:,:,m], extent=[np.min(P), np.max(P), np.min(Q), np.max(Q)], origin='lower',
                   cmap='jet', alpha=0.3, aspect='equal')

        contours = ax.contour(P, Q, sheet[:,:,m], lines, colors='black')
        ax.clabel(contours, inline=True, fontsize=8)
        
        # add lines to distinguish hexagon
        if device_selection == 'Hex':
            x_line = np.array([-4*np.pi/3, 4*np.pi/3])
            y1_line =  x_line*np.sqrt(3) + params.Lx/2 * 8 * np.sqrt(3) * np.pi/3
            y2_line =  x_line*np.sqrt(3) - params.Lx/2 * 8 * np.sqrt(3) * np.pi/3
            y3_line = -x_line*np.sqrt(3) + params.Lx/2 * 8 * np.sqrt(3) * np.pi/3
            y4_line = -x_line*np.sqrt(3) - params.Lx/2 * 8 * np.sqrt(3) * np.pi/3
            ax.plot(x_line, y1_line, color='black', linewidth=2.5)
            ax.plot(x_line, y2_line, color='black', linewidth=2.5)
            ax.plot(x_line, y3_line, color='black', linewidth=2.5)
            ax.plot(x_line, y4_line, color='black', linewidth=2.5)
        if device_selection == 'Honeycomb':
            x_line = np.array([-4/3/np.sqrt(3)*np.pi, 4/3/np.sqrt(3)*np.pi])
            y1_line =  x_line*np.sqrt(3) + params.Lx/2 * 2 * 4 * np.pi/3
            y2_line =  x_line*np.sqrt(3) - params.Lx/2 * 2 * 4 * np.pi/3
            y3_line = -x_line*np.sqrt(3) + params.Lx/2 * 2 * 4 * np.pi/3
            y4_line = -x_line*np.sqrt(3) - params.Lx/2 * 2 * 4 * np.pi/3
            ax.plot(x_line, y1_line, color='black', linewidth=2.5)
            ax.plot(x_line, y2_line, color='black', linewidth=2.5)
            ax.plot(x_line, y3_line, color='black', linewidth=2.5)
            ax.plot(x_line, y4_line, color='black', linewidth=2.5)
    else:
        grad = ax.imshow(sheet[:,:,m], extent=[np.min(x), np.max(x), np.min(y), np.max(y)], origin='lower',
                   cmap='jet', alpha=0.3) # cmap RdGy or jet
        
        contours = ax.contour(x, y, sheet[:,:,m], lines, colors='black')
        ax.clabel(contours, inline=True, fontsize=8)
        
    cbar = fig.colorbar(grad, shrink = 0.7);
    ticks = []
    for i in np.linspace(minimum, maks, 5):
        ticks.append(float(('{:.3f}'.format(i))))
    cbar.set_ticks(ticks)
        
######################################################################################################
    
    if import_dev == 'Yes':
        pass
    elif params.Lx != 1 or params.Ly != 1:
        pass
    elif device_selection == 'Square' or device_selection == 'Frame' or device_selection == 'Ring':
        ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi],
                   [r'$-\pi$',r'$-\frac{\pi}{2}$','0',r'$\frac{\pi}{2}$', r'$\pi$'])
    
        ax.set_yticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi],
                   [r'$-\pi$',r'$-\frac{\pi}{2}$','0',r'$\frac{\pi}{2}$', r'$\pi$'])
        # pass
    elif device_selection == 'Hex':
        ax.set_xticks([-4/3*np.pi, -2*np.pi/3, 0, 2/3*np.pi, 4/3*np.pi],
                   [r'$-\frac{4\pi}{3}$',r'$-\frac{2\pi}{3}$','0',r'$\frac{2\pi}{3}$', r'$\frac{4\pi}{3}$'])
    
        ax.set_yticks([-np.pi*2/np.sqrt(3), -np.pi/np.sqrt(3), 0, np.pi/np.sqrt(3), np.pi*2/np.sqrt(3)],
                   [r'$-\frac{2\pi}{\sqrt{3}}$',r'$-\frac{\pi}{\sqrt{3}}$','0',r'$\frac{\pi}{\sqrt{3}}$', r'$\frac{2\pi}{\sqrt{3}}$'])
        ax.set_ylim([-np.pi*2/np.sqrt(3), np.pi*2/np.sqrt(3)])
    elif device_selection == 'Honeycomb':
        ax.set_xticks([-4/3/np.sqrt(3)*np.pi, -2*np.pi/np.sqrt(3)/3, 0, 2/np.sqrt(3)/3*np.pi, 4/3/np.sqrt(3)*np.pi],
                   [r'$-\frac{4\pi}{3\sqrt{3}}$',r'$-\frac{2\pi}{3\sqrt{3}}$','0',r'$\frac{2\pi}{3\sqrt{3}}$', r'$\frac{4\pi}{3\sqrt{3}}$'])
    
        ax.set_yticks([-np.pi*2/3, -np.pi/3, 0, np.pi/3, np.pi*2/3],
                   [r'$-\frac{2\pi}{3}$',r'$-\frac{\pi}{3}$','0',r'$\frac{\pi}{3}$', r'$\frac{2\pi}{3}$'])
        ax.set_ylim([-np.pi*2/3, np.pi*2/3])
    
    ax.set_xlabel(r'$\beta_x\Lambda_x$, rad', color=bg_color)
    ax.set_ylabel(r'$\beta_y\Lambda_y$, rad', color=bg_color)
    
    if   m == 1:
        ax.set_title('${}$nd Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    elif m == 0:
        ax.set_title('${}$st Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    elif m == 2:
        ax.set_title('${}$rd Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    else:
        ax.set_title('${}$th Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
       
    ax.set_aspect('equal')
            
    """
    AXES VALUE COLOR
    """
    [t.set_color(bg_color) for t in ax.xaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax.xaxis.get_ticklabels()]
    [t.set_color(bg_color) for t in ax.yaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax.yaxis.get_ticklabels()]
    
    ax.xaxis.set_tick_params(color=bg_color)
    ax.yaxis.set_tick_params(color=bg_color)  
    
    fig.patch.set_facecolor(fg_color)  
        
    if background:
        fig.patch.set_facecolor(fg_color)
    
    # set imshow outline
    for spine in ax.axes.spines.values():
        spine.set_edgecolor(bg_color) 
        
    # COLORBAR
    # set colorbar label plus label color
    cbar.set_label(r'$a/\lambda_0$', color=bg_color)
    
    # set colorbar tick color
    cbar.ax.yaxis.set_tick_params(color=bg_color, labelsize = font_size)
    
    # set colorbar edgecolor 
    cbar.outline.set_edgecolor(bg_color)
    
    # set colorbar ticklabels
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=bg_color)
    
    plt.close()
    
    return fig
   
def Plot_Contours3D(W, params, pwem_params, background, font_size, device_selection, import_dev, m = 1, lines = 10, P=0, Q=0):
    
    if background == 'Light':
        fg_color = 'white'
        bg_color = 'black'
    else:
        fg_color = 'black'
        bg_color = 'white'
     
    #####################################################################################################
    
    maks = max(W[m,:])
            
    Harmonic = int(params.Harmonics[0] * params.Harmonics[1])
    sheet    = np.zeros((pwem_params.N_Points, pwem_params.N_Points, Harmonic))
    for i in range(0, Harmonic):
        sheet[:,:,i] = np.reshape(W[i,:], (pwem_params.N_Points, pwem_params.N_Points))
        
    ######################################################################################################

    if import_dev == 'Yes':
        x    = np.linspace(min(pwem_params.beta[0,:]), max(pwem_params.beta[0,:]), pwem_params.N_Points)
        y    = np.linspace(max(pwem_params.beta[1,:]), min(pwem_params.beta[1,:]), pwem_params.N_Points)
            
    elif device_selection == 'Square' or device_selection == 'Frame' or device_selection == 'Ring':
        x    = np.linspace(-np.pi/params.Lx,  np.pi/params.Lx, pwem_params.N_Points)
        y    = np.linspace( np.pi/params.Ly, -np.pi/params.Ly, pwem_params.N_Points)
    elif device_selection == 'Hex':
        x    = np.linspace(-4/3*np.pi,  4/3*np.pi, pwem_params.N_Points)
        y    = np.linspace( np.pi*2/np.sqrt(3), -np.pi*2/np.sqrt(3), pwem_params.N_Points)
    elif device_selection == 'Honeycomb':
        x    = np.linspace(-4/3/np.sqrt(3)*np.pi,  4/3/np.sqrt(3)*np.pi, pwem_params.N_Points)
        y    = np.linspace( np.pi*2/3, -np.pi*2/3, pwem_params.N_Points)
            
    x, y = np.meshgrid(x,y)

    ######################################################################################################
    
    # fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(10, 10))
    fig = plt.Figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')
        
    # m, lines = m, lines
    
    ax.view_init(20, -30)
    
    ######################################################################################################
    
    surf = ax.plot_surface(x, y, sheet[:,:,m], cmap="jet", alpha  = 0.5)
    cp   = ax.contour(x, y, sheet[:,:,m], lines, cmap="jet", offset = 0)
    
    ######################################################################################################
    
    ax.clabel(cp, inline=True, 
              fontsize=18, offset = 0)
    ax.set_zlim(0, maks)
    ax.set_xlim(min(x[0,:]), max(x[0,:]))
    ax.set_ylim(min(y[:,0]), max(y[:,0]))
    
    #####################################################################################################
    
    ax.set_xlabel(r'$\beta_x\Lambda_x$', color=bg_color)
    ax.set_ylabel(r'$\beta_y\Lambda_y$', color=bg_color)
    ax.set_zlabel(r'$a/\lambda_0$', color=bg_color)
    
    if import_dev == 'Yes':
        pass
    elif params.Lx != 1 or params.Ly != 1:
        pass    
    elif device_selection == 'Square' or device_selection == 'Frame' or device_selection == 'Ring':
        ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi],
                   [r'$-\pi$',r'$-\frac{\pi}{2}$','0',r'$\frac{\pi}{2}$', r'$\pi$'])
    
        ax.set_yticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi],
                   [r'$-\pi$',r'$-\frac{\pi}{2}$','0',r'$\frac{\pi}{2}$', r'$\pi$'])
        
    elif device_selection == 'Hex':
        ax.set_xticks([-4/3*np.pi, -2*np.pi/3, 0, 2/3*np.pi, 4/3*np.pi],
                   [r'$-\frac{4\pi}{3}$',r'$-\frac{2\pi}{3}$','0',r'$\frac{2\pi}{3}$', r'$\frac{4\pi}{3}$'])
    
        ax.set_yticks([-np.pi*2/np.sqrt(3), -np.pi/np.sqrt(3), 0, np.pi/np.sqrt(3), np.pi*2/np.sqrt(3)],
                   [r'$-\frac{2\pi}{\sqrt{3}}$',r'$-\frac{\pi}{\sqrt{3}}$','0',r'$\frac{\pi}{\sqrt{3}}$', r'$\frac{2\pi}{\sqrt{3}}$'])
        
    elif device_selection == 'Honeycomb':
        ax.set_xticks([-4/3/np.sqrt(3)*np.pi, -2*np.pi/np.sqrt(3)/3, 0, 2/np.sqrt(3)/3*np.pi, 4/3/np.sqrt(3)*np.pi],
                   [r'$-\frac{4\pi}{3\sqrt{3}}$',r'$-\frac{2\pi}{3\sqrt{3}}$','0',r'$\frac{2\pi}{3\sqrt{3}}$', r'$\frac{4\pi}{3\sqrt{3}}$'])
        ax.set_xlim([-4/3/np.sqrt(3)*np.pi, 4/3/np.sqrt(3)*np.pi])
    
        ax.set_yticks([-np.pi*2/3, -np.pi/3, 0, np.pi/3, np.pi*2/3],
                   [r'$-\frac{2\pi}{3}$',r'$-\frac{\pi}{3}$','0',r'$\frac{\pi}{3}$', r'$\frac{2\pi}{3}$'])
        ax.set_ylim([-np.pi*2/3, np.pi*2/3])
        
    ######################################################################################################
    
    ax.set_aspect("auto")
    cbar = fig.colorbar(surf, pad = 0.05, shrink=0.5, aspect=20, orientation = 'horizontal')
    
    ######################################################################################################
    
    if   m == 1:
        ax.set_title('${}$nd Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    elif m == 0:
        ax.set_title('${}$st Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    elif m == 2:
        ax.set_title('${}$rd Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    else:
        ax.set_title('${}$th Bloch mode, ${}$ $mode$'.format(m+1, params.Mode), color = bg_color)
    
######################################################################################################
            
    """
    AXES VALUE COLOR
    """
    [t.set_color(bg_color) for t in ax.xaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax.xaxis.get_ticklabels()]
    [t.set_color(bg_color) for t in ax.yaxis.get_ticklines()]
    [t.set_color(bg_color) for t in ax.yaxis.get_ticklabels()]
    
    ax.xaxis.set_tick_params(color=bg_color)
    ax.yaxis.set_tick_params(color=bg_color)  
    ax.zaxis.set_tick_params(color=bg_color)
    
    ax.tick_params(axis='z', colors=bg_color)
    
    fig.patch.set_facecolor(fg_color)  
    ax.set_facecolor(fg_color)
        
    if background:
        fig.patch.set_facecolor(fg_color)
    
    # set imshow outline
    for spine in ax.axes.spines.values():
        spine.set_edgecolor(bg_color)
        
    # COLORBAR
    # set colorbar label plus label color
    cbar.set_label(r'$a/\lambda_0$', color=bg_color)
    
    # set colorbar tick color
    cbar.ax.xaxis.set_tick_params(color=bg_color, labelsize = font_size)
    
    # set colorbar edgecolor 
    cbar.outline.set_edgecolor(bg_color)
    
    # set colorbar ticklabels
    plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color=bg_color)

    plt.close()
    
    return fig

def gif_field(t, BC, ER, Bloch_mode, params, WE, k0_num, pwem_params, ticks, ymin, ylim, field_1, X0 = 0, Y0 = 0, 
                 import_dev='No', font_size=16):
    
    if pwem_params.device_sel == 'Square' or pwem_params.device_sel == 'Frame' or pwem_params.device_sel == 'Ring':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11,4))
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9,4), gridspec_kw={'width_ratios': [2, 1]})
        
    plt.subplots_adjust(wspace=0.05)
    
###################################################################################################### 
    '''
    Plot band diagram
    '''
########################################## HANDLE X AXIS #############################################            
    
    if pwem_params.device_sel == 'Square' or pwem_params.device_sel == 'Frame' or pwem_params.device_sel == 'Ring':
        beta  = ["$\Gamma$", "$X$", "$M$", "$\Gamma$"]
    elif pwem_params.device_sel == 'Hex' or pwem_params.device_sel == 'Honeycomb':
        beta  = ["$\Gamma$", "$M$", "$K$", "$\Gamma$"]
            
######################################################################################################

    for i in range(0, t+1):
        # ax1.plot(WH[i,:], 'blue')
        ax1.plot(np.ones(len(WE[:,i]))*i, WE[:,i], 'r*')
        
    for i in range(1,len(ticks) - 1):
        ax1.axvline(x =  ticks[i],   color = 'gray',ls='--')
      
######################################################################################################
        
    Ticks = ticks
    ax1.set_xticks(Ticks,beta)
        
######################################################################################################
        
    # ax1.text(ticks[-1] * 15/40, ymin+0.05, "H mode", bbox=dict(facecolor='blue', alpha=0.25), fontsize=font_size)
    # ax1.text(ticks[-1] * 21/40, ymin+0.05, "E mode", bbox=dict(facecolor='red', alpha=0.25), fontsize=font_size)
    
    ax1.set_xlim(0, ticks[-1])
    ax1.set_ylim(ymin, ylim)

    ax1.set_xlabel(r'$\vec{\beta}$')
    ax1.set_ylabel(r'$a/\lambda_0$')
       
    ax1.set_title(r'$\varepsilon_{} = {}$'.format('r', max([params.er1, params.er2])))
    
###############################################################################
    '''
    Plot fields
    '''
###############################################################################
    
    field_11 = np.append(field_1, field_1, axis=0)
    field_11 = np.append(field_1, field_11, axis=0)
    field_12 = np.append(field_11, field_11, axis=1)
    field_12 = np.append(field_12, field_11, axis=1)
    field_12 = field_12[::3,::3]
    
    ER1 = np.append(ER, ER, axis=0)
    ER1 = np.append(ER, ER1, axis=0)
    ER2 = np.append(ER1, ER1, axis=1)
    ER2 = np.append(ER2, ER1, axis=1)
    ER2 = ER2[::3,::3]
    
    if import_dev == 'No':
        if pwem_params.device_sel == 'Square' or pwem_params.device_sel == 'Frame' or pwem_params.device_sel == 'Ring':
            x = np.linspace(params.Lx*3/2, -params.Lx*3/2, params.dim[0])
            y = np.linspace(params.Ly*3/2, -params.Ly*3/2, params.dim[1])
            
            X, Y = np.meshgrid(x, y)
            
            # normalize the field
            f_max = np.array([max(abs(sublist)) for sublist in field_1])
            field_12 = field_12/max(f_max)
            
            a = ax2.imshow(abs(field_12)**2, extent=[params.x[0]*3, params.x[-1]*3, params.y[0]*3, params.y[-1]*3], cmap='jet', vmin=0, vmax=1)
        else:
            X = X0
            Y = Y0
            
            # normalize the field
            f_max = np.array([max(abs(sublist)) for sublist in field_1])
            field_12 = field_12/max(f_max)
            
            a = ax2.pcolor(X, Y, abs(field_12)**2, vmin=-1, vmax=1, cmap='jet')
    else:

        X = X0
        Y = Y0
        
        # normalize the field
        f_max = np.array([max(abs(sublist)) for sublist in field_1])
        field_12 = field_12/max(f_max)
        
        a = ax2.pcolor(X, Y, abs(field_12)**2, vmin=0, vmax=1, cmap='jet')
        
    ax2.set_aspect('equal')
    cb = fig.colorbar(a)
    cb.set_label(r'I, a.u.')
    ax2.contour(X, Y, ER2, colors = 'black')
    ax2.set_xticks([])
    ax2.set_yticks([])
    
    if Bloch_mode == 1:
        ax2.set_title(r'1st Bloch mode')
    elif Bloch_mode == 2:
        ax2.set_title(r'2nd Bloch mode')
    elif Bloch_mode == 3:
        ax2.set_title(r'3rd Bloch mode')
    else:
        ax2.set_title(r'{}th Bloch mode'.format(Bloch_mode))
    
    plt.savefig(f'./field_img/img_{t}.png', bbox_inches='tight', dpi = 200)
    
    plt.close()
    
    
def single_field(background, device_sel, ER, Bloch_mode, params, WE, field_1, beta_x, beta_y, phase, import_dev, 
                 select_field, font_size, X0 = 0, Y0 = 0):
    
    if background == 'Dark':
        fg_color = 'white'
        bg_color = 'black'
    else:
        fg_color = 'black'
        bg_color = 'white'        
    
    fig, ax = plt.subplots(1, 1)
    
    if background == 'Dark':
        ax.set_facecolor('black')
        
    field_11 = np.append(field_1, field_1, axis=0)
    field_11 = np.append(field_1, field_11, axis=0)
    field_12 = np.append(field_11, field_11, axis=1)
    field_12 = np.append(field_12, field_11, axis=1)
    field_12 = field_12[::3,::3]
    
    ER1 = np.append(ER, ER, axis=0)
    ER1 = np.append(ER, ER1, axis=0)
    ER2 = np.append(ER1, ER1, axis=1)
    ER2 = np.append(ER2, ER1, axis=1)
    ER2 = ER2[::3,::3]
    
    if import_dev == 'No':
        if device_sel == 'Square' or device_sel == 'Frame' or device_sel == 'Ring':
            x = np.linspace(params.Lx*3/2, -params.Lx*3/2, params.dim[0])
            y = np.linspace(params.Ly*3/2, -params.Ly*3/2, params.dim[1])
            X, Y = np.meshgrid(x, y)
                
            if select_field == 'Re(f)':
                # add phase
                phi = np.exp(-1j * (beta_x*X + beta_y*Y + phase))
                
                # normalize the field
                field_12 = np.real(field_12 * phi)
                f_max = np.array([max(np.real(sublist)) for sublist in field_12])
                field_12 = field_12/max(f_max)
            
                a = ax.imshow(field_12, extent=[params.x[0]*3, params.x[-1]*3, params.y[0]*3, params.y[-1]*3], cmap='jet')
            else:
                # normalize the field
                f_max = np.array([max(abs(sublist)) for sublist in field_1])
                field_12 = field_12/max(f_max)
                
                a = ax.imshow(abs(field_12)**2, extent=[params.x[0]*3, params.x[-1]*3, params.y[0]*3, params.y[-1]*3], cmap='jet')
                
            a.set_rasterized(True) # helps save memory
            
        else:
            X = X0
            Y = Y0
            if select_field == 'Re(f)':
                # add phase
                phi = np.exp(-1j * (beta_x*X + beta_y*Y + phase))
                
                # normalize the field
                field_12 = np.real(field_12 * phi)
                f_max = np.array([max(np.real(sublist)) for sublist in field_12])
                field_12 = field_12/max(f_max)
            
                a = ax.pcolor(X, Y, field_12, cmap='jet')
            else:
                # normalize the field
                f_max = np.array([max(abs(sublist)) for sublist in field_1])
                field_12 = abs(field_12)/max(f_max)
                
                a = ax.pcolor(X, Y, field_12**2, cmap='jet')

            a.set_rasterized(True)
        
    else:

        X = X0
        Y = Y0
        if select_field == 'Re(f)':
            # add phase
            phi = np.exp(-1j * (beta_x*X + beta_y*Y + phase))
            
            # normalize the field
            field_12 = np.real(field_12 * phi)
            f_max = np.array([max(np.real(sublist)) for sublist in field_12])
            field_12 = field_12/max(f_max)
            
            a = ax.pcolor(X, Y, field_12, cmap='jet')
        else:
            # normalize the field
            f_max = np.array([max(abs(sublist)) for sublist in field_1])
            field_12 = field_12/max(f_max)
            
            a = ax.pcolor(X, Y, abs(field_12)**2, cmap='jet')

        a.set_rasterized(True)
                
    cb = fig.colorbar(a)
    ax.contour(X, Y, ER2, colors = 'black')
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    
    if Bloch_mode == 1:
        ax.set_title(r'1st Bloch mode', color=fg_color)
    elif Bloch_mode == 2:
        ax.set_title(r'2nd Bloch mode', color=fg_color)
    elif Bloch_mode == 3:
        ax.set_title(r'3rd Bloch mode', color=fg_color)
    else:
        ax.set_title(r'{}th Bloch mode'.format(Bloch_mode), color=fg_color)
        
    a.axes.tick_params(color=fg_color, labelcolor=fg_color)
    """Maybe the code below can be fixed"""
    ax.tick_params(axis='both', which='major', labelsize=font_size)
    ax.tick_params(axis='both', which='minor', labelsize=font_size)
    
    
    # set imshow outline
    for spine in a.axes.spines.values():
        spine.set_edgecolor(fg_color)    
    
    # COLORBAR
    # set colorbar label plus label color
    if select_field == 'Re(f)':
        cb.set_label(r'Re(f), a.u.', color=fg_color)
    else:
        cb.set_label(r'I, a.u.', color=fg_color)
    
    # set colorbar tick color
    cb.ax.yaxis.set_tick_params(color=fg_color, labelsize = font_size)
    
    # set colorbar edgecolor 
    cb.outline.set_edgecolor(fg_color)
    
    # set colorbar ticklabels
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=fg_color)
    
    fig.patch.set_facecolor(bg_color)
        
    plt.close()
        
    return fig
