from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)
# Używamy nazwy serwisu z docker-compose zamiast localhost
API_URL = "http://api:8000/api"

@app.route('/')
def index():
    response = requests.get(f"{API_URL}/keywords")
    keywords = response.json()
    return render_template('index.html', keywords=keywords)

@app.route('/add', methods=['POST'])
def add_keyword():
    data = {
        "keyword": request.form['keyword'],
        "flowise_id": request.form['flowise_id'],
        "description": request.form['description']
    }
    requests.post(f"{API_URL}/keywords", json=data)
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_keyword(id):
    data = {
        "keyword": request.form['keyword'],
        "flowise_id": request.form['flowise_id'],
        "description": request.form['description']
    }
    requests.put(f"{API_URL}/keywords/{id}", json=data)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_keyword(id):
    requests.delete(f"{API_URL}/keywords/{id}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
