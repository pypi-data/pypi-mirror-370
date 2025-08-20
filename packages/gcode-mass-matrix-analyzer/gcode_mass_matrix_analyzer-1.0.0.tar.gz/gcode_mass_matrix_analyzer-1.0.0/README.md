# G-code Mass Matrix Analyzer

A Python package for extracting mass matrices from 3D printer G-code files, including support for zipped G-code files (.3mf) from slicers like BambuLab.

## Features

- **Material Detection**: Automatically detects material types (PLA, PETG, TPU, etc.) from G-code headers
- **Density Mapping**: Uses built-in material density database or extracts from G-code
- **Motion Analysis**: Analyzes all extrusion movements including:
  - G1: Linear moves with extrusion
  - G2: Clockwise arc moves with extrusion  
  - G3: Counterclockwise arc moves with extrusion
- **Smart Arc Subdivision**: Configurable angle-based arc subdivision
  - Small arcs (< min_arc_angle) treated as straight lines
  - Large arcs subdivided based on angular resolution for accuracy
- **Volume Calculation**: Calculates volume of each extrusion segment (linear and arc segments)
- **Multi-Material Tracking**: Tracks extruder changes and uses correct material density per segment
- **Mass Matrix Computation**: Generates mass matrix with inertia tensor and total mass
- **Usage Statistics**: Detailed breakdown of material usage by extruder
- **3mf File Support**: Handles `.gcode.3mf` files with automatic extraction and G-code detection, but you need to rename it first to `.gcode.zip`

## Installation

### From PyPI
```bash
pip install gcode-mass-matrix-analyzer
```

### From Source
```bash
git clone https://github.com/your-username/gcode-mass-matrix-analyzer
cd gcode-mass-matrix-analyzer
pip install -e .
```

## Usage

### Command Line

#### Regular G-code files
```bash
python -m gcode_mass_matrix_analyzer example.gcode
```

#### Zipped G-code files
The `.gcode.3mf` file need to be first rename to `.gcode.zip`.

```bash
python -m gcode_mass_matrix_analyzer ~/example.gcode.zip
python -m gcode_mass_matrix_analyzer ~/example.gcode.zip 0.05  # Custom arc angle
```

#### Using the command-line tool
```bash
gcode-mass-analyzer example.gcode
gcode-mass-analyzer ~/example.gcode.zip 0.05
```

### Python Script
```python
from gcode_mass_matrix_analyzer import GCodeMassMatrixAnalyzer

# Default settings (min_arc_angle = 0.1 rad ≈ 5.7°)
analyzer = GCodeMassMatrixAnalyzer("example.gcode")

# Custom angle threshold (0.05 rad ≈ 2.9°)
analyzer = GCodeMassMatrixAnalyzer("example.gcode", min_arc_angle=0.05)

mass_matrix, stats = analyzer.analyze()
print(f"Total mass: {mass_matrix[3,3]:.6f} kg")
```

### Test with Example File
```bash
python test_analyzer.py
```

## Output

The program generates:

1. **Console Output**: Detailed analysis results including:
   - Material properties detected
   - Object centroid coordinates
   - Total volume and mass
   - Mass matrix
   - Inertia tensor

2. **Saved Results**: NumPy archive file (`*_mass_matrix.npz`) containing:
   - Mass matrix array
   - Centroid coordinates
   - Total volume

## Mass Matrix Format

The mass matrix has the following structure:

```
┌─────────────────────────────┐
│  Ixx  -Ixy  -Ixz    0     │
│ -Ixy   Iyy  -Iyz    0     │
│ -Ixz  -Iyz   Izz    0     │
│   0     0     0   mass    │
└─────────────────────────────┘
```

Where:
- `Ixx`, `Iyy`, `Izz`: Moments of inertia (kg⋅m²)
- `Ixy`, `Ixz`, `Iyz`: Products of inertia (kg⋅m²)
- `mass`: Total mass (kg)

## Supported Materials

The program includes density data for common 3D printing materials:

| Material | Density (g/cm³) |
|----------|----------------|
| PLA      | 1.24           |
| PLA-CF   | 1.30           |
| PETG     | 1.27           |
| PETG-CF  | 1.35           |
| TPU      | 1.20           |
| ABS      | 1.04           |
| PA (Nylon)| 1.13          |
| PA-GF    | 1.35           |
| ASA      | 1.05           |

## Technical Details

### Volume Calculation
Each extrusion segment is modeled as a rectangular cuboid with:
- **Length**: Distance between start and end points
- **Width**: Line width (estimated from nozzle diameter × 1.2)
- **Height**: Layer height (extracted from G-code)

### Inertia Calculation
The program treats each extrusion segment as a point mass at its center and applies the parallel axis theorem to calculate moments and products of inertia about the object's centroid.

### Coordinate System
- **Origin**: Object centroid
- **Units**: 
  - Mass: kg
  - Inertia: kg⋅m²
  - Distance: mm (converted to m for inertia calculations)

## Limitations

1. **Simplified Geometry**: Treats extrusions as rectangular cross-sections
2. **Point Mass Approximation**: Each segment treated as point mass at center
3. **Single Extruder Focus**: Currently optimized for single-material analysis
4. **BambuLab Format**: Designed for BambuLab slicer G-code format
5. **Absolute Offset**: The inertia tensor is relative to the absolute coordinate of the printer, but not the object it self.
6. **Inaccurate Mass**: The mass estimation is not the same as that from the printer.
7. **Material Missalign**: If the material has the same name, it will just take the first density for estimation. This need to be fixed by reading the material mapping from config file.

## Example Output

```
Analyzing G-code file: example.gcode
Materials: ['PLA', 'PLA', 'TPU-AMS', 'PETG', 'PLA']
Material densities: [1.19, 1.26, 1.26, 1.25, 1.26] g/cm³
Layer height: 0.08 mm
Filament diameter: 1.75 mm
Object centroid: (174.875, 163.612, 12.620) mm
Total mass: 23.950 g (0.023950 kg)

Mass Matrix (kg⋅m²):
┌─────────────────────────────────────────────────────────┐
│  2.345678e-06  -1.234567e-07  -2.345678e-08        0 │
│ -1.234567e-07   3.456789e-06  -3.456789e-08        0 │
│ -2.345678e-08  -3.456789e-08   4.567890e-06        0 │
│         0               0               0    0.023950 │
└─────────────────────────────────────────────────────────┘

Total Mass: 0.023950 kg (23.950 g)
```

## Contributing

Feel free to submit issues and enhancement requests!

## Warning

This code is generated by claude with human supervision. There could still be errors besides the mentionds limitations. Please use at your own risk.