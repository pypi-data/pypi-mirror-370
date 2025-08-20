# syntaxmatrix/model_templates.py
from textwrap import dedent

def classification(df, target):
    return dedent(f"""
        # ── Auto-generated Random-Forest classifier ───────────────
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score
        import matplotlib.pyplot as plt
        import pandas as pd

        X = df.drop(columns=['{target}'])
        y = df['{target}']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        clf = RandomForestClassifier(n_estimators=300, random_state=42)
        clf.fit(X_train, y_train)

        acc = accuracy_score(y_test, clf.predict(X_test))
        print(f"Accuracy: {{acc:.2%}}")

        imp = pd.Series(clf.feature_importances_, index=X.columns).nlargest(10)[::-1]
        imp.plot(kind='barh', title='Top 10 Feature Importances')
    """)

