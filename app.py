import csv
import io
import uuid
from flask import Flask, render_template, request, Response
from search import geocode_location, run_all_searches

app = Flask(__name__)

# Simple in-memory cache: maps download_id -> categories dict
_result_cache = {}


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

        download_id = str(uuid.uuid4())
        _result_cache[download_id] = {
            "school_name": school_name,
            "city": city,
            "state": state,
            "categories": categories,
        }

        return render_template(
            "result.html",
            school_name=school_name,
            city=city,
            state=state,
            radius=radius,
            categories=categories,
            download_id=download_id,
        )
    except Exception as e:
        return render_template("index.html", error=str(e), form=form_data)


@app.route("/download/<download_id>")
def download(download_id):
    cached = _result_cache.get(download_id)
    if not cached:
        return "Result not found. Please run a new search.", 404

    output = io.StringIO()
    writer = csv.writer(output)

    for category, rows in cached["categories"].items():
        writer.writerow([category])
        writer.writerow(["Name", "Address", "Phone", "Hours", "Website", "Distance"])
        for row in rows:
            writer.writerow([
                row["name"], row["address"], row["phone"],
                row["hours"], row["website"], row["distance"],
            ])
        writer.writerow([])  # blank line between sections

    filename = f"{cached['school_name']} - {cached['city']}, {cached['state']}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    app.run(debug=True)
