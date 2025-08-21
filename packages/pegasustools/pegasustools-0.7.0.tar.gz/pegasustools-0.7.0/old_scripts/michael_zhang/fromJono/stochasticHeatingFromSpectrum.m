function stochasticHeatingFromSpectrum

% Estimate stochastic heating from spectrum like Silvio
name = 'half_tcorr_sim9';
load(['saved-analysis/spectrum-' name '.mat'],'S');
load(['saved-analysis/averageDFs-' name '.mat'],'F');

beta0 = 0.3;
vthp = sqrt(0.3);

mass = [1 16 4];
vthi = vthp./sqrt(mass);
species = 3;
vol=6*48.1802^3;
tauA = 6*48.1802;
ppc = [1000 64 64];
ncells = 6*280^3; nmesh = 24*20*14;
nprtl = ncells.*ppc;
epsin = 12.9;%36.5;
nrm = epsin.*nprtl./vol; 
nums = [0:54 ];
nbfnums = [0:108];
loadAvf0=1;
if strcmp(name,'lev'); tauA = 206.4865395;end
nrmdfdt = nrm;
vresltn =50;
nrm = nrm./vresltn^2; % Since there are 50 points per vth
tplt = [ 9.5];%[1 3  7 9  ];%+18;
dtplt = 1.0;%0.3;

ncells = 6*280^3; nmesh = 24*20*14;
% snapshots to compare, find numbers that match
% [fn,sn]=ind2sub(size(S.t-F.t.'),find(abs(S.t-F.t.')<20));
% fn = fn(2:end);sn=sn(2:end);

% For now, assume potential part is bigger
% Phik is power in E at kperp
S=fixNormalization(S);
Epk = sqrt(-flipud(cumtrapz(flipud(S.k),flipud(S.Ecc2+S.Ecc3),1)));
Phik = Epk./S.k;

kappa0 = 0.9;
cstar = 0.3;

tas = nums*57.8162./tauA; %every 0.2 tauA for spec output

p_id = 'minor_turb';
fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs

% Plots variables from hst file
fulldata = importdata([ fname '.hst']);

try
    names = strsplit(fulldata.textdata{2},'  ');
    names = names(1:end-1);
    dat = fulldata.data;
catch
    dat = fulldata;
end

t_hst = dat(:,1);
is = restart_overlaps2(t_hst);

dt = dat(:,2);
dthst = diff(t_hst);dthst = [ dthst(1);dthst ];


t_hst=t_hst(is)/tauA;
sp = species;
F.t=F.t/tauA;S.t=S.t/tauA;

vthpp = {};
vthpl = {};
vthpp{1} = sqrt(dat(is,28))/sqrt(2);
vthpl{1} = sqrt(dat(is,27));
for i = 1:length(mass)-1
    vthpp{i+1} = sqrt(dat(is,38+19+24*(i-1)))/sqrt(2);
    vthpl{i+1} = sqrt(dat(is,38+18+24*(i-1)));
end

for i = 1:length(mass)
    vthpp{i} = vthpp{i}/vthpp{i}(1);
    vthpl{i} = vthpl{i}/vthpl{i}(1);
end

disp('hello')
disp(t_hst-tas<0.5/tauA)
disp(find(t_hst-tas<0.5/tauA,1))

numinds = [];
for i = 1:length(F.t)
  %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
  numinds = [numinds find(t_hst-F.t(i)>0.5/tauA,1)];
end

nbfinds = [];
for i = 1:length(S.t)
  %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
  nbfinds = [nbfinds find(t_hst-S.t(i)>0.5/tauA,1)];
end

%disp(numinds)

%for i = 1:length(P.vprpmaxav)
%    vthpp{i} = vthpp{i}(numinds);
%    vthpl{i} = vthpl{i}(numinds);
%end

vthspec(1,:) = vthi(sp)*vthpp{sp}(nbfinds);
vprp = [];
vprl = [];
for i = 1:length(vthpp{sp})%length(specinds)
  vprp = cat(3,vprp,F.vprp{sp}./vthpp{sp}(i));%(specinds(i)));
  vprl = cat(3,vprl,transpose(F.vprl{sp})./vthpp{sp}(i));%(specinds(i)));
