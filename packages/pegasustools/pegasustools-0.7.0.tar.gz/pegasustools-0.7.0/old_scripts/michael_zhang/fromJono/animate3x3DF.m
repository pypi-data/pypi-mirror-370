function animate3x3DF
addpath('~/matlab-libs/BrewerMap')
i_b3 = 0;
b_b3 = 0;
i_b0625 = 0;
b_b0625 = 0;
i_b1=1;
b_b1=0;
DoFullCalculation = 0;
loadsave = 1;
copyViaScp=0;

tstrt = 0;%5;%20;
unscalew = 1;
plot3x3 = 1;
animateF = 0;
plotPaper=0;
animate = 0;%1;
edvprp = 0; %C=-8 i0625 b0625 -7 b03 i03
edvprl = 0; %C=-12 i0625 b0625 -10 b03 i03
symlog = 0;
signed = 0; %plot e.g. sign(edvprp) to see faint features/if heating/cooling
zoom = 1;
plot3x2time = 0;
plot3x1 = 0;
frame1=0;


order3x2 = [1 3 2];
%tplt = [0:0.05:8.25]; %i_b0625
%tplt = [8.25];
%tplt = [4.3];
%tplt = [0:0.05:3.8]; %b_b0625
%tplt = [0:0.05:7.7]; %b_b3
%tplt = [7.7];
%tplt = [1.4 9.5];
%tplt = [2.0 7.0];
%tplt = [5.0];
%tplt = [7.95:0.05:15.25];
%tplt = [0:0.05:15.25];
%tplt = [14.5];
%tplt = tas;
%tplt = [0:0.05:3.45];
tplt = [3.45];
dtplt = 0.5;%0.15;%0.5



if i_b3
    name = 'half_tcorr_sim9';
    nums = [0:440];%[0:401 ];%229:312]; % snapshot numbers for which to find spectrum %i_b3
    %nums = [229:440]; %ib3 edv % min 229 for edotvav output
%nums = [0:95];
    ion_start = 38;
end
if b_b3
    name = 'b_b3_sim1';
    nums = [0:222]; % b3 need to redo, since wrong normalizationg by pcc (32 instead of 27)
    ion_start = 35;
end
if i_b0625
    name = 'hb_beta0625';
    nums = [0:213];
    ion_start = 38;
end
if b_b0625
    name = 'b_b0625_sim1';
    nums = [0:76];
    ion_start = 35;
end
if i_b1
    name = 'i_b1_sim1';
    nums = [0:173];
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
    dtf = 10./tauA
end
if b_b0625 || i_b0625
    P.beta=0.0625;
    vol=6*22.0^3;
    tauA = 6*22.0;
    epsin = 4.0;%36.5; % energy injection per volume is different? because of different beta?
    tas = nums*6.6/tauA;
    dtf = 6.6/tauA;
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
if i_b3
    plotorder = [1 3 2];
    plotorder_trunc = [3 2];
end
if i_b1 || b_b1
    plotorder_trunc = [3 2 4 5 6 7 8];
    plotorder = [1 3 2 4 5 6 7 8];
end


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

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%All of above copied from distfuncav just before fullcalc - copy and paste
%again as needed

load(savefolder,'F','P');
disp(F)
F.n = length(F.t);
% 1-D vs. time plots
% % Heating
% s2= @(f) squeeze(sum(sum(f,2),1));
% nprtl = 216*392^3*6;
% plot(F.t,s2(F.f0)/nprtl)
F.t = F.t/tauA;
tstrt = find(F.t>tstrt,1);
dn=10;
% VDFs
%


% get data
if plotPaper


    specs = [1 3 2]


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);

    %tplt = [0.5 7.5 14.2];
    tplt = [0.5 5.0 8.0];
    %tplt = [0.5 4.0 7.0];
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



    counter = 1;
    plotpos = [1 4 7 2 5 8 3 6 9];
    plotf0 = {};

    for ttt = 1:length(tplt)
        for i = specs
            f0 = m(F.f0{i},tav,tavplt(:,ttt))./ int_dist(m(F.vprl{i},tav,tavplt(:,ttt)),m(F.vprp{i},tav,tavplt(:,ttt)),m(F.f0{i},tav,tavplt(:,ttt)));
            if edvprp
                f0 =  m(F.edv_prp{i},tav,tavplt(:,ttt)) %./ int_dist(m(F.vprl{i},tav,tavplt(:,ttt)),m(F.vprp{i},tav,tavplt(:,ttt)),m(F.f0{i},tav,tavplt(:,ttt)));
            else
                if edvprl
                    f0 = m(F.edv_prl{i},tav,tavplt(:,ttt)) %./ int_dist(m(F.vprl{i},tav,tavplt(:,ttt)),m(F.vprp{i},tav,tavplt(:,ttt)),m(F.f0{i},tav,tavplt(:,ttt)));
                end
            end
            vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
            vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
            plotf0{counter} = f0;
        end
    end
    


