import numpy as np
import ase.io
import matplotlib.pyplot as plt



def lorentz(p, h, p0, w):
    x = (p-p0)/(w/2)
    return h/(1+x**2)


def save_xsf(file1,vector,name,include_H = True):
#    file1 = ase.io.read(name, format='vasp')

    el=file1.get_chemical_symbols()
    el = np.array(el,dtype=str)
    el = el.reshape((len(el),1)) 
    symbols = el
    atoms1 = file1.positions

    if include_H == False:
        no_H = np.where(symbols != 'H')[0]
        el = el[no_H]
        atoms1 = atoms1[no_H]
#        vector = vector[no_H]

    
    xsf_dat = np.concatenate((el, atoms1, vector), axis=1)
    with open(name+'.xsf', 'w') as out:
        line = 'CRYSTAL\n'
        line += 'PRIMVEC'
        for vect in file1.cell:
            line += '\n'
            for a in vect:
                line += ' '+str(a)            
        line += "\nPRIMCOORD\n"
        line += "{:3d} {:d}".format(len(el), 1)
        for a in xsf_dat:
            line += '\n'
            for j in a:
                line += ' '+str(j)
        out.write(line)


def poscars2vect(poscar1, poscar2, include_H = True,scaling='no'):
    '''
    Two poscars to xsf vector.    
    '''
    file1 = ase.io.read(poscar1, format='vasp')
    file2 = ase.io.read(poscar2, format='vasp')
    atoms1 = file1.positions
    coordinates1 = atoms1
    atoms2 = file2.positions
    masses = file1.get_masses()
    masses = np.array(masses,dtype=float)
    masses = masses.reshape((len(masses),1))

    if scaling != 'no':
        at_s1 = file1.get_scaled_positions()
        at_s2 = file2.get_scaled_positions()

        vect_s = at_s2-at_s1

        for i in range(len(vect_s)):
            for j in range(3):
                if vect_s[i,j] > 0.5:
                    print(vect_s[i,j])
                    vect_s[i,j] = vect_s[i,j] - 1
                elif vect_s[i,j] < -0.5:
                    print(vect_s[i,j])
                    vect_s[i,j] = vect_s[i,j] + 1
            
        vector_final = vect_s @ file1.cell
        vector_final1 = vect_s @ file1.cell
        vector_final2 = vect_s @ file2.cell
        vector_final_av = 0.5 * (vector_final1+vector_final2) 
        
        if scaling == 'regular':
            vector = vector_final
        elif scaling == 'average':
            vector = vector_final_av
        
    else:
        vector = atoms2 - atoms1


    symbols=file1.get_chemical_symbols()
    symbols = np.array(symbols,dtype=str)
    symbols = symbols.reshape((len(symbols),1))
    
    no_H = 0  
    if include_H == False:
        no_H = np.where(symbols != 'H')[0]
        symbols = symbols[no_H]
        masses = masses[no_H]
        atoms1, atoms2 = atoms1[no_H], atoms2[no_H]
        vector = vector[no_H]
        coordinates1 = coordinates1[no_H]
        
    vector_norm = vector/np.linalg.norm(vector)
    xsf_dat = np.concatenate((symbols, atoms1, vector_norm), axis=1)
#    xsf_dat_limited = np.concatenate((symbols, atoms1), axis=1) #array with element and positions
    
    with open('vector.xsf', 'w') as out:
        line = 'CRYSTAL\n'
        line += 'PRIMVEC'
        for vect in file1.cell:
            line += '\n'
            for a in vect:
                line += ' '+str(a)            
        line += "\nPRIMCOORD\n"
        line += "{:3d} {:d}".format(len(symbols), 1)
        for a in xsf_dat:
            line += '\n'
            for j in a:
                line += ' '+str(j)
        out.write(line)
        
        
        
    return vector_norm, masses, symbols, no_H


def load_vibmodes_from_outcar(inf, exclude_imag=False, 
                              include_H = True, H_index = 0):
    '''
    Read vibration eigenvectors and eigenvalues from OUTCAR.
    '''

    out = [line for line in open(inf) if line.strip()]
    ln = len(out)
    for line in out:
        if "NIONS =" in line:
            nions = int(line.split()[-1])
            break

    THz_index = []
    for ii in range(ln-1, 0, -1):
        if '2PiTHz' in out[ii]:
            THz_index.append(ii)
        if 'Eigenvectors and eigenvalues of the dynamical matrix' in out[ii]:
            i_index = ii + 2
            break
    j_index = THz_index[0] + nions + 2

    real_freq = [False if 'f/i' in line else True
                 for line in out[i_index:j_index]
                 if '2PiTHz' in line]

    im_freq = [True if 'f/i' in line else False
                 for line in out[i_index:j_index]
                 if '2PiTHz' in line]

    omegas = [line.split()[-4] for line in out[i_index:j_index]
              if '2PiTHz' in line]
    modes = [line.split()[3:6] for line in out[i_index:j_index]
             if ('dx' not in line) and ('2PiTHz' not in line)]

    omegas = np.array(omegas, dtype=float)
    modes = np.array(modes, dtype=float).reshape((-1, nions, 3))
    
    omegas[im_freq] = -omegas[im_freq]

    if exclude_imag:
        omegas = omegas[real_freq]
        modes = modes[real_freq]
        
    if include_H == False:
        modes = modes[:,H_index]    
        
    return omegas, modes


def mode_normalization(mode,mass):
    mode_m_norm = np.zeros(np.shape(mode))
    mode_full_norm = np.zeros(np.shape(mode))
    for i in range(len(mode)):
        mode_m_norm[i] = mode[i]/np.sqrt(mass)   
        mode_full_norm[i] = mode_m_norm[i]/np.linalg.norm(mode_m_norm[i]) 
    return mode_m_norm, mode_full_norm


