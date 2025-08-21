function [cols,tcol] = setAxesAndColors(fig,sz,colsch)

addpath('~/matlab-libs')
addpath('~/matlab-libs/BrewerMap')
    

set(fig,'Color',[1 1 1]);
set(fig, 'Units', 'centimeters', 'OuterPosition', [5,5, sz(1) sz(2) ]);
if nargin>2
    % Nice ones are Dark2, Accent, and Set1
    axes('ColorOrder',brewermap(8,colsch),'NextPlot','replacechildren')
    box on
end

% Some nice color maps from brewermap
% Spectral, RdYlBu for diverging, 
% PuBuGn BuPu  YlGnBu  non diverging
% Other cool nondiverging; magma, plasma and inferno 

% Standard matlab colors, for reference
if nargin<3
    cols = [ 0         0         0
             0    0.4470    0.7410
        0.8500    0.3250    0.0980
        0.9290    0.6940    0.1250
        0.4940    0.1840    0.5560
        0.4660    0.6740    0.1880
        0.3010    0.7450    0.9330
        0.6350    0.0780    0.1840];
else 
    cols = brewermap(8,colsch);
end


tmp=flipud(plasma(256));
tcol=@(t) interp1(1:256,tmp,1+min(1,t/16)*255);

end
