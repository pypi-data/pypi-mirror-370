function save_nbf
% read a bunch of nbfs, and choose to save certain fields
% into one object in a .mat file (which can be read using matlab or hdf5 in
% python
% make a compute_all_pot_from_mat.py script

% if cant save, try calculating potential from within matlab, or loading
% nbfs directly into python script
name = 'b_b3_sim1';%%'half_tcorr_sim9'%'sig-decr-prod';'test-frontera-run';

computer = 'tigress';
DoFullCalculation =1;
reloadSpectrumFile = 0;
%nums = [0:153  ]; % imbalanced beta=0.3
nums = [0:76]; % balanced beta=0.3

rhoi = sqrt(0.3);
tauA = 6*48.1802; %Levs tauA = 206.4865395;

n2s = @(s) num2str(s);
sq=@(f) squeeze(f);

[readF,files_all,folder,~,outputfolder] = chooseComputerAndFiles(name,computer);
savebase = ['saved-analysis/']; %outputfolder '../../' 
savefolder = [ savebase 'efield-' name '.mat'];

disp(['Saving/loading from ' savefolder])

if DoFullCalculation

% Average over all the snapshots
fields = {'Ecc1','Ecc2','Ecc3'};%'spl','smn'};
for var = fields;Sl.(var{1}) = [];end
Sl.t=[];Sl.nums=[];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
if reloadSpectrumFile
    load(savefolder,'Sl');
    Sl
end
for nnn=nums
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
    [readF,files_all,folder] = chooseComputerAndFiles(name,computer);
    try 
        D = readF(files_all(nnn));
        %D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
    catch 
        warning(['Did not find ' folder ' nnn=' num2str(nnn)])
        continue
    end

    Sl.t = [Sl.t D.t];
    Sl.nums = [Sl.nums nnn];
    
    for var = fields
        Sl.(var{1}) = cat(4,Sl.(var{1}), D.(var{1}));
    end
  
    save(savefolder,'Sl', '-v7.3');
    
end
    Sl.n = length(Sl.t);
    save(savefolder,'Sl', '-v7.3');

else % doFullCalculation
    load(savefolder,'Sl','P');
end 