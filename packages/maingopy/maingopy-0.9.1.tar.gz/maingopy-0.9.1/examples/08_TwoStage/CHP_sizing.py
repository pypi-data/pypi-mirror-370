import os
import sys

import numpy as np

import maingopy

FEASIBLE_POINT = maingopy.FEASIBLE_POINT
GLOBALLY_OPTIMAL = maingopy.GLOBALLY_OPTIMAL
LANG_ALE = maingopy.LANG_ALE
LANG_GAMS = maingopy.LANG_GAMS
LANG_NONE = maingopy.LANG_NONE


def read_options(filename):
    import re
    settings_pattern = re.compile(r"\s*(\w+)\s*(\S+)\s*(?:#\.*)?")
    comment_pattern = re.compile(r"\s*#\.*")
    options = {}
    with open(filename, 'r') as settings_file:
        for line in settings_file:
            match = re.match(settings_pattern, line)
            if match:
                setting, val = match.groups()
                try:
                    options[setting] = float(val)
                except ValueError:
                    raise ValueError(f"Couldn't parse value '{val}' "
                                     f"for option '{setting}' as float!")
                continue
            if not line.strip() or re.match(comment_pattern, line):
                continue
            raise ValueError(f"Incorrect line\n'{line.strip()}'\n"
                             "in settings file '{filename}': "
                             "Lines need to be empty, contain "
                             "a comment, starting with '#', "
                             "or be of the form '<setting> <value> "
                             "#<comment>'!")
    return options


DEFAULT_SETTINGS_FILE_NAME = "MAiNGOSettings.txt"


# heat and electricity demands
DEFAULT_DATA = [
    [1.1,  0.5],
    [1.1,  2.5],
    [1.1,  4],
    [1.2,  0.5],
    [1.2,  4],
    [1.3,  0.5],
    [1.3,  2.5],
    [1.3,  4],
]


def vertex_form(x, a, b, c):
    """Compute the vertex form of a * x**2 + b * x + c."""
    return c - b ** 2 / (4 * a) + a * (x + b / (2 * a)) ** 2


