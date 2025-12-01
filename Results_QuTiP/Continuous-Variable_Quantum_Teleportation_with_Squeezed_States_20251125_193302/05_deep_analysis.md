# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Continuous-Variable Quantum Teleportation with Squeezed States

**Timestamp:** 20251125_193302

**Quality Rating:** 2/10 (POOR)

---

## Overview

**EDUCATIONAL POST-MORTEM: CV Quantum Teleportation Simulation**

**1. WHAT THE DESIGNER WANTED:**
The designer wants to demonstrate continuous-variable (CV) quantum teleportation using squeezed light EPR entanglement. The physics goal is:
- Two OPA crystals create EPR-entangled squeezed vacuum modes with orthogonal squeezing (one squeezed in X, one in P)
- Alice performs a Bell measurement (joint homodyne detection of X and P quadratures) on the input coherent state and her EPR mode
- Classical measurement results feed forward to Bob, who applies displacement corrections
- Bob reconstructs the input state with fidelity > 0.5 (classical limit)

Key claim: "90-degree phase difference generate EPR-entangled squeezed vacuum modes with orthogonal squeezing orientations"

**2. WHAT THE CODE ACTUALLY MODELED:**
The simulation has a FUNDAMENTAL PHYSICS ERROR in EPR state generation:

**DESIGNER'S INTENT:** Two separate OPAs with 90° phase difference → orthogonal squeezing → EPR correlations
**CODE IMPLEMENTATION:** Single two-mode squeezing (TMS) operator → parallel squeezing → NOT the designer's setup

The code uses:
```python
H_tms = squeezing_r * (a.dag() * b.dag() - a * b)
S_tms = (-1j * H_tms).expm()
```

This is the **two-mode squeezing Hamiltonian**, which creates the standard EPR state used in CV teleportation papers. However, this is NOT what the designer specified! The designer wanted:
- OPA Crystal A: Creates squeezed vacuum with squeezing in one quadrature
- OPA Crystal B: Creates squeezed vacuum with 90° phase shift → squeezing in orthogonal quadrature
- These combine at "EPR BS" to create entanglement

The correct implementation would be:
```python
# OPA A: squeeze in X
S_A = qt.squeeze(cutoff_dim, squeezing_r)  # angle=0
# OPA B: squeeze in P (90° rotated)
S_B = qt.squeeze(cutoff_dim, squeezing_r * 1j)  # angle=π/2
# Combine at 50:50 BS
```

Instead, the code directly generates an ideal TMS EPR state, which is actually TOO GOOD for the designer's setup.

**3. WHAT RESULTS CAME OUT:**
- **Teleportation fidelity: 0.172** (17.2%) - TERRIBLE, far below classical limit of 0.5
- **EPR criterion: 64.05** - NOT entangled (should be < 2 for EPR)
- **EPR variances: 32.02 each** - Huge variance, indicating NO squeezing correlation
- **Expected fidelity: 0.974** vs actual 0.172 - Off by factor of 5.7×

**4. WHY THE CATASTROPHIC FAILURE:**

The simulation FAILS for multiple compounding reasons:

**REASON A: Wrong EPR State Generation**
The TMS Hamiltonian with r=1.0 should create strong EPR correlations. But look at the results:
- Var(X_A - X_B) = 32.02 (should be ~0.14 for r=1.0)
- Var(P_A + P_B) = 32.02 (should be ~0.14 for r=1.0)
- EPR criterion = 64.05 (should be ~0.28)

This is **7 times WORSE than vacuum** (vacuum has EPR criterion = 2). Something is catastrophically wrong with the state generation or measurement.

**REASON B: Operator Dimension Mismatch**
Look at the Bell measurement code:
```python
# Step 3: Combine input state with Alice's EPR mode
alice_bob_state = qt.tensor(input_state, epr_state)
```

This creates a **3-mode system**: [input_mode, alice_epr_mode, bob_epr_mode]

But then the Bell measurement BS is:
```python
a0 = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a1 = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
H_bell_bs = theta_bs * (a0.dag() * a1 + a0 * a1.dag())
```

This mixes modes 0 and 1, leaving mode 2 (Bob) untouched - **CORRECT topology**.

But then quadrature measurements:
```python
X0 = (a0 + a0.dag()) / np.sqrt(2)  # Input mode
P1 = (a1 - a1.dag()) / (1j * np.sqrt(2))  # Alice's EPR mode
```

Measuring X on mode 0 and P on mode 1 is **WRONG** for CV teleportation! The standard protocol requires:
- X measurement on the **difference** (a0 - a1)
- P measurement on the **sum** (a0 + a1)

Or equivalently, measure both quadratures on the BS output modes, not the input modes.

**REASON C: Monte Carlo Sampling is Physically Incorrect**
The code samples measurement outcomes from Gaussian distributions:
```python
x_meas = np.random.normal(x0_mean, np.sqrt(x0_var))
p_meas = np.random.normal(p1_mean, np.sqrt(p1_var))
```

