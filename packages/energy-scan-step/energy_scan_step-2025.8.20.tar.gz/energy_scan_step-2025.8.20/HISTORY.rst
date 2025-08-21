=======
History
=======
2025.8.20 -- Improved the graphs and added spins to them if available.
   * Added the ability to output graphs to one or more of the following formats: html,
     png, webp, svg, or pdf.
   * Capture the spin values, S**2 and the projected S**2, if captured by the quantum
     code, and add them to the graphs.
   * Fixed an issue if the two atoms in a bond scan were not actually bonded.

2025.8.6 -- Allows the values defining the scans to be variables.
   * This enhancement allows the variables defining the scan or frozen coordinate to be
     variables as well as static values.

2025.8.5 -- Bugfix: not correctly naming the configurations in the scan
   * The code did not correctly name the configurations generated during a scan, so
     their names were None.

2025.5.7 -- Enhancement to continue if minimization does not converge
   * Continue even if the minimization does not fully converge, as sometimes seems to be
     the case.
     
2025.4.11 -- Enhancements to allow repeated points
   * Allows the path to have repeated points, which is useful to e.g. go forwards and
     backawards to see the hysteresis.
     
2025.4.1 -- Bugfix: Error handling the coordinates in some cases
   * There was an error in handling the coordinates created by changes in the RDKit module
     in molsystem. This fixes it.
   * The incorrect logger was used for debugging.
   * Small format updates to due to changes in the code formatting rules in black.
     
2024.12.14 -- Cleanup! Reasonable working version.

2024.5.23 -- Initial working version
   * Can handle scans, freezing coordinates. Is not optimized yet.
   * Produces a graph of 1- and 2-D scans
   * Creates an SDF file with the optmized points along scans, which can be viewed in
     the Dashboard.

2024.4.3 (2024-04-03)
---------------------

* Plug-in created using the SEAMM plug-in cookiecutter.
