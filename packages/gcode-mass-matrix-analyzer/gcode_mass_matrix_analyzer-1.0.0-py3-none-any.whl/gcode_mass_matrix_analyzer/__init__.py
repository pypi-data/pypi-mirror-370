#!/usr/bin/env python3
"""
GCode Mass Matrix Analyzer

A Python package for extracting mass matrices from 3D printer G-code files.
Supports both regular .gcode files and zipped .gcode.zip files from slicers like BambuLab.

Features:
- Material detection and density tracking
- Multi-extruder support with proper material assignment
- G1, G2, G3 motion command parsing
- Configurable arc subdivision based on angular resolution
- Mass matrix calculation with inertia tensor
- Support for zipped G-code files

Usage:
    from gcode_mass_matrix_analyzer import GCodeMassMatrixAnalyzer, analyze_gcode_zip
    
    # Regular G-code file
    analyzer = GCodeMassMatrixAnalyzer("print.gcode")
    mass_matrix, stats = analyzer.analyze()
    
    # Zipped G-code file
    mass_matrix, stats = analyze_gcode_zip("~/print.gcode.zip")

Command line:
    python -m gcode_mass_matrix_analyzer print.gcode
    python -m gcode_mass_matrix_analyzer ~/print.gcode.zip 0.05
"""

from .analyzer import (
    GCodeMassMatrixAnalyzer,
    analyze_gcode_zip,
    print_zip_analysis_results,
    print_mass_matrix,
    MATERIAL_DENSITIES,
    MaterialProperties,
    ExtrusionSegment,
    PrintSettings
)

__version__ = "1.0.0"
__author__ = "GitHub Copilot and Boya"
__email__ = "noreply@github.com"
__description__ = "Extract mass matrices from 3D printer G-code files"

__all__ = [
    "GCodeMassMatrixAnalyzer",
    "analyze_gcode_zip", 
    "print_zip_analysis_results",
    "print_mass_matrix",
    "MATERIAL_DENSITIES",
    "MaterialProperties",
    "ExtrusionSegment",
    "PrintSettings"
]
