import argparse
from .run_stability_analysis import main as stability_analysis_main
from .run_count_loops import main as count_loops_main
from .run_lyapunov_analysis import main as lyapunov_analysis_main
from .run_clustering_analysis import main as clustering_analysis_main

def main():
    parser = argparse.ArgumentParser(prog="boolean_gene", description="Analysis of Boolean gene networks")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    stability_analysis_parser = subparsers.add_parser("run_stability_analysis", help="Run stability analysis")
    stability_analysis_parser.add_argument('-i', '--input', type=str, required=True, help="Path to input text file")
    stability_analysis_parser.add_argument('-o', '--output', type=str, required=True, help="Directory to save results")
    stability_analysis_parser.add_argument('-r', '--num_random_networks', type=int, required=False, default=100, help="Number of random networks to generate, where all random networks are logically identical to the input")
    stability_analysis_parser.add_argument('-n', '--simulations', type=int, required=False, default=1000, help="Number of simulations to run for each network")
    stability_analysis_parser.add_argument('-t', "--max_timesteps", type=int, required=False, default=100, help="Maximum number of timesteps per simulation before quitting if no attractor is found")

    lyapunov_analysis_parser = subparsers.add_parser("run_lyapunov_analysis", help="Run Lyapunov stability analysis")
    lyapunov_analysis_parser.add_argument('-i', '--input', type=str, required=True, help="Path to input text file")
    lyapunov_analysis_parser.add_argument('-o', '--output', type=str, required=True, help="Directory to save results")
    lyapunov_analysis_parser.add_argument('-r', '--num_random_networks', type=int, required=False, default=100, help="Number of random networks to generate, where all random networks are logically identical to the input")
    lyapunov_analysis_parser.add_argument('-n', '--simulations', type=int, required=False, default=1000, help="Number of simulations to run for each network")
    lyapunov_analysis_parser.add_argument('-t', "--max_timesteps", type=int, required=False, default=100, help="Maximum number of timesteps per simulation before quitting if no attractor is found")

    count_loops_parser = subparsers.add_parser("count_loops", help="Count loops in input and randomized networks")
    count_loops_parser.add_argument('-i', '--input', type=str, required=True, help="Path to input text file")
    count_loops_parser.add_argument('-o', '--output', type=str, required=True, help="Directory to save results")
    count_loops_parser.add_argument('-r', '--num_random_networks', type=int, required=False, default=100, help="Number of random networks to generate, where all random networks are logically identical to the input")

    clustering_coefficients_parser = subparsers.add_parser("run_clustering_analysis", help="Run clustering coefficient analysis")
    clustering_coefficients_parser.add_argument('-i', '--input', type=str, required=True, help="Path to input text file")
    clustering_coefficients_parser.add_argument('-o', '--output', type=str, required=True, help="Directory to save results")
    clustering_coefficients_parser.add_argument('-r', '--num_random_networks', type=str, required=False, default=100, help="Number of random networks to generate, where all random networks are logically identical to the input")

    args = parser.parse_args()
    
    if args.command == "run_stability_analysis":
        stability_analysis_main(args.input, args.output, args.num_random_networks, args.simulations, args.max_timesteps)
    elif args.command == "count_loops":
        count_loops_main(args.input, args.output, args.num_random_networks)
    elif args.command == "run_lyapunov_analysis":
        lyapunov_analysis_main(args.input, args.output, args.num_random_networks, args.simulations, args.max_timesteps)
    elif args.command == "run_clustering_analysis":
        clustering_analysis_main(args.input, args.output, args.num_random_networks)
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