end

% non avg specoutput vprp and vprl
t_hstog = t_hst;
vprpog = vprp;
vprlog = vprl;
% will need to rescale vprp by current thermal velocity if we change
% DistributionFunctions to use current thermal velocity for vprp
wp = vthi(sp)*F.vprp{sp}.'; %wp in units of v_A (F.vprp uses initial vthi for each species)
Om = 1;
wpk = kappa0*Om./S.k;
kw = kappa0*Om./wp;
xiwk = Phik./wpk.^2;
for ttt=1:size(Phik,2)
    xiw(:,ttt) = interp1(S.k,Phik(:,ttt),kw,'spline',NaN)./wp.^2;
    Ew(:,ttt) = interp1(S.k,Epk(:,ttt),kw,'spline',NaN);
end

% probably here is where we might want to correct vthermal
Dpnorm = 1/30*1/epsin./vthspec.^2;%1/30*1/epsin/vthi(sp)^2;
disp('4 sizes')
disp(size(vthspec));
disp(size(wpk));
disp(size(wp));
disp(size(Dpnorm));
Dppk = Dpnorm.*vthspec.^4.*(wpk./vthspec).^4.*xiwk.^3.*exp(-cstar./xiwk)*vol;%Dpnorm.*vthi(sp)^4*(wpk/vthi(sp)).^4.*xiwk.^3.*exp(-cstar./xiwk)*vol;
Dppw = Dpnorm.*(wp./vthspec).^4.*xiw.^3.*exp(-cstar./xiw)*vol;
%xiwMatt = 1./(kappa0 * beta0^0.5 * (wp/vthi(sp)).*Ew.^-1); % uses initial temps? - mfz - maybe scale beta by current T
xiwMatt = 1./(kappa0 * wp.*Ew.^-1);
%DppMatt = Dpnorm*kappa0^-3*beta0^-1.5*(wp./vthi(sp)).*Ew.^3.*exp(-cstar./xiwMatt)*vol;% Same thing in a different form as a check
DppMatt = Dpnorm.*kappa0^-3.*vthspec.^-3.*(wp./vthspec).*Ew.^3.*exp(-cstar./xiwMatt)*vol;% 

% Distribution function bits
if loadAvf0
    % Didn't copy over f0 so, get from average ones
    Fa = load(['saved-analysis/AvDFs-' name '.mat']);
    Fa = Fa.F;
    P.nspec_prlav = [1000 2000 2000];%[400 400 400];%%[1000 2000 2000];
    P.nspec_prpav = [500 1000 1000];%[200 200 200];%[500 1000 1000];
    P.vprpmaxav = [10 20 20];%[4 4 4]%[10 20 20];
    P.vprlmaxav = [10 20 20];%[4 4 4]%[10 20 20];
    P.savemid = [200 200 200];%[500 1000 1000];
    vprlst = P.nspec_prlav/2-P.savemid+1 ; vprlend = P.nspec_prlav/2+P.savemid;
    Fa.t=Fa.t/tauA;
    tav = Fa.t;
    f0a = Fa.f0{sp}(vprlst(sp):vprlend(sp),1:P.savemid(sp),:);
    disp(size(f0a))
    %vprl = Fa.vprl{sp};
    %vprp = Fa.vprp{sp};
    
    avinds = [];
    for i = 1:length(tav)
      %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
      avinds = [avinds find(t_hst-tav(i)>0.5/tauA,1)];
    end
    t_hst=tav;
    vthavs(1,1,:) = vthi(sp)*vthpp{sp}(avinds);
    vresltn = P.nspec_prpav./P.vprpmaxav;
    % load(['saved-analysis/AvDFs-' name '.mat']);
    % Dpp from time evolution
    wpf = permute(Fa.vprp{sp},[2 1 3]);%Fa.vprp.';
    wpf(1,:,:)=1e-4; %wpf(1)=1e-4;
    %prlrang = Fa.vprl>-10.*(3-sqrt(5))/sqrt(0.3); % Changing the number here changes the sh
    smprl = @(f) squeeze(sum(f(:,:,:),1));%smprl = @(f) squeeze(sum(f(prlrang,:,:),1));   
    nrmf = 1./Fa.vprp{sp};nrmf(1)=1e-4;
    fE = smprl(nrmf.*Fa.f0{sp}./nprtl(sp));
    dfdt = grad3(nrmf.*Fa.f0{sp},Fa.t)./nrmdfdt(sp);
    dfEdt = smprl(dfdt);
    %disp(size(wpf))
    %disp(size(vthavs))
    dfdw = dbydw2(fE,wp.*vthavs); %dbydw2(fE,wp);%wpf? IF wp, would need torescale Fa.vprp{sp} s.t. it's in alfven units (multiply by vth current)
    % This is A1 from Cerri
    DppF = cumtrap2(wpf(:,1,:).*dfEdt,wpf)./(1./wpf(:,1,:).*dfdw)./vresltn(sp); %DppF = cumtrap2(wpf(:,1,:),wpf(:,1,:).*dfEdt,1)./(1./wpf.*dfdw)/vresltn;
    
