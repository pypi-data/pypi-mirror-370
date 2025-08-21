function paperRate
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

% 0  = time plots
% 1  = figures of 2D power spectra
% 2  = figures of 1D power spectra (in kprp and omega) -- vertical two-time version
% 22 = figures of 1D power spectra (in kprp and omega) -- horizontal last-time version
% 222= figures of 1D power COMPENSATED spectra (in kprp and omega) -- vertical two-time version
% 3  = figures of VDFs from imbalanced and balanced runs
% 4  = figures of heating rates from imbalanced and balanced runs
% 42 = figures of heating rates on logy scale

plotnbr = 58;%488;%488;%48899;%44445;

%48 heating rates (scaled by eps only) for all sims
%487 heating rates scaled by m^0.95 m/q^0.6
%488 temperatures scaled by different things
%48899 heating rates for certain sims scaled by heating rates in other sims
%44445 heating rates (scaled by eps only) + temperatures for beta=0.0625
%58 beta=1 heating rates and temps

%colorder = {myblue myred myorange mypurple myyellow mygreen mysky}
colorder = {mypurple myorange mygreen myred myblue mysky myyellow};
colorderfe = {mypurple myorange mygreen myred myblue mysky myidk};
plotorder_trunc = [3 2 4 5 6 7]
plotorder_trunc_3 = [3 2];
plotorder_3 = [1 3 2];
beta    = 0.3;
beta0625 = 0.0625;
nspecies = 3;
%plotorder = [1 3 2];
plotorder = [1 3 2 4 5 6 7];
chargeog = [1 5 2 6 6 5 9];
massog = [1 16 4 16 12 12 56];
charge0625 = [1 5 2 6 6 5 9];
mass0625 = [1 16 4 16 12 12 24];
charge  = [1 2 5];
mass    = [1,4,16];
qom     = charge./mass;
oovth   = sqrt(mass);
dedt_imb1= 80.0; %12.9;
dedt_bal1= 56.8;
dedt_imb03= 39.89; %12.9;
dedt_bal03= 56.8;
dedt_imb0625= 2.57; %12.9;
dedt_bal0625= 10.75;

savebase = 'saved-analysis/';

if plotnbr==0

    name1 = 'half_tcorr_sim9';
    name2 = 'b_b3_sim1';
    load([ savebase 'PlotZ-' name1 '.mat'],'imba');
    load([ savebase 'PlotZ-' name2 '.mat'],'bala');

    skip = 10;
    imt = imba.ts(1:skip:end);
    imzp= imba.zp(1:skip:end);
    imzm= imba.zm(1:skip:end);
    imsg= imba.sig(1:skip:end);

    bat = bala.ts(1:skip:end);
    bazp= bala.zp(1:skip:end);
    bazm= bala.zm(1:skip:end);
    basg= bala.sig(1:skip:end);

    figure(10); clf; pwidth=8.8; pheight=5.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    lthick=2;
    p1 = plot(nan,nan,'k','Linewidth',lthick);
    hold on
    p2 = plot(nan,nan,'-k');
    plot(bat,bazp,'-','Color',myred);
    plot(bat,bazm,'-','Color',myblue);
    plot(imt,imzp,'-','Color',myred,'Linewidth',lthick);
    plot(imt,imzm,'-','Color',myblue,'Linewidth',lthick);

    yyaxis left
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    ylabel(',');
    ylim([0 0.54]);
    text(-2.6,0.11,'$z^+_{\rm rms}/v_{\rm A}$','interpreter','latex','Color',myred,'Rotation',90);
    text(-2.6,0.29,'$z^-_{\rm rms}/v_{\rm A}$','interpreter','latex','Color',myblue,'Rotation',90);
    set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',[0.15,0.167,0.705,0.82]);
    plotTickLatex2D('ylabeldx',-0.023,'xtickdy',-0.02,'xlabeldy',-0.01);

    yyaxis right
    set(gca,'ycolor',myorange);
    plot(bat,1-basg,'-','Color',myorange);
    plot(imt,1-imsg,'-','Color',myorange,'Linewidth',lthick);
    set(gca,'YScale', 'log');
    ylim([0.01 2])
    yticks(logspace(-2,0,3)); yticklabels({'$10^{-2}$','$10^{-1}$','$10^0$'});
    set(gca,'XTickLabel',[]);
    ylabel('$1-\sigma$','interpreter','latex','Color',myorange)
    plotTickLatex2D('ytickdx',-0.003,'ylabeldx',0.09,'fontcolor',myorange);

    hold off
    leg = legend([p1 p2],'imbal.','bal.', ...
        'Position',[0.58 0.41 0.2407 0.1827],'Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
end

%
% 2D power spectra
%
if plotnbr==1

    name = 'PlotSpectrum_kprlkprp-half_tcorr_sim9';
    load([ savebase name '.mat'],'Bprp','kls','kps');

    figure(11); clf; pwidth=8.8; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    height=0.5; width=height*(pheight/pwidth); offset = 0.165; gap = -0.062;
    normpos = { [offset,0.055+height+gap,width,height], ...
                [offset,0.055,width,height]};
    cbpos   = [0.85 0.1 0.033 0.85];
    lmin    = -11.5; lmax = -1.5;

    ylab    = '$k_\| d_{\rm p0}$';
    xlab    = '$k_\perp\rho_{\rm p0}$';
    levels  = lmin:(1/3):lmax;

    for i=1:2
        bplot   = log10(Bprp{i});
        min(min(bplot))
        max(max(bplot))

        subplot(2,1,i);
        liminds = find(bplot<lmin); bplot(liminds) = lmin-1;
        [C1,h1] = contourf(kps,kls,bplot',levels);
        set(h1,'LineColor',0.7*[1,1,1],'Linewidth',0.3);
        set(gca, 'XScale', 'log','YScale', 'log');
        axis xy; shading flat;
        hold on;
        plot([1 1],[min(kls) max(kls)],':k',[0.1 10],[1 1],':k');
        hold off;
        axis([0.1 10 0.1 4.5]);
        decades_equal(gca);
        colormap(brewermap([],"YlGnBu"))
        ylabel(ylab);
        set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{i});
        if i==1
            %hold on; loglog(kps(1:45),(kps(1:45)/min(kps)).^(2/3)*min(kps)/sqrt(beta)/6*3.5,':w','Linewidth',2); hold off;
            annotation('textarrow',[0.18 0.45],[0.56 0.695],'Linestyle',':', ...
                'LineWidth',2,'Color','w','HeadWidth',8,'HeadLength',8);
            text(0.127,0.18,'CB cascade','Fontsize',12,'Color','w','Rotation',33);
            set(gca,'XTickLabel',[]);
            text(0.14,3,'$t\approx 7.5\tau_{\rm A}$','Fontsize',12);
            plotTickLatex2D('ylabeldx',-0.015);
        else
            %hold on; loglog(kps(1:45),(kps(1:45)/min(kps)).^(2/3)*min(kps)/sqrt(beta)/6*5,':w','Linewidth',2); hold off;
            annotation('textarrow',[0.18 0.45],[0.15 0.285],'Linestyle',':', ...
                'LineWidth',2,'Color','w','HeadWidth',8,'HeadLength',8);
            xlabel(xlab);
            text(0.14,3,'$t\approx 14.2\tau_{\rm A}$','Fontsize',12);
            annotation('textarrow',[0.33 0.24],[0.37 0.33], ...
                'String','ICWs','Color','k', ...
                'Interpreter','latex','LineWidth',0.5,'HeadWidth',4,'HeadLength',7/1.5, ...
                'TextMargin',1,'VerticalAlignment','middle');
            plotTickLatex2D('ylabeldx',-0.015,'xtickdy',-0.01,'xlabeldy',0.005);
        end
    end

    cb = colorbar;
    title(cb,'$\mathcal{E}_B$','interpreter','latex');
    set(cb,'Position',cbpos,'Ticklength',0.01);
    cb.Limits=[lmin,lmax]; cb.Ticks=-11:1:-2;
    cb.TickLabels={'$10^{-11}$','','$10^{-9}$','','$10^{-7}$','','$10^{-5}$', ...
                '','$10^{-3}$',''};
    cb.TickLabelInterpreter='latex';
    cb.FontSize=10; cb.LineWidth=1;


end


%
% 1D power spectra
%
if plotnbr==2

    name = 'half_tcorr_sim9';
    load([ savebase 'PlotSwarm-' name '.mat'],'swarm');
    load([ savebase 'PlotSpectrum1D-' name '.mat'],'paper');
    imbswarm = swarm; clear swarm;
    imbpaper = paper; clear paper;

    name = 'b_b3_sim1';
    load([ savebase 'PlotSwarm-' name '.mat'],'swarm');
    load([ savebase 'PlotSpectrum1D-' name '.mat'],'paper');
    balswarm = swarm; clear swarm;
    balpaper = paper; clear paper;

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { '$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];

    kprp = imbpaper.k*sqrt(beta); om = imbswarm.omega;

    balkprp = balpaper.k*sqrt(beta); balom = balswarm.omega;
    balEB = balpaper.Emp{1}; balEE = balpaper.Eep{1};
    balbs = balswarm.bprp{1}; bales = balswarm.eprp{1};

    for i=1:2
        EB = imbpaper.Emp{i}; EE = imbpaper.Eep{i};
        irhop = qom(1)*sqrt(mass(1))/imbpaper.vthpp1{i};
        irhoa = qom(2)*sqrt(mass(2))/imbpaper.vthpp3{i};
        irhoO = qom(3)*sqrt(mass(3))/imbpaper.vthpp2{i};

        subplot(2,2,i);
        loglog(kprp,EB,'Color',myblue,'LineWidth',1);
        hold on;
        loglog(kprp,EE,'Color',myred,'LineWidth',1);
        loglog(balkprp,balEB,'--','Color',myblue);
        loglog(balkprp,balEE,'--','Color',myred);
        %loglog(kprp(1:35),5e-3*kprp(1:35).^(-1.6666),'--k');
        loglog(irhop*[1 1],[1e-10 1e1],':k');
        loglog(irhoa*[1 1],[1e-10 1e1],':k');
        loglog(irhoO*[1 1],[1e-10 1e1],':k');
        hold off;
        axis([min(kprp) 10 1e-7 1]);
        yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
        xlabel('$k_\perp\rho_{\rm p0}$');
        title(tlab{i});
        set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{i});
        text(xo(i),yo(i),'$k_\perp\rho_{\rm O^{5+}}(t)=1$','Rotation',90,'Fontsize',10);
        text(xa(i),ya(i),'$k_\perp\rho_\alpha(t)=1$','Rotation',90,'Fontsize',10);
        text(xp(i),yp(i),'$k_\perp\rho_{\rm p}(t)=1$','Rotation',90,'Fontsize',10);
        leg = legend({'$~\mathcal{E}_B(k_\perp)$','$~\mathcal{E}_E(k_\perp)$'}, ...
            'Location','NorthEast','Interpreter','latex','FontSize',10);
        legend('boxoff');
        plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    end

	for i=1:2
        bs = imbswarm.bprp{i}; es = imbswarm.eprp{i};

        subplot(2,2,2+i);
        loglog(om,bs,'Color',myblue)
        hold on
        loglog(om,es,'Color',myred)
        loglog(balom,balbs,'--','Color',myblue);
        loglog(balom,bales,'--','Color',myred);
        loglog(qom(1)*[1 1], [1e-10,1e1],':k');
        loglog(qom(2)*[1 1], [1e-10,1e1],':k');
        loglog(qom(3)*[1 1], [1e-10,1e1],':k');
        hold off;
        axis([min(om) 4 1e-6 2e-3]);
        yticks([1e-6 1e-5 1e-4 1e-3]);
        xlabel('$\omega/\Omega_{\rm p0}$');
        set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{2+i});
        %text(0.84,1.6e-6,'$\omega/\Omega_{\rm p,0}=1$','Rotation',90,'Fontsize',10);
        text(0.415,1.6e-6,'$\omega/\Omega_{\alpha0}=1$','Rotation',90,'Fontsize',10);
        text(0.26,1.6e-6,'$\omega/\Omega_{\rm O^{5+}0}=1$','Rotation',90,'Fontsize',10);
        leg = legend({'$~\mathcal{E}_B(\omega)$','$~\mathcal{E}_E(\omega)$'}, ...
            'Location','SouthWest','Interpreter','latex','FontSize',10);
        legend('boxoff');
        plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    end

    annotation('textarrow',[0.83 0.782],[0.41 0.36], ...
            'String','ICWs','Color','k', ...
            'Interpreter','latex','LineWidth',0.5,'HeadWidth',4,'HeadLength',7/1.5, ...
            'TextMargin',1,'VerticalAlignment','middle');

