# Free-Form Simulation Metrics

## Experiment
**Title:** Mach-Zehnder Interferometer
**Description:** Two-path interferometer that splits a coherent beam into two arms and recombines them to create interference fringes sensitive to phase differences

## Simulation Results
**Figures Generated:** 1
**Execution Success:** Yes

## Design Alignment
**Alignment Score:** 9/10
**Models Design Accurately:** True
**Physics Match Quality:** exact

## Convergence
**Converged:** Yes
**Iterations:** 1/3
**Total Time:** 0.00 seconds

### Missing from Simulation
- None

### Incorrect in Simulation
- Energy conservation check expects wrong value - mirrors are in series (should multiply reflectivities), not parallel
- Expected max calculation doesn't properly account for interference - should be full input flux times losses at constructive interference

## API Usage
Token usage data not available

## Physics Assessment

The simulation correctly models quantum interference in a Mach-Zehnder interferometer with proper beam splitter matrices and phase evolution. However, there's a critical error: the beam splitter matrix convention is inconsistent. The code uses a symmetric matrix [[1, i], [i, 1]]/√2, but applies it twice (at BS1 and BS2) which doesn't preserve the standard MZI behavior. A 50/50 beam splitter should map input state [a,b] to [(a+ib)/√2, (ia+b)/√2]. The double application with the same matrix creates unexpected phase relationships. The visibility of 1.0 at detector 1 with minimum intensity exactly zero suggests perfect destructive interference, which is correct for an ideal lossless MZI, but the energy conservation check fails because the code doesn't properly account for how losses should be applied.
