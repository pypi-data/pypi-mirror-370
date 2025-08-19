%%
%  @file example_training_of_GP.m
%
%  @brief Wrties feedforward artificial neural network parameters to csv-files that can be read by our C++ ANN model.
%
% ==============================================================================\n
%   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
% ==============================================================================\n
%
%  @author Artur Schweidtmann and Alexander Mitsos
%  @date 22. January 2020
%%

function sNetwork2CSV(net)

precisionNumber = 20 ;

if ~isa(net, 'network')
    error('Input must be a network')
end

finalDir = fullfile(pwd, net.name);


if(~exist(finalDir,'dir'))
    mkdir(finalDir); 
end

inputLowerBound = net.input.range(:,1)' ;
inputUpperBound = net.input.range(:,2)' ;

outputLowerBound = net.output.range(:,1);
outputUpperBound = net.output.range(:,2);

configFileName = strcat(finalDir,'/' , net.name, '_config.csv');
boundsFileName = strcat(finalDir,'/' , net.name, '_bounds.csv');
bWFileName = strcat(finalDir,'/' , net.name, '_BW.csv');
iWFileName = strcat(finalDir,'/' , net.name, '_IW.csv');
lWFileName = strcat(finalDir,'/' , net.name, '_LW.csv');

configFile = fopen(configFileName, 'w');


fprintf(configFile, strcat( int2str(net.numLayers),'\n'));


for i=1:net.numLayers
    for j=1:net.numInputs % currently only 1 input implemented1
        fprintf(configFile, strcat(int2str(net.inputConnect(i,j)),','));
    end
end

fprintf(configFile,'\n');

for i=1:net.numLayers
    fprintf(configFile, strcat(int2str(net.biasConnect(i)),','));
end

fprintf(configFile,'\n');

for i=1:net.numLayers
    for j=1:net.numLayers
        fprintf(configFile, strcat(int2str(net.layerConnect(i,j)),','));
    end
end


fprintf(configFile,'\n');

for i=1:net.numInputs % currently only 1 input implemented
    fprintf(configFile, strcat(int2str(net.inputs{i}.size),','));
end

fprintf(configFile,'\n');

for i=1:net.numLayers
    fprintf(configFile, strcat(int2str(net.layers{i}.size),','));
end

fprintf(configFile, '\n');

for i=1:net.numLayers
    fprintf(configFile, strcat( net.layers{i}.transferFcn , ','));
end


fclose(configFile);



% inputLowerBound
dlmwrite(boundsFileName, inputLowerBound, 'delimiter', ',','precision',precisionNumber);


% inputUpperBound
dlmwrite(boundsFileName, inputUpperBound ,'-append', 'delimiter', ',','precision',precisionNumber);


% outputLowerBound
dlmwrite(boundsFileName, outputLowerBound,'-append', 'delimiter', ',','precision',precisionNumber);


% outputUpperBound
dlmwrite(boundsFileName, outputUpperBound ,'-append', 'delimiter', ',','precision',precisionNumber);


% biasWeight
dlmwrite(bWFileName,[], 'delimiter', ',','precision',precisionNumber);

for i=1:net.numLayers
    dlmwrite(bWFileName, 900+i,'-append', 'delimiter', ',','precision',precisionNumber)
    dlmwrite(bWFileName, net.b{i}','-append', 'delimiter', ',','precision',precisionNumber);
end


% inputWeight
dlmwrite(iWFileName,[], 'delimiter', ',','precision',precisionNumber);

for i=1:net.numLayers 
    for j=1:net.numInputs %currently only 1 input implemented
        dlmwrite(iWFileName, [900+i,900+j],'-append', 'delimiter', ',','precision',precisionNumber);
        dlmwrite(iWFileName, net.IW{i,j},'-append', 'delimiter', ',','precision',precisionNumber);           
    end
end


% layerWeight
dlmwrite(lWFileName,[], 'delimiter', ',','precision',precisionNumber);
for i=1:net.numLayers
    for j=1:net.numLayers
        dlmwrite(lWFileName, [900+i,900+j],'-append', 'delimiter', ',','precision',precisionNumber);
        dlmwrite(lWFileName, net.LW{i,j},'-append', 'delimiter', ',','precision',precisionNumber);
    end
end

end
