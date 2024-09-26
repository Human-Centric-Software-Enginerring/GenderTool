import re
from typing import List

import joblib
import matplotlib.pyplot as plt
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sklearn.base import clone
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, auc, roc_curve, \
    make_scorer
from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM


def load_examples(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()

    # Original full lines
    full_examples = [line.strip() for line in content.split('\n') if line.strip()]

    # Split sentences
    sentence_examples = [sent.strip() for sent in re.split(r'(?<=[.!?])\s+', content) if sent.strip()]

    # Combine original lines and split sentences
    full_examples += [sent for sent in sentence_examples if sent not in full_examples]

    return full_examples

class EmbeddingGenerator:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name, trust_remote_code=True)

    def get_embeddings(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            try:
                batch_embeddings = self.model.encode(batch_texts, batch_size=batch_size, convert_to_numpy=True)
                embeddings.extend(batch_embeddings)
            except RuntimeError as e:
                if 'out of memory' in str(e):
                    print("Out of memory error, reducing batch size and retrying...")
                    torch.cuda.empty_cache()
                    smaller_batch_size = max(1, batch_size // 2)
                    embeddings.extend(self.get_embeddings(batch_texts, batch_size=smaller_batch_size))
                else:
                    raise e
        return embeddings


def plot_embeddings(embeddings, labels, predictions, model, title):
    pca = PCA(n_components=2, random_state=42)
    reduced_embeddings = pca.fit_transform(np.array(embeddings))

    plt.figure(figsize=(12, 10))

    # Create mesh grid
    xx, yy = np.meshgrid(np.linspace(reduced_embeddings[:, 0].min(), reduced_embeddings[:, 0].max(), 100),
                         np.linspace(reduced_embeddings[:, 1].min(), reduced_embeddings[:, 1].max(), 100))

    # Calculate decision function for mesh grid points
    grid = np.c_[xx.ravel(), yy.ravel()]
    grid_embeddings = pca.inverse_transform(grid)
    Z = model.decision_function(grid_embeddings).reshape(xx.shape)

    # Plot decision boundary
    plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), Z.max(), 7), cmap=plt.cm.PuOr_r, alpha=0.4)
    plt.colorbar(label='Decision Score')

    # Plot data points
    for label, marker, color in zip(['Rapport', 'Non-Rapport'], ['o', '^'], ['blue', 'red']):
        indices = [i for i, l in enumerate(labels) if l == label]
        plt.scatter(reduced_embeddings[indices, 0], reduced_embeddings[indices, 1],
                    label=label, marker=marker, s=50, alpha=0.7, color=color)

    # Plot incorrect predictions
    incorrect_indices = [i for i, (l, p) in enumerate(zip(labels, predictions)) if
                         (l == 'Rapport' and p == 1) or (l == 'Non-Rapport' and p == -1)]
    plt.scatter(reduced_embeddings[incorrect_indices, 0], reduced_embeddings[incorrect_indices, 1],
                facecolors='red', edgecolors='red', s=100, label='Incorrect', alpha=0.5, marker='X')

    plt.title(title)
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.legend()

    # Add performance metrics
    accuracy = accuracy_score([1 if l == 'Non-Rapport' else 0 for l in labels], predictions)
    plt.text(0.05, 0.95, f'Accuracy: {accuracy:.2f}', transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.show()


def print_classification_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, pos_label=1)
    recall = recall_score(y_true, y_pred, pos_label=1)
    f1 = f1_score(y_true, y_pred, pos_label=1)
    cm = confusion_matrix(y_true, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)


def save_model(model, threshold, file_path='rapport_classifier.joblib'):
    """Save the trained model and optimal threshold."""
    joblib.dump({'model': model, 'threshold': threshold}, file_path)
    print(f"Model and threshold saved to {file_path}")


def find_examples_near_boundary(embeddings, model, texts, n=20):
    decision_function = model.decision_function(embeddings)
    sorted_indices = np.argsort(np.abs(decision_function))
    return [texts[i] for i in sorted_indices[:n]]


