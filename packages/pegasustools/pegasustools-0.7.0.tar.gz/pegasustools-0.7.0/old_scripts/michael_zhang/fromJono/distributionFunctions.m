function distributionFunctions

name = 'half_tcorr_sim9';

P.npec_prl = [400 400 400];
P.npec_prp = [200 200 200];
P.vprpmax = [4 4 4];
P.vprlmax = [4 4 4];
P.beta=0.3; % All thermal velocities normalized to sqrt(beta)
P.computerms = 1;
vthp = sqrt(P.beta);
qom = [1 5/16 1/2];
mass = [1 16 4];
vthi = vthp./sqrt(mass);
species = 3;

vol=6*48.1802^3;
tauA = 6*48.1802;
ppc = 1000;
ncells = 6*280^3; nmesh = 24*20*14;
nprtl = ncells*ppc;
epsin = 12.9;%36.5;
nrm = epsin*nprtl/vol; % With this sum(sum(edv_prp)) seems to match (as much as possible) d_t Eprp/epsin. 
% See compareHeatingDiagnostics.m
if strcmp(name,'lev')
    vol=6*34.4144^3;ncells = 6*200^3;nprtl = ncells*ppc;
    epsin = 9.52;nrm = epsin*nprtl/vol;tauA=206.4865395;
end
nrmdfdt = nrm;
nrm = nrm./(P.npec_prp./P.vprpmax).^2; % Since there are 50 points per vth

computer = 'tigress';
DoFullCalculation =1;
loadsave = 0;
sortnums = 0;
copyViaScp=0;
%nums = [0:52 ]; % snapshot numbers for which to find spectrum
% already saved 0:39?
nums = [0:76];%[76]

tstrt = 1;
plotvar = 0;
plotHeat = 0;
plotHeatAllTogether = 0; % 1D versions all on one plot
plotHeat2 = 1;
plotHeatFromF = 0;
plotF =   0;
plotDprp = 0;
plotDprpFromF = 0; % Same as figure for nature paper
prlBeam = 0;
loadAvf0 = 0; % To get f0 from the AvDF file instead. Annoying, but I didn't copy over some of it


n2s = @(s) num2str(s);
[readF,files_all,folder,filenamespec] = chooseComputerAndFiles(name,computer);

savebase = [ './saved-analysis/'];
savefolder = [ savebase 'averageDFsnew-' name '.mat'];
%savefolder = [ savebase 'DFs-rms-' name '.mat'];

disp(['Saving/loading from ' savefolder])


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



tas = nums*0.2;
t = dat(:,1);
is = restart_overlaps2(t);

dt = dat(:,2);
dthst = diff(t);dthst = [ dthst(1);dthst ];


t=t(is)/tauA;
vthpp = {};
vthpl = {};
vthtot = {}
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

disp('hello')
disp(t-tas<0.5/tauA)
disp(find(t-tas<0.5/tauA,1))

numinds = [];
for i = 1:length(tas)
  numinds = [numinds find(t-tas(i)>0.5/tauA,1)];
end

disp(numinds)

for i = 1:length(mass)
    vthpp{i} = vthpp{i}(numinds);
    vthpl{i} = vthpl{i}(numinds);
    vthtot{i} = vthtot{i}(numinds);
end




if DoFullCalculation



fields = {'f0','edv_prp','edv_prl','t','nums','f0_rms'};

for var = fields;F.(var{1}) = [];end
F.f0 = {};
F.edv_prp = {};
F.edv_prl = {};
F.f0_rms = {};
for i = 1:length(P.vprpmax)
    F.f0{i} = [];
    F.edv_prp{i} = [];
    F.edv_prl{i} = [];
    F.f0_rms{i} = [];
end
F.vprp = {};
F.vprl = {};

% to reload some F if already have some saved snapshots
if loadsave
 load(savefolder,'F');
 F
 disp(F.nums)
end
for nnn=nums
    [readF,files_all,folder,filenamespec] = chooseComputerAndFiles(name,computer);
    try 
        disp(['Doing ' folder ' nnn = ' num2str(nnn)])
        F1 = readSpecMPIIO(filenamespec(nnn),'f0',struct(),P);
        P.computerms=0;
        F1 = readSpecMPIIO(filenamespec(nnn),'edv_prp',F1,P);
        F1 = readSpecMPIIO(filenamespec(nnn),'edv_prl',F1,P);
        P.computerms=1;
