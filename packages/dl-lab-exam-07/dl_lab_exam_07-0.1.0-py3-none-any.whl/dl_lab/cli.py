from .core import list_experiments, get_experiment

def main():
    print("Available Experiments:")
    for exp in list_experiments():
        print(exp)

    try:
        num = int(input("\nEnter experiment number: "))
        print("\nCode:\n")
        print(get_experiment(num))
    except ValueError:
        print("Invalid input. Please enter a number.")
