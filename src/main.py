import sys
from tqdm import tqdm as tqdm
import numpy as np
from interfaces import *


if __name__ == "__main__":

    # Show the percentage of feasible solutions in a problem
    if sys.argv[1] == "--venn-diagram":
        assert sys.argv[2] in problem_name_list
        import plot_src
        problem_name = sys.argv[2]
        n_montecarlo = 5000
        prob = problem(problem_name, 100, 'ignore', 2, True)
        set_list = [set() for _ in range(prob.n_constraints)]
        for i in tqdm(range(n_montecarlo)):
            x_random = np.random.random(prob.dim)
            res = prob.constraint_check(x_random)
            [set_list[idx].add(i) for idx in range(prob.n_constraints) if res[idx] > 0.0]
        plot_src.plot_venn_diagram(problem_name, set_list, n_montecarlo, ["constraint_"+str(i) for i in range(prob.n_constraints)])

    # Directly solve problem locally, with f function that returns np.nan on infeasible solutions.
    elif sys.argv[1] == "--local-solve":
        sys.argv.pop()
        problem_name = "airframes"
        task_info = {"task_name": "offsetcone"}
        algorithm_name = "ax"
        constraint_method = "ignore" # 'ignore','nan_on_unfeasible','constant_penalty_no_evaluation','algo_specific', 'nn_encoding'
        reuse_encoding = True
        seed = 6
        budget = 400
        local_solve(problem_name, algorithm_name, constraint_method, seed, budget, reuse_encoding, log_every=1, task_info=task_info)


    # Directly solve problem locally, with f function that returns np.nan on infeasible solutions.
    elif sys.argv[1] == "--all-local-solve":
        sys.argv.pop()
        reuse_encoding = True
        budget = 50
        global_log_path = "global_log.log"
        if os.path.exists(global_log_path):
            os.remove(global_log_path)

        algorithm_name_list = ["nevergrad",] #"snobfit", "cobyqa", "pyopt"]:
        constraint_method_list = ["ignore"]# ["algo_specific", "nn_encoding", 'constant_penalty_no_evaluation']
        problem_name_list = ['airframes']#['windflo', 'toy']
        seed_list = list(range(2,102))

        pb = tqdm(total = len(algorithm_name_list)*len(constraint_method_list)*len(problem_name_list)*len(seed_list))
        for algorithm_name in algorithm_name_list:
            for constraint_method in constraint_method_list:
                for problem_name in problem_name_list:
                    for seed in seed_list:
                        with open(global_log_path, "a") as file:
                            file.write(f"Launching {problem_name} {seed} {constraint_method} - ")
                        local_solve(problem_name, algorithm_name, constraint_method, seed, budget, reuse_encoding, log_every=100)
                        with open(global_log_path, "a") as file:
                            file.write("done\n")
                        pb.update()
        pb.close()



    # Plot how time per evaluation in snobfit increases linearly
    elif sys.argv[1] == "--plot-snobfit-time-per-1000-evaluations":
        from matplotlib import pyplot as plt
        a = [35.672,66.487,83.07,106.848,138.234,164.302,165.799,150.121,209.833,222.891,271.217,238.373,299.406,275.698,383.726,350.589,306.331,362.808,344.787,466.726000000001,495.216,544.442,483.626,572.485,505.259,523.818,644.181000000001,629.82,687.755999999999,601.378000000001,670.198,619.061,793.431000000001,791.849,738.907999999999,605.154999999999,705.071000000002,752.395999999999,727.92,760.445,774.154000000002,1010.754,1039.556,1055.197,1093.278,1070.267,1209.765,1240.372,1382.626,1265.622,1418.167,1332.901,1192.581,1425.083,1391.77,1585.827,1363.194,1522.193,1248.111,1561.504,1648.914,1860.214,1868.236,1732.594,1893.023,1554.103,2117.976,1658.75999999999,1469.963,1273.931]
        plt.plot(a)
        plt.ylabel("time (s)")
        plt.xlabel("x 1000 evaluations")
        plt.title("Snobfit: time per 1000 evaluations")
        plt.show()

    elif sys.argv[1] == "--airframes-f-variance":
        from airframes_objective_functions import motor_position_train, motor_position_enjoy, save_robot_pars_to_file, log_detailed_evaluation_results
        from problem_airframes import loss_function, dump_animation_info_dict, _decode_symmetric_hexarotor_to_RobotParameter_polar

        task_info = {"task_name": "offsetcone"}
        task_name = task_info["task_name"]
        train_for_seconds_list = [721]
        resfilename_list = [f"results/data/hex_f_variance_{seconds}s_{task_name}.csv" for seconds in train_for_seconds_list]
        hex_pars = _decode_symmetric_hexarotor_to_RobotParameter_polar(np.array([
            0.0, 0.5, 0.1667, 0.5, 0.5, 0.0, 0.5, 0.5000, 0.5, 0.5, 0.0, 0.5, 0.8333, 0.5, 0.5, 
        ]))
        pars_list = [hex_pars for i in range(len(train_for_seconds_list))]
        for i in range(len(train_for_seconds_list)):
            pars_list[i].task_info = task_info 


        assert len(train_for_seconds_list) == len(pars_list) == len(resfilename_list)
        for pars, train_for_seconds, resfilename,  in zip(pars_list, train_for_seconds_list, resfilename_list):

            save_robot_pars_to_file(pars)
            with open(resfilename, 'a') as f:
                print("seed_train;seed_enjoy;f",  file=f)
            for seed_train in range(2,22):
                motor_position_train(seed_train, train_for_seconds=train_for_seconds)
                for seed_enjoy in range(42,44):
                    info_dict = motor_position_enjoy(seed_enjoy)
                    f = loss_function(info_dict)
                    log_detailed_evaluation_results(pars, info_dict, seed_train, seed_enjoy, train_for_seconds)
                    dump_animation_info_dict(pars, seed_train, seed_enjoy, info_dict)
                    with open(resfilename, 'a') as file:
                        print(f"{seed_train};{seed_enjoy};{f}",  file=file)

    elif sys.argv[1] == "--airframes-f-variance-plot":
        import plot_src
        plot_src.multiobjective_scatter_by_train_time("results/data/details_every_evaluation_offsetcone.csv")
        plot_src.generate_bokeh_interactive_plot("results/data/details_every_evaluation_offsetcone.csv", "offsetcone")
        exit(0)
        plot_src.sidebyside_boxplots([
            "results/data/hex_f_variance_360s.csv",
            "results/data/hex_f_variance_720s.csv",
        ])

    else:
        print("sys.argv[1]=",sys.argv[1],"not recognized.", sep=" ")
