function spectrum_2d
% 2D spectrum of B and E

i_b3 = 0;
b_b3 = 0;
i_b0625 = 0;
b_b0625 = 1;

DoFullCalculation =1;
reloadSpectrumFile =0;
copyViaScp = 0;

P.numKgrid =  [500 600]; % Perp parallel grid. [500 600] default
P.derefine_prl =2; P.derefine_prp=1;

species = 1;
kprho=1; %normalize k_perp to rho instead of di
plotBvkprl=0;
plotBfromkprlkprp = 0; %plot routine from spectrum_kprlkprp with contours
plotDouble = 0;
plotB=0;
plotBcontour = 1;%1;
plotBnicely = 0;
plotE=0;
plotH = 1;
plotangle = 0;
plotdens = 0;
plotKprl = 0;

if i_b3
    name = 'half_tcorr_sim9';
    nums = [0:153];%[0:108];%[343:364]; % snapshot numbers for which to find spectrum
    mass = [1 16 4];
    qom = [1 5/16 1/2];
end
if b_b3
    name = 'b_b3_sim1';
    nums =  [0:76];
    mass = [1 16 4 16 12 12 56];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/56];
end
if i_b0625
    name = 'hb_beta0625';
    nums = [0:82];
end
if b_b0625
    name = 'b_b0625_sim1';
    nums=[0:38];
end
p_id = 'minor_turb';
if i_b0625
    computer = 'tigressevan';
    fname = ['../../eyerger/' name '/output/' p_id ]; % Folder with outputs']; % Folder with outputs
else
    computer = 'tigress';
    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end
if i_b3 || b_b3
    rhoi = sqrt(0.3);
    tauA = 6*48.1802;
end
if i_b0625 ||  b_b0625
    rhoi = sqrt(0.0625);
    tauA = 6*22.0;
    mass = [1 16 4 16 12 12 24];
    qom = [1 5/16 1/2 6/16 6/12 5/12 9/24];
end

addpath('~/matlab-libs/BrewerMap')
num1 = nums(1);
% rhoi for species at current temperatures:
% r=vth_perp,i/Omega_i=vth_perp,i_curr*vth_perp,io/Omega_p Omega_p/Omega_i
% = vth_perp,i_curr * vth_perp_io/vth_perp_po vth_perp_po/Omega_p
% Omega_p/Omega_i = vth_perp,i_curr * sqrt(mp/mi) * rhop * (mi/mp qp/qi)
% r_i = vth_perp,i_curr * sqrt(mp/mi) * rhop * (qomp/qomi)
% = rhoi * vthpp{i}(nnn) sqrt(1./mass(i))./qom(i)

n2s = @(s) num2str(s);
[readF,files_all,folder,~,outputfolder] = chooseComputerAndFiles(name,computer);
savebase = ['saved-analysis/']; %outputfolder '../../'
savefolder = [ savebase 'spectrum2D-' name '.mat'];
if plotdens; savefolder = [ savebase 'spectrum2D-dens-' name '.mat'];end

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
if i_b3
    is = restart_overlaps2(t_hst);
else
    is = restart_overlaps3(t_hst);
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
for i = 1:length(mass)-1
    vthpp{i+1} = sqrt(dat(is,38+19+24*(i-1)))/sqrt(2);
    vthpl{i+1} = sqrt(dat(is,38+18+24*(i-1)));
    vthtot{i+1} = sqrt( dat(is,38+19+24*(i-1)) +  dat(is,38+18+24*(i-1)) );
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
qqq = files_all(num1)
qqq{1}
D = readF(files_all(num1));
D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
dx = D.x(2)-D.x(1);
dy = D.y(2)-D.y(1);
dz = D.z(2)-D.z(1);
Ls = [D.x(end)-D.x(1)+dx D.y(end)-D.y(1)+dy D.z(end)-D.z(1)+dz];
if i_b0625 || b_b0625
    Ls = Ls.*1.0000000000001;
end
Ns = [length(D.x) length(D.y) length(D.z)];

% Grid in k space, for each dimension, conforming to FT standard [0 1 2 3 ... -N/2 -N/2+1 ... -1]
for kk=1:3
    K{kk} = 2i*pi/Ls(kk)*[0:(Ns(kk)/2-1) -Ns(kk)/2 -Ns(kk)/2+1:-1].';
end
[k3.KX, k3.KY, k3.KZ] = ndgrid(K{1},K{2},K{3}); % 3D grid in K
size(k3.KX)
size(k3.KY)
size(k3.KZ)
Kperp = sqrt(abs(k3.KY).^2 + abs(k3.KZ).^2); % |K|
Kprl = (k3.KX);
size(Kperp)
size(Kprl)
% Kmag = sqrt(abs(k3.KX).^2 + abs(k3.KY).^2 + abs(k3.KZ).^2);
% clear k3; % Don't clear if you're doing the kH/B helicity calculation

