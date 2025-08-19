##
#  @file itils.py
#
#  @brief Utils for training of artificial neural network in Keras and export to file that is readable by MeLOn.
#
# ==============================================================================\n
#   Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
# ==============================================================================\n
#
#  @author Artur M. Schweidtmann, Friedrich von Bülow, Jing Cui, Laurens Lueg, and Alexander Mitsos
#  @date 20. January 2020
##

from pathlib import Path
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import xml.etree.cElementTree as ElemTree


def save_model_to_xml(
    filepath: Path, stripped_model: tf.keras.Sequential, X: np.array, y: np.array,
    scalers: dict[str, MinMaxScaler | StandardScaler], scale_input: bool = True, scale_output: bool = True,
    precision_to_xml: int = 30
    ):
    
    input_lower_bound = scalers['input'].data_min_
    input_upper_bound = scalers['input'].data_max_
    output_lower_bound = np.amin(y, axis=0)
    output_upper_bound = np.amax(y, axis=0)
    y_mean = scalers['output'].mean_
    y_std = scalers['output'].scale_

    ffnet = ElemTree.Element("FFNET")
    description = ElemTree.SubElement(ffnet, "Description")
    values = ElemTree.SubElement(ffnet, "Values")
    inputIsScaled = ElemTree.SubElement(values, "inputIsScaled")
    outputIsNormalized = ElemTree.SubElement(values, "outputIsNormalized")
    std_of_output = ElemTree.SubElement(values, "Stdofoutput")
    mean_of_output = ElemTree.SubElement(values, "Meanofoutput")
    architecture = ElemTree.SubElement(values, "Architecture")
    bounds = ElemTree.SubElement(values, "Bounds")
    layers = ElemTree.SubElement(values, "Layers")
    
    precision_to_xml_str = "{0:." + str(precision_to_xml) + "f}"

    # Description
    ElemTree.SubElement(description, "Description", name="Description").text = str("Optional Description")

    # Information about data preprocessing
    ElemTree.SubElement(inputIsScaled, "inputIsScaled", name="inputIsScaled").text = str(int(scale_input))
    ElemTree.SubElement(outputIsNormalized, "outputIsNormalized", name="outputIsNormalized").text = str(int(scale_output))
    
    # Standard deviation and mean of outputs
    ElemTree.SubElement(std_of_output, "outputStd", name="outputStd").text = str(float(y_std))
    ElemTree.SubElement(mean_of_output, "outputMean", name="outputMean").text = str(float(y_mean))

    # Number of layers, inputs and outputs
    ElemTree.SubElement(architecture, "NumberOfLayers", name="NumberOfLayers").text = str(len(stripped_model.layers))
    ElemTree.SubElement(architecture, "NumberOfInputs", name="NumberOfInputs").text = str(stripped_model.input_shape[1])
    ElemTree.SubElement(architecture, "NumberOfOutputs", name="NumberOfOutputs").text = str(stripped_model.output_shape[1])

    # Iterate over Bounds (Arrays)
    
    input_lb = ElemTree.SubElement(bounds, "InputLowerBound")
    if isinstance(input_lower_bound, np.ndarray):
        for boundIndex, bound in enumerate(input_lower_bound):
            ElemTree.SubElement(input_lb, "Bounds", name="inputLB_" + str(boundIndex)).text = str(bound)
    else:
        ElemTree.SubElement(input_lb, "Bounds", name="inputLB_").text = str(input_lower_bound.values[0])
        
    input_ub = ElemTree.SubElement(bounds, "InputUpperBound")
    if isinstance(input_upper_bound, np.ndarray):
        for boundIndex, bound in enumerate(input_upper_bound):
            ElemTree.SubElement(input_ub, "Bounds", name="inputUB_" + str(boundIndex)).text = str(bound)
    else:
        ElemTree.SubElement(input_ub, "Bounds", name="inputUB_").text = str(input_upper_bound.values[0])
        
    output_lb = ElemTree.SubElement(bounds, "OutputLowerBound")
    if isinstance(output_lower_bound, np.ndarray):
        for boundIndex, bound in enumerate(output_lower_bound):
            ElemTree.SubElement(output_lb, "Bounds", name="outputLB_" + str(boundIndex)).text = str(bound)
    else:
        ElemTree.SubElement(output_lb, "Bounds", name="outputLB").text = str(output_lower_bound.values[0])
        
    output_ub = ElemTree.SubElement(bounds, "OutputUpperBound")
    if isinstance(output_upper_bound, np.ndarray):
        for boundIndex, bound in enumerate(output_upper_bound):
            ElemTree.SubElement(output_ub, "Bounds", name="outputUB_" + str(boundIndex)).text = str(bound)
    else:
        ElemTree.SubElement(output_ub, "Bounds", name="outputUB_").text = str(output_upper_bound.values[0])

    n_neurons = list()
    for layer_index, modelLayer in enumerate(stripped_model.layers):
        
        layer = ElemTree.SubElement(layers, "Layer_" + str(layer_index))
        
        # Write Activation Function
        ElemTree.SubElement(
            layer, "ActivationFunction",
            name="ActivationFunction_" + str(layer_index)).text = \
                str(modelLayer.activation.__name__)
                            
        # Write Biases
        bias = ElemTree.SubElement(layer, "Bias")
        for index2, singleBias in enumerate(modelLayer.get_weights()[1]):
            ElemTree.SubElement(
                bias, "Bias",
                name="Bias_" + str(layer_index) + "_" + str(index2)).text = \
                    precision_to_xml_str.format(singleBias)
            
        # Write weights
        weights = ElemTree.SubElement(layer, "Weights")
        for index3, vectorWeights in enumerate(modelLayer.get_weights()[0]):
            for index4, singleWeight in enumerate(vectorWeights):
                ElemTree.SubElement(
                    weights, "Weight",
                    name="Weight_" + str(layer_index) + "_" + str(index3) + "_" + str(index4)).text = \
                        precision_to_xml_str.format(singleWeight)
                        
        if layer_index < len(stripped_model.layers) - 1:
                    n_neurons.append(len(modelLayer.get_weights()[1]))

    layer_sizes = ElemTree.SubElement(architecture, "LayerSizes")
    for n in n_neurons:
        ElemTree.SubElement(layer_sizes, "LayerSize", name="LayerSize").text = str(n)

    tree = ElemTree.ElementTree(ffnet)

    tree.write(filepath)
