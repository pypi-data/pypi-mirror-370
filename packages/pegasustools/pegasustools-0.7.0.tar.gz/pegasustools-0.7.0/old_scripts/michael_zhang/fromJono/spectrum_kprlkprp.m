function spectrum_kprlkprp
% 2D spectrum of B and E
name = 'half_tcorr_sim9'%'sig-decr-prod';'test-frontera-run';

P.numKgrid =  [200 400];%[200 400]; % Perp parallel grid.
%P.derefine_prl =1; P.derefine_prp=1;
P.derefine_prl =4; P.derefine_prp=1;
P.flinlen = 60;%10 % Length of field line compared to Lx. Can be arbitrary but will change the kprl grid a bit.
P.nlines = 2000%2000; % Number of field lines to use. 

% A couple of notes. It is good to use a field line length ~2-100 times the
% size of the box (matlab is actually faster). The filter is important for
% making the spectrum more featured and the Hammond one seems best.
% Don't over sample at low kprl, even if the field line length is long.
% Best to use kz to construct the grid.
% There is still something wrong with the overall normalization. I get
% consistent results with different length lines etc., but they are scaled
% by some overall factor...

% NOTE: There are some subtleties worth checking with this method. See
% notes in KRMHD file. Seems problematic when B is very large amplitude.

plotB = 1;
plotKprlKprp = 0;
paperSave = 0;
plotBvkprl = 0;

computer = 'tigress';
DoFullCalculation =0;
reloadSpectrumFile = 1;
%nums = [0:153  ]; % snapshot numbers for which to find spectrum
%nums = [64:86];
%nums = [132:152];%[64:86]; 
%nums = [64:86 132:152];
nums = [70:80 137:147];%70:80
num1 = nums(1); % For grid construction
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
savefolder = [ savebase 'spectrum-kprlkprp-derefprl4-n75-len60-200-400-' name '.mat'];

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
clear D;
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
%hack kpgrid to combine the first few bins in kperp
%kpgrid = logspace(log10(abs(K{2}(2))-1e-8),log10(max(abs(K{2}))) ,P.numKgrid(1) );
%kpgrid = [kpgrid(1:26) kpgrid(27)-0.0025 kpgrid(27) kpgrid(27)+0.001 10^-0.6  kpgrid(28)-0.0025 kpgrid(28)-0.001 kpgrid(28) kpgrid(29:end)].';
%kpgrid = [kpgrid(1:18) kpgrid(19)+0.0025 kpgrid(35)-0.0025 kpgrid(36:end)].';
%disp("combined bins are ")
%disp(kpgrid(26))
%disp(kpgrid(27))
%disp(kpgrid(28))
%disp(kpgrid(29))
%disp(kpgrid(18:22))
%disp(kpgrid(16))
%disp(kpgrid(21))
kpfull = [-1 ; kpgrid; 1e100];
Nkpfull = length(kpfull)-1;
[cnts,~, bins] = histcounts(Kperp(:),kpfull); 
bins = min(max(bins,1),Nkpfull);
cnts = cnts(2:end);
kpgrid(cnts==0)=[]; % This grid doesn't have any bins with nothing in them
% To hold the spectrum. Bins between kgrid(i:i+1)
Sl.Nkp = length(kpgrid)-1;
Sl.kp = kpgrid(2:end);%discard first element for saved kperp grid
for kkk = 1:Sl.Nkp
    kr = kpgrid(kkk:kkk+1);%get left and right values of kperp for bin
    Sl.nbinp(kkk) = s3(Kperp>=kr(1) & Kperp<kr(2));% sum up all kperp between the two bins in kpgrid for norm.
