function plot_hst_energy%( fname )
i_b3 = 0;
b_b3 = 0;
i_b0625=0;
b_b0625=0;
i_b1 = 1;
b_b1=0;

plot_gradient=1;
plot_prlgrad = 0;
dens = 0.1;
scaleheat = 0;
scaleprotonheat = 0;
paperSave = 1;
rateSave = 0;

p_id = 'minor_turb';
if i_b3
    name = 'half_tcorr_sim9';
    rhoi = sqrt(0.3);
    nions = 2;
    mass = [1 16 4];
    charge = [1 5 2];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] };
    plotorder = [1 3 2];
    plotorder_trunc = [3 2];

    vol=6*48.1802^3;
    tauA = 6*48.1802;
    beta0 = 0.3;

    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end

if b_b3
   name2 = 'b_b3_sim1';
   rhoi = sqrt(0.3);
    nions = 6;
    mass = [1 16 4 16 12 12 56];
    charge = [1 5 2 6 6 5 9];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder = [1 3 2 4 5 6];
    plotorder_trunc = [3 2 4 5 6 7];
    vol=6*48.1802^3;
    tauA = 6*48.1802;
    beta0=0.3
    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end

if i_b0625
    name = 'hb_beta0625';
    rhoi = sqrt(0.0625);

    nions = 6;
    mass = [1 16 4 16 12 12 24];
    charge = [1 5 2 6 6 5 9];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder = [1 3 2 4 5 6];
    plotorder_trunc = [3 2 4 5 6 7];
    vol=6*22.0^3;
    tauA = 6*22.0;
    beta0 = 0.0625;

    fname = ['../../eyerger/' name '/output/' p_id ]; % Folder with outputs']; % Folder with outputs
end


if b_b0625
    name = 'b_b0625_sim1';
    rhoi = sqrt(0.0625);
    nions = 6;
    mass = [1 16 4 16 12 12 24];
    charge = [1 5 2 6 6 5 9];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] };
    plotorder = [1 3 2 4 5 6];
    plotorder_trunc = [3 2 4 5 6 7];
    vol=6*22.0^3;
    tauA = 6*22.0;
    beta0 = 0.0625;

    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end


if i_b1
    name = 'i_b1_sim1';
    rhoi = 1;

    nions = 7;
    mass = [1 16 4 16 12 12 24 1];
    charge = [1 5 2 6 6 5 9 1];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] [0.2940 0.1840 0.5560]};
    plotorder = [1 3 2 4 5 6 7];
    plotorder_trunc = [3 2 4 5 6 7 8];
    vol=6*87.96459^3;
    tauA = 6*87.96459;
    beta0 = 1.0;

    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end


if b_b1
    name = 'b_b1_sim1';%'i_b1_sim1';
    rhoi = 1;
    nions = 7;
    mass = [1 16 4 16 12 12 24 1];
    charge = [1 5 2 6 6 5 9 1];
    cols = {[0.6350 0.0780 0.1840] [0 0.4470 0.7410] [0.4660 0.6740 0.1880] [0.3010 0.7450 0.9330]  [0.8500 0.3250 0.0980]  [0.9290 0.6940 0.1250]  [0.4940 0.1840 0.5560] [0.2940 0.1840 0.5560]};
    plotorder = [1 3 2 4 5 6 7];
    plotorder_trunc = [3 2 4 5 6 7 8];
    vol=6*87.96459^3;
    tauA = 6*87.96459;
    beta0 = 1.0;
    fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs
end
qom = charge./mass;


savebase = ['saved-analysis/'];




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

t = dat(:,1);
if b_b3 || b_b0625 || b_b1
    is = restart_overlaps3(t);
    ion_start = 35;
end
if i_b1
    is = restart_overlaps3(t);
    ion_start = 38;
end
if i_b3
    is = restart_overlaps2(t);
    ion_start = 38;
end
if i_b0625
    is = restart_overlaps3(t);
    ion_start = 38;
end

dt = dat(:,2);
dthst = mean(diff(t));


va = 1;

uprp = {};
uprl = {};
urms = {};
cross_hel = {};
zp2 = {};
zm2 = {};
imbal = {};
vthpp = {};
vthpl = {};
beta = {};
betap = {};



