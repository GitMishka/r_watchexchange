
from flask import Flask, render_template, request
import search_script 

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_terms = request.form.get("search_terms")
        search_terms_list = [term.strip() for term in search_terms.split(",")]
        search_script.search_terms = search_terms_list
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=8000)