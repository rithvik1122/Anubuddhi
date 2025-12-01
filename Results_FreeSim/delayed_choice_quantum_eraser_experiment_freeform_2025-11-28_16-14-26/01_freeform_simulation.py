import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.ndimage import gaussian_filter1d
from dataclasses import dataclass
from typing import Tuple, List

# Physical constants and parameters
HBAR = 1.054571817e-34  # J·s
C = 299792458  # m/s

@dataclass
class ExperimentParams:
    # Laser and SPDC parameters
    pump_wavelength: float = 405e-9  # m
    signal_wavelength: float = 810e-9  # m (degenerate SPDC)
    idler_wavelength: float = 810e-9  # m
    
    # Double slit parameters
    slit_spacing: float = 500e-6  # m
    slit_width: float = 50e-6  # m
    
    # Optical path lengths (derived from positions)
    distance_to_d0: float = 2.5  # m (from double slit to D0)
    
    # Detector parameters
    detector_efficiency: float = 0.65
    dark_count_rate: float = 25  # Hz
    timing_resolution: float = 50e-12  # s
    coincidence_window: float = 2e-9  # s
    
    # Beam splitter parameters
    bs_transmittance: float = 0.5
    bs_reflectance: float = 0.5
    
    # Simulation parameters
    n_photon_pairs: int = 10000
    n_d0_positions: int = 100
    d0_scan_range: float = 10e-3  # m (scan range at D0)

