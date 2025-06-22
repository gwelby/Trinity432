import numpy as np
import matplotlib.pyplot as plt
import argparse

def generate_pattern(mode: float, grid_size: int = 500):
    """
    Generate a 2D cymatic-like pattern based on sinusoidal modes.

    mode: frequency multiplier controlling number of nodes
    grid_size: resolution of the pattern
    """
    # Create meshgrid over 0..2π
    x = np.linspace(0, 2 * np.pi, grid_size)
    y = np.linspace(0, 2 * np.pi, grid_size)
    X, Y = np.meshgrid(x, y)
    # Simple mode superposition
    Z = np.sin(mode * X) * np.sin(mode * Y)
    return Z


def plot_pattern(Z: np.ndarray, cmap: str = 'viridis'):
    """
    Plot the cymatic pattern.
    """
    plt.figure(figsize=(6, 6))
    # Zero-level contour for nodal lines
    plt.contour(Z, levels=[0], colors='black', linewidths=0.5)
    # Filled background
    plt.imshow(Z, cmap=cmap, origin='lower', extent=(0, 2*np.pi, 0, 2*np.pi))
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Prototype 2D Cymatics Visualizer (Chladni-style)"
    )
    parser.add_argument(
        '--mode', '-m', type=float, default=10.0,
        help='Mode multiplier for nodal pattern (higher -> more nodes)'
    )
    parser.add_argument(
        '--grid', '-g', type=int, default=500,
        help='Grid resolution (pixels)'
    )
    args = parser.parse_args()
    Z = generate_pattern(args.mode, args.grid)
    plot_pattern(Z)


if __name__ == '__main__':
    main()
