#!/usr/bin/env python3
"""Test beam path normalization and splitting"""

# Test the normalization function
def _normalize_beam_path(raw):
    """Normalize beam_path to be a list of paths."""
    if not raw:
        return []
    
    if isinstance(raw, list) and raw and isinstance(raw[0], list):
        if isinstance(raw[0][0], (int, float)):
            path = raw
            paths = []
            current_path = [path[0]]
            
            for i in range(1, len(path)):
                prev_x, prev_y = path[i-1]
                curr_x, curr_y = path[i]
                distance = ((curr_x - prev_x)**2 + (curr_y - prev_y)**2)**0.5
                
                if distance > 3.0:
                    paths.append(current_path)
                    current_path = [path[i]]
                else:
                    current_path.append(path[i])
            
            if current_path:
                paths.append(current_path)
            
            return paths if len(paths) > 1 else [path]
        else:
            return raw
    
    return []

# Mach-Zehnder beam path from LLM
mz_path = [
    [1.0, 3.0],   # Laser
    [3.0, 3.0],   # Input BS
    [3.0, 4.5],   # Upper arm
    [5.0, 4.5],   
    [6.0, 4.5],   
    [7.0, 3.0],   # Output BS
    [9.0, 4.0],   # Detector A
    [3.0, 3.0],   # JUMP back (distance ~6.3)
    [3.0, 1.5],   # Lower arm
    [5.0, 1.5],   
    [7.0, 3.0],   # Output BS
    [9.0, 2.0]    # Detector B
]

result = _normalize_beam_path(mz_path)

print(f"Original path: {len(mz_path)} points")
print(f"Split into: {len(result)} paths\n")

for i, path in enumerate(result):
    print(f"Path {i+1}: {len(path)} points")
    print(f"  Start: {path[0]}")
    print(f"  End: {path[-1]}")
    print(f"  Full: {path}\n")

# Calculate the jump distance
jump_idx = 6  # From [9,4] to [3,3]
p1 = mz_path[jump_idx]
p2 = mz_path[jump_idx + 1]
dist = ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5
print(f"Jump distance from {p1} to {p2}: {dist:.2f} units")
print(f"Threshold: 3.0 units")
print(f"Should split: {dist > 3.0}")
