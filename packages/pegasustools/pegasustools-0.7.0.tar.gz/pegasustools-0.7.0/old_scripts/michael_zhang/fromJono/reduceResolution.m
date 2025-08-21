function D=reduceResolution(D,prl,prp)
if prl~=1 || prp~=1
    % reduce resolution by a factor 
    if round(length(D.x)/prl/2)~=length(D.x)/prl/2 || round(length(D.y)/prp/2)~=length(D.y)/prp/2
        error('Reduced grid size must be an even integer')
    end

    D.nx = D.nx/prl;D.ny = D.ny/prp;D.nz = D.nz/prp;
    D.dx = D.dx*prl; D.dy = D.dy*prp; D.dz = D.dz*prp;
    D.x = D.x(1:prl:end);
    D.y = D.y(1:prp:end);
    D.z = D.z(1:prp:end);
    fields = fieldnames(D);
    for kk = 1:length(fields)
        if length(size(D.(fields{kk}) ))==3
            D.(fields{kk}) = D.(fields{kk})(1:prl:end,1:prp:end,1:prp:end);
        end
    end
end

end

