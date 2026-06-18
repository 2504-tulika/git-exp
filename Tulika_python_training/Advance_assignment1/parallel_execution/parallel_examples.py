import threading
import time

import multiprocessing
import os

from concurrent.futures import ThreadPoolExecutor

from concurrent.futures import ProcessPoolExecutor

# Question 1: Create two threads that print numbers from 1 to 5 simultaneously
def print_numbers(thread_name: str) -> None:
    """
    Print numbers from 1 to 5.
    """
    for number in range(1, 6):
        print(f"{thread_name}: {number}")

# Question 2: Create a thread that calculates the sum of numbers from 1 to 100
def calculate_sum() -> None:
    """
    Calculate sum from 1 to 100.
    """
    result = sum(range(1, 101))

    print("Sum:", result)


# Question 3: Demonstrate join()
def task() -> None:
    """
    Simulate a task.
    """
    print("Task started")

    time.sleep(3)

    print("Task completed")

# Question 4: Create a thread that simulates downloading a file
def download_file(
    file_name: str
) -> None:
    """
    Simulate file download.
    """
    print(
        f"Downloading {file_name}..."
    )

    time.sleep(2)

    print(
        f"{file_name} downloaded."
    )

# Question 5: Create a process that prints the current process ID
def print_process_id() -> None:
    """
    Print current process ID.
    """
    print(
        f"Process ID: {os.getpid()}"
    )

# Question 6: Create a thread that calculates the square of a number

def calculate_square(number: int) -> None:
    """
    Calculate and print the square of a number.
    """
    print(
        f"Square of {number}: "
        f"{number ** 2}"
    )

def run_square_processes() -> None:
    """
    Create processes to calculate squares.
    """
    numbers = [2, 4, 6, 8]

    processes = []

    for number in numbers:
        process = multiprocessing.Process(
            target=calculate_square,
            args=(number,)
        )

        processes.append(process)
        process.start()

    for process in processes:
        process.join()

# Question 7: Convert a normal function into parallel execution using ThreadPoolExecutor
def square_number(number: int) -> int:
    """
    Return square of a number.
    """
    return number ** 2

def run_thread_pool() -> None:
    """
    Calculate squares using ThreadPoolExecutor.
    """
    numbers = [1, 2, 3, 4, 5]

    with ThreadPoolExecutor(
        max_workers=3
    ) as executor:

        results = list(
            executor.map(
                square_number,
                numbers
            )
        )

    print("Results:", results)

# Question 8: Convert a normal function into parallel execution using ProcessPoolExecutor.
def run_process_pool() -> None:
    """
    Calculate squares using ProcessPoolExecutor.
    """
    numbers = [1, 2, 3, 4, 5]
    with ProcessPoolExecutor(
        max_workers=3
    ) as executor:

        results = list(
            executor.map(
                square_number,
                numbers
            )
        )

    print("Results:", results)


if __name__ == "__main__":
    print("\n--- Question 1 ---")
    thread_one = threading.Thread(
        target=print_numbers,
        args=("Thread-1",)
    )
    thread_two = threading.Thread(
        target=print_numbers,
        args=("Thread-2",)
    )

    thread_one.start()
    thread_two.start()

    print("\n--- Question 2 ---")
    sum_thread = threading.Thread(
        target=calculate_sum
    )
    sum_thread.start()
    sum_thread.join()

    print("\n--- Question 3 ---")
    thread = threading.Thread(
        target=task
    )
    thread.start()
    thread.join()
    print("Main thread resumed.")

    print("\n--- Question 4 ---")
    files = [
        "file1.pdf",
        "file2.jpg",
        "file3.zip"
    ]
    download_threads = []
    for file in files:
        thread = threading.Thread(
            target=download_file,
            args=(file,)
        )
        download_threads.append(thread)
        thread.start()
    for thread in download_threads:
        thread.join()

    print("\n--- Question 5 ---")
    process_one = multiprocessing.Process(
        target=print_process_id
    )
    process_two = multiprocessing.Process(
        target=print_process_id
    )
    process_one.start()
    process_two.start()

    process_one.join()
    process_two.join()

    print("\n--- Question 6 ---")
    run_square_processes()

    print("\n--- Question 7 ---")
    run_thread_pool()

    print("\n--- Question 8 ---")
    run_process_pool()