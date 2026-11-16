"""Plot the six measured benchmark rows without committing benchmark_results.csv.

Usage after ``python -m scripts.benchmark`` and installing matplotlib:
    python -m scripts.plot_benchmark --csv benchmark_results.csv
"""
import argparse
import csv
from pathlib import Path


def read_results(path: Path) -> dict[int, dict[str, dict[str, float]]]:
    results: dict[int, dict[str, dict[str, float]]] = {}
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            n = int(row["n"])
            mode = row["mode"]
            if mode not in ("plain", "aes-gcm") or mode in results.get(n, {}):
                raise ValueError("Expected one plain and one aes-gcm row per n")
            results.setdefault(n, {})[mode] = {
                key: float(row[key]) for key in ("insert_seconds_median", "read_seconds_median")
            }
    if not results or any(set(modes) != {"plain", "aes-gcm"} for modes in results.values()):
        raise ValueError("Missing a plain or aes-gcm measurement")
    return results


def plot(results: dict, output_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    n_values = sorted(results)
    for key, title, filename in (
        ("insert_seconds_median", "INSERT median time", "benchmark_insert.png"),
        ("read_seconds_median", "SELECT median time", "benchmark_select.png"),
    ):
        fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
        for mode, label, color in (("plain", "Plaintext", "#2878b5"),
                                   ("aes-gcm", "AES-256-GCM", "#d35238")):
            values = [results[n][mode][key] for n in n_values]
            ax.plot(n_values, values, marker="o", linewidth=2.2, label=label, color=color)
            for n, value in zip(n_values, values):
                ax.annotate(f"{value:.4f}s", (n, value),
                            xytext=(5, -14 if mode == "plain" else 9),
                            textcoords="offset points", fontsize=8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        all_values = [results[n][mode][key] for n in n_values for mode in ("plain", "aes-gcm")]
        ax.set_ylim(min(all_values) / 2, max(all_values) * 1.5)
        ax.set_xticks(n_values, [f"{n:,}" for n in n_values])
        ax.set_xlabel("Number of records")
        ax.set_ylabel("Median seconds (log scale, 3 measured runs)")
        ax.set_title(title)
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend()
        fig.savefig(output_dir / filename, dpi=180)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("benchmark_results.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/figures"))
    args = parser.parse_args()
    plot(read_results(args.csv), args.output_dir)
    print(f"Wrote two benchmark charts to {args.output_dir}")


if __name__ == "__main__":
    main()
