function readTrackBinary%(file,P)

name = 'imbal2-prod';

computer = 'tigress';
DoFullCalculation =0;
nums = [131:135 137:219]; % snapshot numbers for which to find spectrum
sname = @(n) ['track.' sprintf('%02d',n)]; % 0 is 0-9, 1 is 10-19 etc.
% Actually, isn't worth resaving. These are quick to read

% Reads the tracks files to get particle tracks
P.forceyyn = 1;
P.twoD = 0; P.oneD=0;
nmeas = 19+P.forceyyn*3;
if P.twoD;nmeas=nmeas-2;end
if P.oneD;nmeas=nmeas-4;end
beta = 0.3;
tauA = 6*67.4523; % Levs tauA = 206.4865395;
L = [6*67.4523,67.4523,67.4523];


isint = @(n) round(n)==n;
n2s = @(s) num2str(s);
sq = @(f) squeeze(f);

[~,~,folder,~,outputfolder,~,track] = chooseComputerAndFiles(name,computer);
trackfolder = [outputfolder  'track_binary_mpiio/'];

dfull = [];

if DoFullCalculation

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   LOOP OVER SNAPSHOTS
% load([swarmfolder sname '.mat'],'sarray_full');
pselect = randi(164640,1000,1);
disp(['Saving to ' outputfolder '/track1000prtls.mat'])
load([outputfolder '/track1000prtls.mat'],'dfull')
for nnn=nums
    disp([''])
    disp(['<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>'])
    disp(['Doing ' folder ' nnn = ' num2str(nnn)])
   

    fid = fopen([trackfolder track(nnn)]);
    tfile = fscanf(fid, 'Particle track output function at time = %f');
    fgetl(fid); % Not sure what this is...

    data = fread(fid,1e100,'float64',0,'l');
    if isint(size(data,1)/nmeas)
        data = reshape(data,[nmeas,size(data,1)/nmeas]);
    else
        error(['Track cnt dimensions don''t match'])
    end

    nmb = max(data(2,:)-0.001)+1;
    ntrck = max(data(1,:)-0.001)+1;
    disp(['I think there''s ' n2s(ntrck) ' particles per block on ' n2s(nmb) ' blocks = ' n2s(ntrck*nmb)])
    pnum = nmb*(data(1,:)-0.001) + (data(2,:)-0.001);
    data = sortrows([pnum; data(3:end,:)].').';


    tlens = diff(find(diff(data(1,:))>0)); % length of each t vector
    if all(tlens==tlens(1))
        data = reshape(data,[size(data,1) tlens(1) size(data,2)/tlens(1)]);
    else
        error('Found different of t vectors, have to upgrade to deal with this')
    end
    
    % Data dimensions: (quantity, time, particle)
    % Quantities: 1 id: 2 t: 3-5 x: 6-8 v: 9-11 B: 12-14 E: 15-17 U: 18 rho: 19-21 F
    disp(['Data from t=' n2s(data(2,1,1)/tauA) ' to ' n2s(data(2,end,1)/tauA)])
    
    fclose(fid);
    
    dfull = cat(2,dfull,data(:,:,pselect));
    size(dfull)
    
    if mod(nnn,10)==0
        save([outputfolder '/track1000prtls.mat'],'dfull','pselect')
    end
end
% Could save some statistics here
save([outputfolder '/track1000prtls.mat'],'dfull','pselect')

else % DoFullCalculation
    load([ '../simulations/' name '/track1000prtls.mat'],'dfull')
end

% Try plotting a random sample of wprl>0 (scattering?) and wprl<0 (not
% scattering)

nprt = size(dfull,3);
uwrp = @(s,l) unwrap(s*(2*pi)/l,1)*l/(2*pi);
width = 10; % Output freq is 2*pi/10;l
filt = @(f) filter(1/width*ones(width,1),1,f);
i=0;

t = sq(dfull(2,:,1));
in = t>4000;t=t(in);
xf = (sq(dfull(3,in,:)));
yf = (sq(dfull(4,in,:)));
zf = (sq(dfull(5,in,:)));
Bf = sq(sqrt(sum(dfull(9:11,in,:).^2,1)));
wprlf = sq(sum(dfull(6:8,in,:).*dfull(9:11,in,:),1))./Bf;
enf = sq(sum(dfull(6:8,in,:).^2,1));
wprpf = sqrt(enf - wprlf.^2);

while i<10
    
    rsamp = randi(nprt,20,1);
    x = uwrp(xf(:,rsamp),L(1));
    y = uwrp(yf(:,rsamp),L(2));
    z = uwrp(zf(:,rsamp),L(3));
    B = Bf(:,rsamp);
    wprl = wprlf(:,rsamp);
    en = enf(:,rsamp);
    wprp = wprpf(:,rsamp);
    
    wprlm = mean(wprl,1);
    fwd = wprlm>0.2; bkw = wprlm<-0.2;
%     % Random trajectories – ruined by box edges
%     figure
%     subplot(211)
%     plot3(x(:,fwd),y(:,fwd),z(:,fwd))
%     pbaspect([6 1 1])
%     subplot(212)
%     plot3(x(:,bkw),y(:,bkw),z(:,bkw))
%     pbaspect([6 1 1])
    % Energy and mu trajectories
    figure
%     subplot(611)
%     semilogy(t,filt(en(:,fwd)))
%     subplot(612)
%     semilogy(t,filt(en(:,bkw)))
    subplot(411)
    semilogy(t,filt(wprp(:,fwd).^2./B(:,fwd)))
    subplot(412)
    semilogy(t,filt(wprp(:,bkw).^2./B(:,bkw)))
    subplot(413)
    plot(t,wprl(:,fwd))
    subplot(414)
    plot(t,wprl(:,bkw))
    i=i+1;
end

% % Find particles in range with different characteristics
% trang = [15.8 20];
% xrang = [0 L(1)];
% yrang = [65 10];
% zrang = [10 60];
% 
% 
% in = t/tauA>trang(1) & t/tauA <trang(2);
% t=t(in);
% % Change OR parts depending on which edge you want
% numin = sum( x(in,:)>xrang(1) & x(in,:)<xrang(2) & ...
%     (y(in,:)>yrang(1) | y(in,:)<yrang(2)) & ...
%     z(in,:)>zrang(1) & z(in,:)<zrang(2),1);
% prtls = find(numin>length(t)/2);
% 
% vth = sqrt(beta);
% pfwd = mean(wprl(in,prtls),1)>0.5*vth &  mean(wprl(in,prtls),1)<1.2*vth;
% pbwd = mean(wprl(in,prtls),1)<-0.5*vth &  mean(wprl(in,prtls),1)>-1.2*vth;
% 
% xfwd  = uwrp(x(in,prtls(pfwd)),L(1));
% yfwd  = uwrp(y(in,prtls(pfwd)),L(2));
% zfwd  = uwrp(z(in,prtls(pfwd)),L(3));
% xbwd = uwrp(x(in,prtls(pbwd)),L(1));
% ybwd = uwrp(y(in,prtls(pbwd)),L(2));
% zbwd = uwrp(z(in,prtls(pbwd)),L(3));
% 
% % Assume 3D plot is open
% hold on
% caxis([-0.4 0.4])
% % alpha 0.8
% plot3(xfwd,0*yfwd,zfwd,'b')
% plot3(xbwd,0*ybwd,zbwd,'k')

end


