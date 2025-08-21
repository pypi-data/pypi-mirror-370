function quickVolumePlot

addpath('~/matlab-libs/BrewerMap')

name = 'b_b0625_sim1';

computer = 'tigress';%'local';
nums = 35; % snapshot numbers for which to find spectrum
P.derefine_prl =70; P.derefine_y=14; P.derefine_z=20;

[readF,files_all] = chooseComputerAndFiles(name,computer);

% Some nice color maps from brewermap
% Spectral, RdYlBu for diverging, 
% PuBuGn BuPu  YlGnBu  non diverging
% Use flipud to flip the map



for nnn = nums
    try
        V = readF(files_all(nnn));
        size(V.dens)
        %V = reduceResolution(V,P.derefine_prl,P.derefine_prp);
        %V = sumBlock(V,P.derefine_prl,P.derefine_y,P.derefine_z);
        size(V.dens)
    catch
        continue
    end

    disp("read V")
    rho = V.dens;
    %rho = (V.dens_s0+V.dens_s1+V.dens_s2+V.dens_s3+V.dens_s4+V.dens_s5)/6;
    x = V.x;
    y = V.y;
    z = V.z;
    clear V;
    disp("cleared V")

    [dnx, dny, dnz] = gradient(rho);
    disp("dx is ")
    dx = 22/280
    gradrho = sqrt(dnx.*dnx + dny.*dny + dnz.*dnz)./dx;
    disp("minimum rho is")
    minrho = min(rho,[],"all")
    disp("maximum rho is")
    maxrho = max(rho,[],"all")
    disp("max gradfield/field is ")
    maxgrad = max(gradrho./rho,[],"all")
    disp("which is " + maxgrad*dx + "dx")
    disp("max(field)/rms(field)")
    max(abs(rho),[],"all")/rms(rho,"all")
    disp('rms(field)')
    rms(rho,"all")
    disp('number of cells with rho<0.1')
    size(find(rho<0.1))
    disp('number of cells with rho<0.08')
    size(find(rho<0.08))
    disp('number of cells with rho<0.06')
    size(find(rho<0.06))
    disp('number of cells with rho<0.04')
    size(find(rho<0.04))


%{
    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.b_force,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name 'visb_force.fig'])
    saveas(fig,['saved-analysis/' name '/visb_force.png'])
    close(fig)
