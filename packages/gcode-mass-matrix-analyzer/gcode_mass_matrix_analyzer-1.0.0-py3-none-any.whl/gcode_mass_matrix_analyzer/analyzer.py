#!/usr/bin/env python3
"""
G-code Mass Matrix Analyzer for BambuLab Slicer Output

This program extracts material properties and extrusion data from G-code files
to calculate the mass matrix of 3D printed objects.

Author: GitHub Copilot
"""

import numpy as np
import re
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import zipfile
import tempfile
import os
import glob


@dataclass
class MaterialProperties:
    """Properties of 3D printing materials"""
    name: str
    density: float  # g/cm³
    
    
# Material density database (g/cm³)
MATERIAL_DENSITIES = {
    'PLA': 1.24,
    'PLA-CF': 1.3,  # Carbon fiber filled PLA
    'PETG': 1.27,
    'PETG-CF': 1.35,  # Carbon fiber filled PETG
    'TPU': 1.2,
    'TPU-AMS': 1.2,  # TPU for AMS system
    'ABS': 1.04,
    'PA': 1.13,  # Nylon
    'PA-GF': 1.35,  # Glass fiber filled Nylon
    'ASA': 1.05,
}


@dataclass
class ExtrusionSegment:
    """Represents a single extrusion segment"""
    start_pos: np.ndarray  # [x, y, z]
    end_pos: np.ndarray    # [x, y, z]
    extrusion_amount: float  # mm of filament
    layer_height: float     # mm
    line_width: float       # mm (estimated from nozzle diameter)
    extruder_id: int        # Which extruder/material was used
    

@dataclass
class PrintSettings:
    """Print settings extracted from G-code"""
    layer_height: float
    filament_diameter: float
    nozzle_diameter: float
    materials: List[str]
    material_densities: List[float]
    

