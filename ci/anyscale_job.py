import argparse
import ray

parser = argparse.ArgumentParser()
parser.add_argument('--arg', type=str)
args = parser.parse_args()

@ray.remote
def f(arg):
    return "Argument is '" + arg + "'"

args = ["This", "is", "a", "test"] + [args.arg]
results = ray.get([f.remote(arg) for arg in args])

print("\n".join(results))