This treats homodyne detection as a classical random variable, which is fundamentally wrong for quantum teleportation. Homodyne detection should:
1. Project onto quadrature eigenstates |x⟩ or |p⟩
2. Collapse the joint state conditioned on measurement outcome
3. Leave Bob with a specific quantum state (not a statistical mixture)

The code instead:
1. Computes expectation values and variances from the full state
2. Samples classical random numbers
3. Always uses the **same** Bob pre-measurement state (traced over Alice)
4. Applies displacement to this fixed state

This is like measuring a coin flip probability, then flipping a classical coin, rather than actually measuring the quantum coin.

**REASON D: Feedforward Logic**
```python
alpha_correction = gain_x * x_meas_eff + 1j * gain_p * p_meas_eff
D_bob = qt.displace(cutoff_dim, -alpha_correction)
```

The displacement is applied to Bob's **unconditional** state (always the same ptrace), not the state **conditioned on Alice's measurement**. This breaks the teleportation protocol.

**5. HONEST ASSESSMENT:**

**Can Fock-basis simulations model CV teleportation?** 
YES, in principle! QuTip can handle this. CV teleportation has been successfully simulated in Fock basis in many papers.

**Does THIS simulation do it correctly?** 
NO. Multiple critical errors:
1. Wrong EPR state generation (doesn't match designer's two-OPA setup)
2. Wrong Bell measurement quadratures (measures individual modes, not BS outputs)
3. Wrong measurement protocol (classical sampling instead of quantum projection)
4. Wrong feedforward (applies to unconditional state)

**What's the smoking gun?**
The EPR state has variance 32× worse than vacuum. For r=1.0 TMS, we expect:
- Var(X- ) = e^(-2r) = 0.135
- Var(P+) = e^(-2r) = 0.135
- EPR criterion = 0.27

Getting 64.05 means the state is essentially **uncorrelated thermal noise**, not EPR entanglement.

**Rating: 2/10** - The code runs and uses correct QuTip syntax, but fails to implement the physics correctly. The results are nonsensical (worse than classical, worse than vacuum). This simulation provides ZERO validation of the experimental design.

## Key Insight

The simulation attempts CV teleportation but implements wrong measurement operators and uses classical sampling instead of quantum conditional states, resulting in fidelity 17% (worse than classical 50%) when it should exceed 95% for these parameters.

## Design Intent

**Components:**
- OPA Crystal A: PPLN crystal pumped by 500mW laser, generates squeezed vacuum
- OPA Crystal B: PPLN crystal pumped by same laser with 90° phase shift, generates orthogonally-squeezed vacuum
- EPR BS: 50:50 beam splitter combines two squeezed modes to create EPR entanglement
- Bell Measurement BS: 50:50 beam splitter mixes input coherent state with Alice's EPR mode
- Homodyne X & P: Two homodyne detectors measure X and P quadratures of BS outputs
- Displacement EOMs: Apply feedforward corrections to Bob's mode based on Alice's results
- Output Verification: Homodyne detector confirms teleported state matches input

**Physics Goal:** Demonstrate quantum teleportation of continuous-variable coherent states using EPR-entangled squeezed light, achieving fidelity > 0.5 (classical limit) through Bell measurement and feedforward displacement

**Key Parameters:**
- Squeezing: Generated by OPA crystals with 90° phase difference
- EPR entanglement: Created by combining orthogonally-squeezed modes at beam splitter
- Bell measurement: Joint homodyne detection of X and P quadratures
- Feedforward gain: Classical correction signals sent to Bob's displacement modulators
- Target fidelity: > 0.5 to demonstrate quantum advantage

## QuTiP Implementation

### State Init

```python
# EPR state generation (WRONG - uses TMS instead of two separate OPAs)
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))

H_tms = squeezing_r * (a.dag() * b.dag() - a * b)
S_tms = (-1j * H_tms).expm()

vac_vac = qt.tensor(qt.fock(cutoff_dim, 0), qt.fock(cutoff_dim, 0))
epr_state = S_tms * vac_vac
epr_state = epr_state.unit()

# Input coherent state
input_state = qt.coherent(cutoff_dim, alpha_input)

# Combine into 3-mode system
alice_bob_state = qt.tensor(input_state, epr_state)
```

### Operations

```python
# Bell measurement beam splitter (mixes input with Alice's EPR mode)
a0 = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim), qt.qeye(cutoff_dim))
a1 = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
a2 = qt.tensor(qt.qeye(cutoff_dim), qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))

H_bell_bs = theta_bs * (a0.dag() * a1 + a0 * a1.dag())
U_bell_bs = (-1j * H_bell_bs).expm()

alice_bob_state = U_bell_bs * alice_bob_state

# Quadrature operators (WRONG - should measure BS outputs, not inputs)
X0 = (a0 + a0.dag()) / np.sqrt(2)
P0 = (a0 - a0.dag()) / (1j * np.sqrt(2))
X1 = (a1 + a1.dag()) / np.sqrt(2)
P1 = (a1 - a1.dag()) / (1j * np.sqrt(2))
```

