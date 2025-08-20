import sqlite3
import timeit
import os

results = []

def benchmark(db_path: str, journal_mode: str, synchronous: str, mmap_size: int, cache_size: int, page_size: int):
    def setup_db():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f'PRAGMA journal_mode = {journal_mode}')
        cursor.execute(f'PRAGMA synchronous = {synchronous}')
        cursor.execute(f'PRAGMA mmap_size = {mmap_size}')
        cursor.execute(f'PRAGMA cache_size = -{cache_size}')
        cursor.execute(f'PRAGMA page_size = {page_size}')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_value_store (
                key TEXT PRIMARY KEY,
                value BLOB,
                expires_at TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_key_value_store_expires_at 
            ON key_value_store(expires_at)
        ''')
        conn.commit()
        conn.close()

    # Ensure the database directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    # Benchmark the setup_db function
    time_taken = timeit.timeit(setup_db, number=50)
    # print(f"Benchmark for journal_mode={journal_mode}, synchronous={synchronous}, mmap_size={S_hr(mmap_size)}, cache_size={S_hr(cache_size)}, page_size={S_hr(page_size)}: {time_taken:.4f} seconds")

    # Store the results into a dict
    results.append({
        'journal_mode': journal_mode,
        'synchronous': synchronous,
        'mmap_size': mmap_size,
        'cache_size': cache_size,
        'page_size': page_size,
        'time_taken': time_taken
    })


mb = lambda b: b * 1024 * 1024
kb = lambda b: b * 1024
t_hr = lambda s: f"{s // 3600}h {s % 3600 // 60}m {s % 60}s"
s_hr = lambda s: f"{s:.4f} seconds"
# human readable size Kb / Mb / Gb
def S_hr(value: int):
    if value < kb(1):
        return f"{value} bytes"
    elif value < mb(1):
        return f"{value / 1024} KB"
    elif value < mb(1024):
        return f"{value / 1024 / 1024} MB"
    else:
        return f"{value / 1024 / 1024 / 1024} GB"



# Define the parameters and values to test
journal_modes = ['DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF']
synchronous_modes = ['OFF', 'NORMAL', 'FULL', 'EXTRA']
mmap_sizes = [0, mb(16), mb(64), mb(256), mb(512)]  # 0, 16MB, 64MB, 256MB, 512MB
cache_sizes = [mb(2), mb(8), mb(16), mb(32), mb(64), mb(128)]  # 2MB, 8MB, 16MB, 32MB, 64MB, 128MB
page_sizes = [kb(1), kb(4), kb(8), kb(16)]  # 1KB, 4KB, 8KB, 16KB

# Run the benchmark for each combination of parameters
for journal_mode in journal_modes:
    for synchronous_mode in synchronous_modes:
        for mmap_size in mmap_sizes:
            for cache_size in cache_sizes:
                for page_size in page_sizes:
                    benchmark("benchmark.db", journal_mode, synchronous_mode, mmap_size, cache_size, page_size)


# Print the results in a table
print("\nResults:")
print("journal_mode | synchronous | mmap_size | cache_size | page_size | time_taken")
print("-" * 80)
for result in results:
    print(f"{result['journal_mode']:12} | {result['synchronous']:11} | {S_hr(result['mmap_size']):9} | {S_hr(result['cache_size']):10} | {S_hr(result['page_size']):9} | {result['time_taken']:.4f}")

# Save the results to a CSV file
import csv

with open('benchmark_results.csv', 'w', newline='') as csvfile:
    fieldnames = ['journal_mode', 'synchronous', 'mmap_size', 'cache_size', 'page_size', 'time_taken']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for result in results:
        writer.writerow(result)

# print find the configuration that have the fastest time_taken
fastest_time_taken = min(results, key=lambda x: x['time_taken'])
print(f"\nFastest time taken: {fastest_time_taken['time_taken']} seconds")
print('parameters are:')
print(f"journal_mode: {fastest_time_taken['journal_mode']}")
print(f"synchronous: {fastest_time_taken['synchronous']}")
print(f"mmap_size: {S_hr(fastest_time_taken['mmap_size'])}")
print(f"cache_size: {S_hr(fastest_time_taken['cache_size'])}")
print(f"page_size: {S_hr(fastest_time_taken['page_size'])}")
