function energyInICmodes

% Split energy as a function of time into polarizations

name = 'half_tcorr_sim9';%'imbal2-prod';
p_id = 'minor_turb';

[~,~,~,~,outputfolder] = chooseComputerAndFiles(name,'tigress');
savebase = 'saved-analysis/';[outputfolder '/../../saved-analysis/'];
savefolder = [ savebase 'spectrum2D-' name '.mat'];
doFullCalculation = 1;
hcuticw = 0.7;
hcutkaw = 0.3;
withhc = 1;
n2s = @(s) num2str(s);

vol=6*48.1802^3;
tauA = 6*48.1802;

% if doFullCalculation
load(savefolder,'St');

% [tS,ord]=  sort(St.t/tauA);
tS = St.t/tauA;

% St.Bcc1 = St.Bcc1(:,:,ord);St.Bcc2 = St.Bcc2(:,:,ord);St.Bcc3 = St.Bcc3(:,:,ord);
% St.Ecc1 = St.Ecc1(:,:,ord);St.Ecc2 = St.Ecc2(:,:,ord);St.Ecc3 = St.Ecc3(:,:,ord);
% St.h1 = St.h1(:,:,ord);

hel = -St.h1./(St.Bcc1 + St.Bcc2 + St.Bcc3).*sqrt(St.kp.^2 + (St.kl.').^2);
hc = St.ch1e./sqrt(St.Bcc1 + St.Bcc2 + St.Bcc3)./sqrt(St.Ecc1 + St.Ecc2 + St.Ecc3); 
if withhc
    hel = hel.*sign(hc);
end



hmid = hel<=hcutkaw & hel>=-hcuticw;
hpos = hel>hcutkaw ;
hneg = hel<-hcuticw;

s2 = @(f) squeeze(sum(sum(f,2),1));
EBmid = s2(hmid.*(St.Bcc2 + St.Bcc3)/2.*St.nnorm);
EBpos = s2(hpos.*(St.Bcc2 + St.Bcc3)/2.*St.nnorm);
EBneg = s2(hneg.*(St.Bcc2 + St.Bcc3)/2.*St.nnorm);
EBlmid = s2(hmid.*(St.Bcc1)/2.*St.nnorm);
EBlpos = s2(hpos.*(St.Bcc1)/2.*St.nnorm);
EBlneg = s2(hneg.*(St.Bcc1)/2.*St.nnorm);
EEmid = s2(hmid.*(St.Ecc2 + St.Ecc3)/2.*St.nnorm);
EEpos = s2(hpos.*(St.Ecc2 + St.Ecc3)/2.*St.nnorm);
EEneg = s2(hneg.*(St.Ecc2 + St.Ecc3)/2.*St.nnorm);
EElmid = s2(hmid.*(St.Ecc1)/2.*St.nnorm);
EElpos = s2(hpos.*(St.Ecc1)/2.*St.nnorm);
EElneg = s2(hneg.*(St.Ecc1)/2.*St.nnorm);

%clear St hmid  hpos hneg hel hc
clear hmid hpos hneg hel hc
% save(['saved-analysis/ICenergy-' n2s(hcut) '-' n2s(withhc) '-' name '.mat'])
% else 
%     load(['saved-analysis/ICenergy-' n2s(hcut) '-' n2s(withhc) '-' name '.mat'])
% end


fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs

% Plots variables from hst file 
fulldata = importdata([ fname '.hst']);
dat = fulldata.data; 

t = dat(:,1);
is = restart_overlaps2(t);
n2s = @(s) num2str(s);


dt = dat(:,2);
dthst = mean(diff(t));

va = 1;
Euprp = dat(is,8) + dat(is,9);
Ebprp = dat(is,11) + dat(is,12);
Ebprl = dat(is,10);
Eeprp = dat(is,14) + dat(is,15);
Eeprl = dat(is,13);

t=t(is)/tauA;

figure
% subplot(211)
% semilogy(tS,EBmid,tS,EBpos,tS,EBneg,t,Ebprp,'k',tS,EBmid+EBpos+EBneg,'k--')
Et = EBmid+EBpos+EBneg;
semilogy(tS,EBneg./Et)
hold on
% load(['saved-analysis/ICenergy-' n2s(0.3) '-' n2s(withhc) '-' name '.mat'])
semilogy(tS,EBpos./Et)
ylim([1e-4 2e-1])
legend({['${\rm sgn}( H_c)H_m<-' n2s(hcuticw) '$'],['${\rm sgn}( H_c)H_m>' n2s(hcutkaw) '$'],'$E_{B\perp}$'},'interpreter','latex')
% subplot(212)
% semilogy(tS,EBlmid,tS,EBlpos,tS,EBlneg,t,Ebprl,'k',tS,EBlmid+EBlpos+EBlneg,'k--')
% legend({'$H\approx0$',['$H>' n2s(hcut) '$'],['$H<' n2s(hcut) '$'],'$E_{B\|}$'},'interpreter','latex')

% figure
% subplot(211)
% semilogy(tS,EEmid,tS,EEpos,tS,EEneg,t,Eeprp,'k',tS,EEmid+EEpos+EEneg,'k--')
% legend({'$H\approx0$','$H>0$','$H<0$','$E_{E\perp}$'},'interpreter','latex')
% subplot(212)
% semilogy(tS,EElmid,tS,EElpos,tS,EElneg,t,Eeprl,'k',tS,EElmid+EElpos+EElneg,'k--')
% legend({'$H\approx0$','$H>0$','$H<0$','$E_{E\|}$'},'interpreter','latex')

% subplot(211)
% s=pcolor(log10(St.kp),log10(St.kl),(-m(St.h1)./B2.*sqrt(St.kp.^2 + (St.kl.').^2)).');
% s.EdgeColor='none';s.FaceColor='interp';
% colorbar; caxis([-1 1])


size(St.kp)

size(St.kl)


kprange = St.kp <= 
hmid = hel<=hcutkaw & hel>=-hcuticw;
hpos = hel>hcutkaw ;
hneg = hel<-hcuticw;

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
