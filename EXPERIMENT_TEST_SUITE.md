# Quantum Experiment Design Test Suite

**Purpose**: Validate the AgenticQuantum system across different complexity levels

**Date**: November 22, 2025

---

## Tier 1: Standard Quantum Optics Experiments (Foundational)

These are textbook experiments that should work reliably:

### 1.1 Mach-Zehnder Interferometer
**Request**: "Design a Mach-Zehnder interferometer"

**Expected**:
- 2 beam splitters (50:50)
- 2 mirrors
- 1 phase shifter
- 2 detectors
- Proper path lengths
- Correct beam paths showing both arms

**Success Criteria**:
- ✅ Components correctly positioned
- ✅ Beam paths flow left-to-right
- ✅ Upper/lower arms properly labeled
- ✅ Simulation shows interference fringes
- ✅ Quality rating ≥ 8/10

---

### 1.2 Hong-Ou-Mandel (HOM) Interference
**Request**: "Design a Hong-Ou-Mandel interference setup"

**Expected**:
- SPDC source (crystal)
- Beam splitter (50:50)
- 2 single-photon detectors
- Filters/wavelength selection
- Coincidence detection

**Success Criteria**:
- ✅ Two-photon input correctly shown
- ✅ Beam splitter at center
- ✅ Detectors at outputs
- ✅ Simulation shows HOM dip
- ✅ Quality rating ≥ 8/10

---

### 1.3 Bell State Generation (SPDC)
**Request**: "Design a Bell state generator using SPDC"

**Expected**:
- Pump laser (UV/blue)
- Nonlinear crystal (BBO/PPLN)
- 2 detectors for entangled pairs
- Proper wavelength selection
- Type-II phase matching

**Success Criteria**:
- ✅ Pump wavelength appropriate (405nm, 532nm)
- ✅ Signal/idler separation shown
- ✅ Detectors at both outputs
- ✅ Simulation confirms entanglement
- ✅ Quality rating ≥ 7/10

---

### 1.4 Michelson Interferometer
**Request**: "Design a Michelson interferometer"

**Expected**:
- Beam splitter (50:50)
- 2 mirrors (one movable/piezo)
- Laser source
- Detector/screen
- Symmetric arms

**Success Criteria**:
- ✅ Beam splitter at center
- ✅ Mirrors perpendicular to arms
- ✅ One mirror has phase control
- ✅ Detector positioned correctly
- ✅ Quality rating ≥ 7/10

---

### 1.5 Quantum Eraser (Basic)
**Request**: "Design a delayed choice quantum eraser experiment"

**Expected**:
- SPDC source
- Which-path markers (polarizers/beam splitters)
- Erasure mechanism (HWP + PBS)
- Multiple detectors
- Coincidence logic

**Success Criteria**:
- ✅ Signal and idler paths identified
- ✅ Erasure mechanism present
- ✅ Detectors for both erased/not-erased cases
- ✅ Simulation shows interference recovery
- ✅ Quality rating ≥ 6/10

---

## Tier 2: Complex Quantum Optics Experiments (Advanced)

These require sophisticated understanding and precise configurations:

### 2.1 GHZ State Preparation (3-Photon)
**Request**: "Design a GHZ state generator for 3 photons"

**Expected**:
- Multiple SPDC sources OR cascaded downconversion
- Beam splitters for photon routing
- 3+ detectors
- Pump beam management
- Coincidence detection

**Success Criteria**:
- ✅ Three-photon entanglement mechanism
- ✅ Proper phase relationships
- ✅ All three photons reach detectors
- ✅ Simulation confirms GHZ correlations
- ✅ Quality rating ≥ 6/10

---

### 2.2 Quantum Teleportation Setup
**Request**: "Design a quantum teleportation experiment"

**Expected**:
- Entangled pair source (EPR)
- Bell state measurement (BSM)
- Classical communication channel
- Single-photon preparation
- Detection/verification stage

**Success Criteria**:
- ✅ EPR source generates entangled pairs
- ✅ BSM correctly implemented
- ✅ Three distinct regions: Alice, Bob, EPR source
- ✅ Simulation shows fidelity > 90%
- ✅ Quality rating ≥ 6/10

---

### 2.3 Franson Interferometer (Time-Bin Entanglement)
**Request**: "Design a Franson interferometer for time-bin entanglement"

**Expected**:
- Unbalanced Mach-Zehnder pairs
- SPDC source
- Long/short path differences
- Coincidence detection
- Timing resolution requirements

**Success Criteria**:
- ✅ Two unbalanced MZI (one for signal, one for idler)
- ✅ Path length differences specified
- ✅ Timing considerations mentioned
- ✅ Simulation shows time-bin correlations
- ✅ Quality rating ≥ 5/10

---

### 2.4 Squeezed Light Generation
**Request**: "Design a squeezed light source using optical parametric oscillation"

**Expected**:
- Pump laser
- Nonlinear crystal in cavity
- Optical cavity (high finesse)
- Homodyne detector
- Phase locking mechanism

**Success Criteria**:
- ✅ Cavity with crystal inside
- ✅ Pump beam configuration
- ✅ Homodyne detection setup
- ✅ Simulation shows squeezing > 3dB
- ✅ Quality rating ≥ 5/10

---

