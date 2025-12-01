# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Bell State Generator using SPDC

**Timestamp:** 20251123_132334

**Quality Rating:** 7/10 (GOOD)

---

## Overview

The designer wants to create entangled Bell states using Type-II SPDC and demonstrate control over the relative phase between |HV⟩ and |VH⟩ components using a half-wave plate, enabling generation of different Bell states for quantum correlation measurements. The simulation code correctly models the core quantum mechanics: it starts with the proper Type-II SPDC Bell state |Φ+⟩ = (|HV⟩ + |VH⟩)/√2, implements realistic half-wave plate polarization rotation, and calculates appropriate entanglement metrics. The results are excellent - perfect fidelity to target Bell state (≈1.0), maximum entanglement entropy (ln(2) ≈ 0.693), high concurrence (≈1.0), and strong visibility (≈1.0). However, there are critical physics limitations: the simulation uses discrete polarization qubits rather than continuous field modes, cannot model the actual SPDC generation process (assumes perfect Bell state output), ignores spatial mode structure and collection efficiency, and treats detection as perfect projective measurements rather than realistic photodetection. The zero coincidence probability when both polarizers are at 0° is actually CORRECT physics - in the Bell state |HV⟩ + |VH⟩, there's zero amplitude for both photons to be H-polarized simultaneously. The simulation validates the polarization entanglement and measurement aspects but cannot verify whether the proposed experimental setup would actually generate the assumed Bell state.

## Key Insight

Simulation correctly validates Bell state manipulation and measurement, but cannot verify whether the experimental setup would actually produce the required entangled state.

## Design Intent

**Components:**
- 405nm pump laser: Creates SPDC in BBO crystal
- BBO crystal: Type-II SPDC generates orthogonally polarized entangled pairs at 810nm
- Half-wave plate: Controls relative phase φ between |HV⟩ and |VH⟩ components
- Polarizing beam splitter: Spatially separates H and V polarizations
- Adjustable polarizers: Enable measurement in different bases for Bell tests
- SPAD detectors: Detect individual photons with timing resolution

**Physics Goal:** Generate controllable Bell states |ψ⟩ = (|H⟩₁|V⟩₂ + e^(iφ)|V⟩₁|H⟩₂)/√2 for quantum correlation measurements

**Key Parameters:**
- pump_wavelength: 405nm
- signal_wavelength: 810nm
- hwp_angle: 22.5° for phase control
- detector_efficiency: 65%

## QuTiP Implementation

### State Init

```python
# Type-II SPDC Bell state initialization
spdc_state = (qt.tensor(qt.basis(2,0), qt.basis(2,1)) + 
              qt.tensor(qt.basis(2,1), qt.basis(2,0))).unit()
```

### Operations

```python
# Half-wave plate polarization rotation
theta_rad = np.radians(hwp_angle)
hwp_matrix = np.array([[np.cos(2*theta_rad), np.sin(2*theta_rad)],
                       [np.sin(2*theta_rad), -np.cos(2*theta_rad)]])
hwp_op_a = qt.tensor(qt.Qobj(hwp_matrix), qt.qeye(2))
hwp_state = (hwp_op_a * filtered_state).unit()
```

### Measurements

```python
# Polarization projection measurements
h_proj_a = qt.tensor(qt.projection(2, 0, 0), qt.qeye(2))  # |H⟩⟨H| ⊗ I
h_proj_b = qt.tensor(qt.qeye(2), qt.projection(2, 0, 0))  # I ⊗ |H⟩⟨H|
hh_projector = qt.tensor(qt.projection(2, 0, 0), qt.projection(2, 0, 0))
coincidence_prob = float(abs(qt.expect(hh_projector, rho_total)))
```

## How Design Maps to Code

The code correctly implements the designer's Bell state manipulation concept using proper polarization qubit operations and realistic HWP rotation matrices. The zero coincidence probability for HH detection is physically correct for the Bell state, and the high entanglement metrics validate the quantum correlation aspects. However, the simulation bypasses the actual SPDC generation process and spatial mode engineering that would be critical for experimental success.

## Identified Limitations

- Cannot model actual SPDC generation process - assumes perfect Bell state output
- No spatial mode structure or beam propagation - ignores collection efficiency
- Discrete polarization qubits vs continuous electromagnetic fields
- Perfect projective measurements vs realistic photodetection statistics
- No temporal correlations or timing jitter between photon pairs
- Ignores pump depletion, crystal acceptance angle, and phase matching bandwidth

## Recommendations

1. Verify the zero coincidence probability is intentional for the measurement basis used
2. Consider adding realistic noise models to better reflect experimental conditions
3. Implement detector efficiency and dark count effects for more realistic performance assessment

## Conclusion

✅ Simulation successfully captured the design's intended physics.
