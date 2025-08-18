import os
from setuptools.command.install import install
from setuptools import setup, find_packages

class PostInstallCommand(install):
    def run(self):
        install.run(self)  
        script_path = os.path.join(self.install_lib, 'accusnv', 'slurm_status_script.py')
        if os.path.exists(script_path):
            os.chmod(script_path, 0o755)  
            print(f"Set execute permissions on {script_path}")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="accusnv",
    version="1.0.0.5",
    description="High-accuracy SNV calling for bacterial isolates using AccuSNV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lieberman Lab",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'accusnv': [
            'experiment_info.yaml',
            'config.yaml',
            'Snakefile',
            'slurm_status_script.py',
            'CNN_models/**',
            'CNN_models/*',
            'CNN_models/*/**',
            'scripts/**',
            'scripts/*',
            'scripts/*/**',
        ]
    },
    cmdclass={
        'install': PostInstallCommand,  
    },
    entry_points={
        "console_scripts": [
            "accusnv=accusnv.accusnv_main:main",
            "accusnv_snakemake=accusnv.accusnv_snakemake:main",
            "accusnv_downstream=accusnv.downstream:main"
        ]
    },
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "statsmodels",
        "torch>=2.6,<2.7",
        "biopython==1.78",
        "cutadapt",
        "pulp==2.7.0",
        "tqdm",
        "bcbio-gff==0.6.9"
        #"snakemake==7.32.3"
    ],
    python_requires=">=3.9,<3.10",
)
