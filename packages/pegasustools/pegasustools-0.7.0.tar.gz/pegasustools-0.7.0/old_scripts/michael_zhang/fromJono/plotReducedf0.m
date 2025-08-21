function plotReducedf0
set(0,'DefaultTextInterpreter','latex');
set(0,'DefaultLineLineWidth',1.0);
set(0,'DefaultAxesFontSize',11);
set(0,'DefaultTextFontSize',11);
set(0,'DefaultAxesLineWidth',1.0);
myblue   = [16 116 176]/256;
myred    = [227 35 31]/256;
myorange = [228 157 37]/256;
mypurple = [124 50 139]/256;
myyellow = [239 226 82]/256;
mygreen  = [123 174 54]/256;
mysky    = [77 190 238]/256;
myidk    = [16 190 54]/256;


i_b3 = 0; %14.2
b_b3 = 0; %7.5
i_b0625 = 0; %10.5
b_b0625 = 1; %2.5

timename = ['2-5-'];


tstrt = 0;%5;%20;
unscalew = 1;
plotfs = 1;

if b_b3
    name = 'b_b3_sim1';
    nums = [0:222]; % b3 need to redo, since wrong normalizationg by pcc (32 instead of 27)
    P.beta=0.3;
    mass = [1 16 4 16 12 12 56];
    charge = [1 5 2 6 6 5 9];
    fnames = {'p' 'o5' 'he' 'o6' 'c6' 'c5' 'fe9'};
    xnames = {'$w_\|/v_{\rm th0,p}$','$w_\|/v_{\rm th0,O^{5+}}$','$w_\|/v_{\rm th0,He^{++}}$','$w_\|/v_{\rm th0,O^{6+}}$','$w_\|/v_{\rm th0,C^{6+}}$','$w_\|/v_{\rm th0,C^{5+}}$','$w_\|/v_{\rm th0,Fe^{9+}}$'};
    ynames = {'$w_\perp/v_{\rm th0,p}$','$w_\perp/v_{\rm th0,O^{5+}}$','$w_\perp/v_{\rm th0,He^{++}}$','$w_\perp/v_{\rm th0,O^{6+}}$','$w_\perp/v_{\rm th0,C^{6+}}$','$w_\perp/v_{\rm th0,C^{5+}}$','$w_\perp/v_{\rm th0,Fe^{9+}}$'};
    vol=6*48.1802^3;
    tauA = 6*48.1802;
    epsin = 12.9;%36.5; % energy injection per volume is the same?
    tas = nums*10./tauA;
    colorder = {mypurple myorange mygreen myred myblue mysky myidk};
else
    colorder = {mypurple myorange mygreen myred myblue mysky myyellow};
end
if i_b0625
    name = 'hb_beta0625';
    nums = [0:165];
    P.beta= 0.0625;
    mass = [1 16 4 16 12 12 24];
    charge = [1 5 2 6 6 5 9];
    fnames = {'p' 'o5' 'he' 'o6' 'c6' 'c5' 'mg9'};
    xnames = {'$w_\|/v_{\rm th0,p}$','$w_\|/v_{\rm th0,O^{5+}}$','$w_\|/v_{\rm th0,He^{++}}$','$w_\|/v_{\rm th0,O^{6+}}$','$w_\|/v_{\rm th0,C^{6+}}$','$w_\|/v_{\rm th0,C^{5+}}$','$w_\|/v_{\rm th0,Mg^{9+}}$'};
    ynames = {'$w_\perp/v_{\rm th0,p}$','$w_\perp/v_{\rm th0,O^{5+}}$','$w_\perp/v_{\rm th0,He^{++}}$','$w_\perp/v_{\rm th0,O^{6+}}$','$w_\perp/v_{\rm th0,C^{6+}}$','$w_\perp/v_{\rm th0,C^{5+}}$','$w_\perp/v_{\rm th0,Mg^{9+}}$'};
    vol=6*22.0^3;
    tauA = 6*22.0;
    epsin = 4.0;
    tas = nums*6.6/tauA;
