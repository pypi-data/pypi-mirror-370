function plot_hst_inject_bal%( fname )

%name = 'b_b3_sim1';%'first_attempt';%'test-force';'sig-decr-prod';
name = 'b_b0625_sim1';
b_b3 = 0;
b_b0625 = 1;
%name = 'first_attempt';
%name = '21node';
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

% nums = input(['Choose variables:  ' char(10) strjoin(names,char(10)) char(10)]);

figure
t = dat(:,1);
is = restart_overlaps3(t);%restart_overlaps2(t);
%is144 = t144_restart_overlaps(t);

dt = dat(:,2);
dthst = diff(t);dthst = [ dthst(1);dthst ];
if b_b3
    vol=  6*48.1802^3; %4*500^3;6*67.4523^3;
    tauA = 6*48.1802;  %4*500;6*67.4523;
end
if b_b0625
    vol = 6*22.0^3;
    tauA=6*22.0
end
%vol=  6*24.09^3; %4*500^3;6*67.4523^3;
%tauA = 6*24.09;  %4*500;6*67.4523;

epsind = 34;
diss_hypr = dat(:,epsind-1)./dthst*vol;
dedt = (dat(:,epsind))./dthst*vol;
deudt = (dat(:,epsind))./dthst*vol;
cross_hel = sum(dat(:,16:18),2); %*96^2*560*100;   %vol(i)*u_mx*bcc1 * 1./std::sqrt(u_d);
zp2 = 0.5*(sum(dat(:,7:9),2) + sum(dat(:,10:12),2) + cross_hel);  % u^2 + b^2 + cross_hel
zm2 = 0.5*(sum(dat(:,7:9),2) + sum(dat(:,10:12),2) - cross_hel);

on = ones(size(t));
ep = mean(dedt(t<1000));
sige=0.9;

windowSize = ceil(tauA);
filt = @(f) filter((1/windowSize)*ones(1,windowSize),1,f(is));
%filt144 = @(f) filter((1/windowSize)*ones(1,windowSize),1,f(is144));

t=t/tauA;


mean(dedt(is))

hold on
% figure
subplot(211)
%plot(t(is144),filt144(dehdt),'--',t(is144),filt144(dedt),'--',t(is),filt(dehdt),t(is),filt(dedt))
plot(t(is),dedt(is))
% xlim([0 1]); ylim([0 0.06])
xlabel('$t$','interpreter','latex')
ylabel('Energy injection','interpreter','latex')
%legend({'$\varepsilon_H (tcorr=144)$','$\varepsilon (tcorr=144)$','$\varepsilon_H (tcorr=72)$','$\varepsilon (tcorr=72)$',...
%    'Expected $\varepsilon_H$','Expected small-scale dissipation'},...
%    'interpreter','latex')
legend({'$\varepsilon$'},...
    'interpreter','latex')
% ylim(2*[-10 40])


%hold on
% figure
%subplot(211)
%plot(t(is),filt(dehdt),t(is),filt(dedt),'k',t(is),filt(deudt),'--',t(is),filt(debdt),'--',t(is),filt(diss_hypr),':k','Linewidth',1)
% xlim([0 1]); ylim([0 0.06])
%xlabel('$t$','interpreter','latex')
%ylabel('Energy injection','interpreter','latex')
%hold on
%sige = @(t) 0.9*(1-2/3*0.1*max(0,t - 18.2)/0.9);
%plot(t,ep.*sige(t),':',t,(1-sige(t)).*ep,':')
%legend({'$\varepsilon_H$','$\varepsilon$','$\varepsilon_u$','$\varepsilon_B$','$\varepsilon^{rm diss}_{\eta4}$',...
%    'Expected $\varepsilon_H$','Expected small-scale dissipation'},...
%    'interpreter','latex')
% ylim(2*[-10 40])

subplot(212)
% Energy budget
dtKE = diff(sum(dat(:,7:9),2)); dtKE = [dtKE(1); dtKE]./dthst*vol;
dtME = diff(sum(dat(:,10:12),2)); dtME = [dtME(1); dtME]./dthst*vol;
dtzp2 = diff(zp2); dtzp2 = [dtzp2(1); dtzp2]./dthst*vol;
dtzm2 = diff(zm2); dtzm2 = [dtzm2(1); dtzm2]./dthst*vol;
dtEprp =0.5* diff(dat(:,28)); dtEprp = [dtEprp(1); dtEprp]./dthst*vol;
dtEprl = 0.5*diff(dat(:,27)); dtEprl = [dtEprl(1); dtEprl]./dthst*vol;
dtEtotprp =0.5* diff(dat(:,23)); dtEtotprp = [dtEtotprp(1); dtEtotprp]./dthst*vol;
dtEtotprl = 0.5*diff(dat(:,22)); dtEtotprl = [dtEtotprl(1); dtEtotprl]./dthst*vol;
imbal = (zp2 - zm2)./(zp2 + zm2);

