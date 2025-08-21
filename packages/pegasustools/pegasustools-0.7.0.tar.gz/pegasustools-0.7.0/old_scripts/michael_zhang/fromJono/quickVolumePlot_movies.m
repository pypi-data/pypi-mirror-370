function quickVolumePlot_movies

addpath('~/matlab-libs')

name = 'sig-decr-prod';

% name = 'test-frontera-run';'imbal2-prod';
% computer = 'local';'tigress';
% nums = 100;0:162;

computer = 'tigress';
nums =  218:-1:182; % snapshot numbers for which to find spectrum
P.derefine_prl =1; P.derefine_prp=1;

tauA = 6*67.4523; % Levs tauA = 206.4865395;
if strcmp(name,'lev'); tauA = 206.4865395;end


[readF,files_all,~,~,outputfolder] = chooseComputerAndFiles(name,computer);

% Some nice color maps from brewermap
% Spectral, RdYlBu for diverging, 
% PuBuGn BuPu  YlGnBu  non diverging
% Use flipud to flip the map

savebase = [outputfolder '../../saved-analysis/movie-sig-decr/']; %outputfolder '../../' 
addpath ~/matlab-libs/export-fig
mres = '6';
n2s = @(n) sprintf('%03d',n);
t2s = @(t) sprintf('%0.1f',t);

campos = [500 -80 150];
cbpos = [.87 .2 .02 .3];
fpos = [0.1, 0.1, 0.5, 0.7];
axfs = 6;

for nnn = nums
    try
        V = readF(files_all(nnn));
        V = reduceResolution(V,P.derefine_prl,P.derefine_prp);
    catch
        disp('');disp([num2str(nnn) ' didnt work!!!!']);disp('');
        continue
    end
%     fig=figure;set(fig,'color','w');set(gcf, 'Units', 'Normalized', 'OuterPosition', fpos);
%     colormap((brewermap([],'Spectral')))
%     VolumePlot(V.Ecc3,V.x,V.y,V.z);cb = colorbar; set(cb,'position',cbpos,'Fontsize',axfs)
%     caxis([-1 1]*0.4)
%     ax = gca;ax.CameraPosition = campos;set(ax,'xtick',[]);set(ax,'ytick',[]);set(ax,'ztick',[])
%     title(['$t=' t2s(V.t/tauA) '\tau_A$'],'interpreter','latex')
% %     xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
%     export_fig([savebase name '-Ez.'  n2s(nnn) '.png'],['-m' mres])
%     close(fig)
    
    fig=figure;set(fig,'color','w');set(gcf, 'Units', 'Normalized', 'OuterPosition', fpos);
    colormap((brewermap([],'Spectral')))
    VolumePlot(V.Bcc2,V.x,V.y,V.z);cb = colorbar; set(cb,'position',cbpos,'Fontsize',axfs);
    caxis([-1 1]*0.4)
    ax = gca;ax.CameraPosition = campos;set(ax,'xtick',[]);set(ax,'ytick',[]);set(ax,'ztick',[])
    title(['$t=' t2s(V.t/tauA) '\tau_A$'],'interpreter','latex')
%     xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    export_fig([savebase name '-By.'  n2s(nnn) '.png'],['-m' mres])
    close(fig)
    
    fig=figure;set(fig,'color','w');set(gcf, 'Units', 'Normalized', 'OuterPosition', fpos);
    colormap inferno
    VolumePlot(sqrt(V.Ecc2.^2+V.Ecc3.^2),V.x,V.y,V.z);cb = colorbar; set(cb,'position',cbpos,'Fontsize',axfs)
    caxis([0.0 0.5])
    ax = gca;ax.CameraPosition = campos;set(ax,'xtick',[]);set(ax,'ytick',[]);set(ax,'ztick',[])
    title(['$t=' t2s(V.t/tauA) '\tau_A$'],'interpreter','latex')
%     xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    export_fig([savebase name '-Emag.'  n2s(nnn) '.png'],['-m' mres])
    close(fig)
    
%     fig=figure;set(fig,'color','w');set(gcf, 'Units', 'Normalized', 'OuterPosition', fpos);
%     colormap((brewermap([],'PuBuGn')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z);colorbar; set(cb,'position',cbpos)
%     caxis(log10([0.05 0.5]))
%     ax = gca;ax.CameraPosition = campos;
%     xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
%     export_fig([savebase name '-Emag.'  n2s(nnn) '.png'],'-transparent',['-m' mres])
%     close(fig)
    
end
  

end


% set(gcf,'color','none')
% export_fig Emag-imbal.png -transparent -m6
    