### Measurements

```python
# Monte Carlo sampling (WRONG - treats measurement as classical random variable)
alice_bob_dm = alice_bob_state * alice_bob_state.dag()

x0_mean = float(np.real(qt.expect(X0, alice_bob_state)))
p1_mean = float(np.real(qt.expect(P1, alice_bob_state)))
x0_var = float(np.real(qt.variance(X0, alice_bob_state)))
p1_var = float(np.real(qt.variance(P1, alice_bob_state)))

for _ in range(n_samples):
    # Sample from Gaussian (not quantum projection!)
    x_meas = np.random.normal(x0_mean, np.sqrt(x0_var))
    p_meas = np.random.normal(p1_mean, np.sqrt(p1_var))
    
    x_meas_eff = np.sqrt(eta_homodyne) * x_meas
    p_meas_eff = np.sqrt(eta_homodyne) * p_meas
    
    # WRONG: Always uses same unconditional Bob state
    bob_state_pre = alice_bob_dm.ptrace(2)
    bob_state_pre = bob_state_pre / bob_state_pre.tr()
    
    # Apply displacement based on classical samples
    alpha_correction = gain_x * x_meas_eff + 1j * gain_p * p_meas_eff
    D_bob = qt.displace(cutoff_dim, -alpha_correction)
    
    bob_state_post = D_bob * bob_state_pre * D_bob.dag()
    
    fid = float(np.real(qt.fidelity(bob_state_post, target_dm)))
    fidelities.append(fid)
```

## How Design Maps to Code

**DESIGN vs CODE MISMATCH:**

| Design Element | Designer's Intent | Code Implementation | Match? |
|----------------|-------------------|---------------------|--------|
| EPR Generation | Two OPAs (A & B) with 90° phase → orthogonal squeezing → combine at BS | Single TMS operator H = r(a†b† - ab) | ❌ Wrong physics |
| Bell Measurement | Homodyne detect X and P on BS output modes | Measure X on mode 0, P on mode 1 (input modes) | ❌ Wrong quadratures |
| Measurement Protocol | Quantum projection onto |x⟩|p⟩, collapse state | Classical Gaussian sampling from expectation values | ❌ Wrong statistics |
| Feedforward | Displace Bob's conditional state based on outcomes | Displace Bob's unconditional state (ptrace) | ❌ Wrong state |
| EPR Quality | Should have Var(X-) ≈ 0.14, Var(P+) ≈ 0.14 | Actual: Var = 32.02 (230× worse!) | ❌ Catastrophic |
| Fidelity | Should exceed 0.5 (classical), expect ~0.95 for r=1 | Actual: 0.172 (worse than classical) | ❌ Total failure |

**ROOT CAUSE:** The simulation attempts to implement CV teleportation but makes fundamental errors in both the EPR state generation (wrong Hamiltonian topology) and the measurement protocol (classical sampling instead of quantum projection). The EPR variance being 32× instead of 0.14 reveals the state is essentially uncorrelated noise, not entanglement. Even if the measurement protocol were fixed, the wrong EPR generation means this doesn't validate the designer's two-OPA architecture.

## Identified Limitations

- EPR state generation uses two-mode squeezing instead of designer's two separate OPAs with 90° phase difference combined at beam splitter
- Bell measurement quadratures (X on mode 0, P on mode 1) are wrong - should measure quadratures on beam splitter output modes or difference/sum operators
- Monte Carlo sampling treats homodyne detection as classical random variable instead of quantum projection that collapses the state
- Feedforward displacement applies to unconditional Bob state (ptrace over Alice) instead of state conditioned on measurement outcomes
- EPR quality metrics show catastrophic failure (variance 32× worse than vacuum) indicating fundamental error in state generation or measurement operators
- No verification that quadrature operators are correctly defined on the 3-mode Hilbert space
- Squeezing parameter r=1.0 chosen arbitrarily without connection to designer's pump power or crystal parameters

## Recommendations

1. Fix the EPR state generation - squeezing_parameter=1.0 is producing anti-squeezing (variance ~32) instead of squeezing (should be <1). Use negative squeezing or check two-mode squeezing implementation.
2. Verify the Bell measurement and feedforward operations - the massive discrepancy between expected (0.97) and actual fidelity (0.17) indicates incorrect homodyne measurement processing or gain calculation.
3. Debug the state reconstruction at Bob's station - the extremely low purity (0.17) and sub-classical fidelity suggest the feedforward displacement is being applied with wrong sign, wrong quadrature, or wrong scaling factor.

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
