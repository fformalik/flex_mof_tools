import numpy as np

num_img = 5
extrapol = 15
name_of_files = 'juk-8_i'

def volume(a):
    return np.dot(a[0][:],np.cross(a[1][:],a[2][:]))

file_np = open('cp.vasp','r')
file_lp = open('op.vasp','r')

lines_np = file_np.readlines()
lines_lp = file_lp.readlines()

#n_atom = lines_np[6].split()
n_atom = sum([int(i) for i in lines_np[6].split()])

np_coord = np.zeros((n_atom,3))
lp_coord = np.zeros((n_atom,3))

for i in range(8, 8+n_atom):
    np_coord[i-8][0] = float(lines_np[i].split()[0])
    np_coord[i-8][1] = float(lines_np[i].split()[1])
    np_coord[i-8][2] = float(lines_np[i].split()[2])
    lp_coord[i-8][0] = float(lines_lp[i].split()[0])
    lp_coord[i-8][1] = float(lines_lp[i].split()[1])
    lp_coord[i-8][2] = float(lines_lp[i].split()[2])
del i

diff = lp_coord - np_coord
large_diff = np.where(diff>0.5)
small_diff = np.where(diff<-0.5)

for i in range(len(large_diff[1])):
    lp_coord[large_diff[0][i]][large_diff[1][i]] = lp_coord[large_diff[0][i]][large_diff[1][i]] - 1

for i in range(len(small_diff[1])):
    np_coord[small_diff[0][i]][small_diff[1][i]] = np_coord[small_diff[0][i]][small_diff[1][i]] - 1


del lines_np[8:]
del lines_lp[8:]

np_lat_vect = np.zeros((3,3))
lp_lat_vect = np.zeros((3,3))

for i in range(2,5):
    np_lat_vect[i-2][0] = float(lines_np[i].split()[0])
    np_lat_vect[i-2][1] = float(lines_np[i].split()[1])
    np_lat_vect[i-2][2] = float(lines_np[i].split()[2])
    lp_lat_vect[i-2][0] = float(lines_lp[i].split()[0])
    lp_lat_vect[i-2][1] = float(lines_lp[i].split()[1])
    lp_lat_vect[i-2][2] = float(lines_lp[i].split()[2])
del i

V_np = volume(np_lat_vect)
V_lp = volume(lp_lat_vect)


for i in range(-extrapol, num_img+extrapol+1):
    lat_vect = (i/num_img)*lp_lat_vect+((num_img-i)/num_img)*np_lat_vect
    coord = (i/num_img)*lp_coord+((num_img-i)/num_img)*np_coord

    f = open(name_of_files+'_'+str(i)+'.vasp','w')
    f.write(lines_lp[0])
    f.write(lines_lp[1])
    np.savetxt(f, lat_vect)
    f.write(lines_lp[5])
    f.write(lines_lp[6])
    f.write(lines_lp[7])
    np.savetxt(f, coord)
    f.close()
    print(volume(lat_vect))
    print(i)


