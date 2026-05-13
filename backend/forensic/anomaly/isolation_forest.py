from sklearn.ensemble import IsolationForest
import numpy as np
import pickle
import os

class ForensicAnomalyDetector:
    def __init__(self):
        self.model_path = "backend/forensic/anomaly/iso_forest.pkl"
        self.clf = IsolationForest(contamination=0.1, random_state=42)
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.clf = pickle.load(f)
        else:
            # Fit on dummy data representing natural speech if no data is available
            # This is a placeholder; in a real scenario, we'd fit on a 'real speech' dataset.
            np.random.seed(42)
            dummy_data = np.random.normal(0, 1, (100, 11)) # 11 features
            self.clf.fit(dummy_data)
            self.save_model()

    def save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.clf, f)

    def predict_anomaly_score(self, feature_vector):
        """
        Predict how anomalous the feature vector is.
        Returns a score where lower is more anomalous (Isolation Forest convention)
        but we'll flip it to 0-1 risk score.
        """
        # score_samples returns opposite of anomaly score (higher is more normal)
        score = self.clf.score_samples(feature_vector.reshape(1, -1))[0]
        
        # Isolation forest scores usually range from -1 to 0 or so
        # Normalize to 0-1 (1 being high anomaly)
        risk = np.clip((0.5 - score) / 0.5, 0, 1)
        return float(risk)

    def train_on_batch(self, feature_matrix):
        """
        Update the model with new 'normal' speech data.
        """
        self.clf.fit(feature_matrix)
        self.save_model()
