
function V = readVTK(vtkfile)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Usage: V = readVTK(vtkfile)
%
%   V:       Structure in which the data are stored
%   vtkfile: The filename
%   notes:   Only reads binary STRUCTURED_POINTS
%
% Erik Vidholm 2006
% Geoffroy Lesur 2009
%       Extended to include several fields in the same file (as Snoopy
%       does)
%       The output is now a structure.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% open file (OBS! big endian format)
fid = fopen(vtkfile,'r','b');

if( fid == -1 )
  disp('File not found');
end

fgetl(fid); % # vtk DataFile Version x.x
s = fgetl(fid); %  MOMENT vars at time= 3.582106e+03, level= 0, domain= 0
time =  sscanf(s, '%*s vars at time= %f,  level= 0, domain= 0').';
V.t = time; %V.ncycle = time(2);
fgetl(fid); % BINARY
fgetl(fid); % DATASET STRUCTURED_POINTS

s = fgetl(fid); % DIMENSIONS NX NY NZ
sz = sscanf(s, '%*s%d%d%d').';
sz=sz-1;
sz(sz==0)=1;

s = fgetl(fid); % ORIGIN 0.000000e+00 -1.720721e+01 -1.720721e+01
orgn = sscanf(s, '%*s%f%f%f').';

s = fgetl(fid); % SPACING 1.720721e-01 1.720721e-01 1.720721e-01
spc = sscanf(s, '%*s%f%f%f').';
V.dx = spc(1);V.dy = spc(2);V.dz = spc(3);

V.nx = sz(1);
V.ny = sz(2);
V.nz = sz(3);

V.x = orgn(1)+spc(1)/2:spc(1):orgn(1)+V.nx*spc(1);
V.y = orgn(2)+spc(2)/2:spc(2):orgn(2)+V.ny*spc(2);
V.z = orgn(3)+spc(3)/2:spc(3):orgn(3)+V.nz*spc(3);

s = fgetl(fid); % CELL_DATA NXNYNZ
n2read = sscanf(s, '%*s%d');


%Let's now fight with the FIELD region for the other components.
linesBetweenData = 1;
% for a=0:linesBetweenData;s=fgetl(fid); end
s=fgetl(fid);
s=fgetl(fid);
szr=sz; % size to read
while s ~= -1

    vtype = sscanf(s, '%s%*s%*s'); % SCALARS/VECTORS name data_type 
    varname = sscanf(s, '%*s%s%*s');
%     disp(['Adding ' varname])

    if strcmp(vtype,'VECTORS') 
        ncmpt=3;
        szr = sz;
    elseif strcmp(vtype,'SCALARS') 
        ncmpt=1;
        szr = sz;
        fgetl(fid); % LOOKUP_TABLE default -- only with pressure for some reason?
    else
        warning([varname ' NOT A VECTOR OR SCALAR'])
    end

    % read data
    Q = fread(fid,ncmpt*n2read,'*single');
    V = setfield(V,varname,reshape(Q,[ncmpt szr ]));
    
    V.(varname) = squeeze(V.(varname));

    for a=0:linesBetweenData;s=fgetl(fid); end
end


% Put  magnetic field into form that matches hdf5 output
if isfield(V,'cell_centered_B')
    V.Bcc1 = squeeze(V.cell_centered_B(1,:,:,:));
    V.Bcc2 = squeeze(V.cell_centered_B(2,:,:,:));
    V.Bcc3 = squeeze(V.cell_centered_B(3,:,:,:));
    V=rmfield(V,'cell_centered_B');
end
if isfield(V,'cell_centered_E')
    V.Ecc1 = squeeze(V.cell_centered_E(1,:,:,:));
    V.Ecc2 = squeeze(V.cell_centered_E(2,:,:,:));
    V.Ecc3 = squeeze(V.cell_centered_E(3,:,:,:));
    V=rmfield(V,'cell_centered_E');
end
if isfield(V,'cell_centered_F')
    V=rmfield(V,'cell_centered_F');
end

if isfield(V,'particle_momentum')
    V.vel1 = squeeze(V.particle_momentum(1,:,:,:))./V.particle_density;
    V.vel2 = squeeze(V.particle_momentum(2,:,:,:))./V.particle_density;
    V.vel3 = squeeze(V.particle_momentum(3,:,:,:))./V.particle_density;
    V=rmfield(V,'particle_momentum');
end
if isfield(V,'particle_density')
    V.dens = V.particle_density;
    V=rmfield(V,'particle_density');
end


fclose(fid);

end