foldername = '90degT800NoPlateZdir2mm';
subscript = ['X';'Y';'Z'];
for j = 1:3;
    clear Report MME matrixDil matrixDis
    dest = [foldername,'/Reports',subscript(j)];
    Report = ReportParse(dest,j);
    Rows = size(Report);
    Rows = Rows(1);

    %% Interrogation points
    nMatrixIP = 4;
    nFibreIP = 3;
    nIP = nMatrixIP + nFibreIP;
    nArrays = 2;
    nAngles = 12; 

    matrixDilCrit = 0.025; %Dilatational Critical Invatiant
    deltaT = 140; %check if this is correct!!

    MME = csvread('MME_T800s_3900-2_0.60.csv'); %Storage of the MME values
    MME = reshape(MME,[6,7,nIP,nArrays]);

    for i = 1:Rows;   
        unitStrainTensor = Report(i,2:7); %order 11 22 33 12 23 31
        increment = 1;
        extension(i) = 1;
        matrixDil(i) = 0;
        i
        strain = extension(i)*unitStrainTensor; %we creep up to our strain tensor
        result = sift.dehomogenise(strain,deltaT,MME,nMatrixIP,nFibreIP,nArrays,nAngles);
        matrixDil(i) = result.invariant.matrixDil;
        matrixDis(i) = result.invariant.matrixDis;
        extension(i) = extension(i) + increment;
    end
    figure
    ReportPlot
    
    %Small amount of testing code
    i = find(Report(:,1) == 25267)
    matrixDil(i)
    Report(i,8)
end
