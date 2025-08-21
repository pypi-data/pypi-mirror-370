function convertNBFtoVTK

% 2D spectrum of B and E
name = 'imbal2-prod';'forcetest-prod';

P.derefine_prl =4; P.derefine_prp=4;
computer = 'tigress';
nums = [140:181]; % snapshot numbers for which to find spectrum

n2s = @(s) num2str(s);
[readF,files_all,folder,~,outputfolder] = chooseComputerAndFiles(name,computer);
savefolder = @(n) [ outputfolder '/paraview-vtks/particles.eprp.'  sprintf('%05d',n) '.vtk'];
% readfolder = @(n) [ outputfolder '../vtks/particles.lr.'  sprintf('%05d',n) '.vtk'];
% savefolder = @(n) [ outputfolder '../vtks/particles.llr.'  sprintf('%05d',n) '.vtk'];

disp(['Saving to ' savefolder(0)])

for nnn=nums

    D = readF(files_all(nnn));
%     D = readVTK(readfolder(nnn));
    D = reduceResolution(D,P.derefine_prl,P.derefine_prp);
    D.dx = D.x(2)-D.x(1);
    D.dy = D.y(2)-D.y(1);
    D.dz = D.z(2)-D.z(1);
    D.nx = length(D.x);
    D.ny = length(D.y);
    D.nz = length(D.z);
    
    % Delete some of them
    disp('');disp(['Writing nnn=' num2str(nnn)]);disp('');
    D.Eprp = sqrt(D.Ecc2.^2 + D.Ecc3.^2);
    D = rmfield(D,{'dens','vel1','vel2','vel3','Bcc1','Ecc1',...
        'Bcc2','Bcc3','Ecc2','Ecc3'});
    
    writeVTK(D,savefolder(nnn))
end