uprp{1} = sqrt(2*(dat(:,8) + dat(:,9)));
uprl{1} = sqrt(2*dat(:,7));
urms{1} = sqrt(2*sum(dat(:,7:9),2));
bprp = sqrt(2*(dat(:,11) + dat(:,12)));
dbprl = sqrt(2*dat(:,10));
cross_hel{1} = sum(dat(:,16:18),2); %*96^2*560*100;
zp2{1} = 0.5*(sum(dat(:,7:9),2) + sum(dat(:,10:12),2) + cross_hel{1});
zm2{1} = 0.5*(sum(dat(:,7:9),2) + sum(dat(:,10:12),2) - cross_hel{1});
imbal{1} = (zp2{1} - zm2{1})./(zp2{1} + zm2{1});
vthpp{1} = sqrt(dat(:,28))/sqrt(2);
vthpl{1} = sqrt(dat(:,27));
beta{1} = 2/3*(2*vthpp{1}.^2 + vthpl{1}.^2)./(1+bprp.^2+dbprl.^2);
betap{1} = 2*vthpp{1}.^2./(1+bprp.^2+dbprl.^2);

t=t/tauA;


%etahyper = 33
%total_uf = 34
%total bfu = 37
for i  = 1:nions
    ion_ind = ion_start+24*(i-1);
    uprp{i+1} = sqrt(2*(dat(:,ion_ind+5) + dat(:,ion_ind+6)));
    uprl{i+1} = sqrt(2*dat(:,ion_ind+4));
    urms{i+1} = sqrt(2*sum(dat(:,ion_ind+4:ion_ind+6),2));
    cross_hel{i+1} = sum(dat(:,ion_ind+7:ion_ind+9),2); %*96^2*560*100;
    zp2{i+1} = 0.5*(sum(dat(:,ion_ind+4:ion_ind+6),2) + sum(dat(:,10:12),2) + cross_hel{i+1});
    zm2{i+1} = 0.5*(sum(dat(:,ion_ind+4:ion_ind+6),2) + sum(dat(:,10:12),2) - cross_hel{i+1});
    imbal{i+1} = (zp2{i+1} - zm2{i+1})./(zp2{i+1} + zm2{i+1});
    vthpp{i+1} = sqrt(dat(:,ion_ind+19))/sqrt(2);
    vthpl{i+1} = sqrt(dat(:,ion_ind+18));
    beta{i+1} = 2/3*mass(i+1)*dens*(2*vthpp{i+1}.^2 + vthpl{i+1}.^2)./(1+bprp.^2+dbprl.^2);
    betap{i+1} = 2*mass(i+1)*dens*vthpp{i+1}.^2./(1+bprp.^2+dbprl.^2);
end


%
% hst.t = t(is); hst.uprp = uprp(is);hst.bprp = bprp(is);hst.vthpp = vthpp(is);hst.vthpl = vthpl(is);hst.beta = beta(is);
% hst.zp2 = zp2(is);hst.zm2 = zm2(is);hst.imbal = imbal(is);hst.beta = beta(is);
% save(['saved-analysis/hst-energy-' name '.mat'],'hst')


figure('Color',[1 1 1]);
%subplot(211)
plot(t(is),uprl{1}(is),'-','Color',cols{1},'Linewidth',3) 
hold on

for i = 1:nions
    plot(t(is),uprl{i+1}(is),'-','Color',cols{i+1},'Linewidth',3) 
end
hold off


figure('Color',[1 1 1]);
%subplot(211)
%plot(t(is),uprp(is), t(is), bprp(is), t(is),vthpp(is).^2,'--',t(is),vthpl(is).^2,'--',t(is),beta(is),':',t(is),ones(size(is))*sqrt(0.3)/sqrt(2),'k:','Linewidth',1)
%plot(t(is),vthpp(is).^2/vthpp(1)^2,'-','Color',	[0.6350 0.0780 0.1840])%, t(is), vthpl(is).^2/vthpl(1)^2,'--','Color',[0.6350 0.0780 0.1840])%,t(is),vthpp_s2(is).^2 / vthpp_s2(1)^2,'-','Color',[0 0.4470 0.7410],t(is),vthpl_s2(is).^2 / vthpl_s2(1)^2,'--','Color',[0 0.4470 0.7410],t(is),vthpp_s1(is).^2 / vthpp_s1(1)^2,'-','Color',[0.4660 0.6740 0.1880],t(is),vthpl_s1(is).^2 / vthpl_s1(1)^2,'--','Color',[0.4660 0.6740 0.1880],'Linewidth',1)
%plot(t(is),vthpp(is).^2/vthpp(1)^2,'-','Color',[0.6350 0.0780 0.1840],'Linewidth',3) 
plot(t(is),vthpp{1}(is).^2/vthpp{1}(1)^2,'-','Color',cols{1},'Linewidth',3) 
hold on
%plot(t(is), vthpl(is).^2/vthpl(1)^2,'--','Color',[0.6350 0.0780 0.1840],'Linewidth',3)
plot(t(is),vthpl{1}(is).^2/vthpl{1}(1)^2,'--','Color',cols{1},'Linewidth',3) 
for i = 1:nions
    plot(t(is),vthpp{i+1}(is).^2/vthpp{i+1}(1)^2,'-','Color',cols{i+1},'Linewidth',3) 
    plot(t(is),vthpl{i+1}(is).^2/vthpl{i+1}(1)^2,'--','Color',cols{i+1},'Linewidth',3) 
