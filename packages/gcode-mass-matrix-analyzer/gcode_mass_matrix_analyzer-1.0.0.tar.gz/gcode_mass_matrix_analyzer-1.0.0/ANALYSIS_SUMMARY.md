# G-code Analysis Summary

## Program Capabilities

The G-code Mass Matrix Analyzer now supports:

### Motion Commands
- **G1**: Linear interpolation with extrusion
- **G2**: Clockwise circular interpolation with extrusion
- **G3**: Counterclockwise circular interpolation with extrusion

### Key Features
1. **Material Detection**: Extracts material types from BambuLab G-code headers
2. **Multi-Material Support**: Handles multiple materials (PLA, PETG, TPU, etc.)
3. **Accurate Volume Calculation**: 
   - Linear segments: Rectangular cross-section approximation
   - Arc segments: Subdivided into multiple linear segments for accuracy
4. **Mass Matrix Generation**: Matrix with inertia tensor and total mass
5. **Physical Properties**: Uses real material densities

### Analysis Results for example.gcode

```
Materials: PLA, PLA, TPU-AMS, PETG, PLA
Material densities: [1.19, 1.26, 1.26, 1.25, 1.26] g/cm³
Layer height: 0.08 mm
Object centroid: (179.59, 193.30, 7.37) mm
Total Volume: 13.607 cm³
Total mass: 16.927 g
Extrusion segments: 64,306 (includes arc segments)
```

### Mass Matrix (kg⋅m²)
```
┌─────────────────────────────────────────────────────────┐
│ 6.786622e-02  -6.610504e-03  1.598568e-04        0     │
│ -6.610504e-03  2.380038e-03  1.759431e-03        0     │
│ 1.598568e-04  1.759431e-03  6.922817e-02         0     │
│         0              0              0      0.016927   │
└─────────────────────────────────────────────────────────┘
```

### Arc Command Handling
The analyzer found and processed G2/G3 commands with extrusion parameters:
- Calculates true arc lengths using center points and radii
- Subdivides arcs into multiple linear segments for volume approximation
- Maintains accuracy for complex curved geometries

This provides a comprehensive solution for extracting mass properties from modern 3D printer G-code files that include both linear and curved extrusion paths.
