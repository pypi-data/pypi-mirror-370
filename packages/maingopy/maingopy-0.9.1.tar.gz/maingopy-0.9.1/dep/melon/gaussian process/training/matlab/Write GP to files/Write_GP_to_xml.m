%%
%  @file Write_GP_to_xml.m
%
%  @brief Wrties Gaussian process parameters to a xml file that can be read by our C++ GP model.
%
% ==============================================================================\n
%   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
% ==============================================================================\n
%
%  @author Artur Schweidtmann, Xiaopeng Lin, Daniel Grothe, and Alexander Mitsos
%  @date 16. January 2020

%%
function [path] = Write_GP_to_xml(filename, OptGP, X, Y, lb, ub)
% initialize variables
Opt.GP = OptGP;
sample_lb = min(X);
sample_ub = max(X);
[nX, DX] = size(X);
[nY, DY] = size(Y);

% scale hyperparameters from log
ell = exp(Opt.GP.hyp.cov(1:DX));
sf2 = exp(2*Opt.GP.hyp.cov(DX+1));

% scale data
[xScaled, yScaled, MeanOfOutputs, stdOfOutputs] = ScaleVariables(X, Y, sample_lb, sample_ub);

% create document
docNode = com.mathworks.xml.XMLUtils.createDocument(filename);
% document element
docRootNode = docNode.getDocumentElement();
% hyperparameter
hypElement = docNode.createElement('hyperparameter');
docRootNode.appendChild(hypElement);
sf2Node = docNode.createElement('sf2');
sf2Node.appendChild(docNode.createTextNode(sprintf('%f',sf2)));
hypElement.appendChild(sf2Node);
for i = 1:DX
    str = "ell_"+string(i) ;
    ellNode = docNode.createElement(sprintf('%s',str));
    ellNode.appendChild(docNode.createTextNode(sprintf('%f',ell(i))));
    hypElement.appendChild(ellNode);
end
% config of data
Colement = docNode.createElement('config');
docRootNode.appendChild(Colement);
nXNode = docNode.createElement('nX');
nXNode.appendChild(docNode.createTextNode(sprintf('%f',nX)));
Colement.appendChild(nXNode);
DXNode = docNode.createElement('DX');
DXNode.appendChild(docNode.createTextNode(sprintf('%f',DX)));
Colement.appendChild(DXNode);
nYNode = docNode.createElement('nY');
nYNode.appendChild(docNode.createTextNode(sprintf('%f',nY)));
Colement.appendChild(nYNode);
DYNode = docNode.createElement('DY');
DYNode.appendChild(docNode.createTextNode(sprintf('%f',DY)));
Colement.appendChild(DYNode);
lbColement = docNode.createElement('lb');
Colement.appendChild(lbColement);
for i = 1:DX
    str = "lb_"+string(i);
    lbNode = docNode.createElement(sprintf('%s', str));
    lbNode.appendChild(docNode.createTextNode(sprintf('%f', lb(i))));
    lbColement.appendChild(lbNode);
end
ubColement = docNode.createElement('ub');
Colement.appendChild(ubColement);
for i = 1:DX
    str = "ub_"+string(i);
    ubNode = docNode.createElement(sprintf('%s', str));
    ubNode.appendChild(docNode.createTextNode(sprintf('%f', ub(i))));
    ubColement.appendChild(ubNode);
end
meanfunctionNode = docNode.createElement('meanfunction');
meanfunctionNode.appendChild(docNode.createTextNode(sprintf('%f',0)));
Colement.appendChild(meanfunctionNode);
for i = 1:DY
    str = "MeanOfOutputs_"+string(i) ;
    MeanNode = docNode.createElement(sprintf('%s',str));
    MeanNode.appendChild(docNode.createTextNode(sprintf('%f',MeanOfOutputs(i))));
    Colement.appendChild(MeanNode);
end
for i= 1:DY
    str = "stdOfOutputs_"+string(i) ;
    stdNode = docNode.createElement(sprintf('%s',str));
    stdNode.appendChild(docNode.createTextNode(sprintf('%f',stdOfOutputs(i))));
    Colement.appendChild(stdNode);
end
% matern
maternNode = docNode.createElement('matern');
maternNode.appendChild(docNode.createTextNode(sprintf('%f',Opt.GP.matern)));
Colement.appendChild(maternNode);
% Bounds
lBolement = docNode.createElement('l_bounds');
docRootNode.appendChild(lBolement);
for i= 1:DX
    str = "lb_"+string(i) ;
    lbNode = docNode.createElement(sprintf('%s',str));
    lbNode.appendChild(docNode.createTextNode(sprintf('%f',sample_lb(i))));
    lBolement.appendChild(lbNode);
end
uBolement = docNode.createElement('u_bounds');
docRootNode.appendChild(uBolement);
for i= 1:DX
    str = "ub_"+string(i) ;
    ubNode = docNode.createElement(sprintf('%s',str));
    ubNode.appendChild(docNode.createTextNode(sprintf('%f',sample_ub(i))));
    uBolement.appendChild(ubNode);
end
% data input
XSElement = docNode.createElement('XS_data');
docRootNode.appendChild(XSElement);
YSElement = docNode.createElement('YS_data');
docRootNode.appendChild(YSElement);
% scaled X data
for i = 1:nX
    rowOfX = "row_"+string(i);
    rowOfXNode = docNode.createElement(sprintf('%s',rowOfX));
    XSElement.appendChild(rowOfXNode);
    for j = 1 : DX
        str = "Demension_"+ string(j);
        XSNode = docNode.createElement(sprintf('%s',str));
        XSNode.appendChild(docNode.createTextNode(sprintf('%f',xScaled(i,j))));
        rowOfXNode.appendChild(XSNode);
    end
end
% scaled Y data
for i = 1:nY
    rowOfY = "row_"+string(i);
    rowOfYNode = docNode.createElement(sprintf('%s',rowOfY));
    YSElement.appendChild(rowOfYNode);
    for j = 1 : DY
        str = "Demension_"+ string(j);
        YSNode = docNode.createElement(sprintf('%s',str));
        YSNode.appendChild(docNode.createTextNode(sprintf('%f',yScaled(i,j))));
        rowOfYNode.appendChild(YSNode);
    end
end
% covariance matrix
KElement = docNode.createElement('covariance_matrix_K');
docRootNode.appendChild(KElement);
for i = 1 :nX
    rowOfK = "row_"+string(i);
    rowOfKNode = docNode.createElement(sprintf('%s',rowOfK));
    KElement.appendChild(rowOfKNode);
    for j = 1:nX
        str = "Demension_"+ string(j);
        KNode = docNode.createElement(sprintf('%s',str));
        KNode.appendChild(docNode.createTextNode(sprintf('%f',Opt.GP.K(i,j))));
        rowOfKNode.appendChild(KNode);
    end
end
% inverse of the covariance matrix
inKElement = docNode.createElement('inK');
docRootNode.appendChild(inKElement);
for i = 1 :nX
    rowOfinK = "row_"+string(i);
    rowOfinKNode = docNode.createElement(sprintf('%s',rowOfinK));
    inKElement.appendChild(rowOfinKNode);
    for j = 1:nX
        str = "Demension_"+ string(j);
        inKNode = docNode.createElement(sprintf('%s',str));
        inKNode.appendChild(docNode.createTextNode(sprintf('%f',Opt.GP.invK(i,j))));
        rowOfinKNode.appendChild(inKNode);
    end
end
% xmlwrite
xmlFileName = [filename,'.xml'];
xmlwrite(xmlFileName,docNode);

path = fullfile(pwd, filename);
end