function plot_hst_forcing%( fname )

name = 'first_attempt';
p_id = 'minor_turb';
fname = ['../simulations/' name '/' p_id ]; % Folder with outputs']; % Folder with outputs

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
is = restart_overlaps(t);

dt = dat(:,2);
dthst = diff(t);dthst = [ dthst(1);dthst ];
vol=6*48.1802^3;
tauA = 6*48.1802;
tcorr = 144.54;

%find = 38 ;
%forceen = dat(:,find:find+3)*vol*tcorr;

figure
%subplot(211)
%plot(t,forceen,t,sum(forceen,2),'k')

epsind = 34;
diss_hypr = dat(:,epsind-1)./dthst*vol;
dedt = (dat(:,epsind)+dat(:,epsind+1))./dthst*vol;
dehdt = (dat(:,epsind+2)+dat(:,epsind+3))./dthst*vol;
deudt = (dat(:,epsind))./dthst*vol; debdt = (dat(:,epsind+1))./dthst*vol;

%subplot(212)
plot(t,dedt,t,dehdt,t,deudt,t,debdt,t,diss_hypr,'k--')

tin = t<4000;
mean(dedt(tin))
mean(dehdt(tin))
mean(deudt(tin))
mean(debdt(tin))
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
