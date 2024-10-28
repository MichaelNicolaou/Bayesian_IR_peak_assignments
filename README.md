# Bayesian_IR_peak_assignments
This repository is created for the purposes of storing and sharing the scripts created for and used in the research paper "IR of Vanillin, a classic study with a twist" (10.26434/chemrxiv-2023-72r06-v2). 

Three Python scripts are contained in this repository, both as standard .py and as Jupyter notebook .ipynb files, along with images and files used to illustrate and initialise the scripts for introductory purposes.
The Jupyter files contain well-documented tutorials and explanations of what each part of the scripts do and what the fundamental science, logic and concepts behind the processes are, in an interactive way for those interested in understanding the cogs-and-gears of this research, using it in their own subjects or building on top of it.

The research topic of this publication was the study of vibrational IR spectral features as found in experimental IR readings with the help of chemical sense, calibrated DFT calculations (PBE0 / 6-311++G(2d,2p) with a scaling factor of 0.950) and as a novel approach, the implementation of Bayesian inference to present possible matching assignment combinations.

The repository contains three fundamental scripts used for this process:
  1. Pipeline_Gaussian: A script that reads Gaussian-16 results (.log) files (for vibrational frequency calculations) and extracts frequency and intensity information, storing it in the forms of visualised "spectra" (arrays of 4000 points) as a python variables file and normal mode information, storing it as an excel spreadsheet.
  2. Bayesian_peak_assignment: A script that takes in information from a structured excel spreadsheet (information on how to structure contained in the Jupyter notebook) and performs Bayesian inference to produce all acceptable DFT frequency-to-Experimental peak assignment options, along with their respective "probabilities" (thought of as relative fit of peak matches).
  3. Normal_modes: A script that reads the output excel result files from "Pipeline_Gaussian" and displays all important contribution atomic vibrations (bond displacements above a given threshold of % contribution) for a specified vibrational mode as chosen by the user.

Further scripts were developed for the graphs included in the paper, but were not included in the repository.
