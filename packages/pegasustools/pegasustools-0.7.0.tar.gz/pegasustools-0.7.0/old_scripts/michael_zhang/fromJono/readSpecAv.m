function S=readSpecAv(specfile,type,S,P)

testing = 0;
if testing; type = 'f0';S=struct();
    specfile = '../../testing/forcing-tests/output/mpiio/spec/particles.00009';
    P.nspec_prpav = 200; P.nspec_prlav=400;P.vprpmaxav = 8;P.vprlmaxav = 8;
end

switch type 
    case 'f0'
        fend = '.specav';
        tformat = 'Particle distribution function at time = %f';
    case 'edv_prp'
        fend = '.edotv_prp_av';
        tformat = '(E_perp, w_perp) at time = %f';
    case 'edv_prl'
        fend = '.edotv_prl_av';
        tformat = '(E_parallel, w_parallel) at time = %f';
    otherwise
        error('Invalid type');
end
        
specfile = [specfile fend];

nprp = P.nspec_prpav; nprl = P.nspec_prlav;

fid = fopen(specfile,'r','l');

if fid == -1 
  error(['File ' specfile ' not found']);
end
n2s = @(s) num2str(s);

s = fgetl(fid); % Pegasus++ binary output at time = 6.13200512517566e+03
S.t =  sscanf(s, tformat);
spec_data = {};
S.vprp = {};
S.vprl = {};

for i = 1:length(nprp)
  spec_data{i} = fread(fid,[nprl(i) nprp(i)],'double',0,'l');
  S.vprp{i} = linspace(0,P.vprpmaxav(i),nprp(i)+1);
  S.vprp{i} = 0.5*(S.vprp{i}(1:end-1) + S.vprp{i}(2:end));
  S.vprl{i} = linspace(-P.vprlmaxav(i),P.vprlmaxav(i),nprl(i)+1);
  S.vprl{i} = 0.5*(S.vprl{i}(1:end-1) + S.vprl{i}(2:end));
end




S.(type) = spec_data;

fclose(fid);

if testing
    figure;semilogy(S.vprp, sum(S.f0,1),S.vprl, sum(S.f0,2)) % contourf(S.vprl, S.vprp, log10(S.f0.'));
end

end