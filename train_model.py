import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    train_test_split,
    cross_val_score
)

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import RandomForestClassifier

from sklearn.naive_bayes import MultinomialNB

from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


# ============================================
# LOAD DATASET
# ============================================

df = pd.read_csv(
    "Security Vulnerabilities.csv"
)

# ============================================
# CLEAN DATA
# ============================================

df = df.dropna(subset=["Title", "Summary", "Severity"])

# CREATE REVIEW COLUMN

df["review"] = (
    df["Title"].astype(str)
    + " "
    + df["Summary"].astype(str)
)

# ============================================
# DATASET INFORMATION
# ============================================

print("\n===== DATASET SAMPLE =====\n")

print(df.head())

print("\n===== DATASET SHAPE =====\n")

print(df.shape)

print("\n===== COLUMN NAMES =====\n")

print(df.columns)

print("\n===== SEVERITY DISTRIBUTION =====\n")

print(df["Severity"].value_counts())

# ============================================
# FEATURES AND LABELS
# ============================================

X = df["review"]

y = df["Severity"]

# ============================================
# TRAIN TEST SPLIT
# ============================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.3,

    random_state=42,

    stratify=y

)

# ============================================
# MODELS
# ============================================

models = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        ),

    "Naive Bayes":
        MultinomialNB(),

    "SVM":
        LinearSVC(
            class_weight="balanced"
        )

}

# ============================================
# STORE RESULTS
# ============================================

results = []

# ============================================
# TRAIN MODELS
# ============================================

for model_name, model in models.items():

    print(f"\n\n========== {model_name} ==========")

    pipeline = Pipeline([

        (
            "tfidf",

            TfidfVectorizer(

                stop_words="english",

                max_features=3000,

                ngram_range=(1, 2)

            )
        ),

        (
            "classifier",

            model
        )

    ])

    # TRAIN

    pipeline.fit(
        X_train,
        y_train
    )

    # PREDICT

    y_pred = pipeline.predict(X_test)

    # METRICS

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted"
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted"
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted"
    )

    # CROSS VALIDATION

    cv_scores = cross_val_score(

        pipeline,

        X,

        y,

        cv=5,

        scoring="f1_weighted"

    )

    # RESULTS

    print(f"\nAccuracy  : {accuracy:.4f}")

    print(f"Precision : {precision:.4f}")

    print(f"Recall    : {recall:.4f}")

    print(f"F1 Score  : {f1:.4f}")

    print("\nCross Validation Scores:\n")

    print(cv_scores)

    print(
        f"\nAverage CV Score: {cv_scores.mean():.4f}"
    )

    print("\n===== CLASSIFICATION REPORT =====\n")

    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    # CONFUSION MATRIX

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print("\n===== CONFUSION MATRIX =====\n")

    print(cm)

    # DISPLAY MATRIX

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm
    )

    disp.plot()

    plt.title(
        f"{model_name} Confusion Matrix"
    )

    plt.show()

    # SAVE RESULTS

    results.append({

        "Model": model_name,

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1 Score": f1,

        "CV Score": cv_scores.mean()

    })

# ============================================
# FINAL COMPARISON
# ============================================

results_df = pd.DataFrame(results)

print("\n\n===== FINAL MODEL COMPARISON =====\n")

print(results_df)

# SAVE CSV

results_df.to_csv(
    "model_comparison_results.csv",
    index=False
)

# ============================================
# BEST MODEL
# ============================================

best_model = results_df.loc[
    results_df["F1 Score"].idxmax()
]

print("\n===== BEST MODEL =====\n")

print(best_model)

# ============================================
# FINAL GRAPH
# ============================================

plt.figure(figsize=(12, 6))

plt.plot(
    results_df["Model"],
    results_df["Accuracy"],
    marker="o",
    label="Accuracy"
)

plt.plot(
    results_df["Model"],
    results_df["Precision"],
    marker="o",
    label="Precision"
)

plt.plot(
    results_df["Model"],
    results_df["Recall"],
    marker="o",
    label="Recall"
)

plt.plot(
    results_df["Model"],
    results_df["F1 Score"],
    marker="o",
    label="F1 Score"
)

plt.plot(
    results_df["Model"],
    results_df["CV Score"],
    marker="o",
    label="CV Score"
)

plt.title(
    "Machine Learning Model Comparison"
)

plt.xlabel("Models")

plt.ylabel("Scores")

plt.ylim(0, 1)

plt.legend()

plt.grid(True)

plt.show()

print(
    "\nResults saved to model_comparison_results.csv"
)