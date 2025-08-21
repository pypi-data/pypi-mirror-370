% Very simple spectrum from x,y,z and data input
function S=spectrum%(name)

name = 'first_attempt';

P.numKgrid = 120; % nonzero for logarithmic binning
P.perp=1;
P.derefine_prl =1; P.derefine_prp=1;

computer = 'tigress';
DoFullCalculation =1;
nums = 53; % snapshot numbers for which to find spectrum


n2s = @(s) num2str(s);
[readF,files_all,folder] = chooseComputerAndFiles(name,computer);

if DoFullCalculation

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   CONSTRUCT K GRID AND OTHER GENERAL BITS
% If 0, standard k grid, 0:2*pi/L:..., otherwise use standard until
% spacing smaller than numKgrid, then use logarithmic grid

% Form grid of K using first time step
num1 = nums(1);
D = readF(files_all(num1));
D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
D
dx = D.x(2)-D.x(1);
dy = D.y(2)-D.y(1);
dz = D.z(2)-D.z(1);
Ls = [D.x(end)-D.x(1)+dx D.y(end)-D.y(1)+dy D.z(end)-D.z(1)+dz];
Ns = [length(D.x) length(D.y) length(D.z)];
% Grid in k space, for each dimension, conforming to FT standard [0 1 2 3 ... -N/2 -N/2+1 ... -1]
for kk=1:3
    K{kk} = 2i*pi/Ls(kk)*[0:(Ns(kk)/2-1) -Ns(kk)/2 -Ns(kk)/2+1:-1].';
end
[k3.KX, k3.KY, k3.KZ] = ndgrid(K{1},K{2},K{3}); % 3D grid in K
Kmag = sqrt(abs(k3.KX).^2 + abs(k3.KY).^2 + abs(k3.KZ).^2); % |K|
Kperp = sqrt(abs(k3.KY).^2 + abs(k3.KZ).^2); % |K|
if P.perp;Kspec = Kperp;else; Kspec=Kmag;end % The one to use
clear Kperp Kmag k3

% % Bins for k
% kgrid = (0:2*pi/Ls(2):max(imag(K{2}))).'+1e-12; % Use ky for spectrum binning
% if P.numKgrid ~= 0
%     kgridL = logspace(log10(abs(K{2}(2))),log10(max(abs(K{2}))) ,P.numKgrid ).'; 
%     iswtch = find(diff(kgridL)<2*pi/Ls(2),1,'last');
%     lin2log = find(kgrid<kgridL(iswtch+1),1,'last'); % index at which you switch to log scale
%     kgrid = [kgrid(1:lin2log-1);  logspace(log10(kgrid(lin2log)),log10(max(abs(K{2}))), length(kgridL(iswtch+1:end)) ).' ];
% end
% Diferent version: logarithmic, but remove unused bins at small k
kgrid = logspace(log10(abs(K{2}(2))-1e-8),log10(max(abs(K{2}))) ,P.numKgrid ).';
kfull = [-1 ; kgrid; 1e100];
Nkfull = length(kfull)-1;
[cnts,~, bins] = histcounts(Kspec(:),kfull); 
bins = min(max(bins,1),Nkfull);
cnts = cnts(2:end);
kgrid(cnts==0)=[];

% To hold the spectrum
S.Nk = length(kgrid)-1;
S.k = kgrid(2:end);

% Preload the bins and counts for each k
kfull = [-1 ; kgrid; 1e100];
Nkfull = S.Nk+2;
[cnts,~, bins] = histcounts(Kspec(:),kfull); 
bins = min(max(bins,1),Nkfull);
NT2 = numel(Kspec)^2;
clear Kspec;

% Count the number of modes in each bin to normalize later -- this gives a
% smoother result, since we want the average energy in each bin.
oneG = ones(sqrt(NT2),1);
S.nbin = spect1D(oneG,bins,Nkfull,NT2)*numel(oneG)^2;
clear oneG;

S.nnorm = S.nbin./S.k.^2; % k^2 accounts for the fact that in 3D, number of modes in shell increases with k^2
if P.perp;S.nnorm = S.nbin./S.k; end
S.nnorm = S.nnorm/S.nnorm(2); % Want normalization to be the same as for a linear k grid
% S.nnorm = 1;

m3 = @(a) mean(mean(mean(a)));

% Average over all the snapshots
fields = {'vel1','vel2','vel3','Bcc1','Bcc2','Bcc3'};%,'zp1','zp2','zp3','zm1','zm2','zm3'};
for var = fields;S.(var{1}) = [];end

S.t=[];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
% load(['saved-analysis/spectrum-' name '.mat'],'S');
for nnn=nums
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
    try 
        D = readF(files_all(nnn));
        D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
    catch 
        warning(['Did not find ' filename(nnn,o_ids(1))])
        continue
    end
    S.t = [S.t D.t];
    
