function [files_all, filenamespec] = copyFromFrontera(name,computer,type, num)
p_id = 'minor_turb';

switch computer
    case 'maui'
        basefolder = '/projects/KUNZ/mfzhang/simulations/';
        folder = [name '/output/'];
    case 'tigress'
        basefolder = '/projects/KUNZ/mfzhang/simulations/';
        folder = [name '/output/mpiio'];
    case 'tests'
        basefolder = ['../../testing/' ];
        folder = [name '/output'];
    case 'local'
        basefolder = ['../simulations/' ];
        folder = [name '/'];
end
ffolder_base = ['/scratch3/09525/mfzhang/b_b0625/' name '/output/'];
ffolder_grid = ['/scratch3/09525/mfzhang/b_b0625/' name '/output/mpiio/grid/'];
ffolder_spec = ['/scratch3/09525/mfzhang/b_b0625/' name '/output/mpiio/spec/'];
%ffolder_base = ['/scratch1/09525/mfzhang/imbatrial_dump600/output/'];
%ffolder_grid = ['/scratch1/09525/mfzhang/imbatrial_dump600/output/mpiio/grid/'];
%ffolder_spec = ['/scratch1/09525/mfzhang/imbatrial_dump600/output/mpiio/spec/'];

localf = [basefolder name '/output/grid'];
localfsp = [basefolder name '/output/tmp-spec'];

oid = 2;
cmd=['rsync -v frontera:' ffolder_base '*.hst ' basefolder name '/'];
disp(cmd);unix(cmd);
switch type
    case 'grid'
        cmd=['mkdir -p ' localf ];
        disp(cmd);unix(cmd);
        cmd=['rsync -v frontera:' ffolder_grid ...
            p_id '.out*' '.' sprintf('%05d',num) '.nbf ' localf]; %num2str(oid)
        disp(cmd);unix(cmd);
    case 'spec'
        cmd=['rm ' localfsp '/*'];
        disp(cmd);unix(cmd);
        cmd=['rsync -v frontera:' ffolder_spec ...
            p_id '.' sprintf('%05d',num) '.* ' localfsp];
        disp(cmd);unix(cmd);
end

filename = @(n,oid) [localf p_id '.out' num2str(oid) '.'  sprintf('%05d',n) '.nbf'];
filenamespec = @(n) [localfsp p_id '.' sprintf('%05d',n)  ];
files_all = @(n) {filename(n,oid)};

end
