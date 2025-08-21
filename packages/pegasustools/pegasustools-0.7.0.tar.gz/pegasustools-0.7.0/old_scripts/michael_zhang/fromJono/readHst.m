function [t,dat,names] = readHst(name)

% Simple function to read .hst and give data out
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

t = dat(:,1);
is = restart_overlaps(t);

t = t(is);
dat = dat(is,:);



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
