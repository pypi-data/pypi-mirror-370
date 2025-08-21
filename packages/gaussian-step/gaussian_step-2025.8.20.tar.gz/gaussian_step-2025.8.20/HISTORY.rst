=======
History
=======
2025.8.20: Added the atomic reference energies for wB97XD and M062X functionals
    * Added the atomic reference energies for wB97XD and M062X functionals for the
      6-31G, 6-311G, and CBSB7 basis set families.
    * Fixed a bug with the description of the model if the DFT functional was given as a
      variable.
    * Improved error handling when Gaussian fails.

2025.8.12: Added Wavefunction Stability step
    * Added the Wavefunction Stability step, which analyzes the stability of HF and DFT
      wavefunctions and optimially lowers the symmetry to find the stable
      wavefunction. This step can also explore other spin states to find the lowest
      energy state.
    * Added M062X and wB97XD hybrid functionals to the available list.
      
2025.1.31: Bugfix: shape of gradients array
    * Fixed a bug in the shape of the gradients array when reading from the punch
      file. They are now correctly output as a [natoms][3] array.
      
2025.1.29: Added an option to save the structure in the standard orientation.
    * Added an option to save the structure in the standard orientation, which is
      the orientation used by Gaussian for the calculations. This is useful for
      visualizing the structure, and is also the orientation for e.g. the calculated
      orbitals.
    * Fixed a bug in displaying the structure with the orbitals or density. The sructure
      is now always in the standard orientation, regardless of the option above, as it
      must be since the orbitals and density are calculated in the standard orientation.
    
2025.1.5: Added PBErev, HSE06, PBE0 and PBE0rev energies for thermochemistry
    * Added the atom energies for the 6-31G and 6-311G basis set families for the
      PBErev (PBEhPBE), HSE06 (HSEH1PBE), PBE0 (PBE1PBE), and PBE0rev (PBEH1PBE) density
      functionals for the thermodynamics step.
    * Added the electronic state to the output and properties
    * Added refereneces for all the methods and DFT functional in the GUI.
    * Improved the output to include the full name of the method and DFT functional
      
2024.12.24: Minor enhancement to Thermochemistry.txt report
    * Added the method and basis set to the header of the Thermochemistry.txt report.
    * Caught some cases where the system name was reported as None.

2024.12.23: Bugfix: thermochistry for DFT methods failed
    * The code was not properly handling the DFT methods in the thermodynamics step.
      This has been fixed.
    * Improved the reporting on why the atomization energy or enthalpy of formation could
      not be calculated.

2024.12.22: Added more methods and basis sets for thermo
    * Added the atom energies for the 6-31G and 6-311G basis sets to the thermodynamics
      step for HF, B3LYP, all MP, CC, CBS-xx, and Gn composite methods
    * Added detailed output of the thermochemistry calculations in Thermochemistry.txt
    * Allowed composite methods to be access through the Thermodynamics Step.
    * Added ability to print and/or save the basis set to a file.
    * Added options for the numerical grids used in DFT calculations.
      
2024.12.11: Loosened tolerance on gradients from punch file
    * The code checks that the gradients in the punch file are similar to those in the
      output. Apparently the check was too tight, so it has been loosened. A warning is
      printed if the gradients differ too much so that we can understand if it is an
      issue.
      
2024.12.9: Improvements to thermodynamics step
    * Added B3LYP atom energies to the thermodynamics step.
    * Expanded the properties to include essentially everything calculated by Gaussian.
    * Added the ability to get the initial Hessian for an optimization from propertiesm
      or from the checkpoint file.
    * Improved the handling of the checkpoint file so by default it is saved and the
      next substep uses it for initial guesses, etc.
    * Added options to remove the checkpoint files at the end of the calculation.

2024.12.1.1: Bugfix: Typographical problems with the output.

2024.12.1: Added thermodynamics step
    * Access the FREQ command in Gaussian to calculation the thermodynamic functions.
    * Added code and data for calculating enthalpy of formation for many computational
      models including the 6-31G and 6-311G basis set families.
    * Added output of timing data to the standard directory ~/.seamm.d/timing
    * Cleaned up and standardized the names of result data
      
