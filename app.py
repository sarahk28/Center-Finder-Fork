import base64
import csv
import io
from flask import Flask, render_template, request
from search import geocode_location, run_all_searches

app = Flask(__name__)


def build_csv(school_name, city, state, categories):
    output = io.StringIO()
    writer = csv.writer(output)
    for category, rows in categories.items():
        writer.writerow([category])
        writer.writerow(["Name", "Address", "Phone", "Hours", "Website", "Distance"])
        for row in rows:
            writer.writerow([
                row["name"], row["address"], row["phone"],
                row["hours"], row["website"], row["distance"],
            ])
        writer.writerow([])
    csv_bytes = output.getvalue().encode("utf-8")
    b64 = base64.b64encode(csv_bytes).decode("utf-8")
    return f"data:text/csv;base64,{b64}"


@app.route("/")
def index():
    return render_template("index.html", error=None, form={})


@app.route("/generate", methods=["POST"])
def generate():
    school_name = request.form.get("school_name", "").strip()
    city = request.form.get("city", "").strip()
    state = request.form.get("state", "").strip()
    zip_code = request.form.get("zip_code", "").strip()
    try:
        radius = float(request.form.get("radius", "15") or "15")
        if radius <= 0:
            raise ValueError
    except ValueError:
        radius = 15.0

    form_data = {
        "school_name": school_name,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "radius": radius,
    }

    try:
        lat, lng = geocode_location(city, state, zip_code)
        categories = run_all_searches(lat, lng, max_miles=radius)
        csv_data_uri = build_csv(school_name, city, state, categories)
        csv_filename = f"{school_name} - {city}, {state}.csv"

        centers_list = []
        for category_name, rows in categories.items():
            for row in rows:
                centers_list.append({'name': row['name']})

        return render_template(
            "result.html",
            school_name=school_name,
            city=city,
            state=state,
            radius=radius,
            categories=categories,
            csv_data_uri=csv_data_uri,
            csv_filename=csv_filename,
            centers=centers_list
        )
    except Exception as e:
        return render_template("index.html", error=str(e), form=request.form)

if __name__ == "__main__":
    app.run(debug=True)