end


%plot(t(is),vthpp_s2(is).^2 / vthpp_s2(1)^2/(m2^1.07),'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
%plot(t(is),vthpl_s2(is).^2 / vthpl_s2(1)^2/(m2^1.07),'--','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
%plot(t(is),vthpp_s1(is).^2 / vthpp_s1(1)^2/(m1^1.07),'-','Color',	[0 0.4470 0.7410],'Linewidth',3)
%plot(t(is),vthpl_s1(is).^2 / vthpl_s1(1)^2/(m1^1.07),'--','Color',[0 0.4470 0.7410],'Linewidth',3)
hold off
%legend({'$T_{\perp,p}$','$T_{\|,p}$','$T_{\perp,He^{++}}$','$T_{\|,He^{++}}$','$T_{\perp,O^{5+}}$','$T_{\|,O^{5+}}$'},'interpreter','latex','Location','northwest')
legend({'$T_{\perp,p}$','$T_{\|,p}$','$T_{\perp,O^{5+}}$','$T_{\|,O^{5+}}$','$T_{\perp,He^{++}}$','$T_{\|,He^{++}}$','$T_{\perp,O^{6+}}$','$T_{\|,O^{6+}}$','$T_{\perp,C^{6+}}$','$T_{\|,C^{6+}}$','$T_{\perp,C^{5+}}$','$T_{\|,C^{5+}}$','$T_{\perp,Fe^{9+}}$','$T_{\|,Fe^{9+}}$'},'interpreter','latex','Location','northwest')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$T_s/T_{s0}$','interpreter','latex')
set(gca,'fontsize', 16);
%ylim([0 7])
%subplot(212)
dirsave = ['../simulations/' name '/saved-plots/'];
foutlab = [dirsave,'tplotT2' '.png'];
exportname = [dirsave,'tplotT2' '.pdf'];
  drawnow;
  fig = gcf;
  fig.PaperPositionMode = 'auto';
  %print(foutlab,'-dpng','-r0');
  exportname = [dirsave,'tplotT2' '.pdf'];
  %exportgraphics(fig,exportname,'ContentType','vector')
 
disp('final species temperatures (perp)')
for i = 1:nions+1
 disp(vthpp{i}(is(end)).^2/vthpp{i}(1)^2)
 %disp(vthpl{i}(is(end)).^2/vthpl{i}(1)^2)
end



if plot_gradient
    
    dydxpp = {};
    dydxpl = {};

    % unscaled? but we care about mv^2 = T, and initial Ts are the same so
    % shouldn't matter for Q
    Q.tep = {};
    Q.tel = {};
    for i = 1:nions+1
        dydxpp{i} = gradient(vthpp{i}(is).^2/vthpp{i}(1)^2)./gradient(t(is));
        dydxpl{i} = gradient(vthpl{i}(is).^2/vthpl{i}(1)^2)./gradient(t(is));
        Q.tep{i} = vthpp{i}(is)/vthpp{i}(1)
        Q.tel{i} = vthpl{i}(is)/vthpl{i}(1)
    end

    windowSize = ceil(tauA);
    filt = @(f) filter((1/windowSize)*ones(1,windowSize),1,f);
    figure('Color',[1 1 1]);

    for i = 0:nions
        dydxpp{i+1} = filt(dydxpp{i+1});
        dydxpl{i+1} = filt(dydxpl{i+1});
    end
    if rateSave
        Q.qp = dydxpp;
        Q.ql = dydxpl;
        Q.t = t(is);
        save([ savebase 'PlotQ-' name '.mat'],'Q', '-v7.3');
    end
    if scaleheat
        for i = 1:nions
            dydxpp{i+1} = dydxpp{i+1}./(1.35*mass(i+1));
            dydxpl{i+1} = dydxpl{i+1}./(1.35*mass(i+1));
        end
    end
    if scaleprotonheat
        for i = 1:nions
            dydxpp{i+1} = dydxpp{i+1}./dydxpp{1};
            dydxpl{i+1} = dydxpl{i+1}./dydxpl{1};
        end
        dydxpp{1} = dydxpp{1}./dydxpp{1};
        dydxpl{1} = dydxpl{1}./dydxpl{1};
    end

    plot(t(is),dydxpp{1},'-','Color',cols{1},'Linewidth',3) 
    hold on
    if plot_prlgrad
        plot(t(is),dydxpl{1},'--','Color',cols{1},'Linewidth',3)
    end
        for i = plotorder_trunc
            plot(t(is),dydxpp{i},'-','Color',cols{i},'Linewidth',3)
            if plot_prlgrad
                plot(t(is),dydxpl{i},'--','Color',cols{i},'Linewidth',3)
            end
        end

    if scaleprotonheat
        %ylim([-50 600])
        ylim([0 100])
        xlim([0.1 8])
        %ylim([0 250])
        %xlim([2.5 15.3])
        %ylim([0 10])
    end



    %plot(t(is),filt(dydxpp_s2)./(1.35*m2),'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
    %plot(t(is),filt(dydxpl_s2)/(1.35*m2),'--','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
    %plot(t(is),filt(dydxpp_s1)/(1.35*m1),'-','Color',	[0 0.4470 0.7410],'Linewidth',3)
    %plot(t(is),filt(dydxpl_s1)/(1.35*m1),'--','Color',[0 0.4470 0.7410],'Linewidth',3)

    %plot(t(is),filt(dydxpp),'-','Color',[0.6350 0.0780 0.1840],'Linewidth',3) 
    %hold on
    %plot(t(is),filt(dydxpl),'--','Color',[0.6350 0.0780 0.1840],'Linewidth',3)
    %plot(t(is),filt(dydxpp_s2),'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
    %plot(t(is),filt(dydxpl_s2),'--','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
    %plot(t(is),filt(dydxpp_s1),'-','Color',	[0 0.4470 0.7410],'Linewidth',3)
    %plot(t(is),filt(dydxpl_s1),'--','Color',[0 0.4470 0.7410],'Linewidth',3)
    hold off
    %legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$'},'interpreter','latex','Location','northwest')
    %legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$'},'interpreter','latex','Location','northwest')
    
    if plot_prlgrad
        if bal
            %legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{6+}}$','$Q_{\|,O^{6+}}$','$Q_{\perp,C^{6+}}$','$Q_{\|,C^{6+}}$','$Q_{\perp,C^{5+}}$','$Q_{\|,C^{5+}}$','$Q_{\perp,Fe^{9+}}$','$Q_{\|,Fe^{9+}}$'},'interpreter','latex','Location','northeast')
        else
            legend({'$Q_{\perp,p}$','$Q_{\|,p}$','$Q_{\perp,He^{++}}$','$Q_{\|,He^{++}}$','$Q_{\perp,O^{5+}}$','$Q_{\|,O^{5+}}$'},'interpreter','latex','Location','northeast')
        end
    else
        legend({'$Q_{\perp,p}$','$Q_{\perp,He^{++}}$','$Q_{\perp,O^{5+}}$'},'interpreter','latex','Location','northeast')
    end
    xlabel('$t/\tau_A$','interpreter','latex')
    if scaleheat || scaleprotonheat
        ylabel('$\tilde{Q}$','interpreter','latex')
    else
        ylabel('$Q$','interpreter','latex')
    end
    
    set(gca,'fontsize', 16);
    %[grb,ok]=grad(m(S.EMp),S.k,[3 20]);%[3 100]);
    %[gre,ok]=grad(m(S.EEp),S.k,[3 20]);%[3 100]);
    %subplot(212)
    %one = ones(size(ok));
    %semilogx(ok,grb,ok,gre, ok,-5/3*one,'k:',ok,-2.8*one,'k:',ok,-4*one,'k:',1/rhoi*[1 1],[-10 1],'k:')
    %xlim([min(S.k) max(S.k)])
    %ylim([-5 0])
    %xlabel('$k_\perp$','interpreter','latex')
    %ylabel('$\alpha$','interpreter','latex')
    %hold off

    %if bal

    %  exportname = [dirsave,'qplot_bal_all' '.pdf'];


    %else
    %  if scaleheat
    %      exportname = [dirsave,'qplot_imbal_scaled' '.pdf'];
    %  else
    %      exportname = [dirsave,'qplot_imbal' '.pdf'];
    %  end
    %end


      drawnow;
      fig = gcf;
      fig.PaperPositionMode = 'auto';

      %exportgraphics(fig,exportname,'ContentType','vector')
end







figure('Color',[1 1 1]);
plot(t(is), sqrt(2*zp2{1}(is)), t(is), sqrt(2*zm2{1}(is)),'Linewidth',4)
ylabel('$z^{\pm}_{rms}/v_A$','interpreter','latex')
yyaxis right
semilogy(t(is),1-imbal{1}(is),'Linewidth',4)
legend({'$z^{+}_{rms}/v_A$','$z^{-}_{rms}/v_A$','$1-\sigma$'},'interpreter','latex','Location','northwest')
ylabel('$1-\sigma$','interpreter','latex')
% xlim([0 1])
% ylim([0 0.06])
xlabel('$t/\tau_A$','interpreter','latex')
set(gca,'fontsize', 16);
yyaxis left
foutlab = [dirsave,'tplotz' '.png'];
  drawnow;
  fig = gcf;
  fig.PaperPositionMode = 'auto';
  print(foutlab,'-dpng','-r0');
  exportname = [dirsave,'tplotz' '.pdf'];
  exportgraphics(fig,exportname,'ContentType','vector')


if paperSave
    imba.ts = t(is);
    imba.zp = sqrt(2*zp2{1}(is));
    imba.zm = sqrt(2*zm2{1}(is));
    imba.sig = imbal{1}(is);
    save([ savebase 'PlotZ-' name '.mat'],'imba', '-v7.3');
end



 figure('Color',[1 1 1]);
%subplot(211)
%plot(t(is),uprp(is), t(is), bprp(is), t(is),vthpp(is).^2,'--',t(is),vthpl(is).^2,'--',t(is),beta(is),':',t(is),ones(size(is))*sqrt(0.3)/sqrt(2),'k:','Linewidth',1)
%plot(t(is),vthpp(is).^2/vthpp(1)^2,'-','Color',	[0.6350 0.0780 0.1840])%, t(is), vthpl(is).^2/vthpl(1)^2,'--','Color',[0.6350 0.0780 0.1840])%,t(is),vthpp_s2(is).^2 / vthpp_s2(1)^2,'-','Color',[0 0.4470 0.7410],t(is),vthpl_s2(is).^2 / vthpl_s2(1)^2,'--','Color',[0 0.4470 0.7410],t(is),vthpp_s1(is).^2 / vthpp_s1(1)^2,'-','Color',[0.4660 0.6740 0.1880],t(is),vthpl_s1(is).^2 / vthpl_s1(1)^2,'--','Color',[0.4660 0.6740 0.1880],'Linewidth',1)
plot(t(is),urms{1}(is),'-','Color',[0.6350 0.0780 0.1840],'Linewidth',3) 
hold on
plot(t(is),urms{2}(is),'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
plot(t(is),urms{3}(is),'-','Color',	[0 0.4470 0.7410],'Linewidth',3)
%plot(t,temp_sp,'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
%plot(t,urms_sp,'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
hold off
legend({'$u_{p}$','$u_{He^{++}}$','$u_{O^{5+}}$'},'interpreter','latex','Location','northwest')
%legend({'$u_{He^{++}}$'},'interpreter','latex','Location','northwest')
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$u$','interpreter','latex')
set(gca,'fontsize', 16);


%{
 figure('Color',[1 1 1]);
plot(t,temp_sp,'-','Color',[0.4660 0.6740 0.1880],'Linewidth',3)
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$T$','interpreter','latex')
set(gca,'fontsize', 16);


figure
subplot(211)
plot(t(is),uprp{2}(is), t(is), bprp(is), t(is),vthpp{2}(is).^2,'--',t(is),vthpl{2}(is).^2,'--',t(is),beta_s1(is),':',t(is),ones(size(is))*sqrt(0.3)/sqrt(2),'k:','Linewidth',1)
legend({'$u_{1 \perp}$','$B_\perp$','$v_{th1 \perp}$','$v_{th1 \|}$','$\beta_{s1}$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
subplot(212)
plot(t(is), sqrt(2*zp2_s1(is)), t(is), sqrt(2*zm2_s1(is)))
ylabel('$z^\pm_{s1}$','interpreter','latex')
yyaxis right
semilogy(t(is),1-imbal_s1(is))
legend({'$z^+_{s1}$','$z^-_{s1}$','$1-\sigma_{s1}$'},'interpreter','latex')
ylabel('$1-\sigma$','interpreter','latex')
% xlim([0 1])
% ylim([0 0.06])
xlabel('$t/\tau_A$','interpreter','latex')
yyaxis left

figure
subplot(211)
plot(t(is),uprp_s2(is), t(is), bprp(is), t(is),vthpp_s2(is).^2,'--',t(is),vthpl_s2(is).^2,'--',t(is),beta_s2(is),':',t(is),ones(size(is))*sqrt(0.3)/sqrt(2),'k:','Linewidth',1)
legend({'$u_{2 \perp}$','$B_\perp$','$v_{th2 \perp}$','$v_{th2 \|}$','$\beta_{s2}$'},'interpreter','latex')
xlabel('$t/\tau_A$','interpreter','latex')
subplot(212)
plot(t(is), sqrt(2*zp2_s2(is)), t(is), sqrt(2*zm2_s2(is)))
ylabel('$z^\pm_{s2}$','interpreter','latex')
yyaxis right
semilogy(t(is),1-imbal_s2(is))
legend({'$z^+_{s2}$','$z^-_{s2}$','$1-\sigma_{s2}$'},'interpreter','latex')
ylabel('$1-\sigma_{s2}$','interpreter','latex')
% xlim([0 1])
% ylim([0 0.06])
xlabel('$t/\tau_A$','interpreter','latex')
yyaxis left


% Used fo r talk – to DELETE
figure
plot(t(is), beta(is),t(is), betap(is),'LineWidth',1.5)
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\sigma_c$','interpreter','latex')
sige = @(t) max(0.9*(1-2/3*0.1*max(0,t - 18.2)/0.9),0);
yyaxis right
plot(t(is), sige(t(is)),'LineWidth',1.5)
ylabel('$\varepsilon_H/\varepsilon$','interpreter','latex')
xlim([0 max(t)])
%}

ts = t(is);
dbprp = bprp(is);
imba = imbal{1}(is);
if bal
 timeind = find(abs(ts-7)<0.5/tauA,1);
else
 timeind = find(abs(ts-14.2)<0.5/tauA,1);
end
disp("finding time")
disp(timeind)
disp(ts(timeind))
disp(dbprp(timeind))
disp(imba(timeind))

figure('Color',[1 1 1]);
plot(ts,imba,'-','Color',[0.6350 0.0780 0.1840],'Linewidth',3) 
xlabel('$t/\tau_A$','interpreter','latex')
ylabel('$\delta B_{\perp}$','interpreter','latex')
set(gca,'fontsize', 16);



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

function [out, outk] = grad(f,k, smooth)
smin = smooth(1);smax = smooth(2);
disp(smin);
disp(smax)
nk = length(k);
lkmax = log(k(end-smax));lkmin=log(k(smin+1));
nn=1;
sfun = @(lk) floor( smin + ((smax-smin)*((lk-lkmin)/(lkmax-lkmin)).^2) );
for kkk=smin+1:nk-smax
    s = sfun(log(k(kkk)));
    %disp(sfun(log(k(kkk))));
    %disp(kkk);
    %disp(s);
    d = max([kkk-s,1])
    p = polyfit(log(k(kkk-s:kkk+s)),log(f(kkk-s:kkk+s)),1);
    %p = polyfit(log(k(d:kkk+s)),log(f(d:kkk+s)),1);
    outk(nn) = k(kkk);
    out(nn) =p(1);
    nn=nn+1;
end

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
%disp('restart times are ')
%disp(t(rinds)/(6*48.1802))
end


function inds = restart_overlaps4(t)
% Find indicies where the restart has caused an overlap
dtlim = 0.5; % nominal value is 1
rinds = find(diff(t)<0.5)+1; %find indices of restarts
disp(rinds);
%rinds = [815 929 1722 1818] 2433;
inds = [];
startinds = cat(1,[1],rinds);
for inn = [1 2 3 6:length(rinds)]; %1:length(rinds) %for each restart index
    tb = t(rinds(inn)); %find the time of the restart
    ia = find(t(1:rinds(inn))>tb,1);%find the first index before the restart index that has time greater than that just before the restart
    if inn == 7
        ia = find(t(337:rinds(inn))>tb,1);
        ia = ia + 337 -1;
    end
    disp(ia);
    inds = [inds ia:rinds(inn)-1]; %append all indices from before restart up until restart
end
inds = setdiff(1:length(t),inds);%returns all indices except those in inds
disp('restart times are ')
disp(t(rinds([1 2 3 6:18]))/(6*22.0))
end