#!/usr/bin/env python3
"""Execute all project notebooks and verify LaTeX-ready outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

PROJECT_ROOT = Path(__file__).resolve().parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
RESULTS_DIR = PROJECT_ROOT / "results"

NOTEBOOKS = [
    "01_mlp_tabular.ipynb",
    "02_cnn_images.ipynb",
    "03_rnn_seq2seq.ipynb",
]

NOTEBOOK_OUTPUTS = {
    "01_mlp_tabular.ipynb": [
        RESULTS_DIR / "figures" / "mlp" / "mlp_class_distribution.png",
        RESULTS_DIR / "figures" / "mlp" / "mlp_correlation_heatmap.png",
        RESULTS_DIR / "figures" / "mlp" / "mlp_feature_boxplots.png",
        RESULTS_DIR / "figures" / "mlp" / "mlp_f1_comparison.png",
        RESULTS_DIR / "figures" / "mlp" / "mlp_custom_gaussian_curves.png",
        RESULTS_DIR / "figures" / "mlp" / "mlp_custom_gaussian_confusion_matrix.png",
        RESULTS_DIR / "tables" / "mlp" / "mlp_dataset_summary.tex",
        RESULTS_DIR / "tables" / "mlp" / "mlp_comparaison_modeles.tex",
    ],
    "02_cnn_images.ipynb": [
        RESULTS_DIR / "figures" / "cnn" / "fashion_mnist_samples.png",
        RESULTS_DIR / "figures" / "cnn" / "cnn_accuracy_comparison.png",
        RESULTS_DIR / "figures" / "cnn" / "lenet_default_curves.png",
        RESULTS_DIR / "figures" / "cnn" / "lenet_default_confusion_matrix.png",
        RESULTS_DIR / "figures" / "cnn" / "lenet_default_feature_maps_layer_1.png",
        RESULTS_DIR / "tables" / "cnn" / "cnn_manual_ops_comparison.png",
        RESULTS_DIR / "tables" / "cnn" / "cnn_manual_formula_results.tex",
        RESULTS_DIR / "tables" / "cnn" / "cnn_experiments_comparison.tex",
    ],
    "03_rnn_seq2seq.ipynb": [
        RESULTS_DIR / "figures" / "sequence" / "sequence_language_model_perplexity.png",
        RESULTS_DIR / "figures" / "sequence" / "sequence_gradient_norms.png",
        RESULTS_DIR / "figures" / "sequence" / "sequence_clipping_comparison_curves.png",
        RESULTS_DIR / "figures" / "sequence" / "seq2seq_curves.png",
        RESULTS_DIR / "tables" / "sequence" / "sequence_dataset_summary.tex",
        RESULTS_DIR / "tables" / "sequence" / "sequence_language_models_comparison.tex",
        RESULTS_DIR / "tables" / "sequence" / "sequence_gradient_clipping.tex",
        RESULTS_DIR / "tables" / "sequence" / "sequence_seq2seq_bleu.tex",
        RESULTS_DIR / "tables" / "sequence" / "sequence_translation_examples.tex",
    ],
}

EXPECTED_OUTPUTS = [path for paths in NOTEBOOK_OUTPUTS.values() for path in paths]


def execute_notebook(notebook_path: Path, timeout: int) -> None:
    print(f"\n=== Exécution : {notebook_path.name} ===")
    with notebook_path.open("r", encoding="utf-8") as handle:
        notebook = nbformat.read(handle, as_version=4)

    executor = ExecutePreprocessor(
        timeout=timeout,
        kernel_name="python3",
        allow_errors=False,
    )
    executor.preprocess(notebook, {"metadata": {"path": str(notebook_path.parent)}})
    print(f"OK — {notebook_path.name}")


def verify_outputs(notebook_names: list[str]) -> list[Path]:
    expected: list[Path] = []
    for notebook_name in notebook_names:
        expected.extend(NOTEBOOK_OUTPUTS[notebook_name])
    return [path for path in expected if not path.exists()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Exécuter les notebooks du projet Deep Learning.")
    parser.add_argument(
        "--notebook",
        choices=NOTEBOOKS,
        help="Exécuter un seul notebook (par défaut : tous).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Timeout par notebook en secondes (défaut : 3600).",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Vérifier les sorties sans exécuter les notebooks.",
    )
    args = parser.parse_args()

    selected = [args.notebook] if args.notebook else NOTEBOOKS

    if args.verify_only:
        missing = verify_outputs(selected)
        if missing:
            print("Sorties manquantes pour le rapport LaTeX :", file=sys.stderr)
            for path in missing:
                print(f"  - {path.relative_to(PROJECT_ROOT)}", file=sys.stderr)
            return 1
        total = sum(len(NOTEBOOK_OUTPUTS[name]) for name in selected)
        print(f"Toutes les sorties attendues sont présentes ({total} fichiers).")
        return 0

    for notebook_name in selected:
        notebook_path = NOTEBOOKS_DIR / notebook_name
        if not notebook_path.exists():
            print(f"Notebook introuvable : {notebook_path}", file=sys.stderr)
            return 1
        execute_notebook(notebook_path, timeout=args.timeout)

    missing = verify_outputs(selected)
    if missing:
        print("\nSorties manquantes pour le rapport LaTeX :", file=sys.stderr)
        for path in missing:
            print(f"  - {path.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        return 1

    total = sum(len(NOTEBOOK_OUTPUTS[name]) for name in selected)
    print(f"\nTous les notebooks ont été exécutés. {total} fichiers attendus par le rapport sont présents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