end
if b_b0625
    name = 'b_b0625_sim1';
    nums = [0:76];
    mass = [1 16 4 16 12 12 24];
    P.beta= 0.0625;
    charge = [1 5 2 6 6 5 9];
    fnames = {'p' 'o5' 'he' 'o6' 'c6' 'c5' 'mg9'};
    xnames = {'$w_\|/v_{\rm th0,p}$','$w_\|/v_{\rm th0,O^{5+}}$','$w_\|/v_{\rm th0,He^{++}}$','$w_\|/v_{\rm th0,O^{6+}}$','$w_\|/v_{\rm th0,C^{6+}}$','$w_\|/v_{\rm th0,C^{5+}}$','$w_\|/v_{\rm th0,Mg^{9+}}$'};
    ynames = {'$w_\perp/v_{\rm th0,p}$','$w_\perp/v_{\rm th0,O^{5+}}$','$w_\perp/v_{\rm th0,He^{++}}$','$w_\perp/v_{\rm th0,O^{6+}}$','$w_\perp/v_{\rm th0,C^{6+}}$','$w_\perp/v_{\rm th0,C^{5+}}$','$w_\perp/v_{\rm th0,Mg^{9+}}$'};
    vol=6*22.0^3;
    tauA = 6*22.0;
    epsin = 4.0;
    tas = nums*6.6/tauA;
end
if i_b3
    name = 'half_tcorr_sim9';
    nums = [0:440];%[0:401 ];%229:312]; % snapshot numbers for which to find spectrum %i_b3
%nums = [229:440]; %ib3 edv % min 229 for edotvav output
%nums = [0:95];
    P.nspec_prlav = [1000 2000 2000];
    P.nspec_prpav = [500 1000 1000];
    P.vprpmaxav = [10 20 20];
    P.vprlmaxav = [10 20 20];
    P.beta=0.3;
    mass = [1 16 4];
    charge = [1 5 2];
    fnames = {'p' 'o5' 'he'};
    xnames = {'$w_\|/v_{\rm th0,p}$','$w_\|/v_{\rm th0,O^{5+}}$','$w_\|/v_{\rm th0,He^{++}}$'};
    ynames = {'$w_\perp/v_{\rm th0,p}$','$w_\perp/v_{\rm th0,O^{5+}}$','$w_\perp/v_{\rm th0,He^{++}}$'};
    ppc = [1000 64 64];
    vol=6*48.1802^3;
    tauA = 6*48.1802;
    epsin = 12.9;%36.5; % energy injection per volume is the same?  
    tas = nums*10./tauA;
    specs = [1 3 2];
    P.savemid = [500 1000 1000];% 300; % save only first savemid in vprp, middle 2*savemid in vprl
else
    P.nspec_prlav = [1000 2000 2000 2000 2000 2000 2000];
    P.nspec_prpav = [500 1000 1000 1000 1000 1000 1000];
    P.vprpmaxav = [10 20 20 20 20 20 20];
    P.vprlmaxav = [10 20 20 20 20 20 20];
    ppc = [1000 27 27 27 27 27 27];
    tas = nums*10./tauA;
    P.savemid = [500 1000 1000 1000 1000 1000 1000];
    specs = [1 3 2 4 5 6 7]
end