### 2.5 Quantum Key Distribution (BB84)
**Request**: "Design a BB84 quantum key distribution setup"

**Expected**:
- Single-photon source (attenuated laser)
- Alice's encoding (polarization/phase)
- Quantum channel (fiber/free-space)
- Bob's measurement bases
- Basis reconciliation

**Success Criteria**:
- ✅ Encoding mechanism (2 bases)
- ✅ Decoding mechanism (2 bases)
- ✅ Single-photon level operation
- ✅ Eve detection capability mentioned
- ✅ Quality rating ≥ 5/10

---

## Tier 3: Research-Level Experiments (Cutting Edge)

These push the boundaries and test creative problem-solving:

### 3.1 Boson Sampling Experiment
**Request**: "Design a 4-photon boson sampling experiment"

**Expected**:
- 4 single-photon inputs
- Programmable interferometer network
- Multiple beam splitters (integrated optics)
- High-efficiency SPADs
- Coincidence counting

**Success Criteria**:
- ✅ 4+ input modes
- ✅ Complex beam splitter network
- ✅ Multiple output detectors
- ✅ Scalability considerations
- ✅ Quality rating ≥ 4/10 (very hard!)

---

### 3.2 Continuous-Variable Quantum Teleportation
**Request**: "Design a CV quantum teleportation setup with squeezed states"

**Expected**:
- Two squeezed state sources
- EPR beam splitter
- Homodyne detections (multiple)
- Classical feedforward
- Phase-space analysis

**Success Criteria**:
- ✅ EPR state preparation
- ✅ Bell measurement with homodyne
- ✅ Feedforward mechanism
- ✅ Output verification
- ✅ Quality rating ≥ 4/10

---

### 3.3 Hyperentanglement (Polarization + Path)
**Request**: "Design hyperentangled photon source with polarization and spatial DOF"

**Expected**:
- Type-II SPDC
- Spatial mode engineering
- Polarization control (HWP, QWP)
- Multiple measurement bases
- 4D Hilbert space manipulation

**Success Criteria**:
- ✅ Entanglement in 2+ degrees of freedom
- ✅ Independent control mechanisms
- ✅ Proper measurement setups
- ✅ Simulation shows both entanglements
- ✅ Quality rating ≥ 4/10

---

### 3.4 Electromagnetically Induced Transparency (EIT)
**Request**: "Design an EIT experiment with warm atomic vapor"

**Expected**:
- Probe laser (weak)
- Coupling laser (strong)
- Atomic vapor cell (Rb-87 or Cs-133)
- Beam overlap/alignment
- Transmission measurement

**Success Criteria**:
- ✅ Two lasers with correct wavelengths
- ✅ Vapor cell specifications
- ✅ Beam configuration (copropagating or counter)
- ✅ Detection of transmission
- ✅ Quality rating ≥ 4/10

---

### 3.5 Quantum Frequency Conversion
**Request**: "Design a quantum frequency converter for telecom-to-visible photons"

**Expected**:
- Telecom photon input (1550nm)
- Strong pump laser
- Nonlinear waveguide/crystal
- Wavelength filtering
- Visible detector (600-800nm)

**Success Criteria**:
- ✅ Input at telecom wavelength
- ✅ Sum-frequency generation mechanism
- ✅ Appropriate pump wavelength
- ✅ Output wavelength calculation correct
- ✅ Quality rating ≥ 3/10

---

## Testing Procedure

### For Each Experiment:

1. **Send Request**: Input the exact request string
2. **Check Retrieval**: Does it find existing composite? (after Tier 1)
3. **Review Design**: 
   - Component count reasonable?
   - Beam paths make physical sense?
   - Upper/lower labels correct?
4. **Run Simulation**: Click "Run Simulation"
5. **Validate Results**:
   - Rating ≥ threshold?
   - Physics explanation accurate?
   - Recommendations sensible?
6. **Approve/Reject**: Add good designs to toolbox

### Success Metrics:

**System passes if**:
- ✅ Tier 1: 5/5 experiments succeed (100%)
- ✅ Tier 2: 4/5 experiments succeed (80%)
- ✅ Tier 3: 2/5 experiments succeed (40%)
- ✅ No beam path direction errors in Tier 1-2
- ✅ Toolbox correctly stores and retrieves designs
- ✅ Three-button UI works for retrieved designs

---

## Known Issues to Watch:

1. **Beam Path Direction**: Should always go left → right
2. **Upper/Lower Labeling**: High Y = upper, low Y = lower
3. **Component Numbering**: Refinement should understand "#5 and #6"
4. **Toolbox Retrieval**: Should offer Use/Improve/New buttons
5. **Simulation Fidelity**: Should simulate designer's exact setup

---

## Testing Log Template:

```
Experiment: [Name]
Date: [YYYY-MM-DD HH:MM]
Status: [ ] Pass [ ] Fail [ ] Partial

Components Generated: [count]
Beam Paths: [ ] Correct [ ] Wrong direction [ ] Missing
Simulation Rating: [X/10]
Issues Found: 
- 
- 

Notes:


```

---

## Next Steps After Testing:

1. Document all failures with screenshots
2. Prioritize fixes based on tier level
3. Re-test failed experiments after fixes
4. Expand test suite based on findings
5. Create automated test harness (future work)