def custom_cross_val_score(estimator, X, y, param_grid, cv=5):
    scores = []
    for params in ParameterGrid(param_grid):
        cv_scores = []
        for _ in range(cv):
            # Create a clone of the estimator with new parameters
            est = clone(estimator)
            est.set_params(**params)

            # Fit on a random subset (80%) of the non-rapport data
            X = np.array(X)
            y = np.array(y)
            n_samples = X.shape[0]
            subset_size = int(0.8 * n_samples)
            subset_indices = np.random.choice(n_samples, subset_size, replace=False)
            est.fit(X[subset_indices])

            # Predict on the held-out non-rapport data and all rapport data
            X_test = np.vstack((X[~np.isin(np.arange(n_samples), subset_indices)], y))
            y_true = np.hstack((np.ones(n_samples - subset_size), -np.ones(y.shape[0])))
            y_pred = est.predict(X_test)

            # Calculate F1 score
            cv_scores.append(f1_score(y_true, y_pred, pos_label=1))

        scores.append((np.mean(cv_scores), params))

    return scores

def main():
    non_rapport_examples = load_examples('D:\\HCI_Research\\ManaliTests\\recognition\\generated_examples.txt')
    rapport_examples = load_examples('D:\\HCI_Research\\ManaliTests\\recognition\\rapport_examples.txt')

    embedding_generator = EmbeddingGenerator()
    rapport_embeddings = embedding_generator.get_embeddings(rapport_examples)
    non_rapport_embeddings = embedding_generator.get_embeddings(non_rapport_examples)


    # Create a pipeline with scaling and OneClassSVM
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', OneClassSVM(kernel='rbf'))
    ])

    # Define parameter grid
    param_grid = {
        'svm__nu': [0.01, 0.1, 0.2, 0.3, 0.5],
        'svm__gamma': ['scale', 'auto'] + list(np.logspace(-3, 2, 6))
    }

    # Perform custom cross-validation
    scores = custom_cross_val_score(pipeline, non_rapport_embeddings, rapport_embeddings, param_grid)

    # Get the best parameters
    best_score, best_params = max(scores, key=lambda x: x[0])

    print(f"Best parameters: {best_params}")
    print(f"Best cross-validation F1 Score: {best_score:.4f}")

    # Train the final model with the best parameters
    model = clone(pipeline)
    model.set_params(**best_params)
    model.fit(non_rapport_embeddings)

    # Evaluate on the full dataset
    X = np.vstack((non_rapport_embeddings, rapport_embeddings))
    y_true = np.hstack((np.ones(len(non_rapport_embeddings)), -np.ones(len(rapport_embeddings))))
    y_pred = model.predict(X)
    final_f1 = f1_score(y_true, y_pred, pos_label=1)

    print(f"Final F1 Score on full dataset: {final_f1:.4f}")

    all_embeddings = rapport_embeddings + non_rapport_embeddings
    all_texts = rapport_examples + non_rapport_examples
    labels = ['Rapport'] * len(rapport_embeddings) + ['Non-Rapport'] * len(non_rapport_embeddings)

    # Calculate decision function scores
    decision_scores = model.decision_function(all_embeddings)

    # Prepare true labels for ROC curve calculation
    y_true = [0 if label == 'Rapport' else 1 for label in labels]

    # Calculate ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(y_true, decision_scores)
    roc_auc = auc(fpr, tpr)

    print(f"ROC AUC: {roc_auc:.4f}")

    # Find optimal threshold
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]

    print(f"Optimal threshold: {optimal_threshold:.4f}")

    # Make predictions using the optimal threshold
    predictions = (decision_scores >= optimal_threshold).astype(int)

    # Plot embeddings with new predictions
    plot_embeddings(all_embeddings, labels, predictions, model, "Embeddings Plot (Non-Rapport Training)")

    # Print classification metrics with new predictions
    print("\nClassification metrics with optimal threshold:")
    print_classification_metrics(y_true, predictions)

    # Find examples near the new decision boundary
    boundary_examples = find_examples_near_boundary(all_embeddings, model, all_texts)
    print("\nExamples near the decision boundary:")
    for i, example in enumerate(boundary_examples, 1):
        print(f"{i}. {example}")

    save_model(model, optimal_threshold)


if __name__ == '__main__':
    main()