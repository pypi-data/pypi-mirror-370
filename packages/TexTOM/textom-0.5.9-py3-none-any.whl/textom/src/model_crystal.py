import numpy as np
import re
import matplotlib.pyplot as plt

def parse_cif(file_path):
    """
    Parse a CIF file and calculate the positions of all atoms in the unit cell.
    
    Parameters:
        file_path (str): Path to the CIF file.

    Returns:
        dict: Contains lattice vectors, 
        atomic positions in fractional and Cartesian coordinates, and symmetry operations.
    """
    atom_labels = []
    atom_fractions = []
    space_group = None
    lattice_vectors = []
    symmetry_operations = []
    positions_cartesian = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Parse the CIF file line by line
        for i, line in enumerate(lines):
            # Extract space group
            if line.startswith('_space_group_IT_number'):
                space_group = int( line.split()[-1].strip("'\"") )
            
            # Extract lattice vectors
            if line.startswith('_cell_length_a'):
                a = float(line.split()[-1])
            elif line.startswith('_cell_length_b'):
                b = float(line.split()[-1])
            elif line.startswith('_cell_length_c'):
                c = float(line.split()[-1])
            elif line.startswith('_cell_angle_alpha'):
                alpha = float(line.split()[-1])
            elif line.startswith('_cell_angle_beta'):
                beta = float(line.split()[-1])
            elif line.startswith('_cell_angle_gamma'):
                gamma = float(line.split()[-1])

            # Find atomic data section
            if line.strip().startswith('loop_'):
                # Look for atomic position headers in the following lines
                headers = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('_'):
                    headers.append(lines[j].strip())
                    j += 1

                # Check if this block contains atomic positions
                if ('_atom_site_fract_x' in headers and
                        '_atom_site_fract_y' in headers and
                        '_atom_site_fract_z' in headers):
                    # Start reading data rows
                    while j < len(lines) and not lines[j].strip().startswith('loop_') and lines[j].strip():
                        split_line = lines[j].split()
                        atom_labels.append(split_line[headers.index('_atom_site_type_symbol')])  # Assume first column is atom type
                        atom_fractions.append([float(split_line[headers.index('_atom_site_fract_x')]),
                                            float(split_line[headers.index('_atom_site_fract_y')]),
                                            float(split_line[headers.index('_atom_site_fract_z')])])
                        j += 1

        # Convert lattice parameters to lattice vectors
        alpha, beta, gamma = np.radians([alpha, beta, gamma])
        lattice_vectors = [
            [a, 0, 0],
            [b * np.cos(gamma), b * np.sin(gamma), 0],
            [
                c * np.cos(beta),
                c * (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma),
                c * np.sqrt(1 - np.cos(beta) ** 2 - (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) ** 2 / np.sin(gamma) ** 2),
            ],
        ]
        lattice_vectors = np.array(lattice_vectors)

        # Extract symmetry operations
        symmetry_mode = False
        for line in lines:
            if '_space_group_symop_operation_xyz' in line:
                symmetry_mode = True
            elif symmetry_mode and line.strip() == '':
                symmetry_mode = False
            elif symmetry_mode:
                op = line.strip().strip("'")
                symmetry_operations.append(op)

        # Apply symmetry operations to fractional coordinates
        atom_fractions = np.array(atom_fractions)
        full_fractions, atom_list = [], []
        for op in symmetry_operations:
            for (frac, at) in zip(atom_fractions, atom_labels):
                full_fractions.append(apply_symmetry_operation(op, frac))
                atom_list.append(at)
        full_fractions = np.array(full_fractions)
        full_fractions = np.mod(full_fractions, 1)  # Ensure all coordinates are within [0, 1)
        full_fractions, indices = np.unique(np.squeeze(full_fractions), axis=0, return_index=True)

        # Convert fractional to Cartesian coordinates
        positions_cartesian = np.array(
            [np.dot(frac, lattice_vectors) for frac in full_fractions]
        )
        # for frac in full_fractions:
        #     cart = np.dot(frac, lattice_vectors)
        #     positions_cartesian.append(cart)

        return {
            "atom_types": atom_labels,
            "coordinates": np.array(atom_fractions),
            "lattice_vectors": lattice_vectors,
            "space_group": space_group or "Unknown",
            'symmetry_operations': symmetry_operations,
            'atom_list': np.array(atom_list)[indices],
            'fractional_positions': full_fractions,
            'cartesian_positions': positions_cartesian,
        }

    except Exception as e:
        print(f"Error parsing CIF file: {e}")
        return None

