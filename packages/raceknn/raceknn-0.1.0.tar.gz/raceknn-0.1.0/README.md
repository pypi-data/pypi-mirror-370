# RACEkNN: A Hybrid Rule-Guided k-Nearest Neighbor Classifier

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the official Python implementation for the paper: **"RACEkNN: A hybrid approach for improving the effectiveness of the k-nearest neighbor algorithm"**.

RACEkNN is a hybrid classifier that integrates kNN with **RACER** (Rule Aggregating ClassifiEr), a novel rule-based classifier. RACER generates generalized rules to identify the most relevant subset of the training data for a given test instance. This pre-selection significantly reduces the search space for kNN, leading to faster execution times and improved classification accuracy.

---

## 📖 About the Paper

**Title:** RACEkNN: A hybrid approach for improving the effectiveness of the k-nearest neighbor algorithm
**Journal:** *Knowledge-Based Systems* (Volume 301), 2024
**DOI:** [10.1016/j.knosys.2024.112357](https://doi.org/10.1016/j.knosys.2024.112357)
**Authors:** Mahdiyeh Ebrahimi, Alireza Basiri

### Abstract
> Classification is a fundamental task in data mining, involving the prediction of class labels for new data. k-Nearest Neighbors (kNN), a lazy learning algorithm, is sensitive to data distribution and suffers from high computational costs due to the requirement of finding the closest neighbors across the entire training set. Recent advancements in classification techniques have led to the development of hybrid algorithms that combine the strengths of multiple methods to address specific limitations. In response to the inherent execution time constraint of kNN and the impact of data distribution on its performance, we propose RACEkNN (Rule Aggregating ClassifiEr kNN), a hybrid solution that integrates kNN with RACER, a newly devised rule-based classifier. RACER improves predictive capability and decreases kNN’s runtime by creating more generalized rules, each encompassing a subset of training instances with similar characteristics. During prediction, a test instance is compared to these rules based on its features. By selecting the rule with the closest match, the test instance identifies the most relevant subset of training data for kNN. This significantly reduces the data kNN needs to consider, leading to faster execution times and enhanced prediction accuracy. Empirical findings demonstrate that RACEkNN outperforms kNN in terms of both runtime and accuracy. Additionally, it surpasses RACER, four well-known classifiers, and certain kNN-based methods in terms of accuracy.

---

## 🚀 Installation

To get started, clone the repository and install the required dependencies.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/mahdiyehebrahimi/RACEkNN.git](https://github.com/mahdiyehebrahimi/RACEkNN.git)
    cd RACEkNN
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

---

## 💡 Usage Example

You can use `RACEKNNClassifier` just like any other scikit-learn classifier. Here is a simple example using the "Car Evaluation" dataset included in the `Datasets/` directory.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from raceknn import RACEKNNClassifier

# Load data
df = pd.read_csv(
    "Datasets/car_evaluation.data",
    names=["buying", "maint", "doors", "persons", "lug_boot", "safety", "class"]
)
X = df.drop(columns=['class'])
y = df['class']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Initialize and fit the classifier
# alpha: RACER fitness trade-off (accuracy vs. coverage)
# k: Number of neighbors for the final kNN vote
clf = RACEKNNClassifier(alpha=0.9, k=5)
clf.fit(X_train, y_train)

# Predict and evaluate
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of RACEKNN Classifier: {accuracy:.4f}")
```
For more examples, including how to use k-fold cross-validation, see the `example.py`.

---

## 🎓 Citing This Work

If you use RACEkNN in your research, please cite our paper.

### BibTeX
```bibtex
@article{EBRAHIMI2024112357,
  title = {RACEkNN: A hybrid approach for improving the effectiveness of the k-nearest neighbor algorithm},
  journal = {Knowledge-Based Systems},
  volume = {301},
  pages = {112357},
  year = {2024},
  issn = {0950-7051},
  doi = {[https://doi.org/10.1016/j.knosys.2024.112357](https://doi.org/10.1016/j.knosys.2024.112357)},
  author = {Mahdiyeh Ebrahimi and Alireza Basiri}
}
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
