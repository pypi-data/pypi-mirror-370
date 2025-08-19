#include "cApi.h"
#include <exception>
#include <iostream>
#include <sstream>
#include <vector>

int
main()
{

    std::stringstream input;
    input << "definitions:\n";
    input << "real x in [-10, 10];\n";
    input << "set{index} kdisc := {};\n";
    input << "real[0] ydisc := ();\n";
    input << "objective:\n";
    input << "x;\n";
    input << "constraints:\n";
    input << "x >= -1;\n";
    input << "forall k in kdisc : x >= ydisc[k];\n";
    double obj_val, cpu, wall, ub, lb;
    std::vector<double> sol = {0.0};
    OptionPair p{};
    std::string file, log, settings;
    file     = "result.txt";
    log      = "log.txt";
    settings = "settings.txt";

    try {
        int a = solve_problem_from_ale_string_with_maingo(input.str().c_str(), &obj_val, sol.data(), 1, &cpu, &wall,
                                                          &ub, &lb, file.c_str(), log.c_str(), settings.c_str(), &p, 0);
    }
    catch (std::exception e) {
        std::cerr << std::endl
                  << "Encountered an unknown fatal error C-API test. Terminating." << std::endl;
        return -1;
    }

    if (obj_val == sol[0] && obj_val<-0.999 & obj_val> - 1.001) {
        std::cout << "Correct solution: -1" << std::endl;
        std::cout << "LB:" << lb << " UB:" << ub << std::endl;
        return 0;
    }
    else {
        std::cout << "Wrong solution. Correct would be: -1" << std::endl;
        std::cout << "LB:" << lb << " UB:" << ub << std::endl;
        return -1;
    }
}