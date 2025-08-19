function [Xnew,Ynew, meanOfOutput, stdOfOutput] = ScaleVariables(X,Y,lb,ub)
% Copyright (c) by Eric Bradford, Artur M. Schweidtmann and Alexei Lapkin, 2017-13-12.

%% Scales input and output variabels
Xnew = zeros(size(X)) ; % scaled inputs
Ynew = zeros(size(Y)) ; % scaled outputs
meanOfOutput = zeros(size(Y,2)) ;
stdOfOutput = zeros(size(Y,2)) ;

%% Scale input variables to [0,1]
for i = 1 : size(X,2)
    Xnew(:,i) = (X(:,i)-lb(i)) / (ub(i)-lb(i)) ;
end

%% Scale output variables to zero mean and unit variance
for i = 1 : size(Y,2)
    meanOfOutput(i) = mean(Y(:,i)); % calculate mean
    stdOfOutput(i) = std(Y(:,i)) ; % calculate standard deviation
    Ynew(:,i) = (Y(:,i) - meanOfOutput(i)) / stdOfOutput(i) ; % scale outputs
end
return