else
    tav = F.t;
    f0a = F.f0{sp};
    DppF = 0;wpf=0;
end


heatip = mean(F.edv_prp{sp}(:,:,1:2),3);
F.edv_prp = (F.edv_prp{sp}-heatip)./nrm(sp);
filt = @(f) filter((1/5)*ones(1,5),1,f);

m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
m2 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);


tavplt = [tplt-dtplt;tplt+dtplt];
%disp(find(tav>=tavplt(1,1) & tav<=tavplt(2,1)))
%disp(find(t_hst>=tavplt(1,1) & t_hst<=tavplt(2,1)))
plotF = 0;
if plotF
    figure;set(gcf,'Color','white');
    i=species;  %species
    %for i = 1:length(P.vprpmaxav)
        for ttt=1:length(tplt)
            f0 = m(Fa.f0{i}(vprlst(i):vprlend(i),1:P.savemid,:),tav,tavplt(:,ttt))./ int_dist(m(Fa.vprl{i}(vprlst(i):vprlend(i),1,:),tav,tavplt(:,ttt)),m(Fa.vprp{i}(1,1:P.savemid(i),:),tav,tavplt(:,ttt)),m(Fa.f0{i}(vprlst(i):vprlend(i),1:P.savemid(i),:),tav,tavplt(:,ttt)));
            vprl = m(Fa.vprl{i}(vprlst(i):vprlend(i),1,:),tav,tavplt(:,ttt));
            vprp = m(Fa.vprp{i}(1,1:P.savemid(i),:),tav,tavplt(:,ttt));
        vprpn = vprp;
        contourf(vprl,vprp,log10(f0./vprpn).',15);set(gca,'YDir','normal');
        end
end



% Put together 
figure
wp = wp/vthi(sp);
for ttt=1:length(tplt)
        vprlplot = m(vprl,t_hst,tavplt(:,ttt));
        vprlplot = vprlplot(:,1);
        vprpplot = m(vprp,t_hst,tavplt(:,ttt));
        vprpplot = vprpplot(1,:);
        %disp(size(vprlplot))
        %disp(size(vprpplot))
        %disp(size(m(f0a,tav,tavplt(:,ttt))))
        f0 = m(f0a,tav,tavplt(:,ttt))./ int_dist(vprlplot,vprpplot,m(f0a,tav,tavplt(:,ttt)));
        fprp = trapz(vprlplot,f0,1)./vprpplot/2;
        dfprp = gradient(fprp,vprpplot(2)-vprpplot(1))/vthi(sp);
        dqprp = sum(m(F.edv_prp,F.t,tavplt(:,ttt)),1);
        %disp(size(dqprp))
        %disp(size(dfprp))
        % only if loading non averaged spec or if loading averaged
        % edotvavs, or adjust size of averaged spec
        %disp(dqprp)
        Dpp = -filt(dqprp./dfprp);
        %int_dist(vprlplot,vprpplot,m(f0a,tav,tavplt(:,ttt)))
        %disp(m(f0a,tav,tavplt(:,ttt)))
        %test = find(t_hst>=tavplt(1,ttt) & t_hst<=tavplt(2,ttt));
        %disp(test)
        %disp(mean(vprl(:,1,23:39),3))
        %disp(vprlplot)
        %disp(vprpplot)
        %disp(Dpp)



    %loglog(wp,m2(DppMatt,S.t,tavplt(:,ttt)),'--','Color',tcol(tplt(ttt),[min(tplt),max(tplt)]),'LineWidth',1)

    vprpD = m(vprpog,t_hstog,tavplt(:,ttt));
    %vprpD = vprpplot(1,:);
    dppwplot = m2(Dppw,S.t,tavplt(:,ttt));
    dppwind = find(isnan(dppwplot));
    dppwind = setdiff(1:length(dppwplot),dppwind);%returns all indices except those in inds
    loglog(vprpD(1,dppwind),dppwplot(dppwind),'--','LineWidth',1);%,'Color',tcol(tplt(ttt),[min(tplt),max(tplt)]),'LineWidth',1)
    hold on

    %disp(m2(Dppw,S.t,tavplt(:,ttt)))
    %disp(size(vprpD))
    %disp(m2(DppMatt(6:end,:),S.t,tavplt(:,ttt)));
    dppmplot = m2(DppMatt,S.t,tavplt(:,ttt));
    dppmind = find(isnan(dppmplot));
    dppmind = setdiff(1:length(dppmplot),dppmind);%returns all indices except those in inds
    loglog(vprpD(1,dppmind),dppmplot(dppmind),'LineWidth',1);

    hold on
    %disp(size(wpf))
    %disp(size(m2(DppF,Fa.t,tavplt(:,ttt))))
    loglog(m2(wpf,Fa.t,tavplt(:,ttt)),m2(DppF,Fa.t,tavplt(:,ttt)),'-','LineWidth',1);%,'Color')%tcol(tplt(ttt),[min(tplt),max(tplt)]),'LineWidth',1)
    hold on
    dppind = find(isnan(Dpp));
    dppind = setdiff(1:length(Dpp),dppind);%returns all indices except those in inds
    loglog(vprpD(1,dppind),Dpp(dppind),'-','LineWidth',1);
    hold on
    %m(vprp,t_hst,tavplt(:,ttt))(1,:)
    % semilogx(F.vprp,Dpp);
    %xlim([0.01 6])
    %ylim([0.1e-3 1e2])
    % ylim([-1e-3 4e-3])
    title(['t=' num2str(tplt(ttt))]);

    % ginput(1);
