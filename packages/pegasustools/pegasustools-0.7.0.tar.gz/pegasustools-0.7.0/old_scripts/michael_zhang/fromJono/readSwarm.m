function readSwarm

name = 'half_tcorr_sim9';
%name = 'b_b3_sim1';

computer = 'tigress';
DoFullCalculation =1;
%nums = [320:441]; % snapshot numbers for which to find spectrum
nums = [0:441];  %imbalanced
%nums = [0:222];  %balanced
%sname = 'swarm';%'swarm2-300';
sname = 'swarm';
nminor = 2;%6;%2;
loadSave = 0;

P.forceyyn = 1;
P.twoD = 0; P.oneD=0; P.nswarm = 100;
nmeas = 18+P.forceyyn*3+nminor*4;
dts = 0.104719755119660; dtout = 10.;
maxnt = ceil(dtout/dts);

n2s = @(s) num2str(s);
[readF,files_all,folder,filenamespec,outputfolder,swarm] = chooseComputerAndFiles(name,computer);
swarmfolder = [outputfolder  'swarm/'];


sarray_full = [];
if DoFullCalculation

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
if loadSave
    load([swarmfolder sname '.mat'],'sarray_full');
    size(sarray_full)
end
for nnn=nums
    disp([''])
    disp(['<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>'])
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
    %disp(['tar -xf ' swarmfolder swarm(nnn) '.tar --directory ' swarmfolder ])
    %unix(['tar -xf ' swarmfolder swarm(nnn) '.tar --directory ' swarmfolder ]);
files = strsplit(ls([swarmfolder swarm(nnn)]));
files = files(1:end-1);
nproc = length(files);

isint = @(n) round(n)==n;
n2s = @(s) num2str(s);

sarray = zeros(nmeas,P.nswarm, maxnt);
maxnt_true = 0;
for ppp=1:nproc
%     disp([swarmfolder swarm(nnn) '/' files{ppp}])
    fid = fopen([swarmfolder swarm(nnn) '/' files{ppp}]);
    if fid<0; disp([swarmfolder swarm(nnn) '/' files{ppp}]);end
    tmp = fread(fid, 1e100,'float64',0,'l');
    if prod(size(tmp))>0
        if isint(length(tmp)/nmeas)
            tmp = reshape(tmp, [nmeas length(tmp)/nmeas]);
        else
            error('Sizes don''t match up')
        end
        tmp(1,:) = tmp(1,:)-0.001;
        nvals = unique(tmp(1,:))+1;
        for iii=1:length(nvals)
%             disp(['Adding partcle number ' n2s(nvals(iii))])
%             if nvals(iii)==9
%                 nvals(iii)
%             end
            thisn = tmp(:,round(tmp(1,:))==round(nvals(iii)-1));
            sarray(:,nvals(iii),1:size(thisn,2)) = thisn;
            if maxnt_true<size(thisn,2);maxnt_true=size(thisn,2);end
        end
    end
    fclose(fid);
end
sarray = permute(sarray,[1 3 2]);
sarray = sarray(:,1:maxnt_true,:);

%disp(['rm -r ' swarmfolder swarm(nnn) ])
%unix(['rm -r ' swarmfolder swarm(nnn) ]);

sarray_full = cat(2,sarray_full, sarray);
size(sarray_full)

save([swarmfolder sname '.mat'],'sarray_full');

end % nnn loop

end