def scalar(vector,mode_norm):
    dots = np.zeros(len(mode_norm))
    
    for i in range(len(mode_norm)):
        d = 0
        for j in range(len(mode_norm[i])):
            d += np.dot(mode_norm[i][j],vector[j])
        dots[i] = d
    return dots

def scalar_m(vector,mode_norm,m):
    dots = np.zeros(len(mode_norm))
    
    for i in range(len(mode_norm)):
        d = 0
        for j in range(len(mode_norm[i])):
            d += np.sqrt(m[j])*np.dot(mode_norm[i][j],vector[j])
        dots[i] = d
    return dots

def check(mode_norm,dots):
    vector_check_all = np.zeros(np.shape(mode_norm)[1:3])
    for i in range(len(mode_norm)):
        check = dots[i]*mode_norm[i]
        vector_check_all += check        
    return vector_check_all


def main():

   return 1     


if __name__ == "__main__":

# ===========USER=INTERFACE====================================================
    struct_1 = 'zro2_cubic.vasp'
    struct_2 = 'zro2_tetragonal.vasp'
    label ='ZrO$_{2}$'
    plot_file = 'zro'
    outcar = 'OUTCAR'
    fingerprint_xsf_name = 'fingerprint'
    check_xsf_name = 'check'
    width = 10
    h = True  #include hydrogens?
    scaling = 'average'
    max_dot = 0.3
    plot_res = 100000
    figs = (9.36,6.8)
# =============================================================================

    poscar1, poscar2 = struct_1, struct_2                                          
    vector_norm, m, symbols, H_index  = poscars2vect(poscar1, poscar2,
                                               include_H = h, scaling=scaling)     
    omega, mode = load_vibmodes_from_outcar(outcar,include_H=h,
                                        H_index=H_index)                          

    mode_m, mode_norm = mode_normalization(mode,m)                                

    dots = scalar(vector_norm,mode)                                        
    dots_mass = scalar_m(vector_norm,mode_m,m) 
    
    dots = dots_mass
                                       
#-------------------

    omega_dots = np.column_stack((omega,abs(dots)))
    max_dots = np.flip(omega_dots[omega_dots[:, 1].argsort()],axis=0)
    for i in range(len(max_dots)):
        if abs(max_dots[i,1]) < max_dot:
            break
    max_dots = max_dots[0:i,:]
    print('Most significant modes:\n',max_dots)
    
#-------------------      
    f_m_i = np.argmax(abs(dots))
    figerprint_mode = mode_m[f_m_i]
    print('Fingerprint mode no.: {:d}, frequency: {:4.2f} cm^-1, dot: {:1.2f}'
          .format(f_m_i, omega[f_m_i],dots[f_m_i]))
    file1 = ase.io.read(struct_1, format='vasp')
    save_xsf(file1,figerprint_mode,fingerprint_xsf_name,include_H=h)
    
    
#---------saving_some_mode    
    # r_m_i = 30
    # random_mode = mode_norm[r_m_i]
    # print('Fingerprint mode no.: {:d}, frequency: {:4.2f} cm^-1, dot: {:1.2f}'
    #       .format(r_m_i, omega[r_m_i],dots[r_m_i]))
    # file1 = ase.io.read(struct_1, format='vasp')
    # save_xsf(file1,random_mode,str(r_m_i),include_H=h)      
#----CAREFULL ABOVE------    
    
#------------------- 
    check_vector = check(mode,dots)
    # check_vector = check_vector/np.linalg.norm(check_vector)
    save_xsf(file1,check_vector,check_xsf_name,include_H=h)
#-------------------
    d = 0
    for j in range(len(check_vector)):
        d += np.dot(vector_norm[j],check_vector[j])
    print('Coorelation coeficient: {:1.2f}'.format(d))
#-------------------

    np.savetxt(plot_file+'.dat', max_dots, fmt='%5.4f', delimiter='\t', newline='\n',
               header='Fingerprint mode no.: {:d}\nFingerprint mode frequency: {:4.2f} cm^-1\nFMCC: {:1.4f}\nCVCC: {:1.4f}'
               .format(f_m_i, omega[f_m_i],dots[f_m_i],d), footer='', comments='', encoding=None)

#==========================plot=============================================
    
    omega_lin = np.linspace(1.1*min(omega),1.1*max(omega),plot_res)               
    intens = np.zeros((plot_res))                                                
    for j in range(len(dots)):                                                 
        intens = intens + lorentz(omega_lin, abs(dots[j]), omega[j], width)         
    
    np.savetxt(plot_file+'_spectrum.dat',
               np.concatenate((np.reshape(omega_lin,(plot_res,1)),np.reshape(intens,(plot_res,1))),axis=1))
    
    fig = plt.figure(figsize=figs)
    
    plt.plot(omega_lin,intens,label = label)# + ', width = '+str(width)+' cm$^{-1}$')

    plt.xlabel(r'Frequency (cm$^{-1})$', fontsize=15)
#    plt.ylabel(r'$\vec d \cdot \vec e_{i}$', fontsize=15)
    plt.ylabel(r'PDCS', fontsize=15)
    plt.tick_params(direction='in',labelsize=12,top="true",right="true")
    plt.legend(loc='best')#,bbox_to_anchor=(1.05,0.9))
    plt.grid(color='grey', linestyle=':', linewidth=0.5)
    plt.xlim(min(omega_lin),max(omega_lin))
#    plt.ylim(0,1)
    #ax.tick_params(labelleft=False) 
    #plt.title(f'{pltname}, {sgs} ({sgn}), {lt}')
    plt.tight_layout()
    plt.savefig(plot_file+'.png', format='png', dpi=600)
#=============================================================================
   

