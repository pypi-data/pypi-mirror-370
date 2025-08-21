function plotNBFhistoryandhst%( fname )

name = 'half_tcorr_sim9';%'test-force';'sig-decr-prod';
p_id = 'minor_turb';
fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs

vol=6*48.1802^3;
tauA = 6*48.1802;

% Plots variables from hst file
fulldata = importdata([ fname '.hst']);

try
    names = strsplit(fulldata.textdata{2},'  ');
    names = names(1:end-1);
    dat = fulldata.data;
catch
    dat = fulldata;
end

t = dat(:,1);
is = restart_overlaps(t);

dt = dat(:,2);
dthst = diff(t);dthst = [ dthst(1);dthst ];
vol=  6*48.1802^3; %4*500^3;6*67.4523^3;
tauA = 6*48.1802;  %4*500;6*67.4523;

epsind = 34;
%dat(epsind) is totaluf etc. * dt of that timestep (avged throughout box)
%  zpdotfp = (curlyt + V.force2)* (V.vel2+V.Bcc2) + (curlzt + V.force3) * (V.vel3+V.Bcc3)
%  (curlyt*V.vel2 + curlyt*V.Bcc2 + V.force2*V.vel2 + V.force2*V.Bcc2) + (curlzt*V.vel3 + curlzt*V.Bcc3 + V.force3*V.vel3 + V.force3*V.Bcc3) 
%  (curlyt*V.vel2 + curlzt*V.vel3 + curlyt*V.Bcc2 + curlzt*V.Bcc3 + V.force2*V.vel2 + V.force3*V.vel3 + V.force2*V.Bcc2  + V.force3*V.Bcc3)
%  (totalufb + totalb + totalu + totalbfu)

%  zmdotfm = (-curlyt + V.force2)* (V.vel2-V.Bcc2) + (-curlzt + V.force3) * (V.vel3-V.Bcc3)
%  (-curlyt*V.vel2 + curlyt*V.Bcc2 + V.force2*V.vel2 - V.force2*V.Bcc2) + (-curlzt*V.vel3 + curlzt*V.Bcc3 + V.force3*V.vel3 - V.force3*V.Bcc3) 
%  (-curlyt*V.vel2 - curlzt*V.vel3 + curlyt*V.Bcc2 + curlzt*V.Bcc3 + V.force2*V.vel2 + V.force3*V.vel3 - V.force2*V.Bcc2  - V.force3*V.Bcc3)
%  (-totalufb + totalb + totalu - totalbfu)
epsp = (dat(:,epsind)+dat(:,epsind+1)+dat(:,epsind+2)+dat(:,epsind+3))./dthst;
epsm = (dat(:,epsind)+dat(:,epsind+1)-dat(:,epsind+2)-dat(:,epsind+3))./dthst;
cross_hel = sum(dat(:,16:18),2); %*96^2*560*100;   %vol(i)*u_mx*bcc1 * 1./std::sqrt(u_d);
zp_hst = sqrt(sum(dat(:,7:9),2) + sum(dat(:,10:12),2) + cross_hel);  % u^2 + b^2 + cross_hel
zm_hst = sqrt(sum(dat(:,7:9),2) + sum(dat(:,10:12),2) - cross_hel);

dens0 = dat(is,3); dens1 = dat(is,38); dens2 = dat(is,38+24);
momx0 = dat(is,4); momx1 = dat(is,39); momx2 = dat(is,39+24);
momy0 = dat(is,5); momy1 = dat(is,40); momy2 = dat(is,40+24);
momz0 = dat(is,6); momz1 = dat(is,41); momz2 = dat(is,41+24);

t=t/tauA;

%mean(dedt(is))
%mean(dehdt(is))


