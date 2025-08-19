%%
%  @file Write_GP_to_json.m
%
%  @brief Wrties Gaussian process parameters to a json file that can be read by our C++ GP model.
%
% ==============================================================================\n
%   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
% ==============================================================================\n
%
%  @author Artur Schweidtmann, Xiaopeng Lin, Daniel Grothe, and Alexander Mitsos
%  @date 16. January 2020

%%

function [path] = Write_GP_to_json(filename, OptGP, X, Y, lb, ub)
    % initialize variables
    Opt.GP = OptGP;
    sample_lb = min(X) ;        % Compute lower bound of input data
    sample_ub = max(X) ;        % Compute upper bound of input data

    [nX, DX] = size(X);
    [nY, DY] = size(Y);

    % scale data
    [xScaled, yScaled, meanOfOutput, stdOfOutput] = ScaleVariables(X, Y, lb, ub);
    
    % scale hyperparameters from log
    ell = exp(Opt.GP.hyp.cov(1:DX));
    sf2 = exp(2*Opt.GP.hyp.cov(DX+1));

    % fill rest of the struct
    data.nX = nX;
    data.nY = nY;
    data.DX = DX;
    data.DY = DY;
    data.matern = Opt.GP.matern;
    data.meanfunction = 0;
    data.meanOfOutput = meanOfOutput;
    data.stdOfOutput = stdOfOutput;
    data.sf2 = sf2;
    if DX == 1  % fix for json generation of 1x1 array
        data.ell = {ell};
        data.inputLowerBound = {sample_lb};
        data.inputUpperBound = {sample_ub};
        data.problemLowerBound = {lb};
    	data.problemUpperBound = {ub};
        % fix for 1D column vector
        data.X = {'X_dummy'};
        json_X = sprintf('[%f],',xScaled);
        json_X(end) = [];
    else
        data.ell = ell;
        data.inputLowerBound = sample_lb;
        data.inputUpperBound = sample_ub;
        data.problemLowerBound = lb;
        data.problemUpperBound = ub;
        data.X = xScaled;
    end
    data.Y = yScaled;
    data.K = Opt.GP.K;
    data.invK = Opt.GP.invK;
    
    json = jsonencode(data);
    if DX == 1
        json = strrep(json, '"X_dummy"', json_X);
    end
    
    path = fullfile(pwd, filename);
    fid = fopen(path, 'w');
    fwrite(fid, json);
    fclose(fid);
    
end