from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Define classification algorithms
algorithms = [
    RandomForestClassifier(),
    GradientBoostingClassifier(),
    SVC(),
    LogisticRegression(max_iter=200),
    KNeighborsClassifier(),
    DecisionTreeClassifier(),
    GaussianNB(),
    MLPClassifier(max_iter=500)
]

def process_dataset(file_path):
    data = pd.read_csv(file_path)
    X = data.iloc[:, :-1]  # assuming the last column is the target
    y = data.iloc[:, -1]
    meta_data = []
    for algo in algorithms:
        algo_name = algo.__class__.__name__
        scores = cross_val_score(algo, X, y, cv=5, scoring='accuracy')
        avg_score = scores.mean()
        meta_data.append({'algorithm': algo_name, 'accuracy': avg_score})
    return meta_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File successfully uploaded')
        results = process_dataset(file_path)
        return render_template('result.html', results=results)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
