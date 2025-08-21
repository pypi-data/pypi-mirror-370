function S=spectrum_alf%(name)

% Spectrum of the Alfvenic and KAW variables
i_b3 = 0;
b_b3 = 0;
i_b0625 = 1; %do out to more nbfs
b_b0625 = 0;
i_b1 = 0;
b_b1 = 0;

P.numKgrid = 200;%2000; % nonzero for logarithmic binning
P.perp=1; % Only  perp for this version
P.derefine_prl =1; P.derefine_prp=1;

DoFullCalculation = 0;
reloadSpectrumFile = 1;
copyViaScp=0;

plotEB=1;
paperPlot=0;
plotAllTimes = 0;
plotPlusMinus =0;
plotSig=0;
plot_gradient = 1;
plotDens = 0;


if i_b3
    name = 'half_tcorr_sim9';
    nums = [0:152];
    mass = [1 16 4];
    qom = [1 5/16 1/2];
end
if b_b3
    name = 'b_b3_sim1';
    nums = [0:76]; 
    mass = [1 16 4 16 12 12 56];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/56];
end
if i_b0625
    name = 'hb_beta0625';
    nums = [0:133];%[0:82];
    mass = [1 16 4 16 12 12 24];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/24];
end
if b_b0625
    name = 'b_b0625_sim1';
    nums = [0:38];
    mass = [1 16 4 16 12 12 24];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/24];
end
if i_b1
    name = 'i_b1_sim1';
    nums = [0:34];%[0:18];
    mass = [1 16 4 16 12 12 24 1];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/24 1];
end
if b_b1
    name = 'b_b1_sim1';
    nums = [0:38];
    mass = [1 16 4 16 12 12 24 1];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/24 1];
end


if b_b0625 || i_b0625
    tauA = 6*22.0;
    beta = 0.0625;
end
if b_b3 || i_b3
    tauA =6*48.1802; 
    beta = 0.3;
end
if b_b1 || i_b1
    tauA =6*87.96459; 
    beta = 1.0;
end
rhoi = sqrt(beta);
if strcmp(name,'lev'); tauA = 206.4865395;disp('lev');end

species = 1;


p_id = 'minor_turb';

if i_b0625
    computer = 'tigressevan';
    fname = ['../../eyerger/' name '/output/' p_id ]; % Folder with outputs']; % Folder with outputs
else
    computer = 'tigress';
    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end

n2s = @(s) num2str(s);
[readF,files_all,folder] = chooseComputerAndFiles(name,computer);
savebase = [ './saved-analysis/'];
savefolder = [ savebase 'spectrum-' name '.mat'];

disp(['Saving/loading from ' savefolder])

% load history



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
%is = restart_overlaps2(t_hst);
if i_b3
    is = restart_overlaps2(t_hst);
else
    is = restart_overlaps3(t_hst);
end
if i_b0625
    is = restart_overlaps4(t_hst);
end


dt = dat(:,2);
dthst = diff(t_hst);dthst = [ dthst(1);dthst ];


t_hst=t_hst(is)/tauA;
sp = species;

vthpp = {};
vthpl = {};
vthtot = {};
vthpp{1} = sqrt(dat(is,28))/sqrt(2);
vthpl{1} = sqrt(dat(is,27));
vthtot{1} = sqrt(dat(is,28)+dat(is,27));
if b_b3 || b_b0625 || b_b1
    ionind = 35;
else
    ionind = 38;
end
for i = 1:length(mass)-1
    vthpp{i+1} = sqrt(dat(is,ionind+19+24*(i-1)))/sqrt(2);
    vthpl{i+1} = sqrt(dat(is,ionind+18+24*(i-1)));
    vthtot{i+1} = sqrt( dat(is,ionind+19+24*(i-1)) +  dat(is,ionind+18+24*(i-1)) );
end

for i = 1:length(mass)
    vthpp{i} = vthpp{i}/vthpp{i}(1);
    vthpl{i} = vthpl{i}/vthpl{i}(1);
    vthtot{i} = vthtot{i}/vthtot{i}(1);
