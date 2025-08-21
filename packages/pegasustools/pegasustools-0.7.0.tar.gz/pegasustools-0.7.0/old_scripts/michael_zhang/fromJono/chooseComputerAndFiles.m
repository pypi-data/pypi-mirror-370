function [readF,files_all,folder,filenamespec,outputfolder,swarm,track,filenamespecav]=chooseComputerAndFiles(name,computer)

% Chooses folders and file names. Change things here or add extras

p_id = 'minor_turb';

switch computer
    case 'maui'
        basefolder = '/projects/KUNZ/mfzhang/simulations/';
        folder = [name '/output/'];
        spec = 'spec/';
    case 'tigress'
%         basefolder = '/tigress/jsquire/pegasus/';
        basefolder = '/projects/KUNZ/mfzhang/simulations/';
        folder = [name '/output/'];
        spec = 'spec/';
    case 'tigressevan'
        basefolder = '/projects/KUNZ/eyerger/';
        folder = [name '/output/mpiio/'];
        spec = 'specav/';
    case 'tigressLev'
        basefolder = '/projects/KUNZ/leva/turb/turb_beta03/combined/';'/tigress/leva/turb_beta03/combined/';
        folder = '';
        p_id = 'turb';
    case 'tests'
        basefolder = ['../../testing/' ];
        folder = [name '/output/'];
    case 'local'
        basefolder = ['../simulations/' ];
        folder = [name '/output/'];
    case 'localLev'
        basefolder = ['../simulations/lev/' ];
        folder = '';
        p_id = 'turb';
end

o_ids = 2:4; % Output id (set in input file)

filename = @(n,oid) [basefolder folder 'grid/' p_id '.out' num2str(oid) '.'  sprintf('%05d',n) '.nbf'];
filenamespec = @(n) [basefolder folder 'spec/' p_id '.' sprintf('%05d',n)  ];
filenamespecav = @(n) [basefolder name '/output/specav/' p_id '.' sprintf('%05d',n)  ];
outputfolder =  [basefolder name '/output/'];
swarm = @(n) ['swarm.' sprintf('%05d',n)];
track = @(n) [p_id '.' sprintf('%05d',n) '.track_mpiio_optimized'];
readF = @(f) readAllNBF(f);
files_all = @(n) {filename(n,o_ids(1)),filename(n,o_ids(2)),filename(n,o_ids(3))};

if strcmp(computer(end-2:end),'Lev')
    % These are vtk files
    filenamemom = @(n) [basefolder p_id '.' sprintf('%04d',n) '.mom.vtk'];
    filenamefld = @(n) [basefolder p_id '.' sprintf('%04d',n) '.fld.vtk'];
    filenamespec = @(n) [basefolder folder '/spec/' p_id '.' sprintf('%05d',n)  ];
    outputfolder =  [basefolder name '/output/'];
    swarm = @(n) ['swarm.' sprintf('%05d',n)];
    readF = @(f) readAllVTK(f);
    files_all = @(n) {filenamefld(n)};%{filenamemom(n),filenamefld(n)};
end

end
