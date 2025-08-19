%%
%  @file Predict_GP.m
%
%  @brief Computes the prediction of Gaussian processes
%
% ==============================================================================\n
%   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
% ==============================================================================\n
%
%  @author Artur Schweidtmann, Xiaopeng Lin, Daniel Grothe, and Alexander Mitsos
%  @date 16. January 2020

%%
function [ prediction, std ] = Predict_GP(x_test, X, Y, lb, ub, OptGP )

%% Calculate k(x,x*)
Opt.GP = OptGP ;

[xScaled,yScaled,MeanOfOutputs,stdOfOutputs] = ScaleVariables(X,Y,lb,ub) ;

x_test_scaled = zeros(size(x_test)) ;
for i = 1 : size(x_test,2)
    x_test_scaled(:,i) = (x_test(:,i)-lb(i)) / (ub(i)-lb(i)) ;
end

%% Compute prediction
[n,D]            = size(X) ;
[n_test,D_test]  = size(x_test);
hyp              = Opt.GP.hyp ;
ell              = exp(hyp.cov(1:D));
sf2              = exp(2*hyp.cov(D+1));

if Opt.GP.cov ~= inf
    d           = Opt.GP.matern;    % type of Martern
else
    d           = 1;
end

kxxT = zeros(n,n_test) ; % NoTrainingData points X NoTestData points
k_x_x_T = zeros(n,n_test) ; % NoTrainingData points X NoTestData points

for i = 1 : D_test % for all input dimensions
    for j = 1 : n_test % for all test points
        kxxT(:, j) =  (xScaled(:,i) - x_test_scaled(j,i)).^2 * d/ell(i)^2 ;
    end
    k_x_x_T = k_x_x_T + kxxT ;
end

k_x_x = k_x_x_T';

if Opt.GP.cov ~= inf
    sqrtK = sqrt(k_x_x) ;
    expnK = exp(-sqrtK) ;
else
    expnK = exp(-1/2* (k_x_x) );
    sqrtK = [];
end

if      Opt.GP.cov == 3, t = sqrtK ; m =  (1 + t).*expnK;
elseif  Opt.GP.cov == 1,             m =  expnK;
elseif  Opt.GP.cov == 5, t = sqrtK ; m =  (1 + t.*(1+t/3)).*expnK;
elseif  Opt.GP.cov == inf,           m  = expnK;
end

k_x_x = sf2*m;

mean = 0 ;
invK = Opt.GP.invK ;
prediction_scaled = mean + k_x_x * invK * (yScaled  - mean) ;

prediction = prediction_scaled * stdOfOutputs + MeanOfOutputs;

%% Compute squared-distance matrix
a = x_test_scaled' ;
K_M = zeros(n_test,n_test*D_test) ;
for i = 1:D_test
    K_M(:,(i-1)*n_test+1:i*n_test) = sqdist(a(i,:),a(i,:)) ;
end

%% Compute covariance matrix
K = zeros(n_test,n_test) ;

for i = 1:D_test
    K = K_M(:,(i-1)*n_test+1:i*n_test) * d/ell(i)^2 + K ;
end
if Opt.GP.cov ~= inf
    sqrtK = sqrt(K) ;
    expnK = exp(-sqrtK) ;
else
    expnK = exp(-1/2*K);
    sqrtK = [];
end

if      Opt.GP.cov == 3, t = sqrtK ; m =  (1 + t).*expnK;
elseif  Opt.GP.cov == 1,             m =  expnK;
elseif  Opt.GP.cov == 5, t = sqrtK ; m =  (1 + t.*(1+t/3)).*expnK;
elseif  Opt.GP.cov == inf, m  = expnK;
end
K = sf2*m;
K =  K + eye(n_test)*exp(hyp.lik*2) ;
K = (K+K')/2 ; % This guarantees a symmetric matrix

% the another way to calculate the covariance matrix.
% K = eye(n_test,n_test);
% K_x = Opt.GP.K;
% K = K.*K_x(1,1);

var_scaled = diag(K- k_x_x * invK *k_x_x');
var_scaled = max(var_scaled, 1e-6);
std = sqrt(var_scaled) * stdOfOutputs;
return

function D = sqdist(X1, X2)
% Copyright (c) 2016, Mo Chen
% All rights reserved.
% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are
% met:
%
% * Redistributions of source code must retain the above copyright
% notice, this list of conditions and the following disclaimer.
% * Redistributions in binary form must reproduce the above copyright
% notice, this list of conditions and the following disclaimer in
% the documentation and/or other materials provided with the distribution
%
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
% AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
% IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
% ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
% LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
% CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
% SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
% INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
% CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
% ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
% POSSIBILITY OF SUCH DAMAGE.

% https://se.mathworks.com/matlabcentral/fileexchange/24599-pairwise-distance-matrix
% Pairwise square Euclidean distance between two sample sets
% Input:
%   X1, X2: dxn1 dxn2 sample matrices
% Output:
%   D: n1 x n2 square Euclidean distance matrix
% Written by Mo Chen (sth4nth@gmail.com).

D = bsxfun(@plus,dot(X2,X2,1),dot(X1,X1,1)')-2*(X1'*X2);
D(D<0) = 0 ; % check due to numerical errors
return