end


if DoFullCalculation

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   CONSTRUCT K GRID AND OTHER GENERAL BITS
% If 0, standard k grid, 0:2*pi/L:..., otherwise use standard until
% spacing smaller than numKgrid, then use logarithmic grid

% Form grid of K using first time step
num1 = nums(1);
disp(['Reading ' files_all(num1)])
D = readF(files_all(num1));
D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
D
dx = D.x(2)-D.x(1);
dy = D.y(2)-D.y(1);
dz = D.z(2)-D.z(1);
Ls = [D.x(end)-D.x(1)+dx D.y(end)-D.y(1)+dy D.z(end)-D.z(1)+dz];
Ns = [length(D.x) length(D.y) length(D.z)];
% Grid in k space, for each dimension, conforming to FT standard [0 1 2 3 ... -N/2 -N/2+1 ... -1]
for kk=1:3
    K{kk} = 2i*pi/Ls(kk)*[0:(Ns(kk)/2-1) -Ns(kk)/2 -Ns(kk)/2+1:-1].';
end
[k3.KX, k3.KY, k3.KZ] = ndgrid(K{1},K{2},K{3}); % 3D grid in K
% Kmag = sqrt(abs(k3.KX).^2 + abs(k3.KY).^2 + abs(k3.KZ).^2); % |K|
Kperp = sqrt(abs(k3.KY).^2 + abs(k3.KZ).^2); % |K|
kyg0 = imag(k3.KY)>0;
clear  Kmag %k3

% Function in front of E_perp
k2m = rhoi^2/2;
KP = Kperp; KP(KP<2*pi/Ls(2))=2*pi/Ls(2);
omG0 = 1-besseli(0,k2m*KP.^2,1);
Emult = rhoi/sqrt(2)*omG0.*sqrt(1./omG0+1)./KP;
Emult = Emult/(rhoi^2/2);
clear omG0 KP;

