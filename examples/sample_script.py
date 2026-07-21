"""
Deterministic sample script for PyChronicle pipeline integration.

Produces predictable variable assignments, a loop, and a function call
so that integration tests can assert specific line numbers, variable
names, and runtime values from the trace.
"""

# --- Simple assignments ---
x = 10
name = "PyChronicle"
flag = True

# --- Arithmetic ---
total = 0

for i in range(3):
    total += i

average = total / 3  # 1.0

# --- Function ---
def greet(who):
    message = "Hello, " + who
    return message


result = greet(name)

# --- Final marker ---
done = True