end
Sl.nnormp = (Sl.nbinp.')./Sl.kp; 
Sl.nnormp = Sl.nnormp/sum(Sl.nnormp)*trapz(Sl.kp,ones(size(Sl.kp)));

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
Sl.Nkl = length(klgrid)-1;
Sl.kl = klgrid(2:end);
% Preload the bins and counts for each kl
klfull = [-1 ; klgrid; 1e100];
Nklfull = Sl.Nkl+2;
[cnts,~, binsl] = histcounts(abs(Ksall(:)),klfull); 
binsl = min(max(binsl,1),Nklfull);
NTL2 = numel(Ksall)^2;
clear Ksall;
% FILTER %%%%%%%%%%%%
fline_filter = hamming(ns,'periodic')/mean(hamming(ns,'periodic'));
% Number of modes in each bin
oneG = ones(sqrt(NTL2),1);
Sl.nbinl = spect1D(oneG,binsl,Nklfull,NTL2)*numel(oneG)^2; clear oneG;
Sl.nnorml = Sl.nbinl;
Sl.nnorml = Sl.nnorml/sum(Sl.nnorml)*trapz(Sl.kl,ones(size(Sl.kl)));
% Sl.nnorml =Sl.nnorml/Sl.nnorml(1)/nlines

disp(['Using ' n2s(length(kpgrid)) ' points in perp and ' n2s(length(klgrid)) ' points in parallel'])  
disp(['nlines*ns = ' n2s(nlines*ns) ', length(binsl) = ' n2s(length(binsl))])

% Average over all the snapshots
fields = {'Bcc2','Bcc3','Ecc2','Ecc3'};%'spl','smn'};
for var = fields;Sl.(var{1}) = [];end
Sl.t=[];Sl.nums=[];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
if reloadSpectrumFile
    load(savefolder,'Sl','P');
    Sl
end
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

    Sl.t = [Sl.t D.t];
    Sl.nums = [Sl.nums nnn];
    
    % Start by finding the field lines
    FBx = griddedInterpolant({xge,yge,zge},extArray(double(D.Bcc1)),P.interpm,'none');
    FBy = griddedInterpolant({xge,yge,zge},extArray(double(D.Bcc2)),P.interpm,'none');
    FBz = griddedInterpolant({xge,yge,zge},extArray(double(D.Bcc3)),P.interpm,'none');
    
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
    for kkk = 1:Sl.Nkp
        disp(['Computing spectrum in kkk = ' n2s(kkk) ', kperp = ' n2s(kpgrid(kkk))])
        % Filter the data into kperp bin
        kr = kpgrid(kkk:kkk+1);
        filt = Kperp>=kr(1) & Kperp<kr(2);
        for var = fields
            % Looping over fields
            Dfilt = real(ifftperp(filt.*fftperp(D.(var{1}))));
            % Interpolate to field lines
            FD = griddedInterpolant({xge,yge,zge},extArray(Dfilt),P.interpm,'none');
            Dflines = reshape(FD(lnX(:),lnY(:),lnZ(:)),[ns,nlines]).*fline_filter;
            if any3(isnan(Dflines));warning('Found NaN in interpolated filtered field');end
            ft = fft(Dflines,[],1);
            tmp.(var{1})(kkk,:) = spect1D(ft(:),binsl,Nklfull,NTL2)./Sl.nnorml./Sl.nnormp(kkk);
            disp(['As a solution check: tmp.(var{1})(kkk,10) = ' n2s(tmp.(var{1})(kkk,10))])
        end
        
    end
    for var = fields
        Sl.(var{1}) = cat(3,Sl.(var{1}), tmp.(var{1}));
    end
  
    save(savefolder,'Sl','P');
    
end
    Sl.n = length(Sl.t);
    save(savefolder,'Sl','P');

else % doFullCalculation
    load(savefolder,'Sl','P');
end 

% load([ savebase 'spectrum2D-' name '.mat'],'St');

tav = [7.0 8.0];
%tav = [6.5 8.5];
tav2 = [13.7 14.7];
% Sl=St;
Sl.t=Sl.t/tauA;
m = @(d) mean(d(:,:,find(Sl.t>=tav(1) & Sl.t<=tav(2))),3);
m2 = @(d) mean(d(:,:,find(Sl.t>=tav2(1) & Sl.t<=tav2(2))),3);
disp(['Averaging nums ' n2s(find(Sl.t>=tav(1) & Sl.t<=tav(2)))])
disp(['Averaging nums ' n2s(find(Sl.t>=tav2(1) & Sl.t<=tav2(2)))])

