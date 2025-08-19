/**********************************************************************************
* Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* SPDX-License-Identifier: EPL-2.0
*
* @file AnnParser.h
*
* @brief File containing declaration of the ann parser classes.
*
**********************************************************************************/

#pragma once

#include <string>		// std::string
#include <vector>		// std::vector
#include <memory>		// std::shared_ptr, std::unique_ptr

#include "tinyxml2.h"
#include "AnnProperties.h"
#include "modelParser.h"

namespace melon {

    /**
    * @class AnnParser
    * @brief This class implements an abstract parent class for ANN file parser.
    *
    * This abstarct class is used to define a general interface for ANN fileparsers. Child classes can implement the defined interface functions according to their filetype.
    */
    class AnnParser: public ModelParser {

    protected:
        /**
        *  @brief Turns a string containing the name of an activation function in the correct enum representation
        *
        *  @param[in] activationFunctionName is a string containing the name of an activation function
        *
        *  @return returns the enum representation of the input
        */
        ACTIVATION_FUNCTION _string_to_activation_function(const std::string& activationFunctionName);
    public:

        /**
        *  @brief Abstract function for defining the structure of the parsing function which is used to get the ANN data from a file
        *
        *  @param[in] modelPath Path to the location of the ANN file
        *
        *  @param[in] modelName name of the network (either foldername in which csv files are stored or name of an xml file, depending on the filetype)
        *
        *  @return returns ModelData struct containing the information defining the ANN
        */
        virtual std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName) = 0;
    };

    /**
    * @class AnnParserCsv
    * @brief This class implements an specialization of the AnnParser for csv files.
    *
    * This abstarct class is used to implement an ANN file parser for csv files based on the interface provided by AnnParser.
    */
    class AnnParserCsv : public AnnParser {

        const int LAYER_INDICATOR_BASE = 900;

        /**
        *  @brief Parses the content of an csv file into a string matrix
        *
        *  @param[in] fileName name of the the csv file that should be parsed
        *
        *  @returns returns a 2d vector(string) containing the data from the csv file
        */
        std::vector<std::vector<std::string>> _csv_to_string_matrix(std::string fileName);

        /**
        *  @brief Parses the content of an csv file into a double matrix
        *
        *  @param[in] fileName name of the the csv file that should be parsed
        *
        *  @returns returns a 2d vector(double) containing the data from the csv file
        */
        std::vector<std::vector<double>> _csv_to_double_matrix(std::string fileName);

        /**
        *  @brief Parses the configuration csv file
        *
        *  @param[out] structure struct containing the information regarding the anns structure
        */
        void _parse_config_file(AnnStructure& structure);

        /**
        *  @brief Parses the input and output scalers
        *
        *  @param[out] inputScalerData struct containing the parameters used for input sclaing
		*
		*  @param[out] outputScalerData struct containing the parameters used for output scaling
        *
        *  @param[in] structure struct containing the information regarding the anns structure
        */
        void _parse_scalers(std::shared_ptr<ScalerData> inputScalerData, std::shared_ptr<ScalerData> outputScalerData, const AnnStructure& structure);

        /**
        *  @brief Parses the bias weights
        *
        *  @param[in] structure struct containing the information regarding the anns structure
        *
        *  @param[out] weights struct containing the anns weights
        */
        void _parse_bias_weights(const AnnStructure& structure, AnnWeights& weights);

        /**
        *  @brief Parses the layer weights
        *
        *  @param[in] structure struct containing the information regarding the anns structure
        *
        *  @param[out] weights struct containing the anns weights
        */
        void _parse_layer_weights(const AnnStructure& structure, AnnWeights& weights);

        /**
        *  @brief Parses the input weights
        *
        *  @param[in] structure struct containing the information regarding the anns structure
        *
        *  @param[out] weights struct containing the anns weights
        */
        void _parse_input_weights(const AnnStructure& structure, AnnWeights& weights);


        /**
        *  @brief Checks if passed number is a layer indicator
        *
        *  @param[in] number Number to be checked
        *
        *  @returns true if number is an layer indicator, otherwise false is returned
        */
        bool _check_if_layer_indicator(int number);


        /**
        *  @brief Extracts layer index from a layer indicator
        *
        *  @param[in] indicator Indicator from which the layer index should get
        *
        *  @returns Layer index
        */
        int _get_layer_index_from_indicator(int indicator);
    public:
        /**
        *  @brief Parsing function which is used to get the ANN data from a csv file
        *
        *  @param[in] modelPath Path to the location of the ANN file
        *
        *  @param[in] modelName name of the network (either foldername in which csv files are stored)
        *
        *  @return returns modelData struct containing the information defining the ann
        */
		std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName);
    };

    /**
    * @class AnnParserXml
    * @brief This class implements an specialization of the AnnParser for xml files.
    *
    * This abstarct class is used to implement an ANN file parser for xml files based on the interface provided by AnnParser.
    */
    class AnnParserXml : public AnnParser {
        /**
        *  @brief Parses child elements of an xml element into an vector of int
        *
        *  @param[in] parentElement pointer to xml element whose child should get parsed
        *
        *  @param[in] vectorName name of the child elements in the xml file
        *
        *  @param[out] vector vector containing the parsed values
        *
        *  @returns tinyxml2 error code indicating wether parsing was succesfull
        */
        tinyxml2::XMLError _parse_vector_int(tinyxml2::XMLElement *parentElement, const std::string vectorName, std::vector<int>& vector);

        /**
        *  @brief Parses child elements of an xml element into an vector of double
        *
        *  @param[in] parentElement pointer to xml element whose child should get parsed
        *
        *  @param[in] vectorName name of the child elements in the xml file
        *
        *  @param[out] vector vector containing the parsed values
        *
        *  @returns tinyxml2 error code indicating wether parsing was succesfull
        */
        tinyxml2::XMLError _parse_vector_double(tinyxml2::XMLElement *parentElement, const std::string vectorName, std::vector<double>& vector);
    public:

        /**
        *  @brief Parsing function which is used to get the ANN data from a xml file
        *
        *  @param[in] modelPath Path to the location of the ANN file
        *
        *  @param[in] modelName name of the network (name of the xml file)
        *
        *  @return returns modelData struct containing the information defining the ann
        */
		std::shared_ptr<ModelData> parse_model(const std::string modelPath, const std::string modelName);
    };


    /**
    * @class AnnParserFactory
    * @brief This class is a factory class for creating child instances of AnnParser.
    */
    class AnnParserFactory: public ModelParserFactory {
    public:

        /**
        *  @brief Factory function for creating a instance of an ann parser corresponding to the specified file type
        *
        *  @brief fileType type of the file in which ann is stored
        *
        *  @returns Pointer to an instance of a child class of AnnParser
        */
        std::unique_ptr<ModelParser> create_model_parser(const MODEL_FILE_TYPE fileType) override;
    };

}