% gotta correct Dpp calcs (and maybe other 1D calcs to use wp normalized to
% vthperp

 % All thermal velocities normalized to sqrt(beta)
vthp = sqrt(P.beta);
qom = charge./mass;


vthi = vthp./sqrt(mass);



ncells = 6*280^3; nmesh = 24*20*14;
nprtl = ncells.*ppc;


nrm = epsin.*nprtl/vol; % With this sum(sum(edv_prp)) seems to match (as much as possible) d_t Eprp/epsin. 
% See compareHeatingDiagnostics.m
if strcmp(name,'lev')
    vol=6*34.4144^3;ncells = 6*200^3;nprtl = ncells*ppc;
    epsin = 9.52;nrm = epsin*nprtl/vol;tauA=206.4865395;
end
nrmdfdt = nrm;
nrm = nrm./(P.nspec_prpav./P.vprpmaxav).^2; % Since there are 50 points per vth


savebase = [ './saved-analysis/'];
load([ savebase 'PlotDFsNew' timename name '.mat'],'plotf0','vprl','vprp','tav','vthtot');






if plotfs


    
% NOTE:
%   plotf0 is normalized such that 
%             SUM[ plotf0*(dvprp/vth0)*(dvprl/vth0) ] = 1
%   actual VDF = plotf0 / (vprp/vth0) * [n/(2*pi*vth0^3)]
%   looks like we've been setting pi*vth0^2 = 1 in our plotting of f(vprp),
%   so that the Maxwellian f(vprp) = exp(-vprp^2/vth^2), so the def'n of
%   f(vprp) = pi vthprp^2 int[ f dvprl ] 
%           = (vthprp/vth0)^2 int[ 0.5*plotf0*(dvprl/vth0)*(vth0/vprp)
%

    rebinN  = 250;
    %vmaxarr = { 10,20,20,20,20,20,20 };
    %vmaxplt = { 6,8.5,14,14,14,14,14 };

    vmaxarr = { 10,20,20,20,20,20,20 };

        %vmaxplt = { 8,20,10,20,20,20,20  };
    
        vmaxplt = { 20,20,20,20,20,20,20  };
    
        

    xlab    = '$w_\|/v_{\rm th,i0}$';
    ylab    = '$f(w_\|)$';
    tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };

    
    

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    %width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    %normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
    %            [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced, $\beta=0.3$","balanced, $\beta=0.3$", "imbalanced, $\beta=1/16$", "balanced, $\beta=1/16$" };


    counter = 1;
    pcounter = 1;
    
    for spec=specs   % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        %vprpn = vprpq; vprln = vprlq;
        f0 = plotf0{spec};
        dvprl = vprln(2)-vprln(1);
        f0prp = 0.5*dvprl*sum(f0,1)./vprpn;
        vthpp = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
        
        %semilogx(vprpn,exp(-vprpn.^2),':k');

        fprl = trapz(vprpn,f0,2);
        disp(fnames(spec));
        %disp(trapz(vprln,fprl'));
        %disp(trapz(vprln,vprln.*fprl'));
        %f0 = f0./vpn'/2;

        disp((sum(sum(f0.*vprln'.*vprpn))/sum(sum(f0))))


        %f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q;
        plot(vprln,fprl,'Color',colorder{spec},'LineWidth',1) 
        %semilogx(vprpn/vthpp,f0prp*vthpp^2,'Color',colorder{spec});

        %xticks([-15 -10 -5 0 5 10 15]);

        %set(gca,'Units','normalized','Position',normpos{1});

    if spec==1
        hold on
    end

    end
    %semilogx(vprpn,exp(-vprpn.^2),':k');
    plot([0 0],[0 1], ':k')
    hold off
    title(tlab{4});
    if i_b3
        leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    end
    if b_b3
        leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    end
    if b_b0625 || i_b0625
        leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    end
    leg.ItemTokenSize = [25,18];
    xticks([-5 -4 -3 -2 -1 0 1 2 3 4 5])
    xlim([-5 5])
    xlabel('$w_{\parallel}/v_{{\rm th},i0}$','interpreter','latex')
    ylim([0 0.7])
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    plotTickLatex2D('ytickdx',0.003);

    



end  % plotfs




%disp(trapz(vprp{1},plotf0{1},2))
%disp(trapz(vprl{1},plotf0{1},1))

%plot(vprl{1},plotf0{1})
disp(size(trapz(vprp{1},plotf0{1},2)))
disp(size(vprl{1}))

%disp(trapz(vprl{2},trapz(vprp{2},plotf0{6},2),1))

%plot(vprl{1},trapz(vprp{1},plotf0{1},2));


%plotf0










function  out = int_dist(vprl,vprp,F)
% f itself already includes the wprp factor in the integration dw| wprp dwprp
out = trapz(vprl,trapz(vprp,F,2),1);

end


function [fe,egrd,fetheta,thetag] = convertToEthetaDist(vprl,vprp,F)
% See note DistributionFunctions in imbalanced pegasus Notability.
% Jacobian is just 1/2, so just interpolate to e, theta

vprl = vprl.';
egrd = logspace(-2,log10(max(max(vprp.^2 + vprl.^2))),2000);
thetag = linspace(0,180,361);
[e,theta] = ndgrid(egrd,thetag);

wprli = sqrt(e).*cosd(theta);
wprpi = sqrt(e).*sind(theta);

fetheta = 0.5*interpn(vprl,vprp,F,wprli,wprpi,'spline',0);

fe = trapz(thetag,fetheta,2); 
fe = egrd.'.*fe./trapz(egrd,fe); % This is be the logarithmic distribution



% s=pcolor(thetag,log10(egrd),fetheta);
%     s.EdgeColor='none';s.FaceColor='interp';

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



function df = dbydw2(f,w)
% gradient function is shit ? do a loop
dw = w(11,1,:)-w(10,1,:);
df = zeros(size(f));
for nnn=1:size(f,2)
    df(:,nnn) = gradient(f(:,nnn),dw(nnn));
end

end

function df = cumtrap2(f,w)
% gradient function is shit ? do a loop
df = zeros(size(f));
for nnn=1:size(f,2)
    df(:,nnn) = cumtrapz(w(:,1,nnn),f(:,nnn),1);
end

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


function [out,outva,vprlhalf] = resonanceContours(vprp,vprl)
% See IC Resonance Conditions.nb notebook
oblique = 1;

vprl = vprl(vprl>0.01);

vprlhalf = vprl;

[vl,vp]=ndgrid(vprl,vprp);
% This is non-dispersive version, propagating at vA
outva = vl.^2+0.365148E1.*(0.182574E1+vl)+vp.^2;
% This is dispersive cold IC resonance at beta=0.3
if ~oblique
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
else
out = 0.333333E1.*((0.912871E0.*vl.^(-1)+(1/2).*3.^(-1/2).*((-2)+0.1E2.* ...
  vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+ ...
  vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)) ...
  .^(1/3)).^(1/2)+(-1/2).*((-4/3)+0.666667E1.*vl.^(-2)+(-1/3).* ...
  vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(-1/3)+(-1/3).*vl.^(-2).*(0.6E3.* ...
  vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^( ...
  1/2)).^(1/3)+(1/4).*3.^(1/2).*(0.486864E2.*vl.^(-3)+0.146059E2.* ...
  vl.^(-1)).*((-2)+0.1E2.*vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+vl.^6+6.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+ ...
  vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(1/3)).^(-1/2)).^(1/2)).^(-2)+2.*( ...
  0.912871E0.*vl.^(-1)+(1/2).*3.^(-1/2).*((-2)+0.1E2.*vl.^(-2)+ ...
  vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+vl.^6+ ...
  6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)) ...
  .^(1/2)+(-1/2).*((-4/3)+0.666667E1.*vl.^(-2)+(-1/3).*vl.^2.*( ...
  0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.* ...
  vl.^8).^(1/2)).^(-1/3)+(-1/3).*vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.* ...
  3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)+( ...
  1/4).*3.^(1/2).*(0.486864E2.*vl.^(-3)+0.146059E2.*vl.^(-1)).*((-2) ...
  +0.1E2.*vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*( ...
  0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*( ...
  0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.* ...
  vl.^8).^(1/2)).^(1/3)).^(-1/2)).^(1/2)).*(1+(0.912871E0.*vl.^(-1)+ ...
  (1/2).*3.^(-1/2).*((-2)+0.1E2.*vl.^(-2)+vl.^2.*(0.6E3.*vl.^2+ ...
  vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)) ...
  .^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.* ...
  vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)).^(1/2)+(-1/2).*((-4/3)+ ...
  0.666667E1.*vl.^(-2)+(-1/3).*vl.^2.*(0.6E3.*vl.^2+vl.^6+6.*3.^( ...
  1/2).*(0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(-1/3)+(-1/3) ...
  .*vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+ ...
  0.111111E2.*vl.^8).^(1/2)).^(1/3)+(1/4).*3.^(1/2).*(0.486864E2.* ...
  vl.^(-3)+0.146059E2.*vl.^(-1)).*((-2)+0.1E2.*vl.^(-2)+vl.^2.*( ...
  0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).*(0.333333E4.*vl.^4+0.111111E2.* ...
  vl.^8).^(1/2)).^(-1/3)+vl.^(-2).*(0.6E3.*vl.^2+vl.^6+6.*3.^(1/2).* ...
  (0.333333E4.*vl.^4+0.111111E2.*vl.^8).^(1/2)).^(1/3)).^(-1/2)).^( ...
  1/2)).^2).^(-1/2))+vp.^2;


end
out = real(out);
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

end
