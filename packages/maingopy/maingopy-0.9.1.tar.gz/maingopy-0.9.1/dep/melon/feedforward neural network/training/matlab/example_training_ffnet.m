%%
%  @file example_training_of_GP.m
%
%  @brief Illustrative training script for feedforward artificial neural
%  network in Matlab.
%
% ==============================================================================\n
%   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
% ==============================================================================\n
%
%  @author Artur Schweidtmann and Alexander Mitsos
%  @date 22. January 2020
%%

clc();
clear();
close("all");

%% General
nX = 200;                   % Number of training data points
DX = 2;                     % Input dimension of data / GP

lb = [-3, -3];              % Define Lower bound of inputs
ub = [ 3,  3];              % Define upper bound of inputs

test_func = @(x) 3*(1-x(1)).^2.*exp(-(x(1).^2) - (x(2)+1).^2) ... 
   - 10*(x(1)/5 - x(1).^3 - x(2).^5).*exp(-x(1).^2-x(2).^2) ... 
   - 1/3*exp(-(x(1)+1).^2 - x(2).^2) ;


%% Generate training data

X = lhsdesign(nX,DX);       % Generate inputs using a Latin hypercube
X = lb + (ub-lb) .* X;      % Scale inputs onto interval [lb, ub]

Y = cellfun(test_func, num2cell(X,2)); % Evaluate test_func for all X


%% Tranining of ANNs

numNeurons = [10, 10];
trainFcn = 'trainlm'; % Training function (Levenberg Marquardt)
ffNet = feedforwardnet(numNeurons, trainFcn);
ffNet = configure(ffNet, X', Y');


% Transfer function: set transfer function ('tansig', 'purelin',...)
ffNet.layers{1}.transferFcn = 'tansig';
ffNet.layers{2}.transferFcn = 'tansig';
ffNet.layers{3}.transferFcn = 'purelin'; % Output Layer

ffNet.name = 'testFfnet';

% Devide data set into training, validation, and test
ffNet.divideParam.trainRatio = 70/100;
ffNet.divideParam.valRatio = 15/100;
ffNet.divideParam.testRatio = 15/100;

ffNet.divideFcn = 'divideblock';
ffNet.performParam.normalization = 'standard';

% Training Parameters
ffNet.trainParam.epochs = 50000;
ffNet.trainParam.max_fail = 6;
ffNet.trainParam.min_grad = 1e-07;
ffNet.trainParam.mu_max = 1e10;

[ffNet,tr] = train(ffNet, X',Y');


%% View network

view(ffNet)


%% Save ANN parameters in csv-files

sNetwork2CSV(ffNet) ;


%% Compute test predictions 

x_Test_Point = [1.5; -2.0] ;
prediction = ffNet(x_Test_Point);
perf = perform(ffNet, prediction, Y) ;






