etot = -dedt+diss_hypr+dtKE+dtME+dtEprp+dtEprl;
plot(t(is),filt(dedt),t(is),filt(dtKE+dtME),t(is),filt(diss_hypr),'--',...
    t(is),dtEprp(is),'--',t(is),dtEprl(is),'--',...
    t(is),filt(etot),'k-',t(is),0*t(is),':k')
sige = @(t) 0.9*(1-2/3*0.1*max(0,t - 18.2)/0.9);
%plot(t(is),filt(2.0.*epsm),t(is),filt(diss_hypr),'--',t,(1-sige(t)).*ep,':',t(is),etot(is),'k-',t(is),0*t(is),':k')


% plot(t(is),filt(dtKE+dtME),...
%     t(is),filt(dtEprp+dtEprl),'-',t(is),zeros(size(is)),'k:')
% plot(t,dedt,t,-diss_hypr,t,0*dtKE+dtME,'--',t,dtEtotprp,'--',t,dtEtotprl,'--',...
%     t,-dedt+diss_hypr+dtME+dtEtotprp+dtEtotprl,'k-',t,0*t,':k')
legend({'$\varepsilon$','$\partial_t(E_K+E_B)$','$\varepsilon_\eta$','$\partial_t E_{th,\perp}$','$\partial_t E_{th,\|}$',...
    'Sum of all terms $-\varepsilon$'},...
    'interpreter','latex')
%legend({'$2 \varepsilon^-$','$\varepsilon_\eta$','Expected small scale dissipation','Sum of all terms $-\varepsilon$'},...
%    'interpreter','latex')
% legend({'$\partial_t(E_K+E_B)$','$\partial_t (E_{th,\perp}+E_{th,\|})$'},...
%     'interpreter','latex')
%ylim([-30 50])


% plot(t(is),filt(dtzm2),t(is),(1-sige)*on(is)*ep-diss_hypr(is),t(is),zeros(size(is)),'k:')
% legend({'$\partial_t\langle z_-^2\rangle$','$2\varepsilon^--\varepsilon_\eta$'},...
%     'interpreter','latex')


xlabel('$t/\tau_A$','interpreter','latex')
set(gcf,'Color','w')
legend boxoff
% xlim([0 18.1])


figure('Color',[1 1 1]);
plot(t(is),filt(dedt),'-','Linewidth',3) 
hold on
plot(t(is),filt(dtKE+dtME),'--','Linewidth',3)
plot(t(is),filt(diss_hypr),'--','Linewidth',3)
plot(t(is),filt(dtEprp),'--','Linewidth',3)
plot(t(is),filt(dtEprl),'--','Linewidth',3)
plot(t(is),filt(etot),'k-','Linewidth',3)
plot(t(is),0*t(is),':k','Linewidth',3)
hold off
legend({'$\varepsilon$','$\partial_t(E_K+E_B)$','$\varepsilon_\eta$','$\partial_t E_{th,\perp}$','$\partial_t E_{th,\|}$',...
    'Sum of all terms $-\varepsilon$'},...
    'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\epsilon$','interpreter','latex')
set(gca,'fontsize', 16);




if 0 && size(dat,2)>epsind+3
    figure
    voltot = vol;
    nmb = 294*56;
    fu = dat(is,epsind+4);%/nmb*voltot ;
    fb = dat(is,epsind+5);%/nmb*voltot;
    [fsu,fp,tp] = pspectrum(fu,t(is),'spectrogram','TimeResolution',0.3);
    [fsb,fp,tp] = pspectrum(fb,t(is),'spectrogram','TimeResolution',0.3);
    semilogy(t(is),fu,t(is),fb)
    yyaxis right;semilogy(tp,sum(fsu(3*length(fp)/4:end,:),1),tp,sum(fsb(3*length(fp)/4:end,:),1))
