function spectrum_kprlkprp_hel
% 2D spectrum of B and E - helicity version
name = 'half_tcorr_sim8';

P.numKgrid =  [200 400]; % Perp parallel grid.
P.derefine_prl =4; P.derefine_prp=1;
P.flinlen = 10; % Length of field line compared to Lx. Can be arbitrary but will change the kprl grid a bit.
P.nlines = 2000; % Number of field lines to use. 

% A couple of notes. It is good to use a field line length ~2-100 times the
% size of the box (matlab is actually faster). The filter is important for
% making the spectrum more featured and the Hammond one seems best.
% Don't over sample at low kprl, even if the field line length is long.
% Best to use kz to construct the grid.
% There is still something wrong with the overall normalization. I get
% consistent results with different length lines etc., but they are scaled
% by some overall factor...

plotB = 1;
plotKprlKprp = 1;

computer = 'tigress';
DoFullCalculation =0;
nums = [79 79] %[157:-5:142 ]; % snapshot numbers for which to find spectrum
num1 = 79;%100; % For grid construction
P.interpm = 'spline';

rhoi = sqrt(0.3);
tauA = 6*48.1802; %Levs tauA = 206.4865395;
if strcmp(name,'lev'); tauA = 206.4865395;end

n2s = @(s) num2str(s);
sq=@(f) squeeze(f);
m3 = @(a) mean(mean(mean(a)));
s3 = @(a) sum(sum(sum(a)));
any3 = @(a) any(any(any(a)));
isodd = @(n) 2*mod(n/2,1);
fftperp = @(f) fft(fft(f,[],2),[],3); 
ifftperp = @(f) ifft(ifft(f,[],2),[],3);

[readF,files_all,folder,~,outputfolder] = chooseComputerAndFiles(name,computer);
savebase = ['saved-analysis/']; %outputfolder '../../' 
savefolder = [ savebase 'spectrum-kprlkprp-hel-' name '.mat'];

disp(['Saving/loading from ' savefolder])

if DoFullCalculation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   CONSTRUCT K GRID AND OTHER GENERAL BITS
% If 0, standard k grid, 0:2*pi/L:..., otherwise use standard until
% spacing smaller than numKgrid, then use logarithmic grid

% Basics of grid from early snapshot
D = readF(files_all(num1));
D = reduceResolution(D,P.derefine_prl,P.derefine_prp);

dx = D.x(2)-D.x(1);    dy = D.y(2)-D.y(1);    dz = D.z(2)-D.z(1);
Ls = [D.x(end)-D.x(1)+dx D.y(end)-D.y(1)+dy D.z(end)-D.z(1)+dz];
D.x = D.x - (D.x(1)-dx/2); % Shift the grid so it goes 0 to Ls
D.y = D.y - (D.y(1)-dy/2); % Shift the grid so it goes 0 to Ls
D.z = D.z - (D.z(1)-dz/2); % Shift the grid so it goes 0 to Ls
xg = D.x(:); yg = D.y(:); zg = D.z(:);
xge = [xg(1)-dx;xg;xg(end)+dx];yge = [yg(1)-dy;yg;yg(end)+dy];zge = [zg(1)-dz;zg;zg(end)+dz];
Ns = [length(D.x) length(D.y) length(D.z)];
% Grid in k space, for each dimension, conforming to FT standard [0 1 2 3 ... -N/2 -N/2+1 ... -1]
for kk=1:3
    K{kk} = 2i*pi/Ls(kk)*[0:(Ns(kk)/2-1) -Ns(kk)/2 -Ns(kk)/2+1:-1].';
end
[k3.KX, k3.KY, k3.KZ] = ndgrid(K{1},K{2},K{3}); % 3D grid in K
Kperp = sqrt(abs(k3.KY).^2 + abs(k3.KZ).^2); % |K|
% Kprl = (k3.KX); % Use KX grid on prl;
% Kmag = sqrt(abs(k3.KX).^2 + abs(k3.KY).^2 + abs(k3.KZ).^2);
clear k3; % Don't clear if you're doing the kH/B helicity calculation
NT2 = numel(Kperp)^2;