%         F1 = readSpecMPIIO(filenamespec(nnn),'f0',F1,P);
    catch 
        warning(['Did not find ' filenamespec(nnn)])
        continue
    end
    

    F.t = [F.t F1.t];
    F.nums = [F.nums nnn];
    %F.vprp = F1.vprp;
    %F.vprl = F1.vprl;
    F.n = length(F.t);
    for i = 1:length(P.vprpmax)
      F.f0{i} = cat(3,F.f0{i},F1.f0{i});
      F.edv_prp{i} = cat(3,F.edv_prp{i},F1.edv_prp{i});
      F.edv_prl{i} = cat(3,F.edv_prl{i},F1.edv_prl{i});
      F.f0_rms{i} = cat(3,F.f0_rms{i},F1.f0_rms{i});
      F.vprp{i} = F1.vprp{i}
      F.vprl{i} = F1.vprl{i}
    end

    disp("saving F")
    disp(savefolder)
    save(savefolder,'F','P');
    disp("saved F")
    %
end
else % DoFullCalculation
    load(savefolder,'F');
    disp(F)
    disp(F.nums)
end

if sortnums
    [F.nums,sortinds] = sort(F.nums);
    F.t = F.t(sortinds);
    for j = 1:length(P.vprpmax)
        F.f0{j} = F.f0{j}(:,:,sortinds(2));
        F.edv_prp{j} = F.edv_prp{j}(:,:,sortinds);
        F.edv_prl{j} = F.edv_prl{j}(:,:,sortinds);
    end
    save(savefolder,'F','P');
end
disp(F.nums)
disp(F.t)


F.n = length(F.t);
% 1-D vs. time plots
% % Heating
% s2= @(f) squeeze(sum(sum(f,2),1));
% nprtl = 216*392^3*6;
% plot(F.t,s2(F.f0)/nprtl)

F.t = F.t/tauA;
tstrt = find(F.t>tstrt,1);
dn=2;





if plotvar
    
