
function writeVTK(D,fname)

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
fid = fopen(fname,'w','b');

if( fid == -1 )
  disp('File not found');
end

% fgetl(fid); % # vtk DataFile Version x.x
fprintf(fid, '# vtk DataFile Version 3.0\n');
% s = fgetl(fid); %  MOMENT vars at time= 3.582106e+03, level= 0, domain= 0
fprintf(fid, 'FIELD vars at time= %f,  level= 0, domain= 0\n',D.t);
% V.t = time; %V.ncycle = time(2);
% fgetl(fid); % BINARY
% fgetl(fid); % DATASET STRUCTURED_POINTS
fprintf(fid, 'BINARY\n');
fprintf(fid, 'DATASET STRUCTURED_POINTS\n');

% s = fgetl(fid); % DIMENSIONS NX NY NZ
fprintf(fid, 'DIMENSIONS %d %d %d\n',D.nx+1,D.ny+1,D.nz+1);
% sz = sscanf(s, '%*s%d%d%d').';
sz = [D.nx+1,D.ny+1,D.nz+1];
sz=sz-1;
sz(sz==0)=1;


% s = fgetl(fid); % ORIGIN 0.000000e+00 -1.720721e+01 -1.720721e+01
% orgn = sscanf(s, '%*s%f%f%f').';
fprintf(fid, 'ORIGING %e %e %e\n',D.x(1)-D.dx/2,D.y(1)-D.dy/2,D.z(1)-D.dz/2);

% s = fgetl(fid); % SPACING 1.720721e-01 1.720721e-01 1.720721e-01
% spc = sscanf(s, '%*s%f%f%f').';
% V.dx = spc(1);V.dy = spc(2);V.dz = spc(3);
fprintf(fid, 'SPACING %e %e %e\n',D.dx,D.dy,D.dz);

% V.nx = sz(1);
% V.ny = sz(2);
% V.nz = sz(3);
% V.x = orgn(1)+spc(1)/2:spc(1):orgn(1)+V.nx*spc(1);
% V.y = orgn(2)+spc(2)/2:spc(2):orgn(2)+V.ny*spc(2);
% V.z = orgn(3)+spc(3)/2:spc(3):orgn(3)+V.nz*spc(3);

% s = fgetl(fid); % CELL_DATA NXNYNZ
% n2read = sscanf(s, '%*s%d');
fprintf(fid, 'CELL_DATA %d\n',D.nx*D.ny*D.nz);
n2read = D.nx*D.ny*D.nz;

%Let's now fight with the FIELD region for the other components.
linesBetweenData = 0;
% for a=0:linesBetweenData;s=fgetl(fid); end
% s=fgetl(fid);
% s=fgetl(fid);
fprintf(fid,'\n');
szr=sz; % size to read

fields = fieldnames(D);
for fff = 1:length(fields)
    if numel(D.(fields{fff}))==n2read
    %     vtype = sscanf(s, '%s%*s%*s'); % SCALARS/VECTORS name data_type 
    %     varname = sscanf(s, '%*s%s%*s');
        disp(['Adding ' fields{fff}])
        fprintf(fid,'SCALARS %s float\n',fields{fff});
        ncmpt=1;
        szr = sz;
% Need this?   % fgetl(fid); % LOOKUP_TABLE default -- only with pressure for some reason?
        fprintf(fid,'LOOKUP_TABLE default\n');
%         % read data
%         Q = fread(fid,ncmpt*n2read,'*single');
%         V = setfield(V,varname,reshape(Q,[ncmpt szr ]));
        fwrite(fid,single(D.(fields{fff})(:)),'*single');

        for a=0:linesBetweenData;fprintf(fid,'\n'); end
    end
end

fclose(fid);

end