end

if plotnbr==22

    name = 'half_tcorr_sim9';
    load([ savebase 'PlotSwarm-' name '.mat'],'swarm');
    load([ savebase 'PlotSpectrum1D-' name '.mat'],'paper');

    figure(122); clf; pwidth=18.5; pheight=5.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.78; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.2,width,height], [offset+width+gap,0.2,width,height] };

    kprp = paper.k*sqrt(beta);

    i=2;
    EB = paper.Emp{i}; EE = paper.Eep{i};
    irhop = qom(1)*sqrt(mass(1))/paper.vthpp1{i};
    irhoa = qom(2)*sqrt(mass(2))/paper.vthpp3{i};
    irhoO = qom(3)*sqrt(mass(3))/paper.vthpp2{i};

    subplot(1,2,1);
    loglog(kprp,EB,'Color',myblue);
    hold on;
    loglog(kprp,EE,'Color',myred);
    %loglog(kprp(1:35),5e-3*kprp(1:35).^(-1.6666),'--k');
    loglog(irhop*[1 1],[1e-10 1e1],':k');
    loglog(irhoa*[1 1],[1e-10 1e1],':k');
    loglog(irhoO*[1 1],[1e-10 1e1],':k');
    hold off;
    axis([min(kprp) 10 3e-8 3]);
    yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$k_\perp\rho_{\rm p0}$');
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    text(0.2,1e-7,'$k_\perp\rho_{\rm O^{5+}}(t)=1$','Rotation',90,'Fontsize',10);
    text(0.34,1e-7,'$k_\perp\rho_\alpha(t)=1$','Rotation',90,'Fontsize',10);
    text(0.69,1e-7,'$k_\perp\rho_{\rm p}(t)=1$','Rotation',90,'Fontsize',10);
    leg = legend({'$~\mathcal{E}_B(k_\perp)$','$~\mathcal{E}_E(k_\perp)$'}, ...
    	'Location','NorthEast','Interpreter','latex','FontSize',10);
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.04,'xlabeldy',-0.04,'ytickdx',0.003);

    om = swarm.omega;
    bs = swarm.bprp{i}; es = swarm.eprp{i}; rhos = swarm.rho{i};
    %rhos

    subplot(1,2,2);
    loglog(om,bs,'Color',myblue)
    hold on
    loglog(om,es,'Color',myred)
    loglog(om,rhos,'Color',myorange)
    loglog(qom(1)*[1 1], [1e-10,1e1],':k');
    loglog(qom(2)*[1 1], [1e-10,1e1],':k');
    loglog(qom(3)*[1 1], [1e-10,1e1],':k');
    hold off;
    %axis([min(om) 4 1e-6 2e-3]);
    axis([min(om) 4 1e-10 2e-8]);
    %yticks([1e-6 1e-5 1e-4 1e-3]);
    xlabel('$\omega/\Omega_{\rm p0}$');
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %text(0.84,1.7e-6,'$\omega/\Omega_{\rm p,0}=1$','Rotation',90,'Fontsize',10);
    text(0.415,3e-6,'$\omega/\Omega_{\alpha0}=1$','Rotation',90,'Fontsize',10);
    text(0.26,3e-6,'$\omega/\Omega_{\rm O^{5+}0}=1$','Rotation',90,'Fontsize',10);
    leg = legend({'$~\mathcal{E}_B(\omega)$','$~\mathcal{E}_E(\omega)$','$~\mathcal{E}_\rho(\omega)$'}, ...
    	'Location','SouthWest','Interpreter','latex','FontSize',10);
    legend('boxoff');
    annotation('textarrow',[0.83 0.782],[0.79 0.74], ...
                'String','ICWs','Color','k', ...
                'Interpreter','latex','LineWidth',0.5,'HeadWidth',4,'HeadLength',7/1.5, ...
                'TextMargin',1,'VerticalAlignment','middle');
    plotTickLatex2D('xtickdy',-0.04,'xlabeldy',-0.04,'ytickdx',0.002);

end

if plotnbr==222

    name = 'half_tcorr_sim9';
    load([ savebase 'PlotSwarm-' name '.mat'],'swarm');
    load([ savebase 'PlotSpectrum1D-' name '.mat'],'paper');
    imbswarm = swarm; clear swarm;
    imbpaper = paper; clear paper;

    name = 'b_b3_sim1';
    load([ savebase 'PlotSwarm-' name '.mat'],'swarm');
    load([ savebase 'PlotSpectrum1D-' name '.mat'],'paper');
    balswarm = swarm; clear swarm;
    balpaper = paper; clear paper;

    figure(1222); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { '$t\approx 7.5\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };

    xo = [0.265,0.20]; yo = 1.6e-5*[1,1];
    xa = [0.47,0.34]; ya = 1.6e-5*[1,1];
    xp = [0.79,0.69]; yp = 1.6e-5*[1,1];

    kprp = imbpaper.k*sqrt(beta); om = imbswarm.omega;

    balkprp = balpaper.k*sqrt(beta); balom = balswarm.omega;
    balEB = balpaper.Emp{1}.*balkprp.^(5/3); balEE = balpaper.Eep{1}.*balkprp.^(5/3);
    balbs = balswarm.bprp{1}.*balom.^2; bales = balswarm.eprp{1}.*balom.^2;

    for i=1:2
        EB = imbpaper.Emp{i}.*kprp.^(5/3); EE = imbpaper.Eep{i}.*kprp.^(5/3);
        irhop = qom(1)*sqrt(mass(1))/imbpaper.vthpp1{i};
        irhoa = qom(2)*sqrt(mass(2))/imbpaper.vthpp3{i};
        irhoO = qom(3)*sqrt(mass(3))/imbpaper.vthpp2{i};

        subplot(2,2,i);
        loglog(kprp,EB,'Color',myblue,'LineWidth',1);
        hold on;
        loglog(kprp,EE,'Color',myred,'LineWidth',1);
        loglog(balkprp,balEB,'--','Color',myblue);
        loglog(balkprp,balEE,'--','Color',myred);
        %loglog(kprp(1:35),5e-3*kprp(1:35).^(-1.6666),'--k');
        loglog(irhop*[1 1],[1e-10 1e1],':k');
        loglog(irhoa*[1 1],[1e-10 1e1],':k');
        loglog(irhoO*[1 1],[1e-10 1e1],':k');
        hold off;
        axis([min(kprp) 10 9.9999999e-6 2e-2]);
        yticks(logspace(-5,-2,4)); yticklabels({'$10^{-5}$','$10^{-4}$','$10^{-3}$','$10^{-2}$'});
        xlabel('$k_\perp\rho_{\rm p0}$');
        title(tlab{i});
        set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{i});
        text(xo(i),yo(i),'$k_\perp\rho_{\rm O^{5+}}(t)=1$','Rotation',90,'Fontsize',10);
        text(xa(i),ya(i),'$k_\perp\rho_\alpha(t)=1$','Rotation',90,'Fontsize',10);
        text(xp(i),yp(i),'$k_\perp\rho_{\rm p}(t)=1$','Rotation',90,'Fontsize',10);
        leg = legend({'$\,\mathcal{E}_B(k_\perp)\,k^{5/3}_\perp$','$\,\mathcal{E}_E(k_\perp)\,k^{5/3}_\perp$'}, ...
            'Location','NorthEast','Interpreter','latex','FontSize',10);
        leg.ItemTokenSize = [25,18];
        legend('boxoff');
        plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    end

	for i=1:2
        bs = imbswarm.bprp{i}.*om.^2; es = imbswarm.eprp{i}.*om.^2;

        subplot(2,2,2+i);
        loglog(om,bs,'Color',myblue)
        hold on
        loglog(om,es,'Color',myred)
        loglog(balom,balbs,'--','Color',myblue);
        loglog(balom,bales,'--','Color',myred);
        loglog(qom(1)*[1 1], [1e-10,1e1],':k');
        loglog(qom(2)*[1 1], [1e-10,1e1],':k');
        loglog(qom(3)*[1 1], [1e-10,1e1],':k');
        hold off;
        axis([min(om) 4 1e-6 1e-3]);
        %yticks([1e-6 1e-5 1e-4 1e-3]);
        xlabel('$\omega/\Omega_{\rm p0}$');
        set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{2+i});
        %text(0.84,1.6e-6,'$\omega/\Omega_{\rm p,0}=1$','Rotation',90,'Fontsize',10);
        if i==1
            text(0.415,4.9e-5,'$\omega/\Omega_{\alpha0}=1$','Rotation',90,'Fontsize',10);
            text(0.26,3.1e-5,'$\omega/\Omega_{\rm O^{5+}0}=1$','Rotation',90,'Fontsize',10);
        end
        leg = legend({'$\,\mathcal{E}_B(\omega)\,\omega^2$','$\,\mathcal{E}_E(\omega)\,\omega^2$'}, ...
            'Location','NorthWest','Interpreter','latex','FontSize',10);
        leg.ItemTokenSize = [25,18];
        legend('boxoff');
        plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    end

    annotation('textarrow',[0.83 0.782],[0.39 0.34], ...
            'String','ICWs','Color','k', ...
            'Interpreter','latex','LineWidth',0.5,'HeadWidth',4,'HeadLength',7/1.5, ...
            'TextMargin',1,'VerticalAlignment','middle');

