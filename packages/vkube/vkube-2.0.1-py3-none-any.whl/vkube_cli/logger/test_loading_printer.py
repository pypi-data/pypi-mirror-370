from loading_printer import LoadingPrinter
import time
# Stage 1: Output log-1 ten times
def print_loading_printer():
    printer = LoadingPrinter()
    # Output log-1 ten times
    for _ in range(10):
        printer.print("log-1")
        time.sleep(1)

    # Output log-2 ten times
    for _ in range(10):
        printer.print("log-2")
        time.sleep(1)

    # Output different log-0 ~ log-9
    for i in range(10):
        printer.print(f"log-{i}")
        time.sleep(1)

if __name__ == "__main__":
    print_loading_printer()
