function distributionFunctionsAv

%need to recalc vprp and vprl for balanced runs (used ion_start=38 before),
%and correct for ion_start=35 in other VDF plotting scripts
i_b3 = 0;
b_b3 = 0;
i_b0625 = 0;
b_b0625 = 0;
i_b1 = 1; % might need to separate F into f0, edvprp and edvprl due to cadence
b_b1=0;
DoFullCalculation = 1;
loadsave = 1;
copyViaScp=0;

tstrt = 0;%5;%20;
unscalew = 1;
multispecies = 0;
animateF = 0;
savefnew = 0;
plotPaper = 0;%1;
plotFonly2D = 0;
plotF =   0;
plotHeat = 0;
plotHeatAllTogether = 0;
plotDprp =0;
plotDprpFromF = 0;
plotHeatFromF = 0; % don't have eprp and eprl implemented yet
saveVthtot3d = 0;
saveQ = 0;

if i_b3
    name = 'half_tcorr_sim9';
    nums = [0:440];%[0:401 ];%229:312]; % snapshot numbers for which to find spectrum %i_b3
%nums = [229:440]; %ib3 edv % min 229 for edotvav output
%nums = [0:95];
    ion_start=38;
end
if b_b3
    name = 'b_b3_sim1';
    nums = [0:222]; % b3 need to redo, since wrong normalizationg by pcc (32 instead of 27)
    ion_start = 35;
end
if i_b0625
    name = 'hb_beta0625';
    nums = [0:213];
    ion_start=38;
end
if b_b0625
    name = 'b_b0625_sim1';
    nums = [0:76];
    ion_start=35;
end
if i_b1
    name = 'i_b1_sim1';
    nums = [94:173]%[0:93];
    ion_start=38;
end
if b_b1
    name = 'b_b1_sim1';
    %nums = [0:93];
    ion_start=35;