%ts = array of times (in units of t_A that we have nbfs for, and want to plot hst at

t_inded = t(is);
epspinded = epsp(is);
epsminded = epsm(is);
zp_hstinded = zp_hst(is);
zm_hstinded = zm_hst(is);


computer = 'tigress';%'local';
nums = [137:138];%[0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53]; % snapshot numbers for which to find spectrum
ts = nums / 10.0;


round(t_inded,2)

[C,nbfinds,ib] = intersect(round(t_inded,2),ts);
%nbfinds = any(abs(bsxfun(@minus, t_inded(:).', ts(:))) < 1.7*10^-6, 1);
%dt=10^-3. = 10^-3/290 = 3.4 * 10^-6 t_A
%to nearest 0.1t_A - tol = 1.7*10^-6

disp(nbfinds);
disp(size(nbfinds));
disp(size(t_inded));

%fig=figure;
%plot(t_inded(nbfinds),epspinded(nbfinds),'--',t_inded(nbfinds),epsminded(nbfinds),'--','Linewidth',1)
%legend({'$\varepsilon^+$','$\varepsilon^-$'},'interpreter','latex')
%xlabel('$t/\tau_A$','interpreter','latex')

%fig=figure;
%plot(t_inded(nbfinds),zp_hstinded(nbfinds),'--',t_inded(nbfinds),zm_hstinded(nbfinds),'--','Linewidth',1)
%legend({'$\varepsilon^+$','$\varepsilon^-$'},'interpreter','latex')
%xlabel('$t/\tau_A$','interpreter','latex')

[readF,files_all] = chooseComputerAndFiles(name,computer);

fpmag = zeros(size(nums));
f2pmag = zeros(size(nums));
f3pmag = zeros(size(nums));
fmmag = zeros(size(nums));
f2mmag = zeros(size(nums));
f3mmag = zeros(size(nums));
b_force = zeros(size(nums));
curlmag = zeros(size(nums));
curl_y = zeros(size(nums));
curl_z = zeros(size(nums));
fomag = zeros(size(nums));
fo2 = zeros(size(nums));
fo3 = zeros(size(nums));
zpmag = zeros(size(nums));
zmmag = zeros(size(nums));
zpdotfpmag = zeros(size(nums));
zmdotfmmag = zeros(size(nums));
zpdotfpmean = zeros(size(nums));
zmdotfmmean = zeros(size(nums));
zpdotfpnormmean = zeros(size(nums));
zmdotfmnormmean = zeros(size(nums));
zpxmag = zeros(size(nums));
zpymag = zeros(size(nums));
zpzmag = zeros(size(nums));
zmxmag = zeros(size(nums));
zmymag = zeros(size(nums));
zmzmag = zeros(size(nums));
uxmag = zeros(size(nums));
uymag = zeros(size(nums));
uzmag = zeros(size(nums));

ind = 1;
for nnn = nums
    disp(nnn);
    try
        V = readF(files_all(nnn));
    catch
        continue
    end
    b_forcey = zeros(size(V.b_force),'like',V.b_force);
    b_forcez = zeros(size(V.b_force),'like',V.b_force);

    NX=length(V.x);LX=V.x(end)-V.x(1)+(V.x(2)-V.x(1));
    NY=length(V.y);LY=V.y(end)-V.y(1)+(V.y(2)-V.y(1));
    NZ=length(V.z);LZ=V.z(end)-V.z(1)+(V.z(2)-V.z(1));
    [XG,YG,ZG]=meshgrid(linspace(0,LX,NX),linspace(0,LY,NY),linspace(0,LZ,NZ));
    [curlx,curly,curlz,cav] = curl(XG,YG,ZG,pagetranspose(V.b_force),pagetranspose(b_forcey),pagetranspose(b_forcez));
    curlxt = pagetranspose(curlx);
    curlyt = pagetranspose(curly);
    curlzt = pagetranspose(curlz);


    f2p = curlyt + V.force2;
    f3p = curlzt + V.force3;

    f2m =  V.force2 - curlyt;
    f3m =  V.force3 - curlzt;

    zpx = V.vel1+V.Bcc1 -1.0;
    zpy = V.vel2+V.Bcc2;
    zpz = V.vel3+V.Bcc3;

    zmx = V.vel1-V.Bcc1 + 1.0;
    zmy = V.vel2-V.Bcc2;
    zmz = V.vel3-V.Bcc3;

    zpdotfp = f2p.*zpy + f3p.*zpz;
    zmdotfm = f2m.*zmy + f3m.*zmz;

    zpdotfpnormed = curlyt.*V.vel2.*V.dens + curlzt.*V.vel3.*V.dens + curlyt.*V.Bcc2 + curlzt.*V.Bcc3 + V.force2.*V.vel2.*V.dens + V.force3.*V.vel3.*V.dens + V.force2.*V.Bcc2.*sqrt(V.dens)  + V.force3.*V.Bcc3.*sqrt(V.dens);
    zmdotfmnormed = -curlyt.*V.vel2.*V.dens - curlzt.*V.vel3.*V.dens + curlyt.*V.Bcc2 + curlzt.*V.Bcc3 + V.force2.*V.vel2.*V.dens + V.force3.*V.vel3.*V.dens - V.force2.*V.Bcc2.*sqrt(V.dens)  - V.force3.*V.Bcc3.*sqrt(V.dens);

    zp2 = zpx.*zpx+zpy.*zpy+zpz.*zpz;
    zm2 = zmx.*zmx+zmy.*zmy+zmz.*zmz;
    zpx2 = zpx.*zpx;
    zpy2 = zpy.*zpy;
    zpz2 = zpz.*zpz;
    zmx2 = zmx.*zmx;
    zmy2 = zmy.*zmy;
    zmz2 = zmz.*zmz;

    fpf = f2p.*f2p+f3p.*f3p;
    fp22 = f2p.*f2p;
    fp32 =  f3p.*f3p;

    fmf = f2m.*f2m+f3m.*f3m;
    fm22 = f2m.*f2m;
    fm32 =  f3m.*f3m;

    b_force2 = V.b_force.*V.b_force;
    bb = curlyt.*curlyt+curlzt.*curlzt;
    curly2 = curlyt.*curlyt;
    curlz2 = curlzt.*curlzt;

    forcesq = V.force2.*V.force2 + V.force3.*V.force3;
    force2sq = V.force2.*V.force2;
    force3sq = V.force3.*V.force3;

    zpdotfpsq = zpdotfp.*zpdotfp;
    zmdotfmsq = zmdotfm.*zmdotfm;
    
    ux1 = V.mom1_s0./V.dens_s0;
    uy1 = V.mom2_s0./V.dens_s0;
    uz1 = V.mom3_s0./V.dens_s0;


    fpmag(ind) = sqrt(sum(fpf,"all")/numel(fpf));
    f2pmag(ind) = sqrt(sum(fp22,"all")/numel(fpf));
    f3pmag(ind) = sqrt(sum(fp32,"all")/numel(fpf));
    fmmag(ind) = sqrt(sum(fmf,"all")/numel(fpf));
    f2mmag(ind) = sqrt(sum(fm22,"all")/numel(fpf));
    f3mmag(ind) = sqrt(sum(fm32,"all")/numel(fpf));
    b_force(ind) = sqrt(sum(b_force2,"all")/numel(fpf));
    curlmag(ind) = sqrt(sum(bb,"all")/numel(fpf));
    curl_y(ind) = sqrt(sum(curly2,"all")/numel(fpf));
    curl_z(ind) = sqrt(sum(curlz2,"all")/numel(fpf));
    fomag(ind) = sqrt(sum(forcesq,"all")/numel(fpf));
    fo2(ind) = sqrt(sum(force2sq,"all")/numel(fpf));
    fo3(ind) = sqrt(sum(force3sq,"all")/numel(fpf));
    zpmag(ind) = sqrt(sum(zp2,"all")/numel(fpf));
    zmmag(ind) = sqrt(sum(zm2,"all")/numel(fpf));
    zpdotfpmag(ind) = sqrt(sum(zpdotfpsq,"all")/numel(fpf));
    zmdotfmmag(ind) = sqrt(sum(zmdotfmsq,"all")/numel(fpf));
    zpdotfpmean(ind) = sum(zpdotfp,"all")/numel(fpf);
    zmdotfmmean(ind) = sum(zmdotfm,"all")/numel(fpf);
    zpdotfpnormmean(ind) = sum(zpdotfpnormed,"all")/numel(fpf);
    zmdotfmnormmean(ind) = sum(zmdotfmnormed,"all")/numel(fpf);
    zpxmag(ind) = sqrt(sum(zpx2,"all")/numel(fpf));
    zpymag(ind) = sqrt(sum(zpy2,"all")/numel(fpf));
    zpzmag(ind) = sqrt(sum(zpz2,"all")/numel(fpf));
    zmxmag(ind) = sqrt(sum(zmx2,"all")/numel(fpf));
    zmymag(ind) = sqrt(sum(zmy2,"all")/numel(fpf));
    zmzmag(ind) = sqrt(sum(zmz2,"all")/numel(fpf));
    uxmag(ind) = sum(ux1,"all")/numel(fpf);
    uymag(ind) = sum(uy1,"all")/numel(fpf);
    uzmag(ind) = sum(uz1,"all")/numel(fpf);

    ind = ind + 1;

end




figure;
plot(ts,uxmag, t_inded(nbfinds),momx1(nbfinds)/dens1(nbfinds),'Linewidth',1)
legend({'$u_x$','$u_x$ hst'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
drawnow;

fig=figure;
plot(ts,fpmag, ts, f2pmag, ts,f3pmag,ts,fmmag,ts,f2mmag,ts,f3mmag,ts,curlmag,'--',ts,curl_y,'--',ts,curl_z,'--',ts,fomag,':',ts,fo2,':',ts,fo3,':','Linewidth',1)
legend({'$|F^+|$','$|F^+_y|$','$|F^+_z|$','$|F^-|$','$|F^-_y|$','$|F^-_z|$','$|curl(bforce|)$','$|curl(bf)_y|$','$|curl(bf)_z|$','$|force|$','$|force2|$','$|force3|$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
%savefig(['saved-analysis/nbfhist_forces-' name '.fig'])
%saveas(fig,['saved-analysis/nbfhist_forces-' name '.png'])
close(fig)

fig=figure;
plot(ts,b_force,'Linewidth',1)
legend({'$|b_force| (E_x)$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
%savefig(['saved-analysis/nbfhist_b_force_Ex-' name '.fig'])
%saveas(fig,['saved-analysis/nbfhist_b_force_Ex-' name '.png'])
close(fig)

fig=figure;
plot(ts,zpdotfpmag, ts, zmdotfmmag,'Linewidth',1)
legend({'$|z^+.F^+|$','$|z^-.F^-|$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
%savefig(['saved-analysis/nbfhist_zdotf-' name '.fig'])
%saveas(fig,['saved-analysis/nbfhist_zdotf-' name '.png'])
close(fig)

fig=figure;
plot(ts,zpmag, ts, zmmag,t_inded(nbfinds),zp_hstinded(nbfinds),'-.',t_inded(nbfinds),zm_hstinded(nbfinds),'-.',ts,zpxmag,'--',ts,zpymag,'--',ts,zpzmag,'--',ts,zmxmag,':',ts,zmymag,':',ts,zmzmag,':','Linewidth',1)
legend({'$|z^+|$','$|z^-|$','$|z^+|,hst$','$|z^-|,hst$','$|z^+_x|$','$|z^+_y|$','$|z^+_z|$','$|z^-_x|$','$|z^-_y|$','$|z^-_z|$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
%savefig(['saved-analysis/nbfhist_zmag-' name '.fig'])
%saveas(fig,['saved-analysis/nbfhist_zmag-' name '.png'])
close(fig)

fig=figure;
plot(ts,zpdotfpmean, ts, zmdotfmmean,t_inded(nbfinds),epspinded(nbfinds),'--',t_inded(nbfinds),epsminded(nbfinds),'--','Linewidth',1)
legend({'$z^+.F^+$','$z^-.F^-$','$\varepsilon^+$','$\varepsilon^-$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
%savefig(['saved-analysis/nbfhist_zdotfmean-' name '.fig'])
%saveas(fig,['saved-analysis/nbfhist_zdotfmean-' name '.png'])
close(fig)

fig=figure;
plot(ts,zpdotfpnormmean, ts, zmdotfmnormmean,t_inded(nbfinds),epspinded(nbfinds),'--',t_inded(nbfinds),epsminded(nbfinds),'--','Linewidth',1)
legend({'$z^+.F^+$','$z^-.F^-$','$\varepsilon^+$','$\varepsilon^-$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
%savefig(['saved-analysis/nbfhist_zdotfnormmean-' name '.fig'])
%saveas(fig,['saved-analysis/nbfhist_zdotfnormmean-' name '.png'])
close(fig)


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