%     loglog(fp,fsu(:,2:2:end).',fp,1e-3*fp.^-2,'k:')
%     tplot= [find(tp>3900,1),find(tp<4800,1,'last')];
%     loglog(fp(2:end),fsu(2:end,tplot(1):2:tplot(2)))
%     subplot(211)
%     s=pcolor(tp,log10(fp(2:end)),log10(fsu(2:end,:)));set(gca,'YDir','normal');
%     s.EdgeColor='none';colorbar;caxis([-6 2])
%     subplot(212)
%     s=pcolor(tp,log10(fp(2:end)),log10(fsb(2:end,:)));set(gca,'YDir','normal');colorbar;caxis([-6 2])
%     s.EdgeColor='none';colorbar;caxis([-6 2])
%     xlabel('$t$','interpreter','latex')
%     ylabel('Forcing normalization','interpreter','latex')
end

% % Freq spec
% figure(7);%hold on
% tfreq = t(t<860);
% dfreq = dat(t<860,epsind+4);
% nf = floor(length(tfreq)/2);
% omega= 2*pi/(tfreq(end)-tfreq(1))*[0:1:nf];
% ps = abs(fft(dfreq)).^2;
% loglog(omega,ps(1:nf+1))
% hold on
% omegacorr = 2*pi/64.4;
% loglog(omegacorr*[1 1],[1e-10 1e10],'k:')


% Used for talk TODELETE
sige = @(t) max(0.9*(1-2/3*0.1*max(0,t - 18.2)/0.9),0);
filt = @(f) filter((1/windowSize)*ones(1,windowSize),1,f);
% figure
% Qi = dtEprp+dtEprl-etot;
% inc = Qi<60 & Qi>0;
% tq = t(inc);Qi = Qi(inc);diss_hypr = diss_hypr(inc);
% % plot(tq,filt(diss_hypr),tq,filt(Qi),'LineWidth',1)
% semilogy(tq,filt(Qi)./filt(diss_hypr),tq,ones(size(tq)),'k:','LineWidth',1)
% hold on
% % ax=gca;ax.ColorOrderIndex=1;
% % plot(t,(1-sige(t)).*ep,':',t,ep-(1-sige(t)).*ep,':','LineWidth',1)
% % xlim([0 1]); ylim([0 0.06])
% xlabel('$t/\tau_A$','interpreter','latex')
% ylabel('$Q_i/Q_e$','interpreter','latex')
% % ylim(2*[-10 40])
% xlim([0 max(t)])
figure
Qi = dtEprp+dtEprl-etot;
inc = Qi<60 & Qi>0;
tq = t(inc);dtEprp = dtEprp(inc)-2/3*etot(inc);dtEprl = dtEprl(inc)-1/3*etot(inc);
% plot(tq,filt(diss_hypr),tq,filt(Qi),'LineWidth',1)
plot(tq,filt(dtEprp),tq,filt(dtEprl), tq,ones(size(tq)),'k:','LineWidth',1)
hold on
% ax=gca;ax.ColorOrderIndex=1;
% plot(t,(1-sige(t)).*ep,':',t,ep-(1-sige(t)).*ep,':','LineWidth',1)
% xlim([0 1]); ylim([0 0.06])
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$Q_\perp,Q_\|$','interpreter','latex')
% ylim(2*[-10 40])
xlim([0 max(t)])

hold off
loglog(filt(dtEprp), filt(zp2(inc).^0.67.*zm2(inc).^0.33),filt(dtEprp),0.005*filt(dtEprp).^0.5,'k:')
% semilogy(tq, filt(zp2(inc).^0.67.*zm2(inc).^0.33),tq, filt(zp2(inc))/4,tq, 10*filt(zm2(inc)))
% inc(tq<18)=0;
% loglog(zp2(inc),1./(1-imbal(inc)),zp2(inc),300* zp2(inc).^1,'k:')



end


function inds = restart_overlaps(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1818];
inds = [];
for inn = 1:length(rinds) %for each restart index
    tb = t(rinds(inn)-1); %find the time just before the restart
    ia = find(t(rinds(inn):end)>tb,1);  %find the first index after each restart index that has time greater than that just before the restart
    inds = [inds rinds(inn)-1:rinds(inn)+ia]; %append all indices from before restart until a greater time is encountered to index array.  - won't work if haven't progressed past that point post-restart
end
inds = setdiff(1:length(t),inds);%returns all indices except those in inds
end


function inds = t144_restart_overlaps(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1818];
inds = [];
for inn = 1:3%1:length(rinds)-1 %for each restart index
    tb = t(rinds(inn)-1); %find the time just before the restart
    ia = find(t(rinds(inn):end)>tb,1);  %find the first index after each restart index that has time greater than that just before the restart
    inds = [inds rinds(inn)-1:rinds(inn)+ia]; %append all indices from before restart until a greater time is encountered to index array.  - won't work if haven't progressed past that point post-restart
end
inds = setdiff(1:length(t(1:rinds(4)-1)),inds);%returns all indices except those in inds
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

function inds = restart_overlaps_dt(t,dtX)
% Find indicies where the restart has dtX to become large
dtlim = 0.5; % nominal value is 1
cval = max(dtX)/10;
inds = dtX < cval;

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
disp(t(rinds)/(6*48.1802))
end