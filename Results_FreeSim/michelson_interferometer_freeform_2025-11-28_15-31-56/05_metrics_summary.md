# Free-Form Simulation Metrics

## Experiment
**Title:** Michelson Interferometer
**Description:** Creates interference fringes by splitting a coherent beam into two perpendicular arms and recombining them to measure phase differences.

## Simulation Results
**Figures Generated:** 0
**Execution Success:** Yes

## Design Alignment
**Alignment Score:** 8/10
**Models Design Accurately:** True
**Physics Match Quality:** close

## Convergence
**Converged:** Yes
**Iterations:** 2/3
**Total Time:** 0.00 seconds

### Missing from Simulation
- None

### Incorrect in Simulation
- Visibility calculation is inconsistent - reports 0.0192 for 2D pattern analysis but 0.8390 for piezo scan, suggesting implementation error in radial phase model
- Constructive/destructive interference intensities are inverted - constructive (0) shows 0.0644 while quarter-wave shows 1.7653, which is backwards
- Radial phase model (tilt_angle = 0.001) is arbitrary and not specified in design - creates circular fringes not necessarily present in aligned interferometer
- Beam expander component specified but its effect (3x magnification) is only used for beam diameter, not for wavefront curvature changes

## API Usage
Token usage data not available

## Physics Assessment

The simulation has fundamental physics errors. (1) The Michelson interferometer is a CLASSICAL optics experiment, not a quantum experiment - it demonstrates wave interference, not quantum effects like photon statistics, entanglement, or wavefunction collapse. (2) The phase calculation is incorrect: the code uses 'phase_diff = 2 * k * path_difference' which is correct, but then adds an artificial 'radial_phase = k * tilt_angle * R' that doesn't properly model mirror tilt geometry. (3) The intensity formula at key positions gives wrong results: constructive interference (0) should give maximum intensity, but shows 0.0644 while quarter-wave shows 1.7653 - this is backwards. (4) The visibility calculation shows 0.0192 but theoretical maximum is 1.0000, indicating a major implementation bug. (5) The fringe contrast from scan (0.8390) contradicts the visibility (0.0192), showing internal inconsistency.
