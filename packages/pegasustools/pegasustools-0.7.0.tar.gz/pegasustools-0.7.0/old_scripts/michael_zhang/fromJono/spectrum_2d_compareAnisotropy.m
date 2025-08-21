function spectrum_2d_compareAnisotropy()

% Script to compare 2d spectra of mine and Lev's, including the dispersion
% relation of IC waves

rhoi = sqrt(0.3);
clevs = [2e-5 2e-6 2e-7 2e-8];
stys = {'-','-','--',':'};
lw = [2 1  0.4 0.2];


% Find mean of Lev's
savefolder = [ 'saved-analysis/spectrum2D-lev.mat'];
tauA = 206.4865395;
load(savefolder,'St');
tav = [5 22];
St.t = St.t/tauA;
itav = [find(St.t>=tav(1),1);find(St.t<=tav(2),1,'last')];
m = @(d) mean(d(:,:,itav(1):itav(2)),3);
meanlevBp = m(St.Bcc2 + St.Bcc3)/2;
meanlevEp = m(St.Ecc2 + St.Ecc3)/2;
lkp = St.kp;lkl = St.kl;

savefolder = [ 'saved-analysis/spectrum2D-imbal2-prod.mat'];
load(savefolder,'St');
tauA = 6*67.4523;
St.t = St.t/tauA;


% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %  PLOT SHOWING VARIATION IN TIME – HARD TO SEE 
% figure('Color',[1 1 1]);
% set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.4, 0.5]);
% for cc=1:length(clevs)
%     contour(log10(lkp),log10(lkl),meanlevBp.',[clevs(cc) clevs(cc)],'LineStyle',stys{cc},'Color','k','Linewidth',lw(cc))
%     hold on
% end
% % contourf(log10(lkp),log10(lkl),log10(meanlevBp).',(-9:0.2:-4),'LineColor','none')
% % colormap(flipud(gray))
% % hold on
% 
% times = [4:3:13 16.2];
% for ttt = 1:length(times)-1
%     itav = [find(St.t>=times(ttt),1);find(St.t<=times(ttt+1),1,'last')];
%     m = @(d) mean(d(:,:,itav(1):itav(2)),3);
%     Bprp = m(St.Bcc2 + St.Bcc3)/2;
%     for cc=1:length(clevs)
%         contour(log10(St.kp),log10(St.kl),Bprp.',[clevs(cc) clevs(cc)],...
%             'LineStyle',stys{cc},'Color',tcol((times(ttt)+times(ttt+1))/2),'Linewidth',lw(cc))
%         hold on
%     end
% end
% 
% plot(log10(St.kp),2/3*log10(St.kp/St.kp(1))+log10(St.kl(1)),'k:')
% plot(log10(1/rhoi)*[1 1], [log10(min(St.kl)) log10(max(St.kl))],'k:',log10(St.kp),zeros(size(St.kp)),'k:')
% 
% xlabel('$\log_{10} k_\perp d_i$','interpreter','latex')
% ylabel('$\log_{10} k_z d_i$','interpreter','latex')
% xlim(log10([min(St.kp) 10]))
% ylim(log10([min(St.kl),1]))
% 
% load saved-analysis/IC_DR_2D_beta0.3.mat
% % fig=figure;
% figure(1)
% M = contour(log10(D.kp),log10(D.kl/rhoi),log10(D.omega./(D.kp.').^0.667).',log10([0.1:0.1:5]));
% % close(fig)
% geq1 = findContourGradients(M);
% hold on
% 
% % contour(log10(D.kp),log10(D.kl/rhoi),((D.omega+10*D.gamma)./D.omega).',[0 0],'k--')
% 
% plot(geq1(1,:),geq1(2,:),'k-','Linewidth',2)
% plot(log10(1)*[1 1], [log10(min(St.kl)) log10(max(St.kl))],'k:',log10(St.kp),zeros(size(St.kp)),'k:')
% 
% xlim(log10([min(St.kp) 10]))
% ylim(log10([min(St.kl),1]))
% 
% xlabel('$\log_{10} k_\perp \rho_i$','interpreter','latex')
% ylabel('$\log_{10} k_z d_i$','interpreter','latex')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PLOT FOR BEN SHOWING CURVES ON SATURATED SPECTRUM
rhoi = sqrt(0.3);

tauA = 6*67.4523;
Lprp= 67.4523;

tmid = [3.9;6.1];
tsat = [14;18.2];

m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
m2 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
fold = '~/Research/pegasus/imbalanced-turbulence/matlab/saved-analysis/';

load([fold 'spectrum-kprlkprp-' 'imbal2-prod' '.mat'],'Sl'); %Change to kprl kprp spectrum instead
load([fold 'spectrum-' 'imbal2-prod' '.mat'],'S');
% Sl = St;
Sl.t = Sl.t/tauA;

% debug here to compute ICW proportion (see below)
Sl.kp = Sl.kp*rhoi;
di=1/rhoi;rhoi=1;

kplim = [min(Sl.kp) max(Sl.kp)];
kllim = [min(Sl.kl) max(Sl.kl)];

fig = figure;
addpath('/Users/jsquire/Dropbox (Otago University)/Research/pegasus/imbalanced-turbulence/ICandHelicityBarrier-Pegasus/Figures')
[cols, tcol] = setAxesAndColors(fig,[0.12 0.20],'Set1');
Bprp = m(Sl.Bcc2 + Sl.Bcc3,Sl.t,tsat);
Bprp = Bprp./trapz(Sl.kl,trapz(Sl.kp,Bprp,1),2).*energyAtt(S,tsat*tauA);
% s=pcolor(log10(Sl.kp),log10(Sl.kl),log10(Bprp).');
% s.EdgeColor='none';s.FaceColor='interp';
contourf(log10(Sl.kp),log10(Sl.kl),log10(Bprp).',40,'Linecolor',0.5*[1 1 1],'Linewidth',0.3)
c=colorbar; caxis([-8 1]); colormap(brewermap([],'YlGnBu'))
c.TickLabelInterpreter='latex';
hold on
dB0 =4*1/6;zp0=2*2*sqrt(energyAtt(S,tsat*tauA));
kpl = Sl.kp(Sl.kp<1.2);kph = Sl.kp(Sl.kp>1.2 & Sl.kp<8);
% plot(log10(kpl),log10(di*kpl.*zp0.*(Lprp/(2*pi)*kpl*di).^(-1/3)),':',...
%     log10(kpl),log10(di*kpl.*dB0.*(Lprp/(2*pi)*kpl*di).^(-1/3)),':','Color',0.7*[1 1 1],'Linewidth',2)
% plot(log10(kph),log10(1.3*(kph/kph(1)).^(1/3)),':','Color',0.2*[1 1 1],'Linewidth',1)
plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(Sl.kp),zeros(size(Sl.kp)),'k:')

load saved-analysis/IC_DR_2D_beta0.3.mat
rhoi=1/di;di =1;
kp = D.kp;kl = D.kl/rhoi;
inkp = kp<1.1;inkl = kl<1.1;
contour(log10(kp(inkp)),log10(kl(inkl)),log10((Lprp/(2*pi))^(1/3)*D.omega(inkp,inkl)./(kp(inkp).').^0.667/zp0).',log10([0.7 1.3]),'Color','w','Linewidth',2,'Linestyle',':');
% M = contour(log10(D.kp),log10(D.kl/rhoi),log10(D.omega./(D.kp.').^0.667).',log10([0.1:0.1:5]));

xlabel('$ k_\perp \rho_i$','interpreter','latex')
ylabel('$ k_\| d_i$','interpreter','latex')
xlim(log10(kplim))
ylim(log10(kllim))
pbaspect([log10(kplim(2)/kplim(1)) log10(kllim(2)/kllim(1)) 1])
ax = gca;
 logticks(ax) 


end


function geq1 = findContourGradients(M)
% Find contours and then their gradients to see where it's steeper than 1

kkk = 1;
zcf = @(v) find(diff(sign(v))); % Find zero crossings
gradcross = 1; 
kperpcut = 0;

geq1=[];
while size(M,2)>kkk
    cont = M(:,(kkk+1):(kkk+M(2,kkk)));
    dcont = diff(cont,1,2);
    dcont = dcont(2,:)./dcont(1,:); % Contour gradient
    igeq1 = zcf(dcont-gradcross); % Indices where gradient crosses zero
    igeq1 = igeq1(abs(dcont(igeq1)-1)<1); % Remove vertical parts
    coords = 0.5*(cont(:,igeq1)+cont(:,igeq1+1));
    coords = coords(:,coords(1,:)<kperpcut);
    geq1 = [geq1 coords];
     
    kkk = 1+kkk+M(2,kkk);
end

% Sort to ascending kperp
[~,ord]=sort(geq1(1,:));
geq1 = geq1(:,ord);

end


function logticks(ax)
yticks([log10(0.02:0.01:0.1) log10(0.2:0.1:1) log10(2:1:10)]);
yticklabels({'','','','','','','','','$10^{-1}$',...
            '','','','','','','','','$10^0$'...
            '','','','','','','','','$10^1$'});
xticks([log10(0.02:0.01:0.1) log10(0.2:0.1:1) log10(2:1:10)]);
xticklabels({'','','','','','','','','$10^{-1}$',...
            '','','','','','','','','$10^0$'...
            '','','','','','','','','$10^1$'});
ax.TickLabelInterpreter = 'latex';
ax.XTickLabelRotation = 0;

end

function EB = energyAtt(S,tav)
% What the magnetic energy should be in time trng
m = @(d) mean(d(:,find(S.t>=tav(1),1):find(S.t<=tav(2),1,'last')),2);
EB = sum(m(S.Bcc2 + S.Bcc3).*S.nnorm);

end
