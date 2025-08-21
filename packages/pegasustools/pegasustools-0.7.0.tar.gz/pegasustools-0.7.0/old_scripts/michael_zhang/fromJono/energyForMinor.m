function energyforMinor

% Split energy as a function of time into polarizations

b3 = 0;
b0625 = 0;
b1 = 1;

kprho=1; %normalize kp to rho
normplot = 1;
dens = 0.1;
%int from rho^-1/rt(e) rho^-1*rt(e)
loadspec =0;
icwcut = 0;
plot_prlgrad = 0;
plot_gradient=0;
scale1heat = 0;
scale1protonheat = 0;
scaleratio1 = 0;
scaleratio1All = 0;
scaleratio1_0 = 0;
scale1inj = 0;

scale2heat = 0;
scale2protonheat = 0;
scaleratio2 = 0;
scaleratio2All = 0;
scaleratio2_0 = 0;
scale2inj = 0;
kppnorm = 2.0;%exp(1/2);%2;
kplnorm = 1.0* [1.0 1.0 1.0];%1.0 * [1.0 1.0 1.0];%0.7;%1.0;%0.7;
kplnorm2 = 1.0* [1.0 1.0 1.0 1.0 1.0 1.0 1.0];




p_id = 'minor_turb';
if b3
    name1 = 'half_tcorr_sim9';
    name2 = 'b_b3_sim1';
    sname = 'b3';
    comp1 = 'tigress';
    comp2 = 'tigress';
    rhoi = sqrt(0.3);

    nions1 = 2;
    mass = [1 16 4];
    charge = [1 5 2];
    %cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] };
    plotorder = [1 3 2];
    plotorder_trunc = [3 2];
    beta0_1 = 0.3;


    nions2 = 6;
    mass2 = [1 16 4 16 12 12 56];
    charge2 = [1 5 2 6 6 5 9];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder2 = [1 3 2 4 5 6];
    plotorder_trunc2 = [3 2 4 5 6 7];
    vol=6*48.1802^3;
    tauA = 6*48.1802;
    beta0_2 = 0.3;

    fname1 = ['../simulations/' name1 '/' p_id ]; % Folder with outputs']; % Folder with outputs
    fname2 = ['../simulations/' name2 '/' p_id ]; % Folder with outputs']; % Folder with outputs
end

if b0625
    name1 = 'hb_beta0625';
    name2 = 'b_b0625_sim1';
    sname = 'b0625';
    comp1 = 'tigressevan';
    comp2 = 'tigress';
    rhoi = sqrt(0.0625);

    nions1 = 6;
    mass = [1 16 4 16 12 12 24];
    charge = [1 5 2 6 6 5 9];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder = [1 3 2 4 5 6];
    plotorder_trunc = [3 2 4 5 6 7];
    vol=6*22.0^3;
    tauA = 6*22.0;
    beta0_1 = 0.0625;

    nions2 = 6;
    mass2 = [1 16 4 16 12 12 24];
    charge2 = [1 5 2 6 6 5 9];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder2 = [1 3 2 4 5 6];
    plotorder_trunc2 = [3 2 4 5 6 7];
    beta0_2 = 0.0625;

    fname1 = ['../../eyerger/' name1 '/output/' p_id ]; % Folder with outputs']; % Folder with outputs
    fname2 = ['../simulations/' name2 '/' p_id ]; % Folder with outputs']; % Folder with outputs
end


if b1
    name1 = 'i_b1_sim1';
    name2 = 'b_b0625_sim1';%'i_b1_sim1';
    sname = 'b1';
    comp1 = 'tigress';
    comp2 = 'tigress';
    rhoi = 1;

    nions1 = 7;
    mass = [1 16 4 16 12 12 24 1];
    charge = [1 5 2 6 6 5 9 1];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] [0.2940 0.1840 0.5560]};
    plotorder = [1 3 2 4 5 6 7];
    plotorder_trunc = [3 2 4 5 6 7 8];
    vol=6*87.96459^3;
    tauA = 6*87.96459;
    beta0_1 = 1.0;

    %nions2 = 7;
    %mass2 = [1 16 4 16 12 12 24 1];
    %charge2 = [1 5 2 6 6 5 9 1];
    %cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] [0.2940 0.1840 0.5560]};
    %plotorder2 = [1 3 2 4 5 6 7];
    %plotorder_trunc2 = [3 2 4 5 6 7 8];
    %beta0_2 = 1.0;

    nions2 = 6;
    mass2 = [1 16 4 16 12 12 24];
    charge2 = [1 5 2 6 6 5 9];
    %cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder2 = [1 3 2 4 5 6];
    plotorder_trunc2 = [3 2 4 5 6 7];
    beta0_2 = 0.0625;

    fname1 = ['../simulations/' name1 '/' p_id ]; % Folder with outputs']; % Folder with outputs
    fname2 = ['../simulations/' name2 '/' p_id ]; % Folder with outputs']; % Folder with outputs
end
qom = charge./mass;
qom2 = charge2./mass2;

addpath('~/matlab-libs/BrewerMap')
[~,~,~,~,outputfolder] = chooseComputerAndFiles(name1,comp1);
savebase = 'saved-analysis/';[outputfolder '/../../saved-analysis/'];
savefolder = [ savebase 'spectrum2D-' name1 '.mat'];
[~,~,~,~,outputfolder] = chooseComputerAndFiles(name2,comp2);
savebase = 'saved-analysis/';[outputfolder '/../../saved-analysis/'];
savefolder2 = [ savebase 'spectrum2D-' name2 '.mat'];

hcuticw = 0.7;
hcutkaw = 0.3;
withhc = 1;
n2s = @(s) num2str(s);

%mass = [1 16 4]
%qom = [1 5/16 1/2];


if loadspec
St1 = load(savefolder,'St');
St2 = load(savefolder2,'St');

% [tS,ord]=  sort(St.t/tauA);
tS1 = St1.St.t/tauA;
tS2 = St2.St.t/tauA;

% St.Bcc1 = St.Bcc1(:,:,ord);St.Bcc2 = St.Bcc2(:,:,ord);St.Bcc3 = St.Bcc3(:,:,ord);
% St.Ecc1 = St.Ecc1(:,:,ord);St.Ecc2 = St.Ecc2(:,:,ord);St.Ecc3 = St.Ecc3(:,:,ord);
% St.h1 = St.h1(:,:,ord);

