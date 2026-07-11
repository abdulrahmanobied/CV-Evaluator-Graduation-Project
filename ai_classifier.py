"""
===========================================
 AI Suitability Classifier
 A small neural network (Multi-Layer
 Perceptron) built with Scikit-learn that
 learns to classify candidate suitability
 from their scores, as an additional AI-based
 signal alongside the rule-based formula.

 Note: TensorFlow was originally planned here,
 but TensorFlow does not yet support Python 3.14
 at the time of this project. Scikit-learn's
 MLPClassifier (a genuine neural network) is
 used instead as a compatible alternative.
===========================================
"""

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

# ==========================================
# Generate synthetic training data
# (skill_score, experience_score, education_score) -> suitability label
# 0 = Not Suitable, 1 = Moderately Suitable, 2 = Highly Suitable
# ==========================================
def _generate_training_data(n_samples=2000, seed=42):
    rng = np.random.default_rng(seed)
    X = rng.uniform(0, 100, size=(n_samples, 3))  # skill, experience, education scores

    y = []
    for skill, exp, edu in X:
        final_score = (skill * 0.60) + (exp * 0.30) + (edu * 0.10)
        if final_score >= 75:
            y.append(2)  # Highly Suitable
        elif final_score >= 50:
            y.append(1)  # Moderately Suitable
        else:
            y.append(0)  # Not Suitable
    return X, np.array(y)


print("⏳ Training AI suitability classifier (small neural network)...")
_X_train, _y_train = _generate_training_data()

_scaler = StandardScaler()
_X_train_scaled = _scaler.fit_transform(_X_train)

_model = MLPClassifier(
    hidden_layer_sizes=(16, 8),   # 2 small hidden layers -> a real (if tiny) neural network
    activation="relu",
    max_iter=3000,
    random_state=42,
)
_model.fit(_X_train_scaled, _y_train)
print(f"✅ AI classifier ready! (training accuracy: {_model.score(_X_train_scaled, _y_train):.1%})")

_labels = {0: "🔴 Not Suitable", 1: "🟡 Moderately Suitable", 2: "🟢 Highly Suitable"}


def classify_suitability(skill_score, experience_score, education_score):
    """
    Returns the AI classifier's predicted suitability label and
    its confidence (probability) for that prediction.
    """
    features = np.array([[skill_score, experience_score, education_score]])
    features_scaled = _scaler.transform(features)
    prediction = _model.predict(features_scaled)[0]
    probabilities = _model.predict_proba(features_scaled)[0]
    confidence = round(float(probabilities[prediction]) * 100, 1)
    return _labels[prediction], confidence


if __name__ == "__main__":
    print("=" * 60)
    print("  AI Suitability Classifier - Test Run")
    print("=" * 60)

    test_candidates = [
        ("Ahmad Khalil", 90.0, 100.0, 100.0),
        ("Lina Youssef", 56.67, 50.0, 100.0),
        ("Sara Ibrahim", 43.33, 100.0, 100.0),
    ]

    for name, skill, exp, edu in test_candidates:
        label, confidence = classify_suitability(skill, exp, edu)
        print(f"\n{name}:")
        print(f"   Scores -> Skill: {skill}%, Experience: {exp}%, Education: {edu}%")
        print(f"   🤖 AI Classifier says: {label} (confidence: {confidence}%)")

    print("\n" + "=" * 60)