% % Helical basis
% kpzero = Kperp==0;
% Kperpnm = Kperp;Kperpnm(kpzero==0)=1;
% ephi = {0,-k3.KZ./Kperpnm, k3.KY./Kperpnm};
% KmagKperp  = Kperpnm.*sqrt(abs(k3.KX).^2 + abs(k3.KY).^2 + abs(k3.KZ).^2); KmagKperp(1)=1;
% etheta = { - (k3.KZ.^2 + k3.KY.^2)./KmagKperp, k3.KX.*k3.KY./KmagKperp, k3.KX.*k3.KZ./KmagKperp};
% hplus = {(etheta{1} + 1i*ephi{1})./sqrt(2),(etheta{2} + 1i*ephi{2})./sqrt(2),(etheta{3} + 1i*ephi{3})./sqrt(2)};
% hminus = {(etheta{1} - 1i*ephi{1})./sqrt(2),(etheta{2} - 1i*ephi{2})./sqrt(2),(etheta{3} - 1i*ephi{3})./sqrt(2)};
% hplus{1}(kpzero)=0;hplus{2}(kpzero)=0;hplus{3}(kpzero)=0;
% hminus{1}(kpzero)=0;hminus{2}(kpzero)=0;hminus{3}(kpzero)=0;
% kxg0 = imag(k3.KX)>0;
% clear ephi KmagKperp etheta Kperpnm k3

% Bins for k
% kgrid = (0:2*pi/Ls(2):max(imag(K{2}))).'+1e-4; % Use ky for spectrum binning
% if P.numKgrid ~= 0
%     kgridL = logspace(log10(abs(K{2}(2))),log10(max(abs(K{2}))) ,P.numKgrid ).';
%     iswtch = find(diff(kgridL)<2*pi/Ls(2),1,'last');
%     lin2log = find(kgrid<kgridL(iswtch+1),1,'last'); % index at which you switch to log scale
%     kgrid = [kgrid(1:lin2log-1);  logspace(log10(kgrid(lin2log)),log10(max(abs(K{2}))), length(kgridL(iswtch+1:end)) ).' ];
% end
% Diferent version: logarithmic, but remove unused bins at small k
kpgrid = logspace(log10(abs(K{2}(2))-1e-8),log10(max(abs(K{2}))) ,P.numKgrid(1) ).';
klgrid = logspace(log10(abs(K{1}(2))-1e-8),log10(max(abs(K{1}))) ,P.numKgrid(2) ).';
kpfull = [-1 ; kpgrid; 1e100];
klfull = [-1 ; klgrid; 1e100];
Nkfull = [length(kpfull);length(klfull)]-1;
size(kpgrid)
[cnts,~,~, binp,binl] = histcounts2(Kperp(:),abs(Kprl(:)),kpfull,klfull);
binp = min(max(binp,1),Nkfull(1));
binl = min(max(binl,1),Nkfull(2));
cnts = cnts(2:end,2:end);
kpgrid(cnts(:,end)==0)=[];
klgrid(cnts(end,:)==0)=[];
size(kpgrid)
disp(['Using ' n2s(length(kpgrid)) ' points in perp and ' n2s(length(klgrid)) ' points in parallel'])


% To hold the spectrum
St.Nk = [length(kpgrid);length(klgrid)]-1;
St.kp = kpgrid(2:end);
St.kl = klgrid(2:end);

% Preload the bins and counts for each k
kpfull = [-1 ; kpgrid; 1e100];
klfull = [-1 ; klgrid; 1e100];
Nkfull = St.Nk+2;
[cnts,~,~, binp,binl] = histcounts2(Kperp(:),abs(Kprl(:)),kpfull,klfull);
binp = min(max(binp,1),Nkfull(1));
binl = min(max(binl,1),Nkfull(2));
NT2 = numel(Kperp)^2;
clear Kperp Kprl;

% Count the number of modes in each bin to normalize later -- this gives a
% smoother result, since we want the average energy in each bin.
oneG = ones(sqrt(NT2),1);
St.nbin =spect2D(oneG,binp,binl,Nkfull,NT2)*NT2;
clear oneG;

St.nnorm = St.nbin./St.kp;
St.nnorm = St.nnorm/St.nnorm(1); % Want normalization to be the same as for a linear k grid
m3 = @(a) mean(mean(mean(a)));

% Average over all the snapshots
fields = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','vel1','vel2','vel3','h1','ch1e','ch1v'};%'spl','smn'};
for var = fields;St.(var{1}) = [];end
St.t=[];St.nums=[];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
if reloadSpectrumFile
    load(savefolder,'St');
    St
end
for nnn=nums
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
    [readF,files_all,folder] = chooseComputerAndFiles(name,computer);
    try
        if copyViaScp && mod(nnn-2,5)~=0
            files_all = copyFromFrontera(name,computer,'grid',nnn);
        end
        D = readF(files_all(nnn));
        D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
    catch
        warning(['Did not find ' folder ' nnn=' num2str(nnn)])
        continue
    end
    St.t = [St.t D.t];

    for var = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','vel1','vel2','vel3'}
        ft = fftn(D.(var{1}));
        St.(var{1}) = cat(3,St.(var{1}), spect2D(ft,binp,binl,Nkfull,NT2)./St.nnorm);
    end

%     % Helical basis
%     Bhel = (fftn(D.Bcc1).*hplus{1} + fftn(D.Bcc2).*hplus{2} + fftn(D.Bcc3).*hplus{3}).*kxg0;
%     St.spl = cat(3,St.spl,spect2D(Bhel,binp,binl,Nkfull,NT2)./St.nnorm);
%     Bhel = (fftn(D.Bcc1).*hminus{1} + fftn(D.Bcc2).*hminus{2} + fftn(D.Bcc3).*hminus{3}).*kxg0;
%     St.smn = cat(3,St.smn,spect2D(Bhel,binp,binl,Nkfull,NT2)./St.nnorm);

    % Another attempt at helical
%     ftBx = fftn(D.Bcc1);
    ftBy = fftn(D.Bcc2);
    ftBz = fftn(D.Bcc3);
    ftEy = fftn(D.Ecc2);
    ftEz = fftn(D.Ecc3);
    ftVy = fftn(D.vel2);
    ftVz = fftn(D.vel3);
    clear D
    k3.KX(1,:,:)=1i;k3.KY(:,1,:)=1i;k3.KZ(:,:,1)=1i;
    St.h1 = cat(3,St.h1, spect2Dhel(1i*(ftBy.*conj(ftBz) - ftBz.*conj(ftBy))./imag(k3.KX),...
        binp,binl,Nkfull,NT2)./St.nnorm );
%     St.h2 = cat(3,St.h2, spect2Dhel(1i*(ftBz.*conj(ftBx) - ftBx.*conj(ftBz))./imag(k3.KY),...
%         binp,binl,Nkfull,NT2)./St.nnorm );
%     St.h3 = cat(3,St.h3, spect2Dhel(1i*(ftBx.*conj(ftBy) - ftBy.*conj(ftBx))./imag(k3.KZ),...
%         binp,binl,Nkfull,NT2)./St.nnorm );

    St.ch1e = cat(3,St.ch1e, spect2Dhel(real(ftBy.*conj(ftEz) - ftBz.*conj(ftEy)),...
        binp,binl,Nkfull,NT2)./St.nnorm );
    St.ch1v = cat(3,St.ch1v, spect2Dhel(real(ftBy.*conj(ftVy) + ftBz.*conj(ftVz)),...
            binp,binl,Nkfull,NT2)./St.nnorm );

    clear  ftBy ftBz ftEy ftEz ftVy ftVz


    St.nums = [St.nums nnn];
    St.n = length(St.t);

    save(savefolder,'St','P');
end
    save(savefolder,'St','P');
else
    load(savefolder,'St');
    disp(St)
end

% Stupidly cated along the wrong direction
% St=fixCat(St);

% St = resaveAsAverages(St);
% save(['saved-analysis/spectrum2D-' name '.mat'],'St','P');


St.t = St.t/tauA;
if isfield(St,'tmax');St.tmax = St.tmax/tauA;St.tmin = St.tmin/tauA;end
tstrt = find(St.t>0,1);

tav = [14 18];
itav = [find(St.t>=tav(1) & St.t<=tav(2))];
m = @(d) mean(d(:,:,itav(1):itav(2)),3);

mx = @(f) max(max(max(f)));
% basic theory



normplot = St.kp.^(-10/3).*exp(-St.kl.'./St.kp.^(2/3)*48.1802^(1/3));
normplot(normplot<1e-7)=1e-7;lims = [-7 0];
% earlier time
% nnrm = find(St.t>14,1);normplot = (St.Bcc2(:,:,nnrm) + St.Bcc3(:,:,nnrm))/2;
% normplot = normplot/mx(normplot);lims = [-3 3];
% no norm
normplot = 1;lims = [-10,0];
% % levs
% load(['saved-analysis/spectrum2d-meanlev.mat']);
% normplotB=meanlevBp; lims = 2*[-1,1];
% normplotE=meanlevEp; lims = 2*[-1 1];


nbfinds = [];
for i = 1:length(St.t)
  %numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
  nbfinds = [nbfinds find(t_hst-St.t(i)>0.5/tauA,1)];
end

St

if plotBvkprl
    %for min kprp
    Sl = St;
    tav = [6.0 9.0];
    %tav = [6.5 8.5];
    tav2 = [13.2 15.2];
    % Sl=St;
    %Sl.t=Sl.t/tauA;
    m = @(d) mean(d(:,:,find(Sl.t>=tav(1) & Sl.t<=tav(2))),3);
    m2 = @(d) mean(d(:,:,find(Sl.t>=tav2(1) & Sl.t<=tav2(2))),3);
    disp(['Averaging nums ' n2s(find(Sl.t>=tav(1) & Sl.t<=tav(2)))])
    disp(['Averaging nums ' n2s(find(Sl.t>=tav2(1) & Sl.t<=tav2(2)))])
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.4, 0.5]);
    Bprp = m(Sl.Bcc2 + Sl.Bcc3);Bprp = Bprp./normplot;
    plot(log10(Sl.kl),log10(Bprp(1)))
    colorbar;  % caxis(lims) colormap(brewermap([],'PuBuGn')) 
    hold on
    plot(log10(1)*[1 1], [-10 10],'k:')
    plot(log10(1/2)*[1 1], [-10 10],'b:')
    plot(log10(1/16)*[1 1], [-10 10],'o:')
    xlabel('$\log_{10} k_\|$','interpreter','latex')
    xlim(log10([min(Sl.kl) max(Sl.kl)]))

