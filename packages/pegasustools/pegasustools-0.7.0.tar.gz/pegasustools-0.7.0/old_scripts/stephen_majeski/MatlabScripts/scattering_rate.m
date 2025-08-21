import ndSparse
run = '/projects/KUNZ/smajeski/fullfslowmode_0p6_4by1/output/';
run2 = '~/Desktop/';
% Code to extract data from track.dat files
nbrvars  = 5; 
nbrprocs = 1344;%5376;%11760; 0.6, 8by2, 8by1 in order
ntracked = 10;
ntvars = 16;
xmax = 4000;
ymax = 1000;
%

%get restart index fixes
num = [0 0];
fname = [run 'track/slow.' sprintf('%02d',num(1)) '.' sprintf('%05d',num(2)) '.track.dat'];
fulldata=importdata(fname);
t = fulldata.data(:,1);
[ss, es] = restartRemove(t);

%fix time array to get final array length (nbrdumps)
for i=length(ss):-1:1
    inds = ss(i)+2:es(i);
    t(inds) = [];
end
nbrdumps = length(t);
%{
%iterate through processors
allmudat = zeros(nbrdumps,nbrvars,nbrprocs*ntracked);
tic
for nn = 0:(ntracked-1)  % number of tracked particles per proc
  for kk = 0:(nbrprocs-1)   % number of processors
    num = [nn kk]
    fname = [run 'track/slow.' sprintf('%02d',num(1)) '.' sprintf('%05d',num(2)) '.track.dat'];
    % Read in 
    fulldata=importdata(fname);
    
    %fix data
    newdat = zeros(nbrdumps,ntvars);
    for j = 1:ntvars
        temp = fulldata.data(:,j); 
        for i=length(ss):-1:1
            inds = ss(i)+2:es(i);
            temp(inds) = [];
        end
        length(temp)
        newdat(:,j) = temp;
    end
    fulldata.data = newdat;
    
    %process raw data into mu, vprl
    w1 = fulldata.data(:,4) - fulldata.data(:,13);
    w2 = fulldata.data(:,5) - fulldata.data(:,14);
    w3 = fulldata.data(:,6) - fulldata.data(:,15);
    B1 = fulldata.data(:,7);
    B2 = fulldata.data(:,8);
    B3 = fulldata.data(:,9);
    wsq = w1.*w1+w2.*w2+w3.*w3;
    bsq = B1.*B1+B2.*B2+B3.*B3;
    bmg = sqrt(bsq);
    wpl = (w1.*B1+w2.*B2+w3.*B3)./bmg;
    mu  = wsq - wpl.*wpl;
    mu  = 0.5*mu./bmg;
    fulldata.data(:,[4]) = mu;
    fulldata.data(:,[5]) = wpl;
    mudat = fulldata.data(:,[1 2 3 4 5]);
    allmudat(1:nbrdumps, :, kk+1+nn*nbrprocs) = mudat;
  end
end
toc

%}
% YOU'LL WANT TO SAVE THIS SO YOU DON'T HAVE TO DO IT EVER AGAIN!
%
% allmudat with have (t,x,y,mu,wprl) for all tracked particles
%{
save([run 'allmudat.mat'],'allmudat','-v7.3');
clearvars -except run allmudat xmax ymax
%}
% NEXT TIME, JUST LOAD THE FILE USING THIS
%
%load([run 'allmudat.mat']);
%{
disp('registering collision events')
t = squeeze(allmudat(:,1,:));
x = squeeze(allmudat(:,2,:));
y = squeeze(allmudat(:,3,:));
mu = exp(squeeze(filter(1/16*ones(16,1),1,log(allmudat(:,4,:)))));
vprl = squeeze(filter(1/16*ones(16,1),1,allmudat(:,5,:)));
%
totalNlis = size(mu,2); %number of tracked particles

tauc = [];
xevent = [];
yevent = [];
tevent = [];
%}

