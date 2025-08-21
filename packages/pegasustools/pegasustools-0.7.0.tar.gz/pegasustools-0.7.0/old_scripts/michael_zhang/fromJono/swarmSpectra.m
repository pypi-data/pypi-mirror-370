function swarmSpectra

% Spectra from sections of swarm data.

% Saved swarm data into swarm.mat using readSwarm
name = 'half_tcorr_sim9';
%name = 'b_b3_sim1';
savebase = ['saved-analysis/']; %outputfolder '../../'
doFullCalculation = 1;
tauA = 6*48.1802;

n2s = @(s) num2str(s);


if doFullCalculation
load(['/projects/KUNZ/mfzhang/simulations/' name '/output/swarm/swarm.mat']);sarr=sarray_full;clear sarray_full
% load(['saved-analysis/swarm-small.mat'])

% Numbers
% 1 id: 2 t: 3-5 x: 6-8 v: 9-11 B: 12-14 E: 15-17 U: 18 rho: 19-21 F


flds={'bx','by','bz','ex','ey','ez','ux','uy','uz','rho'};
for nnn=1:length(flds);sp.(flds{nnn})=0;end

% Sometimes get repeated times for some reason – remove these.
rtms =  find(diff(sarr(2,:,1))==0);
disp(['Removing times ' mat2str(rtms)])
sarr(:,rtms,:) = [];

nspctot = 0;
for nspc = 1:100
    if sum(sum(sarr(6:8,:,nspc)))<1e-5
        disp(['Including spacecraft ' num2str(nspc)])
        for nnn=1:length(flds)
            num = nnn+8;
            [tmp,fp,tp] = pspectrum(sarr(num,:,nspc),sarr(2,:,nspc),'spectrogram','TimeResolution',tauA);
            %sarr(num,:,nspc)
            sp.(flds{nnn}) = sp.(flds{nnn}) + tmp;
        end
        nspctot = nspctot+1;
    end
end
for nnn=1:length(flds);sp.(flds{nnn})=sp.(flds{nnn})/nspctot;end
sp.fp = fp;  
sp.tp = tp;
    save(['saved-analysis/swarmspec-' name '.mat'],'sp'); 
else % doFullCalculation
    load(['saved-analysis/swarmspec-' name '.mat'],'sp'); 
end

omega=2*pi*sp.fp(2:end);
%tmid = [find(sp.tp>4*tauA,1) find(sp.tp>12*tauA,1)];
%tlate = [find(sp.tp>15.5*tauA,1) ];

tmid = [find(sp.tp>4*tauA,1) find(sp.tp>12*tauA,1)];
tlate = [find(sp.tp>14*tauA,1) ];

mmid = @(f) mean(f(2:end,tmid(1):tmid(2)),2);
mlate = @(f) mean(f(2:end,tlate:end),2);

m = @(d,t,tav) mean(d(2:end,find(t>=tav(1) & t<=tav(2))),2);
m2 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);

tplt = [7.5 14.2];
%tplt = [7.0];
dtplt = 0.5;
tavplt = [tplt-dtplt;tplt+dtplt];
tav = sp.tp/tauA;

norm = omega.^2;

% Filter
wind = floor(20);
filt = @(f) filter((1/wind)*ones(wind,1),1,f.').';

figure
sp.tp = sp.tp/tauA;
mearly = @(f) mean(f(2:end,1:2),2);
tosubtrct = 0.5*(mearly(sp.by)+mearly(sp.bz)).*norm;
dn=5;
disp(length(sp.tp))
for nn =dn+1:dn+1:length(sp.tp)-dn
    disp("doing ")
    disp(nn)
    mnow = @(f) mean(f(2:end,nn-dn:nn+dn),2);
    subplot(311)
    loglog(omega,0.5*(mnow(sp.by)+mnow(sp.bz)).*norm,omega,(mnow(sp.bx)).*norm,'--','Color',tcol(sp.tp(nn)))
% %     loglog(omega,0.5*(mnow(sp.ey)+mnow(sp.ez)).*norm-0*tosbtrct,'Color',tcol(sp.tp(nn)));
    hold on
    loglog(omega,1e-5*ones(size(omega)),'k:')
    xlabel('$\omega/\Omega_i$')
      title(['$t=' n2s(sp.tp(nn)) ',\,B$'],'interpreter','latex')
%     hold off

    subplot(312)
    loglog(omega,0.5*(mnow(sp.ey)+mnow(sp.ez)).*norm,omega,(mnow(sp.ex)).*norm,'--','Color',tcol(sp.tp(nn)))
    hold on
    title(['$t=' n2s(sp.tp(nn)) ',\,E$'],'interpreter','latex')
%     hold off

    subplot(313)
    loglog(...omega,0.5*(mnow(sp.uy)+mnow(sp.uz)).*norm,...omega,(mnow(sp.ux)).*norm,'--',...
        omega,(mnow(sp.rho)).*norm,'-','Color',tcol(sp.tp(nn)))
    hold on
    title(['$t=' n2s(sp.tp(nn)) ',\,u$'],'interpreter','latex')
%     hold off

% ginput(1)
pause(1)
    drawnow
end
subplot(311)




swarm.bprp = {};
swarm.eprp = {};
swarm.tav = {};
swarm.bprl = {};
swarm.eprl = {};
swarm.rho = {};
for ttt = 1:length(tplt)
    swarm.bprp{ttt} = 0.5*(m(sp.by,tav,tavplt(:,ttt))+m(sp.bz,tav,tavplt(:,ttt))).*norm;
    swarm.eprp{ttt} = 0.5*(m(sp.ey,tav,tavplt(:,ttt))+m(sp.ez,tav,tavplt(:,ttt))).*norm;
    swarm.tav{ttt} = m2(tav,tav,tavplt(:,ttt));
    swarm.bprl{ttt} = m(sp.bx,tav,tavplt(:,ttt)).*norm;
    swarm.eprl{ttt} = m(sp.ex,tav,tavplt(:,ttt)).*norm;
    swarm.rho{ttt} = m(sp.rho,tav,tavplt(:,ttt)).*norm;
end

swarm.omega = omega;
swarm.tp = sp.tp;
%swarm.tend = mlate(sp.tp);
%swarm.bprp = 0.5*(mlate(sp.by)+mlate(sp.bz)).*norm;
%swarm.eprp = 0.5*(mlate(sp.ey)+mlate(sp.ez)).*norm;
swarm.bprp
swarm.eprp
swarm.bprl
swarm.eprl
swarm.rho

%swarm.rho{2}

save([ savebase 'PlotSwarm-' name '.mat'],'swarm', '-v7.3');

end