% Bins for k
% kgrid = (0:2*pi/Ls(2):max(imag(K{2}))).'+1e-4; % Use ky for spectrum binning
% if P.numKgrid ~= 0
%     kgridL = logspace(log10(abs(K{2}(2))),log10(max(abs(K{2}))) ,P.numKgrid ).'; 
%     iswtch = find(diff(kgridL)<2*pi/Ls(2),1,'last');
%     lin2log = find(kgrid<kgridL(iswtch+1),1,'last'); % index at which you switch to log scale
%     kgrid = [kgrid(1:lin2log-1);  logspace(log10(kgrid(lin2log)),log10(max(abs(K{2}))), length(kgridL(iswtch+1:end)) ).' ];
% end
% Diferent version: logarithmic, but remove unused bins at small k
kgrid = logspace(log10(abs(K{2}(2))-1e-8),log10(max(abs(K{2}))) ,P.numKgrid ).';
kfull = [-1 ; kgrid; 1e100];
Nkfull = length(kfull)-1;
[cnts,~, bins] = histcounts(Kperp(:),kfull); 
bins = min(max(bins,1),Nkfull);
cnts = cnts(2:end);
kgrid(cnts==0)=[];
% To hold the spectrum
S.Nk = length(kgrid);
S.k = kgrid(1:end);
% Preload the bins and counts for each k
kfull = [-1 ; kgrid; 1e100];
Nkfull = S.Nk+2;
[cnts,~, bins] = histcounts(Kperp(:),kfull); 
bins = min(max(bins,1),Nkfull);
NT2 = numel(Kperp)^2;
clear Kperp;

% Count the number of modes in each bin to normalize later -- this gives a
% smoother result, since we want the average energy in each bin.
oneG = ones(sqrt(NT2),1);
S.nbin = spect1D(oneG,bins,Nkfull,NT2)*numel(oneG)^2;
clear oneG;

S.nnorm = S.nbin./S.k;
a = 1/sum(S.nnorm)*trapz(S.k,ones(size(S.k))); % normalization so int(E(k)) = E
S.nnorm = a*S.nnorm;
m3 = @(a) mean(mean(mean(a)));

% Average over all the snapshots
fields = {'Phi','Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','thetaP','thetaM','vel1','vel2','vel3','dens','ZP','ZM'};
for var = fields;S.(var{1}) = [];end

S.t=[];S.nums=[];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
if reloadSpectrumFile ==1
    load(savefolder,'S','P');S
    P
end
for nnn=nums
    clear D;
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
    [readF,files_all,folder] = chooseComputerAndFiles(name,computer);
    try 
        if copyViaScp && any(nnn==[53 57])==0
            files_all = copyFromFrontera(name,computer,'grid',nnn);
        end
        D = readF(files_all(nnn));
        D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
    catch 
        warning(['Did not find ' folder ' nnn=' num2str(nnn)])
        continue
    end
    S.t = [S.t D.t];
    
    for var = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','dens','vel1','vel2','vel3'}%
        disp(var)
        ft = fftn(D.(var{1}));
        S.(var{1}) = [S.(var{1})  spect1D(ft,bins,Nkfull,NT2)./S.nnorm];
    end
    ftPhi = (k3.KX.*fftn(D.Ecc1) + k3.KY.*fftn(D.Ecc2) + k3.KZ.*fftn(D.Ecc3))./...
                (abs(k3.KX).^2 + abs(k3.KY).^2 + abs(k3.KZ).^2);
    S.Phi = [S.Phi  spect1D(ftPhi,bins,Nkfull,NT2)./S.nnorm]; 
    
    % Assume sqrt(rho)=1 and perp = y,z
    theta2 = -Emult.*fftn(-D.Ecc3) + fftn(D.Bcc2);
    theta3 = -Emult.*fftn(D.Ecc2) + fftn(D.Bcc3);
    S.thetaP = [S.thetaP   (spect1D(theta2,bins,Nkfull,NT2)+spect1D(theta3,bins,Nkfull,NT2))./S.nnorm];
    theta2 = -Emult.*fftn(-D.Ecc3) - fftn(D.Bcc2);
    theta3 = -Emult.*fftn(D.Ecc2) - fftn(D.Bcc3);
    S.thetaM = [S.thetaM   (spect1D(theta2,bins,Nkfull,NT2)+spect1D(theta3,bins,Nkfull,NT2))./S.nnorm];
    % Save Zp and ZM also, to compare 
    theta2 = fftn(D.vel2 + D.Bcc2);
    theta3 = fftn(D.vel3 + D.Bcc3);
    S.ZP = [S.ZP   (spect1D(theta2,bins,Nkfull,NT2)+spect1D(theta3,bins,Nkfull,NT2))./S.nnorm];
    theta2 = fftn(D.vel2 - D.Bcc2);
    theta3 = fftn(D.vel3 - D.Bcc3);
    S.ZM = [S.ZM   (spect1D(theta2,bins,Nkfull,NT2)+spect1D(theta3,bins,Nkfull,NT2))./S.nnorm];
    
%     % Something like magnetic helicity
%     S.sig = [S.sig 2*spectHel(fftn(D.Bcc2),fftn(D.Bcc3).*kyg0,bins,Nkfull,NT2)./S.nnorm];
    S.nums = [S.nums nnn];
    save(savefolder,'S','P');
end
S.n = length(S.t);

%save(savefolder,'S','P');
else % DoFullCalculation
    load(savefolder,'S');
    % For imbal2-prod
%     fields = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','vel1','vel2','vel3','dens','thetaP','thetaM','ZP','ZM'};
%     for var = [fields {'t','nums'}];S.(var{1})(:,9:39) =  [];end
    

end
S=fixNormalization(S);

%%%%%%%%%%%%%%%%%% PLOTTING %%%%%%%%%%%%%%%%%%%%%
wind = floor(1);
filt = @(f) filter((1/wind)*ones(wind,1),1,f.').';
noiseind = 1;
%Enoise = 0*(S.Ecc2(:,noiseind)+S.Ecc3(:,noiseind))/2;
Enoise = (S.Ecc2(:,noiseind)+S.Ecc3(:,noiseind))/2;
S.EMp = filt((S.Bcc2+S.Bcc3)/2);
S.EEp = filt((S.Ecc2+S.Ecc3)/2)-Enoise;
if ~strcmp(name,'lev')
    S.EKp = filt((S.vel2+S.vel3)/2);
    disp('hello')
else
    S.EKp = zeros(size(S.EMp));
    disp('zero')
end

S.t = S.t/tauA;
S.n = length(S.t);

tav = [18 19];
itav = [find(S.t>=tav(1) & S.t<=tav(2))];
m = @(d) mean(d(:,itav),2);
m2 = @(d) mean(d(itav),1);

%dn=10;

dn=1;
S.n

nbfinds = [];
for i = 1:length(S.t)
  %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
  nbfinds = [nbfinds find(t_hst-S.t(i)>0.5/tauA,1)];
end
%dn=20
if plotEB
    figure1 = figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.3, 0.6]);
    %for n=dn:dn+1:S.n-dn;%4-dn;%S.n-dn;
    n=130;%25;%56;
    dn=2;%20;%1;%20
        m = @(d) mean(d(:,n-dn+1:n+dn),2);
        mm = @(d) d(n-dn+1:n+dn);%S.t(n+1)
        m2 = @(d) mean(d(n-dn+1:n+dn),1);
    if plot_gradient;subplot(211);    end
    loglog(S.k, m(S.EMp),'-', S.k, m(S.EEp),'-',S.k, m(S.EKp),'-','Markersize',2)
    hold on
    k53 = S.k;k28 = S.k(S.k>1); k23 = S.k(S.k>1/rhoi); k4 = S.k(S.k>1); 
     k28mult = 0.4e-2;k53mult = 1.5e-1;k23mult = 8e-4;k4mult = 1e-2;
    loglog(k53,k53mult.*(k53/k53(1)).^(-5/3),'k:',k28,k28mult*(k28/k28(1)).^(-2.8),'k:',k23,k23mult*(k23/k23(1)).^(-2/3),'k:',...
        k4,k4mult*(k4/k4(1)).^(-4),'k:',1/rhoi*[1 1],[1e-30,1e10],'k:')


    loglog(1/ (rhoi * m2(vthpp{1}(nbfinds)) * sqrt(1./mass(1))./qom(1))  *[1 1], [1e-30,1e10],'r--')
    loglog(1/ (rhoi * m2(vthpp{2}(nbfinds)) * sqrt(1./mass(2))./qom(2))  *[1 1], [1e-30,1e10],'b--')
    loglog(1/ (rhoi * m2(vthpp{3}(nbfinds)) * sqrt(1./mass(3))./qom(3))  *[1 1], [1e-30,1e10],'g--')

    loglog(S.k, Enoise,'--k')
    ylabel('$E_K$','interpreter','latex')
    xlabel('$k_\perp$','interpreter','latex')
    legend({'$E_{B}$','$E_{E}$','$E_{K}$','$k^{-5/3}$','$k^{-2.8}$','$k^{-2/3}$','$k^{-4}$','$k\rho_i0=1$','$k\rho_p=1$','$k\rho_O5=1$','$k\rho_He=1$','$E$ noise spectrum'},'interpreter','latex')
    %ylim([1e-9 1])
    ylim([1e-5 1])
    xlim([min(S.k) max(S.k)])
