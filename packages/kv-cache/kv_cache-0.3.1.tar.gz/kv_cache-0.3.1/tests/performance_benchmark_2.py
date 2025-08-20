import time
import random
import tracemalloc
from itertools import product
from tqdm import trange
from kv_cache.main import KVStore, scache

# Define a computationally expensive function with three parameters
def expensive_computation(a: int, b: int, c: int) -> int:
    time.sleep(0.001)  # Simulate a time-consuming computation
    return a * b * c

# Decorate the function with scache
@scache(ttl=3600)
def cached_computation(a: int, b: int, c: int) -> int:
    return expensive_computation(a, b, c)

def benchmark():
    # Prepare a list of hundreds of possible combinations
    param_range = range(1, 10)  # 1 to 100
    combinations = list(product(param_range, repeat=3))

    # Number of iterations for each scenario
    iterations_list = [100, 1000, 10000]

    # Start monitoring memory usage
    tracemalloc.start()

    for iterations in iterations_list:
        # Measure performance without cache
        print(f"Benchmarking without cache for {iterations} iterations...")
        start_time = time.time()
        for _ in trange(iterations, desc="Without Cache"):
            a, b, c = random.choice(combinations)
            expensive_computation(a, b, c)
        end_time = time.time()
        print(f"Time taken without cache: {end_time - start_time:.2f} seconds")

        # Measure performance with cache
        print(f"Benchmarking with cache for {iterations} iterations...")
        start_time = time.time()
        for _ in trange(iterations, desc="With Cache"):
            a, b, c = random.choice(combinations)
            cached_computation(a, b, c)
        end_time = time.time()
        print(f"Time taken with cache: {end_time - start_time:.2f} seconds")

    # Stop monitoring memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Current memory usage: {current / 10**6:.2f} MB; Peak: {peak / 10**6:.2f} MB")

if __name__ == "__main__":
    benchmark()