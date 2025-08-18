import runpy
  

def main():
    """Entry point for running the downstream analysis script."""
    runpy.run_module("accusnv.new_snv_script", run_name="__main__")


if __name__ == "__main__":
    main()