%     title(['t=' num2str(S.t(n+1))]);%title({name})
    hold off
    if plot_gradient
        [grb,ok]=grad(m(S.EMp),S.k,[3 20]);%[3 100]);
        [gre,ok]=grad(m(S.EEp),S.k,[3 20]);%[3 100]);
        subplot(212)
        one = ones(size(ok));
        semilogx(ok,grb,ok,gre, ok,-5/3*one,'k:',ok,-2.8*one,'k:',ok,-4*one,'k:',1/rhoi*[1 1],[-10 1],'k:')
        xlim([min(S.k) max(S.k)])
        ylim([-5 0])
        xlabel('$k_\perp$','interpreter','latex')
        ylabel('$\alpha$','interpreter','latex')
        hold off
    end
    title(['t=' num2str(S.t(n+1))]);drawnow;pause(1);%end%ginput(1);end%end
    
end


if plotDens2
    figure1 = figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.3, 0.6]);
    %for n=dn:dn+1:S.n-dn;%4-dn;%S.n-dn;
    n=35;%56;
    dn=1;%20
        m = @(d) mean(d(:,n-dn+1:n+dn),2);
        mm = @(d) d(n-dn+1:n+dn);%S.t(n+1)
        m2 = @(d) mean(d(n-dn+1:n+dn),1);
    loglog(S.k, (beta*(1+beta))*m(S.dens),'-','Markersize',2)
    ylabel('$E_K$','interpreter','latex')
    xlabel('$k_\perp$','interpreter','latex')
    legend({'$E_{\tilde{n}}$'},'interpreter','latex')
    %ylim([1e-9 1])
    xlim([min(S.k) max(S.k)])
