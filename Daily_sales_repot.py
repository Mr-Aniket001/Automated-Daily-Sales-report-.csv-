from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app) # Allows frontend to communicate with backend

@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    products = data.get('products', [])
    sold_data = data.get('soldData', [])
    
    filename = f"sales_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
    
    # 1. Process Data & Calculate Sales
    report = {"Revenue": 0, "Average": 0}
    r_qty = 0
    
    for product in products:
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
        "max_product": max_product.get("Name", ""),
        "min_product": min_product.get("Name", "")
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)