function saveplot(name, options)
oldpath = path;
path(oldpath,'~/matlab-libs/export-fig')
set(gcf,'color','w')
if nargin>1
    export_fig([ '~/Downloads/' name '.pdf'],options)
else
    export_fig([ '~/Downloads/' name '.pdf'])
end
end