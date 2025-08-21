function [t,kp,kl,qprp_kprp,qprl_kprp,qprp_kprl,qprl_kprl] = readHeating(varargin)% 
if nargin>0
    name =varargin{1}; 
    toplot=0;
    smooth=0;
    type =varargin{2};
else
    name ='sig-decr-prod'; 
    smooth=1;
    toplot=1;
    type = 4 ; % a=1,b=2,c=3,d=4. a & c are E1=Eprl. b & d are E.v and E.w (Eprl=Eprl)
end

p_id = 'particles';
fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
n2s = @(s) num2str(s);

fid = fopen([fname '.heat_prl']);
[t,dt,qp_kp,qp_kl]=readheat(fid);
sk = size(qp_kp,1)/4;
qprl_kprp = qp_kp((type-1)*sk+1:(type)*sk,:);
qprl_kprl = qp_kl((type-1)*sk+1:(type)*sk,:);
fclose(fid);
%
fid = fopen([fname '.heat_prp']);
[t,dt,qp_kp,qp_kl,kprp,kprl]=readheat(fid);
qprp_kprp = qp_kp((type-1)*sk+1:(type)*sk,:);
qprp_kprl = qp_kl((type-1)*sk+1:(type)*sk,:);
dth = 5;
fclose(fid);

kp = mean(kprp,2);
kl = mean(kprl,2);

tauA = 6*67.4523; 
norm = 216*6*372^3/(6*67.4523^3);

% Filtering and subtracting off noise contribution
noiseregion = floor(0.3*tauA/dth);
windowSize = floor(1*tauA/dth);

is = restart_overlaps(t);
t=t(is);
qprp_kprp = qprp_kprp(:,is);qprp_kprl = qprp_kprl(:,is);
qprl_kprp = qprl_kprp(:,is);qprl_kprl = qprl_kprl(:,is);

reminit=1;
if smooth
qprp_kprp = qprp_kprp-reminit*mean(qprp_kprp(:,2:noiseregion),2);
qprp_kprl = qprp_kprl-reminit*mean(qprp_kprl(:,2:noiseregion),2);
qprl_kprp = qprl_kprp-reminit*mean(qprl_kprp(:,2:noiseregion),2);
qprl_kprl = qprl_kprl-reminit*mean(qprl_kprl(:,2:noiseregion),2);
filt = @(f) filter((1/windowSize)*ones(1,windowSize),1,f.').';
qprp_kprp = filt(qprp_kprp)/norm;
qprp_kprl = filt(qprp_kprl)/norm;
qprl_kprp = filt(qprl_kprp)/norm;
qprl_kprl = filt(qprl_kprl)/norm;
end

if toplot

rhoi = sqrt(1/0.3);
limprp = [ min(min(min(qprp_kprp)),min(min(qprl_kprp))) max(max(max(qprp_kprp)),max(max(qprl_kprp)))];
limprl = [min(min(min(qprp_kprl)),min(min(qprl_kprl))) max(max(max(qprp_kprl)),max(max(qprl_kprl))) ];

figure
tstrt = 14; tstrt = floor(tstrt*tauA/(t(3)-t(2)));
lname = {};
t = t/tauA;
for ttt=tstrt:windowSize:length(t)-1
    subplot(211)
    semilogx(kp,qprl_kprp(:,ttt),'Color',tcol(t(ttt),[18 36]))
    lname = [lname ['$t=' num2str(t(ttt)) '\tau_A$']];
    hold on
    
    ylim(limprp)
    xlim([min(kp) max(kp)])
    xlabel('$k_\perp d_i$','interpreter','latex')
    ylabel('$Q_\perp$','interpreter','latex')
    legend({'$Q_\perp$','$Q_\|$'},'interpreter','latex','location','southwest')
    hold on
    title(['$t=' n2s(t(ttt)),'\tau_A$'],'interpreter','latex')
    subplot(212)
    semilogx(kl,qprl_kprl(:,ttt),'Color',tcol(t(ttt),[18 34]))
    ylim(limprl)
    xlim([min(kl) max(kl)])
    xlabel('$k_\| d_i$','interpreter','latex')
    hold on
    drawnow
end
semilogy(rhoi*[1 1],1e10*[-1 1],'k:',kp,0*kp,'k:')%,kp,qprl_kprp(:,ttt),
% legend(lname,'interpreter','latex');

end


end



function [t,dt,qp_kp,qp_kl,kprp,kprl]=readheat(fid)
s = fgetl(fid); % # Pegasus++ parallel heating vs k_perp and k_prl
disp(s)
s = fgetl(fid); % # [1]=time     [2]=dt            
nk = fscanf(fid,'nheat_bins=%d      nheat_bins_prl=%d      ');

kfull = fscanf(fid,'%f');
if length(kfull)== 2*(nk(1)+1)+2*(nk(2)+1)
    nl=2*(nk(1)+1)+1;
    kprp = [kfull(1:nk(1)+1) kfull(nk(1)+2:2*(nk(1)+1))];
    kprl = [kfull(nl:nl+nk(2)) kfull(nl+1+nk(2):end)];
else
    warning('kfull seems the wrong length')
end

fgetl(fid); % #
alldat = fscanf(fid,'%f');
ncol = 4*(nk(1)+1)+4*(nk(2)+1)+2;
alldat = reshape(alldat,[ncol,numel(alldat)/ncol]);

t = alldat(1,:);
dt = alldat(2,:);
qp_kp = alldat(3:4*(nk(1)+1)+2,:);
qp_kl = alldat(4*(nk(1)+1)+3:end,:);

if size(qp_kp,1)~=size(qp_kl,1)
    error('Couldn''t read qs correctly')
end
end




function inds = restart_overlaps(t)
% Find indicies where the restart has caused an overlap
dtlim = 2.5; % nominal value is 1
rinds = find(diff(t)<dtlim)+1;
inds = [];
for inn = 1:length(rinds)
    tb = t(rinds(inn)-1);
    ia = find(t(rinds(inn):end)>tb,1);
    inds = [inds rinds(inn):rinds(inn)+ia];
end
inds = setdiff(1:length(t),inds);

end




