"""Train the diagnosis classifier from the de-identified medical CSV."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "dataset" / "medical_data.csv"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "diagnosis_classifier.joblib"
DEFAULT_METRICS = PROJECT_ROOT / "models" / "diagnosis_classifier_metrics.json"
MIN_SAMPLES_PER_CLASS = 5


def load_records(dataset_path: Path) -> tuple[list[str], list[str], Counter[str]]:
    texts: list[str] = []
    labels: list[str] = []
    with dataset_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            text = (row.get("TEXT") or "").strip()
            diagnosis = (row.get("DIAGNOSIS") or "").strip()
            if text and diagnosis:
                texts.append(text)
                labels.append(diagnosis)

    counts = Counter(labels)
    keep = {label for label, count in counts.items() if count >= MIN_SAMPLES_PER_CLASS}
    filtered_texts = [text for text, label in zip(texts, labels) if label in keep]
    filtered_labels = [label for label in labels if label in keep]
    return filtered_texts, filtered_labels, counts


def train(dataset_path: Path, model_path: Path, metrics_path: Path) -> dict:
    texts, labels, all_counts = load_records(dataset_path)
    if len(set(labels)) < 2:
        raise ValueError("At least two diagnosis classes are required after filtering")

    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=100_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1_000,
                    class_weight="balanced",
                    solver="lbfgs",
                ),
            ),
        ]
    )
    model.fit(train_texts, train_labels)
    predictions = model.predict(test_texts)

    report = classification_report(
        test_labels,
        predictions,
        labels=sorted(set(labels)),
        output_dict=True,
        zero_division=0,
    )
    metrics = {
        "dataset": str(dataset_path.relative_to(PROJECT_ROOT)),
        "model": "TF-IDF word n-grams + balanced logistic regression",
        "random_state": 42,
        "minimum_samples_per_class": MIN_SAMPLES_PER_CLASS,
        "total_source_rows": sum(all_counts.values()),
        "filtered_rows": len(labels),
        "classes_used": len(set(labels)),
        "train_rows": len(train_labels),
        "test_rows": len(test_labels),
        "accuracy": accuracy_score(test_labels, predictions),
        "macro_f1": f1_score(test_labels, predictions, average="macro"),
        "weighted_f1": f1_score(test_labels, predictions, average="weighted"),
        "classification_report": report,
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path = model_path.resolve()
    metrics_path = metrics_path.resolve()
    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    args = parser.parse_args()
    metrics = train(args.dataset, args.model, args.metrics)
    print(json.dumps({key: metrics[key] for key in ["filtered_rows", "classes_used", "train_rows", "test_rows", "accuracy", "macro_f1", "weighted_f1"]}, indent=2))


if __name__ == "__main__":
    main()