end

%
% VDFs
%
if plotnbr==3

% NOTE:
%   plotf0 is normalized such that SUM[ plotf0*(dvprp/vth0)*(dvprl/vth0) ] = 1
%   actual VDF = plotf0 / (vprp/vth0) / (2*pi*vth0^3)
%   looks like we've been setting pi*vth0^2 = 1 in our plotting of f(vprp),
%   so that the Maxwellian f(vprp) = exp(-vprp^2/vth^2).
%   Also, Maxwellian f(vprl) = 1/sqrt(pi) * exp(-vprl^2/vth^2)
%   --> 1 = int[ d(vprp/vth)^2 d(vprl/vth) f ]
%

    name = 'half_tcorr_sim9';
    load([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot');

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
    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$' };
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,\alpha 0}$','$w_\perp/v_{\rm th,O^{5+}0}$' };
    tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 9\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };
    levels  = { -0.40:1.2:11.5, -0.4:0.4:5.6, -0.4:0.4:3.8 };
    tposx   = [-3.1,-5.4,-10.2];
    tposy   = [5.1,7.45,12];

    for spec=1:3   % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        vprln = vprlq; vprpn = vprpq;

        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(spec),mass(spec),beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl);
        for i=1:3  % column: t = { 0.5,9,14.2 } tauA
            panel=3*(spec-1)+i; ii = 3*(i-1)+spec;
            subplot(3,3,panel);
            f0 = plotf0{ii};
            f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q';
            liminds = find(log10(f0./vprpn/2)<logfmin); f0(liminds) = 0;
            contourf(vprln,vprpn,log10(f0./vprpn/2).',logfmin:0.5:logfmax);
            C = caxis; caxis([logfmin,logfmax]);
            if i==3
                hold on;
                contour(cvprl,cvprp,out.',levels{spec},'k--','Linewidth',1);
                plot([-1 -1]/sqrt(beta)*oovth(spec),[0 15],'r--','linewidth',1);
                hold off;
                text(tposx(spec),tposy(spec),'$v_{\rm A}$','Color',myred);
            end
            axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
            set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
            set(gca,'Units','normalized','Position',normpos{panel});
            xlabel(xlab{spec},'interpreter','latex');
            if spec==1
                title(tlab{i});
            end
            if i==1
                ylabel(ylab{spec},'interpreter','latex');
                if spec==1
                    text(-5.1,4.9,'$i={\rm p}$','Fontsize',10);
                    plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.02);
                end
                if spec==2
                    text(-7.2,6.94,'$i=\alpha$','Fontsize',10);
                    plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.02);
                end
                if spec==3
                    text(-11.9,11.4,'$i={\rm O}^{5+}$','Fontsize',10);
                    plotTickLatex2D('xlabeldy',0.025,'ytickdx',0.002,'ylabeldx',-0.01);
                end
                if spec==3
                    cb = colorbar;
                    title(cb,'$\langle f_i\rangle $','interpreter','latex');
                    set(cb,'Position',cbpos,'Ticklength',0.01);
                    %set(cb,'Position',cbpos{spec},'Ticklength',0.04);
                    cb.Ticks=[-7 -6 -5 -4 -3 -2 -1];
                    cb.TickLabels={'$10^{-7}$','$10^{-6}$','$10^{-5}$','$10^{-4}$', ...
                        '$10^{-3}$','$10^{-2}$','$10^{-1}$'};
                    cb.TickLabelInterpreter='latex';
                    cb.FontSize=10; cb.LineWidth=1;
                end
            else
                set(gca,'YTickLabel',[]);
                plotTickLatex2D('xlabeldy',0.02);
            end
        end

    end


    figure(23); clf; pwidth=8.8; pheight=5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')

    spec=1;   % s = { p, alpha, O5+ }
    vprpn = vprp{spec}; vprln = vprl{spec}; dvprl = (vprln(2)-vprln(1))/2;
    f0 = plotf0{6+spec}; f0prp = dvprl*sum(f0,1)./vprpn;
    vth = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
    semilogx(vprpn/vth,f0prp*vth^2,'-','Color',myblue);
    hold on;
    spec=2;   % s = { p, alpha, O5+ }
    vprpn = vprp{spec}; vprln = vprl{spec}; dvprl = (vprln(2)-vprln(1))/2;
    f0 = plotf0{6+spec}; f0prp = dvprl*sum(f0,1)./vprpn;
    vth = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
    semilogx(vprpn/vth,f0prp*vth^2,'Color',myred);
    spec=3;   % s = { p, alpha, O5+ }
    vprpn = vprp{spec}; vprln = vprl{spec}; dvprl = (vprln(2)-vprln(1))/2;
    f0 = plotf0{6+spec}; f0prp = dvprl*sum(f0,1)./vprpn;
    vth = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
    semilogx(vprpn/vth,f0prp*vth^2,'Color',myorange);
    semilogx(vprpn,exp(-vprpn.^2),':k');
    hold off;
    axis([0.1 4 0 1]);
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',[0.163,0.21,0.82,0.74]);
    ylabel('$\langle f_i(w_\perp)\rangle$','interpreter','latex');
    xlabel('$w_\perp/v_{{\rm th}\perp,i}(t)$','interpreter','latex');
    text(1.8,0.885,'$i=$','Interpreter','latex','FontSize',10);
    text(0.125,0.11,'${\rm imbalanced}\!:~t\approx 14.2\tau_{\rm A}$');
    leg = legend({'$~{\rm p}$','$~\alpha$','$~{\rm O}^{5+}$'}, ...
    	'Position',[0.72 0.58 0.2462 0.2628],'Interpreter','latex','FontSize',10);
    legend('boxoff');
    plotTickLatex2D('xlabeldy',-0.05,'xtickdy',-0.04,'ylabeldx',-0.03,'ytickdx',-0.005);


    name = 'b_b3_sim1';
    load([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot');

    figure(33); clf; pwidth=8.8; pheight=12;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')

    width = 5.15/pwidth; height=0.5*(pwidth/pheight)*width; offset = 0.205;
    normpos = { [offset,0.74,width,height], ...
                [offset,0.42,width,height], ...
                [offset,0.10,width,height] };
    cbpos   = [0.615+offset 0.1 0.033 0.855];

    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+} 0}$' };
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,\alpha 0}$','$w_\perp/v_{\rm th,O^{5+} 0}$' };
    tlab    = '${\rm balanced}\!:~t\approx 7\tau_{\rm A}$';
    levels  = { -0.40:1.2:11.5, -0.4:0.4:5.6, -0.4:0.4:3.8 };

    for spec=1:3   % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        vprln = vprlq; vprpn = vprpq;

        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(spec),mass(spec),beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl);
        i=3;  % column: t = { 7 } tauA
        panel=spec; ii = 3*(i-1)+spec;

        subplot(3,1,panel);
        f0 = plotf0{ii};
        f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q';
        liminds = find(log10(f0./vprpn/2)<logfmin); f0(liminds) = 0;
        contourf(vprln,vprpn,log10(f0./vprpn/2).',logfmin:0.5:logfmax);
        C = caxis; caxis([logfmin,logfmax]);
        %hold on;
        %contour(cvprl,cvprp,out.',levels{spec},'k--','Linewidth',1);
        %plot([-1 -1]/sqrt(beta)*oovth(spec),[0 15],'r--','linewidth',1);
        %hold off;
        axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
        set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{panel});
        xlabel(xlab{spec},'interpreter','latex');
        if spec==1
            title(tlab);
        end
        ylabel(ylab{spec},'interpreter','latex');
        if spec==1
            text(-5.1,4.9,'$i={\rm p}$','Fontsize',10);
            plotTickLatex2D('xlabeldy',0.025,'ytickdx',-0.005,'ylabeldx',-0.042);
        end
        if spec==2
            text(-7.2,6.94,'$i=\alpha$','Fontsize',10);
            plotTickLatex2D('xlabeldy',0.025,'ytickdx',-0.005,'ylabeldx',-0.042);
        end
        if spec==3
            text(-11.9,11.4,'$i={\rm O}^{5+}$','Fontsize',10);
            plotTickLatex2D('xlabeldy',0.025,'ytickdx',-0.005,'ylabeldx',-0.021);
            cb = colorbar;
            title(cb,'$\langle f_i\rangle $','interpreter','latex');
            set(cb,'Position',cbpos,'Ticklength',0.01);
            cb.Ticks=[-7 -6 -5 -4 -3 -2 -1];
            cb.TickLabels={'$10^{-7}$','$10^{-6}$','$10^{-5}$','$10^{-4}$', ...
                '$10^{-3}$','$10^{-2}$','$10^{-1}$'};
            cb.TickLabelInterpreter='latex';
            cb.FontSize=10; cb.LineWidth=1;
        end

    end


    figure(43); clf; pwidth=8.8; pheight=5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')

    spec=1;   % s = { p, alpha, O5+ }
    vprpn = vprp{spec}; vprln = vprl{spec}; dvprl = (vprln(2)-vprln(1))/2;
    f0 = plotf0{6+spec}; f0prp = dvprl*sum(f0,1)./vprpn;
    vth = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
    semilogx(vprpn/vth,f0prp*vth^2,'-','Color',myblue);
    hold on;
    spec=2;   % s = { p, alpha, O5+ }
    vprpn = vprp{spec}; vprln = vprl{spec}; dvprl = (vprln(2)-vprln(1))/2;
    f0 = plotf0{6+spec}; f0prp = dvprl*sum(f0,1)./vprpn;
    vth = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
    semilogx(vprpn/vth,f0prp*vth^2,'Color',myred);
    spec=3;   % s = { p, alpha, O5+ }
    vprpn = vprp{spec}; vprln = vprl{spec}; dvprl = (vprln(2)-vprln(1))/2;
    f0 = plotf0{6+spec}; f0prp = dvprl*sum(f0,1)./vprpn;
    vth = sqrt(sum(sum(f0.*vprpn.^2))/sum(sum(f0)));    % vth_prp has increased by this amount
    semilogx(vprpn/vth,f0prp*vth^2,'Color',myorange);
    semilogx(vprpn,exp(-vprpn.^2),':k');
    hold off;
    axis([0.1 4 0 1]);
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',[0.163,0.21,0.82,0.74]);
    ylabel('$\langle f_i(w_\perp)\rangle$','interpreter','latex');
    xlabel('$w_\perp/v_{{\rm th}\perp,i}(t)$','interpreter','latex');
    text(1.8,0.885,'$i=$','Interpreter','latex','FontSize',10);
    text(0.125,0.11,'${\rm balanced}\!:~t\approx 7\tau_{\rm A}$');
    leg = legend({'$~{\rm p}$','$~\alpha$','$~{\rm O}^{5+}$'}, ...
    	'Position',[0.72 0.58 0.2462 0.2628],'Interpreter','latex','FontSize',10);
    legend('boxoff');
    plotTickLatex2D('xlabeldy',-0.05,'xtickdy',-0.04,'ylabeldx',-0.03,'ytickdx',-0.005);

end  % plotnbr==3

if plotnbr ==33 %3x1 VDF plot
    rebinN  = 250;
    logfmin = -7.5; logfmax = -0.5;

    vmaxarr = { 10,20,20 };
    vmaxplt = { 6,8.5,14 };
    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+}0}$' };
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,\alpha 0}$','$w_\perp/v_{\rm th,O^{5+}0}$' };
    tlab    = { '${\rm imbalanced}\!:~t\approx 0.5\tau_{\rm A}$','$t\approx 9\tau_{\rm A}$','$t\approx 14.2\tau_{\rm A}$' };
    levels  = { -0.40:1.2:11.5, -0.4:0.4:5.6, -0.4:0.4:3.8 };
    tposx   = [-3.1,-5.4,-10.2];
    tposy   = [5.1,7.45,12];
    name = 'b_b3_sim1';
    load([ savebase 'PlotDFs-' name '.mat'],'plotf0','vprl','vprp','tav','vthtot');

    figure(33); clf; pwidth=18.5; pheight=4.0;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters')

    width = 5.15/pwidth; height=0.5*(pwidth/pheight)*width; offset = 0.0038*pwidth;
    gap = 0.007;
    normpos = { [offset,0.20,width,height], ...
                [offset+(gap+width),0.20,width,height], ...
                [offset+(gap+width)*2.0,0.20,width,height] };
    cbpos   = [0.933 0.10 0.0157 0.855];

    xlab    = { '$w_\|/v_{\rm th,p0}$','$w_\|/v_{\rm th,\alpha 0}$','$w_\|/v_{\rm th,O^{5+} 0}$' };
    ylab    = { '$w_\perp/v_{\rm th,p0}$','$w_\perp/v_{\rm th,\alpha 0}$','$w_\perp/v_{\rm th,O^{5+} 0}$' };
    tlab    = '${\rm balanced}\!:~t\approx 7\tau_{\rm A}$';
    levels  = { -0.40:1.2:11.5, -0.4:0.4:5.6, -0.4:0.4:3.8 };

    for spec=1:3  % row: s = { p,alpha,O5+ }
        vprpn = vprp{spec}; vprln = vprl{spec}'; vmax = vmaxarr{spec}; vplt = vmaxplt{spec};
        vprlq = linspace(-vmax,vmax,2*rebinN); vprpq = linspace(0,vmax,rebinN);
        [vlq,vpq] = meshgrid(vprlq,vprpq); [vln,vpn] = meshgrid(vprln,vprpn);
        vprln = vprlq; vprpn = vprpq;

        [out, cvprp, cvprl, yres] = resonanceContoursMinorIon(qom(spec),mass(spec),beta,2,4);
        %[out,outva,vprlhalf] = resonanceContours(vprp,vprl);
        i=3;  % column: t = { 7 } tauA
        panel=spec; ii = 3*(i-1)+spec;

        subplot(1,3,panel);
        f0 = plotf0{ii};
        f0q = interp2(vln,vpn,f0',vlq,vpq); f0 = f0q';
        liminds = find(log10(f0./vprpn/2)<logfmin); f0(liminds) = 0;
        contourf(vprln,vprpn,log10(f0./vprpn/2).',logfmin:0.5:logfmax);
        C = caxis; caxis([logfmin,logfmax]);
        %hold on;
        %contour(cvprl,cvprp,out.',levels{spec},'k--','Linewidth',1);
        %plot([-1 -1]/sqrt(beta)*oovth(spec),[0 15],'r--','linewidth',1);
        %hold off;
        axis equal; xlim([-vplt vplt]); ylim([0 vplt]);
        set(gca,'YDir','normal','TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
        set(gca,'Units','normalized','Position',normpos{panel});
        xlabel(xlab{spec},'interpreter','latex');
        if spec==1
            title(tlab);
        end
        ylabel(ylab{spec},'interpreter','latex');
        if spec==1
            text(-5.1,4.9,'$i={\rm p}$','Fontsize',10);
            plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025,'ytickdx',0,'ylabeldx',0);
        end
        if spec==2
            text(-7.2,6.94,'$i=\alpha$','Fontsize',10);
            plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025,'ytickdx',-0.005,'ylabeldx',-0.042);
        end
        if spec==3
            text(-11.9,11.4,'$i={\rm O}^{5+}$','Fontsize',10);
            plotTickLatex2D('xtickdy',-0.05,'xlabeldy',-0.025,'ytickdx',-0.005,'ylabeldx',-0.021);
            cb = colorbar;
            title(cb,'$\langle f_i\rangle $','interpreter','latex');
            set(cb,'Position',cbpos,'Ticklength',0.01);
            cb.Ticks=[-7 -6 -5 -4 -3 -2 -1];
            cb.TickLabels={'$10^{-7}$','$10^{-6}$','$10^{-5}$','$10^{-4}$', ...
                '$10^{-3}$','$10^{-2}$','$10^{-1}$'};
            cb.TickLabelInterpreter='latex';
            cb.FontSize=10; cb.LineWidth=1;
        end

    end
end %33


% heating rates
if plotnbr==4
    load([ savebase 'PlotQ-all.mat'],'Q');

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { 'Imbalanced','Balanced' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    p1 = plot(nan,nan,'k');
    hold on
    p2 = plot(nan,nan,'k--');
    plot(Q.t1,Q.qp1{1},'Color',myblue,'LineWidth',1)
    plot(Q.t1,Q.ql1{1},'--','Color',myblue,'LineWidth',1)
    plot(Q.t1,Q.qp1{3},'Color',myred,'LineWidth',1)
    plot(Q.t1,Q.ql1{3},'--','Color',myred,'LineWidth',1)
    plot(Q.t1,Q.qp1{2},'Color',myorange,'LineWidth',1)
    plot(Q.t1,Q.ql1{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','NorthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    p1 = plot(nan,nan,'k');
    hold on
    p2 = plot(nan,nan,'k--');
    plot(Q.t2,Q.qp2{1},'Color',myblue,'LineWidth',1)
    plot(Q.t2,Q.ql2{1},'--','Color',myblue,'LineWidth',1)
    plot(Q.t2,Q.qp2{3},'Color',myred,'LineWidth',1)
    plot(Q.t2,Q.ql2{3},'--','Color',myred,'LineWidth',1)
    plot(Q.t2,Q.qp2{2},'Color',myorange,'LineWidth',1)
    plot(Q.t2,Q.ql2{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','NorthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);
    plot(Q.t1,Q.qp1{1},'Color',myblue,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    plot(Q.t1,Q.qp1{3}/(1.35*mass(2)),'Color',myred,'LineWidth',1)
    plot(Q.t1,Q.qp1{2}/(1.35*mass(3)),'Color',myorange,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha}/(1.35 m_{\rm \alpha})$','$Q_{\perp,\rm O^{5+}}/(1.35 m_{\rm O^{5+}})$', ...
        'Location','NorthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);

    a=0.3;
    subplot(2,2,4);
    plot(Q.t2,Q.qp2{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) ) * 3/2,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        plot(Q.t2,Q.qp2{i}./(massog(i)*(massog(i)/chargeog(i))^(2.*a/(1-a) )),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('$3Q_{\perp,p}/2$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm Fe^{9+}} (Z/A)^{2a\eta}/A$', ...
    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==4

% log heating rates
if plotnbr==42
    load([ savebase 'PlotQ-all.mat'],'Q');

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { 'Imbalanced','Balanced' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    semilogy(Q.t1,Q.qp1{1},'Color',myblue,'LineWidth',1)
    semilogy(Q.t1,Q.ql1{1},'--','Color',myblue,'LineWidth',1)
    semilogy(Q.t1,Q.qp1{3},'Color',myred,'LineWidth',1)
    semilogy(Q.t1,Q.ql1{3},'--','Color',myred,'LineWidth',1)
    semilogy(Q.t1,Q.qp1{2},'Color',myorange,'LineWidth',1)
    semilogy(Q.t1,Q.ql1{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    ylim([ 1e-3 5]);
    yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    semilogy(Q.t2,Q.qp2{1},'Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.ql2{1},'--','Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.qp2{3},'Color',myred,'LineWidth',1)
    semilogy(Q.t2,Q.ql2{3},'--','Color',myred,'LineWidth',1)
    semilogy(Q.t2,Q.qp2{2},'Color',myorange,'LineWidth',1)
    semilogy(Q.t2,Q.ql2{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    ylim([ 1e-3 5]);
    yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    a = 0.3;
    subplot(2,2,3);
    %semilogy(Q.t1,Q.qp1{1},'Color',myblue,'LineWidth',1)
    semilogy(Q.t1,Q.tep1{1}.^2,'Color',myblue,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    %semilogy(Q.t1,Q.qp1{3}/(1.35*mass(2)),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}/(1.35*mass(3)),'Color',myorange,'LineWidth',1)
    semilogy(Q.t1,Q.tep1{3}.^2/(1.35*massog(3)),'Color',myred,'LineWidth',1)
    semilogy(Q.t1,Q.tep1{2}.^2/(1.35*massog(2)),'Color',myorange,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-3 1]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha}/(1.35 m_{\rm \alpha})$','$Q_{\perp,\rm O^{5+}}/(1.35 m_{\rm O^{5+}})$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$', ...
    %'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);

    a = 0.3;
    subplot(2,2,4);
    %semilogy(Q.t2,Q.qp2{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) ) * 3/2,'Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.tep2{1}.^2./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) ) * 3/2,'Color',myblue,'LineWidth',1)
    %plot(Q.t2,Q.qp2{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'--','Color',myblue,'LineWidth',1)
    hold on
    %semilogy(Q.t2,Q.qp2{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*0.25/0.75) ),'Color',myred,'LineWidth',1)
    %semilogy(Q.t2,Q.qp2{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*0.25/0.75) ),'Color',myorange,'LineWidth',1)
    for i = plotorder_trunc
        disp(colorder{i})
        %semilogy(Q.t2,Q.qp2{i}./(massog(i)*(massog(i)/chargeog(i))^(2.*a/(1-a) )),'Color',colorder{i},'LineWidth',1)
        semilogy(Q.t2,Q.tep2{i}.^2./(massog(i)*(massog(i)/chargeog(i))^(2.*a/(1-a) )),'Color',colorder{i},'LineWidth',1)
    end
    %semilogy(Q.t2,Q.qp2{2}./Q.qp2{1},'Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-4 1e-1]);
    %yticks(logspace(-4,-1,4)); yticklabels({'$10^{-4}$','$10^{-3}$','$10^{-2}$','$10^{-1}$'});
    %ylim([ 1 100]);
    %yticks(logspace(1,10,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('$Q_{\perp,p}/0.71$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg = legend('$3Q_{\perp,p}/2$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm Fe^{9+}} (Z/A)^{2a\eta}/A$', ...
    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==42

% log heating rates
if plotnbr==43
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    b03Q = Q; clear Q;
    name = 'hb_beta0625';
    load([ savebase 'PlotQ-' name '.mat'],'Q');
    b0625Q = Q; clear Q;

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { 'Imbalanced','Balanced' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    for i = plotorder
        semilogy(b0625Q.t,b0625Q.qp{i},'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-3 100]);
    yticks(logspace(-3,1,5)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$','$10^1$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    semilogy(b03Q.t2,b03Q.qp2{1},'Color',myblue,'LineWidth',1)
    semilogy(b03Q.t2,b03Q.ql2{1},'--','Color',myblue,'LineWidth',1)
    semilogy(b03Q.t2,b03Q.qp2{3},'Color',myred,'LineWidth',1)
    semilogy(b03Q.t2,b03Q.ql2{3},'--','Color',myred,'LineWidth',1)
    semilogy(b03Q.t2,b03Q.qp2{2},'Color',myorange,'LineWidth',1)
    semilogy(b03Q.t2,b03Q.ql2{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    ylim([ 1e-3 5]);
    yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);
    semilogy(b0625Q.t,b0625Q.tep{1}.^2,'Color',myblue,'LineWidth',1)
    %semilogy(b0625Q.t,b0625Q.qp{1},'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(b0625Q.t,b0625Q.tep{i}.^2*charge0625(i)^0.55/(mass0625(i)^1.7),'Color',colorder{i},'LineWidth',1)
        %semilogy(b0625Q.t,b0625Q.qp{i}/(mass0625(i)^1.07),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %ylim([ 1e-3 1]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha}/(1.35 m_{\rm \alpha})$','$Q_{\perp,\rm O^{5+}}/(1.35 m_{\rm O^{5+}})$','$Q_{\perp,\rm O^{6+}}/(1.35 m_{\rm O^{6+}})$','$Q_{\perp,\rm C^{6+}}/(1.35 m_{\rm C^{6+}})$','$Q_{\perp,\rm C^{5+}}/(1.35 m_{\rm C^{5+}})$','$Q_{\perp,\rm Mg^{9+}}/(1.35 m_{\rm Mg^{9+}})$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);

    a = 0.29
    subplot(2,2,4);
    %semilogy(Q.t2,Q.qp2{3}./Q.qp2{1},'Color',myred,'LineWidth',1)
    plot(b03Q.t2,b03Q.qp2{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'--','Color',myblue,'LineWidth',1)
    hold on
    %semilogy(Q.t2,Q.qp2{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*0.25/0.75) ),'Color',myred,'LineWidth',1)
    %semilogy(Q.t2,Q.qp2{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*0.25/0.75) ),'Color',myorange,'LineWidth',1)
    for i = plotorder_trunc
        disp(colorder{i})
        plot(b03Q.t2,b03Q.qp2{i}./(massog(i)*(massog(i)/chargeog(i))^(2.*a/(1-a) )),'--','Color',colorder{i},'LineWidth',1)
    end
    %semilogy(Q.t2,Q.qp2{2}./Q.qp2{1},'Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-3 1]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    %ylim([ 1 100]);
    %yticks(logspace(1,10,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('$Q_{\perp,p}/0.71$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm Fe^{9+}} (Z/A)^{2a\eta}/A$', ...
    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==43



% heating rates % imbalanced vs balanced comparison (beta=0.0625)
if plotnbr==444
    load([ savebase 'PlotQ-allb0625.mat'],'Q');

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { 'Imbalanced','Balanced' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    for i = plotorder
        semilogy(Q.t1,Q.qp1{i},'Color',colorder{i},'LineWidth',1)
        semilogy(Q.t1,Q.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-1 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('$Q_i/\varepsilon_{\rm inj}~(\perp: {\rm solid};\,\parallel:{\rm dashed})$')
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    for i = plotorder
        semilogy(Q.t2,Q.qp2{i},'Color',colorder{i},'LineWidth',1)
        semilogy(Q.t2,Q.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q.t1,Q.tep1{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q.t1,Q.tep1{i}.^2/(mass0625(i)^1.07),'Color',colorder{i},'LineWidth',1)
    end
    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-1.07}$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a=0.3;
    subplot(2,2,4);
    %plot(Q.t2,log(Q.qp2{1})./(massog(1)^(1/3)*chargeog(1)^(-1/3) ./(Q.tep2{1} .^(1/3))),'Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.tep2{1}.^2,'Color',colorder{1},'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q.t2,Q.tep2{i}.^2./(mass0625(i)^(1.07)),'Color',colorder{i},'LineWidth',1)
    end
    %for i = plotorder_trunc_3
    %    plot(Q.t2,Q.tep2{i}.^2./(1.35 * massog(i)),'--','Color',colorder{i},'LineWidth',1)
    %end
    hold off;
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==444



% heating rates
if plotnbr==44
    load([ savebase 'PlotQ-allb3.mat'],'Q');

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { 'Imbalanced','Balanced' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');

    semilogy(Q.t1,Q.qp1{1},'Color',myblue,'LineWidth',1)
    semilogy(Q.t1,Q.ql1{1},'--','Color',myblue,'LineWidth',1)
    semilogy(Q.t1,Q.qp1{3},'Color',myred,'LineWidth',1)
    semilogy(Q.t1,Q.ql1{3},'--','Color',myred,'LineWidth',1)
    semilogy(Q.t1,Q.qp1{2},'Color',myorange,'LineWidth',1)
    semilogy(Q.t1,Q.ql1{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    semilogy(Q.t2,Q.qp2{1},'Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.ql2{1},'--','Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.qp2{3},'Color',myred,'LineWidth',1)
    semilogy(Q.t2,Q.ql2{3},'--','Color',myred,'LineWidth',1)
    semilogy(Q.t2,Q.qp2{2},'Color',myorange,'LineWidth',1)
    semilogy(Q.t2,Q.ql2{2},'--','Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);
    plot(Q.t1,Q.tep1{1}.^2,'Color',myblue,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    plot(Q.t1,Q.tep1{3}.^2/(massog(3)^1.05),'Color',myred,'LineWidth',1)
    plot(Q.t1,Q.tep1{2}.^2/(massog(2)^1.05),'Color',myorange,'LineWidth',1)

    %plot(Q.t1,Q.tep1{3}.^2/(1.35 * massog(3)),'--','Color',myred,'LineWidth',1)
    %plot(Q.t1,Q.tep1{2}.^2/(1.35 * massog(2)),'--','Color',myorange,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('$T_{\perp,\rm p}$','$T_{\perp,\rm \alpha}/m_{\rm \alpha}^{1.07}$','$T_{\perp,\rm O^{5+}}/m_{\rm O^{5+}}^{1.07}$','$T_{\perp,\rm \alpha}/1.35 m_{\rm \alpha}$','$T_{\perp,\rm O^{5+}}/1.35 m_{\rm O^{5+}}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);

    a=0.3;
    subplot(2,2,4);
    %plot(Q.t2,log(Q.qp2{1})./(massog(1)^(1/3)*chargeog(1)^(-1/3) ./(Q.tep2{1} .^(1/3))),'Color',myblue,'LineWidth',1)
    semilogy(Q.t2,Q.tep2{1}.^2,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc_3
        semilogy(Q.t2,Q.tep2{i}.^2./(massog(i)^(1.07)),'Color',colorder{i},'LineWidth',1)
    end
    %for i = plotorder_trunc_3
    %    plot(Q.t2,Q.tep2{i}.^2./(1.35 * massog(i)),'--','Color',colorder{i},'LineWidth',1)
    %end
    hold off;
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('$T_{\perp,\rm p}$','$T_{\perp,\rm \alpha}/m_{\rm \alpha}^{1.07}$','$T_{\perp,\rm O^{5+}}/m_{\rm O^{5+}}^{1.07}$','$T_{\perp,\rm \alpha}/1.35 m_{\rm \alpha}$','$T_{\perp,\rm O^{5+}}/1.35 m_{\rm O^{5+}}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==44



% heating rates % imbalanced Q vs imbalanced T comparison (beta=0.0625)
if plotnbr==4444
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q

    a=0.7

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "$\beta = 0.3$","$\beta = 1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    semilogy(Q03.t1,Q03.qp1{1}/(massog(1)*(massog(1)/chargeog(1))^a),'Color',colorder{1},'LineWidth',1)
    hold on
    for i = plotorder_trunc_3
        semilogy(Q03.t1,Q03.qp1{i}/(massog(i)*(massog(i)/chargeog(i))^a),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-1 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('($Q_i/\varepsilon_{\rm inj}) \,(m_i/m_{\rm p})(m_i q_{\rm p}/m_{\rm p} q_i)^{b}$')
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    semilogy(Q0625.t1,Q0625.qp1{1}/(mass0625(1)^1.07),'Color',colorder{1},'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.qp1{i}/(mass0625(i)*(mass0625(i)/charge0625(i))^a),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-1 2e2]);
    %ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q03.t1,Q03.tep1{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc_3
        semilogy(Q03.t1,Q03.tep1{i}.^2/(massog(i)*(massog(i)/chargeog(i))^a),'Color',colorder{i},'LineWidth',1)
    end
    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})(m_i q_{\rm p}/m_{\rm p} q_i)^{b}$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    semilogy(Q0625.t1,Q0625.tep1{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.tep1{i}.^2/(mass0625(i)*(mass0625(i)/charge0625(i))^a),'Color',colorder{i},'LineWidth',1)
    end

    hold off;
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==4444


% heating rates % balanced Q vs balanced T comparison 
if plotnbr==44444
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q

    %a=0.7;
    a=0.6/0.7;
    dd = 1.0;%1.55;%beta=0.3 T
    ee = 0.0;%0.50;

    %a = 1.7;
    %b = 0.75; from plotnbr=488 fitting to balanced b0625 temp
    dd = 0.95;%1.55;%beta=0.3 T
    ee = 0.0;%0.50;
    a= 0.75

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "$\beta = 0.3$","$\beta = 1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    semilogy(Q03.t2,Q03.qp2{1}/(massog(1)^dd/chargeog(1)^ee*(massog(1)/chargeog(1))^a),'Color',colorder{1},'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q03.t2,Q03.qp2{i}/(massog(i)^dd/chargeog(i)^ee*(massog(i)/chargeog(i))^a),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-1 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('($Q_i/\varepsilon_{\rm inj}) \,(m_i/m_{\rm p})(m_i q_{\rm p}/m_{\rm p} q_i)^{b}$')
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    semilogy(Q0625.t2,Q0625.qp2{1},'Color',colorder{1},'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.qp2{i}/(mass0625(i)^dd/charge0625(i)^ee*(mass0625(i)/charge0625(i))^a),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-1 2e2]);
    %ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q03.t2,Q03.tep2{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q03.t2,Q03.tep2{i}.^2/(massog(i)^dd/chargeog(i)^ee*(massog(i)/chargeog(i))^a),'Color',colorder{i},'LineWidth',1)
    end
    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})(m_i q_{\rm p}/m_{\rm p} q_i)^{b}$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    semilogy(Q0625.t2,Q0625.tep2{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.tep2{i}.^2/(mass0625(i)^dd/charge0625(i)^ee*(mass0625(i)/charge0625(i))^a),'Color',colorder{i},'LineWidth',1)
    end

    hold off;
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==44444



%  (beta=0.0625) perp+parallel heating rates and temperatures
if plotnbr==44445
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q

    a=0.7

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced","balanced" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    semilogy(Q0625.t1,Q0625.qp1{1}./dedt_imb0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.qp1{i}./dedt_imb0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t1,Q0625.ql1{i}./dedt_imb0625,'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-2 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('($Q_i/\varepsilon_{\rm inj})$')
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    semilogy(Q0625.t2,Q0625.qp2{1}./dedt_bal0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.qp2{i}./dedt_bal0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t2,Q0625.ql2{i}./dedt_bal0625,'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-2 2e2]);
    %ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q0625.t1,Q0625.tep1{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    %semilogy(Q0625.t1,Q0625.tel1{1}.^2,'Color',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.tep1{i}.^2,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.tel1{i}.^2,'--','Color',colorder{i},'LineWidth',1)
    end

    for i = plotorder
        semilogy(Q0625.t1,Q0625.tel1{i}.^2,'--','Color',colorder{i},'LineWidth',1)
    end

    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    semilogy(Q0625.t2,Q0625.tep2{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.tep2{i}.^2,'Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t2,Q0625.tel2{i}.^2,'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==44445



%  (beta=0.0625+beta=0.3, balanced and imb) perp+parallel heating rates
if plotnbr==48
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q

    a=0.7

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced, $\beta=0.3$","balanced, $\beta=0.3$", "imbalanced, $\beta=1/16$", "balanced, $\beta=1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    semilogy(Q03.t1,Q03.qp1{1}./dedt_imb03,'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        semilogy(Q03.t1,Q03.qp1{i}./dedt_imb03,'Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder_3
        semilogy(Q03.t1,Q03.ql1{i}./dedt_imb03,'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q03.t1,Q03.eps_noE1./dedt_imb03,'k');
    hold off;
    xlim([0 15]);
    ylim([ 1e-2 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('$Q_i/\varepsilon_{\rm inj}~(\perp: {\rm solid};\,\parallel:{\rm dashed})$')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    semilogy(Q03.t2,Q03.qp2{1}./dedt_bal03,'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q03.t2,Q03.qp2{i}./dedt_bal03,'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q03.t2,Q03.ql2{i}./dedt_bal03,'--','Color',colorderfe{i},'LineWidth',1)
    end
    p3 = semilogy(Q03.t2,Q03.eps_noE2./dedt_bal03,'k');
    hold off;
    xlim([0 8]);
    ylim([ 1e-2 2e2]);
    %ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q0625.t1,Q0625.qp1{1}./dedt_imb0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.qp1{i}./dedt_imb0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t1,Q0625.ql1{i}./dedt_imb0625,'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q0625.t1,Q0625.eps_noE1./dedt_imb0625,'k');
    hold off;
    title(tlab{3});
    xlim([0 15]);
    ylim([ 1e-2 2e2]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    semilogy(Q0625.t2,Q0625.qp2{1}./dedt_bal0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.qp2{i}./dedt_bal0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t2,Q0625.ql2{i}./dedt_bal0625,'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q0625.t2,Q0625.eps_noE2./dedt_bal0625,'k');
    hold off;
    title(tlab{4});
    xlim([0 8]);
    ylim([ 1e-2 2e2]);
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==48


%  (beta=0.0625+beta=0.3, balanced and imb) heating rates scaled
if plotnbr==487
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q


    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced, $\beta=0.3$","balanced, $\beta=0.3$", "imbalanced, $\beta=1/16$", "balanced, $\beta=1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];

    %a = 1.07;% (m)
    %b = 0; % (q)

    %a=1.55;
    %b=0.6;
    a = 1.77;
    b = 0.75;%0.7;

    a = 1.55;
    b = 0.6;%0.7;
    subplot(2,2,1);
    semilogy(Q03.t1,Q03.qp1{1}./dedt_imb03,'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        semilogy(Q03.t1,Q03.qp1{i}./dedt_imb03/(massog(i)^a / chargeog(i)^b),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    xlim([0 15]);
    ylim([ 1e-2 2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    %ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    ylabel('$(Q_{\perp,i}/Q_{\perp,i0})$')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);

    a = 0;
    b = 0;
    % makes C6 and O6 surround C5 and O5. C5 and O5 matched well
    %10% difference with alphas
    a = 1.77;
    b = 0.75;%0.7;
    %<10% difference with alphas
    % makes O6 and O5 surround C6 and C5. C6 and C5 matched well
    %a = 1.58;
    %b = 0.51;
    % makes C5 and O5 surround C6 and O6. C6 and O6 matched well



    a = 1.55;
    b = 0.6;%0.7;
    subplot(2,2,2);
    semilogy(Q03.t2,Q03.qp2{1}./dedt_bal03,'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q03.t2,Q03.qp2{i}./dedt_bal03/(massog(i)^a / chargeog(i)^b),'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    xlim([0 8]);
    ylim([ 1e-2 2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    %to 8tauA
    a = 1.53;
    b = 0.65;
    % matches O5 and C5, with O6 and C6 surrounding. poor match with other
    % minors
    a = 1.7;
    b = 0.7;
    % matches O6 and C6, O5 C5 surrounding. Mg match. But alphas higher -
    % so some missing mass scaling?
    % to 10.5tauA
    a=1.67;
    b=0.62;
    % matches O6 and C6, O5 C5 surrounding.
    %a=1.5025;
    %b=0.63;
    %match O5 and C5
    %a=1.6;
    %b=0.45;
    %ignore matching specific species - try to get everything vaguely
    %around protons (in between)
    %a=1.3;
    %b=0;
    % mass only


    a = 1.77;
    b = 0.75;%0.7;


    a = 1.55;
    b = 0.6;%0.7;
    semilogy(Q0625.t1,Q0625.qp1{1}./dedt_imb0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.qp1{i}./dedt_imb0625/(mass0625(i)^a / charge0625(i)^b),'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{3});
    xlim([0 15]);
    ylim([ 1e-2 2]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);



    %a = 1.75;
    %b = 0.75;
    % matches O5 and C5, C6 and O6 around. worse match for alphas
    a = 1.7;
    b = 0.75;
    % matches O6 and C6, C5 and O5 around. Mg and alphas a little away but
    % overlapping



    a = 1.77;
    b = 0.75;%0.7;


    a = 1.55;
    b = 0.6;%0.7;
    subplot(2,2,4);
    semilogy(Q0625.t2,Q0625.qp2{1}./dedt_bal0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.qp2{i}./dedt_bal0625/(mass0625(i)^a / charge0625(i)^b),'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{4});
    xlim([0 8]);
    ylim([ 1e-2 2]);
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==487


%  (beta=0.0625+beta=0.3, balanced and imb) temperatures scaled
if plotnbr==488
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q


    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced, $\beta=0.3$","balanced, $\beta=0.3$", "imbalanced, $\beta=1/16$", "balanced, $\beta=1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];

    a = 1.07;% (m)
    b = 0; % (q)

    %a=1.55;
    %b=0.6;



    a = 1.66;
    b = 0.66;%0.7;
    subplot(2,2,1);
    semilogy(Q03.t1,Q03.tep1{1}.^2,'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        semilogy(Q03.t1,Q03.tep1{i}.^2/(massog(i)^a / chargeog(i)^b),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    xlim([0 15]);
    ylim([ 1e-2 2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    %ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);

    a = 1.5;
    b = 0.53;
    % makes C6 and O6 surround C5 and O5. C5 and O5 matched well
    %10% difference with alphas
    a = 1.55;
    b = 0.6;
    %<10% difference with alphas
    % makes O6 and O5 surround C6 and C5. C6 and C5 matched well
    %a = 1.58;
    %b = 0.51;
    % makes C5 and O5 surround C6 and O6. C6 and O6 matched well




    %a = 1.66;
    %b = 0.66;%0.7;


    subplot(2,2,2);
    semilogy(Q03.t2,Q03.tep2{1}.^2,'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q03.t2,Q03.tep2{i}.^2/(massog(i)^a / chargeog(i)^b),'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    xlim([0 8]);
    ylim([ 1e-2 2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    %to 8tauA
    a = 1.53;
    b = 0.65;
    % matches O5 and C5, with O6 and C6 surrounding. poor match with other
    % minors
    a = 1.7;
    b = 0.7;
    % matches O6 and C6, O5 C5 surrounding. Mg match. But alphas higher -
    % so some missing mass scaling?
    % to 10.5tauA
    a=1.67;
    b=0.62;
    % matches O6 and C6, O5 C5 surrounding.
    %a=1.5025;
    %b=0.63;
    %match O5 and C5
    %a=1.6;
    %b=0.45;
    %ignore matching specific species - try to get everything vaguely
    %around protons (in between)
    %a=1.3;
    %b=0;
    % mass only


    %a = 1.66;
    %b = 0.66;%0.7;
    %to 12 t_A
    a=1.65;
    b=0.6;
    semilogy(Q0625.t1,Q0625.tep1{1}.^2,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.tep1{i}.^2/(mass0625(i)^a / charge0625(i)^b),'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{3});
    xlim([0 15]);
    %ylim([ 1e-2 2]);
    %%axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);



    %a = 1.75;
    %b = 0.75;
    % matches O5 and C5, C6 and O6 around. worse match for alphas
    a = 1.7;
    b = 0.75;
    % matches O6 and C6, C5 and O5 around. Mg and alphas a little away but
    % overlapping


    a = 1.66;
    b = 0.66;%0.7;
    subplot(2,2,4);
    semilogy(Q0625.t2,Q0625.tep2{1}.^2,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.tep2{i}.^2/(mass0625(i)^a / charge0625(i)^b),'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{4});
    xlim([0 8]);
    ylim([ 1e-2 2]);
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==488



%  (beta=0.0625+beta=0.3, balanced and imb) temperature anisotropy
if plotnbr==4888
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q

    a=0.7

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced, $\beta=0.3$","balanced, $\beta=0.3$", "imbalanced, $\beta=1/16$", "balanced, $\beta=1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    plot(Q03.t1,(Q03.tep1{1}./Q03.tel1{1}).^2-1,'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        plot(Q03.t1,(Q03.tep1{i}./Q03.tel1{i}).^2-1,'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    xlim([0 15]);
    ylim([ 0 15]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    %ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    ylabel('$\Delta_i \doteq T_{\perp i}/T_{\parallel i}-1$');% \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    plot(Q03.t2,(Q03.tep2{1}./Q03.tel2{1}).^2-1,'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        plot(Q03.t2,(Q03.tep2{i}./Q03.tel2{i}).^2-1,'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    xlim([0 8]);
    ylim([ 0 15]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    plot(Q0625.t1,(Q0625.tep1{1}./Q0625.tel1{1}).^2-1,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        plot(Q0625.t1,(Q0625.tep1{i}./Q0625.tel1{i}).^2-1,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{3});
    xlim([0 15]);
    ylim([ 0 15]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    plot(Q0625.t2,(Q0625.tep2{1}./Q0625.tel2{1}).^2-1,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        plot(Q0625.t2,(Q0625.tep2{i}./Q0625.tel2{i}).^2-1,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{4});
    xlim([0 8]);
    ylim([ 0 15]);
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==4888 temperature anisotropy

%  (beta=0.0625+beta=0.3, balanced and imb) temp. scaled by other sim.
if plotnbr==4889
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q


    figure(14); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbal/bal, $\beta=0.3$","imbalanced, $\beta=1/16/\beta=0.3$ ", "imbal/bal, $\beta=1/16$", "balanced, $\beta=1/16$/$\beta=0.3$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];

    %a = 1.07;% (m)
    %b = 0; % (q)

    a=1.55;
    b=0.6;
    subplot(2,2,1);

    [~,idx] = unique(Q03.t1);

    plot(Q03.t2,interp1(Q03.t1(idx),Q03.tep1{1}(idx),Q03.t2).^2./dedt_imb03./(Q03.tep2{1}.^2./dedt_bal03),'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        plot(Q03.t2,interp1(Q03.t1(idx),Q03.tep1{i}(idx),Q03.t2).^2./dedt_imb03./(Q03.tep2{i}.^2./dedt_bal03),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %xlim([0 15]);
    %ylim([ 1e-2 2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    %ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    ylabel('$(T_{\perp,i}/T_{\perp,i0}) $')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);

    a = 1.5;
    b = 0.53;
    % makes C6 and O6 surround C5 and O5. C5 and O5 matched well
    %10% difference with alphas
    a = 1.55;
    b = 0.6;
    %<10% difference with alphas
    % makes O6 and O5 surround C6 and C5. C6 and C5 matched well
    %a = 1.58;
    %b = 0.51;
    % makes C5 and O5 surround C6 and O6. C6 and O6 matched well
    subplot(2,2,2);
    [~,idx] = unique(Q03.t1);

    plot(Q0625.t1,(Q0625.tep1{1}.^2./dedt_imb0625)./interp1(Q03.t1(idx),Q03.tep1{1}(idx),Q0625.t1).^2.*dedt_imb03,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc_3
        plot(Q0625.t1,(Q0625.tep1{i}.^2./dedt_imb0625)./interp1(Q03.t1(idx),Q03.tep1{i}(idx),Q0625.t1).^2.*dedt_imb03,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %xlim([0 8]);
    %ylim([ 1e-2 2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    %to 8tauA
    a = 1.53;
    b = 0.65;
    % matches O5 and C5, with O6 and C6 surrounding. poor match with other
    % minors
    a = 1.7;
    b = 0.7;
    % matches O6 and C6, O5 C5 surrounding. Mg match. But alphas higher -
    % so some missing mass scaling?
    % to 10.5tauA
    a=1.67;
    b=0.62;
    % matches O6 and C6, O5 C5 surrounding.
    %a=1.5025;
    %b=0.63;
    %match O5 and C5
    %a=1.6;
    %b=0.45;
    %ignore matching specific species - try to get everything vaguely
    %around protons (in between)
    %a=1.3;
    %b=0;
    % mass only
    [~,idx] = unique(Q0625.t1);
    plot(Q0625.t2,interp1(Q0625.t1(idx),Q0625.tep1{1}(idx),Q0625.t2).^2./dedt_imb0625./(Q0625.tep2{1}.^2./dedt_bal0625),'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        plot(Q0625.t2,interp1(Q0625.t1(idx),Q0625.tep1{i}(idx),Q0625.t2).^2./dedt_imb0625./(Q0625.tep2{i}.^2./dedt_bal0625),'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{3});
    %xlim([0 15]);
    %ylim([ 1e-2 2]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);



    %a = 1.75;
    %b = 0.75;
    % matches O5 and C5, C6 and O6 around. worse match for alphas
    a = 1.7;
    b = 0.75;
    % matches O6 and C6, C5 and O5 around. Mg and alphas a little away but
    % overlapping
    subplot(2,2,4);
    [~,idx] = unique(Q03.t2);
    plot(Q0625.t2,(Q0625.tep2{1}.^2./dedt_bal0625)./interp1(Q03.t2(idx),Q03.tep2{1}(idx),Q0625.t2).^2.*dedt_bal03,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = [3 2 4 5 6]
        plot(Q0625.t2,(Q0625.tep2{i}.^2./dedt_bal0625)./interp1(Q03.t2(idx),Q03.tep2{i}(idx),Q0625.t2).^2.*dedt_bal03,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{4});
    %xlim([0 8]);
    %ylim([ 1e-2 2]);
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==4889


%  (beta=0.0625+beta=0.3, balanced and imb) heating rates scaled by other sim.
if plotnbr==48899
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q


    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbal/bal, $\beta=0.3$","imbalanced, $\beta=1/16/\beta=0.3$ ", "imbal/bal, $\beta=1/16$", "balanced, $\beta=1/16$/$\beta=0.3$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];

    %a = 1.07;% (m)
    %b = 0; % (q)

    a=1.55;
    b=0.6;
    subplot(2,2,1);

    [~,idx] = unique(Q03.t1);

    plot(Q03.t2,interp1(Q03.t1(idx),Q03.qp1{1}(idx),Q03.t2)./dedt_imb03./(Q03.qp2{1}./dedt_bal03),'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        plot(Q03.t2,interp1(Q03.t1(idx),Q03.qp1{i}(idx),Q03.t2)./dedt_imb03./(Q03.qp2{i}./dedt_bal03),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %xlim([0 15]);
    %ylim([ 0 2]);
    ylim([0 4]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    %ylabel('$(T_{\perp,i}/T_{\perp,i0}) \,(m_i/m_{\rm p})^{-a} (q_{\rm p}/m_i)^{-b}$')
    ylabel('$(Q_{\perp,i}/Q_{\perp,i0})$')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);

    a = 1.5;
    b = 0.53;
    % makes C6 and O6 surround C5 and O5. C5 and O5 matched well
    %10% difference with alphas
    a = 1.55;
    b = 0.6;
    %<10% difference with alphas
    % makes O6 and O5 surround C6 and C5. C6 and C5 matched well
    %a = 1.58;
    %b = 0.51;
    % makes C5 and O5 surround C6 and O6. C6 and O6 matched well
    subplot(2,2,2);
    [~,idx] = unique(Q03.t1);

    plot(Q0625.t1,(Q0625.qp1{1}./dedt_imb0625)./interp1(Q03.t1(idx),Q03.qp1{1}(idx),Q0625.t1).*dedt_imb03,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc_3
        plot(Q0625.t1,(Q0625.qp1{i}./dedt_imb0625)./interp1(Q03.t1(idx),Q03.qp1{i}(idx),Q0625.t1).*dedt_imb03,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %xlim([0 8]);
    %ylim([ 0 0.5]);
    ylim([0 10]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    %to 8tauA
    a = 1.53;
    b = 0.65;
    % matches O5 and C5, with O6 and C6 surrounding. poor match with other
    % minors
    a = 1.7;
    b = 0.7;
    % matches O6 and C6, O5 C5 surrounding. Mg match. But alphas higher -
    % so some missing mass scaling?
    % to 10.5tauA
    a=1.67;
    b=0.62;
    % matches O6 and C6, O5 C5 surrounding.
    %a=1.5025;
    %b=0.63;
    %match O5 and C5
    %a=1.6;
    %b=0.45;
    %ignore matching specific species - try to get everything vaguely
    %around protons (in between)
    %a=1.3;
    %b=0;
    % mass only
    [~,idx] = unique(Q0625.t1);
    plot(Q0625.t2,interp1(Q0625.t1(idx),Q0625.qp1{1}(idx),Q0625.t2)./dedt_imb0625./(Q0625.qp2{1}./dedt_bal0625),'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        plot(Q0625.t2,interp1(Q0625.t1(idx),Q0625.qp1{i}(idx),Q0625.t2)./dedt_imb0625./(Q0625.qp2{i}./dedt_bal0625),'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{3});
    %xlim([0 15]);
    %ylim([0 2]);
    ylim([ 0 6]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);



    %a = 1.75;
    %b = 0.75;
    % matches O5 and C5, C6 and O6 around. worse match for alphas
    a = 1.7;
    b = 0.75;
    % matches O6 and C6, C5 and O5 around. Mg and alphas a little away but
    % overlapping
    subplot(2,2,4);
    [~,idx] = unique(Q03.t2);
    plot(Q0625.t2,(Q0625.qp2{1}./dedt_bal0625)./interp1(Q03.t2(idx),Q03.qp2{1}(idx),Q0625.t2).*dedt_bal03,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = [3 2 4 5 6]
        plot(Q0625.t2,(Q0625.qp2{i}./dedt_bal0625)./interp1(Q03.t2(idx),Q03.qp2{i}(idx),Q0625.t2).*dedt_bal03,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    title(tlab{4});
    %xlim([0 8]);
    %ylim([ 0 0.3]);
    ylim([0 1])
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==48899

%  heating rates from edv
if plotnbr==45
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    b03Q = Q; clear Q;
    name = 'b_b3_sim1';
    load([ savebase 'Qfromedv-' name '.mat'],'q_t','times');
    for i = 1:7
        q_t{i} = squeeze(q_t{i})
    end


    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { 'Qperp from dT/dt','Qperp from Evf' };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');

    semilogy(b03Q.t2,b03Q.qp2{1},'Color',myblue,'LineWidth',1)
    for i = plotorder_trunc
        semilogy(b03Q.t2,b03Q.qp2{i},'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    p1 = semilogy(nan,nan,'k');
    hold on
    p2 = semilogy(nan,nan,'k--');
    semilogy(times,q_t{1},'Color',myblue,'LineWidth',1)
    for i = plotorder_trunc
        semilogy(times,q_t{i},'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-3 5]);
    yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend([p1 p2],'$Q_{\perp}$','$Q_{\parallel}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);
    a=0.3;
    semilogy(b03Q.t2,b03Q.qp2{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a) )*2./3),'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(b03Q.t2,b03Q.qp2{i}/(massog(i)*(massog(i)/chargeog(i))^(2.*a/(1-a) )),'Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %ylim([ 1e-3 1]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm Fe^{9+}} (Z/A)^{2a\eta}/A$', ...
    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);

    a = 0.3
    subplot(2,2,4);
    %semilogy(Q.t2,Q.qp2{3}./Q.qp2{1},'Color',myred,'LineWidth',1)
    semilogy(times,q_t{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a))*2./3 ),'--','Color',myblue,'LineWidth',1)
    hold on
    %semilogy(Q.t2,Q.qp2{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*0.25/0.75) ),'Color',myred,'LineWidth',1)
    %semilogy(Q.t2,Q.qp2{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*0.25/0.75) ),'Color',myorange,'LineWidth',1)
    for i = plotorder_trunc
        disp(colorder{i})
        semilogy(times,q_t{i}./(massog(i)*(massog(i)/chargeog(i))^(2.*a/(1-a) )),'--','Color',colorder{i},'LineWidth',1)
    end
    %semilogy(Q.t2,Q.qp2{2}./Q.qp2{1},'Color',myorange,'LineWidth',1)
    hold off;
    %ylim([ 1e-3 1]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    %ylim([ 1 100]);
    %yticks(logspace(1,10,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('$Q_{\perp,p}/0.71$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg = legend('$Q_{\perp,p}$','$Q_{\perp,\alpha} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm O^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{6+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm C^{5+}} (Z/A)^{2a\eta}/A$','$Q_{\perp,\rm Fe^{9+}} (Z/A)^{2a\eta}/A$', ...
    'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==45



%  (beta=0.0625+beta=0.3, balanced and imb) perp+parallel heating rates.
%  replaced one with beta=1
if plotnbr==59
    load([ savebase 'PlotQ-allb0625.mat'],'Q');
    Q0625 = Q;
    clear Q
    load([ savebase 'PlotQ-allb3.mat'],'Q');
    Q03 = Q;
    clear Q

    a=0.7

    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced, $\beta=0.3$","balanced, $\beta=0.3$", "imbalanced, $\beta=1/16$", "balanced, $\beta=1/16$" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];


    subplot(2,2,1);
    semilogy(Q03.t1,Q03.qp1{1}./dedt_imb03,'Color',colorder{1},'LineWidth',1) 
    hold on
    for i = plotorder_trunc_3
        semilogy(Q03.t1,Q03.qp1{i}./dedt_imb03,'Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder_3
        semilogy(Q03.t1,Q03.ql1{i}./dedt_imb03,'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q03.t1,Q03.eps_noE1./dedt_imb03,'k');
    hold off;
    xlim([0 15]);
    ylim([ 1e-2 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('$Q_i/\varepsilon_{\rm inj}~(\perp: {\rm solid};\,\parallel:{\rm dashed})$')
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    semilogy(Q03.t2,Q03.qp2{1}./dedt_bal03,'Color',colorderfe{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q03.t2,Q03.qp2{i}./dedt_bal03,'Color',colorderfe{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q03.t2,Q03.ql2{i}./dedt_bal03,'--','Color',colorderfe{i},'LineWidth',1)
    end
    p3 = semilogy(Q03.t2,Q03.eps_noE2./dedt_bal03,'k');
    hold off;
    xlim([0 8]);
    ylim([ 1e-2 2e2]);
    %ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Fe}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    %set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q0625.t1,Q0625.qp1{1}./dedt_imb0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t1,Q0625.qp1{i}./dedt_imb0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t1,Q0625.ql1{i}./dedt_imb0625,'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q0625.t1,Q0625.eps_noE1./dedt_imb0625,'k');
    hold off;
    title(tlab{3});
    xlim([0 15]);
    ylim([ 1e-2 2e2]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    %ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    semilogy(Q0625.t2,Q0625.qp2{1}./dedt_bal0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q0625.t2,Q0625.qp2{i}./dedt_bal0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q0625.t2,Q0625.ql2{i}./dedt_bal0625,'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q0625.t2,Q0625.eps_noE2./dedt_bal0625,'k');
    hold off;
    title(tlab{4});
    xlim([0 8]);
    ylim([ 1e-2 2e2]);
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    %leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
    %    'Location','SouthEast','Interpreter','latex','FontSize',10);
    %leg.ItemTokenSize = [25,18];
    %legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==58


%  (beta=1) perp+parallel heating rates and temperatures
if plotnbr==58
    load([ savebase 'PlotQ-allb1.mat'],'Q');
    Q1 = Q;
    clear Q



    figure(12); clf; pwidth=18.5; pheight=11.5;
    set(gcf,'Color',[1 1 1]);
    set(gcf,'Units','centimeters');
    set(gcf,'Position',[1,1,pwidth,pheight]);
    set(gcf,'PaperPositionMode','auto');
    set(gcf,'renderer','Painters');

    width=0.38; height=0.373; offset = 0.08; gap = 0.08;
    normpos = { [offset,0.58,width,height], [offset+width+gap,0.58,width,height], ...
                [offset,0.09,width,height], [offset+width+gap,0.09,width,height] };
    tlab    = { "imbalanced","balanced" };

    xo = [0.265,0.20]; yo = 2.6e-7*[1,1];
    xa = [0.47,0.34]; ya = 2.6e-7*[1,1];
    xp = [0.79,0.69]; yp = 2.6e-7*[1,1];

    
    a = 0;%2.5;
    b = 0;%2.0;%0.7;

    subplot(2,2,1);
    semilogy(Q1.t1,Q1.qp1{1}./dedt_imb1,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t1,Q0625.ql1{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q1.t1,Q1.qp1{i}./dedt_imb1./(mass0625(i)^a / charge0625(i)^b),'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.ql1{i},'--','Color',colorder{i},'LineWidth',1)
    end
    semilogy(Q1.t1,Q1.qp1{8}./dedt_imb1,'.-','Color',colorder{1},'LineWidth',1)
    for i = plotorder
        semilogy(Q1.t1,Q1.ql1{i}./dedt_imb1/(mass0625(i)^a / charge0625(i)^b),'--','Color',colorder{i},'LineWidth',1)
    end
    p3 = semilogy(Q1.t1,Q1.eps_noE1./dedt_imb1,'k');
    hold off;
    ylim([ 1e-2 2e2]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{1});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{1});
    ylabel('($Q_i/\varepsilon_{\rm inj})$')
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);


    subplot(2,2,2);
    semilogy(Q1.t2,Q1.qp2{1}./dedt_bal0625,'Color',colorder{1},'LineWidth',1) 
    hold on
    %semilogy(Q0625.t2,Q0625.ql2{1},'Color','--',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q1.t2,Q1.qp2{i}./dedt_bal0625,'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t2,Q0625.ql2{i},'--','Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q1.t2,Q1.ql2{i}./dedt_bal0625,'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    ylim([ 1e-2 2e2]);
    %ylim([ 1e-1 2e2]);
    %ylim([ 1e-3 5]);
    %yticks(logspace(-3,0,4)); yticklabels({'$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^0$'});
    title(tlab{2});
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{2});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    set(gca,'XTickLabel',[]);
    plotTickLatex2D('ytickdx',0.003);



    subplot(2,2,3);

    semilogy(Q1.t1,Q1.tep1{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    %semilogy(Q0625.t1,Q0625.tel1{1}.^2,'Color',colorder{1},'LineWidth',1)
    for i = plotorder_trunc
        semilogy(Q1.t1,Q1.tep1{i}.^2./(mass0625(i)^a / charge0625(i)^b),'Color',colorder{i},'LineWidth',1)
        %semilogy(Q0625.t1,Q0625.tel1{i}.^2,'--','Color',colorder{i},'LineWidth',1)
    end
    semilogy(Q1.t1,Q1.tep1{8}.^2,'.-','Color',colorder{1},'LineWidth',1)
    for i = plotorder
        semilogy(Q1.t1,Q1.tel1{i}.^2./(mass0625(i)^a / charge0625(i)^b),'--','Color',colorder{i},'LineWidth',1)
    end

    %semilogy(Q.t1,Q.qp1{3}./(massog(3)*(massog(3)/chargeog(3))^(2.*a/(1-a) )),'Color',myred,'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{2}./(massog(2)*(massog(2)/chargeog(2))^(2.*a/(1-a) )),'Color',myorange,'LineWidth',1)
    hold off;
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    ylabel('$(T_{\perp,i}/T_{\perp,i0})$')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{3});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    %plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);
    plotTickLatex2D('xtickdy',0.005,'xlabeldy',0.03,'ytickdx',0.003,'ylabeldx',-0.005);

    a
    subplot(2,2,4);
    semilogy(Q1.t2,Q1.tep2{1}.^2,'Color',colorder{1},'LineWidth',1)
    %semilogy(Q.t1,Q.qp1{1}./(massog(1)*(massog(1)/chargeog(1))^(2.*a/(1-a)) )/0.666,'Color',myblue,'LineWidth',1)
    hold on
    for i = plotorder_trunc
        semilogy(Q1.t2,Q1.tep2{i}.^2,'Color',colorder{i},'LineWidth',1)
    end
    for i = plotorder
        semilogy(Q1.t2,Q1.tel2{i}.^2,'--','Color',colorder{i},'LineWidth',1)
    end
    hold off;
    %ylim([-10 5])
    %ylim([0 1.3])
    %ylim([0 100]);
    %axis([min(kprp) 10 1e-7 1]);
    %yticks(logspace(-7,0,8)); yticklabels({'','$10^{-6}$','','$10^{-4}$','','$10^{-2}$','','$10^0$'});
    xlabel('$t/\tau_{\rm A}$','interpreter','latex')
    set(gca,'TickLength',[0.02 0.02],'XMinorTick','on','YMinorTick','on');
    set(gca,'Units','normalized','Position',normpos{4});
    leg = legend('${\rm p}$','$\alpha$','${\rm O}^{5+}$','${\rm O}^{6+}$','${\rm C}^{6+}$','${\rm C}^{5+}$','${\rm Mg}^{9+}$', ...
        'Location','SouthEast','Interpreter','latex','FontSize',10);
    leg.ItemTokenSize = [25,18];
    legend('boxoff');
    plotTickLatex2D('xtickdy',-0.003,'xlabeldy',0.02,'ytickdx',0.003);


end % plotnbr==58



end




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
vprl = linspace(minvl+1e-3,vaprl,100*vaprp);
vlsolve = @(y,vl) -vl - 1./sqrt(1+y.^2) + qom./y;
yres = [];yguess = qom/(1+vprl(end));
for lll = length(vprl):-1:1
    yres = [fzero(@(y) vlsolve(y,vprl(lll)),yguess) yres];
    yguess = yres(1);
end

vprp = linspace(1e-3,vaprp,100*vaprp); % Grid out to va
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



function decades_equal(hAxes,xLimits,yLimits)

  if (nargin < 2) || isempty(xLimits)
    xLimits = get(hAxes,'XLim');
  end
  if (nargin < 3) || isempty(yLimits)
    yLimits = get(hAxes,'YLim');
  end

  logScale = diff(yLimits)/diff(xLimits);
  powerScale = diff(log10(yLimits))/diff(log10(xLimits));

  set(hAxes,'Xlim',xLimits,...
            'YLim',yLimits,...
            'DataAspectRatio',[1 logScale/powerScale 1]);

end