end
loglog(wp,5*wp.^2,'k:')
legend({'$Dppw$','$DppMatt$','$DppF$','$Dpp$','$5  wp^{2}$'},'interpreter','latex')
xlabel('$w_\perp$','Interpreter','latex')
%disp(dqprp)
%disp(fprp)

% lw = 1;
% rhoi = sqrt(0.3);
% beta = 0.3;
% 
% % Compare Phi spectra between my run and Lev's
% load(['saved-analysis/spectrum-' 'lev' '.mat'],'S');
% S=fixNormalization(S);
% tauA = 206.4865395;
% S.t = S.t/tauA;
% m = @(d,t,tav) mean(d(:,find(t>=tav(1),1):find(t<=tm2(DppF,tav,tavplt(:,ttt))av(2),1,'last')),2);
% 
% 
% 
% loglog(S.k,m(S.Phi,S.t,[2 6]),'k','Linewidth',1.5)
% hold on
% loglog(S.k,m(S.Phi,S.t,[5 22]),'k','Linewidth',0.3)
% 
% load(['saved-analysis/spectrumPhi-' 'imbal2-prod' '.mat'],'S');
% S=fixNormalization(S);
% tauA = 6*67.4523;
% S.t = S.t/tauA;
% 
% tplot = [2:2:16];
% for ttt=1:length(tplot)
%     loglog(S.k,m(S.Phi,S.t,tplot(ttt)+[-1 1]),'Color',tcol(tplot(ttt)),'Linewidth',1.0)
% end
% 
% k83 = S.k; k53 = S.k(S.k>1/rhoi); k5 = S.k(S.k>1 & S.k<3/rhoi); 
% k83mult = 1.2;k53mult = 12*8e-6;k5mult = 4.8e-3;
% loglog(k83,k83mult.*(k83/k83(1)).^(-11/3),'k:',k53,k53mult*(k53/k53(1)).^(-8/3),'k:',...
%     k5,k5mult*(k5/k5(1)).^(-6),'k:',1/rhoi*[1 1],[1e-30,1e10],'k:','Linewidth',0.5)
% ylabel('$E_{\Phi}$','interpreter','latex')
% xlabel('$k_\perp$','interpreter','latex')
% legend({'Balanced (SH dominates)','Balanced (KAW dominates)',...
%     '$t=2\tau_A$','$t=4\tau_A$','$t=6\tau_A$','$t=8\tau_A$','$t=10\tau_A$','$t=12\tau_A$','$t=14\tau_A$','$t=16\tau_A$',...
%     '$k^{-11/3}$','$k^{-8/3}$','$k^{-6}$'},'interpreter','latex')
% ylim([1e-9 3])
% xlim([min(S.k) max(S.k)])
% set(gcf,'Color','w')
% 
% lw = 1;
% rhoi = sqrt(0.3);
% 
% 
% 
% %%%%%%%%%%%%%%%%% Density spectra in the same way.
% figure
% % Compare density spectra between my run and Lev's
% load(['saved-analysis/spectrum-' 'lev' '.mat'],'S');
% S=fixNormalization(S);
% tauA = 206.4865395;
% S.t = S.t/tauA;
% m = @(d,t,tav) mean(d(:,find(t>=tav(1),1):find(t<=tav(2),1,'last')),2);
% 
% % S.ntild = (beta*(1+beta))*m(S.dens);
% S.Bprp = S.Bcc2+S.Bcc3;
% 
% % loglog(S.k,m(S.Bprp,S.t,[5 22]),'k--','Linewidth',1)
% 
% load(['saved-analysis/spectrum-' 'imbal2-prod' '.mat'],'S');
% S=fixNormalization(S);
% tauA = 6*67.4523;
% S.t = S.t/tauA;
% 
% S.ntild = (beta*(1+beta))*S.dens;
% S.Bprp = S.Bcc2+S.Bcc3;
% 
% tplot = [4:3:16];
% for ttt=1:length(tplot)
%     loglog(S.k,m(S.ntild,S.t,tplot(ttt)+[-1 1]),'Color',tcol(tplot(ttt)),'Linewidth',1.0)
%     hold on
% end
% for ttt=1:length(tplot)
%     loglog(S.k,m(S.Bprp,S.t,tplot(ttt)+[-1 1]),'--','Color',tcol(tplot(ttt)),'Linewidth',0.3)
% end
% 
% k53 = S.k; k28= S.k(S.k>1/rhoi); 
% k53mult = 0.12;k28mult = 1.2e-4;
% loglog(k53,k53mult.*(k53/k53(1)).^(-5/3),'k:',k28,k28mult.*(k28/k28(1)).^(-2.8),'k:','Linewidth',0.5)
% ylabel('$E_{\tilde{n}}$','interpreter','latex')
% xlabel('$k_\perp$','interpreter','latex')
% legend({...
%     '$t=4\tau_A$','$t=7\tau_A$','$t=10\tau_A$','$t=13\tau_A$','$t=16\tau_A$'},'interpreter','latex')
% ylim([1e-9 3])
% xlim([min(S.k) max(S.k)])
% set(gcf,'Color','w')


end

function  out = int_dist(vprl,vprp,F)

out = trapz(vprl,trapz(vprp,vprp.*F,2),1);

end

function S=fixNormalization(S)
% Stuffed up overall factor on nnorm. Want int(dk EK)=u^2
nnorm_old = S.nnorm;
nnorm = S.nbin./S.k;
a = 1/sum(nnorm)*trapz(S.k,ones(size(S.k)));
S.nnorm = a*nnorm;
fields = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','vel1','vel2','vel3','dens','thetaP','thetaM','ZP','ZM','Phi'}; 
for var = [fields]
    if isfield(S,var{1})
        S.(var{1}) = S.(var{1}).*nnorm_old./S.nnorm;
    end
end

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
