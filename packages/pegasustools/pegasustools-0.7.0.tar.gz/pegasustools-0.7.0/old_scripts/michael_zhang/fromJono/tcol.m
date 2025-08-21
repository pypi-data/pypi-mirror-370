function col = tcol(t,trng)

% Colormap for time 
if nargin==1
    tmin = 18.1;
    tmax = 35;
else
    tmin = trng(1);
    tmax = trng(2);
end
a=jet(256);


if t>tmax; t=tmax;end
if t<tmin t=tmin;end

col=interp1(1:256,a,1+(t-tmin)/(tmax-tmin)*255);

% Standard matlab colors, for reference
scol = [ 0         0         0
         0    0.4470    0.7410
    0.8500    0.3250    0.0980
    0.9290    0.6940    0.1250
    0.4940    0.1840    0.5560
    0.4660    0.6740    0.1880
    0.3010    0.7450    0.9330
    0.6350    0.0780    0.1840];
end