%     title(['t=' num2str(S.t(n+1))]);%title({name})
    hold off
    title(['t=' num2str(S.t(n+1))]);drawnow;pause(1);%end%ginput(1);end%end
    S.nums

end

dn=5;
if paperPlot
    m = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m2 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);

    tplt = [7]%[7.5 14.2];
    dtplt = 0.5;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = S.t;

    %m = @(d) mean(d(:,S.n-2*dn+1:S.n-1),2);mm = @(d) d(S.n-2*dn:S.n-1);S.t(S.n)
    %m2 = @(d) mean(d(S.n-2*dn:S.n-1),1);

    paper.k = S.k;
    paper.nbfinds = nbfinds;
    paper.vthpp = vthpp;

    paper.Emp = {};
    paper.Eep = {};
    paper.vthpp1 = {};
    paper.vthpp2 = {};
    paper.vthpp3 = {};

    for ttt = 1:length(tplt)
        paper.Emp{ttt} = m(S.EMp,tav,tavplt(:,ttt));
        paper.Eep{ttt} = m(S.EEp,tav,tavplt(:,ttt));
        paper.vthpp1{ttt} = m2(vthpp{1}(nbfinds),tav,tavplt(:,ttt));
        paper.vthpp2{ttt} = m2(vthpp{2}(nbfinds),tav,tavplt(:,ttt));
        paper.vthpp3{ttt} = m2(vthpp{3}(nbfinds),tav,tavplt(:,ttt));
    end
    paper.Emp
    save([ savebase 'PlotSpectrum1D-' name '.mat'],'paper', '-v7.3');


end



dn = 10;
toplt = 'EMp';%'EEp';
if plotAllTimes
    % Spectra at evenly spaced times for one field
    dir = ['../simulations/' name '/saved-plots/specalf/B'];
    exportname = [dir,'.pdf'];
    figure1 = figure('Color',[1 1 1]);
    set(gcf, 'Units', 'centimeters', 'OuterPosition', [20 20 16 13]);
    sp1 = subplot(2,1,1,'Parent',figure1);
     sp1.Position = sp1.Position + 0.132*[0 -1 0 1];

    m = @(d) mean(d(:,142-dn+1:142+dn),2);mm = @(d) mean(d(142-dn+1:142+dn));
    t = mm(S.t);
    loglog(S.k, m(S.('EEp')),'--','Color',[0 0.4470 0.7410],'Linewidth',2)





    %ylabel('$E_E$','interpreter','latex')
    ylabel('$\mathcal{E} (k_{\perp})$','interpreter','latex')
    xlabel('$k_\perp$','interpreter','latex')
