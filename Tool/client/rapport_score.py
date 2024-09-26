import os
import random
import joblib
import numpy as np
import torch
from scipy.integrate import quad
from scipy.stats import gaussian_kde
from sentence_transformers import SentenceTransformer


class RapportScore:
    def __init__(self, min_words=None, overlap=None):
        # Load saved parameters
        saved_params = self.load_saved_parameters()

        # Determine which parameters to use
        if min_words is not None and overlap is not None:
            self.min_words, self.overlap = min_words, overlap
            print(f"Using user-provided parameters: min_words={self.min_words}, overlap={self.overlap}")
        elif saved_params:
            self.min_words, self.overlap = saved_params
            print(f"Loaded saved parameters: min_words={self.min_words}, overlap={self.overlap}")
        else:
            self.min_words, self.overlap = 7, 1  # Default values
            print(f"Using default parameters: min_words={self.min_words}, overlap={self.overlap}")

        # Load the model and threshold
        model_dict = joblib.load('D:\\HCI_Research\\GenderTool\\Tool\\client\\rapport_classifier.joblib')
        self.svm_model = model_dict['model']
        self.threshold = model_dict['threshold']

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').to(self.device)

        # Determine if tuning is needed
        self.tune_needed = not (saved_params or (min_words is not None and overlap is not None))
        if self.tune_needed:
            self.best_params, self.best_separation = self.tune_parameters()
            self.save_best_params(self.best_params, self.best_separation)
            self.min_words, self.overlap = self.best_params
            print(f"Tuning completed. Best parameters: min_words={self.min_words}, overlap={self.overlap}")
            print(f"Best Separation: {self.best_separation}")

    def load_saved_parameters(self):
        if os.path.isfile('D:\\HCI_Research\\GenderTool\\Tool\\client\\rapport_classifier.joblib'):
            model_dict = joblib.load('D:\\HCI_Research\\GenderTool\\Tool\\client\\rapport_classifier.joblib')
            if 'best_separation' in model_dict:
                return model_dict['best_params']
        return None

    def save_best_params(self, best_params, best_separation):
        model_dict = joblib.load('D:\\HCI_Research\\GenderTool\\Tool\\client\\rapport_classifier.joblib')
        model_dict['best_params'] = best_params
        model_dict['best_separation'] = best_separation
        joblib.dump(model_dict, 'rapport_classifier.joblib')
        print("Best parameters saved to rapport_classifier.joblib.")

    def aggregate_speech_events_sliding_window(self, data):
        aggregated_speeches = []
        current_speech = []

        for entry in data:
            if entry['event'] == 'speech' and 'transcription' in entry:
                words = entry['transcription'].split()
                current_speech.extend(words)

                while len(current_speech) >= self.min_words:
                    aggregated_speeches.append(' '.join(current_speech[:self.min_words]))
                    current_speech = current_speech[self.overlap:]

        if current_speech:
            aggregated_speeches.append(' '.join(current_speech))

        return aggregated_speeches

    def predict_rapport(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        decision_scores = self.svm_model.decision_function(embeddings)
        probabilities = 1 / (1 + np.exp(-decision_scores))
        return probabilities

    def rapport_score(self, utterances):
        text = self.aggregate_speech_events_sliding_window(utterances)
        if len(text) > 0:
            probabilities = self.predict_rapport(text)
            return 1 - probabilities.mean()  # Higher value indicates more rapport
        else:
            return 0.5  # Neutral score if no text

    def __call__(self, utterances):
        return self.rapport_score(utterances)

    def objective(self, min_words, overlap):
        self.min_words = min_words
        self.overlap = overlap

        rapport_scores = [self.rapport_score(utterances) for utterances in self.rapport_data]
        non_rapport_scores = [self.rapport_score(utterances) for utterances in self.non_rapport_data]

        # Create KDE for both distributions
        kde_rapport = gaussian_kde(rapport_scores)
        kde_non_rapport = gaussian_kde(non_rapport_scores)

        # Define the KL divergence integrand
        def kl_integrand(x):
            epsilon = 1e-10  # Small value to prevent division by zero
            p = kde_rapport(x) + epsilon
            q = kde_non_rapport(x) + epsilon
            return np.where(p > epsilon, p * np.log(np.clip(p / q, epsilon, None)), 0)

        # Calculate KL divergence
        kl_divergence, _ = quad(kl_integrand, 0, 1)

        return -kl_divergence  # We negate because gp_minimize minimizes the objective

    def tune_parameters(self):
        from skopt import gp_minimize
        from skopt.space import Integer
        from skopt.utils import use_named_args
        self.rapport_data = load_and_convert_to_utterances('D:\\HCI_Research\\GenderTool\\Tool\\client\\rapport_examples.txt')
        self.non_rapport_data = load_and_convert_to_utterances('D:\\HCI_Research\\GenderTool\\Tool\\client\\generated_examples.txt')

        space = [
            Integer(3, 20, name='min_words'),
            Integer(1, 10, name='overlap')
        ]

        @use_named_args(space)
        def objective_wrapper(min_words, overlap):
            if overlap >= min_words:
                return 0  # Invalid combination
            return self.objective(min_words, overlap)

        result = gp_minimize(
            func=objective_wrapper,
            dimensions=space,
            n_calls=50,  # Number of evaluations
            n_random_starts=10,  # Number of random evaluations before starting the optimization
            random_state=42
        )

        best_min_words, best_overlap = result.x
        best_separation = -result.fun  # Remember to negate back

        return (best_min_words, best_overlap), best_separation

def load_and_convert_to_utterances(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines()

    all_utterances = []
    for line in lines:
        utterances = []
        words = line.strip().split()
        start_time = 0
        while words:
            chunk_size = random.randint(3, 7)  # Randomly choose 3-7 words per utterance
            chunk = words[:chunk_size]
            end_time = start_time + len(chunk) * 0.5  # Assume 0.5 seconds per word
            utterances.append({
                "start_timestamp": start_time,
                "end_timestamp": end_time,
                "event": "speech",
                "transcription": " ".join(chunk)
            })
            words = words[chunk_size:]
            start_time = end_time
        all_utterances.append(utterances)

    return all_utterances

# Usage
rapport_scorer = RapportScore()