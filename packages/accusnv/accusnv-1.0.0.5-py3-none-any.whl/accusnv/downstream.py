import runpy


def main():
    """Entry point for running the downstream analysis script."""
    runpy.run_module("accusnv.accusnv_downstream", run_name="__main__")


if __name__ == "__main__":
    main()
