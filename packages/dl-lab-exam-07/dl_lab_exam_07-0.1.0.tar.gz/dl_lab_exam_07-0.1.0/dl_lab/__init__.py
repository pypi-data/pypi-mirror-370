from .core import list_experiments, get_experiment
def main():
    from .cli import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()