class CHP_sizing_problem(maingopy.TwoStageModel):
    """Initialize a MAiNGO Model for the CHP sizing Problem.

    Arguments
    ---------
    Nx : number of first-stage variables
    Ny : number of second-stage variables
    w : list of float
      weights for the Ns scenarios
    data : list of list of float
      values for the scenario-dependent parameters, the first
      dimension specifies the scenario, the second the parameter
    """

    def __init__(self, data=DEFAULT_DATA, use_heater=False, reduced_space=False, sample=False):
        CHP_data_file = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "CHP_data.txt")
        if os.path.exists(CHP_data_file):
            print("Found CHP_data.txt file, using values:\n")
            CHP_data = read_options(CHP_data_file)
        else:
            print("No CHP_data.txt file found, using default values:\n")
            CHP_data = dict(
                # Numerical data for CHP sizing problem
                Qdot_nom_ref=1,  # [MW], reference nominal power
                c_ref=1.3e6,  # [€], reference cost
                M=0.9,  # [-], cost exponent
                c_m=0.05,  # [-], maintenance cost relative to investment
                Qdot_rel_min=0.5,  # [-] minimum output part load
                Qdot_nom_min=0.5,  # [MW]
                Qdot_nom_max=2.3,  # [MW]
                n=30,  # lifetime in years
                i=0.05,  # annualization interst rate
                T_OP=6000,  # [h] annual operating time
                p_gas=80,  # [€ / MWh]
                p_el_buy=250,  # [€ / MWh]
                p_el_sell=100,  # [€ / MWh]
            )

        for quantity, value in CHP_data.items():
            print(quantity, '=', value)
            setattr(CHP_sizing_problem, quantity, value)

        self.Qdot_eps = 0.001 * self.Qdot_nom_max  # [MW]
        self.Qdot_mean = (self.Qdot_nom_min + self.Qdot_nom_max) / 2  # [MW]
        self.af = (((1 + self.i) ** self.n) * self.i) / \
            (((1 + self.i) ** self.n) - 1)  # annuity factor
        self.use_heater = use_heater
        self.reduced_space = reduced_space
        self.sample = sample

        # Sanity checks
        Qdot_dem = np.array(data)[:, 0]

        # Demands larger than the maximum nominal power are not feasible
        excess_demands = np.where(Qdot_dem > self.Qdot_nom_max)[0]
        for s in excess_demands:
            print(f"Warning: Heat demand for scenario {s}, {Qdot_dem[s]} MW "
                  f"is larger than maximum nominal power {self.Qdot_nom_max} "
                  f"MW! Correcting to {self.Qdot_nom_max} MW.")
            data[s][0] = self.Qdot_nom_max

        if not use_heater:
            # ensure the ratio of all nonzero heat demands over
            # the maximum heat demand is larger than Qdot_rel_min
            nonzero_demands = np.nonzero(Qdot_dem)[0]
            ratios = Qdot_dem[nonzero_demands] / np.max(Qdot_dem)
            violated_ratios = ratios < self.Qdot_rel_min
            min_partload_violations = \
                nonzero_demands[np.where(violated_ratios)[0]]
            for s in min_partload_violations:
                print(f"Warning: Heat demand for scenario {s}, {Qdot_dem[s]} "
                      "MW cannot be reached with a part load of "
                      f"{self.Qdot_rel_min}! Correcting to 0 MW.")
                data[s][0] = 0

        if reduced_space:
            Ny = 1
        else:
            Ny = 3
        maingopy.TwoStageModel.__init__(
            self, 1, Ny, data)

    def eff_th_nom(self, Qdot_nom):
        """Compute the nominal thermal efficiency of the CHP."""
        return 0.498 - 3.55e-2 * Qdot_nom

    def eff_el_nom(self, Qdot_nom):
        """Compute the nominal electrical efficiency of the CHP."""
        return 0.372 + 3.55e-2 * Qdot_nom

    def eff_th_rel(self, Qdot_rel):
        """Compute the relative electrical efficiency of the CHP."""
        return vertex_form(Qdot_rel, -0.0768, -0.0199, 1.0960)

    def eff_el_rel(self, Qdot_rel):
        """Compute the relative electrical efficiency of the CHP."""
        return vertex_form(Qdot_rel, -0.2611, 0.6743, 0.5868)

    def eff_th(self, Qdot_nom, Qdot_rel):
        """Compute the thermal efficiency of the CHP."""
        return self.eff_th_nom(Qdot_nom) * self.eff_th_rel(Qdot_rel)

    def eff_el(self, Qdot_nom, Qdot_rel):
        """Compute the electrical efficiency of the CHP."""
        return self.eff_el_nom(Qdot_nom) * self.eff_el_rel(Qdot_rel)

    def get_variables(self):
        """Get the MAiNGO variables."""
        BRANCHING_FILE_NAME = 'prios.txt'

        print()
        if os.path.exists(BRANCHING_FILE_NAME):
            prios = {k: int(v) for k, v in read_options(
                BRANCHING_FILE_NAME).items()}
            print(f"Using branching priorities from {BRANCHING_FILE_NAME}:")
        else:
            print("No 'prios.txt' file found in", os.getcwd(),
                  "proceeding with default branching priorities:")
            prios = {}
        vars = [
            maingopy.OptimizationVariable(
                maingopy.Bounds(self.Qdot_nom_min, self.Qdot_nom_max),
                prios.get("Qdot_nom", 1),
                "Qdot_nom"
            )
        ]
        if self.reduced_space:
            vars.extend([
                *(
                    maingopy.OptimizationVariable(
                        maingopy.Bounds(0, 1),
                        prios.get(f"Qdot_rel_s{s}", 1),
                        f"Qdot_rel_s{s}"
                    )
                    for s in range(self.Ns)
                ),
            ])
        else:
            for s in range(self.Ns):
                vars.extend([
                    maingopy.OptimizationVariable(
                        maingopy.Bounds(0, 1),
                        prios.get(f"Qdot_rel_s{s}", 1),
                        f"Qdot_rel_s{s}"
                    ),
                    maingopy.OptimizationVariable(
                        maingopy.Bounds(
                            0, self.Qdot_nom_max /
                            self.eff_th(self.Qdot_nom_max, 1)
                        ),
                        prios.get(f"Edot_in_s{s}", 1),
                        f"Edot_in_s{s}"
                    ),
                    maingopy.OptimizationVariable(
                        maingopy.Bounds(
                            0, self.Qdot_nom_max *
                            self.eff_el(self.Qdot_nom_max, 1) /
                            self.eff_th(self.Qdot_nom_max, 1)
                        ),
                        prios.get(f"P_out_s{s}", 1),
                        f"P_out_s{s}"
                    )
                ])

        for var in vars:
            print(" ", var.get_name(), var.get_branching_priority())
        print()
        return vars

    def approximate_optimal_point(self, n=1000):
        """Approximate the optimal point by evaluating the objective function"""
        if not self.reduced_space:
            raise NotImplementedError(
                "Approximation of optimal point not implemented for full space")
        
        import warnings

        def _nan_cols(arr):
            """Find the indices of nan columns (infeasible x domain)."""
            with warnings.catch_warnings():
                # All-NaN slice encountered
                warnings.simplefilter("ignore")
                return np.isnan(np.nanmin(arr, axis=0))

        x = np.linspace(self.Qdot_nom_min, self.Qdot_nom_max, n)
        y = np.linspace(0, 1, n)
        self.X, self.Y = np.meshgrid(x, y)
        F = np.ones_like(self.X)  # feasibility mask, 1 or nan
        Zx = self.f1_func([self.X])
        self.Z = np.zeros_like(Zx)  # objective value

        self.scenarioZs = []
        self.scenarioSolutions = []
        Fss = F * 0
        FSs = []
        for s in range(self.Ns):
            ps = self.data[s]
            Fs = np.ones_like(self.X)
            for res in self.g2_func([self.X], [self.Y], ps)[0]:
                Fs[res[0] >= 0] = float('nan')
            F[:, _nan_cols(Fs)] = float('nan')
            Zy = self.f2_func([self.X], [self.Y], ps)
            Zs = (Zx + Zy) * Fs
            Fss += np.nan_to_num(Fs, nan=0)
            FSs.append(Fs)
            feasible_x = ~_nan_cols(Zs)
            min_y = np.nanargmin(Zs[:, feasible_x], axis=0)
            self.Z[:, feasible_x] += self.w[s] * Zs[min_y, feasible_x]
            self.scenarioZs.append(Zs)
            self.scenarioSolutions.append((self.X[min_y, feasible_x], self.Y[min_y, feasible_x]))
        self.Z *= F
        with warnings.catch_warnings():
            # All-NaN slice encountered
            warnings.simplefilter("ignore")
            self.Z *= Fss/Fss

        xopt = self.X.flatten()[np.nanargmin(self.Z)]
        yopt = [np.interp(xopt, *mins) for mins in self.scenarioSolutions]
        return [xopt, *yopt]

    def get_initial_point(self):
        """Get the current variable values as the initial point."""
        if self.sample:
            return self.approximate_optimal_point(1000)

        initial_point = [
            self.Qdot_nom_max,
        ]

        if self.reduced_space:
            initial_point.extend([1] * self.Ns)
        else:
            initial_point.extend([
                1,
                self.Qdot_nom_max / self.eff_th(self.Qdot_nom_max, 1),
                self.Qdot_nom_max *
                self.eff_el(self.Qdot_nom_max, 1) /
                self.eff_th(self.Qdot_nom_max, 1)
            ] * self.Ns)
        return initial_point

    def f1_func(self, x):
        """Annualized investment cost in million euros/a."""
        Qdot_nom = x[0]
        # investment cost of the component
        ic = self.c_ref * (Qdot_nom / self.Qdot_nom_ref) ** self.M
        # fixed cost of the component
        fc = self.c_m * ic

        return 1e-6 * (self.af * ic + fc)

    def f2_func(self, x, ys, ps):
        """Annual operating cost in million euros/a."""
        Qdot_nom = x[0]
        Qdot_rel = ys[0]
        if (isinstance(Qdot_nom, maingopy.FFVar)
                and isinstance(Qdot_rel, maingopy.FFVar)):
            max = maingopy.max
        else:
            try:
                import sympy
                if (isinstance(Qdot_nom, sympy.Symbol)
                        and isinstance(Qdot_rel, sympy.Symbol)):
                    max = sympy.Max
                else:
                    max = np.maximum
            except ImportError:
                max = np.maximum
        Qdot_out = Qdot_nom * Qdot_rel

        if self.reduced_space:
            Edot_in = Qdot_out / \
                self.eff_th(Qdot_nom=Qdot_nom,
                            Qdot_rel=Qdot_rel)
        else:
            Edot_in = ys[1]

        if self.reduced_space:
            P_out = Edot_in * \
                self.eff_el(Qdot_nom=Qdot_nom,
                            Qdot_rel=Qdot_rel)
        else:
            P_out = ys[2]

        Qdot_dem, P_dem = ps

        if self.use_heater:
            # When allowing an electric heater with 100% efficiency
            Qdot_supplied_via_electricity = max(0, Qdot_dem - Qdot_out)
        else:
            # When not allowing an electric heater
            Qdot_supplied_via_electricity = 0

        P_grid = P_dem - P_out + Qdot_supplied_via_electricity

        # Total variable cost = purchase for gas
        # + purchase for missing electricity
        # or compensation (negative cost) for selling excess electricity
        return 1e-6 * (
            self.p_gas * Edot_in
            + self.p_el_buy * max(0, P_grid)
            - self.p_el_sell * max(0, -P_grid)
        ) * self.T_OP

    def g2_func(self, x, ys, ps):
        Qdot_rel = ys[0]
        # quadratic function that is positive (indicating a violation)
        # if we violate minimum part load requirements, i.e., if
        # Qdot_eps <= Qdot_out <= Qdot_out_min
        # min_partload_viol =
        #   -(Qdot_rel - self.Qdot_rel_min) * (Qdot_rel - self.Qdot_eps)
        # = -(Qdot_rel ** 2
        #     - Qdot_rel * (self.Qdot_rel_min + self.Qdot_eps)
        #     + self.Qdot_rel_min * self.Qdot_eps)
        # = -1 * Qdot_rel ** 2
        #   + (self.Qdot_rel_min + self.Qdot_eps) * Qdot_rel
        #   - self.Qdot_rel_min * self.Qdot_eps
        a = -1
        b = self.Qdot_rel_min + self.Qdot_eps
        c = -self.Qdot_rel_min * self.Qdot_eps
        min_partload_viol = vertex_form(Qdot_rel, a, b, c)

        definitions = []
        if not self.reduced_space:
            Qdot_nom = x[0]
            Edot_in = ys[1]
            P_out = ys[2]

            Qdot_out = Qdot_nom * Qdot_rel
            Edot_in_expr = Qdot_out / \
                self.eff_th(Qdot_nom, Qdot_rel)
            definitions.append(
                ((Edot_in_expr - Edot_in), "Edot_in_definition"))

            P_out_expr = Edot_in * \
                self.eff_el(Qdot_nom, Qdot_rel)
            definitions.append((P_out_expr - P_out, "P_out_definition"))

        # functions indicating a violation for positive values
        ineqs = [
            [min_partload_viol, "Minimum part load requirement"],
        ]
        if not self.use_heater:
            Qdot_nom = x[0]
            Qdot_out = Qdot_nom * Qdot_rel
            Qdot_dem = ps[0]
            dem_violation = Qdot_dem - Qdot_out
            ineqs.append([dem_violation, "Heat demand satisfaction"])

        return [
            ineqs,  # ineq
            [],  # squash
            definitions,  # eq
            [],  # ineqRelOnly
            [],  # eqRelOnly
        ]

    def solve(self, **options):
        """Solve the problem with the given options.

        Options
        -------
        epsilonA : double
            Absolute optimality tolerance, i.e., termination when (UBD-LBD) <
            BAB_epsilon_a.

        epsilonR : double
            Relative optimality tolerance, i.e., termination when (UBD-LBD) <
            BAB_epsilon_r * UBD.

        deltaIneq : double
            Absolute feasibility tolerance for inequality constraints (i.e.,
            constraint is considered satisfied if gi_(x)<=UBP_delta_ineq.

        deltaEq : double
            Absolute feasibility tolerance for equality constraints (i.e.,
            constraint is considered satisfied if abs(hi_(x))<=UBP_delta_eq.

        relNodeTol : double
            Relative tolerance for minimum node size.

        BAB_maxNodes : unsigned
            Maximum number of nodes (i.e., solver terminates when more than
            BAB_maxnodes are held in memory; used to avoid excessive branching)

        BAB_maxIterations : unsigned
            Maximum number of iterations (i.e., maximum number of nodes visited
            in the Branch-and-Bound tree)

        maxTime : unsigned
            CPU time limit in seconds.

        confirmTermination : bool
            Whether to ask the user before terminating when reaching time,
            node, or iteration limits.

        terminateOnFeasiblePoint : bool
            Whether to terminate as soon as the first feasible point was found
            (no guarantee of global or local optimality!)

        targetLowerBound : double
            Target value for the lower bound on the optimal objective. MAiNGO
            terminates once LBD>=targetLowerBound (no guarantee of global or
            local optimality!)

        targetUpperBound : double
            Target value for the upper bound on the optimal objective. MAiNGO
            terminates once UBD<=targetUpperBound (no guarantee of global or
            local optimality!)

        infinity : double
            User definition of infinity (used to initialize UBD and LBD)
            [currently cannot be set by the user via set_option].

        PRE_maxLocalSearches : unsigned
            Number of local searches in the multistart heuristic during
            preprocessing at the root node.

        PRE_obbtMaxRounds : unsigned
            Maximum number of rounds of optimization-based range reduction
            (OBBT; cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731;
            maximizing and minimizing each variable subject to relaxed
            constraints) at the root node. If >=1 and a feasible point is
            found during multistart, one round of OBBT using an objective cut
            (f_cv<=UBD) is conducted as well.

        PRE_pureMultistart : bool
            Whether to perform a multistart only. A B&B tree will not be
            constructed and no lower bounding problems will be solved.

        BAB_nodeSelection : babBase::enums::NS
            How to select the next node to process. See documentation of
            babBase::enums::NS for possible values.

        BAB_branchVariable : babBase::enums::BV
            Which dimension to branch in for the current node. See
            documentation of babBase::enums::BV for possible values.

        BAB_alwaysSolveObbt : bool
            Whether to solve OBBT (feasibility- and, once a feasible point has
            been found, also optimality-based) at every BaB node.

        BAB_dbbt : bool
            Whether to do a single round of duality based bound tightening
            (DBBT, cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19 (1995) 551). If
            false, no DBBT is used. If true, multipliers from CPLEX are used to
            tighten bounds (essentially for free). we tried additional rounds
            but without reasonable improvement.

        BAB_probing : bool
            Whether to do probing (cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19
            (1995) 551) at every node (can only be done if BAB_DBBT_maxrounds
            >= 1)

        BAB_constraintPropagation : bool
            Whether to do constraint propagation. If false, no constraint
            propagation is executed.

        LBP_solver : lbp::LBP_SOLVER
            Solver for solution of lower bounding problems.

        LBP_linPoints : lbp::LINP
            At which points to linearize for affine relaxation. See
            documentation of lbp::LINP for possible values.

        LBP_subgradientIntervals : bool
            Whether to use the heuristic to improve McCormick relaxations by
            tightening the range of each factor with the use of subgradients
            (cf. Najman & Mitsos, JOGO 2019)

        LBP_obbtMinImprovement : double
            How much improvement needs to be achievable (relative to initial
            diameter) to conduct OBBT for a variable.

        LBP_activateMoreScaling : unsigned
            Number of consecutive iterations without LBD improvement needed to
            activate more aggressive scaling in LP solver (e.g., CPLEX)

        LBP_addAuxiliaryVars : bool
            Whether to add auxiliary variables for common factors in the lower
            bounding DAG/problem.

        LBP_minFactorsForAux : unsigned
            Minimum number of common factors to add an auxiliary variable.

        LBP_maxNumberOfAddedFactors : unsigned
            Maximum number of added factor as auxiliaries.

        MC_mvcompUse : bool
            Whether to use multivariate composition theorem for computing
            McCormick relaxations (see MC++ documentation for details)

        MC_mvcompTol : double
            (see MC++ documentation for details)

        MC_envelTol : double
            (see MC++ documentation for details)

        UBP_solverPreprocessing : ubp::UBP_SOLVER
            Solver to be used during pre-processing (i.e., multistart). See
            documentation of ubp::UBP_SOLVER for possible values.

        UBP_maxStepsPreprocessing : unsigned
            Maximum number of steps the local solver is allowed to take in each
            local run during multistart in pre-processing.

        UBP_maxTimePreprocessing : double
            Maximum CPU time the local solver is allowed to take in each local
            run during multistart in pre-processing. Usually, this should only
            be a fall-back option to prevent truly getting stuck in local
            solution.

        UBP_solverBab : ubp::UBP_SOLVER
            Solver to be used during Branch-and-Bound. See documentation of
            ubp::UBP_SOLVER for possible values.

        UBP_maxStepsBab : unsigned
            Maximum number of steps the local solver is allowed to take at each
            BaB node.

        UBP_maxTimeBab : double
            Maximum CPU time the local solver is allowed to take at each BaB
            node. Usually, this should only be a fall-back option to prevent
            truly getting stuck in local solution.

        UBP_ignoreNodeBounds : bool
            Flag indicating whether the UBP solvers should ignore the box
            constraints of the current node during the B&B (and consider only
            the ones of the root node instead).

        EC_nPoints : unsigned
            Number of points on the Pareto front to be computed in
            epsilon-constraint method (only available via the C++ API)

        BAB_verbosity : VERB
            How much output to print from Branch & Bound solver. Possible
            values are VERB_NONE (=0), VERB_NORMAL (=1), VERB_ALL (=2)

        LBP_verbosity : VERB
            How much output to print from Lower Bounding Solver. Possible
            values are VERB_NONE (=0), VERB_NORMAL (=1), VERB_ALL (=2)

        UBP_verbosity : VERB
            How much output to print from Upper Bounding Solver. Possible
            values are VERB_NONE (=0), VERB_NORMAL (=1), VERB_ALL (=2)

        BAB_printFreq : unsigned
            After how many iterations to print progress on screen
            (additionally, a line is printed when a new incumbent is found)

        BAB_logFreq : unsigned
            Like BAB_printFreq, but for log.

        writeLog : bool
            Whether to write a log file (named bab.log)

        writeToLogSec : unsigned
            Write to log file after a given ammount of CPU seconds.

        writeResFile : bool
            Whether to write an additional file containing non-standard
            information about the solved model.

        writeCsv : bool
            Whether to write a csv-log file (named bab.csv). Currently, this
            only include time, LBD, UBD, and final output.

        PRE_printEveryLocalSearch : bool
            Whether to print every run during multistart at the root node.

        writeToOtherLanguage : PARSING_LANGUAGE
            Write to a file in a different modeling language.

        Returns
        -------
        solver : MAiNGO solver object
            A solver object that can be queried for solve related information
            and adjust different settings:

            * solver.evaluate_additional_outputs_at_point(point)
            * solver.evaluate_additional_outputs_at_solution_point()
            * solver.evaluate_model_at_point(point)
            * solver.evaluate_model_at_solution_point()
            * solver.get_LBP_count()
            * solver.get_UBP_count()
            * solver.get_cpu_solution_time()
            * solver.get_final_LBD()
            * solver.get_final_abs_gap()
            * solver.get_final_rel_gap()
            * solver.get_iterations()
            * solver.get_max_nodes_in_memory()
            * solver.get_objective_value()
            * solver.get_solution_point()
            * solver.get_status()
            * solver.get_wallclock_solution_time()
            * solver.read_settings('settings.txt')
            * solver.set_iterations_csv_file_name('iterations.csv')
            * solver.set_json_file_name('results.json')
            * solver.set_log_file_name('results.log')
            * solver.set_model(myMAiNGOmodel)
            * solver.set_option(option, value)
            * solver.set_result_file_name('res.txt')
            * solver.set_solution_and_statistics_csv_file_name('sol.csv')
            * solver.solve()
            * solver.write_model_to_file_in_other_language('ALE', 'prob.ale')

        status : MAiNGO RETCODE
            Return code for the solution, possible values are:

            * GLOBALLY_OPTIMAL
            * INFEASIBLE
            * FEASIBLE_POINT
            * NO_FEASIBLE_POINT_FOUND
            * BOUND_TARGETS
            * NOT_SOLVED_YET
            * JUST_A_WORKER_DONT_ASK_ME
        """
        self.branching_priorities = options.pop('branching_priorities', {})
        solver = maingopy.MAiNGO(self)
        lang = options.pop('writeToOtherLanguage', LANG_NONE)
        if lang is None:
            lang = LANG_NONE
        if lang not in {LANG_ALE, LANG_GAMS, LANG_NONE}:
            try:  # whether a string was given
                lang = globals().get(f'LANG_{lang.upper()}')
            except KeyError:
                raise ValueError(f'Language {lang} is not implemented! '
                                 'Possible values for writeToOtherLanguage are'
                                 ' ALE, GAMS or NONE!')
        if lang != LANG_NONE:
            ending = {LANG_ALE: '.ale', LANG_GAMS: '.gms'}[lang]
            solver.write_model_to_file_in_other_language(lang,
                                                         type(self).__name__ + ending)

        # Handle special options for adjusting default file names
        for file_name_option in [
            'iterations_csv_file_name',
            'json_file_name',
            'log_file_name',
            'result_file_name',
            'solution_and_statistics_csv_file_name',
            'bab_file_name',
        ]:
            file_name = options.pop(file_name_option, '')
            if file_name:
                getattr(solver, 'set_' + file_name_option)(file_name)

        for option, value in options.items():
            if not solver.set_option(option, value):
                raise ValueError(f'Option "{option}" is not recognized!')
        status = solver.solve()
        return solver, status


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Solve the CHP sizing problem.')
    parser.add_argument(
        '--Ns', type=int, default=-1,
        help='Number of samples to generate for the random demands.'
    )
    parser.add_argument(
        '--settings', type=str, default='',
        help='Settings file to use.'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Pause to allow attaching debugger.'
    )
    parser.add_argument(
        '--plot', action='store_true',
        help='Plot the feasible points in the domain and quit.'
    )
    parser.add_argument(
        '--print', action='store_true',
        help='Print the objective and constraint expressions and quit.'
    )
    parser.add_argument(
        '--use_heater', action='store_true',
        help='Consider an electric heater to satisfy unmet heat demand.'
    )
    parser.add_argument(
        '--reduced_space', action='store_true',
        help='Use a reduced space model for optimization.'
    )
    parser.add_argument(
        '--sample', action='store_true',
        help='Use sampling for initialization.'
    )
    args = parser.parse_args()

    if maingopy.HAVE_MAiNGO_MPI():

        import sys
        try:
            from mpi4py import MPI
        except ImportError:
            print("maingopy was built with MPI support, but mpi4py was not found.")
            sys.exit(1)

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        buffers = maingopy.muteWorker()

    if args.debug:
        msg = "Pausing to allow attaching debugger, press enter to continue."
        if maingopy.HAVE_MAiNGO_MPI():
            if rank == 0:
                input(msg)
            comm.Barrier()
        else:
            input(msg)

    import pandas as pd

    if args.Ns > 0:
        from get_demands import random_demands
        data = random_demands(args.Ns)
    else:
        data = DEFAULT_DATA

    mymodel = CHP_sizing_problem(
        data, use_heater=args.use_heater, reduced_space=args.reduced_space, sample=args.sample)

    if args.print:
        import sympy
        print("Objectives:")
        if args.reduced_space:
            x = [sympy.S('x')]
            ys = [sympy.S(f'y_s')]
        else:
            x = [sympy.S('x')]
            ys = [sympy.S(f'y1_s'), sympy.S(f'y2_s'), sympy.S(f'y3_s')]
        ps = [sympy.S(f'p1_s'), sympy.S(f'p2_s')]
        f1 = mymodel.f1_func(x)
        f2s = mymodel.f2_func(x, ys, ps)
        print(str(f1).lower())
        print(str(f2s).lower())
        print("Constraints:")
        g2s = mymodel.g2_func(x, ys, ps)[0]
        for g2si in g2s:
            print(f'{g2si[1]}:', str(g2si[0]).lower())

        Qdot_dem = [d[0] for d in data]
        P_dem = [d[1] for d in data]

        results = pd.DataFrame(index=range(mymodel.Ns), data=dict(
            Qdot_dem=Qdot_dem,
            P_dem=P_dem,
        ))
        print(results)
        sys.exit(0)

    if args.plot:
        import matplotlib.pyplot as plt
        import matplotlib.lines as mlines

        if not args.reduced_space:
            print("Plotting is only supported for the reduced space model, "
                  "switching reduced_space flag!")
            mymodel.reduced_space = True

        # Render text with LaTeX (uncomment for faster plotting)
        plt.rc('text', usetex=True)

        xopt, *yopt = mymodel.approximate_optimal_point()

        levels = np.linspace(
            min(np.nanmin(Zs) for Zs in mymodel.scenarioZs),
            max(np.nanmax(Zs) for Zs in mymodel.scenarioZs),
            100
        )

        l = int(np.ceil((mymodel.Ns + 1) / 3))
        fig, axs = plt.subplots(l, 3, figsize=(
            9/0.8, 3 * l), sharex=True, sharey=True)
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']

        axes = iter(axs.flatten())
        for s, (Zs, ax) in enumerate(zip(mymodel.scenarioZs, axes)):
            c = colors[s % len(colors)]
            ax.contourf(mymodel.X, mymodel.Y, Zs, levels=levels)
            i = np.nanargmin(Zs)
            label = f'(x^*_{s}, y^*_{s})'
            if plt.rcParams['text.usetex']:
                label = '$' + label + '$'
            ax.scatter(mymodel.X.flatten()[i], mymodel.Y.flatten()[i], c=c, label=label)
            
            label = f'f_{{I}}(x) + f^*_{{II,{s}}}(x)'
            # If rendered with LaTeX add $...$ around the label
            if plt.rcParams['text.usetex']:
                label = '$' + label + '$'
            ax.plot(*mymodel.scenarioSolutions[s], ls='--', c=c, label=label)
            # ax.plot(*mins, ls='--', c=c, label=label)
            
            title = f'f_{{I}}(x) + f_{{II,{s}}}(x,y)'
            # If rendered with LaTeX add $...$ around the title
            if plt.rcParams['text.usetex']:
                title = '$' + title + '$'
            ax.set_title(title)
            if plt.rcParams['text.usetex']:
                ax.set_xlabel('$x$')
                ax.set_ylabel('$y$')
            else:
                ax.set_xlabel('x')
                ax.set_ylabel('y')
            # bottom left corner
            ax.legend(loc=3)

        ax = next(axes)

        # ensure the cbar shows up
        fig.subplots_adjust(right=0.8, wspace=0.1, hspace=0.25)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.025, 0.7])
        fig.colorbar(
            ax.contourf(mymodel.X, mymodel.Y, mymodel.Z, levels=levels),
            cax=cbar_ax
        )
        label = f'x^*'
        # If rendered with LaTeX add $...$ around the label
        if plt.rcParams['text.usetex']:
            label = '$' + label + '$'
        ax.axvline(xopt, c='k', ls='-', label=label)
        for s, mins in enumerate(mymodel.scenarioSolutions):
            c = colors[s % len(colors)]
            ax.plot(*mins, c=c, ls='--')
            ax.scatter(xopt, yopt[s], c=c)
        title = f'f_{{I}}(x) + \sum_s f^*_{{II,s}}(x)/{mymodel.Ns}'
        # If rendered with LaTeX add $...$ around the title
        if plt.rcParams['text.usetex']:
            title = '$' + title + '$'
        ax.set_title(title)
        if plt.rcParams['text.usetex']:
            ax.set_xlabel('$x$')
            ax.set_ylabel('$y$')
        else:
            ax.set_xlabel('x')
            ax.set_ylabel('y')

        # modify legend
        handles, labels = ax.get_legend_handles_labels()
        yopt_label = f'y^*_s'
        fsopt_label = 'f_{I}(x) + f^*_{II,s}(x)'
        # If rendered with LaTeX add $...$ around the label
        if plt.rcParams['text.usetex']:
            yopt_label = '$' + yopt_label + '$'
            fsopt_label = '$' + fsopt_label + '$'
        # Add a black marker to the legend
        yopt = mlines.Line2D([], [], color='k', marker='o',
                                linestyle='None', label=yopt_label)
        # Add a black dashed line
        fsopt = mlines.Line2D([], [], color='k', linestyle='--',
                                label=fsopt_label)
        ax.legend(handles=[handles[0], yopt, fsopt])

        # empty the remaining axes
        for eax in axes:
            eax.axis('off')

        if args.use_heater:
            figname = f'CHP_with_heater_{mymodel.Ns}_scenarios.pdf'
        else:
            figname = f'CHP_without_heater_{mymodel.Ns}_scenarios.pdf'
        plt.savefig(figname)
        plt.show()
        sys.exit(0)

    if args.settings:
        try:
            options = read_options(args.settings)
        except Exception as e:
            raise RuntimeError(
                f"Trying to interpret argument '{args.settings}' "
                f"as settings file name gives: {e}")
    elif os.path.exists(DEFAULT_SETTINGS_FILE_NAME):
        options = read_options(DEFAULT_SETTINGS_FILE_NAME)
    else:
        options = {}

    if args.debug:
        options["bab_file_name"] = 'bab.dot'
    solver, status = mymodel.solve(**options)

    Qdot_dem = [d[0] for d in data]
    P_dem = [d[1] for d in data]
    Qdot_nom, *op_vars = solver.get_solution_point()
    if args.reduced_space:
        Qdot_rel = op_vars
    else:
        Qdot_rel = np.array([op_vars[i]
                             for i in range(0, 3 * mymodel.Ns, 3)])
        Edot_in = np.array([op_vars[i] for i in range(1, 3 * mymodel.Ns, 3)])
        P_out = np.array([op_vars[i] for i in range(2, 3 * mymodel.Ns, 3)])
    Qdot_rel = np.array(Qdot_rel)
    Qdot_out = Qdot_nom * Qdot_rel
    Qdot_diff = Qdot_out - Qdot_dem
    Qdot_diss = np.maximum(0, Qdot_diff)
    Qdot_el = np.maximum(0, -Qdot_diff)
    if args.reduced_space:
        Edot_in = Qdot_out / \
            mymodel.eff_th(Qdot_nom=Qdot_nom,
                           Qdot_rel=Qdot_rel)
        P_out = Edot_in * \
            mymodel.eff_el(Qdot_nom=Qdot_nom,
                           Qdot_rel=Qdot_rel)
    P_buy = np.maximum(0, P_dem - P_out)
    P_sell = np.maximum(0, P_out - P_dem)

    N_s = len(data)

    results = pd.DataFrame(index=range(N_s), data=dict(
        Qdot_dem=Qdot_dem,
        P_dem=P_dem,
        Qdot_nom=[Qdot_nom] * N_s,
        Qdot_rel=Qdot_rel,
        Qdot_out=Qdot_out,
        Qdot_el=Qdot_el,
        Qdot_diss=Qdot_diss,
        Edot_in=Edot_in,
        P_out=P_out,
        P_buy=P_buy,
        P_sell=P_sell,
    ))
    print(results)

    if maingopy.HAVE_MAiNGO_MPI():
        maingopy.unmuteWorker(buffers)
