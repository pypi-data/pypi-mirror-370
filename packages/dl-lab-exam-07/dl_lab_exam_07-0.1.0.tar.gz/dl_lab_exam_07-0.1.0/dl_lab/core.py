EXPERIMENTS = {
    1: """# Experiment 1: Hello World
print("Hello, World!")""",
    2: """# Experiment 2: Addition
a, b = 5, 10
print("Sum:", a + b)""",
    3: """# Experiment 3: Multiplication Table
for i in range(1, 6):
    print(f"2 x {i} = {2*i}")"""
}

def list_experiments():
    return [f"{num}: {code.splitlines()[0]}" for num, code in EXPERIMENTS.items()]

def get_experiment(num: int) -> str:
    return EXPERIMENTS.get(num, "Experiment not found.")