end


if plotBfromkprlkprp
Sl = St;
tav = [6.0 9.0];
%tav = [6.5 8.5];
tav2 = [13.2 15.2];
% Sl=St;
%Sl.t=Sl.t/tauA;
m = @(d) mean(d(:,:,find(Sl.t>=tav(1) & Sl.t<=tav(2))),3);
m2 = @(d) mean(d(:,:,find(Sl.t>=tav2(1) & Sl.t<=tav2(2))),3);
disp(['Averaging nums ' n2s(find(Sl.t>=tav(1) & Sl.t<=tav(2)))])
disp(['Averaging nums ' n2s(find(Sl.t>=tav2(1) & Sl.t<=tav2(2)))])
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.4, 0.5]);
    % for n=dn:dn+1:Sl.n-dn; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);Sl.t(n+1)
    Bprp = m(Sl.Bcc2 + Sl.Bcc3);Bprp = Bprp./normplot;
    Eprp = m(Sl.Ecc2 + Sl.Ecc3);Eprp = Eprp./normplot;
%     s=pcolor(log10(Sl.kp),log10(Sl.kl),log10(Bprp).');
%     s.EdgeColor='none';s.FaceColor='interp';
    contourf(log10(Sl.kp),log10(Sl.kl),log10(Bprp).',40,'Linecolor',0.5*[1 1 1])
    colorbar;  % caxis(lims) colormap(brewermap([],'PuBuGn')) 
    hold on
    plot(log10(Sl.kp),2/3*log10(Sl.kp/Sl.kp(1))+log10(Sl.kl(1)),'k:')
    plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(Sl.kp),zeros(size(Sl.kp)),'k:')
    xlabel('$\log_{10} k_\perp$','interpreter','latex')
    ylabel('$\log_{10} k_\|$','interpreter','latex')
    xlim(log10([min(Sl.kp) max(Sl.kp)]))
    ylim(log10([min(Sl.kl) max(Sl.kl)]))
    %  title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])
    % ginput(1);end
    %m(St.Bcc2 + St.Bcc3)