2024.11.18: Enhancement: added properties
    * Added properties for the energy and enthalpy, etc. from composite models.
    * Protected the code from crashing is Gaussian failed.
      
2024.10.15: Bugfix: errors using short names of methods and functionals
    * There were bugs in the code that caused errors when using short names, e.g. "HF"
      or "CCD" for the method, or e.g. "B3LYP" for the density functional.
      
2024.10.10: Enhancement: added sempiempirical methods
    * Added the various semiempirical methods supported by Gaussian so they can be used
      from SEAMM.
      
2024.8.23: Enhancements: added bond orders and improved transition state optimization
    * Added ability to calculate the Wiberg bond order matrix and optionally use to set
      the bond orders of the structure.
    * Enhanced the optimization for transitions states to capture the vibrational
      analysis if the second derivatives are calculated, and report on the stability of
      the structure.

2024.7.27: Bugfix: issues when used in loop
    * Fixed a bug that caused the plug-in to fail when used in a loop.
    * Improved the creation of the gaussian.ini file to both work better and keep the
      comments in the file.
      
2024.6.5: Cleaned up logging from code.
    * The logging was a bit aggressive, so moved most logging down to the debug
      level. This will make the output of e.g. geomeTRIC more readable.
      
2024.5.31: Added optimization of transition states, and...
    * Corrected implementation of composite methods (Gn, CBS-x) to handle optimization.
    * Added target of the optimization to allow transition states and saddle points.
    * Corrected a bug in handling the maximum number of optimization steps.
    * Corrected bug determining if optimization completed properly.
    * Corrected bug handling the composite method results.
      
2024.5.27: Added number of optimization steps to results
    * Added the number of steps for the optimizations to the results that can be output
      to tables, variables, etc.
      
2024.5.8 General enhancements
    * Updated to new calculation handling, with ~/SEAMM/gaussian.ini controlling access
      to the installed version of Gaussian on the machine.
    * Added energy and gradients to results to support general use in e.g. energy scans.

2024.1.19: Switched to new way to run Gaussian, added option to just write input file
    * Switched to using the new way to run executables, which supports containers.
    * Added an option to just write the input file, without running
      Gaussian. This is useful for debugging, and for running Gaussian
      on a remote server.

2023.10.25 Bug fixes: variable for functional, and parsing FChk file
    * Fixed a problem with handling the functional if it was a variable rather than a
      specific functional.
    * Fixed a problem parsing the FChk file. For exponents > 99 the FORTRAN format used
      in Gaussian grops the "E", resulting in numbers like 0.947-104 that caused a
      problem when trying to read them.
      
2023.10.22 Bug fixes: orbital plots and output
    * The plots of the HOMO and LUMO were shifted by one orbital due to some code
      counting from 1 and other, from 0. Sigh.
    * The output to Job.out was inadvertently truncated.

2023.10.7 Added structure file for plots of density and orbitals.
    * Always write the current structure as 'structure.sdf' in the directory where the
      cube files for orbitals and densities are written. The Dashboard picks up this
      file to render the structure along with the surfaces.
      
2023.9.27 Added composite and other methods, DFT functionals
    * Now support HF, DFT, MP4, CCD & CCSD, CBS-x, and Gn methods
    * Added PBE, PBE-98, PBE0, and HSE06 functionals
    * Added analysis of HOMO/LUMO gap energy
    * Added plotting of orbitals and densities
    * Added otuput of atomic charges and spins, and placing them on the configuration.
    * Added ability to control the system/configuration update

2023.2.26.1 Moved Gaussian output to output.txt
    * Capturing stdout prevent users from seeing the output during a calculation.
      This fixes that.
      
2023.2.26 Initial version with energy and optimization 
    * Support running the energy or optimization with HF, DFT, MP2 and MP3 though
      testing has not yet been thorough.
    * The DFT functional supported are at the moment limited.
      
2023.2.24
    * Plug-in created using the SEAMM plug-in cookiecutter.
