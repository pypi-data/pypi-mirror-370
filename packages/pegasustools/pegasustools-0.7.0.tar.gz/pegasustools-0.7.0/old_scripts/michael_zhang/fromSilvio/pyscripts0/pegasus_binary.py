import numpy as np
import struct

def nbf(filename):

  # read the binary file
  f = open(filename,'rb')   
  line = f.readline()

  # check if the file was written correctly
  if (line.split()[0] != b"Pegasus++"):
    print("Error in nbf(): unexpected file format")
    return

  # read output information
  time = np.float64(line.split()[-1]) # line 1 - output time
  line = f.readline()
  # line 2 - endianess (not used for now, but may be useful of certain machines)
  line = f.readline()
  nbtotal = int(line.split()[-1])     # line 3 - number of meshblocks
  line = f.readline()
  nvars =   int(line.split()[-1])     # line 4 - number of variables
  line = f.readline()
  var_list = line.split()[1:nvars+1]  # line 5 - list of variables
  line = f.readline()

  # lines 6-8 - read mesh information
  temp_split = line.split()
  Nx1 = int(temp_split[1].decode('ascii').split('=')[1])      
  X1min = np.float64(temp_split[2].decode('ascii').split('=')[1])      
  X1max = np.float64(temp_split[3].decode('ascii').split('=')[1])      
  line = f.readline()
  temp_split = line.split()
  Nx2 = int(temp_split[0].decode('ascii').split('=')[1])      
  X2min = np.float64(temp_split[1].decode('ascii').split('=')[1])      
  X2max = np.float64(temp_split[2].decode('ascii').split('=')[1])     
  line = f.readline()
  temp_split = line.split()
  Nx3 = int(temp_split[0].decode('ascii').split('=')[1])      
  X3min = np.float64(temp_split[1].decode('ascii').split('=')[1])      
  X3max = np.float64(temp_split[2].decode('ascii').split('=')[1])
  line = f.readline()

  # line 9 - meshblock size
  temp_split = line.split()
  nx1 = int(temp_split[1].decode('ascii').split('=')[1]) 
  nx2 = int(temp_split[2].decode('ascii').split('=')[1]) 
  nx3 = int(temp_split[3].decode('ascii').split('=')[1]) 

  # final result = dictionary of arrays
  result = {}
  # add an entry for each variable
  for nv in range(nvars):
    result[var_list[nv]] = np.zeros((Nx3,Nx2,Nx1)) 
 
  # starting indices for each logical location
  islist = np.arange(0,Nx1,nx1)
  jslist = np.arange(0,Nx2,nx2)
  kslist = np.arange(0,Nx3,nx3)

  # loop over all meshblocks and read all variables
  for nb in range(nbtotal):
    il1 = struct.unpack("@i",f.read(4))[0]
    il2 = struct.unpack("@i",f.read(4))[0]
    il3 = struct.unpack("@i",f.read(4))[0]
    mx1 = struct.unpack("@i",f.read(4))[0]
    minx1 = struct.unpack("@f",f.read(4))[0] 
    maxx1 = struct.unpack("@f",f.read(4))[0] 
    mx2 = struct.unpack("@i",f.read(4))[0]
    minx2 = struct.unpack("@f",f.read(4))[0] 
    maxx2 = struct.unpack("@f",f.read(4))[0] 
    mx3 = struct.unpack("@i",f.read(4))[0]
    minx3 = struct.unpack("@f",f.read(4))[0] 
    maxx3 = struct.unpack("@f",f.read(4))[0] 
    iis = islist[il1]
    iie = iis + mx1
    ijs = jslist[il2]
    ije = ijs + mx2
    iks = kslist[il3]
    ike = iks + mx3
    fmt = "@%df"%(mx1*mx2*mx3)
    for nv in range(nvars):
      tmp = result[var_list[nv]]
      data = np.array(struct.unpack(fmt,f.read(4*mx1*mx2*mx3)))
      data = data.reshape(mx3,mx2,mx1)
      tmp[iks:ike,ijs:ije,iis:iie] = data 
  # close the file
  f.close()

  return result