end






if kprho
    St.kp = St.kp .* rhoi
end




tstrt=0;
dn =10;
i=species;
if plotDouble

    dir = ['../simulations/' name '/saved-plots/spec2d/B'];



    figure('Color',[1 1 1]);
    nplt = [75 142];
    %set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.2, 0.6]);
    Bprp = {};
    s = {};
    counter = 1;
    for n=nplt;%dn:dn+1:St.n-dn;
        m = @(d) mean(d(:,:,n-dn+1:n+dn),3);St.t(n+1)
        m2 = @(d) mean(d(n-dn+1:n+dn),1);
      if (n<10)
        numlab = ['000',num2str(n)];
      elseif (n<100)
        numlab = ['00',num2str(n)];
      elseif (n<1000)
        numlab = ['0',num2str(n)];
      else
        numlab = num2str(n);
      end
      Bprp{counter} = m(St.Bcc2 + St.Bcc3);Bprp{counter} = Bprp{counter}./normplot;
      %s{counter}=pcolor(log10(St.kp),log10(St.kl),log10(Bprp{counter}).');
      counter = counter + 1

    end

      clf;
      foutlab = [dir,'fp.',numlab,'.png'];
      exportname = [dir,'fp.',numlab,'.pdf'];

    subplot(211)
%     [KPL,KLL]=ndgrid(kpl,kll);Bprp = interpn(St.kp,St.kl,m(St.Bcc2 + St.Bcc3),KPL,KLL,'spline',NaN);
%     s=pcolor(log10(kpl),log10(kll),log10(abs(Bprp)).');
    %Bprp = m(St.Bcc2 + St.Bcc3);Bprp = Bprp./normplot;
    s{1}=pcolor(log10(St.kp),log10(St.kl),log10(Bprp{1}).');
    s{1}.EdgeColor='none';s{1}.FaceColor='interp';
    colorbar; colormap(brewermap([],'YlGnBu'))%colormap jet;
    caxis(lims)
    hold on
    plot(log10(St.kp),2/3*log10(St.kp/St.kp(1))+log10(St.kl(1)),'k:','LineWidth',2)
    plot(log10(1)*[1 1], [-10 10],'k:',log10(St.kp),zeros(size(St.kp)),'k:','LineWidth',2)
    % proton k_par rho = 1
    xlabel('$\log_{10} (k_\perp \rho_{p})$','interpreter','latex')
    ylabel('$\log_{10} (k_\| d_{p})$','interpreter','latex')
    subplot(212)
    %Bprp = m(St.Bcc2 + St.Bcc3);Bprp = Bprp./normplot;
    s{2}=pcolor(log10(St.kp),log10(St.kl),log10(Bprp{2}).');
    s{2}.EdgeColor='none';s{2}.FaceColor='interp';
    colorbar; colormap(brewermap([],'YlGnBu'))%colormap jet;
    caxis(lims)
    hold on
    plot(log10(St.kp),2/3*log10(St.kp/St.kp(1))+log10(St.kl(1)),'k:','LineWidth',2)
    plot(log10(1)*[1 1], [-10 10],'k:',log10(St.kp),zeros(size(St.kp)),'k:','LineWidth',2)
    % proton k_par rho = 1
    xlabel('$\log_{10} (k_\perp \rho_{p})$','interpreter','latex')
    ylabel('$\log_{10} (k_\| d_{p})$','interpreter','latex')
    subplot(211);
    title(['$t/\tau_{A}=$' num2str(St.t(n+1))]);
    hold off
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      print(foutlab,'-dpng','-r0');
      %exportgraphics(fig,exportname,'ContentType','vector');
    %ginput(1);end
    kls = St.kl
    kps = St.kp
    save([ savebase 'PlotSpectrum2D-' name '.mat'],'Bprp','kls','kps', '-v7.3');
    
end






tstrt=0;
dn =5;
i=species;
if plotBcontour

    dir = ['../simulations/' name '/saved-plots/spec2d/B'];



    figure('Color',[1 1 1]);

    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    %set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');
    lmin = -14;%-10
    lmax = -2;
    ylab    = '$k_\| d_{\rm p0}$';
    xlab    = '$k_\perp\rho_{\rm p0}$';
    nplt = [147]
    %nplt = [17 47 89 131 147];
    %set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.2, 0.6]);
    for n=dn:dn+1:St.n-dn;%nplt
        m = @(d) mean(d(:,:,n-dn+1:n+dn),3);St.t(n+1)
        m2 = @(d) mean(d(n-dn+1:n+dn),1);
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
      exportname = [dir,'fp.',numlab,'.pdf'];
    Bprp = m(St.Bcc2 + St.Bcc3);Bprp = Bprp./normplot;
    bplot = log10(Bprp);
    %liminds = find(bplot<lmin); bplot(liminds) = lmin-1;
    levels  = lmin:(1/3):lmax;
    %contourf(log10(St.kp),log10(St.kl),log10(Bprp).',40,'Linecolor',0.5*[1 1 1])
    [C1,h1] = contourf(St.kp,St.kl,bplot',levels);
    set(h1,'LineColor',0.7*[1,1,1],'Linewidth',0.3);
    set(gca, 'XScale', 'log','YScale', 'log');
    axis xy; shading flat;
    hold on;
    plot([1 1],[min(St.kl) max(St.kl)],':k',[0.1 10],[1 1],':k');
    hold off;
    %axis([0.1 10 0.1 4.5]);
    decades_equal(gca);
    colormap(brewermap([],"YlGnBu"))
    ylabel(ylab);
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    xlabel(xlab);
    plotTickLatex2D('ylabeldx',-0.015,'xtickdy',-0.01,'xlabeldy',0.005); 

    
    cb = colorbar;
    title(cb,'$\mathcal{E}_B$','interpreter','latex');
    %set(cb,'Position',cbpos,'Ticklength',0.01);
    cb.Limits=[lmin,lmax]; cb.Ticks=lmin:1:lmax;
    %cb.TickLabels={'$10^{-10}$','','$10^{-8}$','','$10^{-6}$','','$10^{-4}$', ...
    %            '','$10^{-2}$'};
    cb.TickLabelInterpreter='latex';
    cb.FontSize=10; cb.LineWidth=1;
    title(['$t/\tau_{A}=$' num2str(St.t(n+1))]);

    %pause(1);end
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      %exportgraphics(fig,exportname,'ContentType','vector');
    ginput(1);end
    %end
end


if plotB

    dir = ['../simulations/' name '/saved-plots/spec2d/B'];

    figure('Color',[1 1 1]);

    nplt = [147]
    %nplt = [17 47 89 131 147];
    %set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.2, 0.6]);
    for n=dn:dn+1:St.n-dn;%nplt
        m = @(d) mean(d(:,:,n-dn+1:n+dn),3);St.t(n+1)
        m2 = @(d) mean(d(n-dn+1:n+dn),1);
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
      exportname = [dir,'fp.',numlab,'.pdf'];

    %subplot(211)
%     [KPL,KLL]=ndgrid(kpl,kll);Bprp = interpn(St.kp,St.kl,m(St.Bcc2 + St.Bcc3),KPL,KLL,'spline',NaN);
%     s=pcolor(log10(kpl),log10(kll),log10(abs(Bprp)).');
    Bprp = m(St.Bcc2 + St.Bcc3);Bprp = Bprp./normplot;
    s=pcolor(log10(St.kp),log10(St.kl),log10(Bprp).'); 
    s.EdgeColor='none';s.FaceColor='interp';
    colorbar; colormap(brewermap([],'YlGnBu'))%colormap jet;
    caxis(lims)


    hold on
    plot(log10(St.kp),2/3*log10(St.kp/St.kp(1))+log10(St.kl(1)),'k:','LineWidth',2)
    plot(log10(1)*[1 1], [-10 10],'k:',log10(St.kp),zeros(size(St.kp)),'k:','LineWidth',2)
    % cyclotron freqs
    plot(log10(St.kp),log10(ones(size(St.kp)).* qom(1) ), 'r--','Linewidth', 1.5   ) ;
    plot(log10(St.kp),log10(ones(size(St.kp)).* qom(2) ), '--','Color',[0.6350 0.0780 0.1840],'Linewidth', 1.5   ) ;
    plot(log10(St.kp),log10(ones(size(St.kp)).* qom(3) ), 'c--','Linewidth', 1.5   ) ;
    % proton k_par rho = 1
    %disp((rhoi * m2(vthpp{0}(nbfinds)) * sqrt(1./mass(0))./qom(0)))
    %plot(log10(St.kp),log10(ones(size(St.kp))./ (rhoi * m2(vthpp{1}(nbfinds)) * sqrt(1./mass(1))./qom(1)) ), 'r--','Linewidth', 1.5   ) ;
    %plot(log10(St.kp),log10(ones(size(St.kp))./ (rhoi * m2(vthpp{2}(nbfinds)) * sqrt(1./mass(2))./qom(2)) ), '--','Color',[0.6350 0.0780 0.1840],'Linewidth', 1.5   ) ;
    %plot(log10(St.kp),log10(ones(size(St.kp))./ (rhoi * m2(vthpp{3}(nbfinds)) * sqrt(1./mass(3))./qom(3)) ), 'c--','Linewidth', 1.5   ) ;
    plot(log10(1/ (m2(vthpp{1}(nbfinds)) * sqrt(1./mass(1))./qom(1)) ) *[1 1], [-10 10],'r--')
    plot(log10(1/ (m2(vthpp{2}(nbfinds)) * sqrt(1./mass(2))./qom(2)) ) *[1 1], [-10 10],'--','Color',[0.6350 0.0780 0.1840])
    plot(log10(1/ (m2(vthpp{3}(nbfinds)) * sqrt(1./mass(3))./qom(3)) ) *[1 1], [-10 10],'c--')
    xlabel('$\log_{10} (k_\perp \rho_{p})$','interpreter','latex')
    ylabel('$\log_{10} (k_\| d_{p})$','interpreter','latex')
    %subplot(212)
    %Eprp = interpn(St.kp,St.kl,m(St.Ecc2 + St.Ecc3),KPL,KLL,'spline',NaN); Eprp = Eprp./normplotE;
%         s=pcolor(log10(kpl),log10(kll),log10(abs(Eprp)).');
    %Eprp = m(St.Ecc2 + St.Ecc3);Eprp = Eprp./normplot;
    %s=pcolor(log10(St.kp),log10(St.kl),log10(Eprp).');
    %xlabel('$\log_{10}k_\perp$','interpreter','latex')
    %ylabel('$\log_{10}k_\|$','interpreter','latex')
    %s.EdgeColor='none';s.FaceColor='interp';
    %colorbar;  colormap jet;  caxis(lims)
    %subplot(211);
    title(['$t/\tau_{A}=$' num2str(St.t(n+1))]);
    %legend({'','','','','$k \rho_{H+}=1$','$k \rho_{O5+}=1$','$k \rho_{He++}=1$'},'interpreter','latex')
    hold off
    %pause(1);end
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0');
      %exportgraphics(fig,exportname,'ContentType','vector');
    ginput(1);end
    %end
end


if plotE
nnrm = find(St.t>8,1);normplot = (St.Ecc2(:,:,nnrm) + St.Ecc3(:,:,nnrm))/2;
normplot = 1;
normplot = normplot/mx(normplot);
    figure
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.35, 0.9]);
    for n=floor(0*St.n/2):St.n-1; m = @(d) d(:,:,n+1);St.t(n+1)
    subplot(211)
    Eprp = m(St.Ecc2 + St.Ecc3)/2;Eprp = Eprp/mx(Eprp)./normplot;
    s=pcolor(log10(St.kp),log10(St.kl),log10(Eprp).');
    s.EdgeColor='none';s.FaceColor='interp';
    colorbar
    hold on
    plot(log10(St.kp),2/3*log10(St.kp/St.kp(1))+log10(St.kl(1)*[1 10 100]),'k:')
    xlabel('$k_\perp$','interpreter','latex')
    ylabel('$k_\|$','interpreter','latex')
    subplot(212)
    El = m(St.Ecc1); El = El/mx(El)./normplot;
    s=pcolor(log10(St.kp),log10(St.kl),log10(El).');
    xlabel('$k_\perp$','interpreter','latex')
    ylabel('$k_\|$','interpreter','latex')
    s.EdgeColor='none';s.FaceColor='interp';
    colorbar
    subplot(211);title(['t=' num2str(St.t(n+1))]);ginput(1);end
end

if plotBnicely
    % plot B 2D spectrum like the one in nature paper averaged over trng
    %load([ savebase 'spectrum2D-' name '.mat']);
    St.kp = St.kp*rhoi;
    di=1/rhoi;rhoi=1;Lprp= 48.1802;
    kplim = [min(St.kp) max(St.kp)/3];
    kllim = [min(St.kl) max(St.kl)/5];
    fig = figure;
    cols = setAxesAndColors(fig,[10 12],'Set1');
    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);

    trng = [9 10];
    Bprp = m(St.Bcc2 + St.Bcc3,St.t,trng);
    disp(mean(mean(Bprp)))
    disp(trapz(St.kl,trapz(St.kp,Bprp,1),2))
    disp(energyAtt(St,trng*tauA))
    Bprp = Bprp./trapz(St.kl,trapz(St.kp,Bprp,1),2).*energyAtt(St,trng);%*tauA);


    % s=pcolor(log10(St.kp),log10(St.kl),log10(Bprp).');
    % s.EdgeColor='none';s.FaceColor='interp';
    contourf(log10(St.kp),log10(St.kl),log10(Bprp).',40,'Linecolor',0.5*[1 1 1],'Linewidth',0.3)
    c=colorbar; caxis([-6 1]); colormap('jet')%colormap(brewermap([],'YlGnBu'))
    c.TickLabelInterpreter='latex';
    hold on
    dB0 = 1/4;zp0=0*2*sqrt(energyAtt(St,trng*tauA));
    kpl = St.kp(St.kp<1.2);kph = St.kp(St.kp>1.2 & St.kp<8);
    plot(log10(kpl),log10(di*kpl.*zp0.*(Lprp/(2*pi)*kpl*di).^(-1/3)),':',...
        log10(kpl),log10(di*kpl.*dB0.*(Lprp/(2*pi)*kpl*di).^(-1/3)),':','Color',0.7*[1 1 1],'Linewidth',1)
    % plot(log10(kph),log10(1.3*(kph/kph(1)).^(1/3)),':','Color',0.2*[1 1 1],'Linewidth',1)
    plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(St.kp),zeros(size(St.kp)),'k:')
    xlabel('$ k_\perp \rho_i$','interpreter','latex')
    ylabel('$ k_z d_i$','interpreter','latex')
    xlim(log10(kplim))
    ylim(log10(kllim))
    pbaspect([log10(kplim(2)/kplim(1)) log10(kllim(2)/kllim(1)) 1])
     logticks()
end


if plotH

        dir = ['../simulations/' name '/saved-plots/spec2d/hel'];

    figure('Color',[1 1 1]);


    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    %set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    %set(gcf,'renderer','Painters');
    ylab    = '$k_\| d_{\rm p0}$';
    xlab    = '$k_\perp\rho_{\rm p0}$';


    %set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.35, 0.9]);
    %nplt = [17 47 55 65 75 89 131 147];
    nplt = [142];
    for n=nplt;%dn:dn+1:St.n-dn;nplt
        m = @(d) mean(d(:,:,n-dn+1:n+dn),3);St.t(n+1)
        m2 = @(d) mean(d(n-dn+1:n+dn),1);
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
      exportname = [dir,'fp.',numlab,'.pdf'];
    B2 =  m(St.Bcc1 + St.Bcc2 + St.Bcc3);
    %subplot(211)
    
    %hold on
    s=pcolor(St.kp,St.kl,(-m(St.h1)./B2.*sqrt(St.kp.^2 + (St.kl.').^2)).');
    s.EdgeColor='none';s.FaceColor='interp';
    %[C1,h1] = contourf(St.kp,St.kl,(-m(St.h1)./B2.*sqrt(St.kp.^2 + (St.kl.').^2)).');
    %set(h1,'LineColor',0.7*[1,1,1],'Linewidth',0.3);
    max(max(m(St.h1)./B2.*sqrt(St.kp.^2 + (St.kl.').^2)).')
    colorbar; caxis([-1 1]); colormap(brewermap([],'RdBu'))%'Spectral'))RdBu
    hold on
    plot([1 1], [min(St.kl) max(St.kl)],'k:',St.kp,ones(size(St.kp)),'k:','Linewidth',2)
    %plot(log10(St.kp),log10(ones(size(St.kp))./ (rhoi * m2(vthpp{1}(nbfinds)) * sqrt(1./mass(1))./qom(1)) ), 'r--','Linewidth', 1.5   ) ;
    %plot(log10(St.kp),log10(ones(size(St.kp))./ (rhoi * m2(vthpp{2}(nbfinds)) * sqrt(1./mass(2))./qom(2)) ), '--','Color',[0.6350 0.0780 0.1840],'Linewidth', 1.5   ) ;
    %plot(log10(St.kp),log10(ones(size(St.kp))./ (rhoi * m2(vthpp{3}(nbfinds)) * sqrt(1./mass(3))./qom(3)) ), 'c--','Linewidth', 1.5   ) ;
    %plot(log10(1/ (rhoi * m2(vthpp{1}(nbfinds)) * sqrt(1./mass(1))./qom(1)) ) *[1 1], [-10 10],'r--')
    %plot(log10(1/ (rhoi * m2(vthpp{2}(nbfinds)) * sqrt(1./mass(2))./qom(2)) ) *[1 1], [-10 10],'--','Color',[0.6350 0.0780 0.1840])
    %plot(log10(1/ (rhoi * m2(vthpp{3}(nbfinds)) * sqrt(1./mass(3))./qom(3)) ) *[1 1], [-10 10],'c--')
    hold off
    set(gca, 'XScale', 'log','YScale', 'log');
    axis xy;
    xlabel(xlab)
    ylabel(ylab)
    %decades_equal(gca);
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    %plotTickLatex2D('ylabeldx',-0.015,'xtickdy',-0.01,'xlabeldy',0.005); 
    cmp = colormap;
    cmp = flipud(cmp);
    colormap(cmp);
%     title(['$t=' n2s(St.tmin(n+1)) '$ to $t=' n2s(St.tmax(n+1)) '$'])
    if plotangle
    subplot(212)
    % Plot vs. angle instead
    mkp = min(St.kp); mkl = min(St.kl);
    thetag = 0:90; lkg= linspace(log10(min(St.kp)),log10(max(St.kp)),100);
    [lk,theta] = ndgrid(lkg,thetag);
    kpi = 10.^lk.*sind(theta)+0*mkp; kli = 10.^lk.*cosd(theta)+0*mkl;
    heltheta = interpn(St.kp,St.kl,m(St.h1)./B2.*sqrt(St.kp.^2 + (St.kl.').^2),...
        kpi,kli,'spline',NaN);
    s=pcolor(fliplr(thetag)+90,lkg,heltheta);
    s.EdgeColor='none';s.FaceColor='interp';
    colorbar; caxis([-1 1]); colormap(brewermap([],'Spectral'))
    xlabel('$\theta_k$','interpreter','latex')
    ylabel('$\log_{10} k$','interpreter','latex')
    title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])
    hold on
    plot(thetag+90,log10(1/rhoi)*ones(size(thetag)),'k:')
    plot(thetag+90,zeros(size(thetag)),'k:')
%     nm =  sqrt(m(St.Bcc1 + St.Bcc2 + St.Bcc3)).*sqrt(m(St.Ecc1 + St.Ecc2 + St.Ecc3));
% %     nm =  sqrt(m(St.Bcc1 + St.Bcc2 + St.Bcc3)).*sqrt(m(St.vel2 + St.vel2 + St.vel3));
%     s=pcolor(log10(St.kp),log10(St.kl),(m(St.ch1e)./nm).');
%     s.EdgeColor='none';s.FaceColor='interp';
%     colorbar; caxis([-1 1])
%     hold on
%     plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(St.kp),zeros(size(St.kp)),'k:')
%     hold off
%     xlabel('$\log_{10} k_\perp$','interpreter','latex')
%     ylabel('$\log_{10} k_\|$','interpreter','latex')
%     title(['$t=' n2s(St.tmin(n+1)) '$ to $t=' n2s(St.tmax(n+1)) '$'])
    hold off
    subplot(211);

    
    end

title(['$t/\tau_{A}=$' num2str(St.t(n+1))]);
      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';
      %print(foutlab,'-dpng','-r0')%ginput(1);end
      %exportgraphics(fig,exportname,'ContentType','vector');end
   end
end

if plotKprl
    % Kprl spectrum over low kperp modes. Or spectrum of negative helicity
    % modes
    figure
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.35, 0.4]);
    norml = sum(St.nbin,1);norml=norml/norml(1); % 1D, so don't divide by k or k^2
    for n=dn:dn+1:St.n-dn; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);St.t(n+1)
%         B2 =  m(St.Bcc1 + St.Bcc2 + St.Bcc3);
%         filt = (-m(St.h1)./B2.*sqrt(St.kp.^2 + (St.kl.').^2)) > 0.5;
        [KP,~]=ndgrid(St.kp,St.kl);
        filt = KP < 10^-0.5;
        EBprl = sum(filt.*(m(St.vel2 + St.vel3))/2.*St.nnorm,1)./norml;
        loglog(St.kl,EBprl,St.kl,1e-8*St.kl.^-2,'k:','Color',tcol(St.t(n+1)))
        hold on
    title(['t=' num2str(St.t(n+1))]);ginput(1);end

end

lims = [-8 -5];
if plotdens
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.5, 0.6]);
    for n=0:St.n-1; m = @(d) d(:,:,n+1);St.t(n+1)
    Bprp = m(St.Bcc2 + St.Bcc3);Bprp = Bprp./normplot;
    dens = m(St.dens);dens = dens./normplot;
    s=pcolor(log10(St.kp),log10(St.kl),log10(Bprp).');
    s.EdgeColor='none';s.FaceColor='interp';
    colorbar; colormap jet;   caxis(lims)
    hold on
    plot(log10(St.kp),2/3*log10(St.kp/St.kp(1))+log10(St.kl(1)),'k:')
    plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(St.kp),zeros(size(St.kp)),'k:')
    xlabel('$\log_{10} k_\perp$','interpreter','latex')
    ylabel('$\log_{10} k_\|$','interpreter','latex')
%      title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])
    title(['t=' num2str(St.t(n+1))]);ginput(1);end
end

end


function out = spect2D(v1,binp,binl,Nkfull,NT2)
% Fast version of 2D spectrum
out = full(sparse(binp,binl,abs(double(v1(:))).^2,Nkfull(1),Nkfull(2)))/NT2;
out = out(2:end-1,2:end-1); % Include extra bins at the ends for the ones that are missed out
end

function out = spect2Dhel(v1v2,binp,binl,Nkfull,NT2)
% Fast version of 2D spectrum
out = full(sparse(binp,binl,real(double(v1v2(:))),Nkfull(1),Nkfull(2)))/NT2;
out = out(2:end-1,2:end-1); % Include extra bins at the ends for the ones that are missed out
end

function St=fixCat(St)
% Turn into a
fields = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3'};
for var = fields
    St.(var{1}) = reshape(St.(var{1}),[314,length(St.kl),length(St.t)]);
end
St.n = length(St.t);
end

function S = resaveAsAverages(St)
% Resave full 1:162 data with averages over. Dt is 0.1*tauA
midi = [5:5:163]+1;
imin = midi-5;
imax = midi+5;imax(imax>163)=163;
S.t = St.t(midi);
S.tmin = St.t(imin);
S.tmax = St.t(imax);
S.nums = midi;
fields = {'Ecc1','Ecc2','Ecc3','Bcc1','Bcc2','Bcc3','vel1','vel2','vel3','h1','ch1e','ch1v'};
for iii=1:length(midi)
    for fff=1:length(fields)
        S.(fields{fff})(:,:,iii) = mean(St.(fields{fff})(:,:,imin(iii):imax(iii)),3);
    end
end
S.Nk=St.Nk;S.kp=St.kp;S.kl=St.kl;S.nnorm=St.nnorm;S.nbin=St.nbin;
S.n=length(midi);
S
end



function EB = energyAtt(S,tav)
% What the magnetic energy should be in time trng
m = @(d) mean(d(:,:,find(S.t>=tav(1),1):find(S.t<=tav(2),1,'last')),3);
EB = sum(m(S.Bcc2 + S.Bcc3).*S.nnorm);
disp(size(S.Bcc2))
disp(size(S.Bcc3))
disp(size(S.Bcc2+S.Bcc3))
disp(sum(isnan(mean((S.Bcc2 + S.Bcc3),3)),'all'))
disp(find(S.t>=tav(1),1))
disp(find(S.t<=tav(2),1,'last'))
disp(tav(1))
disp(tav(2))
disp(S.t)

end

function logticks()
yticks([log10(0.02:0.01:0.1) log10(0.2:0.1:1) log10(2:1:10)]);
yticklabels({'','','','','','','','','$10^{-1}$',...
            '','','','','','','','','$10^0$'...
            '','','','','','','','','$10^1$'});
xticks([log10(0.02:0.01:0.1) log10(0.2:0.1:1) log10(2:1:10)]);
xticklabels({'','','','','','','','','$10^{-1}$',...
            '','','','','','','','','$10^0$'...
            '','','','','','','','','$10^1$'});
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

function decades_equal(hAxes,xLimits,yLimits)

  if (nargin < 2) || isempty(xLimits)
    xLimits = get(hAxes,'XLim');
  end
  if (nargin < 3) || isempty(yLimits)
    yLimits = get(hAxes,'YLim');
  end

  logScale = diff(yLimits)/diff(xLimits);
  powerScale = diff(log10(yLimits))/diff(log10(xLimits));

  set(hAxes,'Xlim',xLimits,...
            'YLim',yLimits,...
            'DataAspectRatio',[1 logScale/powerScale 1]);

end