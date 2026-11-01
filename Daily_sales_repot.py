from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from datetime import datetime
import csv
import webbrowser
from threading import Timer

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = "Dail_sales_report.html"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# Built-in CORS support (no need to install flask-cors)
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def home():
    if (BASE_DIR / HTML_FILE).exists():
        return send_from_directory(BASE_DIR, HTML_FILE)
    return jsonify({
        "error": f"'{HTML_FILE}' not found in {BASE_DIR}"
    }), 404


@app.route("/test", methods=["GET"])
def test():
    return jsonify({
        "success": True,
        "message": "Dail_sales_report.py backend is running!"
    })


@app.route("/download/<path:filename>", methods=["GET"])
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename, as_attachment=True)


@app.route("/generate-report", methods=["POST", "OPTIONS"])
def generate_report():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON data"}), 400

        products = data.get("products")
        sold_data = data.get("soldData")

        if not isinstance(products, list) or not isinstance(sold_data, list):
            return jsonify({"error": "Invalid products or sales list"}), 400

        if not products:
            return jsonify({"error": "Add at least one product"}), 400

        product_map = {}

        for p in products:
            if not isinstance(p, dict):
                return jsonify({"error": "Invalid product record"}), 400

            for key in ("ID", "Name", "Price", "Quantity"):
                if key not in p:
                    return jsonify({"error": f"Missing product field: {key}"}), 400

            product_id = str(p["ID"]).strip()

            if not product_id or product_id in product_map:
                return jsonify({"error": "Product IDs must be unique and non-empty"}), 400

            try:
                price = float(p["Price"])
                quantity = int(p["Quantity"])
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid price or stock quantity"}), 400

            if price < 0 or quantity < 0:
                return jsonify({"error": "Price and stock cannot be negative"}), 400

            p["ID"] = product_id
            p["Price"] = price
            p["InitialQuantity"] = quantity
            p["Quantity"] = quantity
            p["Sold"] = 0
            p["Total"] = round(price * quantity, 2)

            product_map[product_id] = p

        revenue = 0.0
        total_sold = 0

        for sale in sold_data:
            if not isinstance(sale, dict):
                return jsonify({"error": "Invalid sale record"}), 400

            if "ID" not in sale or "Quantity" not in sale:
                return jsonify({"error": "Sale must contain ID and Quantity"}), 400

            product_id = str(sale["ID"]).strip()

            try:
                quantity_sold = int(sale["Quantity"])
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid sold quantity"}), 400

            if quantity_sold <= 0:
                return jsonify({"error": "Sold quantity must be positive"}), 400

            if product_id not in product_map:
                return jsonify({"error": "Selected product does not exist"}), 400

            product = product_map[product_id]

            if quantity_sold > product["Quantity"]:
                return jsonify({
                    "error": f"Insufficient stock for {product['Name']}"
                }), 400

            product["Quantity"] -= quantity_sold
            product["Sold"] += quantity_sold

            revenue += product["Price"] * quantity_sold
            total_sold += quantity_sold

        revenue = round(revenue, 2)
        average = round(revenue / total_sold, 2) if total_sold else 0

        max_product = max(products, key=lambda p: p["Sold"])
        min_product = min(products, key=lambda p: p["Sold"])

        filename = "sales_report_" + datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        ) + ".csv"

        filepath = REPORT_DIR / filename

        with open(filepath, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)

            writer.writerow([
                "ID", "Product", "Price",
                "Initial Quantity", "Remaining Quantity",
                "Total Price", "Sold"
            ])

            for p in products:
                writer.writerow([
                    p["ID"],
                    p["Name"],
                    p["Price"],
                    p["InitialQuantity"],
                    p["Quantity"],
                    p["Total"],
                    p["Sold"]
                ])

            writer.writerow([])
            writer.writerow(["Daily Sales Summary"])
            writer.writerow(["Total Revenue", revenue])
            writer.writerow(["Average Sale", average])
            writer.writerow([
                "Maximum Sold Product",
                max_product["Name"],
                max_product["Sold"]
            ])
            writer.writerow([
                "Minimum Sold Product",
                min_product["Name"],
                min_product["Sold"]
            ])

        return jsonify({
            "success": True,
            "message": "Sales report generated and saved in the 'reports' folder!",
            "revenue": revenue,
            "average": average,
            "max_product": max_product["Name"],
            "max_product_qty": max_product["Sold"],
            "min_product": min_product["Name"],
            "min_product_qty": min_product["Sold"],
            "filename": filename,
            "saved_path": str(filepath),
            "products": products
        }), 200

    except Exception:
        app.logger.exception("Report generation failed")
        return jsonify({"error": "Backend processing failed. Check terminal."}), 500


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5001")


if __name__ == "__main__":
    print(f"CSV reports folder: {REPORT_DIR}")
    print("Opening browser at: http://127.0.0.1:5001")
    Timer(1.0, open_browser).start()
    app.run(host="127.0.0.1", port=5001, debug=False)