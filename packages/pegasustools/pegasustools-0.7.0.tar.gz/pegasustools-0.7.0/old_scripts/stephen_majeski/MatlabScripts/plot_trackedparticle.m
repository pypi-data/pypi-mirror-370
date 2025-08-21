%script to plot individual particle positions vs time as well as the time evolution of their magnetic moment and parallel energy (useful for scattering studies)

%fodler where tracked particle output resides
run = '/projects/KUNZ/smajeski/fullfslowmode_0p8_8by2/output/';

%which particle you want to get data from (proc, particle #)
num = [8 1600];
fname = [run 'track/slow.' sprintf('%02d',num(1)) '.' sprintf('%05d',num(2)) '.track.dat'];

%read in particle file
fulldata = importdata(fname);

t = fulldata.data(:,1);                        %time array
w1 = fulldata.data(:,4) - fulldata.data(:,13); %specific velocities
w2 = fulldata.data(:,5) - fulldata.data(:,14);
w3 = fulldata.data(:,6) - fulldata.data(:,15);
B1 = fulldata.data(:,7);                       %magnetic fields
B2 = fulldata.data(:,8);
B3 = fulldata.data(:,9);
wsq = w1.*w1+w2.*w2+w3.*w3;
bsq = B1.*B1+B2.*B2+B3.*B3;
bmg = sqrt(bsq);
wpl = (w1.*B1+w2.*B2+w3.*B3)./bmg;             %specific field-parallel velocity
mu  = wsq - wpl.*wpl;
mu  = 0.5*mu./bmg;                             %mu invariant

%smooth data a bit
mu_filter = exp(squeeze(filter(1/16*ones(16,1),1,log(mu))));
wpl_filter = (squeeze(filter(1/16*ones(16,1),1,wpl)));

%position data plot particle track
x = fulldata.data(:,2);
y = fulldata.data(:,3);
plot(x,y,'.')
axis equal

%plot mu and w_prl time series
figure 
subplot(2,1,1);
semilogy(t,mu_filter)
subplot(2,1,2);
plot(t,wpl_filter)