def apply_symmetry_operation(operation, position):
    """
    Apply a symmetry operation to a fractional position.

    Parameters:
        operation (str): The symmetry operation in CIF format (e.g., "x,y,z").
        position (list or np.ndarray): Fractional coordinates [x, y, z].

    Returns:
        np.ndarray: New fractional coordinates after applying the operation.
    """
    # Ensure the symmetry operation format is consistent and parse it
    operation = operation.strip().replace(' ', '')  # Remove spaces for easier parsing
    operation = operation.replace('x', '{x}').replace('y', '{y}').replace('z', '{z}')

    # Check for simple transformations (e.g., -x or x+1/2)
    operation = re.sub(r'([+-]?\d*\.\d+|\d+)', r'float("\1")', operation)  # Convert numbers to float type

    x, y, z = position
    local_dict = {'x': x, 'y': y, 'z': z}

    # Safely evaluate the operation
    try:
        new_pos = [eval(operation.format(x=x, y=y, z=z))]
        return np.array(new_pos)
    except Exception as e:
        print(f"Error applying symmetry operation: {operation}")
        raise e

"""
array([[1.3268    , 3.70216157, 4.84805619],
       [3.9804    , 5.19063843, 1.57644381],
       [3.9804    , 8.14856157, 4.78869381],
       [1.3268    , 0.74423843, 1.63580619],
       [1.3268    , 6.72562464, 5.90861265],
       [3.9804    , 2.16717536, 0.51588735],
       [3.9804    , 2.27922464, 3.72813735],
       [1.3268    , 6.61357536, 2.69636265],
       [1.3268    , 8.0124128 , 5.85593175],
       [3.9804    , 0.8803872 , 0.56856825],
       [3.9804    , 3.5660128 , 3.78081825],
       [1.3268    , 5.3267872 , 2.64368175],
       [2.43918912, 6.08356448, 5.9066853 ],
       [2.86801088, 2.80923552, 0.5178147 ],
       [2.86801088, 1.63716448, 3.7300647 ],
       [2.43918912, 7.25563552, 2.6944353 ],
       [5.09278912, 2.80923552, 0.5178147 ],
       [0.21441088, 6.08356448, 5.9066853 ],
       [0.21441088, 7.25563552, 2.6944353 ],
       [5.09278912, 1.63716448, 3.7300647 ]])
       """

def reciprocal_lattice( crystal_info, h_max=3, k_max=3, l_max=3):
    """
    Calculate reciprocal lattice points for the given crystal up to the given miller indices.
    """
    # Direct lattice vectors
    a1 = crystal_info['lattice_vectors'][0]
    a2 = crystal_info['lattice_vectors'][1]
    a3 = crystal_info['lattice_vectors'][2]
    
    # Reciprocal lattice vectors
    V = np.dot(a1, np.cross(a2, a3))  # Unit cell volume
    b1 = 2 * np.pi * np.cross(a2, a3) / V
    b2 = 2 * np.pi * np.cross(a3, a1) / V
    b3 = 2 * np.pi * np.cross(a1, a2) / V
    
    # Generate reciprocal lattice points
    h_vals = np.arange(-h_max, h_max + 1)
    k_vals = np.arange(-k_max, k_max + 1)
    l_vals = np.arange(-l_max, l_max + 1)
    
    reciprocal_points = []
    for h in h_vals:
        for k in k_vals:
            for l in l_vals:
                G = h * b1 + k * b2 + l * b3
                reciprocal_points.append(G)
    
    return np.array(reciprocal_points)

def plot_powder_pattern(reciprocal_points, energy_keV, num_bins=100):
    """Compute and plot the powder diffraction pattern (Intensity vs 2θ)."""
    wavelength = 12.398 / energy_keV  # Convert energy to wavelength (Å)
    G_magnitudes = np.linalg.norm(reciprocal_points, axis=1)  # Compute |G|
    
    # Convert |G| to 2θ using Bragg's Law: 2θ = 2 * arcsin(λG / 4π)
    theta_2 = 2 * np.arcsin(wavelength * G_magnitudes / (4 * np.pi)) * (180 / np.pi)  # Convert to degrees
    
    # Create histogram (powder diffraction pattern)
    hist, bin_edges = np.histogram(theta_2, bins=num_bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Plot powder pattern
    plt.figure(figsize=(8, 5))
    plt.plot(bin_centers, hist, '-k', lw=1.5)
    plt.xlabel('2θ (degrees)')
    plt.ylabel('Intensity (arb. units)')
    plt.title('Simulated Powder Diffraction Pattern')
    plt.grid(True)
    plt.show()