%     legend({'$E_{B}$','$E_{E}$','$E_{K}$','$k^{-5/3}$','$k^{-2.8}$','$k^{-2/3}$','$k^{-4}$','$k\rho_i=1$','$E$ noise spectrum'},'interpreter','latex')
    ylim([5e-8 1])
    xlim([min(S.k) max(S.k)])
    xticklabels([]);
    hold on
    if plot_gradient
        subplot(212)
        ok=S.k;
        one = ones(size(ok));
        semilogx(ok,-5/3*one,'k:',ok,-0.8*one,'k:',ok,-4*one,'k:',1/rhoi*[1 1],[-10 1],'k:')
        xlim([min(S.k) max(S.k)])
        ylim([-5 0])
        xlabel('$k_\perp$','interpreter','latex')
        ylabel('$\alpha$','interpreter','latex')
        hold on
    end
    

    nplt = [30 50 70 90]%[10    32    54    76    98   120   142   164];%dn:dn+1:S.n-dn;
    for n= nplt;m = @(d) mean(d(:,n-dn+1:n+dn),2);mm = @(d) mean(d(n-dn+1:n+dn));
        if plot_gradient;subplot(sp1);   end
        t = mm(S.t);
        loglog(S.k, m(S.(toplt)),'-','Color',tcol(t,[3 15]),'Linewidth',2)
        hold on; 
        if plot_gradient
            [grb,ok]=grad(m(S.(toplt)),S.k,[3 20]);
            subplot(212)
            semilogx(ok,grb,'Color',tcol(t,[3 15]),'Linewidth',2)
            hold on
        end
    end
    m = @(d) mean(d(:,142-dn+1:142+dn),2);mm = @(d) mean(d(142-dn+1:142+dn));
        if plot_gradient;subplot(sp1);   end
        t = mm(S.t);
        loglog(S.k, m(S.(toplt)),'-','Color',tcol(t,[3 15]),'Linewidth',4)
        hold on; 
        if plot_gradient
            [grb,ok]=grad(m(S.(toplt)),S.k,[3 20]);
            subplot(212)
            semilogx(ok,grb,'Color',tcol(t,[3 15]),'Linewidth',4)
            hold on
        end


    if plot_gradient;subplot(sp1);   end
    k53 = S.k(S.k<3);k28 = S.k(S.k>1); k23 = S.k(S.k>1/rhoi); k4 = S.k(S.k>1); 
    k28mult = 0.4e-2;k53mult = 1.5e-1;k23mult = 4e-4;k4mult = 0.4e-2;
    loglog(k53,k53mult.*(k53/k53(1)).^(-5/3),'k:',k23,k23mult*(k23/k23(1)).^(-0.8),'k:',...k28,k28mult*(k28/k28(1)).^(-2.8),'k:',
    k4,k4mult*(k4/k4(1)).^(-4),'k:',1/rhoi*[1 1],[1e-30,1e10],'k:')

    loglog(1/ (rhoi * vthpp{1}(nbfinds(end)) * sqrt(1./mass(1))./qom(1))  *[1 1], [1e-30 1e10],'k--')
    loglog(1/ (rhoi * vthpp{2}(nbfinds(end)) * sqrt(1./mass(2))./qom(2))  *[1 1], [1e-30 1e10],'k--')
    loglog(1/ (rhoi * vthpp{3}(nbfinds(end)) * sqrt(1./mass(3))./qom(3))  *[1 1], [1e-30 1e10],'k--')
    
    legend({'$\mathcal{E}_{E}, t=14.2 \tau_{A}$','$\mathcal{E}_{B}, t=3 \tau_{A}$','$\mathcal{E}_{B}, t=5 \tau_{A}$','$\mathcal{E}_{B}, t=7 \tau_{A}$','$\mathcal{E}_{B}, t=9 \tau_{A}$','$\mathcal{E}_{B}, t=14.2 \tau_{A}$'},'interpreter','latex','Location','Southwest')
    set(gca,'fontsize', 12);

      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      exportgraphics(fig,exportname,'ContentType','vector');

end