ntbin = 100;			    % NUMBER OF BINS IN TIME
nxbin = 80;					% NUMBER OF BINS IN X
nybin = 20;					% NUMBER OF BINS IN Y
tBin  = linspace(min(min(t)),max(max(t)),ntbin); %array between absolute first and last events
xBin  = linspace(0,xmax,nxbin);
yBin  = linspace(0,ymax,nybin);
%{
fac = 1.2;	% FACTOR BY WHICH MU CHANGES TO REGISTER A "COLLISION"
tic
for nn = 1:totalNlis %iterate through particles
    jj = 1; 
    jjstore = jj;
    % Local vectors for each particle
    tloc = t(20:end,nn);tloc = tloc(tloc>0);% Remove initial rise and crap at the end
    xloc = x(tloc>0,nn);
    yloc = y(tloc>0,nn);
    muloc = mu(tloc>0,nn);
    tcurr = tloc(jj);
    while jj<length(tloc) %iterate through time looking for mu changes by fac
        mucurr = muloc(jj); %increase in mu       %decrease in mu
        jj = find(muloc(jj:end)>mucurr*fac | muloc(jj:end)<mucurr/fac,1)+jj-1;
        jjstore = [jjstore jj]; %append time mu changed
    end
    tauc = [tauc ; tloc(jjstore(2:end))-tloc(jjstore(1:end-1))]; %record collision deltat
    xevent = [xevent ; xloc(jjstore(2:end))]; %append collision locations (x,y,t)
    yevent = [yevent ; yloc(jjstore(2:end))];
    tevent = [tevent ; tloc(jjstore(2:end))];
end
xevent = mod(xevent,xmax);
yevent = mod(yevent,ymax);
%}
xG = (xBin(1:end-1) + xBin(2:end))/2; %bin centers
yG = (yBin(1:end-1) + yBin(2:end))/2;
tG = (tBin(1:end-1) + tBin(2:end))/2;
xN = length(xBin)-1;
yN = length(yBin)-1;
tN = length(tBin)-1;

disp('creating histogram')
%{
%t,x,ybin are bin edges
hstdata = cat(2,tevent,xevent,yevent);
[cntstemper,~,~,loc] = histcn(hstdata,tBin,xBin,yBin); %only tBin had something recorded at end
%need to shrink cntstemp by one in each dim after ensuring its tN+1 by xN+1 by yN+1
s = size(cntstemper);
cntstemp = zeros(tN+1,xN+1,yN+1);
cntstemp(1:s(1),1:s(2),1:s(3)) = cntstemper;
cnts = cntstemp(1:end-1,1:end-1,1:end-1);
cnts(1:end,1:end,end) = cnts(1:end,1:end,end)+cntstemp(1:end-1,1:end-1,end);
cnts(1:end,end,1:end) = cnts(1:end,end,1:end)+cntstemp(1:end-1,end,1:end-1);
cnts(end,1:end,1:end) = cnts(end,1:end,1:end)+cntstemp(end,1:end-1,1:end-1);
cnts(end,end,1:end) = cnts(end,end,1:end) + cntstemp(end,end,1:end-1);
cnts(end,1:end,end) = cnts(end,1:end,end) + cntstemp(end,1:end-1,end);
cnts(1:end,end,end) = cnts(1:end,end,end) + cntstemp(1:end-1,end,end);
cnts(end,end,end) = cnts(end,end,end) + cntstemp(end,end,end);
cnts = max(cnts,1);
bint = loc(:,1); binx = loc(:,2); biny = loc(:,3); %extract locations
%elements that don't fit in bins are forcefully placed in end bins (NaN, extra end bin, etc)
bint = min(max(bint,1),tN); 
binx = min(max(binx,1),xN);
biny = min(max(biny,1),yN);

relocs = cat(2,bint,binx,biny); %replace in MbyN matrix
collis = full(ndSparse.build(relocs,tauc,[tN,xN,yN]))./cnts; % mean of tauc in each bin
collis = 1./collis; %turn into frequency
collisn = collis;
collisn(cnts<50) = 0; %get rid of underpopulated bins - possibly anomalous
collisn = collisn*(log(fac)/log(exp(1)))^2; %scale the mu change by fac time to a change by e time

%}
% SAVE SO YOU DON'T HAVE TO DO THIS AGAIN
%
disp("saving data")
%save([run 'collisn.mat'],'collisn','tG','xG','yG','t','x','y','mu','vprl','tN','xN','yN','-v7.3');
%clearvars -except collisn tG xG yG t x y mu vprl run tN xN yN xmax
disp("generating plots")
%}
% NEXT TIME, JUST LOAD THE FILE USING THIS
%
load([run 'collisn.mat']);

%
% IF YOU WANT SPACE-TIME TO BE X-T, THEN...
%}
collisnr = collisn;
collisnr(1,:,:) = 0;
collisnkavg = zeros(tN,xN);
for i=1:tN
    for j=1:yN
        arr = squeeze(squeeze(collisnr(i,:,j)));
        collisnkavg(i,:) = collisnkavg(i,:)+circshift(arr,4*j); %stays as 4 due to number of bins
    end
