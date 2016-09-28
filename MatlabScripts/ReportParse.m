function [ StrainState ] = ReportParse(foldertitle,windex)
%Function returns a strain state (three principal, three shear) from a
%pointer to the folder with all of the Mentat reports
%   Detailed explanation goes here

%Read each of the reports into a local variable
%Sort each by node number
%Concatonate values as appropriate

index = {'11', '22', '33','12', '23', '31'};

for i = 1:max(size(index));
    path = strcat('+results/+',foldertitle,'/',char(index(i)),'.rpt');
    [node, data] = textread(path,'%f %f','headerlines',9);
    datastore=[node data];
    datastore = sortrows(datastore,1);
    StrainState(:,1) = datastore(:,1);
    StrainState(:,i+1) = datastore(:,2);
end
    path = strcat('+results/+',foldertitle,'/pos.rpt');
    datastore=load(path);
    datastore= sortrows(datastore,1);
    StrainState(:,i+2) = datastore(:,windex+1); %Z positions
    StrainState(:,7) = -StrainState(:,7); %We have our 6th strain variable as 31, but onset uses it as 13
end