class DelayedChoiceQuantumEraser:
    def __init__(self, params: ExperimentParams):
        self.params = params
        self.k_signal = 2 * np.pi / params.signal_wavelength
        self.k_idler = 2 * np.pi / params.idler_wavelength
        
        # D0 detector positions for scanning
        self.d0_positions = np.linspace(
            -params.d0_scan_range/2, 
            params.d0_scan_range/2, 
            params.n_d0_positions
        )
        
        # Precompute signal propagation for both slits
        self._precompute_signal_propagation()
        
        # Initialize coincidence counters
        self.reset_counters()
    
    def _precompute_signal_propagation(self):
        """Precompute signal photon amplitudes for both slits"""
        d = self.params.slit_spacing
        L = self.params.distance_to_d0
        k = self.k_signal
        w = self.params.slit_width
        
        y_a = d / 2
        y_b = -d / 2
        
        # Store complex amplitudes
        self.signal_amp_a = np.zeros(len(self.d0_positions), dtype=complex)
        self.signal_amp_b = np.zeros(len(self.d0_positions), dtype=complex)
        
        for i, y_d0 in enumerate(self.d0_positions):
            # Distance from each slit to detector position
            r_a = np.sqrt(L**2 + (y_d0 - y_a)**2)
            r_b = np.sqrt(L**2 + (y_d0 - y_b)**2)
            
            # Phase from propagation
            phase_a = k * r_a
            phase_b = k * r_b
            
            # Single-slit diffraction envelope
            theta_a = np.arctan((y_d0 - y_a) / L)
            theta_b = np.arctan((y_d0 - y_b) / L)
            
            beta_a = k * w * np.sin(theta_a) / 2
            beta_b = k * w * np.sin(theta_b) / 2
            
            if np.abs(beta_a) < 1e-10:
                sinc_a = 1.0
            else:
                sinc_a = np.sin(beta_a) / beta_a
                
            if np.abs(beta_b) < 1e-10:
                sinc_b = 1.0
            else:
                sinc_b = np.sin(beta_b) / beta_b
            
            # Complex amplitude with diffraction envelope
            self.signal_amp_a[i] = (sinc_a / np.sqrt(r_a)) * np.exp(1j * phase_a)
            self.signal_amp_b[i] = (sinc_b / np.sqrt(r_b)) * np.exp(1j * phase_b)
        
        # Normalize amplitudes
        norm_a = np.sqrt(np.sum(np.abs(self.signal_amp_a)**2))
        norm_b = np.sqrt(np.sum(np.abs(self.signal_amp_b)**2))
        
        self.signal_amp_a /= norm_a
        self.signal_amp_b /= norm_b
        
        # Convert to probabilities for which-path cases
        self.signal_prob_a = np.abs(self.signal_amp_a)**2
        self.signal_prob_b = np.abs(self.signal_amp_b)**2
        
        # Renormalize probabilities
        self.signal_prob_a /= np.sum(self.signal_prob_a)
        self.signal_prob_b /= np.sum(self.signal_prob_b)
        
        # Compute interference patterns for erased cases
        # D3: constructive combination (0 phase difference at eraser)
        amp_d3 = (self.signal_amp_a + self.signal_amp_b) / np.sqrt(2)
        self.signal_prob_d3 = np.abs(amp_d3)**2
        self.signal_prob_d3 /= np.sum(self.signal_prob_d3)
        
        # D4: destructive combination (π phase difference at eraser)
        amp_d4 = (self.signal_amp_a - self.signal_amp_b) / np.sqrt(2)
        self.signal_prob_d4 = np.abs(amp_d4)**2
        self.signal_prob_d4 /= np.sum(self.signal_prob_d4)
    
    def reset_counters(self):
        """Reset all coincidence counters"""
        n_pos = self.params.n_d0_positions
        self.counts_d0_d1 = np.zeros(n_pos)
        self.counts_d0_d2 = np.zeros(n_pos)
        self.counts_d0_d3 = np.zeros(n_pos)
        self.counts_d0_d4 = np.zeros(n_pos)
        self.counts_d0_total = np.zeros(n_pos)
    
    def generate_entangled_pair(self) -> str:
        """Generate which-slit information for entangled pair"""
        return 'A' if np.random.rand() < 0.5 else 'B'
    
    def simulate_photon_pair(self):
        """Simulate one entangled photon pair through the entire setup"""
        # Generate entangled pair - which-slit info encoded in idler path
        which_slit = self.generate_entangled_pair()
        
        # Determine idler detection outcome based on which slit
        t = self.params.bs_transmittance
        r = self.params.bs_reflectance
        eff = self.params.detector_efficiency
        
        # Idler detection probabilities
        if which_slit == 'A':
            # Slit A: transmitted through BS_A goes to D1
            prob_d1 = t * eff
            prob_d2 = 0  # Cannot reach D2 from slit A
            # Reflected from BS_A, then through eraser BS
            prob_d3 = r * 0.5 * eff
            prob_d4 = r * 0.5 * eff
        else:  # which_slit == 'B'
            # Slit B: transmitted through BS_B goes to D2
            prob_d1 = 0  # Cannot reach D1 from slit B
            prob_d2 = t * eff
            # Reflected from BS_B, then through eraser BS
            prob_d3 = r * 0.5 * eff
            prob_d4 = r * 0.5 * eff
        
        total_prob = prob_d1 + prob_d2 + prob_d3 + prob_d4
        
        # Check if idler is detected at all
        if np.random.rand() > total_prob:
            return
        
        # Determine which idler detector fires
        rand = np.random.rand() * total_prob
        
        if rand < prob_d1:
            idler_detector = 'D1'
            signal_prob_dist = self.signal_prob_a  # Which-path A known
        elif rand < prob_d1 + prob_d2:
            idler_detector = 'D2'
            signal_prob_dist = self.signal_prob_b  # Which-path B known
        elif rand < prob_d1 + prob_d2 + prob_d3:
            idler_detector = 'D3'
            signal_prob_dist = self.signal_prob_d3  # Which-path erased, interference
        else:
            idler_detector = 'D4'
            signal_prob_dist = self.signal_prob_d4  # Which-path erased, interference (π phase shift)
        
        # Detect signal photon at D0 according to appropriate distribution
        d0_index = np.random.choice(len(self.d0_positions), p=signal_prob_dist)
        
        # Apply detector efficiency for signal
        if np.random.rand() > self.params.detector_efficiency:
            return
        
        # Record coincidence
        self.counts_d0_total[d0_index] += 1
        
        if idler_detector == 'D1':
            self.counts_d0_d1[d0_index] += 1
        elif idler_detector == 'D2':
            self.counts_d0_d2[d0_index] += 1
        elif idler_detector == 'D3':
            self.counts_d0_d3[d0_index] += 1
        else:  # D4
            self.counts_d0_d4[d0_index] += 1
    
    def run_simulation(self):
        """Run full simulation of delayed choice quantum eraser"""
        print("="*70)
        print("DELAYED CHOICE QUANTUM ERASER SIMULATION")
        print("="*70)
        print(f"\nSimulating {self.params.n_photon_pairs} entangled photon pairs...")
        
        # Run simulation
        for i in range(self.params.n_photon_pairs):
            self.simulate_photon_pair()
            
            if (i + 1) % 2000 == 0:
                print(f"  Processed {i+1}/{self.params.n_photon_pairs} pairs...")
        
        print(f"\nSimulation complete!")
        self.analyze_results()
    
    def calculate_visibility(self, counts: np.ndarray) -> float:
        """Calculate interference visibility V = (I_max - I_min)/(I_max + I_min)"""
        if np.sum(counts) < 10:
            return 0.0
        
        smoothed = gaussian_filter1d(counts, sigma=2)
        
        I_max = np.max(smoothed)
        I_min = np.min(smoothed)
        
        if I_max + I_min == 0:
            return 0.0
        
        visibility = (I_max - I_min) / (I_max + I_min)
        return visibility
    
    def analyze_results(self):
        """Analyze and print results"""
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        
        total_d0 = np.sum(self.counts_d0_total)
        total_d0_d1 = np.sum(self.counts_d0_d1)
        total_d0_d2 = np.sum(self.counts_d0_d2)
        total_d0_d3 = np.sum(self.counts_d0_d3)
        total_d0_d4 = np.sum(self.counts_d0_d4)
        
        print(f"\nTotal Counts:")
        print(f"  D0 (signal detector): {total_d0:.0f}")
        print(f"  D0-D1 coincidences (which-path A): {total_d0_d1:.0f}")
        print(f"  D0-D2 coincidences (which-path B): {total_d0_d2:.0f}")
        print(f"  D0-D3 coincidences (erased): {total_d0_d3:.0f}")
        print(f"  D0-D4 coincidences (erased): {total_d0_d4:.0f}")
        
        vis_d1 = self.calculate_visibility(self.counts_d0_d1)
        vis_d2 = self.calculate_visibility(self.counts_d0_d2)
        vis_d3 = self.calculate_visibility(self.counts_d0_d3)
        vis_d4 = self.calculate_visibility(self.counts_d0_d4)
        vis_total = self.calculate_visibility(self.counts_d0_total)
        
        print(f"\nInterference Visibility:")
        print(f"  D0-D1 (which-path A): {vis_d1:.4f}")
        print(f"  D0-D2 (which-path B): {vis_d2:.4f}")
        print(f"  D0-D3 (erased): {vis_d3:.4f}")
        print(f"  D0-D4 (erased): {vis_d4:.4f}")
        print(f"  D0 total (no post-selection): {vis_total:.4f}")
        
        self.plot_results()
    
    def plot_results(self):
        """Plot interference patterns"""
        fig, axes = plt.subplots(3, 2, figsize=(12, 10))
        fig.suptitle('Delayed Choice Quantum Eraser - Interference Patterns', fontsize=14)
        
        x_mm = self.d0_positions * 1e3
        
        axes[0, 0].plot(x_mm, self.counts_d0_d1, 'b-', linewidth=1.5)
        axes[0, 0].set_title(f'D0-D1 Coincidences (Which-Path A)\nVisibility = {self.calculate_visibility(self.counts_d0_d1):.4f}')
        axes[0, 0].set_xlabel('D0 Position (mm)')
        axes[0, 0].set_ylabel('Coincidence Counts')
        axes[0, 0].grid(True, alpha=0.3)
        
        axes[0, 1].plot(x_mm, self.counts_d0_d2, 'r-', linewidth=1.5)
        axes[0, 1].set_title(f'D0-D2 Coincidences (Which-Path B)\nVisibility = {self.calculate_visibility(self.counts_d0_d2):.4f}')
        axes[0, 1].set_xlabel('D0 Position (mm)')
        axes[0, 1].set_ylabel('Coincidence Counts')
        axes[0, 1].grid(True, alpha=0.3)
        
        axes[1, 0].plot(x_mm, self.counts_d0_d3, 'g-', linewidth=1.5)
        axes[1, 0].set_title(f'D0-D3 Coincidences (Erased)\nVisibility = {self.calculate_visibility(self.counts_d0_d3):.4f}')
        axes[1, 0].set_xlabel('D0 Position (mm)')
        axes[1, 0].set_ylabel('Coincidence Counts')
        axes[1, 0].grid(True, alpha=0.3)
        
        axes[1, 1].plot(x_mm, self.counts_d0_d4, 'm-', linewidth=1.5)
        axes[1, 1].set_title(f'D0-D4 Coincidences (Erased)\nVisibility = {self.calculate_visibility(self.counts_d0_d4):.4f}')
        axes[1, 1].set_xlabel('D0 Position (mm)')
        axes[1, 1].set_ylabel('Coincidence Counts')
        axes[1, 1].grid(True, alpha=0.3)
        
        axes[2, 0].plot(x_mm, self.counts_d0_total, 'k-', linewidth=1.5)
        axes[2, 0].set_title(f'D0 Total (No Post-Selection)\nVisibility = {self.calculate_visibility(self.counts_d0_total):.4f}')
        axes[2, 0].set_xlabel('D0 Position (mm)')
        axes[2, 0].set_ylabel('Total Counts')
        axes[2, 0].grid(True, alpha=0.3)
        
        axes[2, 1].plot(x_mm, self.counts_d0_d3 + self.counts_d0_d4, 'g-', 
                       linewidth=1.5, label='Erased (D3+D4)', alpha=0.7)
        axes[2, 1].plot(x_mm, self.counts_d0_d1 + self.counts_d0_d2, 'b-', 
                       linewidth=1.5, label='Which-Path (D1+D2)', alpha=0.7)
        axes[2, 1].set_title('Comparison: Erased vs Which-Path')
        axes[2, 1].set_xlabel('D0 Position (mm)')
        axes[2, 1].set_ylabel('Coincidence Counts')
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('delayed_choice_quantum_eraser.png', dpi=150, bbox_inches='tight')
        print("\nPlot saved as 'delayed_choice_quantum_eraser.png'")
        plt.close()

if __name__ == "__main__":
    params = ExperimentParams()
    experiment = DelayedChoiceQuantumEraser(params)
    experiment.run_simulation()
    
    print("\nSimulation complete.")