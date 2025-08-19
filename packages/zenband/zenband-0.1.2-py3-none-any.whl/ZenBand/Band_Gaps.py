import matplotlib.pyplot as plt
import numpy as np

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

class Band_Gaps():

    def find_gaps(WE, N = 0):
        
        gap       = []
        omega_min = []
        omega_max = []
        
        for n in range(N):
            if min(WE[n+1,:]) - max(WE[n,:]) > 0.001:
                gap.append(min(WE[n+1,:]) - max(WE[n,:]))
                omega_min.append(max(WE[n,:]))
                omega_max.append(min(WE[n+1,:]))
            else:
                gap.append(0)
                omega_min.append(float('nan'))
                omega_max.append(float('nan'))
            
        return gap, omega_min, omega_max
    
    
    def complete_BGs(WE_min, WE_max, WM_min, WM_max):
        
        gap       = []
        omega_min = []
        omega_max = []
        
        for n in range(len(WE_min)):
            for m in range(len(WM_min)):
                if WM_min[m] <= WE_min[n] and WE_min[n] < WM_max[m]:
                    omega_min.append(max([WE_min[n], WM_min[m]]))
                    omega_max.append(min([WE_max[n], WM_max[m]]))
                    gap.append(omega_max[-1] - omega_min[-1])
                elif WE_min[n] <= WM_min[m] and WM_min[m] < WE_max[n]:
                     omega_min.append(max([WE_min[n], WM_min[m]]))
                     omega_max.append(min([WE_max[n], WM_max[m]]))
                     gap.append(omega_max[-1] - omega_min[-1])  
        
        return gap, omega_min, omega_max
    
  
    def plot_gaps_sep(R, gaps, omega_min, omega_max, er, N = 0, graph_color='red', mode='E'):
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (18, 6))
        plt.subplots_adjust(wspace=0.2)
        
        for n in range(N):
            ax1.plot(R, gaps[n::N], graph_color)
            
        ax1.set_xlim(0, 0.5)
        ax1.set_ylim(bottom=0)
        ax1.set_xlabel('$r$')
        ax1.set_ylabel('$\Delta a/\lambda_0$')
        ax1.set_title(f'Band gap width for {mode} mode, $e_r = {er}$')
        
        for n in range(N):
            ax2.fill_between(R, omega_min[n::N], omega_max[n::N], color = graph_color, alpha = 0.5, edgecolor = 'black')
            
        ax2.set_xlim(0, 0.5)
        ax2.set_ylim(bottom=0)
        ax2.set_xlabel('$r$')
        ax2.set_ylabel('$a/\lambda_0$')
        ax2.set_title(f'Band gap frequencies for {mode} mode')
        
        plt.savefig(f'./gaps_er{er}_{mode}', bbox_inches='tight', dpi = 200)
        
        plt.close(fig)
        
        
    def Plot_Gaps(R, gaps_E, gaps_H, omega_min_E, omega_min_H, omega_max_E, omega_max_H, y_lo, y_hi, R_min, R_max, background, Fontsize = 12, N = 0):
        
        if background == 'Light':
            fg_color = 'white'
            bg_color = 'black'
        else:
            fg_color = 'black'
            bg_color = 'white'
        
        colors_e = ['#440a02', '#881405', '#cd1f08', '#f53f27', '#f87c6c', '#fa9a8e']
        colors_h = ['#08203f', '#10407e', '#1860bd', '#3883e5', '#77abed', '#97bef1']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, facecolor = fg_color, figsize = (12, 4))
        plt.subplots_adjust(wspace = 0.2)
        ax1.tick_params(axis='both', which='major', labelsize=Fontsize, color = bg_color)
        ax2.tick_params(axis='both', which='major', labelsize=Fontsize, color = bg_color)
       
        for n in range(N):
            if sum(gaps_E[n::N]) >= 0.1:
                ax1.plot(R, gaps_E[n::N], color = colors_e[n % 6], label = r'$\Delta \omega_{{{lo}-{up}}}$, E mode'.format(up = n+2, lo = n+1))
            if sum(gaps_H[n::N]) >= 0.1:
                ax1.plot(R, gaps_H[n::N], color = colors_h[n % 6], label = r'$\Delta \omega_{{{lo}-{up}}}$, H mode'.format(up = n+2, lo = n+1))
               
        ax1.set_xlim(R_min, R_max)
        ax1.set_ylim(bottom=0)
        ax1.set_xlabel('$r^*$', fontsize = Fontsize, color = bg_color)
        ax1.set_ylabel('$\Delta \omega_n$', fontsize = Fontsize, color = bg_color)
        ax1.set_title(r'Band gap width', fontsize = Fontsize, color = bg_color)
        ax1.legend(fontsize = Fontsize, facecolor = fg_color, labelcolor = bg_color)
       
        for n in range(N):
            if sum(gaps_E[n::N]) >= 0.1:
                ax2.fill_between(R, omega_min_E[n::N], omega_max_E[n::N], color = colors_e[n % 6], alpha = 0.5, edgecolor = 'black')
            if sum(gaps_H[n::N]) >= 0.1:
                ax2.fill_between(R, omega_min_H[n::N], omega_max_H[n::N], color = colors_h[n % 6], alpha = 0.5, edgecolor = 'black')
       
        ax2.set_xlim(R_min, R_max)
        ax2.set_ylim(y_lo, y_hi)
        ax2.set_xlabel('$r^*$', fontsize = Fontsize, color = bg_color)
        ax2.set_ylabel('$\omega_n$', fontsize = Fontsize, color = bg_color)
        ax2.set_title('Band gap frequencies', fontsize = Fontsize, color = bg_color)
        
        """
        AXES VALUE COLOR
        """
        [t.set_color(bg_color) for t in ax1.xaxis.get_ticklines()]
        [t.set_color(bg_color) for t in ax1.xaxis.get_ticklabels()]
        [t.set_color(bg_color) for t in ax1.yaxis.get_ticklines()]
        [t.set_color(bg_color) for t in ax1.yaxis.get_ticklabels()]
        
        [t.set_color(bg_color) for t in ax2.xaxis.get_ticklines()]
        [t.set_color(bg_color) for t in ax2.xaxis.get_ticklabels()]
        [t.set_color(bg_color) for t in ax2.yaxis.get_ticklines()]
        [t.set_color(bg_color) for t in ax2.yaxis.get_ticklabels()]
        
        ax1.xaxis.set_tick_params(color=bg_color)
        ax1.yaxis.set_tick_params(color=bg_color)
        ax2.xaxis.set_tick_params(color=bg_color)
        ax2.yaxis.set_tick_params(color=bg_color)
           
        fig.patch.set_facecolor(fg_color)   
        
        """Maybe the code below can be fixed"""
        ax1.tick_params(axis='both', which='major', labelsize=Fontsize)
        ax1.tick_params(axis='both', which='minor', labelsize=Fontsize)
        ax2.tick_params(axis='both', which='major', labelsize=Fontsize)
        ax2.tick_params(axis='both', which='minor', labelsize=Fontsize)
        
        if background == 'Dark':
            ax1.set_facecolor(fg_color)
            ax2.set_facecolor(fg_color)
            fig.patch.set_facecolor(fg_color)
        
        # set imshow outline
        for spine in ax1.axes.spines.values():
            spine.set_edgecolor(bg_color) 
            
        for spine in ax2.axes.spines.values():
            spine.set_edgecolor(bg_color) 
        
        return fig
    
        plt.close(fig)