dn=1;
if plotPlusMinus
    % figure
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.3, 0.6]);
    for n=dn:dn:S.n-dn+1; m = @(d) mean(d(:,n-dn+1:n+dn-1),2);mm = @(d) d(n-dn+1:n+dn-1);S.t(n)
    if plot_gradient;subplot(211);end
    loglog(S.k, m(S.thetaP),'-', S.k, m(S.thetaM),'-',...
        S.k, m(S.ZP),'--', S.k, m(S.ZM),'--','Markersize',2)
    hold on
    k53 = S.k;k28 = S.k(S.k>1); k4 = S.k(S.k>1); 
    k28mult = 0.3e-3;k53mult = 5e-1;k4mult = 8e-4;
    loglog(k53,k53mult.*(k53/k53(1)).^(-3/2),'k:')%...
%         ,k28,k28mult*(k28/k28(1)).^(-2.8),'k:',k4,k4mult*(k4/k4(1)).^(-4),'k:',...
%         1/rhoi*[1 1],[1e-30,1e10],'k:')
%     loglog(S.k, (S.thetaP(:,1)+S.thetaM(:,1))/2,'--k')
    ylabel('$E_K$','interpreter','latex')
    xlabel('$k_\perp$','interpreter','latex')
    legend({'$E_{\Theta^+}$','$E_{\Theta^-}$','$E_{Z^+}$','$E_{Z^-}$','$k^{-3/2}$','$k^{-4}$','$k^{-2.8}$','$E^{\pm}$ noise spectrum'},'interpreter','latex')
    % ylim([1e-8 5])
    xlim([min(S.k) max(S.k)])
    title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])%title({name})
    hold off
    if plot_gradient
        [grp,ok]=grad(m(S.thetaP),S.k,[3 20]);
        [grm,ok]=grad(m(S.thetaM),S.k,[3 20]);
        subplot(212)
        one = ones(size(ok));
        semilogx(ok,grp,ok,grm, ok,-5/3*one,'k:',ok,-2.8*one,'k:',ok,-4*one,'k:',1/rhoi*[1 1],[-10 1],'k:')
        xlim([min(S.k) max(S.k)])
        ylim([-5 0])
        xlabel('$k_\perp$','interpreter','latex')
        ylabel('$\alpha$','interpreter','latex')
    end
    title(['t=' num2str(S.t(n))]);ginput(1);end

end


if plotDens
    figure1 = figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.3, 0.6]);
%     for n=floor(0.5*S.n):10:S.n-1; m = @(d) d(:,n+1);mm = @(d) d(n+1);S.t(n+1)
%     if plot_gradient;subplot(211);    end
    loglog(S.k, 2*m(S.EMp),'-',S.k, (beta*(1+beta))*m(S.dens),'-', S.k, m(S.Bcc1)*(1+1/beta),'-','Markersize',2)
    hold on
    k53 = S.k;k28 = S.k(S.k>1); k23 = S.k(S.k>1/rhoi); k4 = S.k(S.k>1); 
     k28mult = 0.4e-4;k53mult = 1.5e-3;k23mult = 8e-6;k4mult = 1e-4;
    loglog(k53,k53mult.*(k53/k53(1)).^(-5/3),'k:',k28,k28mult*(k28/k28(1)).^(-2.8),'k:',k23,k23mult*(k23/k23(1)).^(-2/3),'k:',...
        k4,k4mult*(k4/k4(1)).^(-4),'k:',1/rhoi*[1 1],[1e-30,1e10],'k:')
    ylabel('$E_K$','interpreter','latex')
    xlabel('$k_\perp$','interpreter','latex')
    legend({'$E_{B_\perp}$','$E_{\tilde{n}}$','$E_{B_x}(1+1/\beta)$','$k^{-5/3}$','$k^{-2.8}$','$k^{-2/3}$','$k\rho_i=1$'},'interpreter','latex')
    ylim([1e-8 0.01])
    xlim([min(S.k) max(S.k)])
    title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])%title({name})
%     title(['t=' num2str(S.t(n+1))]);ginput(1);end
    
