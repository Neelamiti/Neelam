"""
Flask app for exploring the health_data.csv dataset.

Run with:
    pip install flask --break-system-packages
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""
import csv
import os
from statistics import mean

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "health_data.csv")

NUMERIC_FIELDS = [
    "Age", "Height_cm", "Weight_kg", "BMI", "Heart_Rate_bpm",
    "BP_Systolic", "BP_Diastolic", "Body_Temp_F", "Sleep_Hours",
    "Water_Intake_Glasses", "Daily_Steps", "Calories_Burned", "Health_Score",
]


def load_data():
    """Load the CSV into a list of dicts, casting numeric columns."""
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            for field in NUMERIC_FIELDS:
                row[field] = float(row[field])
            rows.append(row)
    return rows


# Cache the dataset in memory (1200 rows is tiny).
DATA = load_data()


def filter_rows(rows, gender=None, risk=None):
    if gender and gender != "All":
        rows = [r for r in rows if r["Gender"] == gender]
    if risk and risk != "All":
        rows = [r for r in rows if r["Risk_Level"] == risk]
    return rows


@app.route("/")
def index():
    genders = sorted({r["Gender"] for r in DATA})
    risk_levels = sorted({r["Risk_Level"] for r in DATA})
    return render_template("index.html", genders=genders, risk_levels=risk_levels)


@app.route("/api/summary")
def api_summary():
    """Return overall summary stats, optionally filtered by gender/risk."""
    gender = request.args.get("gender")
    risk = request.args.get("risk")
    rows = filter_rows(DATA, gender, risk)

    if not rows:
        return jsonify({"count": 0})

    summary = {"count": len(rows)}
    for field in NUMERIC_FIELDS:
        values = [r[field] for r in rows]
        summary[field] = {
            "avg": round(mean(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
        }

    risk_counts = {}
    for r in rows:
        risk_counts[r["Risk_Level"]] = risk_counts.get(r["Risk_Level"], 0) + 1
    summary["risk_breakdown"] = risk_counts

    gender_counts = {}
    for r in rows:
        gender_counts[r["Gender"]] = gender_counts.get(r["Gender"], 0) + 1
    summary["gender_breakdown"] = gender_counts

    return jsonify(summary)


@app.route("/api/records")
def api_records():
    """Return paginated raw records, optionally filtered by gender/risk."""
    gender = request.args.get("gender")
    risk = request.args.get("risk")
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 25)), 1), 200)

    rows = filter_rows(DATA, gender, risk)
    total = len(rows)
    start = (page - 1) * per_page
    end = start + per_page
    page_rows = rows[start:end]

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max((total + per_page - 1) // per_page, 1),
        "records": page_rows,
    })


@app.route("/api/scatter")
def api_scatter():
    """Return x/y pairs for a scatter plot, e.g. Daily_Steps vs Health_Score."""
    gender = request.args.get("gender")
    risk = request.args.get("risk")
    x_field = request.args.get("x", "Daily_Steps")
    y_field = request.args.get("y", "Health_Score")

    if x_field not in NUMERIC_FIELDS or y_field not in NUMERIC_FIELDS:
        return jsonify({"error": "invalid field"}), 400

    rows = filter_rows(DATA, gender, risk)
    points = [
        {"x": r[x_field], "y": r[y_field], "risk": r["Risk_Level"], "gender": r["Gender"]}
        for r in rows
    ]
    return jsonify({"x_field": x_field, "y_field": y_field, "points": points})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
