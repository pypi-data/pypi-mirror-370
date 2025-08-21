function S = readSpecMPIIO(specfile,type,S,P)
% Reads the mpi-io spec file from pegasus

testing = 0;
if testing; type = 'f0';S=struct();
    specfile = '../../testing/forcing-tests/output/mpiio/spec/particles.00009';
    P.npec_prp = 100; P.npec_prl=200;P.vprpmax = 4;P.vprlmax = 4;
end

switch type 
    case 'f0'
        fend = '.spec';
        tformat = 'Particle distribution function at time = %f';
    case 'edv_prp'
        fend = '.edotv_prp';
        tformat = '(E_perp, w_perp) at time = %f';
    case 'edv_prl'
        fend = '.edotv_prl';
        tformat = '(E_parallel, w_parallel) at time = %f';
    otherwise
        error('Invalid type');
end
        
specfile = [specfile fend];

nprp = P.npec_prp; nprl = P.npec_prl;
if ~isfield(P,'computeFullSpec');P.computeFullSpec=0;end

fid = fopen(specfile,'r','l');

if fid == -1 
  error(['File ' specfile ' not found']);
end
n2s = @(s) num2str(s);

s = fgetl(fid); % Pegasus++ binary output at time = 6.13200512517566e+03
S.t =  sscanf(s, tformat);

frsing = @(n) fread(fid,n,'float64',0,'l');
nnn = 1;

xyz = frsing(6);
max_x = 0; max_y=0; max_z =0;
min_x = 0; min_y=0; min_z =0;
while length(xyz)>1
    mb_data{nnn}.xb = xyz(1:2);
    mb_data{nnn}.yb = xyz(3:4);
    mb_data{nnn}.zb = xyz(5:6);
    if xyz(2)>max_x; max_x=xyz(2);end
    if xyz(4)>max_y; max_y=xyz(4);end
    if xyz(6)>max_z; max_z=xyz(6);end
    if xyz(1)<min_x; min_x=xyz(1);end
    if xyz(3)<min_y; min_y=xyz(3);end
    if xyz(5)<min_z; min_z=xyz(5);end
    for i = 1:length(P.npec_prl)
      spec_data{i,nnn}=fread(fid,[P.npec_prl(i) , P.npec_prp(i)],'double',0,'l');
    end
    xyz = frsing(6);
    nnn = nnn+1;
end
nmb = nnn-1;
disp(['Found data from ' n2s(nmb) ' meshblocks'])

dx = diff(mb_data{1}.xb);
dy = diff(mb_data{1}.yb);
dz = diff(mb_data{1}.zb);
Nx = round((max_x-min_x)/dx);Ny = round((max_y-min_y)/dy);Nz = round((max_z-min_z)/dz);
disp(['Meshblock array of size ' mat2str([Nx,Ny,Nz])])
if prod([Nx,Ny,Nz])~=nmb
    warning('Number of meshblocks doesnt match processor number')
end


for i = 1:length(nprp)
  S.vprp{i} = linspace(0,P.vprpmax(i),nprp(i)+1);
  S.vprp{i} = 0.5*(S.vprp{i}(1:end-1) + S.vprp{i}(2:end));
  S.vprl{i} = linspace(-P.vprlmax(i),P.vprlmax(i),nprl(i)+1);
  S.vprl{i} = 0.5*(S.vprl{i}(1:end-1) + S.vprl{i}(2:end));
end

if P.computeFullSpec
    tfull = [type '_grid'];
    for nnn=1:np
        xpos = round(mb_data{nnn}.xb(2)/dx);
        ypos = round(mb_data{nnn}.yb(2)/dy);
        zpos = round(mb_data{nnn}.zb(2)/dz);
        S.mb_data{xpos,ypos,zpos}.xb = mb_data{nnn}.xb;
        S.mb_data{xpos,ypos,zpos}.yb = mb_data{nnn}.yb;
        S.mb_data{xpos,ypos,zpos}.zb = mb_data{nnn}.zb;
        S.x(xpos) = mean(mb_data{nnn}.xb);
        S.y(ypos) = mean(mb_data{nnn}.yb);
        S.z(zpos) = mean(mb_data{nnn}.zb);
        for i = 1:length(nprp)
          S.(tfull){i,xpos,ypos,zpos} = spec_data{i,nnn};
        end
    %     [Sf.qprp(xpos,ypos,zpos),Sf.qprp(xpos,ypos,zpos)] = ...
    %         computeHeatFluxes(S.vprl,S.vprp,spec_data{nnn});
    end
end


S.(type) = {};
for i = 1:length(nprp)
  S.(type){i} = 0;
  for nnn=1:nmb
    S.(type){i} = S.(type){i} + spec_data{i,nnn};
  end
end


if P.computerms
        rms = [type '_rms'];
        S.(rms) = {};
        for i = 1:length(nprp)
          S.(rms){i} = 0;
          for nnn=1:nmb
            S.(rms){i} = S.(rms){i} + (spec_data{i,nnn}-S.(type){i}/nmb).^2;
          end
          S.(rms){i} = sqrt(S.(rms){i});
        end
end


% S.(type) = S.(type)/nmb;

fclose(fid);

if testing
    figure;semilogy(S.vprp, sum(S.f0,1),S.vprl, sum(S.f0,2))
end

end



function h = weightedhistc(vals, weights, edges)
    
    if ~isvector(vals) || ~isvector(weights) || length(vals)~=length(weights)
        error('vals and weights must be vectors of the same size');
    end
    
    Nedge = length(edges);
    h = zeros(size(edges));
    
    for n = 1:Nedge-1
        ind = find(vals >= edges(n) & vals < edges(n+1));
        if ~isempty(ind)
            h(n) = sum(weights(ind));
        end
    end

    ind = find(vals == edges(end));
    if ~isempty(ind)
        h(Nedge) = sum(weights(ind));
    end
end


function out = trapz2D(x,y,f)
% x is first dimension, y second
out = trapz(x,trapz(y,f,2),1);
end

