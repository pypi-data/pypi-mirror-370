function D=sumBlock(D,prl,prpy,prpz)
if prl~=1 || prpy~=1 || prpz~=1
    % reduce resolution by a factor 
    if round(length(D.x)/prl/2)~=length(D.x)/prl/2 || round(length(D.y)/prpy/2)~=length(D.y)/prpy/2 || round(length(D.z)/prpz/2)~=length(D.z)/prpz/2
        error('Reduced grid size must be an even integer')
    end
    % The factors by which to reduce the size
    D.nx = D.nx/prl;D.ny = D.ny/prpy;D.nz = D.nz/prpz;
    D.dx = D.dx*prl; D.dy = D.dy*prpy; D.dz = D.dz*prpz;
    D.x = D.x(1:prl:end);
    D.y = D.y(1:prpy:end);
    D.z = D.z(1:prpz:end);
    fields = fieldnames(D);
    % Get the subscripts for each element of the input array
    %[subsAi, subsAj, subsAk] = ndgrid(1:size(D.x,1), 1:size(D.y,2), 1:size(D.z,3));
    % Compute the corresponding output subscripts
    %subsBi = 1 + floor((subsAi-1)/prl);
    %subsBj = 1 + floor((subsAj-1)/prpy);
    %subsBk = 1 + floor((subsAk-1)/prpz);
    %disp(size(subsBj))
    %disp(size(subsBk))
    for kk = 1:length(fields)
        if length(size(D.(fields{kk}) ))==3
            %D.(fields{kk}) = D.(fields{kk})(1:prl:end,1:prp:end,1:prp:end);
            %disp(abs(sum(D.(fields{kk})(:)) - sum(accumarray([subsBi(:) subsBj(:) subsBk(:)], D.(fields{kk})(:)))));
            %Y = reshape(D.(fields{kk}), prl, D.nx, prpy, D.ny, prpz, D.nz);
            D.(fields{kk}) = squeeze(sum(reshape(D.(fields{kk}), prl, D.nx, prpy, D.ny, prpz, D.nz), [1,3,5])) / (prl*prpy*prpz);
            %D.(fields{kk}) = accumarray([subsBi(:) subsBj(:) subsBk(:)], D.(fields{kk})(:)); 
            
        end
    end


end

end