%save([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot', '-v7.3');


end



if plot3x3
    
% NOTE:
%   plotf0 is normalized such that 
%             SUM[ plotf0*(dvprp/vth0)*(dvprl/vth0) ] = 1
%   actual VDF = plotf0 / (vprp/vth0) * [n/(2*pi*vth0^3)]
%   looks like we've been setting pi*vth0^2 = 1 in our plotting of f(vprp),
%   so that the Maxwellian f(vprp) = exp(-vprp^2/vth^2), so the def'n of
%   f(vprp) = pi vthprp^2 int[ f dvprl ] 
%           = (vthprp/vth0)^2 int[ 0.5*plotf0*(dvprl/vth0)*(vth0/vprp)
%

    clev = [3.12 1.87 1.76];    clevb= [3.21 2.02 1.76];

    %load([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot');

    rebinN  = 250;
    %logfmin = -7.5; logfmax = -0.5;
    logfmin = -7.0; logfmax = -0.5;

    %vmaxarr = { 10,20,20,20,20,20,20 };
    %vmaxplt = { 6,8.5,14,14,14,14,14 };
    vmaxarr = { 10,20,20,20,20,20,20,10 };
    if zoom
        vmaxplt = { 8,20,10,20,20,20,20,8  };
    else
        vmaxplt = { 20,20,20,20,20,20,20,20  };
    end
    if i_b1
        vmaxplt = { 10,10,10,10,10,10,10,10  };
    end
    


    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    if (edvprp || edvprl) & i_b3
        tav = F.t(230:441);
    end

    if zoom
        dir =  ['../simulations/' name '/saved-plots/vdf-zoom/'];
    else
        dir =  ['../simulations/' name '/saved-plots/vdf/'];
    end
    if edvprp
        if frame1
            dir =  ['../simulations/' name '/saved-plots/edvprp-1f/'];
        else
            dir =  ['../simulations/' name '/saved-plots/edvprp/'];
        end
    end
    if edvprl
        if frame1
            dir =  ['../simulations/' name '/saved-plots/edvprl-1f/'];
        else
            dir =  ['../simulations/' name '/saved-plots/edvprl/'];
        end
    end

    pwidth=18.5; pheight=12;
    if i_b3
        %pwidth = 7.0;
        pheight = 4.0;
    end
    width = 5.15/pwidth; height=0.5*(pwidth/pheight)*width; gap = 0.007; offset = 0.0038*pwidth;
    normpos = { [offset,0.74,width,height],[offset+gap+width,0.74,width,height],[offset+(gap+width)*2,0.74,width,height], ...
                [offset,0.42,width,height],[offset+gap+width,0.42,width,height],[offset+(gap+width)*2,0.42,width,height], ...
                [offset,0.10,width,height],[offset+gap+width,0.10,width,height],[offset+(gap+width)*2,0.10,width,height] };
    if i_b3
        %height=(pwidth/pheight)*width;
        normpos = { [offset,0.20,width,height],[offset+gap+width,0.20,width,height],[offset+(gap+width)*2,0.20,width,height]};
    end
    cbpos   = [0.933 0.10 0.0157 0.855];
    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,O^{6+}0}$','$w_\|/v_{\rm th,C^{6+}0}$','$w_\|/v_{\rm th,C^{5+}0}$','$w_\|/v_{\rm th,Mg^{9+}0}$','$w_\|/v_{\rm th,pm0}$'};
    ylab    = { '$w_\perp/v_{\rm th,i0}$','$w_\perp/v_{\rm th,i 0}$','$w_\perp/v_{\rm th,i0}$','$w_\perp/v_{\rm th,i0}$','$w_\perp/v_{\rm th,i0}$','$w_\perp/v_{\rm th,i0}$','$w_\perp/v_{\rm th,i0}$','$w_\perp/v_{\rm th,i0}$' };
    tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };
    levels  = { -0.40:1.2:11.5, -0.4:0.2:3.0, -0.4:0.4:5.6, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0,  -0.40:1.2:11.5 };
    %levels  = { -0.40:0.6:5.6, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0 };
    tposx   = [-4.1,-6.9,-12.5];
    tposxb  = [2.1,4.1,8];
    tposy   = [5.25,7.45,12];
    pick    = [1,3,3];
    splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm O^{6+}}$','$i={\rm C^{6+}}$','$i={\rm C^{5+}}$','$i={\rm Mg^{9+}}$','$i={\rm pm}$'};
    
    if b_b3
        xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,O^{6+}0}$','$w_\|/v_{\rm th,C^{6+}0}$','$w_\|/v_{\rm th,C^{5+}0}$','$w_\|/v_{\rm th,Fe^{9+}0}$'};
        splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm O^{6+}}$','$i={\rm C^{6+}}$','$i={\rm C^{5+}}$','$i={\rm Fe^{9+}}$'};
        levels  = { -0.40:1.2:12.7, -0.4:0.8:6.8, -0.4:0.6:5.0, -0.4:0.8:6.8,-0.4:0.8:6.8,-0.4:0.8:6.8,-0.4:0.8:6.8 };
    end
    if i_b3
        xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$'};
        splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$'};
        levels  = { -0.40:1.2:12.7, -0.4:0.8:6.8, -0.4:0.6:5.0};
    end

    if i_b1
        levels  = { -0.40:2.4:33.2, -0.40:2.4:33.2, -0.40:2.4:33.2, -0.40:2.4:33.2, -0.40:2.4:33.2, -0.40:2.4:33.2, -0.40:2.4:33.2,  -0.40:2.4:33.2 };
    end
    
    if frame1
        dtplt = 0.5*dtf;
    end


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);
    
    size(vthtot{1})
    size(F.vprl{1})

    for i = 1:length(mass)
        vthtot3d{i}(1,1,:) = vthtot{i};
        if (edvprp ||edvprl) & i_b3
            size(F.vprl{i})
            size(vthtot{i})
            F.vprl{i} = F.vprl{i}(:,:,230:441);
            F.vprp{i} = F.vprp{i}(:,:,230:441);
            F.f0{i} = F.f0{i}(:,:,230:441);
            F.edv_prp{i} = F.edv_prp{i}(:,:,230:441);
            F.edv_prl{i} = F.edv_prl{i}(:,:,230:441);
        end
        F.vprl{i} = F.vprl{i} .* vthtot3d{i};
        F.vprp{i} = F.vprp{i} .* vthtot3d{i};
    end

    if edvprp || edvprl
        maxheat=0;
        minheat = 1000000;
        spheat = {};
        for i = 1:length(mass)
            if edvprp
                temp = max(F.edv_prp{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}),[],"all");
                % Remove zeros from the array
                A = abs(F.edv_prp{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}));
                nonZeroElements = A(A > 0);
                if ~isempty(nonZeroElements)
                    mintemp = min(nonZeroElements,[],"all");
                else
                    minValue = []; % Handle the case where all elements are zero
                end
            end
            if edvprl
                temp = max(F.edv_prl{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}),[],"all");
                A = abs(F.edv_prl{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}));
                nonZeroElements = A(A > 0);
                if ~isempty(nonZeroElements)
                    mintemp = min(nonZeroElements,[],"all");
                else
                    minValue = []; % Handle the case where all elements are zero
                end
            end
            spheat{i} = temp;
            minheat = min([mintemp,minheat],[],"all");
            maxheat = max([temp,maxheat],[],"all");
        end
        spheat
        minheat
    end
    for ttt=1:length(tplt)
      if (ttt<10)
        numlab = ['000',num2str(ttt)];
      elseif (ttt<100)
        numlab = ['00',num2str(ttt)];
      elseif (ttt<1000)
        numlab = ['0',num2str(ttt)];
      else
        numlab = num2str(ttt);
      end

      clf;
      foutlab = [dir,'fp.',numlab,'.png'];
      exportname = [dir,'pdf/fp.',numlab,'.pdf'];

    close all
    figure(13); clf; 
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')


    
    for i = 1:length(mass)
        vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
        vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
    end


    counter = 1;
    pcounter = 1;
    for spec=plotorder   % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        %vprpn = vprpq; vprln = vprlq;

        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(spec),mass(spec),P.beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl);
        figure(1);clf; 
        M = contour(cvprl,cvprp,out.',levels{spec});
        close(1);
        if i_b3
            subplot(1,3,counter);
        else
            subplot(3,3,counter);
        end
        f0 = m(F.f0{spec},tav,tavplt(:,ttt))./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
        fprl = trapz(vprpn,f0,2);
        disp(splab(counter));
        disp(trapz(vprln,fprl'));
        disp(trapz(vprln,vprln.*fprl'));
        disp('vthprp')
        disp(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));
        f0 = f0./vpn'/2;
        %size(f0)
        if edvprp
            f0 =  m(F.edv_prp{spec},tav,tavplt(:,ttt)) ./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
        else
            if edvprl
                f0 = m(F.edv_prl{spec},tav,tavplt(:,ttt)) ./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
            end
        end
        %f0 = f0./vpn'/2;
        f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q;
        if edvprp || edvprl
            %caxis([-maxheat,maxheat]);
            if symlog
                s=pcolor(vprlq,vprpq,signedlog10(f0));
            else
                if signed
                    s=pcolor(vprlq,vprpq,sign(f0));
                else
                    s=pcolor(vprlq,vprpq,f0);
                end
            end
            s.EdgeColor='none';s.FaceColor='interp';
            if symlog
                crange = [-1 1]*maxheat; % make symmetric
                crange = round(signedlog10(crange)); % you may choose to round to integer values
                clim(crange); %% represented in signed log10
            else
                if signed
                    crange = [-2 2];
                    clim (crange);
                else
                    clim([-0.3*maxheat,0.3*maxheat]); % linear
                end
            end
            colormap(brewermap([],'RdBu'));%'Spectral'))RdBu
            cmp = colormap;
            cmp = flipud(cmp);
            colormap(cmp);
            hold on; 
            contour(cvprl,cvprp,out.',levels{spec},'--k','linewidth',1);
            %plot([-1 -1]/sqrt(P.beta)*oovth(spec),[0 15],'r--','linewidth',1);
            hold off;
            %
        else
            liminds = find(log10(f0)<logfmin); f0(liminds) = 0;
            if i_b3
                contourf(vprlq,vprpq,log10(f0),logfmin:0.5:logfmax);%5:logfmax);
            else
                contourf(vprlq,vprpq,log10(f0),logfmin:0.4:logfmax);%5:logfmax);
            end
            C = caxis; caxis([logfmin,logfmax]);
            hold on; 
            contour(cvprl,cvprp,out.',levels{spec},'--k','linewidth',1);
            %plot([-1 -1]/sqrt(P.beta)*oovth(spec),[0 15],'r--','linewidth',1);
            hold off;
        end
        axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
        set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{counter});
        set(gca,'Layer','top');
        xlabel(xlab{counter},'interpreter','latex');
        if counter == 8
            if zoom
                text(-7.6,6.4,splab{counter},'Fontsize',10);
            end
        else
            text(-19,16,splab{counter},'Fontsize',10);
        end
        if zoom
            if counter == 1
                text(-7.6,6.4,splab{counter},'Fontsize',10);
            end
            if counter == 2
                text(-9.5,8,splab{counter},'Fontsize',10);
            end
        end

        xticks([-15 -10 -5 0 5 10 15]);
        %xticklabels({'$0$','$10^{-3}$','$10^{-2}$','$10^{-1}$'})
        if counter==1 || counter==4 || counter==7
            ylabel(ylab{spec},'interpreter','latex');
            if counter==1
                if i_b3
                    plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025,'ytickdx',0,'ylabeldx',0);
                else
                    plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.02);
                end
                %if i_b3
                %else
                    title([n2s(tplt(ttt)) '$\tau_A$']);
                %end
            end
            if counter==4
                plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.02);
            end
            if counter==7
                plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.01);
            end

        else
            set(gca,'YTickLabel',[]);
            if i_b3
                plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025);
            else
                plotTickLatex2D('xlabeldy',0.02);
            end
            if counter==2 %|| (counter==1 & i_b3)
                if edvprp
                    if symlog
                        if b_b3 || i_b3
                            title('$\log 10^{7} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                        %elseif i_b3
                        %    title(['$\log 10^{7} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $ at '  n2s(tplt(ttt)) '$\tau_A$'] ,'interpreter','latex');
                        else
                            title('$\log 10^{8} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                        end
                    else
                        %if i_b3
                        %    title(['$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $'  n2s(tplt(ttt)) '$\tau_A$'],'interpreter','latex');
                        %else
                            title('$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                        %end
                    end
                end
                if edvprl
                    if symlog
                        if b_b3  || i_b3
                            title('$ \log 10^{10} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                        %elseif i_b3
                        %    title(['$ \log 10^{10} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $ at '  n2s(tplt(ttt)) '$\tau_A$'] ,'interpreter','latex');
                        else
                            title('$ \log 10^{12} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                        end
                    else
                        %if i_b3
                        %    title(['$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $'  n2s(tplt(ttt)) '$\tau_A$'],'interpreter','latex');
                        %else
                            title('$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                        %end
                    end
                end
            end

            %plotTickLatex2D('xlabeldy',0.02,'ytickdx',0.002,'ylabeldx',-0.02);
        end
        if counter==length(mass) 
                cb = colorbar;
                
                set(cb,'Position',cbpos,'Ticklength',0.01);
                %set(cb,'Position',cbpos{spec},'Ticklength',0.04);
                if edvprp ||edvprl
                    %colormap(brewermap([],'RdBu'))%'Spectral'))RdBu
                    %cmp = colormap;
                    %cmp = flipud(cmp);
                    %colormap(cmp);
                    %if edvprp
                    %    title(cb,'$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %else
                        %cb.Title.String = '$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $'
                        %title(cb,'$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %end
                    if symlog
                        % create ticks, ticklabels
                        % choose nticks as desired 
                        nticks = 4;
                        ticklabels = logspace(0,max(crange),nticks);
                        ticklabels = [-flip(ticklabels) 0 ticklabels]; % make symmetric
                        % set Ticks and TickLabels
                        %cb('Ticks',signedlog10(ticklabels),'TickLabels',ticklabels)
                        signedlog10(ticklabels);
                        ticklabels;
                        %cb.Ticks = signedlog10(ticklabels);
                        %cb.TickLabels = ticklabels;
                    end
                else
                    title(cb,'$\langle f_i\rangle $','interpreter','latex');
                    cb.Ticks=[-7 -6 -5 -4 -3 -2 -1];
                    cb.TickLabels={'$10^{-7}$','$10^{-6}$','$10^{-5}$','$10^{-4}$', ...
                        '$10^{-3}$','$10^{-2}$','$10^{-1}$'};
                end
                cb.TickLabelInterpreter='latex';
                cb.FontSize=10; cb.LineWidth=1;
            %text(25,10,['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
        end

        if i_b3
            %counter = counter +3;
            counter = counter +1;
            pcounter = pcounter+1;
        else
            counter = counter +1;
        end
    end


    if animate
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      disp(foutlab)
      exportgraphics(fig,foutlab,'Resolution',600)
      exportgraphics(fig,exportname,'ContentType','vector')
    end

    end

    

end  % plotnbr==3 3x3





if plot3x2time
    
% NOTE:
%   plotf0 is normalized such that 
%             SUM[ plotf0*(dvprp/vth0)*(dvprl/vth0) ] = 1
%   actual VDF = plotf0 / (vprp/vth0) * [n/(2*pi*vth0^3)]
%   looks like we've been setting pi*vth0^2 = 1 in our plotting of f(vprp),
%   so that the Maxwellian f(vprp) = exp(-vprp^2/vth^2), so the def'n of
%   f(vprp) = pi vthprp^2 int[ f dvprl ] 
%           = (vthprp/vth0)^2 int[ 0.5*plotf0*(dvprl/vth0)*(vth0/vprp)
%

    clev = [3.12 1.87 1.76];    clevb= [3.21 2.02 1.76];

    %load([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot');

    rebinN  = 250;
    %logfmin = -7.5; logfmax = -0.5;
    logfmin = -7.0; logfmax = -0.5;

    %vmaxarr = { 10,20,20,20,20,20,20 };
    %vmaxplt = { 6,8.5,14,14,14,14,14 };
    vmaxarr = { 10,20,20,20,20,20,20 };
    if zoom
        vmaxplt = { 8,20,10,20,20,20,20  };
    else
        vmaxplt = { 20,20,20,20,20,20,20  };
    end
    


    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    if (edvprp || edvprl) & i_b3
        tav = F.t(230:441);
    end

    if zoom
        dir =  ['../simulations/' name '/saved-plots/vdf-zoom/'];
    else
        dir =  ['../simulations/' name '/saved-plots/vdf/'];
    end
    if edvprp
        if frame1
            dir =  ['../simulations/' name '/saved-plots/edvprp-1f/'];
        else
            dir =  ['../simulations/' name '/saved-plots/edvprp/'];
        end
    end
    if edvprl
        if frame1
            dir =  ['../simulations/' name '/saved-plots/edvprl-1f/'];
        else
            dir =  ['../simulations/' name '/saved-plots/edvprl/'];
        end
    end

    pwidth=18.5; pheight=6.5;
    width = 4.75/pwidth; height=0.5*(pwidth/pheight)*width; gap = 0.05; offset = 0.0028*pwidth;
    normpos = { [offset,0.55,width,height],[offset+gap+width,0.55,width,height],[offset+(gap+width)*2,0.55,width,height], ...
                [offset,0.13,width,height],[offset+gap+width,0.13,width,height],[offset+(gap+width)*2,0.13,width,height] };

    cbpos   = [0.933 0.13 0.0157 0.42+height];%0.855];
    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$'};
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,O^{5+}0}$','$w_\perp/v_{\rm th,\alpha 0}$'};
    tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };
    levels  = { -0.40:1.2:11.5, -0.4:0.2:3.0, -0.4:0.4:5.6, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0 };
    %levels  = { -0.40:0.6:5.6, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0 };
    tposx   = [-4.1,-6.9,-12.5];
    tposxb  = [2.1,4.1,8];
    tposy   = [5.25,7.45,12];
    pick    = [1,3,3];
    splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$'};
    
    if b_b3
        %xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,O^{6+}0}$','$w_\|/v_{\rm th,C^{6+}0}$','$w_\|/v_{\rm th,C^{5+}0}$','$w_\|/v_{\rm th,Fe^{9+}0}$'};
        %splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm O^{6+}}$','$i={\rm C^{6+}}$','$i={\rm C^{5+}}$','$i={\rm Fe^{9+}}$'};
        levels  = { -0.40:1.2:12.7, -0.4:0.8:6.8, -0.4:0.6:5.0, -0.4:0.8:6.8,-0.4:0.8:6.8,-0.4:0.8:6.8,-0.4:0.8:6.8 };
    end
    if i_b3
        %xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$'};
        %splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$'};
        levels  = { -0.40:1.2:12.7, -0.4:0.8:6.8, -0.4:0.6:5.0};
    end
    
    if frame1
        dtplt = 0.5*dtf;
    end


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);
    
    size(vthtot{1})
    size(F.vprl{1})

    for i = 1:length(mass)
        vthtot3d{i}(1,1,:) = vthtot{i};
        if (edvprp ||edvprl) & i_b3
            size(F.vprl{i})
            size(vthtot{i})
            F.vprl{i} = F.vprl{i}(:,:,230:441);
            F.vprp{i} = F.vprp{i}(:,:,230:441);
            F.f0{i} = F.f0{i}(:,:,230:441);
            F.edv_prp{i} = F.edv_prp{i}(:,:,230:441);
            F.edv_prl{i} = F.edv_prl{i}(:,:,230:441);
        end
        F.vprl{i} = F.vprl{i} .* vthtot3d{i};
        F.vprp{i} = F.vprp{i} .* vthtot3d{i};
    end

    if edvprp || edvprl
        maxheat=0;
        minheat = 1000000;
        spheat = {};
        for i = 1:length(mass)
            if edvprp
                temp = max(F.edv_prp{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}),[],"all");
                % Remove zeros from the array
                A = abs(F.edv_prp{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}));
                nonZeroElements = A(A > 0);
                if ~isempty(nonZeroElements)
                    mintemp = min(nonZeroElements,[],"all");
                else
                    mintemp = []; % Handle the case where all elements are zero
                end
            end
            if edvprl
                temp = max(F.edv_prl{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}),[],"all");
                A = abs(F.edv_prl{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}));
                nonZeroElements = A(A > 0);
                if ~isempty(nonZeroElements)
                    mintemp = min(nonZeroElements,[],"all");
                else
                    mintemp = []; % Handle the case where all elements are zero
                end
            end
            spheat{i} = temp;
            minheat = min([mintemp,minheat],[],"all");
            maxheat = max([temp,maxheat],[],"all");
        end
        spheat
        minheat
    end

    % all times on same plot
    close all
    figure(13); clf; 
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')
    counter = 1;


    for ttt=1:length(tplt)
      if (ttt<10)
        numlab = ['000',num2str(ttt)];
      elseif (ttt<100)
        numlab = ['00',num2str(ttt)];
      elseif (ttt<1000)
        numlab = ['0',num2str(ttt)];
      else
        numlab = num2str(ttt);
      end

      %clf;
      foutlab = [dir,'fp.',numlab,'.png'];
      exportname = [dir,'pdf/fp.',numlab,'.pdf'];


    % different times on each plot  
    %close all
    %figure(13); clf; 
    %set(gcf,'Color',[1 1 1]);
    %set(gcf,'Units','centimeters');
    %set(gcf,'Position',[1,1,pwidth,pheight]);
    %set(gcf,'PaperPositionMode','auto');
    %set(gcf,'renderer','Painters')
    %counter = 1;
    %pcounter = 1;

    
    for i = 1:length(mass)
        vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
        vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
    end



    for spec=order3x2;   % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        %vprpn = vprpq; vprln = vprlq;

        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(spec),mass(spec),P.beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl);
        figure(1);clf; 
        M = contour(cvprl,cvprp,out.',levels{spec});
        close(1);
        subplot(2,3,counter);
        f0 = m(F.f0{spec},tav,tavplt(:,ttt))./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
        f0 = f0./vpn'/2;
        size(f0)
        if edvprp
            f0 =  m(F.edv_prp{spec},tav,tavplt(:,ttt)) ./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
        else
            if edvprl
                f0 = m(F.edv_prl{spec},tav,tavplt(:,ttt)) ./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
            end
        end
        %f0 = f0./vpn'/2;
        size(f0)
        f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q;
        if edvprp || edvprl
            %caxis([-maxheat,maxheat]);
            if symlog
                s=pcolor(vprlq,vprpq,signedlog10(f0));
            else
                s=pcolor(vprlq,vprpq,f0);
            end
            s.EdgeColor='none';s.FaceColor='interp';
            if symlog
                crange = [-1 1]*maxheat; % make symmetric
                crange = round(signedlog10(crange)); % you may choose to round to integer values
                clim(crange); %% represented in signed log10
                crange
            else
                clim([-0.3*maxheat,0.3*maxheat]); % linear
            end
            colormap(brewermap([],'RdBu'))%'Spectral'))RdBu
            cmp = colormap;
            cmp = flipud(cmp);
            colormap(cmp);
            hold on; 
            contour(cvprl,cvprp,out.',levels{spec},'--k','linewidth',1);
            %plot([-1 -1]/sqrt(P.beta)*oovth(spec),[0 15],'r--','linewidth',1);
            hold off;
            %
        else
            liminds = find(log10(f0)<logfmin); f0(liminds) = 0;
            if i_b3
                contourf(vprlq,vprpq,log10(f0),logfmin:0.5:logfmax);%5:logfmax);
            else
                contourf(vprlq,vprpq,log10(f0),logfmin:0.4:logfmax);%5:logfmax);
            end
            C = caxis; caxis([logfmin,logfmax]);
            hold on; 
            contour(cvprl,cvprp,out.',levels{spec},'--k','linewidth',1);
            %plot([-1 -1]/sqrt(P.beta)*oovth(spec),[0 15],'r--','linewidth',1);
            hold off;
        end
        axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
        set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{counter});
        set(gca,'Layer','top');
        %text(-19,16,splab{counter},'Fontsize',10);
        if zoom
            if counter == 1 || counter == 4
                text(-7.2,4.8,splab{counter},'Fontsize',10);
                text(-7.2,6.4,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
            end
            if counter == 2 || counter == 5
                text(-9,6,splab{counter},'Fontsize',10);
                text(-9,8,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
            end
            if counter == 3 || counter == 6
                text(-18,12,splab{counter},'Fontsize',10);
                text(-18,16,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
            end
        else
            text(-19,16,splab{counter},'Fontsize',10);
            text(-19,16,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
        end

        xticks([-15 -10 -5 0 5 10 15]);
    %xticklabels({'$0$','$10^{-3}$','$10^{-2}$','$10^{-1}$'})
        ylabel(ylab{spec},'interpreter','latex');
        if counter==1 
            set(gca,'XTickLabel',[]);
            plotTickLatex2D('ytickdx',0.002,'ylabeldx',0.0);
        end
        if counter==2  || counter==3
            set(gca,'XTickLabel',[]);
            plotTickLatex2D('ytickdx',0.002,'ylabeldx',0.005);
        end
        if counter==4 
            xlabel(xlab{counter},'interpreter','latex');
            plotTickLatex2D('xtickdy',-0.008,'xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',0.00);

        end
        if counter==5  || counter==6
            xlabel(xlab{counter},'interpreter','latex');
            plotTickLatex2D('xtickdy',-0.008,'xlabeldy',0.02,'ytickdx',0.002,'ylabeldx',0.005);
        end
        if counter==6 
            cb = colorbar;
            
            set(cb,'Position',cbpos,'Ticklength',0.01);
            %set(cb,'Position',cbpos{spec},'Ticklength',0.04);
            if edvprp ||edvprl
                %colormap(brewermap([],'RdBu'))%'Spectral'))RdBu
                %cmp = colormap;
                %cmp = flipud(cmp);
                %colormap(cmp);
                %if edvprp
                %    title(cb,'$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                %else
                    %cb.Title.String = '$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $'
                    %title(cb,'$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                %end
                if symlog
                    % create ticks, ticklabels
                    % choose nticks as desired 
                    nticks = 4;
                    ticklabels = logspace(0,max(crange),nticks);
                    ticklabels = [-flip(ticklabels) 0 ticklabels]; % make symmetric
                    % set Ticks and TickLabels
                    %cb('Ticks',signedlog10(ticklabels),'TickLabels',ticklabels)
                    %signedlog10(ticklabels)
                    %ticklabels
                    %cb.Ticks = signedlog10(ticklabels);
                    %cb.TickLabels = ticklabels;
                end
            else
                title(cb,'$\langle f_i\rangle $','interpreter','latex');
                cb.Ticks=[-7 -6 -5 -4 -3 -2 -1];
                cb.TickLabels={'$10^{-7}$','$10^{-6}$','$10^{-5}$','$10^{-4}$', ...
                    '$10^{-3}$','$10^{-2}$','$10^{-1}$'};
            end
            cb.TickLabelInterpreter='latex';
            cb.FontSize=10; cb.LineWidth=1;
        %text(25,10,['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
        end




        if counter==2 %|| (counter==1 & i_b3)
            if edvprp
                if symlog
                    if b_b3 || i_b3
                        title('$\log 10^{7} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %elseif i_b3
                    %    title(['$\log 10^{7} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $ at '  n2s(tplt(ttt)) '$\tau_A$'] ,'interpreter','latex');
                    else
                        title('$\log 10^{8} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    end
                else
                    %if i_b3
                    %    title(['$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $'  n2s(tplt(ttt)) '$\tau_A$'],'interpreter','latex');
                    %else
                        title('$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %end
                end
            end
            if edvprl
                if symlog
                    if b_b3  || i_b3
                        title('$ \log 10^{10} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %elseif i_b3
                    %    title(['$ \log 10^{10} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $ at '  n2s(tplt(ttt)) '$\tau_A$'] ,'interpreter','latex');
                    else
                        title('$ \log 10^{12} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    end
                else
                    %if i_b3
                    %    title(['$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $'  n2s(tplt(ttt)) '$\tau_A$'],'interpreter','latex');
                    %else
                        title('$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %end
                end
            end
        end

        counter = counter +1;
    end
 


    if animate
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      disp(foutlab)
      exportgraphics(fig,foutlab,'Resolution',600)
      exportgraphics(fig,exportname,'ContentType','vector')
    end

    end

    

end    %3x2


if plot3x1
    
% NOTE:
%   plotf0 is normalized such that 
%             SUM[ plotf0*(dvprp/vth0)*(dvprl/vth0) ] = 1
%   actual VDF = plotf0 / (vprp/vth0) * [n/(2*pi*vth0^3)]
%   looks like we've been setting pi*vth0^2 = 1 in our plotting of f(vprp),
%   so that the Maxwellian f(vprp) = exp(-vprp^2/vth^2), so the def'n of
%   f(vprp) = pi vthprp^2 int[ f dvprl ] 
%           = (vthprp/vth0)^2 int[ 0.5*plotf0*(dvprl/vth0)*(vth0/vprp)
%

    clev = [3.12 1.87 1.76];    clevb= [3.21 2.02 1.76];

    %load([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot');

    rebinN  = 250;
    %logfmin = -7.5; logfmax = -0.5;
    logfmin = -7.0; logfmax = -0.5;

    %vmaxarr = { 10,20,20,20,20,20,20 };
    %vmaxplt = { 6,8.5,14,14,14,14,14 };
    vmaxarr = { 10,20,20,20,20,20,20 };
    if zoom
        vmaxplt = { 8,20,10,20,20,20,20  };
    else
        vmaxplt = { 20,20,20,20,20,20,20  };
    end
    


    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    if (edvprp || edvprl) & i_b3
        tav = F.t(230:441);
    end

    if zoom
        dir =  ['../simulations/' name '/saved-plots/vdf-zoom/'];
    else
        dir =  ['../simulations/' name '/saved-plots/vdf/'];
    end
    if edvprp
        if frame1
            dir =  ['../simulations/' name '/saved-plots/edvprp-1f/'];
        else
            dir =  ['../simulations/' name '/saved-plots/edvprp/'];
        end
    end
    if edvprl
        if frame1
            dir =  ['../simulations/' name '/saved-plots/edvprl-1f/'];
        else
            dir =  ['../simulations/' name '/saved-plots/edvprl/'];
        end
    end

    pwidth=18.5; pheight=4.0;
    width = 4.75/pwidth; height=0.5*(pwidth/pheight)*width; gap = 0.05; offset = 0.0028*pwidth;
    normpos = { [offset,0.2,width,height],[offset+gap+width,0.2,width,height],[offset+(gap+width)*2,0.2,width,height] };

    cbpos   = [0.933 0.2 0.0157 height];%0.855];
    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$'};
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,O^{5+}0}$','$w_\perp/v_{\rm th,\alpha 0}$'};
    tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };
    levels  = { -0.40:1.2:11.5, -0.4:0.2:3.0, -0.4:0.4:5.6, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0 };
    %levels  = { -0.40:0.6:5.6, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0, -0.4:0.2:3.0 };
    tposx   = [-4.1,-6.9,-12.5];
    tposxb  = [2.1,4.1,8];
    tposy   = [5.25,7.45,12];
    pick    = [1,3,3];
    splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$'};
    
    if b_b3
        %xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,O^{6+}0}$','$w_\|/v_{\rm th,C^{6+}0}$','$w_\|/v_{\rm th,C^{5+}0}$','$w_\|/v_{\rm th,Fe^{9+}0}$'};
        %splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm O^{6+}}$','$i={\rm C^{6+}}$','$i={\rm C^{5+}}$','$i={\rm Fe^{9+}}$'};
        levels  = { -0.40:1.2:12.7, -0.4:0.8:6.8, -0.4:0.6:5.0, -0.4:0.8:6.8,-0.4:0.8:6.8,-0.4:0.8:6.8,-0.4:0.8:6.8 };
    end
    if i_b3
        %xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$'};
        %splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$'};
        levels  = { -0.40:1.2:12.7, -0.4:0.8:6.8, -0.4:0.6:5.0};
    end
    
    if frame1
        dtplt = 0.5*dtf;
    end


    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);
    
    size(vthtot{1})
    size(F.vprl{1})

    for i = 1:length(mass)
        vthtot3d{i}(1,1,:) = vthtot{i};
        if (edvprp ||edvprl) & i_b3
            size(F.vprl{i})
            size(vthtot{i})
            F.vprl{i} = F.vprl{i}(:,:,230:441);
            F.vprp{i} = F.vprp{i}(:,:,230:441);
            F.f0{i} = F.f0{i}(:,:,230:441);
            F.edv_prp{i} = F.edv_prp{i}(:,:,230:441);
            F.edv_prl{i} = F.edv_prl{i}(:,:,230:441);
        end
        F.vprl{i} = F.vprl{i} .* vthtot3d{i};
        F.vprp{i} = F.vprp{i} .* vthtot3d{i};
    end

    if edvprp || edvprl
        maxheat=0;
        minheat = 1000000;
        spheat = {};
        for i = 1:length(mass)
            if edvprp
                temp = max(F.edv_prp{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}),[],"all");
                % Remove zeros from the array
                A = abs(F.edv_prp{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}));
                nonZeroElements = A(A > 0);
                if ~isempty(nonZeroElements)
                    mintemp = min(nonZeroElements,[],"all");
                else
                    mintemp = []; % Handle the case where all elements are zero
                end
            end
            if edvprl
                temp = max(F.edv_prl{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}),[],"all");
                A = abs(F.edv_prl{i}./int_dist(F.vprl{i}(:,:,1),F.vprp{i}(:,:,1),F.f0{i}));
                nonZeroElements = A(A > 0);
                if ~isempty(nonZeroElements)
                    mintemp = min(nonZeroElements,[],"all");
                else
                    mintemp = []; % Handle the case where all elements are zero
                end
            end
            spheat{i} = temp;
            minheat = min([mintemp,minheat],[],"all");
            maxheat = max([temp,maxheat],[],"all");
        end
        spheat
        minheat
    end

    % all times on same plot
    %close all
    %%figure(13); clf; 
    %set(gcf,'Color',[1 1 1]);
    %set(gcf,'Units','centimeters');
    %set(gcf,'Position',[1,1,pwidth,pheight]);
    %set(gcf,'PaperPositionMode','auto');
    %set(gcf,'renderer','Painters')
    %counter = 1;


    for ttt=1:length(tplt)
      if (ttt<10)
        numlab = ['000',num2str(ttt)];
      elseif (ttt<100)
        numlab = ['00',num2str(ttt)];
      elseif (ttt<1000)
        numlab = ['0',num2str(ttt)];
      else
        numlab = num2str(ttt);
      end

      clf;
      foutlab = [dir,'fp.',numlab,'.png'];
      exportname = [dir,'pdf/fp.',numlab,'.pdf'];


    % different times on each plot  
    close all
    figure(13); clf; 
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')
    counter = 1;
    pcounter = 1;

    
    for i = 1:length(mass)
        vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
        vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
    end



    for spec=order3x2;   % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        %vprpn = vprpq; vprln = vprlq;

        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(spec),mass(spec),P.beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl);
        figure(1);clf; 
        M = contour(cvprl,cvprp,out.',levels{spec});
        close(1);
        subplot(2,3,counter);
        f0 = m(F.f0{spec},tav,tavplt(:,ttt))./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
        f0 = f0./vpn'/2;
        size(f0)
        if edvprp
            f0 =  m(F.edv_prp{spec},tav,tavplt(:,ttt)) ./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
        else
            if edvprl
                f0 = m(F.edv_prl{spec},tav,tavplt(:,ttt)) ./ int_dist(m(F.vprl{spec},tav,tavplt(:,ttt)),m(F.vprp{spec},tav,tavplt(:,ttt)),m(F.f0{spec},tav,tavplt(:,ttt)));
            end
        end
        %f0 = f0./vpn'/2;
        size(f0)
        f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q;
        if edvprp || edvprl
            %caxis([-maxheat,maxheat]);
            if symlog
                s=pcolor(vprlq,vprpq,signedlog10(f0));
            else
                s=pcolor(vprlq,vprpq,f0);
            end
            s.EdgeColor='none';s.FaceColor='interp';
            if symlog
                crange = [-1 1]*maxheat; % make symmetric
                crange = round(signedlog10(crange)); % you may choose to round to integer values
                clim(crange); %% represented in signed log10
                crange
            else
                clim([-0.3*maxheat,0.3*maxheat]); % linear
            end
            colormap(brewermap([],'RdBu'))%'Spectral'))RdBu
            cmp = colormap;
            cmp = flipud(cmp);
            colormap(cmp);
            hold on; 
            contour(cvprl,cvprp,out.',levels{spec},'--k','linewidth',1);
            %plot([-1 -1]/sqrt(P.beta)*oovth(spec),[0 15],'r--','linewidth',1);
            hold off;
            %
        else
            liminds = find(log10(f0)<logfmin); f0(liminds) = 0;
            if i_b3
                contourf(vprlq,vprpq,log10(f0),logfmin:0.5:logfmax);%5:logfmax);
            else
                contourf(vprlq,vprpq,log10(f0),logfmin:0.4:logfmax);%5:logfmax);
            end
            C = caxis; caxis([logfmin,logfmax]);
            hold on; 
            contour(cvprl,cvprp,out.',levels{spec},'--k','linewidth',1);
            %plot([-1 -1]/sqrt(P.beta)*oovth(spec),[0 15],'r--','linewidth',1);
            hold off;
        end
        axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
        set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{counter});
        set(gca,'Layer','top');
        %text(-19,16,splab{counter},'Fontsize',10);
        if zoom
            if counter == 1
                text(-7.2,6.4,splab{counter},'Fontsize',10);
                %text(-7.2,6.4,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
            end
            if counter == 2 
                text(-9,8,splab{counter},'Fontsize',10);
                %text(-9,8,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
            end
            if counter == 3 
                text(-18,16,splab{counter},'Fontsize',10);
                %text(-18,16,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
            end
        else
            text(-19,16,splab{counter},'Fontsize',10);
            text(-19,16,[n2s(tplt(ttt)) '$\tau_A$'],'Fontsize',10);
        end

        xticks([-15 -10 -5 0 5 10 15]);
    %xticklabels({'$0$','$10^{-3}$','$10^{-2}$','$10^{-1}$'})
        ylabel(ylab{spec},'interpreter','latex');
        if counter==1 
            xlabel(xlab{counter},'interpreter','latex');
            %plotTickLatex2D('xtickdy',-0.008,'xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',0.00);
            plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025,'ytickdx',0,'ylabeldx',0);

        end
        if counter==2  || counter==3
            xlabel(xlab{counter},'interpreter','latex');
            %plotTickLatex2D('xtickdy',-0.008,'xlabeldy',0.02,'ytickdx',0.002,'ylabeldx',0.005);
            plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025,'ytickdx',0,'ylabeldx',0.005);
        end
        if counter==3
            cb = colorbar;
            
            set(cb,'Position',cbpos,'Ticklength',0.01);
            %set(cb,'Position',cbpos{spec},'Ticklength',0.04);
            if edvprp ||edvprl
                %colormap(brewermap([],'RdBu'))%'Spectral'))RdBu
                %cmp = colormap;
                %cmp = flipud(cmp);
                %colormap(cmp);
                %if edvprp
                %    title(cb,'$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                %else
                    %cb.Title.String = '$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $'
                    %title(cb,'$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                %end
                if symlog
                    % create ticks, ticklabels
                    % choose nticks as desired 
                    nticks = 4;
                    ticklabels = logspace(0,max(crange),nticks);
                    ticklabels = [-flip(ticklabels) 0 ticklabels]; % make symmetric
                    % set Ticks and TickLabels
                    %cb('Ticks',signedlog10(ticklabels),'TickLabels',ticklabels)
                    %signedlog10(ticklabels)
                    %ticklabels
                    %cb.Ticks = signedlog10(ticklabels);
                    %cb.TickLabels = ticklabels;
                end
            else
                title(cb,'$\langle f_i\rangle $','interpreter','latex');
                cb.Ticks=[-7 -6 -5 -4 -3 -2 -1];
                cb.TickLabels={'$10^{-7}$','$10^{-6}$','$10^{-5}$','$10^{-4}$', ...
                    '$10^{-3}$','$10^{-2}$','$10^{-1}$'};
            end
            cb.TickLabelInterpreter='latex';
            cb.FontSize=10; cb.LineWidth=1;
        %text(25,10,['$t/\tau_{A}=' n2s(m3(F.t)) '$'],'interpreter','latex');
        end




        if counter==2 %|| (counter==1 & i_b3)
            if edvprp
                if symlog
                    if b_b3 || i_b3
                        title('$\log 10^{7} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %elseif i_b3
                    %    title(['$\log 10^{7} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $ at '  n2s(tplt(ttt)) '$\tau_A$'] ,'interpreter','latex');
                    else
                        title('$\log 10^{8} \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    end
                else
                    %if i_b3
                    %    title(['$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $'  n2s(tplt(ttt)) '$\tau_A$'],'interpreter','latex');
                    %else
                        title('$ \partial^{2}Q_{\perp} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %end
                end
            end
            if edvprl
                if symlog
                    if b_b3  || i_b3
                        title('$ \log 10^{10} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %elseif i_b3
                    %    title(['$ \log 10^{10} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $ at '  n2s(tplt(ttt)) '$\tau_A$'] ,'interpreter','latex');
                    else
                        title('$ \log 10^{12} \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    end
                else
                    %if i_b3
                    %    title(['$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $'  n2s(tplt(ttt)) '$\tau_A$'],'interpreter','latex');
                    %else
                        title('$ \partial^{2}Q_{\parallel} / \partial w_{\parallel} \partial w_{\perp} $','interpreter','latex');
                    %end
                end
            end
        end

        counter = counter +1;
    end
 


    if animate
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      disp(foutlab)
      exportgraphics(fig,foutlab,'Resolution',600)
      exportgraphics(fig,exportname,'ContentType','vector')
    end

    end

    

end    %3x1




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


function out = signedlog10(in)
    % naive signed-log
    %out = sign(in).*log10(abs(in));
    
    % modified continuous signed-log
    % see Measurement Science and Technology (Webber, 2012)
    C = -7; % controls smallest order of magnitude near zero
    out = sign(in).*(log10(1+abs(in)/(10^C)));
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
