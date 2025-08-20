import time
import random
import string
import tracemalloc
from kv_cache.main import KVStore, scache

# Define a computationally expensive function
def expensive_computation(size: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

# Decorate the function with scache
@scache(ttl=3600)
def cached_computation(size: int) -> str:
    return expensive_computation(size)

def benchmark():
    sizes = [1000, 10000, 100000, 1000000]  # Different input sizes
    iterations = 100  # Number of iterations for each size

    # Start monitoring memory usage
    tracemalloc.start()

    # Measure performance without cache
    print("Benchmarking without cache...")
    start_time = time.time()
    for size in sizes:
        for _ in range(iterations):
            expensive_computation(size)
    end_time = time.time()
    print(f"Time taken without cache: {end_time - start_time:.2f} seconds")

    # Measure performance with cache
    print("Benchmarking with cache...")
    start_time = time.time()
    for size in sizes:
        for _ in range(iterations):
            cached_computation(size)
    end_time = time.time()
    print(f"Time taken with cache: {end_time - start_time:.2f} seconds")

    # Stop monitoring memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Current memory usage: {current / 10**6:.2f} MB; Peak: {peak / 10**6:.2f} MB")

if __name__ == "__main__":
    benchmark()