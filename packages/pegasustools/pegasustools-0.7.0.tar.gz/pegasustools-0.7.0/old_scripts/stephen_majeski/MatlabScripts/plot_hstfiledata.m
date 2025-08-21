%plots rms values from hist files vs time

%get box-averaged data from hst file
currfol = "/projects/KUNZ/smajeski/newfullfslowmode_0p4_4by1/output/";
fid = fopen(currfol+"slow.hst");
%fid = fopen("../output/slow.hst");
C = textscan(fid,repmat('%f',[1,32]),'CommentStyle','#');
fclose(fid);
time = C{1}; nsqm1 = C{30}; nm1 = C{31}; dnsq2 = nsqm1-nm1.^2-2*nm1;
dsq = C{32};
deltbet = sqrt(2*dsq)*2;

%plot delta*beta vs time
figure
plot(time,deltbet)
xlabel('time (\Omega_i^{-1})')
ylabel('\Delta \beta')


