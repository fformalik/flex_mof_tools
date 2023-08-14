import numpy as np
import matplotlib.pyplot as plt

f = open("OUTCAR", "r")
lines = f.readlines()



for l in range(len(lines)):
    if 'NIONS' in lines[l]:
#        print(lines[l])
        nions = int(lines[l].split()[-1])

for l in range(len(lines)):
    if 'EDIFFG' in lines[l]:
#        print(lines[l])
        edifg = float(lines[l].split()[2])        
        
E = []
F_max = []
for l in range(len(lines)):
    if 'free  energy   TOTEN' in lines[l]:
#        print(l,lines[l])
        E.append(float(lines[l].split()[-2]))

    if 'TOTAL-FORCE (eV/Angst)' in lines[l]:
#        print(l,lines[l])
        
        
        Fx = []
        Fy = []
        Fz = []
        for i in range(l+2,l+nions+2):
#            print(i,lines[i])
            fx = float(lines[i].split()[-3])
            fy = float(lines[i].split()[-2])
            fz = float(lines[i].split()[-1])
            Fx.append(fx)
            Fy.append(fy)
            Fz.append(fz) 
        F = np.concatenate((np.array(Fx).reshape((nions,1)),
                            np.array(Fy).reshape((nions,1)),
                            np.array(Fz).reshape((nions,1))),axis=1)
        
        F_max.append(np.max(np.abs(F)))

iterations = np.arange(1,len(E)+1,1)

it = iterations.reshape((len(E),1))
E_arr = np.array(E).reshape((len(E),1))
F_arr = np.array(F_max).reshape((len(E),1))
output = np.concatenate((it,E_arr,F_arr),axis=1)

np.savetxt('conv.out', output, fmt='%i\t\t%1.4f\t\t%1.4f',
           header='Step\tEnergy (eV)\t Force_max (eV/A)')


fig, (ax1, ax2) = plt.subplots(1, 2,figsize=(10,4.5))
ax1.plot(it[10:],E_arr[10:],'o',color='tab:orange',label = 'Energy')
ax2.plot(it[10:],F_arr[10:],'o',label = 'Force')
      
ax1.tick_params(direction='in',labelsize=12,top="true",right="true")
ax2.tick_params(direction='in',labelsize=12,top="true",right="true")
ax2.set_yscale('log')
ax1.set_xlabel('Steps', fontsize=14)
ax2.set_xlabel('Steps', fontsize=14)
ax1.set_ylabel('Energy (eV)', fontsize=14)
ax2.set_ylabel('Max Force (eV/$\AA$)', fontsize=14)

ax2.axhline(abs(edifg),ls=':',color='tab:red',lw=3)
#ax2.set_ylim(0.1*edifg)

ax1.legend(loc='best')
ax2.legend(loc='best')
ax1.grid(color='grey', linestyle=':', linewidth=0.5)
ax2.grid(color='grey', linestyle=':', linewidth=0.5)
plt.tight_layout()

plt.savefig('conv.png', format='png', dpi=600)#, bbox_inches='tight')



