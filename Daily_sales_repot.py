from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app) # Allows frontend to communicate with backend

@app.route('/')
def index():
    return send_from_directory(app.root_path, 'Dail_sales_report.html')

@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON request."}), 400

    products = data.get('products', [])
    sold_data = data.get('soldData', [])
    if not isinstance(products, list) or not isinstance(sold_data, list):
        return jsonify({"error": "Products and soldData must be lists."}), 400
    
    filename = f"sales_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    # 1. Process Data & Calculate Sales
    report = {"Revenue": 0, "Average": 0}
    r_qty = 0
    
    for product in products:
        if not all(key in product for key in ('ID', 'Name', 'Price', 'Quantity')):
            return jsonify({"error": "Each product must include ID, Name, Price, and Quantity."}), 400

        product['InitialQuantity'] = product['Quantity']
        product['Total'] = product['Price'] * product['Quantity']
        product['Sold'] = 0
        
        # Match sold data to products
        for sale in sold_data:
            if sale['ID'] == product['ID'] and sale['Quantity'] <= product['Quantity']:
                product['Quantity'] -= sale['Quantity']
                product['Sold'] += sale['Quantity']
                report["Revenue"] += product['Price'] * sale['Quantity']
                r_qty += sale['Quantity']
    
    if r_qty > 0:
        report["Average"] = round(report["Revenue"] / r_qty, 2)
        
    max_product = max(products, key=lambda p: p["Sold"]) if products else {}
    min_product = min(products, key=lambda p: p["Sold"]) if products else {}

    # 2. Generate CSV
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Product", "Price", "Quantity", "Total Price", "Sold"])
        for p in products:
            writer.writerow([p['ID'], p['Name'], p['Price'], p['Quantity'], p['Total'], p['Sold']])
            
        writer.writerow([])
        writer.writerow(["Daily Sales Summary"])
        writer.writerow(["Total Revenue", report["Revenue"]])
        writer.writerow(["Average Sale", report["Average"]])
        writer.writerow(["Maximum Sold Product", max_product.get("Name", ""), max_product.get("Sold", 0)])
        writer.writerow(["Minimum Sold Product", min_product.get("Name", ""), min_product.get("Sold", 0)])

    # 3. Send success response back to frontend
    return jsonify({
        "message": f"CSV report saved as '{filename}' successfully!",
        "revenue": report["Revenue"],
        "average": report["Average"],
        "max_product": max_product.get("Name", ""),
        "max_product_qty": max_product.get("Sold", 0),
        "min_product": min_product.get("Name", ""),
        "min_product_qty": min_product.get("Sold", 0),
        "filename": filename,
        "products": products
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)\