%}
%{
    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.force2,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visforce2.fig'])
    saveas(fig,['saved-analysis/' name '/visforce2.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.force3,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visforce3.fig'])
    saveas(fig,['saved-analysis/' name '/visforce3.png'])
    close(fig)
%{
    b_forcey = zeros(size(V.b_force),'like',V.b_force);
    b_forcez = zeros(size(V.b_force),'like',V.b_force);

    %[xgrid,ygrid,zgrid] = meshgrid(V.x,V.y,V.z);

    %disp(size(V.x));
    %disp(size(V.y));
    %disp(size(xgrid));
    %disp(size(pagetranspose(xgrid)));
    %disp(size(V.b_force));

    NX=length(V.x);LX=V.x(end)-V.x(1)+(V.x(2)-V.x(1));
    NY=length(V.y);LY=V.y(end)-V.y(1)+(V.y(2)-V.y(1));
    NZ=length(V.z);LZ=V.z(end)-V.z(1)+(V.z(2)-V.z(1));


%Grid
    [XG,YG,ZG]=meshgrid(linspace(0,LX,NX),linspace(0,LY,NY),linspace(0,LZ,NZ));

    %[curlx,curly,curlz,cav] = curl(pagetranspose(XG),pagetranspose(YG),pagetranspose(ZG),V.b_force,b_forcey,b_forcez);
    [curlx,curly,curlz,cav] = curl(XG,YG,ZG,pagetranspose(V.b_force),pagetranspose(b_forcey),pagetranspose(b_forcez));

    %(curly + V.force2).*(V.vel2 + V.Bcc2) + (curlz + V.force3).*(V.vel3 + V.Bcc3)

    %disp(size(curly));
    %disp(size(V.force2));
    %disp(size((curly + V.force2).*(V.vel2 + V.Bcc2) + (curlz + V.force3).*(V.vel3 + V.Bcc3)));

    curlxt = pagetranspose(curlx);
    curlyt = pagetranspose(curly);
    curlzt = pagetranspose(curlz);

    %zpdotF = (curly + V.force2).*(V.vel2 + V.Bcc2) + (curlz + V.force3).*(V.vel3 + V.Bcc3);
 
    
    %disp(class(curly));
    %disp(class(V.force2));
    %disp(curlyt(800,140,140));
    %disp(V.force2(800,140,140));
    %V.curly = curly;

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot((curlyt + V.force2).*(V.vel2 + V.Bcc2) + (curlzt + V.force3).*(V.vel3 + V.Bcc3),V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszpdotF.fig'])
    saveas(fig,['saved-analysis/' name '/viszpdotF.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot((curlyt + V.force2).*(V.vel2 - V.Bcc2) + (curlzt + V.force3).*(V.vel3 - V.Bcc3),V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszmdotF.fig'])
    saveas(fig,['saved-analysis/' name '/viszmdotF.png'])
    close(fig)


    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot((curlyt + V.force2),V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visFy.fig'])
    saveas(fig,['saved-analysis/' name '/visFy.png'])
    close(fig)


    

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot( (curlzt + V.force3),V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visFz.fig'])
    saveas(fig,['saved-analysis/' name '/visFz.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot( (curlyt ),V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viscurly.fig'])
    saveas(fig,['saved-analysis/' name '/viscurly.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot( (curlzt ),V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viscurlz.fig'])
    saveas(fig,['saved-analysis/' name '/viscurlz.png'])
    close(fig)

%}
    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel1 + V.Bcc1 - 1.0,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszpxcmp.fig'])
    saveas(fig,['saved-analysis/' name '/viszpxcmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel2 + V.Bcc2,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszpycmp.fig'])
    saveas(fig,['saved-analysis/' name '/viszpycmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel3 + V.Bcc3,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszpzcmp.fig'])
    saveas(fig,['saved-analysis/' name '/viszpzcmp.png'])
    close(fig)


    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel1 - V.Bcc1 + 1.0,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszpmcmp.fig'])
    saveas(fig,['saved-analysis/' name '/viszpmcmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel2 - V.Bcc2,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszmycmp.fig'])
    saveas(fig,['saved-analysis/' name '/viszmycmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel3 - V.Bcc3,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszmzcmp.fig'])
    saveas(fig,['saved-analysis/' name '/viszmzcmp-.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel1,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visuxcmp.fig'])
    saveas(fig,['saved-analysis/' name '/visuxcmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel2,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visuycmp.fig'])
    saveas(fig,['saved-analysis/' name '/visuycmp.png'])
    close(fig)


    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.vel3,V.x,V.y,V.z);colorbar; %caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visuzcmp.fig'])
    saveas(fig,['saved-analysis/' name '/visuzcmp.png'])
    close(fig)


    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(log10(sqrt(V.vel2.^2+V.vel3.^2)),V.x,V.y,V.z);colorbar; %caxis(log10([0.05 0.5]))
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visuprp.fig']);
    saveas(fig,['saved-analysis/' name '/visuprp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(log10(sqrt(V.vel1.^2)),V.x,V.y,V.z);colorbar; %caxis(log10([0.05 0.5]))
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visuprl.fig']);
    saveas(fig,['saved-analysis/' name '/visuprl.png'])
    close(fig)

    %zp
    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(log10(sqrt( 0.5*( 0.5*V.vel1.^2 + 0.5*V.vel2.^2 + 0.5*V.vel3.^2 + 0.5*V.Bcc1.^2 + 0.5*V.Bcc2.^2 + 0.5*V.Bcc3.^2       +  V.vel1.*(V.Bcc1-1.0)+V.vel2.*V.Bcc2+V.vel3.*V.Bcc3  )   )  ),V.x,V.y,V.z);colorbar; %caxis(log10([0.05 0.5]))
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszpmag.fig']);
    saveas(fig,['saved-analysis/' name '/viszpmag.png'])
    close(fig)

    %zm
    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(log10(sqrt( 0.5*( 0.5*V.vel1.^2 + 0.5*V.vel2.^2 + 0.5*V.vel3.^2 + 0.5*V.Bcc1.^2 + 0.5*V.Bcc2.^2 + 0.5*V.Bcc3.^2       -  V.vel1.*(V.Bcc1-1.0)+V.vel2.*V.Bcc2+V.vel3.*V.Bcc3  )   )  ),V.x,V.y,V.z);colorbar; %caxis(log10([0.05 0.5]))
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/viszmmag.fig']);
    saveas(fig,['saved-analysis/' name '/viszmmag.png'])
    close(fig)


    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.Ecc3,V.x,V.y,V.z);colorbar; caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visEzcmp.fig'])
    saveas(fig,['saved-analysis/' name '/visEzcmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.Ecc2,V.x,V.y,V.z);colorbar; caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visEycmp.fig'])
    saveas(fig,['saved-analysis/' name '/visEycmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
%     VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z)
    VolumePlot(V.Ecc1,V.x,V.y,V.z);colorbar; caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visExcmp.fig'])
    saveas(fig,['saved-analysis/' name '/visExcmp.png'])
    close(fig)
    
    fig=figure;
    colormap((brewermap([],'Spectral')))
    VolumePlot(V.Bcc1-1.0,V.x,V.y,V.z);colorbar; caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visBxcmp.fig'])
    saveas(fig,['saved-analysis/' name '/visBxcmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
    VolumePlot(V.Bcc2,V.x,V.y,V.z);colorbar; caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visBycmp.fig'])
    saveas(fig,['saved-analysis/' name '/visBycmp.png'])
    close(fig)

    fig=figure;
    colormap((brewermap([],'Spectral')))
    VolumePlot(V.Bcc3,V.x,V.y,V.z);colorbar; caxis([-1 1]*0.5)
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visBzcmp.fig'])
    saveas(fig,['saved-analysis/' name '/visBzcmp.png'])
    close(fig)
    
    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(log10(sqrt(V.Ecc2.^2+V.Ecc3.^2)),V.x,V.y,V.z);colorbar; caxis(log10([0.05 0.5]))
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visEmag.fig']);
    saveas(fig,['saved-analysis/' name '/visEmag.png'])
    close(fig)
    
    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(log10(sqrt(V.Bcc2.^2+V.Bcc3.^2)),V.x,V.y,V.z);colorbar; caxis([-1.5 0])
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visBmag.fig'])
    saveas(fig,['saved-analysis/' name '/visBmag.png'])
    close(fig)
%}

    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(rho,x,y,z);colorbar; caxis([0 2])
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visrho.fig'])
    saveas(fig,['saved-analysis/' name '/visrho.png'])
    %close(fig)

    %{
    rho0 = ~rho;
    fig=figure;
    colormap((brewermap([],'PuBuGn')))
    VolumePlot(rho0,x,y,z);colorbar; caxis([0 1])
    ax = gca;ax.CameraPosition = [900.3931  -80.9985  150.1834];
    xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    savefig(['saved-analysis/' name '/visrho.fig'])
    saveas(fig,['saved-analysis/' name '/visrho.png'])

    sum(rho0,'all')
    %}
end
  

end


% set(gcf,'color','none')
% export_fig Emag-imbal.png -transparent -m6
    