hel1 = -St1.St.h1./(St1.St.Bcc1 + St1.St.Bcc2 + St1.St.Bcc3).*sqrt(St1.St.kp.^2 + (St1.St.kl.').^2);
hc1 = St1.St.ch1e./sqrt(St1.St.Bcc1 + St1.St.Bcc2 + St1.St.Bcc3)./sqrt(St1.St.Ecc1 + St1.St.Ecc2 + St1.St.Ecc3); 
hel2 = -St2.St.h1./(St2.St.Bcc1 + St2.St.Bcc2 + St2.St.Bcc3).*sqrt(St2.St.kp.^2 + (St2.St.kl.').^2);
hc2 = St2.St.ch1e./sqrt(St2.St.Bcc1 + St2.St.Bcc2 + St2.St.Bcc3)./sqrt(St2.St.Ecc1 + St2.St.Ecc2 + St2.St.Ecc3); 
if withhc
    hel1 = hel1.*sign(hc1);
    hel2 = hel2.*sign(hc2);
end



hmid1 = hel1<=hcutkaw & hel1>=-hcuticw;
hpos1 = hel1>hcutkaw ;
hneg1 = hel1<-hcuticw;

hmid2 = hel2<=hcutkaw & hel2>=-hcuticw;
hpos2 = hel2>hcutkaw ;
hneg2 = hel2<-hcuticw;

s2 = @(f) squeeze(sum(sum(f,2),1));
EBmid = s2(hmid1.*(St1.St.Bcc2 + St1.St.Bcc3)/2.*St1.St.nnorm);
EBpos = s2(hpos1.*(St1.St.Bcc2 + St1.St.Bcc3)/2.*St1.St.nnorm);
EBneg = s2(hneg1.*(St1.St.Bcc2 + St1.St.Bcc3)/2.*St1.St.nnorm);
EBlmid = s2(hmid1.*(St1.St.Bcc1)/2.*St1.St.nnorm);
EBlpos = s2(hpos1.*(St1.St.Bcc1)/2.*St1.St.nnorm);
EBlneg = s2(hneg1.*(St1.St.Bcc1)/2.*St1.St.nnorm);
EEmid = s2(hmid1.*(St1.St.Ecc2 + St1.St.Ecc3)/2.*St1.St.nnorm);
EEpos = s2(hpos1.*(St1.St.Ecc2 + St1.St.Ecc3)/2.*St1.St.nnorm);
EEneg = s2(hneg1.*(St1.St.Ecc2 + St1.St.Ecc3)/2.*St1.St.nnorm);
EElmid = s2(hmid1.*(St1.St.Ecc1)/2.*St1.St.nnorm);
EElpos = s2(hpos1.*(St1.St.Ecc1)/2.*St1.St.nnorm);
EElneg = s2(hneg1.*(St1.St.Ecc1)/2.*St1.St.nnorm);

%clear St hmid  hpos hneg hel hc
clear hmid1 hpos1 hel1 hc1 hmid2 hpos2 hel2 hc2
% save(['saved-analysis/ICenergy-' n2s(hcut) '-' n2s(withhc) '-' name '.mat'])
% else 
%     load(['saved-analysis/ICenergy-' n2s(hcut) '-' n2s(withhc) '-' name '.mat'])
% end

if kprho
    St1.St.kp = St1.St.kp .* rhoi
    St2.St.kp = St2.St.kp .* rhoi
end
end %end loadspec




% Plots variables from hst file 
fulldata = importdata([ fname1 '.hst']);

try
    names = strsplit(fulldata.textdata{2},'  ');
    names = names(1:end-1);
    dat = fulldata.data;
catch
    dat = fulldata;
end

t1 = dat(:,1);
if b3
    is1 = restart_overlaps2(t1);
elseif b0625
    is1 = restart_overlaps4(t1);
end
if b1
    is1 = restart_overlaps3(t1);
end
ion_start = 38;

n2s = @(s) num2str(s);


dt1 = dat(:,2);
dthst1 = diff(t1);dthst1 = [ dthst1(1); dthst1];

t_hst1 = t1;
%t_hst = dat(:,1)
%is = restart_overlaps2(t_hst);
dt1 = dat(:,2);
%dthst = diff(t_hst);dthst = [ dthst(1);dthst ];

t_hst1=t_hst1(is1)/tauA;
%sp = species;


va = 1;

uprp1 = {};
uprl1 = {};
urms1 = {};
cross_hel1 = {};
zp21 = {};
zm21 = {};
imbal1 = {};
vthpp1 = {};
vthpl1 = {};
beta1 = {};
betap1 = {};
vthtot1 = {};
qp1 = {};
ql1 = {};
tp1 = {};
tl1 = {};

uprp1{1} = sqrt(2*(dat(is1,8) + dat(is1,9)));
uprl1{1} = sqrt(2*dat(is1,7));
urms1{1} = sqrt(2*sum(dat(is1,7:9),2));
bbprp1 = sqrt(2*(dat(is1,11) + dat(is1,12)));
dbprl1 = sqrt(2*dat(is1,10));
cross_hel1{1} = sum(dat(is1,16:18),2); %*96^2*560*100;
zp21{1} = 0.5*(sum(dat(is1,7:9),2) + sum(dat(is1,10:12),2) + cross_hel1{1});
zm21{1} = 0.5*(sum(dat(is1,7:9),2) + sum(dat(is1,10:12),2) - cross_hel1{1});
imbal1{1} = (zp21{1} - zm21{1})./(zp21{1} + zm21{1});
vthpp1{1} = sqrt(dat(is1,28))/sqrt(2);
vthpl1{1} = sqrt(dat(is1,27));
vthtot1{1} = sqrt(dat(is1,28)+dat(is1,27));
beta1{1} = 2/3*(2*vthpp1{1}.^2 + vthpl1{1}.^2)./(1+bbprp1.^2+dbprl1.^2);
betap1{1} = 2*vthpp1{1}.^2./(1+bbprp1.^2+dbprl1.^2);
qp1{1} = 0.5* diff(dat(is1,28)); qp1{1} = [qp1{1}(1); qp1{1}]./dthst1(is1)*vol;
ql1{1} = 0.5* diff(dat(is1,27)); ql1{1} = [ql1{1}(1); ql1{1}]./dthst1(is1)*vol;
tp1{1} = 0.5* dat(is1,28)/6;
tl1{1} = 0.5* dat(is1,27)/3;
%tp defined as 1/2 m<v_perp^2>/2 /3
%tl defined as 1/2 m<v_par^2>  /3
%s.t. 2tp+tl = t = thermal_energy/3 / k_b = 1/2 m v_th^2?? Jono2022 vs.
%what he plots for qp and ql in plot_hst_inject which should be correct,
%since K.E = 1/2 mv^2
for i = 1:length(mass)-1
    ion_ind = ion_start+24*(i-1);
    uprp1{i+1} = sqrt(2*(dat(is1,ion_ind+5) + dat(is1,ion_ind+6)));
    uprl1{i+1} = sqrt(2*dat(is1,ion_ind+4));
    urms1{i+1} = sqrt(2*sum(dat(is1,ion_ind+4:ion_ind+6),2));
    cross_hel1{i+1} = sum(dat(is1,ion_ind+7:ion_ind+9),2); %*96^2*560*100;
    zp21{i+1} = 0.5*(sum(dat(is1,ion_ind+4:ion_ind+6),2) + sum(dat(is1,10:12),2) + cross_hel1{i+1});
    zm21{i+1} = 0.5*(sum(dat(is1,ion_ind+4:ion_ind+6),2) + sum(dat(is1,10:12),2) - cross_hel1{i+1});
    imbal1{i+1} = (zp21{i+1} - zm21{i+1})./(zp21{i+1} + zm21{i+1});
    vthpp1{i+1} = sqrt(dat(is1,ion_ind+19))/sqrt(2);
    vthpl1{i+1} = sqrt(dat(is1,ion_ind+18));
    vthtot1{i+1} = sqrt( dat(is1,ion_ind+19) + dat(is1,ion_ind+18));
    beta1{i+1} = 2/3*mass(i+1)*dens*(2*vthpp1{i+1}.^2 + vthpl1{i+1}.^2)./(1+bbprp1.^2+dbprl1.^2);
    betap1{i+1} = 2*mass(i+1)*dens*vthpp1{i+1}.^2./(1+bbprp1.^2+dbprl1.^2);
    qp1{i+1} = 0.5* mass(i+1)*diff(dat(is1,ion_ind+19)); qp1{i+1} = [qp1{i+1}(1); qp1{i+1}]./dthst1(is1)*vol;
    ql1{i+1} = 0.5* mass(i+1)*diff(dat(is1,ion_ind+18)); ql1{i+1} = [ql1{i+1}(1); ql1{i+1}]./dthst1(is1)*vol;
    tp1{i+1} = 0.5* mass(i+1)*dat(is1,ion_ind+19)/6;
    tl1{i+1} = 0.5* mass(i+1)*dat(is1,ion_ind+18)/3;
end



for i = 1:length(mass)
    vthpp1{i} = vthpp1{i}/vthpp1{i}(1);
    vthpl1{i} = vthpl1{i}/vthpl1{i}(1);
    vthtot1{i} = vthtot1{i}/vthtot1{i}(1);
end

if loadspec
    nbfinds1 = [];
    for i = 1:length(St1.St.t)
      %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
      nbfinds1 = [nbfinds1 find(t_hst1-tS1(i)>0.5/tauA,1)];
    end
end

epsind = 34;
diss_hypr1 = dat(is1,epsind-1)./dthst1(is1)*vol;
dedt1 = (dat(is1,epsind)+dat(is1,epsind+1))./dthst1(is1)*vol;
dehdt1 = (dat(is1,epsind+2)+dat(is1,epsind+3))./dthst1(is1)*vol;
deudt1 = (dat(is1,epsind))./dthst1(is1)*vol; debdt1 = (dat(is1,epsind+1))./dthst1(is1)*vol;
epsp1 = 0.5*(dat(is1,epsind)+dat(is1,epsind+1)+dat(is1,epsind+2)+dat(is1,epsind+3))./dthst1(is1)*vol;
%epsm = (dat(:,epsind)+dat(:,epsind+1)-dat(:,epsind+2)-dat(:,epsind+3))./dthst*vol;
epsm1 = 0.5*(dedt1-dehdt1);
dtKE1 = diff(sum(dat(is1,7:9),2)); dtKE1 = [dtKE1(1); dtKE1]./dthst1(is1)*vol;
dtME1 = diff(sum(dat(is1,10:12),2)); dtME1 = [dtME1(1); dtME1]./dthst1(is1)*vol;

Euprp = dat(is1,8) + dat(is1,9);
Ebprp = dat(is1,11) + dat(is1,12);
Ebprl = dat(is1,10);
Eeprp = dat(is1,14) + dat(is1,15);
Eeprl = dat(is1,13);



% Plots variables from hst file 
fulldata = importdata([ fname2 '.hst']);

try
    names = strsplit(fulldata.textdata{2},'  ');
    names = names(1:end-1);
    dat = fulldata.data;
catch
    dat = fulldata;
end

t2 = dat(:,1);
is2 = restart_overlaps3(t2);
ion_start = 35;

dt2 = dat(:,2);
dthst2 = diff(t2);dthst2 = [ dthst2(1);dthst2 ];

t_hst2 = t2;
t_hst2 = t_hst2(is2)/tauA;

uprp2 = {};
uprl2 = {};
urms2 = {};
cross_hel2 = {};
zp22 = {};
zm22 = {};
imbal2 = {};
vthpp2 = {};
vthpl2 = {};
beta2 = {};
betap2 = {};
vthtot2 = {};
%dydxpp2 = {};
%dydxpl2 = {};
qp2 = {};
ql2 = {};
tp2 = {};
tl2 = {};

uprp2{1} = sqrt(2*(dat(is2,8) + dat(is2,9)));
uprl2{1} = sqrt(2*dat(is2,7));
urms2{1} = sqrt(2*sum(dat(is2,7:9),2));
bbprp2 = sqrt(2*(dat(is2,11) + dat(is2,12)));
dbprl2 = sqrt(2*dat(is2,10));
cross_hel2{1} = sum(dat(is2,16:18),2); %*96^2*560*100;
zp22{1} = 0.5*(sum(dat(is2,7:9),2) + sum(dat(is2,10:12),2) + cross_hel2{1});
zm22{1} = 0.5*(sum(dat(is2,7:9),2) + sum(dat(is2,10:12),2) - cross_hel2{1});
imbal2{1} = (zp22{1} - zm22{1})./(zp22{1} + zm22{1});
vthpp2{1} = sqrt(dat(is2,28))/sqrt(2);
vthpl2{1} = sqrt(dat(is2,27));
vthtot2{1} = sqrt(dat(is2,28)+dat(is2,27));
beta2{1} = 2/3*(2*vthpp2{1}.^2 + vthpl2{1}.^2)./(1+bbprp2.^2+dbprl2.^2);
betap2{1} = 2*vthpp2{1}.^2./(1+bbprp2.^2+dbprl2.^2);
%dydxpp2{1} = (gradient(dat(:,28)./dat(1,28))./gradient(t2/tauA));
%dydxpl2{1} = gradient(dat(:,27)./dat(1,27))./gradient(t2/tauA);
%dydxpp2{1} = dydxpp2{1}(is2);
%dydxpl2{1} = dydxpl2{1}(is2);
qp2{1} = 0.5* diff(dat(is2,28)); qp2{1} = [qp2{1}(1); qp2{1}]./dthst2(is2)*vol;
ql2{1} = 0.5* diff(dat(is2,27)); ql2{1} = [ql2{1}(1); ql2{1}]./dthst2(is2)*vol;
tp2{1} = 0.5* dat(is2,28)/6;
tl2{1} = 0.5* dat(is2,27)/3;
for i = 1:length(mass2)-1
    ion_ind = ion_start+24*(i-1);
    uprp2{i+1} = sqrt(2*(dat(is2,ion_ind+5) + dat(is2,ion_ind+6)));
    uprl2{i+1} = sqrt(2*dat(is2,ion_ind+4));
    urms2{i+1} = sqrt(2*sum(dat(is2,ion_ind+4:ion_ind+6),2));
    cross_hel2{i+1} = sum(dat(is2,ion_ind+7:ion_ind+9),2); %*96^2*560*100;
    zp22{i+1} = 0.5*(sum(dat(is2,ion_ind+4:ion_ind+6),2) + sum(dat(is2,10:12),2) + cross_hel2{i+1});
    zm22{i+1} = 0.5*(sum(dat(is2,ion_ind+4:ion_ind+6),2) + sum(dat(is2,10:12),2) - cross_hel2{i+1});
    imbal2{i+1} = (zp22{i+1} - zm22{i+1})./(zp22{i+1} + zm22{i+1});
    vthpp2{i+1} = sqrt(dat(is2,ion_ind+19))/sqrt(2);
    vthpl2{i+1} = sqrt(dat(is2,ion_ind+18));
    vthtot2{i+1} = sqrt( dat(is2,ion_ind+19) + dat(is2,ion_ind+18));
    beta2{i+1} = 2/3*mass2(i+1)*dens*(2*vthpp2{i+1}.^2 + vthpl2{i+1}.^2)./(1+bbprp2.^2+dbprl2.^2);
    betap2{i+1} = 2*mass2(i+1)*dens*vthpp2{i+1}.^2./(1+bbprp2.^2+dbprl2.^2);
    %dydxpp2{i+1} = (gradient(dat(:,ion_ind+19)./dat(1,ion_ind+19))./gradient(t2/tauA));
    %dydxpl2{i+1} = gradient(dat(:,ion_ind+18)./dat(1,ion_ind+18))./gradient(t2/tauA);
    %dydxpp2{i+1} = dydxpp2{i+1}(is2);
    %dydxpl2{i+1} = dydxpl2{i+1}(is2);
    qp2{i+1} = 0.5* mass2(i+1)*diff(dat(is2,ion_ind+19)); qp2{i+1} = [qp2{i+1}(1); qp2{i+1}]./dthst2(is2)*vol;
    ql2{i+1} = 0.5* mass2(i+1)*diff(dat(is2,ion_ind+18)); ql2{i+1} = [ql2{i+1}(1); ql2{i+1}]./dthst2(is2)*vol;
    tp2{i+1} = 0.5* mass2(i+1)*dat(is2,ion_ind+19)/6;
    tl2{i+1} = 0.5* mass2(i+1)*dat(is2,ion_ind+18)/3;
end

for i = 1:length(mass2)
    vthpp2{i} = vthpp2{i}/vthpp2{i}(1);
    vthpl2{i} = vthpl2{i}/vthpl2{i}(1);
    vthtot2{i} = vthtot2{i}/vthtot2{i}(1);
end


if loadspec
    nbfinds2 = [];
    for i = 1:length(St2.St.t)
      %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
      nbfinds2 = [nbfinds2 find(t_hst2-tS2(i)>0.5/tauA,1)];
    end
end

epsind = 34;
diss_hypr2 = dat(is2,epsind-1)./dthst2(is2)*vol;
dedt2 = (dat(is2,epsind))./dthst2(is2)*vol;
deudt2 = (dat(is2,epsind))./dthst2(is2)*vol;
dtKE2 = diff(sum(dat(is2,7:9),2)); dtKE2 = [dtKE2(1); dtKE2]./dthst2(is2)*vol;
dtME2 = diff(sum(dat(is2,10:12),2)); dtME2 = [dtME2(1); dtME2]./dthst2(is2)*vol;



t1=t1(is1)/tauA;
t2=t2(is2)/tauA;

if loadspec
%make time dependent kpprange and kplrange c.f. distfuncav
kpprange1 = {};
kprlrange1 = {};
kpprange1_0 = {};
kpprange2 = {};
kprlrange2 = {};
kpprange2_0 = {};
for i = 1:length(mass)
   kpprange1{i} = [];
   kplrange1{i} = St1.St.kl >= kplnorm(i) * qom(i);
end
for i = 1:length(mass2)
   kpprange2{i} = [];
   kplrange2{i} = St2.St.kl >= kplnorm2(i) * qom2(i);
end
aboveBarrier1 = St1.St.kp <= 1;
aboveBarrier2 = St2.St.kp <= 1;
for ti = nbfinds1
    for i = 1:length(mass)
      kpprange1{i} = cat(3,kpprange1{i},St1.St.kp <= kppnorm ./ (vthpp1{i}(ti) * sqrt(1./mass(i))./qom(i)));
    end
end
for ti = nbfinds2
    for i = 1:length(mass2)
      kpprange2{i} = cat(3,kpprange2{i},St2.St.kp <= kppnorm ./ (vthpp2{i}(ti) * sqrt(1./mass2(i))./qom2(i)));
    end
end


for i = 1:length(mass)
    kpprange1_0{i} = St1.St.kp <= 1 ./ (vthpp1{i}(1) * sqrt(1./mass(i))./qom(i));
end
for i = 1:length(mass2)
    kpprange2_0{i} = St2.St.kp <= 1 ./ (vthpp2{i}(1) * sqrt(1./mass2(i))./qom2(i));
end

Bprp1 = {};
BprpAllkp1 = {};
Bprp1_0 = {};
Bprp2 = {};
BprpAllkp12= {};
Bprp2_0 = {};
for i = 1:length(mass)
  Bprp1{i} = (St1.St.Bcc2 + St1.St.Bcc3).*kpprange1{i}.*kplrange1{i}.'./normplot;
  BprpAllkp1{i} = (St1.St.Bcc2 + St1.St.Bcc3).*aboveBarrier1.*kplrange1{i}.'./normplot;
  Bprp1_0{i} = (St1.St.Bcc2 + St1.St.Bcc3).*kpprange1_0{i}.*kplrange1{i}.'./normplot;
    if icwcut
      Bprp1{i} = Bprp1{i}.*hneg1;
      BprpAllkp1{i} = BprpAllkp1{i}.*hneg1;
      Bprp1_0{i} = Bprp1_0{i}.*hneg1;
    end
end
for i = 1:length(mass2)
  Bprp2{i} = (St2.St.Bcc2 + St2.St.Bcc3).*kpprange2{i}.*kplrange2{i}.'./normplot;
  BprpAllkp2{i} = (St2.St.Bcc2 + St2.St.Bcc3).*aboveBarrier2.*kplrange2{i}.'./normplot;
  Bprp2_0{i} = (St2.St.Bcc2 + St2.St.Bcc3).*kpprange2_0{i}.*kplrange2{i}.'./normplot;
  if icwcut
      Bprp2{i} = Bprp2{i}.*hneg2;
      BprpAllkp2{i} = BprpAllkp2{i}.*hneg2;
      Bprp2_0{i} = Bprp2_0{i}.*hneg2;
  end
end


% \delta B_icw / \delta B
dBprpICWfrac1 = s2((St1.St.Bcc2 + St1.St.Bcc3).*hneg1)./ s2((St1.St.Bcc2 + St1.St.Bcc3))
dBtotICWfrac1 = s2((St1.St.Bcc1 + St1.St.Bcc2 + St1.St.Bcc3).*hneg1)./ s2((St1.St.Bcc1 + St1.St.Bcc2 + St1.St.Bcc3))
% \delta B / B_0=1
%bbprp1 = sqrt(2*(dat(is1,11) + dat(is1,12)));
%dbprl1 = sqrt(2*dat(is1,10));

% \delta B_icw  / B_0
dBprpICW1 = dBprpICWfrac1.*bbprp1(nbfinds1).*bbprp1(nbfinds1);
dBtotICW1 = dBprpICWfrac1.*(bbprp1(nbfinds1)+dbprl1(nbfinds1)).^2;





intBprp1 = {};
intBprpAllkp1 = {};
intBprp1_0 = {};
intBprp2 = {};
intBprpAllkp2 = {};
intBprp2_0 = {};
for i = 1:length(mass)
  intBprp1{i} = s2(Bprp1{i});
  intBprpAllkp1{i} = s2(BprpAllkp1{i});
  intBprp1_0{i} = s2(Bprp1_0{i});
end
for i = 1:length(mass2)
  intBprp2{i} = s2(Bprp2{i});
  intBprpAllkp2{i} = s2(BprpAllkp2{i});
  intBprp2_0{i} = s2(Bprp2_0{i});
end

ratioAvail1 = {};
ratioAvailAllkp1 = {};
ratioAvail1_0 = {};
ratioAvail2 = {};
ratioAvailAllkp2 = {};
ratioAvail2_0 = {};

for i = 1:length(mass)
  ratioAvail1{i} = intBprp1{i}./(intBprp1{1}+intBprp1{2}+intBprp1{3});
  ratioAvailAllkp1{i} = intBprpAllkp1{i}./(intBprpAllkp1{1}+intBprpAllkp1{2}+intBprpAllkp1{3});
  ratioAvail1_0{i} = intBprp1_0{i}./(intBprp1_0{1}+intBprp1_0{2}+intBprp1_0{3});
end
for i = 1:length(mass2)
  ratioAvail2{i} = intBprp2{i}./(intBprp2{1}+intBprp2{2}+intBprp2{3});
  ratioAvailAllkp2{i} = intBprpAllkp2{i}./(intBprpAllkp2{1}+intBprpAllkp2{2}+intBprpAllkp2{3});
  ratioAvail2_0{i} = intBprp2_0{i}./(intBprp2_0{1}+intBprp2_0{2}+intBprp2_0{3});
end


figure('Color',[1 1 1]);
nplt = [142];
s = {};
dn = 10;
lims = [-10,0];
for n=nplt;%dn:dn+1:St.n-dn;
    m = @(d) mean(d(:,:,n-dn+1:n+dn),3);St1.St.t(n+1)
    m2 = @(d) mean(d(n-dn+1:n+dn),1);
    %s{1}=pcolor(log10(St.kp),log10(St.kl),log10(m(St.Bcc2 + St.Bcc3)./normplot).');
    s{1}=pcolor(log10(St1.St.kp),log10(St1.St.kl),log10(m((St1.St.Bcc2 + St1.St.Bcc3).*hneg1)./normplot).');
    %s{1}=pcolor(log10(St.kp),log10(St.kl),log10(m(Bprp{1})).');
    s{1}.EdgeColor='none';s{1}.FaceColor='interp';
    colorbar; colormap(brewermap([],'YlGnBu'))%colormap jet;
    caxis(lims)
    xlabel('$\log_{10} (k_\perp \rho_{p})$','interpreter','latex')
    ylabel('$\log_{10} (k_\| d_{p})$','interpreter','latex')
end


figure('Color',[1 1 1]);
plot(t1,vthpp1{1}.^2,'-','Color',cols{1},'Linewidth',3) 
hold on
plot(t1,vthpl1{1}.^2,'--','Color',cols{1},'Linewidth',3) 
for i = 1:nions1
    plot(t1,vthpp1{i+1}.^2,'-','Color',cols{i+1},'Linewidth',3) 
    plot(t1,vthpl1{i+1}.^2,'--','Color',cols{i+1},'Linewidth',3) 
end
hold off
%legend({'$T_{\perp,p}$','$T_{\|,p}$','$T_{\perp,He^{++}}$','$T_{\|,He^{++}}$','$T_{\perp,O^{5+}}$','$T_{\|,O^{5+}}$'},'interpreter','latex','Location','northwest')
legend({'$T_{\perp,p}$','$T_{\|,p}$','$T_{\perp,O^{5+}}$','$T_{\|,O^{5+}}$','$T_{\perp,He^{++}}$','$T_{\|,He^{++}}$','$T_{\perp,O^{6+}}$','$T_{\|,O^{6+}}$','$T_{\perp,C^{6+}}$','$T_{\|,C^{6+}}$','$T_{\perp,C^{5+}}$','$T_{\|,C^{5+}}$','$T_{\perp,Fe^{9+}}$','$T_{\|,Fe^{9+}}$'},'interpreter','latex','Location','northwest')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$T_s/T_{s0}$','interpreter','latex')
set(gca,'fontsize', 16);

figure('Color',[1 1 1]);
plot(t2,vthpp2{1}.^2,'-','Color',cols{1},'Linewidth',3) 
hold on
plot(t2,vthpl2{1}.^2,'--','Color',cols{1},'Linewidth',3) 
for i = 1:nions2
    plot(t2,vthpp2{i+1}.^2,'-','Color',cols{i+1},'Linewidth',3) 
    plot(t2,vthpl2{i+1}.^2,'--','Color',cols{i+1},'Linewidth',3) 
end
hold off
%legend({'$T_{\perp,p}$','$T_{\|,p}$','$T_{\perp,He^{++}}$','$T_{\|,He^{++}}$','$T_{\perp,O^{5+}}$','$T_{\|,O^{5+}}$'},'interpreter','latex','Location','northwest')
legend({'$T_{\perp,p}$','$T_{\|,p}$','$T_{\perp,O^{5+}}$','$T_{\|,O^{5+}}$','$T_{\perp,He^{++}}$','$T_{\|,He^{++}}$','$T_{\perp,O^{6+}}$','$T_{\|,O^{6+}}$','$T_{\perp,C^{6+}}$','$T_{\|,C^{6+}}$','$T_{\perp,C^{5+}}$','$T_{\|,C^{5+}}$','$T_{\perp,Fe^{9+}}$','$T_{\|,Fe^{9+}}$'},'interpreter','latex','Location','northwest')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$T_s/T_{s0}$','interpreter','latex')
set(gca,'fontsize', 16);


figure('Color',[1 1 1]);
%semilogy(tS,intBprp{1},tS,intBprp{2},tS,intBprp{3})
%semilogy(tS,intBprpAllkp{1},tS,intBprpAllkp{2},tS,intBprpAllkp{3})
if scaleratio1
    semilogy(tS1,ratioAvail1{1},'Color',cols{1},'Linewidth',3)
    hold on
    semilogy(tS1,ratioAvail1{3},'Color',cols{3},'Linewidth',3)
    semilogy(tS1,ratioAvail1{2},'Color',cols{2},'Linewidth',3)
    hold off
end
if scaleratio1_0
    semilogy(tS1,ratioAvail1_0{1},'Color',cols{1},'Linewidth',3)
    hold on
    semilogy(tS1,ratioAvail1_0{3},'Color',cols{3},'Linewidth',3)
    semilogy(tS1,ratioAvail1_0{2},'Color',cols{2},'Linewidth',3)
    hold off
end
if scaleratio1All
    %semilogy(tS,ratioAvailAllkp{1},tS,ratioAvailAllkp{2},tS,ratioAvailAllkp{3})
    semilogy(tS1,ratioAvailAllkp1{1},'Color',cols{1},'Linewidth',3)
    hold on
    semilogy(tS1,ratioAvailAllkp1{3},'Color',cols{3},'Linewidth',3)
    semilogy(tS1,ratioAvailAllkp1{2},'Color',cols{2},'Linewidth',3)
    hold off
end
legend({'$p$','$He^{++}$','$O^{5+}$'},'interpreter','latex','Location','northwest')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('Ratio of B_perp energy available','interpreter','latex')
set(gca,'fontsize', 16);
end % if loadspec

windowSize = ceil(tauA);
filt = @(f) filter((1/windowSize)*ones(1,windowSize),1,f);


figure('Color',[1 1 1]);
plot(t1,filt(dedt1),'-','Linewidth',3) 
hold on
plot(t2,filt(dedt2),'--','Linewidth',3)
hold off
legend({'$\epsilon_{imbalanced}$','$\epsilon_{balanced}$'},'interpreter','latex','Location','northwest')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);

    
dydxpp1 = {};
dydxpl1 = {};
dydxpp2 = {};
dydxpl2 = {};

% unscaled? but we care about mv^2 = T, and initial Ts are the same so
% shouldn't matter for Q
for i = 1:length(mass)
    dydxpp1{i} = gradient(vthpp1{i}.^2)./gradient(t1);
    dydxpl1{i} = gradient(vthpl1{i}.^2)./gradient(t1);
end
for i = 1:length(mass2)
    dydxpp2{i} = gradient(vthpp2{i}.^2)./gradient(t2);
    dydxpl2{i} = gradient(vthpl2{i}.^2)./gradient(t2);
end



for i = 0:nions1
    dydxpp1{i+1} = filt(dydxpp1{i+1});
    dydxpl1{i+1} = filt(dydxpl1{i+1});
end

for i = 0:nions2
    dydxpp2{i+1} = filt(dydxpp2{i+1});
    dydxpl2{i+1} = filt(dydxpl2{i+1});
end

if scaleratio1
    for i = 0:nions1
        dydxpp1{i+1} = dydxpp1{i+1}(nbfinds1)./ratioAvail1{i+1};
    end
    t1=t1(nbfinds1);
end
if scaleratio1All
    for i = 0:nions1
        dydxpp1{i+1} = dydxpp1{i+1}(nbfinds1)./ratioAvailAllkp1{i+1};
    end
    t1=t1(nbfinds1);
end
if scaleratio1_0
    for i = 0:nions1
        dydxpp1{i+1} = dydxpp1{i+1}(nbfinds1)./ratioAvail1_0{i+1};
    end
    t1=t1(nbfinds1);
end

if scale1heat
    for i = 1:nions1
        dydxpp1{i+1} = dydxpp1{i+1}./(1.35*mass(i+1));
        dydxpl1{i+1} = dydxpl1{i+1}./(1.35*mass(i+1));
    end
end
if scale1protonheat
    for i = 1:nions1
        dydxpp1{i+1} = dydxpp1{i+1}./dydxpp1{1};
        dydxpl1{i+1} = dydxpl1{i+1}./dydxpl1{1};
    end
    dydxpp1{1} = dydxpp1{1}./dydxpp1{1};
    dydxpl1{1} = dydxpl1{1}./dydxpl1{1};
end
if scale1inj
    for i = 0:nions1
        dydxpp1{i+1} = dydxpp1{i+1}./filt(dedt1);
        dydxpl1{i+1} = dydxpl1{i+1}./filt(dedt1);
    end
end


if scaleratio2
    for i = 0:nions2
        dydxpp2{i+1} = dydxpp2{i+1}(nbfinds2)./ratioAvail2{i+1};
    end
    t2=t2(nbfinds2);
end
if scaleratio2All
    for i = 0:nions2
        dydxpp2{i+1} = dydxpp2{i+1}(nbfinds2)./ratioAvailAllkp2{i+1};
    end
    t2=t2(nbfinds2);
end
if scaleratio2_0
    for i = 0:nions2
        dydxpp2{i+1} = dydxpp2{i+1}(nbfinds2)./ratioAvail2_0{i+1};
    end
    t2=t2(nbfinds2);
end

if scale2heat
    for i = 1:nions2
        dydxpp2{i+1} = dydxpp2{i+1}./(1.35*mass2(i+1));
        dydxpl2{i+1} = dydxpl2{i+1}./(1.35*mass2(i+1));
    end
end
if scale2protonheat
    for i = 1:nions2
        dydxpp2{i+1} = dydxpp2{i+1}./dydxpp2{1};
        dydxpl2{i+1} = dydxpl2{i+1}./dydxpl2{1};
    end
    dydxpp2{1} = dydxpp2{1}./dydxpp2{1};
    dydxpl2{1} = dydxpl2{1}./dydxpl2{1};
end
if scale2inj
    for i = 0:nions2
        dydxpp2{i+1} = dydxpp2{i+1}./filt(dedt2);
        dydxpl2{i+1} = dydxpl2{i+1}./filt(dedt2);
    end
end




figure('Color',[1 1 1]);
plot(t1,dydxpp1{1},'-','Color',cols{1},'Linewidth',3) 
hold on
if plot_prlgrad
    plot(t1,dydxpl1{1},'--','Color',cols{1},'Linewidth',3)
end
    for i = plotorder_trunc
        plot(t1,dydxpp1{i},'-','Color',cols{i},'Linewidth',3)
        if plot_prlgrad
            plot(t1,dydxpl1{i},'--','Color',cols{i},'Linewidth',3)
        end
    end
if scale1protonheat
    %ylim([-50 600])
    ylim([0 100])
    xlim([0.1 8])
    %ylim([0 250])
    %xlim([2.5 15.3])
    %ylim([0 10])
end
hold off
if plot_prlgrad
        %legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{6+}}$','$Q_{\|,O^{6+}}$','$Q_{\perp,C^{6+}}$','$Q_{\|,C^{6+}}$','$Q_{\perp,C^{5+}}$','$Q_{\|,C^{5+}}$','$Q_{\perp,Fe^{9+}}$','$Q_{\|,Fe^{9+}}$'},'interpreter','latex','Location','northeast')
        legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$'},'interpreter','latex','Location','northeast')
else
    legend({'$Q_{\perp,p}$','$Q_{\perp,He^{++}}$','$Q_{\perp,O^{5+}}$'},'interpreter','latex','Location','northeast')
end
xlabel('$t/\tau_A$','interpreter','latex')
if scale1heat || scale1protonheat
    ylabel('$\tilde{Q}$','interpreter','latex')
else
    ylabel('$Q$','interpreter','latex')
end
set(gca,'fontsize', 16);

figure('Color',[1 1 1]);
plot(t2,dydxpp2{1},'-','Color',cols{1},'Linewidth',3) 
hold on
if plot_prlgrad
    plot(t2,dydxpl2{1},'--','Color',cols{1},'Linewidth',3)
end
for i = plotorder_trunc2
    plot(t2,dydxpp2{i},'-','Color',cols{i},'Linewidth',3)
    if plot_prlgrad
        plot(t2,dydxpl2{i},'--','Color',cols{i},'Linewidth',3)
    end
end
hold off
if plot_prlgrad
        %legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{6+}}$','$Q_{\|,O^{6+}}$','$Q_{\perp,C^{6+}}$','$Q_{\|,C^{6+}}$','$Q_{\perp,C^{5+}}$','$Q_{\|,C^{5+}}$','$Q_{\perp,Fe^{9+}}$','$Q_{\|,Fe^{9+}}$'},'interpreter','latex','Location','northeast')
        legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$'},'interpreter','latex','Location','northeast')
else
    legend({'$Q_{\perp,p}$','$Q_{\perp,He^{++}}$','$Q_{\perp,O^{5+}}$'},'interpreter','latex','Location','northeast')
end
xlabel('$t/\tau_A$','interpreter','latex')
if scale2heat || scale2protonheat
    ylabel('$\tilde{Q}$','interpreter','latex')
else
    ylabel('$Q$','interpreter','latex')
end
set(gca,'fontsize', 16);


%close all
etot1 = dedt1-dtKE1-dtME1-diss_hypr1-qp1{1}-ql1{1};
% t(is),filt(etot),'k-',t(is),0*t(is),':k')
figure('Color',[1 1 1]);
plot(t1,filt(dedt1),'-','Linewidth',3) 
hold on
plot(t1,filt(dtKE1+dtME1),'--','Linewidth',3)
plot(t1,filt(diss_hypr1),'--','Linewidth',3)
plot(t1,filt(qp1{1}),'--','Linewidth',3)
plot(t1,filt(ql1{1}),'--','Linewidth',3)
plot(t1,filt(etot1),'k-','Linewidth',3)
plot(t1,0*t1,':k','Linewidth',3)
hold off
legend({'$\varepsilon$','$\partial_t(E_K+E_B)$','$\varepsilon_\eta$','$\partial_t E_{th,\perp}$','$\partial_t E_{th,\|}$',...
    'Sum of all terms $-\varepsilon$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);

etot2 = dedt2-dtKE2-dtME2-diss_hypr2-qp2{1}-ql2{1};
% t(is),filt(etot),'k-',t(is),0*t(is),':k')
figure('Color',[1 1 1]);
plot(t2,filt(dedt2),'-','Linewidth',3) 
hold on
plot(t2,filt(dtKE2+dtME2),'--','Linewidth',3)
plot(t2,filt(diss_hypr2),'--','Linewidth',3)
plot(t2,filt(qp2{1}),'--','Linewidth',3)
plot(t2,filt(ql2{1}),'--','Linewidth',3)
plot(t2,filt(etot2),'k-','Linewidth',3)
plot(t2,0*t2,':k','Linewidth',3)
hold off
legend({'$\varepsilon$','$\partial_t(E_K)$','$\varepsilon_\eta$','$\partial_t E_{th,\perp}$','$\partial_t E_{th,\|}$',...
    'Sum of all terms $-\varepsilon$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);


figure('Color',[1 1 1]);
plot(t1,filt(diss_hypr1./dedt1),'-','Linewidth',3) 
hold on
plot(t1,filt((qp1{1}+ql1{1})./dedt1),'-','Linewidth',3)
plot(t1,filt((qp1{1}+ql1{1})./diss_hypr1),'-','Linewidth',3)
plot(t1,filt(diss_hypr1./(dedt1-dtKE1-dtME1)),'--','Linewidth',3) 
plot(t1,filt((qp1{1}+ql1{1})./(dedt1-dtKE1-dtME1)),'--','Linewidth',3) 
plot(t1,filt(dehdt1./dedt1),'--','Linewidth',3) 
hold off
legend({'$\varepsilon_\eta/\varepsilon$','$Q_{p}/\varepsilon$','$Q_{p}/\varepsilon_\eta$','$\varepsilon_\eta/(\varepsilon-\partial_t(E_K+E_B))$','$Q_{p}/(\varepsilon-\partial_t(E_K+E_B))$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);

figure('Color',[1 1 1]);
plot(t2,filt(diss_hypr2./dedt2),'-','Linewidth',3) 
hold on
plot(t2,filt((qp2{1}+ql2{1})./dedt2),'-','Linewidth',3)
plot(t2,filt((qp2{1}+ql2{1})./diss_hypr2),'-','Linewidth',3)
plot(t2,filt(diss_hypr2./(dedt2-dtKE2-dtME2)),'--','Linewidth',3) 
plot(t2,filt((qp2{1}+ql2{1})./(dedt2-dtKE2-dtME2)),'--','Linewidth',3) 
hold off
legend({'$\varepsilon_\eta/\varepsilon$','$Q_{p}/\varepsilon$','$Q_{p}/\varepsilon_\eta$','$\varepsilon_\eta/(\varepsilon-\partial_t(E_K+E_B))$','$Q_{p}/(\varepsilon-\partial_t(E_K+E_B))$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);


%tav1 = [14.2 15.5];
%tav1 = [12.5 16.0];
tav1 = [0.5 4.5];%[5.0 10.0];
%tav = [6.5 8.5];
tav2 = [5 8];
tav3 = [3 8];

m1 = @(d) mean(d(find(t1>=tav1(1) & t1<=tav1(2))));
m2 = @(d) mean(d(find(t2>=tav2(1) & t2<=tav2(2))));
m3 = @(d) mean(d(find(t2>=tav3(1) & t2<=tav3(2))));
n2s(find(t1>=tav1(1) & t1<=tav1(2)))
%disp(['Averaging nums ' n2s(find(t1>=tav1(1) & t1<=tav1(2)))])
%disp(['Averaging nums ' n2s(find(t2>=tav2(1) & t2<=tav2(2)))])

disp("q_p/eps_eta for imbalanced run (12.5-end)")
m1((qp1{1}+ql1{1})./diss_hypr1)
disp("q_p/eps_eta for balanced run (5-7.5)")
m2((qp2{1}+ql2{1})./diss_hypr2)
disp("eps_eta/(eps-KEME) for imbalanced run (12.5-end)")
m1(diss_hypr1./(dedt1-dtKE1-dtME1))
disp("eps_eta/(eps-KEME)  for balanced run (5-7.5)")
m2(diss_hypr2./(dedt2-dtKE2-dtME2))
disp("q_p/(eps-KEME) for imbalanced run (12.5-end)")
m1((qp1{1}+ql1{1})./(dedt1-dtKE1-dtME1))
disp("q_p/(eps-KEME)  for balanced run (5-7.5)")
m2((qp2{1}+ql2{1})./(dedt2-dtKE2-dtME2))
disp("eps_h/eps for imbalanced run (12.5-end)")
m1(dehdt1./dedt1)
disp("eps for imbalanced run (12.5-end)")
m1(dedt1)
disp("eps_h for imbalanced run (12.5-end)")
m1(dehdt1)
disp("eps_h/eps for imbalanced run")
mean(dehdt1(2:end)./dedt1(2:end))
disp("eps for imbalanced run")
mean(dedt1)
disp("eps_h for imbalanced run")
mean(dehdt1)
disp("eps for balanced run")
mean(dedt2)
disp("eps for balanced run 3-end")
m3(dedt2)
disp("eps for balanced run 5-end")
m2(dedt2)

qp1_eps = {};
ql1_eps = {};
qp1_eps_noE = {};
ql1_eps_noE = {};
for i = 0:nions1
    qp1_eps{i+1} = filt(qp1{i+1}./dedt1);
    ql1_eps{i+1} = filt(ql1{i+1}./dedt1);
    qp1_eps_noE{i+1} = filt(qp1{i+1}./(dedt1-dtKE1-dtME1));
    ql1_eps_noE{i+1} = filt(ql1{i+1}./(dedt1-dtKE1-dtME1));
    qp1{i+1} = filt(qp1{i+1});
    ql1{i+1} = filt(ql1{i+1});
end

qp2_eps = {};
ql2_eps = {};
qp2_eps_noE = {};
ql2_eps_noE = {};
for i = 0:nions2
    qp2_eps{i+1} = filt(qp2{i+1}./dedt2);
    ql2_eps{i+1} = filt(ql2{i+1}./dedt2);
    qp2_eps_noE{i+1} = filt(qp2{i+1}./(dedt2-dtKE2-dtME2));
    ql2_eps_noE{i+1} = filt(ql2{i+1}./(dedt2-dtKE2-dtME2));
    qp2{i+1} = filt(qp2{i+1});
    ql2{i+1} = filt(ql2{i+1});
end


figure('Color',[1 1 1]);
%plot(t1,qp1{1}./dydxpp1{1} / (vol*12*tp1{1}(1)/tauA/2) ,'-','Linewidth',3) 
plot(t1,qp1{1}./dydxpp1{1} / (vol*beta0_1/2/tauA) ,'-','Linewidth',3) 
hold on
%plot(t1,ql1{1}./dydxpl1{1}/ (vol*6*tl1{1}(1)/tauA/2),'--','Linewidth',3) 
plot(t1,ql1{1}./dydxpl1{1}/ (vol*beta0_1/4/tauA),'--','Linewidth',3) 
for i = 1:nions1
    plot(t1,qp1{i}./dydxpp1{i}/ (vol*beta0_1/2/tauA),'-','Linewidth',3) 
    plot(t1,ql1{i}./dydxpl1{i}/ (vol*beta0_1/4/tauA),'--','Linewidth',3) 
end
hold off
ylim([0 2])
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$q_i/dT/dt$','interpreter','latex')
set(gca,'fontsize', 16);

figure('Color',[1 1 1]);
%plot(t2,qp2{1}./dydxpp2{1} / (vol*12*tp1{1}(1)/tauA/2),'-','Linewidth',3) 
plot(t2,qp2{1}./dydxpp2{1} / (vol*beta0_2/2/tauA),'-','Linewidth',3) 
hold on
plot(t2,ql2{1}./dydxpl2{1} / (vol*beta0_2/4/tauA),'--','Linewidth',3) 
for i = 1:nions2
    plot(t2,qp2{i}./dydxpp2{i} / (vol*beta0_2/2/tauA),'-','Linewidth',3) 
    plot(t2,ql2{i}./dydxpl2{i} / (vol*beta0_2/4/tauA),'--','Linewidth',3) 
end
hold off
ylim([0 2])
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$q_i/dT/dt$','interpreter','latex')
set(gca,'fontsize', 16);

6*tl1{1}(1)
6*tl2{1}(1)

12*tp1{1}(1)
12*tp2{1}(1)






figure('Color',[1 1 1]);
plot(t1,filt(dedt1),'-','Linewidth',3) 
%plot(t1,filt(dedt1),'-','Linewidth',3) 
hold on
%plot(t1,filt(dehdt1),'-','Linewidth',3) 
plot(t1,filt(dehdt1),'-','Linewidth',3) 
%plot(t1,dehdt1./dedt1,'-','Linewidth',3) 
plot(t1,filt(dehdt1)./filt(dedt1),'-','Linewidth',3) 
hold off
legend({'$\varepsilon$','$\varepsilon_h$','$\varepsilon_h/\varepsilon$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);


figure('Color',[1 1 1]);
plot(t2,filt(dedt2),'-','Linewidth',3) 
legend({'$\varepsilon$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);

figure('Color',[1 1 1]);
plot(t1,filt(dedt1-dtKE1-dtME1),'-','Linewidth',3) 
hold on
plot(t2,filt(dedt2-dtKE2-dtME2),'-','Linewidth',3) 
hold off
legend({'$Qtot_im$','$Qtot_ba$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);



test = diff(vthpp1{2});
test = [test(1); test];
figure('Color',[1 1 1]);
plot(t1,vthpp1{2},'-','Linewidth',3) 
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$Q$','interpreter','latex')
set(gca,'fontsize', 16);



Q.tep1 = vthpp1;
Q.tel1 = vthpl1;
Q.tep2 = vthpp2;
Q.tel2 = vthpl2;
Q.te1 = vthtot1;
Q.te2 = vthtot2;
Q.uprp1 = uprp1;
Q.uprl1 = uprl1;
Q.urms1 = urms1;
Q.uprp2 = uprp2;
Q.uprl2 = uprl2;
Q.urms2 = urms2;


Q.qp1 = qp1;%dydxpp1;
Q.ql1 = ql1;%dydxpl1;
Q.qp2 = qp2;%dydxpp2;
Q.ql2 = ql2;%dydxpl2;
Q.t1 = t1;
Q.t2 = t2;

Q.qp1_eps = qp1_eps;
Q.ql1_eps = ql1_eps;
Q.qp1_eps_noE = qp1_eps_noE;
Q.ql1_eps_noE = ql1_eps_noE;
Q.eps1 = filt(dedt1);
Q.dtE1 = filt(dtKE1+dtME1);
Q.eta1 = filt(diss_hypr1);
Q.eta1_eps = filt(diss_hypr1./dedt1);
Q.eta1_eps_noE = filt(diss_hypr1./(dedt1-dtKE1-dtME1));
Q.eps_noE1 = filt(dedt1-dtKE1-dtME1);
Q.eps_noE_eps1 = filt((dedt1-dtKE1-dtME1)./dedt1);

Q.qp2_eps = qp2_eps;
Q.ql2_eps = ql2_eps;
Q.qp2_eps_noE = qp2_eps_noE;
Q.ql2_eps_noE = ql2_eps_noE;
Q.eps2 = filt(dedt2);
Q.dtE2 = filt(dtKE2+dtME2);
Q.eta2 = filt(diss_hypr2);
Q.eta2_eps = filt(diss_hypr2./dedt2);
Q.eta2_eps_noE = filt(diss_hypr2./(dedt2-dtKE2-dtME2));
Q.eps_noE2 = filt(dedt2-dtKE2-dtME2);
Q.eps_noE_eps2 = filt((dedt2-dtKE2-dtME2)./dedt2);


save([ savebase 'PlotQ-all' sname '.mat'],'Q', '-v7.3');


    figure('Color',[1 1 1]);
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');
    plot(t1,bbprp1.^2,'LineWidth',1)
    ylabel('$(\delta B_{\perp}/B_{0})^{2}$','interpreter','latex');
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'fontsize', 16);

    figure('Color',[1 1 1]);
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');
    plot(t1,(dbprl1+bbprp1).^2,'LineWidth',1)
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    ylabel('$(\delta B/B_{0})^{2}$','interpreter','latex');
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    set(gca,'fontsize', 16);


if loadspec
    close all
    figure(14); clf; pwidth=18.5; pheight=14.8;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.289; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.67,width,height], [offset+width+gap,0.67,width,height], ...
                [offset,0.37,width,height], [offset+width+gap,0.37,width,height], ...
                [offset,0.07,width,height], [offset+width+gap,0.07,width,height] };
    tlab    = { 'Bprp','B' };


    subplot(3,2,1);
    plot(t1(nbfinds1),dBprpICWfrac1,'LineWidth',1)
    %axis([1 max(t1) 1e-2 1e2]);
    ylabel('$(\delta B_{\perp,\rm ICW}/\delta B_{\perp})^{2}$')
    %yticks(logspace(-2,2,5)); yticklabels({'$10^{-2}$','$10^{-1}$','$10^0$','$10^1$','$10^2$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    %leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg = legend([p3],'$\,Q_{\rm tot}/\varepsilon_{\rm inj}$','Location','Northeast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003,'ylabeldx',-0.005);

    subplot(3,2,2);
    plot(t1(nbfinds1),dBtotICWfrac1,'LineWidth',1)
    %axis([1 max(t2) 1e-2 1e2]);
    %yticks(logspace(-2,2,5)); yticklabels({'$10^{-2}$','$10^{-1}$','$10^0$','$10^1$','$10^2$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg = legend([p3],'$\,Q_{\rm tot}/\varepsilon_{\rm inj}$','Location','Northeast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);

    subplot(3,2,3);
    plot(t1,bbprp1.^2,'LineWidth',1)
    %axis([1 max(t1) -1 7.5]);
    ylabel('$(\delta B_{\perp}/B_{0})^{2}$');
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    set(gca,'XTickLabel',[]);
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.002,'ylabeldx',-0.033);

    subplot(3,2,4);
    plot(t1,(dbprl1+bbprp1).^2,'LineWidth',1)
    %axis([1 max(t2) -1 7.5]);
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
    %    'Location','NorthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);

    subplot(3,2,5);
    plot(t1(nbfinds1),dBprpICW1,'LineWidth',1)
    %axis([1 max(t1) 4e-2 2]);
    ylabel('$(\delta B_{\perp,\rm ICW}/B_{0})^{2}$')
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{5});
    %text(11.8,0.19,'$i=$','Interpreter','latex','FontSize',10);
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    subplot(3,2,6);
    plot(t1(nbfinds1),dBtotICW1,'LineWidth',1)
    %axis([1 max(t2) 4e-2 2]);
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{6});
    %text(6.05,0.19,'$i=$','Interpreter','latex','FontSize',10);
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003);

end



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

function inds = restart_overlaps(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1;
inds = [];
for inn = 1:length(rinds)
    tb = t(rinds(inn)-1);
    ia = find(t(rinds(inn):end)>tb,1);
    inds = [inds rinds(inn)-1:rinds(inn)+ia];
end
inds = setdiff(1:length(t),inds);

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
disp('restart times are ')
disp(t(rinds)/(6*22.0))
end
%[189 242 259 297 332 337 371 478 572 611 698 760 826 896 960 980 1042 1110 1187 1322]
%[163 230 230 280 328 279 328 462 569 603 672 759 821 887 957 957 1041 1103 1171 1308]
%[1.22 1.52 1.52 1.67 1.90 1.67 1.90 2.58 3.27 3.49 3.95 4.40 4.86 5.31 5.76 5.76 6.22 6.67 7.13 8.04]

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