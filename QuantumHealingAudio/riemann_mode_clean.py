import re
import argparse
import os


def parse_zeros(md_path):
    """
    Parse non-trivial zeros from the RIEMANN_HYPOTHESIS_KNOW.md file;
    expects a markdown table where each row starts with '| <index> | <t>...'.
    Returns a list of floats representing the imaginary parts t.
    """
    zeros = []
    try:
        with open(md_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('|') or line.startswith('|-') or 'Zero #' in line:
                    continue
                cols = [c.strip() for c in line.strip('|').split('|')]
                if len(cols) < 2 or not cols[0].isdigit():
                    continue
                t_str = cols[1].rstrip('.').strip()
                try:
                    t_val = float(t_str)
                except ValueError:
                    continue
                zeros.append(t_val)
    except Exception:
        return []
    return zeros


def compute_intervals(zeros):
    """
    Compute successive intervals between zeros.
    Returns a list of intervals: zeros[i] - zeros[i-1]
    """
    return [round(zeros[i] - zeros[i-1], 6) for i in range(1, len(zeros))]


def main():
    parser = argparse.ArgumentParser(description="Compute Riemann zero intervals for audio scheduling")
    parser.add_argument('md_path', help='Path to RIEMANN_HYPOTHESIS_KNOW.md file')
    args = parser.parse_args()

    if not os.path.exists(args.md_path):
        print(f"File not found: {args.md_path}")
        return

    zeros = parse_zeros(args.md_path)
    if len(zeros) < 2:
        print("Not enough zeros parsed.")
        return
    intervals = compute_intervals(zeros)
    print("Imaginary parts (first 10 zeros):", zeros[:10])
    print("Intervals between successive zeros:", intervals)

    # Suggest beat frequencies (1 / interval)
    beat_freqs = [round(1.0 / dt, 3) if dt > 0 else 0 for dt in intervals]
    print("Suggested beat frequencies (Hz):", beat_freqs)

if __name__ == '__main__':
    main()
