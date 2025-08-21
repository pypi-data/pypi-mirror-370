function V=readNBF(nbffile)
% Reads pegasus binary (.nbf) format

% open file (OBS! big endian format)
fid = fopen(nbffile,'r','b');

if( fid == -1 )
  disp('File not found');
  disp('<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>')
  disp(nbffile)
  disp('<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>')
end

s = fgetl(fid); % Pegasus++ binary output at time = 6.13200512517566e+03
V.t =  sscanf(s, 'Pegasus++ binary output at time = %f').';
s = fgetl(fid); % Big endian = 0
bl = sscanf(s, 'Big endian = %d').';
if bl==0; bl='l';else ;bl='b';end
s = fgetl(fid); % Number of MeshBlocks = #
V.nbtotal = sscanf(s, 'Number of MeshBlocks = %d').';
s = fgetl(fid); % Number of variables = 6
V.nvars = sscanf(s, 'Number of variables = %d').';
s = fgetl(fid); % Variables: {list of variables}
var_list = strsplit(s);
var_list = var_list(2:end-1);
if length(var_list) ~= V.nvars
    error('length(var_list) ~= V.nvars');
end

% Mesh information 
s = fgetl(fid); % Mesh:   nx1=#   x1min=#  x1max=#
tmp = sscanf(s, 'Mesh:   nx1=%d   x1min=%f   x1max=%f');
V.xr = [tmp(2) tmp(3)]; V.nx = tmp(1); V.dx = (V.xr(2)-V.xr(1))/V.nx;
V.x = (V.xr(1)+V.dx/2):V.dx:(V.xr(2)-V.dx/2);
s = fgetl(fid); %       nx2=#   x2min=#  x2max=#
tmp = sscanf(s, '        nx2=%d   x2min=%f   x2max=%f');
V.yr = [tmp(2) tmp(3)]; V.ny = tmp(1); V.dy = (V.yr(2)-V.yr(1))/V.ny;
V.y = (V.yr(1)+V.dy/2):V.dy:(V.yr(2)-V.dy/2);
s = fgetl(fid); %         nx3=#   x3min=#  x3max=#
tmp = sscanf(s, '        nx3=%d   x3min=%f   x3max=%f');
V.zr = [tmp(2) tmp(3)]; V.nz = tmp(1); V.dz = (V.zr(2)-V.zr(1))/V.nz;
V.z = (V.zr(1)+V.dz/2):V.dz:(V.zr(2)-V.dz/2);

% Meshblock size 
s = fgetl(fid); % MeshBlock: nx1=25   nx2=20   nx3=1
V.nblk = sscanf(s,' MeshBlock: nx1=%d   nx2=%d   nx3=%d');

% Forcing
cpos = ftell(fid);
s = fgetl(fid); % MeshBlock: nx1=25   nx2=20   nx3=1
if strcmp(s(1:7),'Forcing')
    f_norm = sscanf(s,'Forcing: unorm=%f   bnorm=%f');
    V.force_unorm = f_norm(1); V.force_bnorm = f_norm(2);
else
    fseek(fid,cpos,'bof');
end


% Logical locations of each block 
islist = 0:V.nblk(1):V.nx-1;
jslist = 0:V.nblk(2):V.ny-1;
kslist = 0:V.nblk(3):V.nz-1;

% Preallocate V fields
for vvv = 1:V.nvars
    V.(var_list{vvv}) = zeros(V.nx, V.ny, V.nz);
end

% Loop over all meshblocks, put results into V fields.
frint = @(n) fread(fid,n,'int',0,bl);
frsing = @(n) fread(fid,n,'*single',0,bl);
for bbb = 1:V.nbtotal
    il1 = frint(1)+1;
    il2 =  frint(1)+1;
    il3 =  frint(1)+1;
    mx1 = frint(1);
    minx1 = frsing(1);
    maxx1 = frsing(1);
    mx2 =  frint(1);
    minx2 = frsing(1);
    maxx2 = frsing(1);
    mx3 =  frint(1);
    minx3 = frsing(1);
    maxx3 = frsing(1);
    iis = islist(il1)+1;
    iie = islist(il1)+mx1;
    ijs = jslist(il2)+1;
    ije = jslist(il2)+mx2;
    iks = kslist(il3)+1;
    ike = kslist(il3)+mx3;
    
    for vvv = 1:V.nvars
        V.(var_list{vvv})(iis:iie,ijs:ije,iks:ike) = ...
            reshape(frsing(mx1*mx2*mx3),[mx1,mx2,mx3]);
    end
end


if isfield(V,'mom1')
    V.vel1 = V.mom1./V.dens;
    V.vel2 = V.mom2./V.dens;
    V.vel3 = V.mom3./V.dens;
    V = rmfield(V,{'mom1','mom2','mom3'});
end

fclose(fid);

end 