end



if plotSig
    figure
    for n=floor(S.n/2):S.n-1; m = @(d) d(:,n+1);mm = @(d) d(n+1);S.t(n+1)
    semilogx(S.k*rhoi,m(imag(S.sig))./m(S.EMp))
    title(['t=' num2str(S.t(n+1))]);ginput(1);end
end

% oldpath = path;
% path(oldpath,'~/Research/export-fig')
% set(gcf,'color','w')
% export_fig(['saved-states/spectrum-' folder '.pdf']) 

%disp('hello3')

end


function out = spect1D(v1,bins,ngrid,NT2)
% Fast version of 1D spectrum 
out = (full(sparse(ones(size(bins,1),1),bins,abs(double(v1(:))).^2,1,ngrid))/NT2).';
out = out(2:end-1); % Include extra bins at the ends for the ones that are missed out
end


function out = spect1Dslow(v1,v2,K,kgrid)
% Function to find the spectrum <v1 v2>, 
% K is the kgrid associated with v1 and v2
% kgrid is the grid for spectral shell binning

nk = length(kgrid)-1;
out = zeros(nk,1);
NT2 = numel(K)^2;
for kk = 1:nk
    out(kk) = sum( real(v1(K<kgrid(kk+1) & K>kgrid(kk)).*conj(v2(K<kgrid(kk+1) & K>kgrid(kk)))) )/NT2;
end

end

function out = spectHel(v1,v2,bins,ngrid,NT2)
% Function to find the cross spectrum <v1 v2>, 
% K is the kgrid associated with v1 and v2
% kgrid is the grid for spectral shell binning. 
% kyg0 includes only imag(ky)>0 values because on symmetry

out = (full(sparse(ones(size(bins,1),1),bins,double(v1(:).*conj(v2(:))),1,ngrid))/NT2).';
out = out(2:end-1); % Include extra bins at the ends for the ones that are missed out

end

function [out, outk] = grad(f,k, smooth)
smin = smooth(1);smax = smooth(2);
%disp(smin);
%disp(smax);
nk = length(k);
lkmax = log(k(end-smax));lkmin=log(k(smin+1));
nn=1;
sfun = @(lk) floor( smin + ((smax-smin)*((lk-lkmin)/(lkmax-lkmin)).^2) );
for kkk=smin+1:nk-smax
    s = sfun(log(k(kkk)));
    %disp(sfun(log(k(kkk))));
    %disp(kkk);
    %disp(s);
    d = max([kkk-s,1]);
    p = polyfit(log(k(kkk-s:kkk+s)),log(f(kkk-s:kkk+s)),1);
    %p = polyfit(log(k(d:kkk+s)),log(f(d:kkk+s)),1);
    outk(nn) = k(kkk);
    out(nn) =p(1);
    nn=nn+1;
end

end


function S=fixNormalization(S)
% Stuffed up overall factor on nnorm. Want int(dk EK)=u^2
nnorm_old = S.nnorm;
nnorm = S.nbin./S.k;
a = 1/sum(nnorm)*trapz(S.k,ones(size(S.k)));
S.nnorm = a*nnorm;
fields = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','thetaP','thetaM','ZP','ZM','Phi','vel1','vel2','vel3','dens'}; 
for var = [fields]
    if isfield(S,var{1})
        S.(var{1}) = S.(var{1}).*nnorm_old./S.nnorm;
    end
end

end

function inds = restart_overlaps(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1722 1818] 2433;
inds = [];
startinds = cat(1,[1],rinds);
for inn = 1:length(rinds) %for each restart index
    tb = t(rinds(inn)); %find the time of the restart
    ia = find(t(startinds(inn):rinds(inn))>tb,1);%find the first index before the restart index that has time greater than that just before the restart
    disp(ia+startinds(inn))
    inds = [inds ia+startinds(inn)-1:rinds(inn)-1]; %append all indices from before restart up until restart
end
inds = setdiff(1:length(t),inds);%returns all indices except those in inds
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