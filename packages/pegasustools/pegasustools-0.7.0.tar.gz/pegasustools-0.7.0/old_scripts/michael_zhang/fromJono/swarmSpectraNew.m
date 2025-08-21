function swarmSpectraNew

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


flds={'bx','by','bz','ex','ey','ez','ux','uy','uz','rho','fx','fy','fz'};

% Sometimes get repeated times for some reason ? remove these.
rtms =  find(diff(sarr(2,:,1))==0);
disp(['Removing times ' mat2str(rtms)])
sarr(:,rtms,:) = [];

nspctot = 0;
%imbalanced
tcent =  [1 3   5   7.5   9   11  13.5   ]; % central times over which to FT (psectrum computes this automatically, so ignore if using this)
dtwind = [1 1.5 1.5 1.5 1.5 1.5 1.5 ];
%balanced
%tcent = [1 3 5 6];
%dtwind = [1 1.5 1.5 1.5];

all_nspc = 100;

for ttt=1:length(tcent)
    inds = sarr(2,:,1)>tauA*(tcent(ttt)-dtwind(ttt)) & sarr(2,:,1)<tauA*(tcent(ttt)+dtwind(ttt));
    tin = sarr(2,inds,1); 
    ns = length(tin);
    T = tin(end)-2*tin(1)+tin(2);
    omega = 2*pi/T*(1:ceil(ns/2-1)).';
    disp(['Including ' num2str(ns) ' time points with omega_min = ' num2str(2*pi/(tin(end)-2*tin(1)+tin(2)))])
    time_filter =hamming(ns,'periodic'); % Top hat window a bit more polluted with high freq noise + a little more ringing a low freq
    for nnn=1:length(flds)
        num = nnn+8;
        tmp = 0;
        tot_spc = 0;
        for nspc = 1:all_nspc
            if sum(sum(sarr(6:8,:,nspc)))<1e-5
%                 if nnn==1;disp(['Including spacecraft ' num2str(nspc)]);end
                ft = fft(time_filter.*(sarr(num,inds,nspc)-mean(sarr(num,inds,nspc))).');
                tmp = tmp + abs(ft(1:length(omega))).^2;
                tot_spc = tot_spc+1;
            end
        end
        tmp = tmp/tot_spc;
        sp.(flds{nnn}){ttt} = tmp*(T^2/pi/ns^2); % Without a filter, this ensures \int dt db^2 = \int domega P(omega)
    end
    sp.omega{ttt} = omega;
    sp.trange{ttt} = [tcent(ttt)-dtwind(ttt) tcent(ttt)+dtwind(ttt)];
    sp.tp{ttt} = tcent(ttt);
end
    save(['saved-analysis/swarmspec-' name '-new.mat'],'sp'); 
else % doFullCalculation
    load(['saved-analysis/swarmspec-' name '-new.mat'],'sp'); 
end


% Filter
wind = floor(3);
filt = @(f) filter((1/wind)*ones(wind,1),1,f.').';

figure
% tosubtrct = 0.5*(mearly(sp.by)+mearly(sp.bz)).*norm;

for ttt=1:length(sp.trange)

    norm = sp.omega{ttt}.^2;
    subplot(311)
    loglog(sp.omega{ttt},0.5*filt(sp.by{ttt}+sp.bz{ttt}).*norm,...sp.omega{ttt},filt(sp.bx{ttt}),'--',...
        'Color',tcol(mean(sp.trange{ttt}),[0 18]+18.2))
    hold on
    xlabel('$\omega/\Omega_i$')
    title(['$t=' n2s(sp.trange{ttt}) ',\,B$'])
%     hold off

    subplot(312)
    loglog(sp.omega{ttt},0.5*filt(sp.ey{ttt}+sp.ez{ttt}).*norm,...sp.omega{ttt},filt(sp.ex{ttt}),'--',...
        'Color',tcol(mean(sp.trange{ttt}),[0 18]+18.2))
    hold on
    xlabel('$\omega/\Omega_i$')
    title(['$t=' n2s(sp.trange{ttt}) ',\,E$'])
%     hold off

    subplot(313)
    loglog(sp.omega{ttt},filt(sp.rho{ttt}).*norm,...sp.omega{ttt},0.5*filt(sp.uy{ttt}+sp.uz{ttt}),'--',...
        'Color',tcol(mean(sp.trange{ttt}),[0 18]+18.2))
    hold on
    xlabel('$\omega/\Omega_i$')
    title(['$t=' n2s(sp.trange{ttt}) ',\,\rho,\,u_\perp$'])
%     hold off

    ginput(1)
% pause(1)
    drawnow
end
subplot(311)


tplt = [7.5 13.5]; %imbalanced
tind = [4 length(sp.trange)]
%tplt = [6.0]; %balanced
%tind = [length(sp.trange)]

swarm.bprp = {};
swarm.eprp = {};
swarm.tav = {};
swarm.bprl = {};
swarm.eprl = {};
swarm.rho = {};
swarm.omega = {};
for ttt = 1:length(tplt)
    swarm.omega{ttt} = sp.omega{tind(ttt)}
    norm = swarm.omega{ttt}.^2;
    swarm.bprp{ttt} = 0.5*filt(sp.by{tind(ttt)}+sp.bz{tind(ttt)}).*norm;
    swarm.eprp{ttt} = 0.5*filt(sp.ey{tind(ttt)}+sp.ez{tind(ttt)}).*norm;
    swarm.bprl{ttt} = filt(sp.bx{tind(ttt)}).*norm;
    swarm.eprl{ttt} = filt(sp.ex{tind(ttt)}).*norm;
    swarm.rho{ttt} = filt(sp.rho{tind(ttt)}).*norm;
end



swarm.bprp
swarm.eprp
swarm.bprl
swarm.eprl
swarm.rho

%swarm.rho{2}

save([ savebase 'PlotSwarmNew-' name '.mat'],'swarm', '-v7.3');

end