class GCodeMassMatrixAnalyzer:
    """Analyzes G-code files to extract mass matrix"""
    
    def __init__(self, gcode_file: str, min_arc_angle: float = 0.1, selected_materials = None):
        """
        Initialize the analyzer
        
        Args:
            gcode_file: Path to the G-code file
            min_arc_angle: Minimum arc angle (in radians) below which arcs are treated as straight lines
                          Default: 0.1 rad ≈ 5.7 degrees
            selected_materials: List of materials to include in analysis (e.g., ['PLA', 'TPU']). 
                               If None, all materials are included.
        """
        self.gcode_file = Path(gcode_file)
        self.min_arc_angle = min_arc_angle  # Minimum angle for arc subdivision
        self.max_segment_angle = 0.2  # Maximum angle per segment (radians) ≈ 11.5 degrees
        self.selected_materials = selected_materials  # Materials to include in analysis
        self.print_settings = PrintSettings(
            layer_height=0.2,
            filament_diameter=1.75,
            nozzle_diameter=0.4,
            materials=['PLA'],
            material_densities=[1.24]
        )
        self.extrusion_segments = []
        self.current_position = np.array([0.0, 0.0, 0.0])
        self.current_e = 0.0
        self.current_extruder = 0
        self.current_layer_height = 0.2  # Default
        self.in_wipe_tower = False  # Track if we're in wipe tower section
        self.in_wipe_section = False  # Track if we're in wipe section
        self.current_line_width = 0.4   # Default
        self.wipe_tower_segments = []  # Track wipe tower extrusions
        self.wipe_segments = []  # Track wipe extrusions
        
    def parse_gcode_header(self) -> PrintSettings:
        """Extract print settings from G-code header"""
        materials = []
        densities = []
        layer_height = 0.2
        filament_diameter = 1.75
        nozzle_diameter = 0.4
        
        with open(self.gcode_file, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                
                # Stop reading header after a certain point
                if line_num > 1000 or line.startswith('G'):
                    break
                    
                # Extract filament types
                if '; filament_type =' in line:
                    types_str = line.split('=')[1].strip()
                    materials = [t.strip() for t in types_str.split(';') if t.strip()]
                
                # Extract filament densities
                elif '; filament_density:' in line:
                    try:
                        densities_str = line.split(':')[1].strip()
                        densities = [float(d.strip()) for d in densities_str.split(',') if d.strip() and d.strip() != ';']
                    except (ValueError, IndexError):
                        pass
                
                # Extract layer height
                elif '; layer_height =' in line:
                    try:
                        layer_height = float(line.split('=')[1].strip())
                    except (ValueError, IndexError):
                        pass
                
                # Extract filament diameter
                elif '; filament_diameter:' in line:
                    try:
                        diameters_str = line.split(':')[1].strip()
                        diameters = [float(d.strip()) for d in diameters_str.split(',') if d.strip() and d.strip() != ';']
                        filament_diameter = diameters[0] if diameters else 1.75
                    except (ValueError, IndexError):
                        pass
                
                # Extract nozzle diameter (approximate from line width or settings)
                elif 'nozzle_diameter' in line and '=' in line:
                    try:
                        diameter_str = line.split('=')[1].strip().split(',')[0]
                        if diameter_str and not diameter_str.startswith(';'):
                            nozzle_diameter = float(diameter_str)
                    except (ValueError, IndexError):
                        pass
        
        # Use material database densities if not found in file
        if not densities and materials:
            densities = [MATERIAL_DENSITIES.get(mat, 1.24) for mat in materials]
        
        self.print_settings = PrintSettings(
            layer_height=layer_height,
            filament_diameter=filament_diameter,
            nozzle_diameter=nozzle_diameter,
            materials=materials,
            material_densities=densities
        )
        
        return self.print_settings
    
    def parse_gcode_commands(self):
        """Parse G-code commands to extract extrusion segments"""
        print("Parsing G-code commands...")
        
        with open(self.gcode_file, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                
                # Check for wipe tower and wipe section markers
                if '; WIPE_TOWER_START' in line:
                    self.in_wipe_tower = True
                elif '; WIPE_TOWER_END' in line:
                    self.in_wipe_tower = False
                elif '; WIPE_START' in line:
                    self.in_wipe_section = True
                elif '; WIPE_END' in line:
                    self.in_wipe_section = False
                
                # Skip comments and empty lines
                if not line or line.startswith(';'):
                    continue
                
                # Parse movement commands (G1, G2, G3)
                # Always update position, but only record extrusion if not in wipe sections
                if line.startswith('G1 '):
                    self._parse_g1_command(line, record_extrusion=not (self.in_wipe_tower or self.in_wipe_section))
                elif line.startswith('G2 ') or line.startswith('G3 '):
                    self._parse_arc_command(line, record_extrusion=not (self.in_wipe_tower or self.in_wipe_section))
                
                # Parse tool changes
                elif line.startswith('T'):
                    try:
                        # Extract tool number (T0, T1, T2, etc.)
                        tool_match = re.search(r'T(\d+)', line)
                        if tool_match:
                            self.current_extruder = int(tool_match.group(1))
                    except ValueError:
                        pass
                
                # Progress indicator
                if line_num % 10000 == 0:
                    print(f"Processed {line_num} lines...")
    
    def _parse_g1_command(self, command: str, record_extrusion: bool = True):
        """Parse a G1 command and extract movement and extrusion data"""
        # Extract coordinates and extrusion
        x_match = re.search(r'X([-+]?\d*\.?\d+)', command)
        y_match = re.search(r'Y([-+]?\d*\.?\d+)', command)
        z_match = re.search(r'Z([-+]?\d*\.?\d+)', command)
        e_match = re.search(r'E([-+]?\d*\.?\d+)', command)
        
        # Update current position
        new_position = self.current_position.copy()
        
        if x_match:
            new_position[0] = float(x_match.group(1))
        if y_match:
            new_position[1] = float(y_match.group(1))
        if z_match:
            new_position[2] = float(z_match.group(1))
            self.current_layer_height = self.print_settings.layer_height
        
        # Check for extrusion
        if e_match:
            new_e = float(e_match.group(1))
            extrusion_amount = new_e - self.current_e
            
            # Only record positive extrusion (printing, not retraction)
            if extrusion_amount > 0:
                segment = ExtrusionSegment(
                    start_pos=self.current_position.copy(),
                    end_pos=new_position.copy(),
                    extrusion_amount=extrusion_amount,
                    layer_height=self.current_layer_height,
                    line_width=self.current_line_width,
                    extruder_id=self.current_extruder
                )
                
                # Add to appropriate list based on current state
                if self.in_wipe_tower:
                    self.wipe_tower_segments.append(segment)
                elif self.in_wipe_section:
                    self.wipe_segments.append(segment)
                elif record_extrusion:
                    self.extrusion_segments.append(segment)
            
            # Always update E position regardless of recording
            self.current_e = new_e
        
        # Always update position regardless of extrusion recording
        self.current_position = new_position
    
    def _parse_arc_command(self, command: str, record_extrusion: bool = True):
        """Parse G2/G3 arc commands and extract movement and extrusion data"""
        # Extract coordinates, arc parameters, and extrusion
        x_match = re.search(r'X([-+]?\d*\.?\d+)', command)
        y_match = re.search(r'Y([-+]?\d*\.?\d+)', command)
        z_match = re.search(r'Z([-+]?\d*\.?\d+)', command)
        i_match = re.search(r'I([-+]?\d*\.?\d+)', command)  # X offset to arc center
        j_match = re.search(r'J([-+]?\d*\.?\d+)', command)  # Y offset to arc center
        r_match = re.search(r'R([-+]?\d*\.?\d+)', command)  # Arc radius
        e_match = re.search(r'E([-+]?\d*\.?\d+)', command)
        
        # Determine if it's G2 (clockwise) or G3 (counterclockwise)
        is_clockwise = command.startswith('G2')
        
        # Update current position
        new_position = self.current_position.copy()
        
        if x_match:
            new_position[0] = float(x_match.group(1))
        if y_match:
            new_position[1] = float(y_match.group(1))
        if z_match:
            new_position[2] = float(z_match.group(1))
            self.current_layer_height = self.print_settings.layer_height
        
        # Calculate arc length and angle for volume calculation
        arc_length, arc_angle = self._calculate_arc_length_and_angle(
            self.current_position[:2], new_position[:2], 
            i_match, j_match, r_match, is_clockwise
        )
        
        # Check for extrusion
        if e_match:
            new_e = float(e_match.group(1))
            extrusion_amount = new_e - self.current_e
            
            # Only record positive extrusion (printing, not retraction)
            if extrusion_amount > 0 and arc_length > 0:
                # Check if arc is significant enough to subdivide
                if arc_angle < self.min_arc_angle:
                    # Treat as single straight line segment
                    segment = ExtrusionSegment(
                        start_pos=self.current_position.copy(),
                        end_pos=new_position.copy(),
                        extrusion_amount=extrusion_amount,
                        layer_height=self.current_layer_height,
                        line_width=self.current_line_width,
                        extruder_id=self.current_extruder
                    )
                    
                    # Add to appropriate list based on current state
                    if self.in_wipe_tower:
                        self.wipe_tower_segments.append(segment)
                    elif self.in_wipe_section:
                        self.wipe_segments.append(segment)
                    elif record_extrusion:
                        self.extrusion_segments.append(segment)
                else:
                    # Subdivide arc based on angular resolution
                    num_segments = max(2, int(arc_angle / self.max_segment_angle))
                    
                    # Generate intermediate points along the arc
                    arc_points = self._generate_arc_points(
                        self.current_position[:2], new_position[:2],
                        i_match, j_match, r_match, is_clockwise, num_segments
                    )
                    
                    # Create segments for each part of the arc
                    segment_extrusion = extrusion_amount / num_segments
                    for i in range(len(arc_points) - 1):
                        start_3d = np.array([arc_points[i][0], arc_points[i][1], self.current_position[2]])
                        end_3d = np.array([arc_points[i+1][0], arc_points[i+1][1], new_position[2]])
                        
                        segment = ExtrusionSegment(
                            start_pos=start_3d,
                            end_pos=end_3d,
                            extrusion_amount=segment_extrusion,
                            layer_height=self.current_layer_height,
                            line_width=self.current_line_width,
                            extruder_id=self.current_extruder
                        )
                        
                        # Add to appropriate list based on current state
                        if self.in_wipe_tower:
                            self.wipe_tower_segments.append(segment)
                        elif self.in_wipe_section:
                            self.wipe_segments.append(segment)
                        elif record_extrusion:
                            self.extrusion_segments.append(segment)
            
            # Always update E position regardless of recording
            self.current_e = new_e
        
        # Always update position regardless of extrusion recording
        self.current_position = new_position
    
    def _calculate_arc_length_and_angle(self, start_xy, end_xy, i_match, j_match, r_match, is_clockwise):
        """Calculate the length and angle of an arc given start/end points and center or radius"""
        try:
            start_x, start_y = start_xy[0], start_xy[1]
            end_x, end_y = end_xy[0], end_xy[1]
            
            # Determine arc center
            if i_match and j_match:
                # Center specified by I and J offsets
                center_x = start_x + float(i_match.group(1))
                center_y = start_y + float(j_match.group(1))
                radius = math.sqrt((center_x - start_x)**2 + (center_y - start_y)**2)
            elif r_match:
                # Center calculated from radius
                radius = float(r_match.group(1))
                # Find center point (there are two possible centers, choose the one that makes a smaller arc)
                center_x, center_y = self._find_arc_center(start_x, start_y, end_x, end_y, radius, is_clockwise)
            else:
                # Cannot determine arc, treat as straight line
                straight_distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                return straight_distance, 0.0  # Zero angle for straight line
            
            # Calculate arc angle
            start_angle = math.atan2(start_y - center_y, start_x - center_x)
            end_angle = math.atan2(end_y - center_y, end_x - center_x)
            
            # Calculate angle difference considering direction
            if is_clockwise:
                if end_angle > start_angle:
                    angle_diff = start_angle + (2 * math.pi - end_angle)
                else:
                    angle_diff = start_angle - end_angle
            else:
                if start_angle > end_angle:
                    angle_diff = end_angle + (2 * math.pi - start_angle)
                else:
                    angle_diff = end_angle - start_angle
            
            # Arc length = radius * angle
            arc_length = radius * angle_diff
            return arc_length, angle_diff
            
        except (ValueError, ZeroDivisionError):
            # Fallback to straight line distance if arc calculation fails
            straight_distance = math.sqrt((end_xy[0] - start_xy[0])**2 + (end_xy[1] - start_xy[1])**2)
            return straight_distance, 0.0  # Zero angle for straight line
    
    def _find_arc_center(self, x1, y1, x2, y2, radius, is_clockwise):
        """Find the center of an arc given start/end points and radius"""
        # Midpoint between start and end
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        
        # Distance from midpoint to center
        chord_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if chord_length == 0 or chord_length > 2 * radius:
            return mx, my  # Fallback
        
        center_distance = math.sqrt(radius**2 - (chord_length / 2)**2)
        
        # Unit vector perpendicular to chord
        chord_dx = x2 - x1
        chord_dy = y2 - y1
        chord_length = math.sqrt(chord_dx**2 + chord_dy**2)
        
        if chord_length == 0:
            return mx, my
        
        perp_dx = -chord_dy / chord_length
        perp_dy = chord_dx / chord_length
        
        # Choose center based on arc direction
        if is_clockwise:
            center_x = mx - center_distance * perp_dx
            center_y = my - center_distance * perp_dy
        else:
            center_x = mx + center_distance * perp_dx
            center_y = my + center_distance * perp_dy
        
        return center_x, center_y
    
    def _generate_arc_points(self, start_xy, end_xy, i_match, j_match, r_match, is_clockwise, num_segments):
        """Generate points along an arc for approximation"""
        try:
            start_x, start_y = start_xy[0], start_xy[1]
            end_x, end_y = end_xy[0], end_xy[1]
            
            # Determine arc center
            if i_match and j_match:
                center_x = start_x + float(i_match.group(1))
                center_y = start_y + float(j_match.group(1))
                radius = math.sqrt((center_x - start_x)**2 + (center_y - start_y)**2)
            elif r_match:
                radius = float(r_match.group(1))
                center_x, center_y = self._find_arc_center(start_x, start_y, end_x, end_y, radius, is_clockwise)
            else:
                # Fallback to linear interpolation
                points = []
                for i in range(num_segments + 1):
                    t = i / num_segments
                    x = float(start_x) + t * (float(end_x) - float(start_x))
                    y = float(start_y) + t * (float(end_y) - float(start_y))
                    points.append([x, y])
                return points
            
            # Calculate angles
            start_angle = math.atan2(start_y - center_y, start_x - center_x)
            end_angle = math.atan2(end_y - center_y, end_x - center_x)
            
            # Calculate angle step
            if is_clockwise:
                if end_angle > start_angle:
                    total_angle = start_angle + (2 * math.pi - end_angle)
                    angle_step = -total_angle / num_segments
                else:
                    total_angle = start_angle - end_angle
                    angle_step = -total_angle / num_segments
            else:
                if start_angle > end_angle:
                    total_angle = end_angle + (2 * math.pi - start_angle)
                    angle_step = total_angle / num_segments
                else:
                    total_angle = end_angle - start_angle
                    angle_step = total_angle / num_segments
            
            # Generate points
            points = []
            current_angle = start_angle
            for i in range(num_segments + 1):
                if i == num_segments:
                    # Ensure we end exactly at the target point
                    points.append([end_x, end_y])
                else:
                    x = center_x + radius * math.cos(current_angle)
                    y = center_y + radius * math.sin(current_angle)
                    points.append([x, y])
                    current_angle += angle_step
            
            return points
            
        except (ValueError, ZeroDivisionError):
            # Fallback to linear interpolation
            points = []
            for i in range(num_segments + 1):
                t = i / num_segments
                x = float(start_x) + t * (float(end_x) - float(start_x))
                y = float(start_y) + t * (float(end_y) - float(start_y))
                points.append([x, y])
            return points
    
    def calculate_segment_volume(self, segment: ExtrusionSegment) -> float:
        """Calculate the volume of material in an extrusion segment"""
        # Calculate the length of the path
        path_vector = segment.end_pos - segment.start_pos
        path_length = np.linalg.norm(path_vector)
        
        if path_length == 0:
            return 0.0
        
        # Volume of extruded material (simplified as rectangular cross-section)
        # Volume = width × height × length
        volume = segment.line_width * segment.layer_height * path_length
        
        return volume
    
    def get_material_density(self, extruder_id: int) -> float:
        """Get the material density for a specific extruder"""
        if 0 <= extruder_id < len(self.print_settings.material_densities):
            return self.print_settings.material_densities[extruder_id]
        else:
            # Fallback to average density if extruder_id is out of range
            return np.mean(self.print_settings.material_densities)
    
    def calculate_segment_mass(self, segment: ExtrusionSegment) -> float:
        """Calculate the mass of material in an extrusion segment"""
        volume_mm3 = self.calculate_segment_volume(segment)
        volume_cm3 = volume_mm3 / 1000.0  # Convert mm³ to cm³
        material_density = self.get_material_density(segment.extruder_id)
        mass_g = volume_cm3 * material_density
        return mass_g
    
    def calculate_centroid(self) -> np.ndarray:
        """Calculate the centroid of all extruded material (filtered by selected materials if specified)"""
        total_mass = 0.0
        weighted_position = np.array([0.0, 0.0, 0.0])
        
        # Filter segments by selected materials if specified
        segments_to_process = []
        if self.selected_materials is not None:
            for segment in self.extrusion_segments:
                # Get material name for this extruder
                extruder_id = segment.extruder_id
                if extruder_id < len(self.print_settings.materials):
                    material_name = self.print_settings.materials[extruder_id]
                    # Check if this material is in selected materials
                    if any(selected.upper() in material_name.upper() for selected in self.selected_materials):
                        segments_to_process.append(segment)
        else:
            segments_to_process = self.extrusion_segments
        
        for segment in segments_to_process:
            # Use extruder-specific density
            mass = self.calculate_segment_mass(segment)
            
            # Center of segment
            center = (segment.start_pos + segment.end_pos) / 2.0
            
            weighted_position += mass * center
            total_mass += mass
        
        if total_mass > 0:
            return weighted_position / total_mass
        else:
            return np.array([0.0, 0.0, 0.0])
    
    def calculate_mass_matrix(self) -> np.ndarray:
        """Calculate the mass matrix of the object"""
        print("Calculating mass matrix...")
        
        # Calculate centroid
        centroid = self.calculate_centroid()
        print(f"Object centroid: ({centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f}) mm")
        
        # Initialize mass matrix components
        total_mass = 0.0
        Ixx = Iyy = Izz = 0.0  # Moments of inertia
        Ixy = Ixz = Iyz = 0.0  # Products of inertia
        
        # Use extruder-specific densities instead of average
        # Filter segments by selected materials if specified
        segments_to_process = []
        if self.selected_materials is not None:
            for segment in self.extrusion_segments:
                # Get material name for this extruder
                extruder_id = segment.extruder_id
                if extruder_id < len(self.print_settings.materials):
                    material_name = self.print_settings.materials[extruder_id]
                    # Check if this material is in selected materials
                    if any(selected.upper() in material_name.upper() for selected in self.selected_materials):
                        segments_to_process.append(segment)
        else:
            segments_to_process = self.extrusion_segments
            
        print(f"Processing {len(segments_to_process)} segments out of {len(self.extrusion_segments)} total")
        if self.selected_materials is not None:
            print(f"Selected materials: {self.selected_materials}")
        
        for segment in segments_to_process:
            mass = self.calculate_segment_mass(segment)
            
            # Center of mass of this segment relative to global centroid
            center = (segment.start_pos + segment.end_pos) / 2.0
            r = center - centroid
            
            x, y, z = r[0], r[1], r[2]
            
            # Add to total mass
            total_mass += mass
            
            # Calculate moments and products of inertia
            # For a point mass: I = m * r²
            Ixx += mass * (y*y + z*z)
            Iyy += mass * (x*x + z*z)
            Izz += mass * (x*x + y*y)
            
            Ixy += mass * x * y
            Ixz += mass * x * z
            Iyz += mass * y * z
        
        # Convert to kg and meters for standard units
        total_mass_kg = total_mass / 1000.0  # g to kg
        scale = 1e-6  # mm² to m²
        
        Ixx *= scale
        Iyy *= scale
        Izz *= scale
        Ixy *= scale
        Ixz *= scale
        Iyz *= scale
        
        # Construct mass matrix
        # Upper 3x3 is the inertia tensor, bottom-right is total mass
        mass_matrix = np.array([
            [Ixx, -Ixy, -Ixz, 0],
            [-Ixy, Iyy, -Iyz, 0],
            [-Ixz, -Iyz, Izz, 0],
            [0, 0, 0, total_mass_kg]
        ])
        
        print(f"Total mass: {total_mass:.3f} g ({total_mass_kg:.6f} kg)")
        print(f"Number of extrusion segments: {len(self.extrusion_segments)}")
        
        return mass_matrix
    
    def get_material_usage_stats(self) -> Dict:
        """Calculate material usage statistics by extruder"""
        usage_by_extruder = {}
        
        for segment in self.extrusion_segments:
            extruder_id = segment.extruder_id
            
            if extruder_id not in usage_by_extruder:
                usage_by_extruder[extruder_id] = {
                    'mass_g': 0.0,
                    'volume_cm3': 0.0,
                    'segments': 0,
                    'material_name': self.print_settings.materials[extruder_id] if extruder_id < len(self.print_settings.materials) else 'Unknown'
                }
            
            mass = self.calculate_segment_mass(segment)
            volume = self.calculate_segment_volume(segment) / 1000.0  # Convert to cm³
            
            usage_by_extruder[extruder_id]['mass_g'] += mass
            usage_by_extruder[extruder_id]['volume_cm3'] += volume
            usage_by_extruder[extruder_id]['segments'] += 1
        
        return usage_by_extruder
    
    def get_wipe_tower_usage_stats(self) -> Dict:
        """Calculate wipe tower material usage statistics by extruder"""
        usage_by_extruder = {}
        
        for segment in self.wipe_tower_segments:
            extruder_id = segment.extruder_id
            
            if extruder_id not in usage_by_extruder:
                usage_by_extruder[extruder_id] = {
                    'mass_g': 0.0,
                    'volume_cm3': 0.0,
                    'segments': 0,
                    'material_name': self.print_settings.materials[extruder_id] if extruder_id < len(self.print_settings.materials) else 'Unknown'
                }
            
            mass = self.calculate_segment_mass(segment)
            volume = self.calculate_segment_volume(segment) / 1000.0  # Convert to cm³
            
            usage_by_extruder[extruder_id]['mass_g'] += mass
            usage_by_extruder[extruder_id]['volume_cm3'] += volume
            usage_by_extruder[extruder_id]['segments'] += 1
        
        return usage_by_extruder

    def get_wipe_usage_stats(self) -> Dict:
        """Calculate wipe material usage statistics by extruder"""
        usage_by_extruder = {}
        
        for segment in self.wipe_segments:
            extruder_id = segment.extruder_id
            
            if extruder_id not in usage_by_extruder:
                usage_by_extruder[extruder_id] = {
                    'mass_g': 0.0,
                    'volume_cm3': 0.0,
                    'segments': 0,
                    'material_name': self.print_settings.materials[extruder_id] if extruder_id < len(self.print_settings.materials) else 'Unknown'
                }
            
            mass = self.calculate_segment_mass(segment)
            volume = self.calculate_segment_volume(segment) / 1000.0  # Convert to cm³
            
            usage_by_extruder[extruder_id]['mass_g'] += mass
            usage_by_extruder[extruder_id]['volume_cm3'] += volume
            usage_by_extruder[extruder_id]['segments'] += 1
        
        return usage_by_extruder

    def analyze(self) -> Tuple[np.ndarray, Dict]:
        """Main analysis function"""
        print(f"Analyzing G-code file: {self.gcode_file}")
        
        # Parse header
        settings = self.parse_gcode_header()
        print(f"Materials: {settings.materials}")
        print(f"Material densities: {settings.material_densities} g/cm³")
        print(f"Layer height: {settings.layer_height} mm")
        print(f"Filament diameter: {settings.filament_diameter} mm")
        
        # Estimate line width from nozzle diameter
        self.current_line_width = settings.nozzle_diameter * 1.2  # Typical extrusion width
        
        # Parse G-code commands
        self.parse_gcode_commands()
        
        # Calculate mass matrix
        mass_matrix = self.calculate_mass_matrix()
        
        # Calculate additional statistics
        # Filter segments by selected materials for statistics if specified
        segments_for_stats = []
        if self.selected_materials is not None:
            for segment in self.extrusion_segments:
                extruder_id = segment.extruder_id
                if extruder_id < len(self.print_settings.materials):
                    material_name = self.print_settings.materials[extruder_id]
                    if any(selected.upper() in material_name.upper() for selected in self.selected_materials):
                        segments_for_stats.append(segment)
        else:
            segments_for_stats = self.extrusion_segments
            
        total_volume = sum(self.calculate_segment_volume(seg) for seg in segments_for_stats)
        centroid = self.calculate_centroid()
        material_usage = self.get_material_usage_stats()
        wipe_tower_usage = self.get_wipe_tower_usage_stats()
        wipe_usage = self.get_wipe_usage_stats()
        
        stats = {
            'total_volume_mm3': total_volume,
            'total_volume_cm3': total_volume / 1000.0,
            'centroid_mm': centroid,
            'num_segments': len(self.extrusion_segments),
            'num_filtered_segments': len(segments_for_stats),
            'num_wipe_tower_segments': len(self.wipe_tower_segments),
            'num_wipe_segments': len(self.wipe_segments),
            'materials': settings.materials,
            'densities': settings.material_densities,
            'material_usage': material_usage,
            'wipe_tower_usage': wipe_tower_usage,
            'wipe_usage': wipe_usage,
            'selected_materials': self.selected_materials
        }
        
        return mass_matrix, stats

def print_mass_matrix(mass_matrix: np.ndarray, stats: Dict):
    """Pretty print the mass matrix and statistics"""
    print("\n" + "="*60)
    print("MASS MATRIX ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\nObject Statistics:")
    print(f"  Total Volume: {stats['total_volume_cm3']:.3f} cm³")
    print(f"  Centroid: ({stats['centroid_mm'][0]:.2f}, {stats['centroid_mm'][1]:.2f}, {stats['centroid_mm'][2]:.2f}) mm")
    print(f"  Object Extrusion Segments: {stats['num_segments']}")
    if 'num_wipe_tower_segments' in stats:
        print(f"  Wipe Tower Segments: {stats['num_wipe_tower_segments']}")
    if 'num_wipe_segments' in stats:
        print(f"  Wipe Segments: {stats['num_wipe_segments']}")
    if 'num_filtered_segments' in stats and stats['selected_materials'] is not None:
        print(f"  Filtered Segments: {stats['num_filtered_segments']} (selected materials: {', '.join(stats['selected_materials'])})")
    print(f"  Materials: {', '.join(stats['materials'])}")
    
    # Print material usage by extruder if available
    if 'material_usage' in stats:
        print(f"\nMaterial Usage by Extruder (Object Only):")
        total_mass = 0.0
        for extruder_id, usage in stats['material_usage'].items():
            print(f"  T{extruder_id} ({usage['material_name']}): {usage['mass_g']:.3f} g, {usage['volume_cm3']:.3f} cm³, {usage['segments']} segments")
            total_mass += usage['mass_g']
        print(f"  Total Object Mass: {total_mass:.3f} g")

    # Print wipe tower usage if available
    if 'wipe_tower_usage' in stats and stats['wipe_tower_usage']:
        print(f"\nWipe Tower Material Usage:")
        total_wipe_tower_mass = 0.0
        for extruder_id, usage in stats['wipe_tower_usage'].items():
            print(f"  T{extruder_id} ({usage['material_name']}): {usage['mass_g']:.3f} g, {usage['volume_cm3']:.3f} cm³, {usage['segments']} segments")
            total_wipe_tower_mass += usage['mass_g']
        print(f"  Total Wipe Tower Mass: {total_wipe_tower_mass:.3f} g")

    # Print wipe usage if available
    if 'wipe_usage' in stats and stats['wipe_usage']:
        print(f"\nWipe Material Usage:")
        total_wipe_mass = 0.0
        for extruder_id, usage in stats['wipe_usage'].items():
            print(f"  T{extruder_id} ({usage['material_name']}): {usage['mass_g']:.3f} g, {usage['volume_cm3']:.3f} cm³, {usage['segments']} segments")
            total_wipe_mass += usage['mass_g']
        print(f"  Total Wipe Mass: {total_wipe_mass:.3f} g")

    print(f"\nInertia Tensor (kg⋅m²) - Calculated about object centroid:")
    centroid = stats.get('centroid_mm', [0,0,0])
    print(f"Coordinate system: Origin at centroid ({centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f}) mm")
    print("┌─────────────────────────────────────────────────────────┐")
    for i in range(3):
        row_str = "│ "
        for j in range(3):
            row_str += f"{mass_matrix[i,j]:>12.6e}"
            if j < 2:
                row_str += "  "
        row_str += " │"
        print(row_str)
    print("└─────────────────────────────────────────────────────────┘")

    print(f"\nTotal Mass: {mass_matrix[3,3]:.6f} kg ({mass_matrix[3,3]*1000:.3f} g)")


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python gcode_mass_matrix_analyzer.py <gcode_file> [min_arc_angle] [material1,material2,...]")
        print("  python gcode_mass_matrix_analyzer.py <gcode_zip_file> [min_arc_angle] [material1,material2,...]")
        print("\nExamples:")
        print("  python gcode_mass_matrix_analyzer.py example.gcode")
        print("  python gcode_mass_matrix_analyzer.py ~/example.gcode.zip")
        print("  python gcode_mass_matrix_analyzer.py ~/example.gcode.zip 0.05")
        print("  python gcode_mass_matrix_analyzer.py example.gcode 0.1 PLA,TPU")
        print("  python gcode_mass_matrix_analyzer.py ~/example.gcode.zip 0.05 PETG")
        sys.exit(1)

    input_file = sys.argv[1]
    min_arc_angle = 0.1
    selected_materials = None
    
    # Parse optional arguments
    if len(sys.argv) >= 3:
        try:
            min_arc_angle = float(sys.argv[2])
        except ValueError:
            # If second argument is not a float, it might be materials
            selected_materials = sys.argv[2].split(',')
            
    if len(sys.argv) >= 4:
        selected_materials = sys.argv[3].split(',')
        
    if selected_materials:
        print(f"Selected materials: {selected_materials}")
    
    try:
        # Check if input is a zip file
        if input_file.lower().endswith('.zip') or input_file.lower().endswith('.gcode.zip'):
            print(f"Detected zip file format")
            mass_matrix, stats = print_zip_analysis_results(input_file, min_arc_angle, selected_materials)
            if mass_matrix is None or stats is None:
                sys.exit(1)
            
            # Save results
            zip_path = Path(input_file).expanduser()
            output_file = zip_path.stem.replace('.gcode', '') + "_mass_matrix.npz"
        else:
            print(f"Detected regular G-code file format")
            analyzer = GCodeMassMatrixAnalyzer(input_file, min_arc_angle=min_arc_angle, selected_materials=selected_materials)
            mass_matrix, stats = analyzer.analyze()
            print_mass_matrix(mass_matrix, stats)
            
            # Save results
            output_file = Path(input_file).stem + "_mass_matrix.npz"
        
        np.savez(output_file, 
                mass_matrix=mass_matrix, 
                centroid=stats['centroid_mm'],
                volume=stats['total_volume_cm3'])
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing G-code file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def analyze_gcode_zip(zip_file_path: str, min_arc_angle: float = 0.1, selected_materials = None) -> Tuple[np.ndarray, Dict]:
    """
    Analyze a zipped G-code file (.gcode.zip format)
    
    Args:
        zip_file_path: Path to the .gcode.zip file (supports ~ expansion)
        min_arc_angle: Minimum arc angle for subdivision (default: 0.1 rad ≈ 5.7°)
        selected_materials: List of materials to include in analysis (e.g., ['PLA', 'TPU'])
        
    Returns:
        Tuple of (mass_matrix, statistics_dict)
        
    Raises:
        FileNotFoundError: If zip file doesn't exist
        ValueError: If no G-code files found in Metadata folder
    """
    # Expand user home directory
    zip_path = Path(zip_file_path).expanduser().resolve()
    
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    print(f"Processing zipped G-code file: {zip_path}")
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract zip file
        print("Extracting zip file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        
        # Look for G-code files in Metadata directory
        metadata_path = temp_path / "Metadata"
        
        if not metadata_path.exists():
            # Try alternative locations
            possible_paths = [
                temp_path,  # Root of zip
                temp_path / "metadata",  # lowercase
                temp_path / "METADATA",  # uppercase
            ]
            
            for alt_path in possible_paths:
                if alt_path.exists():
                    gcode_files = list(alt_path.glob("*.gcode"))
                    if gcode_files:
                        metadata_path = alt_path
                        break
            else:
                raise ValueError(f"No Metadata directory found in zip file. Available directories: {[d.name for d in temp_path.iterdir() if d.is_dir()]}")
        
        # Find G-code files in metadata directory
        gcode_files = list(metadata_path.glob("*.gcode"))
        
        if not gcode_files:
            raise ValueError(f"No .gcode files found in {metadata_path}. Available files: {[f.name for f in metadata_path.iterdir() if f.is_file()]}")
        
        if len(gcode_files) > 1:
            print(f"Warning: Multiple G-code files found: {[f.name for f in gcode_files]}")
            print(f"Using the first one: {gcode_files[0].name}")
        
        # Analyze the first G-code file
        gcode_file = gcode_files[0]
        print(f"Analyzing G-code file: {gcode_file.name}")
        
        analyzer = GCodeMassMatrixAnalyzer(str(gcode_file), min_arc_angle=min_arc_angle, selected_materials=selected_materials)
        mass_matrix, stats = analyzer.analyze()
        
        # Add source file info to stats
        stats['source_zip'] = str(zip_path)
        stats['gcode_file'] = gcode_file.name
        
        return mass_matrix, stats


def print_zip_analysis_results(zip_file_path: str, min_arc_angle: float = 0.1, selected_materials = None):
    """
    Convenience function to analyze and print results for a zipped G-code file
    
    Args:
        zip_file_path: Path to the .gcode.zip file
        min_arc_angle: Minimum arc angle for subdivision
        selected_materials: List of materials to include in analysis
    """
    try:
        mass_matrix, stats = analyze_gcode_zip(zip_file_path, min_arc_angle, selected_materials)
        
        print(f"\n" + "="*70)
        print(f"ZIPPED G-CODE ANALYSIS RESULTS")
        print(f"="*70)
        print(f"Source zip file: {stats['source_zip']}")
        print(f"G-code file: {stats['gcode_file']}")
        
        print_mass_matrix(mass_matrix, stats)
        
        return mass_matrix, stats
        
    except Exception as e:
        print(f"Error analyzing zipped G-code file: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    main()