tstrt=0;
normplot = 1;lims = [-10,0];
dn=1;
Bprp = {};
if paperSave
    kls = Sl.kl;
    kps = Sl.kp .* rhoi;
    Bprp{1} = m(Sl.Bcc2 + Sl.Bcc3);Bprp{1} = Bprp{1}./normplot;
    Bprp{2} = m2(Sl.Bcc2 + Sl.Bcc3);Bprp{2} = Bprp{2}./normplot;
    Bprp
    save([ savebase 'PlotSpectrum_kprlkprpv2-' name '.mat'],'Bprp','kls','kps', '-v7.3');
end



if plotB
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.4, 0.5]);
    % for n=dn:dn+1:Sl.n-dn; m = @(d) mean(d(:,:,n-dn+1:n+dn),3);Sl.t(n+1)
    Bprp = m(Sl.Bcc2 + Sl.Bcc3);Bprp = Bprp./normplot;
    Eprp = m(Sl.Ecc2 + Sl.Ecc3);Eprp = Eprp./normplot;
%     s=pcolor(log10(Sl.kp),log10(Sl.kl),log10(Bprp).');
%     s.EdgeColor='none';s.FaceColor='interp';
    contourf(log10(Sl.kp),log10(Sl.kl),log10(Bprp).',40,'Linecolor',0.5*[1 1 1])
    colorbar;  % caxis(lims) colormap(brewermap([],'PuBuGn')) 
    hold on
    plot(log10(Sl.kp),2/3*log10(Sl.kp/Sl.kp(1))+log10(Sl.kl(1)),'k:')
    plot(log10(1/rhoi)*[1 1], [-10 10],'k:',log10(Sl.kp),zeros(size(Sl.kp)),'k:')
    %plot(log10(Sl.kp),log10(ones(size(Sl.kp))).*1,'k:')
    %plot(log10(Sl.kp), log10(ones(size(Sl.kp))).*1/2,'b:')
    %plot(log10(Sl.kp), log10(ones(size(Sl.kp))).*5/16,'o:')
    plot(log10(Sl.kp),log10(ones(size(Sl.kp)) ), 'r--','Linewidth', 1.5   ) ;
    plot(log10(Sl.kp),log10(ones(size(Sl.kp)).* 1/2 ), '--','Color',[0.6350 0.0780 0.1840],'Linewidth', 1.5   ) ;
    plot(log10(Sl.kp),log10(ones(size(Sl.kp)).* 5/16 ), 'c--','Linewidth', 1.5   ) ;
    hold off
    xlabel('$\log_{10} k_\perp$','interpreter','latex')
    ylabel('$\log_{10} k_\|$','interpreter','latex')
    xlim(log10([min(Sl.kp) max(Sl.kp)]))
    ylim(log10([min(Sl.kl) max(Sl.kl)]))
    %  title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])
    % ginput(1);end
end


if plotBvkprl
    %for min kprp
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.4, 0.5]);
    Bprp1 = m(Sl.Bcc2 + Sl.Bcc3);Bprp1 = Bprp1./normplot;
    Bprp2 = m2(Sl.Bcc2 + Sl.Bcc3);Bprp2 = Bprp2./normplot;
    plot(log10(Sl.kl),log10(Bprp1(2,:)))
    hold on
    plot(log10(Sl.kl),log10(Bprp2(2,:)))
    plot(log10(1)*[1 1], [-10 10],'k:')
    plot(log10(1/2)*[1 1], [-10 10],'b:')
    plot(log10(5/16)*[1 1], [-10 10],'o:')
    xlabel('$\log_{10} k_\|$','interpreter','latex')
    ylabel('$\log_{10} B_\perp(log10(k_\perp) = -0.6)$','interpreter','latex')
    xlim(log10([min(Sl.kl) max(Sl.kl)]))
    Sl.kp(1)
    Sl.kp(2)
    log10(Sl.kp(1))
    log10(Sl.kp(2))
    %0.2511