end
collisnkavg = collisnkavg/yN;
nu = mean(collisnkavg,2); t = tG;
numax = max(collisnkavg,[],2);
numin = min(collisnkavg,[],2);
%}
figure('Renderer', 'painters', 'Position', [10 10 280 240])
set(groot,'defaultAxesTickLabelInterpreter','latex');
set(groot,'defaultLegendInterpreter','latex');
beta = 16; ft=9;
load('whitebluered.mat')
set(gca,'DefaultFigureColor',[1 1 1])
set(gca,'FontSize',ft)
collisn(1,:) = 0;
collisnkavg(1,:) = 0;
imagesc(t*2*pi/xmax*sqrt(16), xG/sqrt(16), collisnkavg'*xmax/2/pi/sqrt(16)); shading flat; axis xy;
%set(gca, 'FontName', 'Serif','FontSize',ft)
scale = 0.2;
pos = get(gca, 'Position');
pos(2) = pos(2)+0.3*scale*pos(4);
pos(4) = 0.9*(1-scale)*pos(4);
pos(1) = pos(1)+0.5*scale*pos(3);
pos(3) = (1-0.2*scale)*pos(3);
set(gca, 'Position', pos)
colormap(myCustomColormap)
ylabel({'$x \; (\rho_\mathrm{i})$'}, 'Interpreter', 'latex', 'FontSize', ft)
xlabel({'$k_{||}v_{\mathrm{th,i}}t$'}, 'Interpreter', 'latex', 'FontSize', ft)
a=colorbar;
a.Label.String = {'$\langle \nu_{\mathrm{eff}} \rangle _k \; (k_{||}v_{\mathrm{th,i}})$'};
a.FontSize = ft+1;
a.Label.FontSize = ft;
a.Label.Interpreter = 'latex';
a.TickDirection = 'out';
a.Location = 'northoutside';
set(a,'TickLabelInterpreter','latex')
scale = 0.2;
pos = get(a, 'Position');
pos(2) = pos(2)+30*scale*pos(4);
pos(4) = 0.8*(1-scale)*pos(4);
set(a, 'Position', pos)

%savefig("../nuxt_big.fig")

figure('Renderer', 'painters', 'Position', [10 10 280 240])
set(gca,'DefaultFigureColor',[1 1 1])
%set(gca, 'FontName', 'Serif','FontSize',ft)
set(gca,'FontSize',ft)
n1 = "$\langle \nu_\mathrm{eff} \rangle$";
semilogy(t*2*pi/xmax*sqrt(beta),nu*xmax/2/pi/sqrt(beta), 'k-', 'LineWidth', 1.5);
hold on
n2 = "$\langle \nu_\mathrm{eff} \rangle _k$";
semilogy(t*2*pi/xmax*sqrt(beta),max(collisnkavg,[],2)*xmax/2/pi/sqrt(beta), 'r-', 'LineWidth', 1.5);
xlabel({'$k_{||}v_{\mathrm{th,i}}t$'}, 'Interpreter', 'latex', 'FontSize', ft)
ylabel({'$\nu_{\mathrm{eff}} \; (k_{||}v_{\mathrm{th,i}})$'}, 'Interpreter', 'latex', 'FontSize', ft);
set(gca, 'FontName', 'Serif')
%ylim([9e-3 1.5])
%xlim([0 27])
leg = legend(gca,{'$\langle \nu_{\mathrm{eff}} \rangle $','$\mathrm{max}(\langle \nu_{\mathrm{eff}} \rangle _k)$'});
set(leg, 'Interpreter', 'latex')
set(leg, 'FontSize',ft)
set(leg, 'Location', 'southeast')
legend boxoff
%}
%savefig("../nut_big.fig")
numax = max(nu)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%function to get indices needed to remove restart crap
function [startskips, endskips] = restartRemove(time)

    %get indices and times of all skips
    iskips = [];
    tskips = [];
    for i=1:length(time)-1
        if time(i+1)<time(i)
            iskips = [iskips; i+1];
            tskips = [tskips; time(i+1)];
        end
    end

    %remove multiple skips to same time
    tskipfilt = unique(tskips);
    iskipfilt = zeros(1,length(tskipfilt));
    for i=1:length(tskipfilt)
        x = find(tskips == tskipfilt(i));
        iskipfilt(i) = max(x);
    end

    %indices to end jump from
    endskips = zeros(1,length(iskipfilt));
    for i=1:length(iskipfilt)
        endskips(i) = iskips(iskipfilt(i));
    end
    
    %indices to start jump from
    startskips = zeros(1,length(endskips));
    for i=1:length(startskips)
        for j=1:length(time)
            if time(j) == tskipfilt(i)
                startskips(i) = j-1;
                break
            end
        end
    end
end
