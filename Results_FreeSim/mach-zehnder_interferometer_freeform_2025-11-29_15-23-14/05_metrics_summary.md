# Free-Form Simulation Metrics

## Experiment
**Title:** Mach-Zehnder Interferometer
**Description:** Creates interference fringes by splitting a coherent beam into two parallel arms and recombining them to measure phase differences and demonstrate wave-particle duality

## Simulation Results
**Figures Generated:** 0
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
- Total intensity (0.931095) exceeds expected total with losses (0.912566) by ~2%, suggesting minor error in loss accounting - likely double-counting beam splitter losses
- Theoretical comparison shows ~2.4% RMS error, which is larger than expected for a perfect simulation - suggests beam splitter phase convention may not perfectly match theoretical I₁ ∝ cos²(φ/2) formula

## API Usage

### Design Phase
**Prompt Tokens:** 3,120
**Completion Tokens:** 603
**Total Tokens:** 3,723
**Cost:** $0.018405

### Simulation Phase
**Prompt Tokens:** 14,462
**Completion Tokens:** 7,263
**Total Tokens:** 21,725
**Cost:** $0.152331

### Combined Total
**Total Tokens:** 25,448
**Total Cost:** $0.170736

## Physics Assessment

The beam splitter transformation is correctly implemented with proper i phase shift for reflection. The interference pattern qualitatively matches expected cos²(φ/2) and sin²(φ/2) behavior. However, there's a critical error: the expected total intensity calculation doesn't match the simulated values (0.9126 expected vs 0.9311 observed, ~2% discrepancy). The theoretical comparison shows 2.4% RMS error, which is too high for a simulation that should be exact. The phase convention and superposition are correct, but the normalization and loss accounting appear inconsistent.