end

if plotKprlKprp
    figure('Color',[1 1 1]);
    set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.27, 0.7]);
%     for n=tstrt:Sl.n-1; m = @(d) d(:,:,n+1);Sl.t(n+1)
    Bprp = m(Sl.Bcc2 + Sl.Bcc3);
    EpBprp = trapz(Sl.kl,Bprp,2);
    ElBprp = trapz(Sl.kp,Bprp,1).';
    % Integrate to get structure functions
    Sprp = -flipud(cumtrapz(flipud(Sl.kp),flipud(EpBprp)));
    Sprl = -flipud(cumtrapz(flipud(Sl.kl),flipud(ElBprp)));
    subplot(211)
    loglog(Sl.kp,EpBprp,Sl.kl,ElBprp,'.-');
    hold on
    k53 = Sl.kp( Sl.kp<1/(rhoi));k2 = Sl.kl( Sl.kl<1); k6 = Sl.kl( Sl.kl<1/(rhoi) & Sl.kl>0.5); 
    k53mult = 8e-5;k2mult = 0.5e-3;k6mult = 1e-5;
    loglog(k53,k53mult.*(k53/k53(1)).^(-5/3),'k:',k2,k2mult*(k2/k2(1)).^(-2),'k:',k6,k6mult*(k6/k6(1)).^(-6),'k:',...
        1/rhoi*[1 1],[1e-30,1e10],'k:')
    ylim([1e-9 1e-3])
    xlim([min(Sl.kl) max(Sl.kp)])
    title(['$t=' n2s(tav(1)) '$ to $t=' n2s(tav(2)) '$'])
    legend({'$E_B(k_\perp)$','$E_B(k_\|)$','$k^{-5/3}$','$k^{-2}$','$k^{-6}$'})
    xlabel('$k d_i$','interpreter','latex')
    subplot(212)
%     sfprl = sf(:,1); sfprp = sf(:,end);
%     notnan = ~isnan(Sprp) & ~isnan(Sprl);
    kprl = interp1(Sprl,Sl.kl,Sprp,'spline',NaN);
%     Sl.kp = Sl.kp*rhoi;kprl = kprl*rhoi;
    loglog(Sl.kp,kprl)
    k23 = Sl.kp(Sl.kp<1);k1 = Sl.kp(Sl.kp>0.8 & Sl.kp<2/(rhoi)); k13 = Sl.kp(Sl.kp>1.2/rhoi); 
    k23mult = 3.5*min(Sl.kl)/2;k1mult = 0.4/2;k13mult = 1/2;
    hold on
    loglog(k23,k23mult.*(k23/k23(1)).^(2/3),'k:',k1,k1mult*(k1/k1(1)).^(1),'k:',k13,k13mult*(k13/k13(1)).^(1/3),'k:',...
        1/rhoi*[1 1],[1e-30,1e10],'k:')
    xlim([min(Sl.kp) 10])
    ylim([min(Sl.kl) 1/sqrt(rhoi)])
    ylabel('$k_\| d_i$','interpreter','latex')
    xlabel('$k_\perp d_i$','interpreter','latex')
    legend({'$k_\|(k_\perp)$','$k_\perp^{2/3}$','$k_\perp^{1}$','$k_\perp^{1/3}$'})
    % kprp versus kprl
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
 

function Ax=extArray(Ax)
% Extend array through periodicity
Ax = cat(1,Ax(end,:,:),Ax,Ax(1,:,:));
Ax = cat(2,Ax(:,end,:),Ax,Ax(:,1,:));
Ax = cat(3,Ax(:,:,end),Ax,Ax(:,:,1));
end