%%%%%%%%%%%%%%%%%%% Kperp grid  %%%%%%%%%%%%%%%%%%%%%%%%
kpgrid = logspace(log10(abs(K{2}(2))-1e-8),log10(max(abs(K{2}))) ,P.numKgrid(1) ).';
kpfull = [-1 ; kpgrid; 1e100];
Nkpfull = length(kpfull)-1;
[cnts,~, bins] = histcounts(Kperp(:),kpfull); 
bins = min(max(bins,1),Nkpfull);
cnts = cnts(2:end);
kpgrid(cnts==0)=[]; % This grid doesn't have any bins with nothing in them
% To hold the spectrum. Bins between kgrid(i:i+1)
Slh.Nkp = length(kpgrid)-1;
Slh.kp = kpgrid(2:end);
for kkk = 1:Slh.Nkp
    kr = kpgrid(kkk:kkk+1);
    Slh.nbinp(kkk) = s3(Kperp>=kr(1) & Kperp<kr(2));
end
Slh.nnormp = (Slh.nbinp.')./Slh.kp; 
Slh.nnormp = Slh.nnormp/sum(Slh.nnormp)*trapz(Slh.kp,ones(size(Slh.kp)));

%%%%%%%%%%%%%%%%%%% Kprl grid  %%%%%%%%%%%%%%%%%%%%%%%%
ds = dx; % Choose dx to get the max kprl you want. Need at least kmax/4 to get rhoi in the grid...
slen = P.flinlen*Ls(1);
sgrid = 0:ds:slen-ds; if isodd(length(sgrid));sgrid=sgrid(1:end-1);end
ns = length(sgrid);
nlines = floor(sqrt(P.nlines)).^2;
Ks = 2i*pi/slen*[0:(ns/2-1) -ns/2 -ns/2+1:-1].';
Ksall = repmat(Ks,[1,nlines]); % This is what you see from the interpolation
% Using sgrid to work out binning can cause problematic periodicities
klgrid = logspace(log10(abs(K{1}(2))-1e-8),log10(max(abs(K{1}))) ,P.numKgrid(2) ).'; % Use Kz dimensions for base grid
klfull = [-1 ; klgrid; 1e100];
Nklfull = length(klfull)-1;
[cnts,~, binsl] = histcounts(abs(K{1}),klfull); %Using kz to work out binning.
binsl = min(max(binsl,1),Nklfull);
cnts = cnts(2:end);
klgrid(cnts==0)=[]; % Grid for kl
% To hold the spectrum
Slh.Nkl = length(klgrid)-1;
Slh.kl = klgrid(2:end);
% Preload the bins and counts for each kl
klfull = [-1 ; klgrid; 1e100];
Nklfull = Slh.Nkl+2;
[cnts,~, binsl] = histcounts(abs(Ksall(:)),klfull); 
binsl = min(max(binsl,1),Nklfull);
NTL2 = numel(Ksall)^2;

Ksall(1,:) = 1i; % Remove zero to divide for helicity

% FILTER %%%%%%%%%%%%
fline_filter = hamming(ns,'periodic')/mean(hamming(ns,'periodic'));
% Number of modes in each bin
oneG = ones(sqrt(NTL2),1);
Slh.nbinl = spect1D(oneG,binsl,Nklfull,NTL2)*numel(oneG)^2; clear oneG;
Slh.nnorml = Slh.nbinl;
Slh.nnorml = Slh.nnorml/sum(Slh.nnorml)*trapz(Slh.kl,ones(size(Slh.kl)));
% Slh.nnorml =Slh.nnorml/Slh.nnorml(1)/nlines

disp(['Using ' n2s(length(kpgrid)) ' points in perp and ' n2s(length(klgrid)) ' points in parallel'])  
disp(['nlines*ns = ' n2s(nlines*ns) ', length(binsl) = ' n2s(length(binsl))])

% Average over all the snapshots
fields = {'h1'};
for var = fields;Slh.(var{1}) = [];end
Slh.t=[];Slh.nums=[];

save(savefolder,'Slh','P')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
load(savefolder,'Slh','P'); 
Slh
for nnn=nums
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
    [readF,files_all,folder] = chooseComputerAndFiles(name,computer);
    try 
        D = readF(files_all(nnn));
        D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
    catch 
        warning(['Did not find ' folder ' nnn=' num2str(nnn)])
        continue
    end

    Slh.t = [Slh.t D.t];
    Slh.nums = [Slh.nums nnn];
    B1 = D.Bcc1; B2 = D.Bcc2; B3 = D.Bcc3;
    clear D
    
    % Start by finding the field lines
    FBx = griddedInterpolant({xge,yge,zge},extArray(double(B1)),P.interpm,'none');
    clear B1
    FBy = griddedInterpolant({xge,yge,zge},extArray(double(B2)),P.interpm,'none');
    FBz = griddedInterpolant({xge,yge,zge},extArray(double(B3)),P.interpm,'none');
    
    disp(['Computing field lines from ' n2s(nlines) ' points'])
    ppnt = linspace(0,Ls(2),sqrt(nlines)+2);
    ppnt = ppnt(2:end-1);
    [Y,Z]=ndgrid(ppnt,ppnt);
    ics = [dx*ones(nlines,1) Y(:) Z(:)].';
    tic;[strue,flines] = ode45(@bhat,sgrid,ics(:));toc
    flines = permute(reshape(flines,[ns 3 nlines]),[1,2,3]);
    %     plot3(sq(flines(:,1,:)),sq(flines(:,2,:)),sq(flines(:,3,:)))
    lnX =  mod(sq(flines(:,1,:)),Ls(1));
    lnY = mod(sq(flines(:,2,:)),Ls(2));
    lnZ = mod(sq(flines(:,3,:)),Ls(3));
    if any3(isnan(lnY)) || any3(isnan(lnZ));warning('Found NaN in field lines');end
    if ns~=size(lnX,1); warning('Length of lnX not expected ns');end
    clear flines FBx FBy FBz;
        
    %%%%%%%%%%%%%%%%%%%%%%%
    % We now have the field lines in lnX lnY lnZ. Now apply a filter to the
    % kperp dimension. 
    for kkk = 1:Slh.Nkp
        disp(['Computing spectrum in kkk = ' n2s(kkk) ', kperp = ' n2s(kpgrid(kkk))])
        % Filter the data into kperp bin
        kr = kpgrid(kkk:kkk+1);
        filt = Kperp>=kr(1) & Kperp<kr(2);
        
        Dfilt = real(ifftperp(filt.*fftperp(B2)));
        FD = griddedInterpolant({xge,yge,zge},extArray(Dfilt),P.interpm,'none');
        Dflines = reshape(FD(lnX(:),lnY(:),lnZ(:)),[ns,nlines]).*fline_filter;
        if any3(isnan(Dflines));warning('Found NaN in interpolated filtered field');end
        ftBy = fft(Dflines,[],1);
        clear Dfilt FD Dflines
        
        Dfilt = real(ifftperp(filt.*fftperp(B3)));
        FD = griddedInterpolant({xge,yge,zge},extArray(Dfilt),P.interpm,'none');
        Dflines = reshape(FD(lnX(:),lnY(:),lnZ(:)),[ns,nlines]).*fline_filter;
        if any3(isnan(Dflines));warning('Found NaN in interpolated filtered field');end
        ftBz = fft(Dflines,[],1);
        clear Dfilt FD Dflines
        
        tmp(kkk,:) = spectHel(1i*(ftBy.*conj(ftBz) - ftBz.*conj(ftBy))./imag(Ksall),...
            binsl,Nklfull,NTL2)./Slh.nnorml./Slh.nnormp(kkk);
        disp(['As a solution check: tmp(kkk,10) = ' n2s(tmp(kkk,10))])
    end
    Slh.h1 = cat(3, Slh.h1, tmp);
    
    save(savefolder,'Slh','P');
    
end
    Slh.n = length(Slh.t);
    save(savefolder,'Slh','P');

else % doFullCalculation
    load(savefolder,'Slh','P');
end 

load([ savebase 'spectrum-kprlkprp-' name '.mat'],'Sl');


tav = [5 21];
% Sl=St;
Slh.t=Slh.t/tauA;
m = @(d) mean(d(:,:,find(Slh.t>=tav(1),1):find(Slh.t<=tav(2),1,'last')),3);
disp(['Averaging nums ' n2s(find(Slh.t>=tav(1),1)) ' to ' n2s(find(Slh.t<=tav(2),1,'last'))])

tstrt=0;
normplot = 1;lims = [-10,0];

if plotB
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.4, 0.5]);
%     for n=tstrt:Slh.n-1; m = @(d) d(:,:,n+1);Slh.t(n+1)
    
