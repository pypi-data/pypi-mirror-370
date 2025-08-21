function quickVolumePlot_flines
 

addpath('~/matlab-libs')

name = 'imbal2-prod';

% name = 'test-frontera-run';'imbal2-prod';
% computer = 'local';'tigress';
% num = 100;


computer = 'tigress';
num =  162; % snapshot numbers for which to find spectrum
P.derefine_prl =4; P.derefine_prp=1;

tauA = 6*67.4523; % Levs tauA = 206.4865395;
if strcmp(name,'lev'); tauA = 206.4865395;end

[readF,files_all,~,~,outputfolder] = chooseComputerAndFiles(name,computer);

% Some nice color maps from brewermap
% Spectral, RdYlBu for diverging, 
% PuBuGn BuPu  YlGnBu  non diverging
% Use flipud to flip the map

sq=@(f) squeeze(f);
m3 = @(a) mean(mean(mean(a)));
s3 = @(a) sum(sum(sum(a)));
any3 = @(a) any(any(any(a)));
isodd = @(n) 2*mod(n/2,1);

savebase = [outputfolder '../../saved-analysis/movie-nature/']; %outputfolder '../../' 
% savebase = '/Users/jsquire/Dropbox (Otago University)/Research/pegasus/imbalanced-turbulence/simulations/movies/movie-nature/test/';
addpath ~/matlab-libs/export-fig
mres = '20';
n2s = @(n) sprintf('%03d',n);
t2s = @(t) sprintf('%0.1f',t);

campos = [460 -60 150];  % [440 -90 115] From the side for top field lines ; [460 -60 150] from above for side flines
cbpos = [.87 .2 .02 .3];
fpos = [0.1, 0.1, 0.5, 0.7];
axfs = 6;

V = readF(files_all(num));
xf = V.x;yf=V.y;zf = V.z; Eprp = sqrt(V.Ecc2.^2+V.Ecc3.^2);
V = reduceResolution(V,P.derefine_prl,P.derefine_prp);
% Flip around in x if wanted
V.Bcc1 = V.Bcc1(end:-1:1,:,:);
V.Bcc2 = V.Bcc2(end:-1:1,:,:);
V.Bcc3 = V.Bcc3(end:-1:1,:,:);
Eprp = Eprp(end:-1:1,:,:);

mBz = 1;
lnX=[];lnY=[];lnZ=[];
nlines = 300;
for nl=2

    xg = V.x(:); yg = V.y(:); zg = V.z(:);
    dx = V.x(2)-V.x(1);    dy = V.y(2)-V.y(1);    dz = V.z(2)-V.z(1);
    Ls = [V.x(end)-V.x(1)+dx V.y(end)-V.y(1)+dy V.z(end)-V.z(1)+dz];
    xge = [xg(1)-dx;xg;xg(end)+dx];yge = [yg(1)-dy;yg;yg(end)+dy];zge = [zg(1)-dz;zg;zg(end)+dz];
    FBx = griddedInterpolant({xge,yge,zge},extArray(double(-V.Bcc1)),'spline','none');
    FBy = griddedInterpolant({xge,yge,zge},extArray(double(V.Bcc2)),'spline','none');
    FBz = griddedInterpolant({xge,yge,zge},extArray(double(V.Bcc3)),'spline','none');
    sgrid = 0:dx:Ls(1)-dx; ns = length(sgrid);
    
    disp(['Computing field lines from ' n2s(nlines) ' points'])
    switch nl
        case 1
            ppnty = linspace(dy, Ls(2)-dy,nlines).';
            ics = [(Ls(1)-2*dx)*ones(nlines,1) ppnty (Ls(3)-20*dz)*ones(nlines,1)].';
        case 2
            ppntz = linspace(dz, Ls(3)-dz,nlines).';
            ics = [(Ls(1)-2*dx)*ones(nlines,1) (dy)*ones(nlines,1) ppntz].';
    end
    tic;[strue,flines] = ode45(@bhat,sgrid,ics(:));toc
    flines = permute(reshape(flines,[ns 3 nlines]),[1,2,3]);
    %     plot3(sq(flines(:,1,:)),sq(flines(:,2,:)),sq(flines(:,3,:)))
    lnX =  [lnX sq(flines(:,1,:))];%mod(sq(flines(:,1,:)),Ls(1));
    lnY = [lnY sq(flines(:,2,:))];%mod(sq(flines(:,2,:)),Ls(2));
    lnZ = [lnZ sq(flines(:,3,:))];%mod(sq(flines(:,3,:)),Ls(3));
    if any3(isnan(lnY)) || any3(isnan(lnZ));warning('Found NaN in field lines');end
%     if ns~=size(lnX,1); warning('Length of lnX not expected ns');end
    clear flines FBx FBy FBz;
    
end
% lnX(lnX>Ls(1))=NaN;
% lnX(lnX<0)=NaN;
% lnY(lnY<0.)=NaN;
% lnY(lnY>Ls(2))=NaN;
% lnZ(lnZ>Ls(3)+0.1)=NaN;
% lnZ = lnZ+1.1*dz;
col=brewermap(8,'Set1');
col = col(2,:);


nz = length(V.z);
slices = (nz:-1:4)/nz;0.5:-0.2:0.2;%(nz:-2:2)/nz;
snum = 1;
for slz = slices
    
    
    fig=figure;set(fig,'color','w');set(gcf, 'Units', 'Normalized', 'OuterPosition', fpos);
    colormap inferno
    VolumePlot(Eprp,xf,yf,zf,slz); colorbar('hide');%cb = colorbar; set(cb,'position',cbpos,'Fontsize',axfs)
    caxis([0.0 0.5])
    % Draw field lines
    hold on
%     plot3(lnX,lnY,lnZ,'Color',col,'Linewidth',0.1)
    p  = patchline(lnX,lnY,lnZ,'linestyle','-','edgecolor',col,'linewidth',0.4,'edgealpha',0.5);
    
    ax = gca;ax.CameraPosition = campos;set(ax,'xtick',[]);set(ax,'ytick',[]);set(ax,'ztick',[])
    ax.YColor = 'w';ax.XColor = 'w';ax.ZColor = 'w';
%     title(['$t=' t2s(V.t/tauA) '\tau_A$'],'interpreter','latex')
    
%     xlabel('$x/d_i$','interpreter','latex');ylabel('$y/d_i$','interpreter','latex');zlabel('$z/d_i$','interpreter','latex')
    export_fig([savebase '/flines-side2-Emag.'  n2s(snum) '.png'],['-m' mres])
    snum=snum+1;
    close(fig)
    
end
  


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    function xdot = bhat(t,x)
        xv = mod(x(1:3:end),Ls(1));
        yv = mod(x(2:3:end),Ls(2));
        zv = mod(x(3:3:end),Ls(3));
        bx = FBx(xv,yv,zv);
        by = FBy(xv,yv,zv);
        bz = FBz(xv,yv,zv);
        xdot = ([bx by bz]./sqrt(bx.^2+by.^2+bz.^2)).';
        xdot = xdot(:);
    end


end


function Ax=extArray(Ax)
% Extend array through periodicity
Ax = cat(1,Ax(end,:,:),Ax,Ax(1,:,:));
Ax = cat(2,Ax(:,end,:),Ax,Ax(:,1,:));
Ax = cat(3,Ax(:,:,end),Ax,Ax(:,:,1));
end