%     ft = fftn(D.vel1);
%     tic;S.v1 = spect1Dslow(ft,ft,Kspec,kgrid);toc;
%     tic;v1 = spect1D(ft,bins,Nkfull,NT2);toc;
    
    
    for var = {'vel1','vel2','vel3'}
        ft = fftn(D.(var{1}));
        S.(var{1}) = [S.(var{1})  spect1D(ft,bins,Nkfull,NT2)];
    end
    for var = {'Bcc1','Bcc2','Bcc3'}
        ft = fftn(D.(var{1}));
        S.(var{1}) = [S.(var{1})  spect1D(ft,bins,Nkfull,NT2)];
    end
%     for var = {'zp1','zp2','zp3','zm1','zm2','zm3'}
%         ft = fftn(D.(var{1}));
%         S.(var{1}) = [S.(var{1})  spect1D(ft,bins,Nkfull,NT2)];
%     end

end
S.n = length(S.t);
for var = fields
    S.(var{1}) =  S.(var{1})./repmat(S.nnorm,[1 length(S.n)]);
end

S.nums = nums;

save(['saved-analysis/spectrum-' name '.mat'],'S','P');
else % DoFullCalculation
    load(['saved-analysis/spectrum-' name '.mat'],'S');
    disp(S)
end


%%%%%%%%%%%%%%%%%% PLOTTING %%%%%%%%%%%%%%%%%%%%%
S.EK = (S.vel1+S.vel2+S.vel3)/2;
S.EM = (S.Bcc1+S.Bcc2+S.Bcc3)/2;
%S.Ezp = (S.zp1+S.zp2+S.zp3)/2;
%S.Ezm = (S.zm1+S.zm2+S.zm3)/2;

rhoi=sqrt(0.3);

tav = [4000 7000];
itav = [find(S.t>=tav(1),1);find(S.t<=tav(2),1,'last')];
m = @(d) mean(d(:,itav(1):itav(2)),2);

% figure
set(gcf, 'Units', 'Normalized', 'OuterPosition', [0.5, 0.4, 0.3, 0.6]);
for n=0:S.n-1; m = @(d) d(:,n+1);mm = @(d) d(n+1);S.t(n+1)
%subplot(211)
loglog(S.k, m(S.EK),'.-', S.k, m(S.EM),'.-')
hold on
k53 = S.k(S.k<1);k28 = S.k(S.k>1); k4 = S.k(S.k>1); 
k28mult = 0.5e-3;k53mult = 5e-2;k4mult = 1e-3;
loglog(k53,k53mult.*(k53/k53(1)).^(-5/3),'k:',k28,k28mult*(k28/k28(1)).^(-2.8),'k:',k4,k4mult*(k4/k4(1)).^(-4),'k:',...
    rhoi*[1 1],[1e-30,1e10],'k:')
ylabel('$E_K$','interpreter','latex')
xlabel('$k$','interpreter','latex')
legend({'$E_K$','$E_M$','$k^{-5/3}$'},'interpreter','latex')
ylim([1e-8 0.1])
xlim([min(S.k) max(S.k)])
title({name})
hold off
%subplot(212)
%loglog(S.k, m(S.Ezp),'.-', S.k, m(S.Ezm),'.-')
%hold on
%loglog(k53, k53mult.*(k53/k53(1)).^(-5/3),'k:',k28,k28mult*(k28/k28(1)).^(-2.8),'k:',k4,k4mult*(k4/k4(1)).^(-4),'k:',...
%    rhoi*[1 1],[1e-30,1e10],'k:')
%ylabel('$E_+$','interpreter','latex')
%xlabel('$k$','interpreter','latex')
%legend({'$E_+$','$E_-$','$k^{-5/3}$'},'interpreter','latex')
%ylim([1e-8 0.1])
%xlim([min(S.k) max(S.k)])
%hold off
% title(["t=" num2str(S.t(n+1))]);ginput(1);end
title(['t=' num2str(S.t(n+1))]);drawnow;end

% oldpath = path;
% path(oldpath,'~/Research/export-fig')
% set(gcf,'color','w')
% export_fig(['saved-states/spectrum-' folder '.pdf']) 

end


function out = spect1D(v1,bins,ngrid,NT2)
% Faster version of 1D spectrum 

out = (full(sparse(ones(size(bins,1),1),bins,abs(v1(:)).^2,1,ngrid))/NT2).';
out = out(2:end-1); % Include extra bins at the ends for the ones that are missed out

end


function out = spect1Dslow(v1,v2,K,kgrid)
% Function to find the spectrum <v1 v2>, 
% K is the kgrid associated with v1 and v2
% kgrid is the grid for spectral shell binning

nk = length(kgrid)-1;
out = zeros(nk,1);
NT2 = numel(K)^2;
for kk = 1:nk
    out(kk) = sum( real(v1(K<kgrid(kk+1) & K>kgrid(kk)).*conj(v2(K<kgrid(kk+1) & K>kgrid(kk)))) )/NT2;
end

end