%     s=pcolor(log10(Slh.kp),log10(Slh.kl),log10(Bprp).');
%     s.EdgeColor='none';s.FaceColor='interp';
    nl = length(Slh.kl);np = length(Slh.kp);
    Bprp = mean(Sl.Bcc2+Sl.Bcc3,3);
    Bprp = Bprp(1:np,1:nl);
    kmag = sqrt(Slh.kp.^2 + (Slh.kl.').^2);
    s=pcolor(log10(Slh.kp),log10(Slh.kl),-(m(Slh.h1)./Bprp.*kmag).');%,40,'Linecolor',0.5*[1 1 1])
    s.EdgeColor='none';s.FaceColor='interp';
    colorbar;   caxis([-1 1]) %colormap(brewermap([],'PuBuGn')) 
    hold on
    plot(log10(Slh.kp),2/3*log10(Slh.kp/Slh.kp(1))+log10(Slh.kl(1)),'k:')
    plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(Slh.kp),zeros(size(Slh.kp)),'k:')
    xlabel('$\log_{10} k_\perp$','interpreter','latex')
    ylabel('$\log_{10} k_\|$','interpreter','latex')
    xlim(log10([min(Sl.kp) max(Sl.kp)]))
    ylim(log10([min(Sl.kl) max(Sl.kl)]))
     title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])
%     ginput(1);end
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


% % Test cut power spectra from edge effects
% ns = 1000; nlines = 1200; L = 1; npl=ns/2;
% ff = randn(ns,nlines);
% ks = 2*pi/L*[0:ns/2-1 -ns/2:1:-1].';
% ks(1) =1;
% kpl = abs(ks(1:npl));
% ff = ifft(1./abs(ks).^2.*fft(ff,[],1));
% ps = @(f) abs(fft(f,[],1)).^2;
% pspl = ps(ff);
% loglog(kpl,mean(pspl(1:npl,:),2) )
% npl = 400;
% ff = ff(1:npl*2,:);
% kpl = kpl(1:npl);
% pspl = ps(ff);
% hold on
% loglog(kpl,mean(pspl(1:npl,:),2) )

end


function out = spect1D(v1,bins,ngrid,NT2)
% Fast version of 1D spectrum 
out = (full(sparse(ones(size(bins,1),1),bins,abs(double(v1(:))).^2,1,ngrid))/NT2).';
out = out(2:end-1); % Include extra bins at the ends for the ones that are missed out
end

function out = spectHel(v1,bins,ngrid,NT2)
% Fast version of 1D spectrum 
out = (full(sparse(ones(size(bins,1),1),bins,double(v1(:)),1,ngrid))/NT2).';
out = out(2:end-1); % Include extra bins at the ends for the ones that are missed out
end
 

function Ax=extArray(Ax)
% Extend array through periodicity
Ax = cat(1,Ax(end,:,:),Ax,Ax(1,:,:));
Ax = cat(2,Ax(:,end,:),Ax,Ax(:,1,:));
Ax = cat(3,Ax(:,:,end),Ax,Ax(:,:,1));
end

