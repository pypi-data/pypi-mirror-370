function V = readAllNBF(nbffiles)
% Reads a VTK files, or VTK files at a given timestep (e.g., if B, V P in
% different out{N} files), then puts them together and calculates other useful
% things like pressure anisotropy.

% Obviously, all the vtk files should be at the same time

% vtkfiles should be a cell list of different 

nnbf = length(nbffiles);

for nnn=1:nnbf
    tmp=readNBF(nbffiles{nnn});
    
    fields = fieldnames(tmp);
    for fff=1:length(fields)
        V.(fields{fff}) = tmp.(fields{fff});
    end
end

% Now have all the fields in one structure, work out some other interesting
% bits

excl_vel = 1;
if isfield(V,'pressure_tensor_11')
    V.pressure_tensor_11 = V.pressure_tensor_11 - excl_vel*V.dens.*V.vel1.*V.vel1;
    V.pressure_tensor_12 = V.pressure_tensor_12 - excl_vel*V.dens.*V.vel1.*V.vel2;
    V.pressure_tensor_13 = V.pressure_tensor_13 - excl_vel*V.dens.*V.vel1.*V.vel3;
    V.pressure_tensor_22 = V.pressure_tensor_22 - excl_vel*V.dens.*V.vel2.*V.vel2;
    V.pressure_tensor_23 = V.pressure_tensor_23 - excl_vel*V.dens.*V.vel2.*V.vel3;
    V.pressure_tensor_33 = V.pressure_tensor_33 - excl_vel*V.dens.*V.vel3.*V.vel3;
    V.bsq  = (V.Bcc1).^2 + (V.Bcc2).^2 + (V.Bcc3).^2;
    V.ptot = ( V.pressure_tensor_11 + V.pressure_tensor_22 + V.pressure_tensor_33 ) / 3;
    V.pprl = V.Bcc1 .* ( V.pressure_tensor_11 .* V.Bcc1 + V.pressure_tensor_12 .* V.Bcc2 + V.pressure_tensor_13 .* V.Bcc3 ) ./ V.bsq ...
       + V.Bcc2 .* ( V.pressure_tensor_12 .* V.Bcc1 + V.pressure_tensor_22 .* V.Bcc2 + V.pressure_tensor_23 .* V.Bcc3 ) ./ V.bsq ...
       + V.Bcc3 .* ( V.pressure_tensor_13 .* V.Bcc1 + V.pressure_tensor_23 .* V.Bcc2 + V.pressure_tensor_33 .* V.Bcc3 ) ./ V.bsq;
    V.pprp = 1.5 * V.ptot - 0.5 * V.pprl;
    V.Delta= 1.0 - V.pprl./V.pprp;
    V.FHparam = (V.pprp-V.pprl)./V.bsq;
end

% if 1%isfield(V,'force_unorm')
%     % Get Elsasser variables
%     isrho = 1./sqrt(V.dens);
%     V.zp1 = V.vel1 + V.Bcc1.*isrho;
%     V.zp2 = V.vel2 + V.Bcc2.*isrho;
%     V.zp3 = V.vel3 + V.Bcc3.*isrho;
%     V.zm1 = V.vel1 - V.Bcc1.*isrho;
%     V.zm2 = V.vel2 - V.Bcc2.*isrho;
%     V.zm3 = V.vel3 - V.Bcc3.*isrho;
% end

    
end
    
    
