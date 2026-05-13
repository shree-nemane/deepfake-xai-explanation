import numpy as np
from sklearn.metrics import roc_auc_score, f1_score, precision_recall_curve, confusion_matrix
import matplotlib.pyplot as plt
import io
import base64

class EvaluationService:
    @staticmethod
    def calculate_metrics(y_true, y_scores, threshold=0.5):
        """
        Calculate research-grade metrics.
        """
        y_true = np.array(y_true)
        y_scores = np.array(y_scores)
        y_pred = (y_scores >= threshold).astype(int)
        
        metrics = {
            "auc": float(roc_auc_score(y_true, y_scores)),
            "f1": float(f1_score(y_true, y_pred)),
            "cm": confusion_matrix(y_true, y_pred).tolist()
        }
        
        return metrics

    @staticmethod
    def generate_calibration_curve(y_true, y_scores):
        """
        Generate calibration curve for uncertainty validation.
        """
        # Placeholder for calibration curve logic
        pass

    @staticmethod
    def plot_roc_curve(y_true, y_scores):
        """
        Generate ROC curve plot as base64.
        """
        from sklearn.metrics import roc_curve
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        
        plt.figure(figsize=(6, 4))
        plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve')
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')
