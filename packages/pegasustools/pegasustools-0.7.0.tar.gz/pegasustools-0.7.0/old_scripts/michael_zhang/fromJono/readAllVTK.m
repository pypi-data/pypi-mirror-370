function V = readAllVTK(vtkfiles)
% Reads a VTK files, or VTK files at a given timestep (e.g., if B, V P in
% different out{N} files), then puts them together and calculates other useful
% things like pressure anisotropy.

% Obviously, all the vtk files should be at the same time

% vtkfiles should be a cell list of different 

nvtk = length(vtkfiles);

for nnn=1:nvtk
    tmp=readVTK(vtkfiles{nnn});
    
    fields = fieldnames(tmp);
    for fff=1:length(fields)
        V.(fields{fff}) = tmp.(fields{fff});
    end
end

% Now have all the fields in one structure, work out some other interesting
% bits

if isfield(V,'particle_pressure_11')
    V=rmfield(V,'particle_pressure_11');V=rmfield(V,'particle_pressure_12');V=rmfield(V,'particle_pressure_13');
    V=rmfield(V,'particle_pressure_22');V=rmfield(V,'particle_pressure_23');V=rmfield(V,'particle_pressure_33');
end
    
end
    
    