end
%bal = 1;
% gotta correct Dpp calcs (and maybe other 1D calcs to use wp normalized to
% vthperp

if i_b3
    P.nspec_prlav = [1000 2000 2000];
    P.nspec_prpav = [500 1000 1000];
    P.vprpmaxav = [10 20 20];
    P.vprlmaxav = [10 20 20];
    species = 3;
    ppc = [1000 64 64];
    P.savemid = [500 1000 1000];% 300; % save only first savemid in vprp, middle 2*savemid in vprl
else
    P.nspec_prlav = [1000 2000 2000 2000 2000 2000 2000];
    P.nspec_prpav = [500 1000 1000 1000 1000 1000 1000];
    P.vprpmaxav = [10 20 20 20 20 20 20];
    P.vprlmaxav = [10 20 20 20 20 20 20];
    species = 7;
    ppc = [1000 27 27 27 27 27 27]
    P.savemid = [500 1000 1000 1000 1000 1000 1000];
end
if i_b1 || b_b1
    P.nspec_prlav = [1000 2000 2000 2000 2000 2000 2000 2000];
    P.nspec_prpav = [500 1000 1000 1000 1000 1000 1000 1000];
    P.vprpmaxav = [10 20 20 20 20 20 20 20];
    P.vprlmaxav = [10 20 20 20 20 20 20 20];
    species = 8;
    ppc = [1000 27 27 27 27 27 27 27]
    P.savemid = [500 1000 1000 1000 1000 1000 1000 1000];
end
if b_b3 || i_b3
    P.beta=0.3; % All thermal velocities normalized to sqrt(beta)
    vol=6*48.1802^3;
    tauA = 6*48.1802;
    epsin = 12.9;%36.5; % energy injection per volume is the same?
    tas = nums*10./tauA;
end
if b_b0625 || i_b0625
    P.beta=0.0625;
    vol=6*22.0^3;
    tauA = 6*22.0;
    epsin = 4.0;%36.5; % energy injection per volume is different? because of different beta?
    tas = nums*6.6/tauA;
end
if i_b1 || b_b1
    P.beta=1.0;
    vol=6*87.96459^3;
    tauA = 6*87.96459;
    epsin = 80.0;%36.5; % energy injection per volume is different? because of different beta?
    tas = nums*10.5557508/tauA;
end
vthp = sqrt(P.beta);
if i_b3
    mass = [1 16 4];
    charge = [1 5 2];
    fnames = {'p' 'o5' 'he'};
    xnames = {'$w_\|/v_{\rm th0,p}$','$w_\|/v_{\rm th0,O^{5+}}$','$w_\|/v_{\rm th0,He^{++}}$'};
    ynames = {'$w_\perp/v_{\rm th0,p}$','$w_\perp/v_{\rm th0,O^{5+}}$','$w_\perp/v_{\rm th0,He^{++}}$'};
end
if b_b3
    mass = [1 16 4 16 12 12 56];
    charge = [1 5 2 6 6 5 9];
    ppc = [1000 27 27 27 27 27 27]
    fnames = {'p' 'o5' 'he' 'o6' 'c6' 'c5' 'fe9'};
    xnames = {'$w_\|/v_{th0,p}$','$w_\|/v_{th0,O^{5+}}$','$w_\|/v_{th0,He^{++}}$','$w_\|/v_{th0,O^{6+}}$','$w_\|/v_{th0,C^{6+}}$','$w_\|/v_{th0,C^{5+}}$','$w_\|/v_{th0,Fe^{9+}}$'};
    ynames = {'$w_\perp/v_{th0,p}$','$w_\perp/v_{th0,O^{5+}}$','$w_\perp/v_{th0,He^{++}}$','$w_\perp/v_{th0,O^{6+}}$','$w_\perp/v_{th0,C^{6+}}$','$w_\perp/v_{th0,C^{5+}}$','$w_\perp/v_{th0,Fe^{9+}}$'};
end
if i_b0625 || b_b0625
    mass = [1 16 4 16 12 12 24];
    charge = [1 5 2 6 6 5 9];
    fnames = {'p' 'o5' 'he' 'o6' 'c6' 'c5' 'mg9'};
    xnames = {'$w_\|/v_{th0,p}$','$w_\|/v_{th0,O^{5+}}$','$w_\|/v_{th0,He^{++}}$','$w_\|/v_{th0,O^{6+}}$','$w_\|/v_{th0,C^{6+}}$','$w_\|/v_{th0,C^{5+}}$','$w_\|/v_{th0,Mg^{9+}}$'};
    ynames = {'$w_\perp/v_{th0,p}$','$w_\perp/v_{th0,O^{5+}}$','$w_\perp/v_{th0,He^{++}}$','$w_\perp/v_{th0,O^{6+}}$','$w_\perp/v_{th0,C^{6+}}$','$w_\perp/v_{th0,C^{5+}}$','$w_\perp/v_{th0,Mg^{9+}}$'};
end
if i_b1 || b_b1
    mass = [1 16 4 16 12 12 24 1];
    charge = [1 5 2 6 6 5 9 1];
    fnames = {'p' 'o5' 'he' 'o6' 'c6' 'c5' 'mg9' 'pm'};
    xnames = {'$w_\|/v_{th0,p}$','$w_\|/v_{th0,O^{5+}}$','$w_\|/v_{th0,He^{++}}$','$w_\|/v_{th0,O^{6+}}$','$w_\|/v_{th0,C^{6+}}$','$w_\|/v_{th0,C^{5+}}$','$w_\|/v_{th0,Mg^{9+}}$','$w_\|/v_{th0,pm}$'};
    ynames = {'$w_\perp/v_{th0,p}$','$w_\perp/v_{th0,O^{5+}}$','$w_\perp/v_{th0,He^{++}}$','$w_\perp/v_{th0,O^{6+}}$','$w_\perp/v_{th0,C^{6+}}$','$w_\perp/v_{th0,C^{5+}}$','$w_\perp/v_{th0,Mg^{9+}}$','$w_\perp/v_{th0,pm}$'};
end
p_id = 'minor_turb';
if i_b0625
    computer = 'tigressevan';
    fname = ['../../eyerger/' name '/output/' p_id ]; % Folder with outputs']; % Folder with outputs
else
    computer = 'tigress';
    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end
qom = charge./mass;
vthi = vthp./sqrt(mass);
oovth   = sqrt(mass);
%species = 3;%7;
ncells = 6*280^3; nmesh = 24*20*14;
nprtl = ncells.*ppc;

set(0,'DefaultTextInterpreter','latex');
set(0,'DefaultLineLineWidth',1.0);
set(0,'DefaultAxesFontSize',11);
set(0,'DefaultTextFontSize',11);
set(0,'DefaultAxesLineWidth',1.0);
myblue   = [16 116 176]/256;
myred    = [227 35 31]/256;
myorange = [228 157 37]/256;
mypurple = [124 50 139]/256;
myyellow = [239 226 82]/256;
mygreen  = [123 174 54]/256;
mysky    = [77 190 238]/256;
mygrey   = [132 136 132]/256;
colorder = {myblue  myorange myred mypurple myyellow mygreen mysky};
plotorder_trunc = [3 2 4 5 6 7];
plotorder = [1 3 2 4 5 6 7];


% Plots variables from hst file
fulldata = importdata([ fname '.hst']);

try
    names = strsplit(fulldata.textdata{2},'  ');
    names = names(1:end-1);
    dat = fulldata.data;
catch
    dat = fulldata;
end

t = dat(:,1);
if i_b3
    is = restart_overlaps2(t);
else
    is = restart_overlaps3(t);
end
if i_b0625
    is = restart_overlaps4(t);
end

dt = dat(:,2);
dthst = diff(t);dthst = [ dthst(1);dthst ];


t=t(is)/tauA;
vthpp = {};
vthpl = {};
vthtot = {}
vthpp{1} = sqrt(dat(is,28))/sqrt(2);
vthpl{1} = sqrt(dat(is,27));
vthtot{1} = sqrt(dat(is,28)+dat(is,27));

for i = 1:length(P.vprpmaxav)-1
    vthpp{i+1} = sqrt(dat(is,ion_start+19+24*(i-1)))/sqrt(2);
    vthpl{i+1} = sqrt(dat(is,ion_start+18+24*(i-1)));
    vthtot{i+1} = sqrt( dat(is,ion_start+19+24*(i-1)) +  dat(is,ion_start+18+24*(i-1)) );
end

for i = 1:length(P.vprpmaxav)
    vthpp{i} = vthpp{i}/vthpp{i}(1);
    vthpl{i} = vthpl{i}/vthpl{i}(1);
    vthtot{i} = vthtot{i}/vthtot{i}(1);
end

disp('hello')
disp(t-tas<0.5/tauA)
disp(find(t-tas<0.5/tauA,1))

numinds = [];
for i = 1:length(tas)
  numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
end

disp(numinds)

for i = 1:length(P.vprpmaxav)
    vthpp{i} = vthpp{i}(numinds);
    vthpl{i} = vthpl{i}(numinds);
    vthtot{i} = vthtot{i}(numinds);
end

disp(t(numinds))

%t=t(numinds);
%figure
%plot(t,vthpp{1}, t, vthpp{2}, t,vthpp{3},t,vthpl{1}, t, vthpl{2}, t,vthpl{3},'Linewidth',1)
%legend({'$v_{thp,\perp}$','$v_{th1,\perp}$','$v_{th2,\perp}$','$v_{thp,\|}$','$v_{th1,\|}$','$v_{th2,\|}$'},'interpreter','latex')
%xlabel('$t/\tau_A$','interpreter','latex')
%ylabel('$v_{th} 1$','interpreter','latex')



nrm = epsin.*nprtl/vol; % With this sum(sum(edv_prp)) seems to match (as much as possible) d_t Eprp/epsin. 
% See compareHeatingDiagnostics.m
if strcmp(name,'lev')
    vol=6*34.4144^3;ncells = 6*200^3;nprtl = ncells*ppc;
    epsin = 9.52;nrm = epsin*nprtl/vol;tauA=206.4865395;
end
nrmdfdt = nrm;
nrm = nrm./(P.nspec_prpav./P.vprpmaxav).^2; % Since there are 50 points per vth






n2s = @(s) num2str(s);
[readF,files_all,folder,filenamespec] = chooseComputerAndFiles(name,computer);

savebase = [ './saved-analysis/'];
savefolder = [ savebase 'AvDFs-' name '.mat'];

disp(['Saving/loading from ' savefolder])


if DoFullCalculation

    
fields = {'f0','edv_prp','edv_prl','t','nums'};
for var = fields;disp(var{1});F.(var{1}) = [];end
F.f0 = {};
F.edv_prp = {};
F.edv_prl = {};
F.vprp = {};
F.vprl = {};
F.vprpp = {};
F.vprll = {};
for i = 1:length(P.vprpmaxav)
    F.f0{i} = [];
    F.edv_prp{i} = [];
    F.edv_prl{i} = [];
    F.vprp{i} = [];
    F.vprl{i} = [];
    F.vprpp{i} = [];
    F.vprll{i} = [];
end

vprlst = P.nspec_prlav/2-P.savemid+1 ;
vprlend = P.nspec_prlav/2+P.savemid;
numcnt = 1;
if loadsave
 load(savefolder,'F');
 F
 disp(F.nums)
end
for nnn=nums
    [readF,files_all,folder,filenamespec,outputfolder,swarm,track,filenamespecav] = chooseComputerAndFiles(name,computer);
    try 
        if copyViaScp 
            [~, filenamespecav] = copyFromFrontera(name,computer,'spec',nnn);
        end 
        disp(['Doing ' folder ' nnn = ' num2str(nnn)])
        F1 = readSpecAv(filenamespecav(nnn),'f0',struct(),P);
        if i_b3
            if nnn > 228
                F1 = readSpecAv(filenamespecav(nnn),'edv_prp',F1,P);
                F1 = readSpecAv(filenamespecav(nnn),'edv_prl',F1,P);
            end
        else
            F1 = readSpecAv(filenamespecav(nnn),'edv_prp',F1,P);
            F1 = readSpecAv(filenamespecav(nnn),'edv_prl',F1,P);
        end

    catch 
        warning(['Did not find ' filenamespecav(nnn)])
        continue
    end
    
    

    F.t = [F.t F1.t];
    F.nums = [F.nums nnn];
    zeroarr = zeros(size(F1.f0{i}),'like',F1.f0{i});
    %F.f0 = {};
    %F.f0{1} = 1;
    %disp(F.f0)
    for i = 1:length(P.vprpmaxav)
      F.f0{i} = cat(3,F.f0{i},F1.f0{i}(vprlst(i):vprlend(i),1:P.savemid(i)));
      %F.f0{end+1} = cat(3,F.f0{end+1},F1.f0{i}(vprlst:vprlend,1:P.savemid));
      if i_b3
          if nnn < 229
           F.edv_prp{i} = cat(3,F.edv_prp{i},zeroarr(vprlst(i):vprlend(i),1:P.savemid(i)));
           F.edv_prl{i} = cat(3,F.edv_prp{i},zeroarr(vprlst(i):vprlend(i),1:P.savemid(i)));
          else
           F.edv_prp{i} = cat(3,F.edv_prp{i},F1.edv_prp{i}(vprlst(i):vprlend(i),1:P.savemid(i)));
           F.edv_prl{i} = cat(3,F.edv_prl{i},F1.edv_prl{i}(vprlst(i):vprlend(i),1:P.savemid(i)));
          end
      else
           F.edv_prp{i} = cat(3,F.edv_prp{i},F1.edv_prp{i}(vprlst(i):vprlend(i),1:P.savemid(i)));
           F.edv_prl{i} = cat(3,F.edv_prl{i},F1.edv_prl{i}(vprlst(i):vprlend(i),1:P.savemid(i)));
      end

      %disp(i);
      %disp(P.savemid(i));
      %disp(size(F1.vprp{i}));
      F.vprp{i} = cat(3,F.vprp{i},F1.vprp{i}(1:P.savemid(i))/vthtot{i}(numcnt));
      F.vprl{i} = cat(3,F.vprl{i},transpose(F1.vprl{i}(vprlst(i):vprlend(i))/vthtot{i}(numcnt)));
      F.vprpp{i} = cat(3,F.vprp{i},F1.vprp{i}(1:P.savemid(i))/vthpp{i}(numcnt));
      F.vprll{i} = cat(3,F.vprl{i},transpose(F1.vprl{i}(vprlst(i):vprlend(i))/vthpl{i}(numcnt)));
    end
    numcnt = numcnt + 1;
end
save(savefolder,'F','P', '-v7.3');
else % DoFullCalculation
    load(savefolder,'F','P');
    disp(F)
end
F.n = length(F.t);
% 1-D vs. time plots
% % Heating
% s2= @(f) squeeze(sum(sum(f,2),1));
% nprtl = 216*392^3*6;
% plot(F.t,s2(F.f0)/nprtl)

F.t = F.t/tauA;
tstrt = find(F.t>tstrt,1);
dn=10;


%figure;set(gcf,'Color','white');
%[out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
%cvprl = cvprl./mean(vthtot{i}(16:35),1);
%cvprp = cvprp./mean(vthtot{i}(16:35),1);
%contourf(cvprl,cvprp,out.','k--','Linewidth',1);
%colorbar
%0.8:1:8.8 for protons at nnn=229+25
%-0.4:0.4:2.8 for oxygen at nnn=229+25
if saveVthtot3d
    vthtot3d = {};
    for i = 1:length(mass)
        vthtot3d{i}(1,1,:) = vthtot{i};
    end
    vfolder = [ savebase 'vthtot3d-' name '.mat'];
    save(vfolder,'vthtot3d', '-v7.3');
end

if saveQ
    heatip = {};
    heatil = {};
    for i = 1:length(P.vprpmaxav)
       heatip{i} = 0;%mean(F.edv_prp{i}(:,:,1:5),3);
       heatil{i} = 0;%mean(F.edv_prl{i}(:,:,1:5),3);
    end
    % save('saved-analysis/initDR-imbal2-prod.mat','heatip','heatil');
    %load('saved-analysis/initDR-imbal2-prod.mat','heatip','heatil');
    for i = 1:length(P.vprpmaxav)
        F.edv_prp{i} = (F.edv_prp{i}-heatip{i})/nrm(i); % vprp because histogram gives vprp*F
        F.edv_prl{i} = (F.edv_prl{i}-heatil{i})/nrm(i);
    end

    if unscalew
        for i = 1:length(mass)
            vthtot3d{i}(1,1,:) = vthtot{i};
            F.vprl{i} = F.vprl{i} .* vthtot3d{i} / sqrt(mass(i));
            F.vprp{i} = F.vprp{i} .* vthtot3d{i} / sqrt(mass(i));
        end
    end
    q_t = {};
    for i = 1:length(P.vprpmaxav)
        q_t{i} = int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.edv_prp{i})
    end
    times = F.t;

    qfolder = [ savebase 'Qfromedv-' name '.mat'];
    save(qfolder,'q_t','times', '-v7.3');

    if unscalew
        for i = 1:length(mass)
            F.vprl{i} = F.vprl{i} ./ vthtot3d{i} * sqrt(mass(i));
            F.vprp{i} = F.vprp{i} ./ vthtot3d{i} * sqrt(mass(i));
        end
    end
end


if savefnew


    %specs = [1 3 2]


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);


    tplt=[2.5]
    %tplt = [0.5 7.5 14.2];
    %tplt = [0.5 5.0 6.0];
    %tplt = [0.5 4.0 7.0];
    %dtplt = 0.5;
    dtplt = 0.1;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    vthtot3d = {};
    vprl = {};
    vprp = {};
    % Perpendicular diffusion coefficient
    if unscalew
        for i = 1:length(mass)
            vthtot3d{i}(1,1,:) = vthtot{i};
            F.vprl{i} = F.vprl{i} .* vthtot3d{i};
            F.vprp{i} = F.vprp{i} .* vthtot3d{i};
        end
    end

    counter = 1;

    plotf0 = {};

    for ttt = 1:length(tplt)
        for i = 1:length(mass)
        
            f0 = m(F.f0{i},tav,tavplt(:,ttt))./ int_dist(m(F.vprl{i},tav,tavplt(:,ttt)),m(F.vprp{i},tav,tavplt(:,ttt)),m(F.f0{i},tav,tavplt(:,ttt)));
            vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
            vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
            plotf0{counter} = f0;
            counter = counter+1;
        end
    end


    if unscalew
        for i = 1:length(mass)
            F.vprl{i} = F.vprl{i} ./ vthtot3d{i};
            F.vprp{i} = F.vprp{i} ./ vthtot3d{i};
        end
    end

save([ savebase 'PlotDFsNew2-5-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot', '-v7.3');


end %savefnew


if plotPaper

    set(0,'DefaultLineLineWidth',1.0);
    set(0,'DefaultTextInterpreter', 'latex');
    set(0,'DefaultAxesFontSize',16);
    set(0,'DefaultTextFontSize',16);
    set(0,'DefaultAxesLineWidth',1.0);

    dir =  ['../simulations/' name '/saved-plots/f0/'];

    pnum = 111;
    %nplt = [10:2:430];
    specs = [1 3 2]


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);


    %tplt = [0.5 7.5 14.2];
    tplt = [0.5 5.0 6.0];
    %tplt = [0.5 4.0 7.0];
    %dtplt = 0.5;
    dtplt = 0.1;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    vthtot3d = {};
    vprl = {};
    vprp = {};
    % Perpendicular diffusion coefficient
    if unscalew
        for i = 1:length(mass)
            vthtot3d{i}(1,1,:) = vthtot{i};
            F.vprl{i} = F.vprl{i} .* vthtot3d{i};
            F.vprp{i} = F.vprp{i} .* vthtot3d{i};
        end
    end


    figure(111); clf;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,18,6]);
    set(gcf,'PaperPositionMode','auto');

    counter = 1;
    plotpos = [1 4 7 2 5 8 3 6 9];
    plotf0 = {};

    for ttt = 1:length(tplt)
        for i = specs
        
            
            subplot(3,3,counter);%plotpos(counter))
            f0 = m(F.f0{i},tav,tavplt(:,ttt))./ int_dist(m(F.vprl{i},tav,tavplt(:,ttt)),m(F.vprp{i},tav,tavplt(:,ttt)),m(F.f0{i},tav,tavplt(:,ttt)));
            vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
            vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
            plotf0{counter} = f0;
    
            vprpn = vprp{i};
    
            if i==2 || i>=4
                liminds = find(log10(f0./vprpn)<-7);
                f0(liminds) = 0;
            end
            if i ==3
                liminds = find(log10(f0./vprpn)<-7);
                f0(liminds) = 0;
            end
            contourf(vprl{i},vprp{i},log10(f0./vprpn).',15);set(gca,'YDir','normal');
            %[out,outva,vprlhalf] = resonanceContours(vprp,vprl,vthpl{i}(25),vthpp{i}(25));
            [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
            cvprl = cvprl./m4(vthtot{i},tav,tavplt(:,ttt));
            cvprp = cvprp./m4(vthtot{i},tav,tavplt(:,ttt));
            if unscalew
                cvprl = cvprl.*m4(vthtot{i},tav,tavplt(:,ttt));
                cvprp = cvprp.*m4(vthtot{i},tav,tavplt(:,ttt));
            end
            %disp(cvprl)
            %disp(cvprp)
            if i==1
                levels = -0.4:1.2:11.6;%0.8:1:8.8;
            end
    
            if i == 2 || i>=4
                levels = -0.4:0.4:2.8;
            end
            if i == 3
                levels = -0.4:0.4:5.6;
            end
            %hold on;contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1);
            %hold on;contour(cvprl,cvprp,out.',0.8:1:8.8,'k--','Linewidth',1);
            hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);%7,'k--','Linewidth',1);%contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf./vthpl{i}(25)^2,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf,F.vprp,outva.',4:2:28,'k:')
            % figure out how to do shared colorbars
            %colorbar;
            caxis([-7 -0.5])
            if counter<7
                set(gca,'TickLength',[0.02 0.02],'XTickLabel',[],'XMinorTick','on');
            else
                xlabel(xnames{i},'interpreter','latex');
                set(gca,'TickLength',[0.02 0.02],'XMinorTick','on')
            end
            
            ylabel(ynames{i},'interpreter','latex')
    
            axis equal
            %O5+
            if i==2 || i>=4
            xlim([ -15 15]);
            ylim([0 15]);
            end
    
            if i ==3
            %He
            xlim([ -10 10]);
            ylim([0 10]);
            end
    
            if i==1
            %H
            xlim([ -7 7]);
            ylim([0 7]);
            end
    
            if i==7
                xlim([-20 20]);
                ylim([0 20]);
            end
            set(gca,'fontsize', 16);
            %legend({'','','$v_{A}$','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')
            %title(['$t/\tau_{A}=' n2s(F.t(n-dn+1)) '$t/\tau_{A}=' n2s(F.t(n+dn)) '$']);
            % include time as a textbox
            %title(['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
            
            hold off
            counter = counter +1;

            %set(gca,'Units','normalized','Position',[0.15,0.15,0.9,0.9]);
            plotTickLatex2D('ylabeldx',0,'xlabeldy',0,'xtickdy',0);
        end
    end




          drawnow;
          fig = gcf;
          fig.PaperPositionMode = 'auto';
          exportname = [dir,'pdf/paper','.pdf'];
          %exportgraphics(fig,exportname,'ContentType','vector');

    if unscalew
        for i = 1:length(mass)
            F.vprl{i} = F.vprl{i} ./ vthtot3d{i};
            F.vprp{i} = F.vprp{i} ./ vthtot3d{i};
        end
    end

save([ savebase 'PlotDFs6-0-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot', '-v7.3');


end



if multispecies

    set(0,'DefaultLineLineWidth',1.0);
    set(0,'DefaultTextInterpreter', 'latex');
    set(0,'DefaultAxesFontSize',16);
    set(0,'DefaultTextFontSize',16);
    set(0,'DefaultAxesLineWidth',1.0);

    dir =  ['../simulations/' name '/saved-plots/f0/'];

    pnum = 1;
    %nplt = [10:2:430];
    specs = [1 3 2]


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);

    tplt = [0.5 9 14.5];
    dtplt = 0.5;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    vthtot3d = {};
    vprl = {};
    vprp = {};
    % Perpendicular diffusion coefficient
    if unscalew
        for i = 1:length(mass)
            vthtot3d{i}(1,1,:) = vthtot{i};
            F.vprl{i} = F.vprl{i} .* vthtot3d{i};
            F.vprp{i} = F.vprp{i} .* vthtot3d{i};
        end
    end


    figure(pnum);set(gcf,'Color','white');

    for i = specs
        for ttt = 1:length(tplt)
            
            f0 = m(F.f0{i})./ int_dist(m(F.vprl{i}),m(F.vprp{i}),m(F.f0{i}));
            vprl{i} = m(F.vprl{i}); % should be same for all times if unscaled
            vprp{i} = m(F.vprp{i});
    
            vprpn = vprp{i};
    
            if i==2 || i>=4
                liminds = find(log10(f0./vprpn)<-7);
                f0(liminds) = 0;
            end
            if i ==3
                liminds = find(log10(f0./vprpn)<-7);
                f0(liminds) = 0;
            end
            contourf(vprl{i},vprp{i},log10(f0./vprpn).',15);set(gca,'YDir','normal');
            %[out,outva,vprlhalf] = resonanceContours(vprp,vprl,vthpl{i}(25),vthpp{i}(25));
            [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
            cvprl = cvprl./m4(vthtot{i});
            cvprp = cvprp./m4(vthtot{i});
            if unscalew
                cvprl = cvprl.*m4(vthtot{i});
                cvprp = cvprp.*m4(vthtot{i});
            end
            %disp(cvprl)
            %disp(cvprp)
            if i==1
                levels = -0.4:1.2:11.6;%0.8:1:8.8;
            end
    
            if i == 2 || i>=4
                levels = -0.4:0.4:2.8;
            end
            if i == 3
                levels = -0.4:0.4:5.6;
            end
            %hold on;contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1);
            %hold on;contour(cvprl,cvprp,out.',0.8:1:8.8,'k--','Linewidth',1);
            hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);%7,'k--','Linewidth',1);%contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf./vthpl{i}(25)^2,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf,F.vprp,outva.',4:2:28,'k:')
            colorbar;caxis([-7 -0.5])

            xlabel(xnames{i},'interpreter','latex')
            ylabel(ynames{i},'interpreter','latex')
    
            axis equal
            %O5+
            if i==2 || i>=4
            xlim([ -15 15]);
            ylim([0 15]);
            end
    
            if i ==3
            %He
            xlim([ -10 10]);
            ylim([0 10]);
            end
    
            if i==1
            %H
            xlim([ -7 7]);
            ylim([0 7]);
            end
    
            if i==7
                xlim([-20 20]);
                ylim([0 20]);
            end
            set(gca,'fontsize', 16);
            %legend({'','','$v_{A}$','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')
            %title(['$t/\tau_{A}=' n2s(F.t(n-dn+1)) '$t/\tau_{A}=' n2s(F.t(n+dn)) '$']);
            title(['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
            
            hold off
    
          drawnow;
          fig = gcf;
          fig.PaperPositionMode = 'auto';
          exportname = [dir,'pdf/multi','.pdf'];
          exportgraphics(fig,exportname,'ContentType','vector')
        end
    end

    if unscalew
        for i = 1:length(mass)
            F.vprl{i} = F.vprl{i} ./ vthtot3d{i};
            F.vprp{i} = F.vprp{i} ./ vthtot3d{i};
        end
    end


end


if animateF

    set(0,'DefaultLineLineWidth',1.0);
    set(0,'DefaultTextInterpreter', 'latex');
    set(0,'DefaultAxesFontSize',16);
    set(0,'DefaultTextFontSize',16);
    set(0,'DefaultAxesLineWidth',1.0);
    i = species; 

    dir =  ['../simulations/' name '/saved-plots/ani-f0-' fnames{i} '/'];
    %if i ==1
    %    dir = ['../simulations/' name '/saved-plots/ani-f0-p/'];
    %end
    %if i ==2
    %    dir = ['../simulations/' name '/saved-plots/ani-f0-o5/'];
    %end
    %if i ==3
    %    dir = ['../simulations/' name '/saved-plots/ani-f0-he/'];
    %end

    pnum = 1;
    %nplt = [10:2:430];
    nplt = [10:2:212];
    
    if unscalew
        vthtot3d(1,1,:) = vthtot{i};
        F.vprl{i} = F.vprl{i} .* vthtot3d;
        F.vprp{i} = F.vprp{i} .* vthtot3d;
    end

    for n=nplt
      if (n<10)
        numlab = ['000',num2str(n)];
      elseif (n<100)
        numlab = ['00',num2str(n)];
      elseif (n<1000)
        numlab = ['0',num2str(n)];
      else
        numlab = num2str(n);
      end

      clf;
      foutlab = [dir,'fp.',numlab,'.png'];
      exportname = [dir,'pdf/fp.',numlab,'.pdf'];


        m = @(d) mean(d(:,:,n-dn+1:n+dn),3); %n=dn:dn+1:F.n-dn;
        %m2 = @(d) mean(d(:,n-dn+1:n+dn),2);
        m2 = @(d) mean(d(:,:,n-dn+1:n+dn),3);
        m3 = @(d) mean(d(:,n-dn+1:n+dn),2);
        m4 = @(d) mean(d(n-dn+1:n+dn),1);
        figure(pnum);set(gcf,'Color','white');
        f0 = m(F.f0{i})./ int_dist(m2(F.vprl{i}),m2(F.vprp{i}),m(F.f0{i}));
        vprl = m2(F.vprl{i});
        vprp = m2(F.vprp{i});

        vprpn = vprp;

        if i==2 || i>=4
            liminds = find(log10(f0./vprpn)<-7);
            f0(liminds) = 0;
        end
        if i ==3
            liminds = find(log10(f0./vprpn)<-7);
            f0(liminds) = 0;
        end
        contourf(vprl,vprp,log10(f0./vprpn).',15);set(gca,'YDir','normal');
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl,vthpl{i}(25),vthpp{i}(25));
        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
        cvprl = cvprl./m4(vthtot{i});
        cvprp = cvprp./m4(vthtot{i});
        if unscalew
            cvprl = cvprl.*m4(vthtot{i});
            cvprp = cvprp.*m4(vthtot{i});
        end
        %disp(cvprl)
        %disp(cvprp)
        if i==1
            levels = -0.4:1.2:11.6;%0.8:1:8.8;
        end

        if i == 2 || i>=4
            levels = -0.4:0.4:2.8;
        end
        if i == 3
            levels = -0.4:0.4:5.6;
        end
        %hold on;contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1);
        %hold on;contour(cvprl,cvprp,out.',0.8:1:8.8,'k--','Linewidth',1);
        hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);%7,'k--','Linewidth',1);%contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf./vthpl{i}(25)^2,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf,F.vprp,outva.',4:2:28,'k:')
        % vertical line at v_A
        if unscalew
            plot(-1 /vthi(i) *[1 1], [0 20],'r--')
            % vertical line at vth_par
            %plot(- m4(vthpl{i}) *[1 1], [0 20],'-.','Color',[0.4940 0.1840 0.5560])
            % horizontal line at vth_perp
            %plot([-20 20], [1 1] .* m4(vthpp{i}),'m--')
        else
            plot(-1 /(m4(vthtot{i}) * vthi(i)) *[1 1], [-10 10],'r--')
        end
        
        if i ==1
            colorbar;caxis([-9 -0.5])
        end
        if i == 2 || i>=4
            colorbar;caxis([-7 -0.5])
        end
        if i ==3
            colorbar;caxis([-7 -0.5])
        end
        %xlabel('$w_\|/v_{th0,Fe^{9+}}$','interpreter','latex')
        %ylabel('$w_\perp/v_{th0,Fe^{9+}}$','interpreter','latex')
        xlabel(xnames{i},'interpreter','latex')
        ylabel(ynames{i},'interpreter','latex')

        axis equal
        %O5+
        if i==2 || i>=4
        xlim([ -15 15]);
        ylim([0 15]);
        end

        if i ==3
        %He
        xlim([ -10 10]);
        ylim([0 10]);
        end

        if i==1
        %H
        xlim([ -7 7]);
        ylim([0 7]);
        end

        if i==7
            xlim([-20 20]);
            ylim([0 20]);
        end
        set(gca,'fontsize', 16);
        %legend({'','','$v_{A}$','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')
        %title(['$t/\tau_{A}=' n2s(F.t(n-dn+1)) '$t/\tau_{A}=' n2s(F.t(n+dn)) '$']);
        title(['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
        
        hold off

      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      disp(foutlab)
      exportgraphics(fig,foutlab,'Resolution',600)
      %exportname = [dirsave,'tplotT' '.pdf'];
      exportgraphics(fig,exportname,'ContentType','vector')
    end

    if unscalew
        F.vprl{i} = F.vprl{i} ./ vthtot3d;
        F.vprp{i} = F.vprp{i} ./ vthtot3d;
    end

end



if plotFonly2D
    pnum = 1;
    nplt = [10:10:210];
    i = species; 
    if unscalew
        vthtot3d(1,1,:) = vthtot{i};
        F.vprl{i} = F.vprl{i} .* vthtot3d;
        F.vprp{i} = F.vprp{i} .* vthtot3d;
    end
        for n=nplt; m = @(d) mean(d(:,:,n-dn+1:n+dn),3); %n=dn:dn+1:F.n-dn;
        %m2 = @(d) mean(d(:,n-dn+1:n+dn),2);
        m2 = @(d) mean(d(:,:,n-dn+1:n+dn),3);
        m3 = @(d) mean(d(:,n-dn+1:n+dn),2);
        m4 = @(d) mean(d(n-dn+1:n+dn),1);
        figure(pnum);set(gcf,'Color','white');
        f0 = m(F.f0{i})./ int_dist(m2(F.vprl{i}),m2(F.vprp{i}),m(F.f0{i}));
        vprl = m2(F.vprl{i});
        vprp = m2(F.vprp{i});

        vprpn = vprp;

        if i==2
            liminds = find(log10(f0./vprpn)<-7.5);
            f0(liminds) = 0;
        end
        if i ==3
            liminds = find(log10(f0./vprpn)<-7.5);
            f0(liminds) = 0;
        end
        contourf(vprl,vprp,log10(f0./vprpn).',15);set(gca,'YDir','normal');
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl,vthpl{i}(25),vthpp{i}(25));
        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
        cvprl = cvprl./m4(vthtot{i});
        cvprp = cvprp./m4(vthtot{i});
        if unscalew
            cvprl = cvprl.*m4(vthtot{i});
            cvprp = cvprp.*m4(vthtot{i});
        end
        %disp(cvprl)
        %disp(cvprp)
        if i==1
            levels = -0.4:1.2:9.2;%0.8:1:8.8;
        end

        if i == 2
            levels = -0.4:0.4:2.8;
        end
        if i == 3
            levels = -0.4:0.4:5.2;
        end
        %hold on;contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1);
        %hold on;contour(cvprl,cvprp,out.',0.8:1:8.8,'k--','Linewidth',1);
        hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);%7,'k--','Linewidth',1);%contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf./vthpl{i}(25)^2,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf,F.vprp,outva.',4:2:28,'k:')
        % vertical line at v_A
        if unscalew
            plot(-1 /vthi(i) *[1 1], [0 20],'r--')
            % vertical line at vth_par
            plot(- m4(vthpl{i}) *[1 1], [0 20],'-.','Color',[0.4940 0.1840 0.5560])
            % horizontal line at vth_perp
            plot([-20 20], [1 1] .* m4(vthpp{i}),'m--')
        else
            plot(-1 /(m4(vthtot{i}) * vthi(i)) *[1 1], [-10 10],'r--')
        end
        
        colorbar;caxis([-9 -0.5])
        xlabel('$w_\|$','interpreter','latex')
        ylabel('$w_\perp$','interpreter','latex')

        axis equal
        %O5+ unscaled axes
        if i==2
        xlim([ -15 15]);
        ylim([0 15]);
        end

        if i ==3
        %He
        xlim([ -10 10]);
        ylim([0 10]);
        end

        if i==1
        %H
        xlim([ -7 7]);
        ylim([0 7]);
        end
        set(gca,'fontsize', 16);
        legend({'','','$v_{A}$','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')
        %title(['$t/\tau_{A}=' n2s(F.t(n-dn+1)) '$t/\tau_{A}=' n2s(F.t(n+dn)) '$']);
        title(['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
        
        hold off
        drawnow;pause(0.2);end%end
    if unscalew
        F.vprl{i} = F.vprl{i} ./ vthtot3d;
        F.vprp{i} = F.vprp{i} ./ vthtot3d;
    end
end

if plotF
    figure;set(gcf,'Color','white');
    betaplot = 1; % vprp vprl are in units of thermal velocity
    betaplot2 = 1;
    %nplt =  [25];  %[  218  219 220]; %i.e. from initial spec number 
    nplt=[356;]
    %nplt = [48    81   114   147   180   213   246   279   322   356];
    i=species;  %species
    %disp(size(F.vprl{i}));
    %disp(size(F.vprp{i}));
    %disp(size(F.f0{i}));
    %for i = 1:length(P.vprpmaxav)
        for n=nplt; m = @(d) mean(d(:,:,n-dn+1:n+dn),3); %n=dn:dn+1:F.n-dn;
            %m2 = @(d) mean(d(:,n-dn+1:n+dn),2);
            m2 = @(d) mean(d(:,:,n-dn+1:n+dn),3);
            m3 = @(d) mean(d(:,n-dn+1:n+dn),2);
            m4 = @(d) mean(d(n-dn+1:n+dn),1);
            f0 = m(F.f0{i})./ int_dist(m2(F.vprl{i}),m2(F.vprp{i}),m(F.f0{i}));
            vprl = m3(F.vprl{i});
            vprp = m2(F.vprp{i});
        %disp(size(vprl));
        %disp(size(vprp));
        subplot(411)
        vprpn = vprp;
        %disp(size(F.f0{i}))
        %disp('vprp is')
        %disp(vprp);
        %disp('F.vprp is')
        %disp(size(F.vprp{i}));
        %disp('F.vprl is')
        %disp(size(F.vprl{i}));
        contourf(vprl,vprp,log10(f0./vprpn).',15);set(gca,'YDir','normal');
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl,vthpl{i}(25),vthpp{i}(25));
        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(F.vprp{i}(:,:,25).*vthpp{i}(25)^2,F.vprl{i}(:,:,25).*vthpl{i}(25)^2);
        %[out,outva,vprlhalf] = resonanceContours(F.vprp{i}(:,:,25)*vthtot{i}(25),F.vprl{i}(:,:,25).*vthtot{i}(25));
        %vprlhalf = vprlhalf./m4(vthtot{i});

        %contourf(vprlhalf,vprp,outva.',15);set(gca,'YDir','normal');
        cvprl = cvprl./m4(vthtot{i});
        cvprp = cvprp./m4(vthtot{i});
        %disp(cvprl)
        %disp(cvprp)
        if i==1
            levels = -0.4:1.2:9.2%0.8:1:8.8;
        else
            levels = -0.4:0.4:2.8
        end
        %hold on;contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1);
        %hold on;contour(cvprl,cvprp,out.',0.8:1:8.8,'k--','Linewidth',1);
        hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);%7,'k--','Linewidth',1);%contour(vprlhalf,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf./vthpl{i}(25)^2,vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf,F.vprp,outva.',4:2:28,'k:')
        colorbar;caxis([-9 -0.5])
        xlabel('$w_\|$','interpreter','latex')
        ylabel('$w_\perp$','interpreter','latex')
        %[val, idx] =  max(f0./vprpn)
        %disp(val);
        %disp('min_vprl');
        %disp(outva);
        %disp('min_vprl scaled');
        %disp(outva/vthpl{i}(25)^2);
        %

        %
        
        % flat top characteristic of stochastic heating
        fprp = trapz(vprl,f0,1)./vprp/2;
        betaplot2 = trapz(vprp,2*fprp.*vprp.^3);
        disp('T_perp');
        disp(betaplot2);
        disp(vthpp{i}(25)^2);
        betaplot2 = vthpp{i}(25);
        disp('perp drift');
        disp(trapz(vprp,2*fprp.*vprp.^2));
        disp(trapz(vprp,fprp));
        disp(trapz(vprp,0.5*4*betaplot2^-1.5/sqrt(pi).*exp(-vprp.^2/betaplot2)));

        % maxwellian fit from heatingAndBeamFromVDF
        fprp = trapz(vprl,f0,1); fprl = trapz(vprp,f0,2);
        %[VL,VP]= ndgrid(vprl, vprp);
        oneDMaxl = @(ps,vl) 1*ps(1)/(pi^0.5*ps(2)).*exp(-(vl-ps(3)).^2./ps(2).^2); 
        oneDMaxp = @(ps,vp) 2*ps(1)/(ps(2)^2).*vp.*exp(-vp.^2./ps(2).^2);
        options = optimoptions('lsqnonlin','Algorithm','levenberg-marquardt');
        fitp = lsqnonlin( @(ps) oneDMaxp(ps,vprp) - fprp, [1 1] ,[],[],options);
        fitl = lsqnonlin( @(ps) oneDMaxl(ps,vprl) - fprl, [1 1 0] ,[],[],options);
        fff = oneDMaxp(fitp,vprp);%.*oneDMaxl(fitl,vprl);
        
        %disp(fitp(1))
        %disp(fitp(2)^2);
        %disp(trapz(vprp,fprp));
        %disp(trapz(vprp,fff));
        %disp(trapz(vprp,oneDMaxp([1 sqrt(betaplot2)],vprp)));
        %disp(trapz(vprp,0.5*4*betaplot2^-1.5/sqrt(pi).*exp(-vprp.^2/betaplot2).*vprp*2));

        subplot(412)
        betaplot1 = trapz(vprl,vprl.^2.*fprl);
        disp('T_par');
        disp(betaplot1);
        disp(vthpl{i}(25)^2);
        disp('par drift');
        disp(trapz(vprl,vprl.*fprl));
        %plot(vprl,fprl,vprl,1/sqrt(pi*betaplot1)*exp(-vprl.^2/betaplot1),'--')
        plot(vprl,fprl,vprl,oneDMaxl(fitl,vprl),'--');
        xlabel('$w_\|$','interpreter','latex')
        hold on;plot(-1*[1 1],1e10*[-1 1],'k:',1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:',-1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
        ylim(1*[-0. 0.7])
        xlim([-4 4])

        subplot(413)

        plot(vprp,fprp./vprp/2,vprp,fff./vprp/2,'--')
        %plot(vprp,fprp./vprp/2,vprp,oneDMaxp([1 sqrt(betaplot2)],vprp)./vprp/2,'--')
        %plot(vprp,fprp./vprp/2,vprp,0.5*4*betaplot2^-1.5/sqrt(pi).*exp(-vprp.^2/betaplot2),'--')

        %plot(vprp,fprp,vprp,fff,'--')
        %plot(vprp,fprp,vprp,oneDMaxp([1 sqrt(betaplot2)],vprp),'--')
        %plot(vprp,fprp,vprp,0.5*4*betaplot2^-1.5/sqrt(pi).*exp(-vprp.^2/betaplot2),'--')
        xlabel('$w_\perp$','interpreter','latex')
        hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
        ylim(1.2*[0 1])
        %ylim([0 0.3])
        %ylim(1.2*[0 0.05])
        %xlim([0.01 2.5])
        xlim([0.01 6.0])
        %
        subplot(414)
        [fe,egrd] = convertToEthetaDist(permute(vprl,[2 1]),vprp,f0);
        eg = egrd(egrd>5);
        loglog(egrd,fe,egrd,sqrt(pi/betaplot^3)*egrd.*exp(-egrd./betaplot),'--',eg,1*(eg./eg(1)).^-10,'k:')
        ylim([1e-11,2])
    
        % % subplot(411);
        title(['$t=' n2s(F.t(n-dn+1)) '$ to $t=' n2s(F.t(n+dn)) '$']);
        drawnow;end%ginput(1);end%
    %end


end


% init from imbal2-prod
heatip = {};
heatil = {};
for i = 1:length(P.vprpmaxav)
   heatip{i} = 0;%mean(F.edv_prp{i}(:,:,1:5),3);
   heatil{i} = 0;%mean(F.edv_prl{i}(:,:,1:5),3);
end
% save('saved-analysis/initDR-imbal2-prod.mat','heatip','heatil');
%load('saved-analysis/initDR-imbal2-prod.mat','heatip','heatil');
for i = 1:length(P.vprpmaxav)
    F.edv_prp{i} = (F.edv_prp{i}-heatip{i})/nrm(i); % vprp because histogram gives vprp*F
    F.edv_prl{i} = (F.edv_prl{i}-heatil{i})/nrm(i);
end
dn = 20;
if plotHeat
%     nrm=1;
vthtot3d = {};

if unscalew
    for i = 1:length(mass)
        vthtot3d{i}(1,1,:) = vthtot{i}(230:441);
        F.vprl{i} = F.vprl{i} .* vthtot3d{i};
        F.vprp{i} = F.vprp{i} .* vthtot3d{i};
    end
end
for i = 1:length(P.vprpmaxav)
    pnums = [2 3];

    if i ==1
        dir = ['../simulations/' name '/saved-plots/edotw/p/'];
        xlab = '$w_\|/v_{th0,p}$'
        ylab = '$w_\perp/v_{th0,p}$'
    end
    if i ==2
        dir = ['../simulations/' name '/saved-plots/edotw/o5/'];
        xlab = '$w_\|/v_{th0,O^{5+}}$'
        ylab = '$w_\perp/v_{th0,O^{5+}}$'
    end
    if i ==3
        dir = ['../simulations/' name '/saved-plots/edotw/he/'];
        xlab = '$w_\|/v_{th0,He^{++}}$'
        ylab = '$w_\perp/v_{th0,He^{++}}$'
    end
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp.^2.*F.f0;
        eprl = 0.5.*(F.vprl.').^2.*F.f0;
        %output from spectrum.cpp computes E.w/v_A, and bins it according
        %to w/vthi0... So want these vprp and vprl here to be unscaled. Can
        %then scale axes how you want, knowing that the values of the plot
        %are in terms of alfven speed. Or can also rescale that according
        %to vth or current vth, but could be confusing/non intuitive to have a changing
        %color scale
        F.edv_prp{i} = grad3(eprp,F.t)/nrmdfdt;
        F.edv_prl{i} = grad3(eprl,F.t)/nrmdfdt;
        clear eprp eprl
    end
    prpmax = 1;max(max(max(F.edv_prp{i})))/5;
    prlmax = 0.05;max(max(max(F.edv_prl{i})))/2;

    nplt = [250:20:420];
    for n=nplt; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);%n=dn:dn+1:F.n-dn; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);
        m4 = @(d) mean(d(n-dn+1:n+dn),1);
        m3 = @(d) mean(d(:,n-dn+1:n+dn),2);
          if (n<10)
            numlab = ['000',num2str(n)];
          elseif (n<100)
            numlab = ['00',num2str(n)];
          elseif (n<1000)
            numlab = ['0',num2str(n)];
          else
            numlab = num2str(n);
          end
    
          clf;
          foutlab = [dir,'fp.',numlab,'.png'];
          exportname = [dir,'pdf/fp.',numlab,'.pdf'];
        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
        cvprl = cvprl./m4(vthtot{i});
        cvprp = cvprp./m4(vthtot{i});
        if unscalew
            cvprl = cvprl.*m4(vthtot{i});
            cvprp = cvprp.*m4(vthtot{i});
        end
        if i==1
            levels = -0.4:1.2:11.6;%0.8:1:8.8;
        end

        if i == 2
            levels = -0.4:0.4:2.8;
        end
        if i == 3
            levels = -0.4:0.4:5.6;
        end

    figure(pnums(1));set(gcf,'Color','white');
    subplot(211)
    imagesc(m(F.vprl{i}),m(F.vprp{i}),m(F.edv_prp{i}).');set(gca,'YDir','normal')
    prpmax = 0.8*max(max(max(m(F.edv_prp{i}))));
	clim(prpmax*[-1 1])
        hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);
    % vertical line at v_A
    if unscalew
        %plot(-1 /vthi(i) *[1 1], [0 20],'r--')
        % vertical line at vth_par
        plot(- m4(vthpl{i}) *[1 1], [0 20],'-.','Color',[0.4940 0.1840 0.5560])
        % horizontal line at vth_perp
        plot([-20 20], [1 1] .* m4(vthpp{i}),'m--')
    end
    xlabel(xlab,'interpreter','latex')
    ylabel(ylab,'interpreter','latex')


    %O5+ unscaled axes
    if i==2
        xlim([ -10 10]);
        ylim([0 10]);
    end

    if i ==3
    %He
        xlim([ -6 6]);
        ylim([0 6]);
    end

    if i==1
    %H
        xlim([ -4 4]);
        ylim([0 4]);
    end
    %xlim([-2 2])
    %ylim([0 2])
    set(gca,'fontsize', 16);
    legend({'','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')
    %title(['$t/\tau_{A}=' n2s(F.t(n-dn+1)) '$t/\tau_{A}=' n2s(F.t(n+dn)) '$']);


    %axis equal
    colormap jet;colorbar 
    hold off
    subplot(212)
    imagesc(m(F.vprl{i}),m(F.vprp{i}),m(F.edv_prl{i}).');set(gca,'YDir','normal')
    xlabel(xlab,'interpreter','latex')
    ylabel(ylab,'interpreter','latex')
    title('$\partial Q_\parallel/\partial w_{\perp} \partial w_{\parallel}$','interpreter','latex')
    prlmax = 0.8*max(max(max(m(F.edv_prl{i}))));
    clim(prlmax*[-1 1])

        hold on;
    % vertical line at v_A
    if unscalew
        plot(-1 /vthi(i) *[1 1], [0 20],'r--')
        % vertical line at vth_par
        plot(- m4(vthpl{i}) *[1 1], [0 20],'-.','Color',[0.4940 0.1840 0.5560])
        % horizontal line at vth_perp
        plot([-20 20], [1 1] .* m4(vthpp{i}),'m--')
    else
        plot(-1 /(m4(vthtot{i}) * vthi(i)) *[1 1], [-10 10],'r--')
    end

    %O5+ unscaled axes
    if i==2
        xlim([ -10 10]);
        ylim([0 10]);
    end

    if i ==3
    %He
        xlim([ -6 6]);
        ylim([0 6]);
    end

    if i==1
    %H
        xlim([ -4 4]);
        ylim([0 4]);
    end
    %xlim([-4 4])
    %ylim([0 3])
    set(gca,'fontsize', 16);
    legend({'$v_{A}$','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')

    colormap jet;colorbar 
    hold off
    subplot(211)
    %figure(pnums(2))
    %subplot(211)
    %plot(m(F.vprl{i}),sum(m(F.edv_prl{i}),2),m(F.vprl{i}),sum(m(F.edv_prp{i}),2))%, F.vprl,sum(F.edv_prp(:,:,1),2),'k--')
    %xlabel('$w_\|$','interpreter','latex')
%     ylim([-50000 100000])
    %subplot(212)
    %semilogx(m(F.vprp{i}),sum(m(F.edv_prl{i}),1),m(F.vprp{i}),sum(m(F.edv_prp{i}),1))%, F.vprp,sum(F.edv_prp(:,:,1),1),'k--')
    %xlim([0.1 4])
    %xlabel('$w_\perp$','interpreter','latex')
    %legend({'$Q_\|$','$Q_\perp$'},'interpreter','latex')
%     ylim(2e4*[-1 1])
    figure(pnums(1))
    set(gcf,'Color','w')
    %title(['$t=' n2s(F.t(n-dn+1)) '$ to $t=' n2s(F.t(n+dn)) '$']);
    %title('$Q_\perp$','interpreter','latex')
    title([ '$t/\tau_{A}=' n2s(round(m3(F.t),2)) '\quad \partial Q_\perp/\partial w_{\perp} \partial w_{\parallel}$'],'interpreter','latex');
    set(gca,'fontsize', 16);
    drawnow;%ginput(1);end%pause(0.2);end


      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      %exportgraphics(fig,exportname,'ContentType','vector')
    end
    if unscalew
        F.vprl{i} = F.vprl{i} ./ vthtot3d{i};
        F.vprp{i} = F.vprp{i} ./ vthtot3d{i};
    end
end
end


dn=15;
if plotHeatAllTogether
%     nrm=1;
    pnums = [4 5];
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp{i}.^2.*F.f0{i};
        eprl = 0.5.*(F.vprl{i}).^2.*F.f0{i};
        F.edv_prp{i} = grad3(eprp,F.t)./nrmdfdt(i);
        F.edv_prl{i} = grad3(eprl,F.t)./nrmdfdt(i);
        clear eprp eprl
    end
    prpmax = 1;max(max(max(F.edv_prp{i})))/5;
    prlmax = 0.05;max(max(max(F.edv_prl{i})))/2;
    
    smooth = @(f) filter((1/5)*ones(1,5),1,f); 
    for n=[dn:dn+1:F.n-dn F.n-dn]; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);
%         m = @(d) mean(d(:,:,tstrt:end),3);
            m2 = @(d) mean(d(:,:,n-dn+1:n+dn),3);
            m3 = @(d) mean(d(:,:,n-dn+1:n+dn),3);
            vprl = m3(F.vprl{i});
            vprp = m2(F.vprp{i});
    figure(pnums(2))
    subplot(411)
    semilogx(vprp,smooth(sum(m(F.edv_prp{i}),1)),'Color',tcol(F.t(n)))
    xlabel('$w_\perp$','interpreter','latex')
    ylabel('$Q_\perp$','Interpreter','latex')
    xlim([0.1 4])
    title(['$t=' num2str(F.t(n)) '$'],'Interpreter','latex')
    hold on
    subplot(412)
    semilogx(vprp,sum(m(F.edv_prl{i}),1),'Color',tcol(F.t(n)))
    xlabel('$w_\perp$','interpreter','latex')
    ylabel('$Q_\|$','Interpreter','latex')
    xlim([0.1 4])
    hold on
    subplot(413)
    plot(vprl,sum(m(F.edv_prp{i}),2),'Color',tcol(F.t(n)))
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$Q_\perp$','Interpreter','latex')
    hold on
    subplot(414)
    plot(vprl,sum(m(F.edv_prl{i}),2),'Color',tcol(F.t(n)))
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$Q_\|$','Interpreter','latex')
    hold on
    drawnow;end
end



vresltn = P.nspec_prpav./P.vprpmaxav;
% Compute Dpp from dfdt = d/de(Dpp dfde)
wp = permute(F.vprp{i},[2 1 3]);
%disp(size(wp));
wp(1,:,:)=1e-4;
%prlrang = F.vprl{i}>0.5*(3-sqrt(5))/sqrt(0.3); % Changing the number here changes the sh
%disp(size(prlrange))
%smprl = @(f) squeeze(sum(f(prlrang,:,:),1));
% picks out resonant parallel resonant velocities - ignore for now
smprl = @(f) squeeze(sum(f(:,:,:),1));
smprlall = @(f) squeeze(sum(f(:,:,:),1));
nrmf = 1./F.vprp{i};nrmf(1)=1e-4;
fE = smprl(nrmf.*F.f0{i}./nprtl(i));
fEall = smprlall(nrmf.*F.f0{i}./nprtl(i));
dfdt = grad3(nrmf.*F.f0{i},F.t)./nrmdfdt(i);
dfEdt = smprl(dfdt);
dfEdtall = smprlall(dfdt);
dfdw = dbydw2(fE,wp);
dfdwall = dbydw2(fE,wp);

%disp(size(dfEdt));
% This is A1 from Cerri

Dpp = cumtrap2(wp(:,1,:).*dfEdt,wp)./(1./wp(:,1,:).*dfdw)./vresltn(i);
DppAll = cumtrap2(wp(:,1,:).*dfEdtall,wp)./(1./wp(:,1,:).*dfdwall)./vresltn(i);
%Dpp = cumtrapz(wp,wp.*dfEdt,1)./(1./wp.*dfdw)./vresltn(i);
%DppAll = cumtrapz(wp,wp.*dfEdtall,1)./(1./wp.*dfdwall)./vresltn(i);
% This is Cerri A8 from Vasquez
dQ = wp(:,1,:).^2.*dfEdt;
dQall = wp(:,1,:).^2.*dfEdtall;

if plotDprpFromF

    vresltn = P.nspec_prpav./P.vprpmaxav;
    % Compute Dpp from dfdt = d/de(Dpp dfde). Same as Figure_FandDprp
    wp = permute(F.vprp{i},[2 1 3]);
    wp(1,:,:)=1e-4;
    % picks out resonant parallel resonant velocities - ignore for now
    %prlrang = F.vprl{i}>-10.*(3-sqrt(5))/sqrt(0.3); % Changing the number here changes the sh
    %smprl = @(f) squeeze(sum(f(prlrang,:,:),1));
    smprl = @(f) squeeze(sum(f(:,:,:),1));
    smprlall = @(f) squeeze(sum(f(:,:,:),1));
    nrmf = 1./F.vprp{i};nrmf(1)=1e-4;
    fE = smprl(nrmf.*F.f0{i}/nprtl(i));
    fEall = smprlall(nrmf.*F.f0{i}/nprtl(i));
    dfdt = grad3(nrmf.*F.f0{i},F.t)/nrmdfdt(i);
    dfEdt = smprl(dfdt);
    dfEdtall = smprlall(dfdt);
    dfdw = dbydw2(fE,wp);
    dfdwall = dbydw2(fEall,wp);
    
    % This is A1 from Cerri
    DppF = cumtrap2(wp(:,1,:).*dfEdt,wp)./(1./wp(:,1,:).*dfdw)./vresltn(i);
    DppFAll = cumtrap2(wp(:,1,:).*dfEdtall,wp)./(1./wp(:,1,:).*dfdwall)./vresltn(i);
    %Dpp = cumtrapz(wp,wp.*dfEdt,1)./(1./wp.*dfdw)/vresltn;
    %DppAll = cumtrapz(wp,wp.*dfEdtall,1)./(1./wp.*dfdwall)/vresltn;
    % This is Cerri A8 from Vasquez
    dQ = wp(:,1,:).^2.*dfEdt;
    dQall = wp(:,1,:).^2.*dfEdtall;

    figure
    set(gcf,'Color','w')
    % Perpendicular diffusion coefficient
%     % Movie
%     for n=tstrt+dn+1:(dn+1):F.n; m = @(d) mean(d(:,n-dn:n+dn),2);
%     subplot(311)
%     semilogx(F.vprp,m(fE)./sum(m(fE)),'k',F.vprp,m(fEall)./sum(m(fEall)),'r')
%     ylabel('$f$','Interpreter','latex')
%     xlim([0.05 4])
%     subplot(312)
%     loglog(F.vprp,m(Dpp),'k',F.vprp,-m(Dpp),'k--',F.vprp,20*F.vprp.^2,'k:')
%     hold on
%     loglog(F.vprp,m(DppAll),'r',F.vprp,-m(DppAll),'r--')
%     hold off
%     xlim([0.05 4])
%     ylim([1e-2 2e2])
%     ylabel('$D_\perp$','Interpreter','latex')
%     subplot(313)
%     semilogx(F.vprp,m(dQ),'k',F.vprp,m(dQall),'r',F.vprp,0*F.vprp,'k:')
% %     hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
%     xlim([0.05 4])
%     ylabel('$q_\perp$','Interpreter','latex')
%     subplot(311);title(['t=' num2str(F.t(n+1))]);ginput(1);end

    % All on one plot
    %nplt = [25];tstrt+dn+1:(dn+1):F.n-dn;
    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m2 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m3 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);
    filt = @(f) filter((1/10)*ones(1,10),1,f,[],1);
    tplt = [9.5];
    dtplt = 1;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    for ttt = 1:length(tplt)
        vprl = m(F.vprl{i},tav,tavplt(:,ttt));
        vprp = m(F.vprp{i},tav,tavplt(:,ttt));

        loglog(vprp,DppF(:,find(tav>=tavplt(1,ttt) & tav<=tavplt(2,ttt))),'Color',tcol(m3(F.t,tav,tavplt(:,ttt))),'Linewidth',1)
        hold on
        %loglog(vprp,m2(DppF,tav,tavplt(:,ttt)),'Color','red','Linewidth',1)%,vprp,-m2(DppF,tav,tavplt(:,ttt)),'--','Color',tcol(m3(F.t,tav,tavplt(:,ttt))),'Linewidth',1)
        %hold on
        loglog(vprp,m2(filt(DppF),tav,tavplt(:,ttt)),vprp,-(m2(filt(DppF),tav,tavplt(:,ttt))),'--','Color','red','Linewidth',2)
        %inds = find(tav>=tavplt(1,ttt));
        %loglog(vprp,DppF(:,inds(1)),vprp,-DppF(:,inds(1)),'--','Linewidth',2)
        %disp(m2(DppF,tav,tavplt(:,ttt)))
        hold on
    end
    loglog(vprp,20*vprp.^2,'k:')
    %xlim([0.3 4])
    %ylim([5e-2 2e2])    
    ylabel('$D_{\perp\perp}$','Interpreter','latex')
    xlabel('$w_\perp$','Interpreter','latex')
    hold off
end


if plotDprp
    i = species;
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp{i}.^2.*F.f0{i};
        eprl = 0.5.*(F.vprl{i}.').^2.*F.f0{i};
        F.edv_prp{i} = grad3(eprp,F.t)/nrmdfdt(i);
        F.edv_prl{i} = grad3(eprl,F.t)/nrmdfdt(i);
        clear eprp eprl
        pnums = [6 7];
    end
    % heatip = mean(F.edv_prp(:,:,1:2),3);
    % F.edv_prp = (F.edv_prp-heatip)/nrm;
    figure
    filt = @(f) filter((1/10)*ones(1,10),1,f);
    lnm={};
    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    
    tplt = [9.5];
    dtplt = 1;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t
    % Perpendicular diffusion coefficient
    for ttt = 1:length(tplt)
        vprpplot = m(F.vprp{i},tav,tavplt(:,ttt));
        vprlplot = m(F.vprl{i},tav,tavplt(:,ttt));
        f0 = m(F.f0{i},tav,tavplt(:,ttt))./ int_dist(vprlplot,vprpplot,m(F.f0{i},tav,tavplt(:,ttt)));
        fprp = trapz(vprlplot,f0,1)./vprpplot/2;
        dfprp = gradient(fprp,vprpplot(2)-vprpplot(1))/vthi(i);
        dqprp = sum(m(F.edv_prp{i},F.t,tavplt(:,ttt)),1);
        % subplot(311)
        % semilogx(F.vprp,fprp)
        % ylabel('$f$','Interpreter','latex')
        % subplot(312)
        Dpp = -filt(dqprp./dfprp)/(epsin*vthi(i)^2);%*P.beta);
        loglog(vprpplot,Dpp,'-',vprpplot,-Dpp,'--','Color',tcol(tplt(ttt)),'LineWidth',1)
        hold on;
        loglog(vprpplot, 200*vprpplot.^2,'k:');hold off
        %xlim([0.1 4])
        %ylim([1 2e3])
        ylabel('$D_\perp$','Interpreter','latex')
        hold on
    %     subplot(313)
    %     semilogx(F.vprp,dqprp)
    % %     hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
    %     xlim([0.1 4])
    %     ylabel('$q_\perp$','Interpreter','latex')
    %     subplot(311);title(['t=' num2str(tplt(ttt))]);ginput(1);
        drawnow
    end
   
end




end


function  out = int_dist(vprl,vprp,F)
% f itself already includes the wprp factor in the integration dw| wprp dwprp
out = trapz(vprl,trapz(vprp,F,2),1);

end


function [fe,egrd,fetheta,thetag] = convertToEthetaDist(vprl,vprp,F)
% See note DistributionFunctions in imbalanced pegasus Notability.
% Jacobian is just 1/2, so just interpolate to e, theta

vprl = vprl.';
egrd = logspace(-2,log10(max(max(vprp.^2 + vprl.^2))),2000);
thetag = linspace(0,180,361);
[e,theta] = ndgrid(egrd,thetag);

wprli = sqrt(e).*cosd(theta);
wprpi = sqrt(e).*sind(theta);

fetheta = 0.5*interpn(vprl,vprp,F,wprli,wprpi,'spline',0);

fe = trapz(thetag,fetheta,2); 
fe = egrd.'.*fe./trapz(egrd,fe); % This is be the logarithmic distribution



% s=pcolor(thetag,log10(egrd),fetheta);
%     s.EdgeColor='none';s.FaceColor='interp';

end



function out = grad3(fld,tv)
% Time derivative in 3 direction
nt = length(tv);
out = zeros(size(fld));
out(:,:,1)= (fld(:,:,2)-fld(:,:,1))/(tv(2)-tv(1));
for nn = 2:nt-1
    out(:,:,nn) = (fld(:,:,nn+1)-fld(:,:,nn-1))/(tv(nn+1)-tv(nn-1));
end
out(:,:,nt)= (fld(:,:,nt)-fld(:,:,nt-1))/(tv(nt)-tv(nt-1));

end

function df = dbydw(f,w)
% gradient function is shit ? do a loop
dw = w(11)-w(10);
df = zeros(size(f));
for nnn=1:size(f,2)
    df(:,nnn) = gradient(f(:,nnn),dw);
end

end



function df = dbydw2(f,w)
% gradient function is shit ? do a loop
dw = w(11,1,:)-w(10,1,:);
df = zeros(size(f));
for nnn=1:size(f,2)
    df(:,nnn) = gradient(f(:,nnn),dw(nnn));
end

end

function df = cumtrap2(f,w)
% gradient function is shit ? do a loop
df = zeros(size(f));
for nnn=1:size(f,2)
    df(:,nnn) = cumtrapz(w(:,1,nnn),f(:,nnn),1);
end

end



function [out,vprp,vprl,yres] = resonanceContoursMinorIon(qom,momp,beta0,vaprl,vaprp)
% Oblique proton ICW contours for general q/m 
% qom,momp are q/m and m/mp in units of proton mass. beta0 is vth units of distribution you want to plot it on
% y is kprl*di (Isenberg's notation). v in units of va until the end

miny = ((1/qom)^(2/3)-1)^-0.5;
minvl = qom/miny - 1/sqrt(1+miny^2);

% Compute contour function in vprp y, then convert y grid to vprl
% yres = linspace(miny,-0.01,200);
% vprl = -1./sqrt(1+yres.^2) - qom./yres;
% inc = vprl<1; yres = yres(inc);vprl = vprl(inc);
% Compute uniform vprl grid and convert to y
vprl = linspace(minvl+1e-3,vaprl,200*vaprp);
vlsolve = @(y,vl) -vl - 1./sqrt(1+y.^2) + qom./y;
yres = [];yguess = qom/(1+vprl(end));
for lll = length(vprl):-1:1
    yres = [fzero(@(y) vlsolve(y,vprl(lll)),yguess) yres];
    yguess = yres(1);
end

vprp = linspace(0,vaprp,200*vaprp); % Grid out to va
[Y,VP]=ndgrid(yres,vprp);

out = VP.^2+qom.*Y.^(-2).*(qom+2.*Y.^3.*(1+Y.^2).^(-1/2));
% out = VP.^2+(-1+1./Y).^2+2./Y; % non-dispersive
vprl = vprl*sqrt(momp/beta0);
vprp = vprp*sqrt(momp/beta0);


% % Code to check these are correct
% [outold,outva,vprlhalf] = resonanceContours(linspace(0,3.5,200),linspace(-2,2,200));
% 
% figure
% subplot(121)
% contour(vprl,vprp,out.',10,'-k')
% hold on
% contour(vprlhalf,linspace(0,3.5,200),outold.',10,'-b')
% pbaspect([max(vprl)-min(vprl) max(vprp) 1])
% subplot(122)
% plot(vprl,yres,'.-')
% xlabel('$v_\|/v_{\rm th0}$','Interpreter','latex')
% ylabel('$k_{\|,res}d_i$','Interpreter','latex')



end


function [out,outva,vprlhalf] = resonanceContours(vprp,vprl)
% See IC Resonance Conditions.nb notebook
oblique = 1;

vprl = vprl(vprl>0.01);

vprlhalf = vprl;

[vl,vp]=ndgrid(vprl,vprp);
% This is non-dispersive version, propagating at vA
outva = vl.^2+0.365148E1.*(0.182574E1+vl)+vp.^2;
% This is dispersive cold IC resonance at beta=0.3
if ~oblique
out = (0.182574E1.*(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*(0.2E2.* ...
  vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^( ...
  1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(-1/3)+ ...
  0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)) ...
  .^(-1)+0.912871E0.*(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*( ...
  0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+ ...
  3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^( ...
  -1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)+(-1).*(4+(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*( ...
  0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+ ...
  3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^( ...
  -1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)).^2).^(1/2))).^2+vp.^2+(-0.166667E1).*((0.182574E0.*vl+( ...
  -0.230029E0).*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+ ...
  (-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+( ...
  -0.148148E3).*vl.^6).^(1/2)).^(-1/3)+0.144909E0.*vl.^(-1).*( ...
  0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)).^2+((-0.182574E0).*vl+ ...
  0.230029E0.*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+( ...
  -0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+( ...
  -0.148148E3).*vl.^6).^(1/2)).^(-1/3)+(-0.144909E0).*vl.^(-1).*( ...
  0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)+(-2).*(0.182574E0.*vl+( ...
  -0.230029E0).*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+ ...
  (-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+( ...
  -0.148148E3).*vl.^6).^(1/2)).^(-1/3)+0.144909E0.*vl.^(-1).*( ...
  0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)).^(-1)).*(4+( ...
  0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4) ...
  .*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*( ...
  0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(-1/3)+ ...
  0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)) ...
  .^2).^(1/2)+2.*asinh((1/2).*(0.182574E0.*vl+(-0.230029E0).*vl.^( ...
  -1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(-1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)))+(-2).*log(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*( ...
  0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+ ...
  3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^( ...
  -1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)));
else
out = 0.333333E1.*((0.912871E0.*vl.^(-1)+(1/2).*3.^(-1/2).*((-2)+0.1E2.* ...
  vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+ ...
  vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)) ...
  .^(1/3)).^(1/2)+(-1/2).*((-4/3)+0.666667E1.*vl.^(-2)+(-1/3).* ...
  vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(-1/3)+(-1/3).*vl.^(-2).*(0.6E3.* ...
  vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^( ...
  1/2)).^(1/3)+(1/4).*3.^(1/2).*(0.486864E2.*vl.^(-3)+0.146059E2.* ...
  vl.^(-1)).*((-2)+0.1E2.*vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+vl.^6+6.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+ ...
  vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(1/3)).^(-1/2)).^(1/2)).^(-2)+2.*( ...
  0.912871E0.*vl.^(-1)+(1/2).*3.^(-1/2).*((-2)+0.1E2.*vl.^(-2)+ ...
  vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+vl.^6+ ...
  6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)) ...
  .^(1/2)+(-1/2).*((-4/3)+0.666667E1.*vl.^(-2)+(-1/3).*vl.^2.*( ...
  0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.* ...
  vl.^8).^(1/2)).^(-1/3)+(-1/3).*vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)+( ...
  1/4).*3.^(1/2).*(0.486864E2.*vl.^(-3)+0.146059E2.*vl.^(-1)).*((-2) ...
  +0.1E2.*vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*( ...
  0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*( ...
  0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.* ...
  vl.^8).^(1/2)).^(1/3)).^(-1/2)).^(1/2)).*(1+(0.912871E0.*vl.^(-1)+ ...
  (1/2).*3.^(-1/2).*((-2)+0.1E2.*vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+ ...
  vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)) ...
  .^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)).^(1/2)+(-1/2).*((-4/3)+ ...
  0.666667E1.*vl.^(-2)+(-1/3).*vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^( ...
  1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+(-1/3) ...
  .*vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(1/3)+(1/4).*3.^(1/2).*(0.486864E2.* ...
  vl.^(-3)+0.146059E2.*vl.^(-1)).*((-2)+0.1E2.*vl.^(-2)+vl.^2.*( ...
  0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.* ...
  vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).* ...
  (0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)).^(-1/2)).^( ...
  1/2)).^2).^(-1/2))+vp.^2;


end
out = real(out);
end


function inds = restart_overlaps2(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1722 1818] 2433;
inds = [];
startinds = cat(1,[1],rinds);
for inn = 1:4 %1:length(rinds) %for each restart index
    tb = t(rinds(inn)); %find the time of the restart
    ia = find(t(1:rinds(inn))>tb,1);%find the first index before the restart index that has time greater than that just before the restart
    disp(ia);
    inds = [inds ia:rinds(inn)-1]; %append all indices from before restart up until restart
end
for inn = 5:length(rinds) %for each restart index
    tb = t(rinds(inn)); %find the time of the restart
    ia = find(t(startinds(inn):rinds(inn))>tb,1);%find the first index before the restart index that has time greater than that just before the restart
    disp(ia+startinds(inn))
    inds = [inds ia+startinds(inn)-1:rinds(inn)-1]; %append all indices from before restart up until restart
end
inds = setdiff(1:length(t),inds);%returns all indices except those in inds
end



function inds = restart_overlaps3(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1722 1818] 2433;
inds = [];
startinds = cat(1,[1],rinds);
for inn = 1:length(rinds) %for each restart index
    tb = t(rinds(inn)); %find the time of the restart
    ia = find(t(1:rinds(inn))>tb,1);%find the first index before the restart index that has time greater than that just before the restart
    disp(ia);
    inds = [inds ia:rinds(inn)-1]; %append all indices from before restart up until restart
end
inds = setdiff(1:length(t),inds);%returns all indices except those in inds
%disp('restart times are ')
%disp(t(rinds)/(6*48.1802))
end


function inds = restart_overlaps4(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1722 1818] 2433;
inds = [];
startinds = cat(1,[1],rinds);
for inn = [1 2 3 6:length(rinds)]; %1:length(rinds) %for each restart index
    tb = t(rinds(inn)); %find the time of the restart
    ia = find(t(1:rinds(inn))>tb,1);%find the first index before the restart index that has time greater than that just before the restart
    if inn == 7
        ia = find(t(337:rinds(inn))>tb,1);
        ia = ia + 337 -1;
    end
    disp(ia);
    inds = [inds ia:rinds(inn)-1]; %append all indices from before restart up until restart
end
inds = setdiff(1:length(t),inds);%returns all indices except those in inds
disp('restart times are ')
disp(t(rinds([1 2 3 6:18]))/(6*22.0))
end