% NOTE:
%   plotf0 is normalized such that 
%             SUM[ plotf0*(dvprp/vth0)*(dvprl/vth0) ] = 1
%   actual VDF = plotf0 / (vprp/vth0) * [n/(2*pi*vth0^3)]
%   looks like we've been setting pi*vth0^2 = 1 in our plotting of f(vprp),
%   so that the Maxwellian f(vprp) = exp(-vprp^2/vth^2), so the def'n of
%   f(vprp) = pi vthprp^2 int[ f dvprl ] 
%           = (vthprp/vth0)^2 int[ 0.5*plotf0*(dvprl/vth0)*(vth0/vprp)
%   
    spec =1;
    rebinN  = 250;
    logfmin = -7.5; logfmax = -0.5;

    vmaxarr = { 10,20,20 };
    vmaxplt = { 6,8.5,14 };
    
    figure(13); clf; pwidth=18.5; pheight=12;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')

    width = 5.15/pwidth; height=0.5*(pwidth/pheight)*width; gap = 0.007; offset = 0.0038*pwidth;
    normpos = { [offset,0.74,width,height],[offset+gap+width,0.74,width,height],[offset+(gap+width)*2,0.74,width,height], ...
                [offset,0.42,width,height],[offset+gap+width,0.42,width,height],[offset+(gap+width)*2,0.42,width,height], ...
                [offset,0.10,width,height],[offset+gap+width,0.10,width,height],[offset+(gap+width)*2,0.10,width,height] };
    cbpos   = [0.933 0.10 0.0157 0.855];
    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$','$w_\|/v_{\rm th,O^{6+}0}$','$w_\|/v_{\rm th,C^{6+}0}$','$w_\|/v_{\rm th,C^{5+}0}$','$w_\|/v_{\rm th,Mg^{9+}0}$'};
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,i 0}$','$w_\perp/v_{\rm th,i0}$' };
    %tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };
    levels  = { -0.40:1.2:11.5, -0.4:0.4:5.6, -0.4:0.4:3.8, -0.4:0.4:5.6, -0.4:0.4:5.6, -0.4:0.4:5.6, -0.4:0.4:5.6 };
    tposx   = [-4.1,-6.9,-12.5];
    tposxb  = [2.1,4.1,8];
    tposy   = [5.25,7.45,12];
    pick    = [1,3,3];
    splab = {'$i={\rm p}$','$i={\rm \alpha}$','$i={\rm O^{5+}}$','$i={\rm O^{6+}}$','$i={\rm C^{6+}}$','$i={\rm C^{5+}}$','$i={\rm Mg^{9+}}$'}





    m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);
    m3 = @(d,t,tav) mean(d(:,find(t>=tav(1) & t<=tav(2))),2);
    m4 = @(d,t,tav) mean(d(find(t>=tav(1) & t<=tav(2))),1);


    tplt = [15.0];
    dtplt = 0.5;
    tavplt = [tplt-dtplt;tplt+dtplt];
    tav = F.t;
    for ttt = 1:length(tplt)
        for i = 1:length(mass)
            vprl{i} = m(F.vprl{i},tav,tavplt(:,ttt)); % should be same for all times if unscaled
            vprp{i} = m(F.vprp{i},tav,tavplt(:,ttt));
        end
        
    vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
    vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
    [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
    normf0 = int_dist(m(F.vprl{i},tav,tavplt(:,ttt)),m(F.vprp{i},tav,tavplt(:,ttt)),m(F.f0{i},tav,tavplt(:,ttt)));
    f0 = m(F.f0{spec},tav,tavplt(:,ttt))./ normf0;
    f0 = f0./vpn'/2;
    f0rms = m(F.f0_rms{spec},tav,tavplt(:,ttt))./ normf0;
    f0rms = f0rms./vpn'/2;
    size(f0)
    size(vprl{spec})
    size(vprp{spec})
    %f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q;
    %f0q = interp2(vln,vpn,f0rms',vlq,vpq); f0rms = f0q;
    liminds = find(log10(f0)<logfmin); f0(liminds) = 0;
    contourf(vprl{spec}(1,:),vprp{spec},log10(f0rms'./f0'),logfmin:0.5:logfmax);
    C = caxis; caxis([-3 0])%caxis([logfmin,logfmax]);
    axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
    set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    %set(gca,'Units','normalized','Position',normpos{spec});
    xlabel(xlab{spec},'interpreter','latex');
    text(-5.1,4.9,splab{spec},'Fontsize',10);
    ylabel(ylab{spec},'interpreter','latex');
    plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.01);


    cb = colorbar;
    title(cb,'$\langle f_i\rangle $','interpreter','latex');
    set(cb,'Position',cbpos,'Ticklength',0.01);
    %set(cb,'Position',cbpos{spec},'Ticklength',0.04);
    cb.Ticks=[-3 -2 -1 0];
    cb.TickLabels={'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^{0}$'};
    cb.TickLabelInterpreter='latex';
    cb.FontSize=10; cb.LineWidth=1;
    end
end  % plotnbr==3





% init from imbal2-prod
heatip = {};
heatil = {};
for i = 1:length(P.vprpmax)
   heatip{i} = mean(F.edv_prp{i}(:,:,1:5),3);
   heatil{i} = mean(F.edv_prl{i}(:,:,1:5),3);
end
% save('saved-analysis/initDR-imbal2-prod.mat','heatip','heatil');
%load('saved-analysis/initDR-imbal2-prod.mat','heatip','heatil');

dn = 4;
if plotHeat
%     nrm=1;
    i = species;
    F.edv_prp{i} = (F.edv_prp{i}-heatip{i})/nrm(i); % vprp because histogram gives vprp*F
    F.edv_prl{i} = (F.edv_prl{i}-heatil{i})/nrm(i);

    pnums = [2 3];
    
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp.^2.*F.f0;
        eprl = 0.5.*(F.vprl.').^2.*F.f0;
        F.edv_prp = grad3(eprp,F.t)/nrmdfdt;
        F.edv_prl = grad3(eprl,F.t)/nrmdfdt;
        clear eprp eprl
    end
    prpmax = 1;max(max(max(F.edv_prp{i})))/5;
    prlmax = 0.05;max(max(max(F.edv_prl{i})))/2;

    
    for n=dn:dn+1:F.n-dn; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);
%         m = @(d) mean(d(:,:,tstrt:end),3);
    figure(pnums(1))
    subplot(211)
    imagesc(F.vprl{i},F.vprp{i},m(F.edv_prp{i}).');set(gca,'YDir','normal')
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$w_\perp$','interpreter','latex')
    title('$Q_\perp$','interpreter','latex')
    prpmax = 0.8*max(max(max(m(F.edv_prp{i}))));
	clim(prpmax*[-1 1])
    colormap jet;colorbar 
    subplot(212)
    imagesc(F.vprl{i},F.vprp{i},m(F.edv_prl{i}).');set(gca,'YDir','normal')
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$w_\perp$','interpreter','latex')
    title('$Q_\|$','interpreter','latex')
    prlmax = 0.8*max(max(max(m(F.edv_prl{i}))));
    clim(prlmax*[-1 1])
    colormap jet;colorbar 
    subplot(211)
    figure(pnums(2))
    subplot(211)
    plot(F.vprl{i},sum(m(F.edv_prl{i}),2),F.vprl{i},sum(m(F.edv_prp{i}),2))%, F.vprl,sum(F.edv_prp(:,:,1),2),'k--')
    xlabel('$w_\|$','interpreter','latex')
%     ylim([-50000 100000])
    subplot(212)
    semilogx(F.vprp{i},sum(m(F.edv_prl{i}),1),F.vprp{i},sum(m(F.edv_prp{i}),1))%, F.vprp,sum(F.edv_prp(:,:,1),1),'k--')
    xlim([0.1 4])
    xlabel('$w_\perp$','interpreter','latex')
    legend({'$Q_\|$','$Q_\perp$'},'interpreter','latex')
%     ylim(2e4*[-1 1])
    figure(pnums(1))
    set(gcf,'Color','w')
    title(['$t=' n2s(F.t(n-dn+1)) '$ to $t=' n2s(F.t(n+dn)) '$']);drawnow;end%ginput(1);end
end

dn=4;
if plotHeatAllTogether
%     nrm=1;
    F.edv_prp{i} = (F.edv_prp{i}-heatip{i})/nrm(i); % vprp because histogram gives vprp*F
    F.edv_prl{i} = (F.edv_prl{i}-heatil{i})/nrm(i);
    pnums = [2 3];
    
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp.^2.*F.f0;
        eprl = 0.5.*(F.vprl.').^2.*F.f0;
        F.edv_prp = grad3(eprp,F.t)/nrmdfdt;
        F.edv_prl = grad3(eprl,F.t)/nrmdfdt;
        clear eprp eprl
    end
    prpmax = 1;max(max(max(F.edv_prp{i})))/5;
    prlmax = 0.05;max(max(max(F.edv_prl{i})))/2;
    
    smooth = @(f) filter((1/5)*ones(1,5),1,f); 
    for n=[dn:dn+1:F.n-dn F.n-dn]; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);
%         m = @(d) mean(d(:,:,tstrt:end),3);
    figure(pnums(2))
    subplot(411)
    semilogx(F.vprp{i},smooth(sum(m(F.edv_prp{i}),1)),'Color',tcol(F.t(n)))
    xlabel('$w_\perp$','interpreter','latex')
    ylabel('$Q_\perp$','Interpreter','latex')
    xlim([0.1 4])
    title(['$t=' num2str(F.t(n)) '$'],'Interpreter','latex')
    hold on
    subplot(412)
    semilogx(F.vprp{i},sum(m(F.edv_prl{i}),1),'Color',tcol(F.t(n)))
    xlabel('$w_\perp$','interpreter','latex')
    ylabel('$Q_\|$','Interpreter','latex')
    xlim([0.1 4])
    hold on
    subplot(413)
    plot(F.vprl{i},sum(m(F.edv_prp{i}),2),'Color',tcol(F.t(n)))
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$Q_\perp$','Interpreter','latex')
    hold on
    subplot(414)
    plot(F.vprl{i},sum(m(F.edv_prl{i}),2),'Color',tcol(F.t(n)))
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$Q_\|$','Interpreter','latex')
    hold on
    drawnow;ginput(1);end
end

if plotF
    figure;set(gcf,'Color','white');
    betaplot = 1; % vprp vprl are in units of thermal velocity
    for n=tstrt:dn:F.n-1; m = @(d) mean(d(:,:,n-dn:n+dn),3);
        f0 = m(F.f0)./ int_dist(F.vprl,F.vprp,m(F.f0));
    subplot(311)
    vprpn = F.vprp;
    contourf(F.vprl,F.vprp,log10(f0./vprpn).',15);set(gca,'YDir','normal')
    [out,outva,vprlhalf] = resonanceContours(F.vprp,F.vprl);
    hold on;contour(vprlhalf,F.vprp,out.',4:3:35,'k--','Linewidth',1); %contour(vprlhalf,F.vprp,outva.',4:2:28,'k:')
    colorbar;caxis([-9 -0.5])
    title(['$t=' n2s(F.t(n-dn)) '$ to $t=' n2s(F.t(n+dn)) '$'])
    xlabel('$w_\|$','interpreter','latex')
    ylabel('$w_\perp$','interpreter','latex')
    subplot(312)
    fprl = trapz(F.vprp,f0,2);
    loglog(F.vprl.^2,fprl,F.vprl,1/sqrt(pi*betaplot)*exp(-F.vprl.^2/betaplot),'--')
    xlabel('$w_\|$','interpreter','latex')
    hold on;plot(-1*[1 1],1e10*[-1 1],'k:',1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:',-1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
    ylim(1*[-0. 0.6])
    subplot(313)
    fprp = trapz(F.vprl,f0,1)./F.vprp/2;
    loglog(F.vprp.^2,fprp,F.vprp,0.5*4*betaplot^-1.5/sqrt(pi).*exp(-F.vprp.^2/betaplot),'--')
    xlabel('$w_\perp$','interpreter','latex')
    hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
    ylim(1.2*[0 1])
    xlim([0.1 4])
    subplot(311)
    title(['$t=' n2s(F.t(n-dn)) '$ to $t=' n2s(F.t(n+dn)) '$']);
    ginput(1);end


end

if prlBeam
    % examime if df/dt is consistent with parallel beam
    % Assume d(wl^2 f)/dt = dQl/dwl, and see how they match up
    eprl = 0.5.*(F.vprl.').^2.*F.f0;
    dqprl= grad3(eprl,F.t)/nrmdfdt;
    dqprl = squeeze(sum(dqprl,2));
    dedvprl = squeeze(sum(F.edv_prl/nrm,2));
    dvprp = 1/50;
    
    figure;set(gcf,'Color','white');
    for n= tstrt:10:F.n-1
        m = @(d) mean(d(:,n-5:n+5)*dvprp,2);
        plot(F.vprl,m(dqprl),'-',F.vprl,m(dedvprl),'-','Linewidth',1)%'Color',tcol(F.t(n)),
        hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:',...
            -1*[1 1],1e10*[-1 1],'k:',-1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
        title(['$t=' n2s(F.t(n-5)) '$ to $t=' n2s(F.t(n+5)) '$']);
        legend({'$d(e_\| f)/dt$','$E_\|\cdot v_\|$'})
        ylabel('$dQ_\|/dw_\|$')
        xlabel('$w_\|$')
        ylim([-1 1]*max(m(dqprl))*1.2)
        drawnow;ginput(1);
    end
    

        
    
end

if loadAvf0
    % Didn't copy over f0 so, get from average ones
    Fa = load([ savebase 'AvDFs-' name '.mat']);
    Fa = Fa.F;
    P.nspec_prlav = 600; P.nspec_prpav = 300;
    P.savemid = 200;
    vprlst = P.nspec_prlav/2-P.savemid+1 ; vprlend = P.nspec_prlav/2+P.savemid;
    tav = Fa.t/tauA;
    f0a = Fa.f0(vprlst:vprlend,1:P.savemid,:);
else
    tav = F.t;
    f0a = F.f0;
end

m = @(d,t,tav) mean(d(:,:,find(t>=tav(1) & t<=tav(2))),3);

tplt = [1  5  9  13  17]+18.2;
dtplt = 2;
tavplt = [tplt-dtplt;tplt+dtplt];

if plotDprp
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp.^2.*F.f0;
        eprl = 0.5.*(F.vprl.').^2.*F.f0;
        F.edv_prp = grad3(eprp,F.t)/nrmdfdt;
        F.edv_prl = grad3(eprl,F.t)/nrmdfdt;
        clear eprp eprl
        pnums = [6 7];
    end
    % heatip = mean(F.edv_prp(:,:,1:2),3);
    % F.edv_prp = (F.edv_prp-heatip)/nrm;
    figure(6)
    filt = @(f) filter((1/10)*ones(1,10),1,f);
    lnm={};
    % Perpendicular diffusion coefficient
    for ttt = 1:length(tplt)
        f0 = m(f0a,tav,tavplt(:,ttt))./ int_dist(F.vprl,F.vprp,m(f0a,tav,tavplt(:,ttt)));
        fprp = trapz(F.vprl,f0,1)./F.vprp/2;
        dfprp = gradient(fprp,F.vprp(2)-F.vprp(1))/vthi;
        dqprp = sum(m(F.edv_prp,F.t,tavplt(:,ttt)),1);
        % subplot(311)
        % semilogx(F.vprp,fprp)
        % ylabel('$f$','Interpreter','latex')
        % subplot(312)
        Dpp = -filt(dqprp./dfprp)/(epsin*P.beta);
        loglog(F.vprp,Dpp,'-',F.vprp,-Dpp,'--','Color',tcol(tplt(ttt)),'LineWidth',1)
        hold on;
        loglog(F.vprp, 200*F.vprp.^2,'k:');hold off
        xlim([0.1 4])
        ylim([1 2e3])
        ylabel('$D_\perp$','Interpreter','latex')
        hold on
    %     subplot(313)
    %     semilogx(F.vprp,dqprp)
    % %     hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
    %     xlim([0.1 4])
    %     ylabel('$q_\perp$','Interpreter','latex')
    %     subplot(311);title(['t=' num2str(tplt(ttt))]);ginput(1);
        drawnow
    end
   
end



if plotDprpFromF

    vresltn =50;
    % Compute Dpp from dfdt = d/de(Dpp dfde). Same as Figure_FandDprp
    wp = F.vprp.';
    wp(1)=1e-4;
    prlrang = F.vprl>0.5*(3-sqrt(5))/sqrt(0.3); % Changing the number here changes the sh
    smprl = @(f) squeeze(sum(f(prlrang,:,:),1));
    smprlall = @(f) squeeze(sum(f(:,:,:),1));
    nrmf = 1./F.vprp;nrmf(1)=1e-4;
    fE = smprl(nrmf.*F.f0/nprtl);
    fEall = smprlall(nrmf.*F.f0/nprtl);
    dfdt = grad3(nrmf.*F.f0,F.t)/nrmdfdt;
    dfEdt = smprl(dfdt);
    dfEdtall = smprlall(dfdt);
    dfdw = dbydw(fE,wp);
    dfdwall = dbydw(fEall,wp);
    
    % This is A1 from Cerri
    Dpp = cumtrapz(wp,wp.*dfEdt,1)./(1./wp.*dfdw)/vresltn;
    DppAll = cumtrapz(wp,wp.*dfEdtall,1)./(1./wp.*dfdwall)/vresltn;
    % This is Cerri A8 from Vasquez
    dQ = wp.^2.*dfEdt;
    dQall = wp.^2.*dfEdtall;

    figure(5)
    % Perpendicular diffusion coefficient
    for n=tstrt+dn+1:(dn+1):F.n; m = @(d) mean(d(:,n-dn:n+dn),2);
    subplot(311)
    semilogx(F.vprp,m(fE),'k',F.vprp,m(fEall),'r')
    ylabel('$f$','Interpreter','latex')
    xlim([0.05 4])
    subplot(312)
    loglog(F.vprp,m(Dpp),'k',F.vprp,-m(Dpp),'k--',F.vprp,20*F.vprp.^2,'k:')
    hold on
    loglog(F.vprp,m(DppAll),'r',F.vprp,-m(DppAll),'r--')
    hold off
    xlim([0.05 4])
    ylim([1e-2 2e2])
    ylabel('$D_\perp$','Interpreter','latex')
    subplot(313)
    semilogx(F.vprp,m(dQ),'k',F.vprp,m(dQall),'r',F.vprp,0*F.vprp,'k:')
%     hold on;semilogx(1*[1 1],1e10*[-1 1],'k:',1/sqrt(P.beta)*[1 1],1e10*[-1 1],'k:');hold off
    xlim([0.05 4])
    ylabel('$q_\perp$','Interpreter','latex')
    subplot(311);title(['t=' num2str(F.t(n+1))]);ginput(1);end
        
end



dn=4;
if plotHeat2
%     nrm=1;
for i = 1:length(mass)
    F.edv_prp{i} = (F.edv_prp{i}-heatip{i})/nrm(i); % vprp because histogram gives vprp*F
    F.edv_prl{i} = (F.edv_prl{i}-heatil{i})/nrm(i);
end

    pnums = [2 3];
for i = 1:length(mass)
    pnums = [2 3];

    if i ==1
        dir = ['../simulations/' name '/saved-plots/edotw/p/'];
        xlab = '$w_\|/v_{th0,p}$'
        ylab = '$w_\perp/v_{th0,p}$'
    end
    if i ==2
        dir = ['../simulations/' name '/saved-plots/edotw/o5/'];
        xlab = '$w_\|/v_{th0,O^{5+}}$'
        ylab = '$w_\perp/v_{th0,O^{5+}}$'
    end
    if i ==3
        dir = ['../simulations/' name '/saved-plots/edotw/he/'];
        xlab = '$w_\|/v_{th0,He^{++}}$'
        ylab = '$w_\perp/v_{th0,He^{++}}$'
    end
    if plotHeatFromF
        % Uses time derivative of F to compute perp and parallel heating
        eprp = 0.5.*F.vprp.^2.*F.f0;
        eprl = 0.5.*(F.vprl.').^2.*F.f0;
        %output from spectrum.cpp computes E.w/v_A, and bins it according
        %to w/vthi0... So want these vprp and vprl here to be unscaled. Can
        %then scale axes how you want, knowing that the values of the plot
        %are in terms of alfven speed. Or can also rescale that according
        %to vth or current vth, but could be confusing/non intuitive to have a changing
        %color scale
        F.edv_prp{i} = grad3(eprp,F.t)/nrmdfdt;
        F.edv_prl{i} = grad3(eprl,F.t)/nrmdfdt;
        clear eprp eprl
    end
    prpmax = 1;max(max(max(F.edv_prp{i})))/5;
    prlmax = 0.05;max(max(max(F.edv_prl{i})))/2;

    nplt = [15]%[235:10:435];
    for n=nplt; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);%n=dn:dn+1:F.n-dn; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);
        m4 = @(d) mean(d(n-dn+1:n+dn),1);
        m3 = @(d) mean(d(:,n-dn+1:n+dn),2);
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
          foutlab = [dir,'specfp.',numlab,'.png'];
          exportname = [dir,'pdf/specfp.',numlab,'.pdf'];
        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(i),mass(i),P.beta,2,4);
        %cvprl = cvprl./m4(vthtot{i});
        %cvprp = cvprp./m4(vthtot{i});
        %if unscalew
        %    cvprl = cvprl.*m4(vthtot{i});
        %    cvprp = cvprp.*m4(vthtot{i});
        %end
        if i==1
            levels = -0.4:1.2:11.6;%0.8:1:8.8;
        end

        if i == 2
            levels = -0.4:0.4:2.8;
        end
        if i == 3
            levels = -0.4:0.4:5.6;
        end

    figure(pnums(1));set(gcf,'Color','white');
    subplot(211)
    imagesc(F.vprl{i},F.vprp{i},m(F.edv_prp{i}).');set(gca,'YDir','normal')
    prpmax = 0.8*max(max(max(m(F.edv_prp{i}))));
	clim(prpmax*[-1 1])
        hold on;contour(cvprl,cvprp,out.',levels,'k--','Linewidth',1);
    % vertical line at v_A

        %plot(-1 /vthi(i) *[1 1], [0 20],'r--')
        % vertical line at vth_par
        plot(- m4(vthpl{i}) *[1 1], [0 20],'-.','Color',[0.4940 0.1840 0.5560])
        % horizontal line at vth_perp
        plot([-20 20], [1 1] .* m4(vthpp{i}),'m--')

    xlabel(xlab,'interpreter','latex')
    ylabel(ylab,'interpreter','latex')



    set(gca,'fontsize', 16);
    legend({'','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')
    %title(['$t/\tau_{A}=' n2s(F.t(n-dn+1)) '$t/\tau_{A}=' n2s(F.t(n+dn)) '$']);


    %axis equal
    colormap jet;colorbar 
    hold off
    subplot(212)
    imagesc(F.vprl{i},F.vprp{i},m(F.edv_prl{i}).');set(gca,'YDir','normal')
    xlabel(xlab,'interpreter','latex')
    ylabel(ylab,'interpreter','latex')
    title('$\partial Q_\parallel/\partial w_{\perp} \partial w_{\parallel}$','interpreter','latex')
    prlmax = 0.8*max(max(max(m(F.edv_prl{i}))));
    clim(prlmax*[-1 1])

        hold on;
    % vertical line at v_A

        plot(-1 /vthi(i) *[1 1], [0 20],'r--')
        % vertical line at vth_par
        plot(- m4(vthpl{i}) *[1 1], [0 20],'-.','Color',[0.4940 0.1840 0.5560])
        % horizontal line at vth_perp
        plot([-20 20], [1 1] .* m4(vthpp{i}),'m--')



    set(gca,'fontsize', 16);
    legend({'$v_{A}$','$v_{th\|}$','$v_{th\perp}$'},'interpreter','latex')

    colormap jet;colorbar 
    hold off
    subplot(211)
    figure(pnums(2))
    subplot(211)
    plot(F.vprl{i},sum(m(F.edv_prl{i}),2),F.vprl{i},sum(m(F.edv_prp{i}),2))%, F.vprl,sum(F.edv_prp(:,:,1),2),'k--')
    xlabel('$w_\|$','interpreter','latex')
%     ylim([-50000 100000])
    subplot(212)
    semilogx(F.vprp{i},sum(m(F.edv_prl{i}),1),F.vprp{i},sum(m(F.edv_prp{i}),1))%, F.vprp,sum(F.edv_prp(:,:,1),1),'k--')
    xlim([0.1 4])
    xlabel('$w_\perp$','interpreter','latex')
    legend({'$Q_\|$','$Q_\perp$'},'interpreter','latex')
%     ylim(2e4*[-1 1])
    figure(pnums(1))
    set(gcf,'Color','w')
    %title(['$t=' n2s(F.t(n-dn+1)) '$ to $t=' n2s(F.t(n+dn)) '$']);
    %title('$Q_\perp$','interpreter','latex')
    title([ '$t/\tau_{A}=' n2s(round(m3(F.t),2)) '\quad \partial Q_\perp/\partial w_{\perp} \partial w_{\parallel}$'],'interpreter','latex');
    set(gca,'fontsize', 16);
    drawnow;%ginput(1);end%pause(0.2);end


      fig = gcf;
      fig.PaperPositionMode = 'auto';
      print(foutlab,'-dpng','-r0');
      exportgraphics(fig,exportname,'ContentType','vector')
    end

    end
end
end

function  out = int_dist(vprl,vprp,F)

out = trapz(vprl,trapz(vprp,F,2),1);

end

function out = grad3(fld,tv)
% Time derivative in 3 direction
nt = length(tv);
out = zeros(size(fld));
out(:,:,1)= (fld(:,:,2)-fld(:,:,1))/(tv(2)-tv(1));
for nn = 2:nt-1
    out(:,:,nn) = (fld(:,:,nn+1)-fld(:,:,nn-1))/(tv(nn+1)-tv(nn-1));
end
out(:,:,nt)= (fld(:,:,nt)-fld(:,:,nt-1))/(tv(nt)-tv(nt-1));

end

function df = dbydw(f,w)
% gradient function is shit ? do a loop
dw = w(11)-w(10);
df = zeros(size(f));
for nnn=1:size(f,2)
    df(:,nnn) = gradient(f(:,nnn),dw);
end

end

function [out,outva,vprlhalf] = resonanceContours(vprp,vprl)
% See IC Resonance Conditions.nb notebook

vprl = vprl(vprl>0.01);
vprlhalf = vprl;
[vl,vp]=ndgrid(vprl,vprp);
% This is non-dispersive version, propagating at vA
outva = vl.^2+0.365148E1.*(0.182574E1+vl)+vp.^2;
% This is dispersive cold IC resonance at beta=0.3 
out = (0.182574E1.*(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*(0.2E2.* ...
  vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^( ...
  1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(-1/3)+ ...
  0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)) ...
  .^(-1)+0.912871E0.*(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*( ...
  0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+ ...
  3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^( ...
  -1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)+(-1).*(4+(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*( ...
  0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+ ...
  3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^( ...
  -1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)).^2).^(1/2))).^2+vp.^2+(-0.166667E1).*((0.182574E0.*vl+( ...
  -0.230029E0).*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+ ...
  (-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+( ...
  -0.148148E3).*vl.^6).^(1/2)).^(-1/3)+0.144909E0.*vl.^(-1).*( ...
  0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)).^2+((-0.182574E0).*vl+ ...
  0.230029E0.*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+( ...
  -0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+( ...
  -0.148148E3).*vl.^6).^(1/2)).^(-1/3)+(-0.144909E0).*vl.^(-1).*( ...
  0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)+(-2).*(0.182574E0.*vl+( ...
  -0.230029E0).*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+ ...
  (-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+( ...
  -0.148148E3).*vl.^6).^(1/2)).^(-1/3)+0.144909E0.*vl.^(-1).*( ...
  0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)).^(-1)).*(4+( ...
  0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*(0.2E2.*vl.^2+(-1).*vl.^4) ...
  .*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.*3.^(1/2).*( ...
  0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(-1/3)+ ...
  0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+3.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^(1/3)) ...
  .^2).^(1/2)+2.*asinh((1/2).*(0.182574E0.*vl+(-0.230029E0).*vl.^( ...
  -1).*(0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(-1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)))+(-2).*log(0.182574E0.*vl+(-0.230029E0).*vl.^(-1).*( ...
  0.2E2.*vl.^2+(-1).*vl.^4).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.*vl.^6+ ...
  3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2)).^( ...
  -1/3)+0.144909E0.*vl.^(-1).*(0.3E3.*vl.^2+(-0.6E2).*vl.^4+2.* ...
  vl.^6+3.*3.^(1/2).*(0.333333E4.*vl.^4+(-0.148148E3).*vl.^6).^(1/2) ...
  ).^(1/3)));
out = real(out);
end

function [out,vprp,vprl,yres] = resonanceContoursMinorIon(qom,momp,beta0,vaprl,vaprp)
% Oblique proton ICW contours for general q/m 
% qom,momp are q/m and m/mp in units of proton mass. beta0 is vth units of distribution you want to plot it on
% y is kprl*di (Isenberg's notation). v in units of va until the end

miny = ((1/qom)^(2/3)-1)^-0.5;
minvl = qom/miny - 1/sqrt(1+miny^2);

% Compute contour function in vprp y, then convert y grid to vprl
% yres = linspace(miny,-0.01,200);
% vprl = -1./sqrt(1+yres.^2) - qom./yres;
% inc = vprl<1; yres = yres(inc);vprl = vprl(inc);
% Compute uniform vprl grid and convert to y
vprl = linspace(minvl+1e-3,vaprl,200*vaprp);
vlsolve = @(y,vl) -vl - 1./sqrt(1+y.^2) + qom./y;
yres = [];yguess = qom/(1+vprl(end));
for lll = length(vprl):-1:1
    yres = [fzero(@(y) vlsolve(y,vprl(lll)),yguess) yres];
    yguess = yres(1);
end

vprp = linspace(0,vaprp,200*vaprp); % Grid out to va
[Y,VP]=ndgrid(yres,vprp);

out = VP.^2+qom.*Y.^(-2).*(qom+2.*Y.^3.*(1+Y.^2).^(-1/2));
% out = VP.^2+(-1+1./Y).^2+2./Y; % non-dispersive
vprl = vprl*sqrt(momp/beta0);
vprp = vprp*sqrt(momp/beta0);


% % Code to check these are correct
% [outold,outva,vprlhalf] = resonanceContours(linspace(0,3.5,200),linspace(-2,2,200));
% 
% figure
% subplot(121)
% contour(vprl,vprp,out.',10,'-k')
% hold on
% contour(vprlhalf,linspace(0,3.5,200),outold.',10,'-b')
% pbaspect([max(vprl)-min(vprl) max(vprp) 1])
% subplot(122)
% plot(vprl,yres,'.-')
% xlabel('$v_\|/v_{\rm th0}$','Interpreter','latex')
% ylabel('$k_{\|,res}d_i$','Interpreter','latex')



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
