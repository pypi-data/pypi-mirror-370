%%
%  @file example_training_of_GP.m
%
%  @brief Illustrative training script for Gaussian processes in Matlab.
%
% ==============================================================================\n
%   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
% ==============================================================================\n
%
%  @author Artur Schweidtmann, Xiaopeng Lin, Daniel Grothe, and Alexander Mitsos
%  @date 16. January 2020
%%

clc();
clear();
close("all");

addpath(genpath(fullfile(pwd, "functions")));


%% General
nX = 32;                    % Number of training data points
DX = 2;                     % Input dimension of data / GP

lb = [-3, -3];              % Define Lower bound of inputs
ub = [ 3,  3];              % Define upper bound of inputs

test_func = @(x) 3*(1-x(1)).^2.*exp(-(x(1).^2) - (x(2)+1).^2) ... 
   - 10*(x(1)/5 - x(1).^3 - x(2).^5).*exp(-x(1).^2-x(2).^2) ... 
   - 1/3*exp(-(x(1)+1).^2 - x(2).^2) ; % Function for data generation


%% Generate training data

X = lhsdesign(nX,DX);       % Generate inputs using a Latin hypercube
X = lb + (ub-lb) .* X ;     % Scale inputs onto interval [lb, ub]

Y = cellfun(test_func, num2cell(X,2)); % Evaluate test_func for all X


%% Tranining of GPs

Opt.GP(1).matern = 5 ;          % Define covariance function Martern 1, 3, 5, inf
Opt.GP(1).fun_eval = 200;       % internal option for solver

Opt = Train_GP_and_return_hyperparameters(X,Y,lb,ub,Opt) ; % Training of GP


%% Save GP parameters in json file

filename = "testGp.json" ; 
Write_GP_to_json(filename, Opt.GP(1), X, Y, lb, ub);


%% Compute test predictions 

x_Test_Point = [1.5, -2.0] ;
[ prediction, var ] = Predict_GP(x_Test_Point, X, Y, lb, ub, Opt.GP ) ;
