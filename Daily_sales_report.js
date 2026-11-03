
let productCount = 0;
let saleCount = 0;

// Updated with top labels inside a bordered card like the second photo
function addProduct() {
    productCount++;

    const div = document.createElement("div");
    div.className = "form-grid product-row";

    div.innerHTML = `
        <div>
            <label>Product ID</label>
            <input class="pid" placeholder="Enter product ID">
        </div>

        <div>
            <label>Product Name</label>
            <input class="pname" placeholder="Enter product name">
        </div>

        <div>
            <label>Product Price</label>
            <input class="price" type="number" min="0"
                   step="0.01" placeholder="Enter price">
        </div>

        <div>
            <label>Product Quantity</label>
            <input class="quantity" type="number" min="0"
                   step="1" placeholder="Enter quantity">
        </div>
    `;

    document.getElementById("products").appendChild(div);
    updateProductOptions();
}

function addSale() {
    saleCount++;

    const div = document.createElement("div");
    div.className = "sale-grid sale-row";

    div.innerHTML = `
        <div>
            <label>Product</label>
            <select class="sale-product"></select>
        </div>

        <div>
            <label>Quantity Sold</label>
            <input class="sold-quantity"
                   type="number"
                   min="1"
                   step="1"
                   placeholder="Enter quantity">
        </div>
    `;

    document.getElementById("sales").appendChild(div);
    updateProductOptions();
}

function updateProductOptions() {
    const productRows = document.querySelectorAll(".product-row");
    const options = [];

    productRows.forEach(row => {
        const id = row.querySelector(".pid").value.trim();
        const name = row.querySelector(".pname").value.trim();

        if (id && name) {
            options.push({
                id: id,
                name: name
            });
        }
    });

    document.querySelectorAll(".sale-product").forEach(select => {
        const previousValue = select.value;

        select.innerHTML = '<option value="">Select Product</option>';

        options.forEach(product => {
            const option = document.createElement("option");
            option.value = product.id;
            option.textContent = product.name;
            select.appendChild(option);
        });

        if (options.some(p => p.id === previousValue)) {
            select.value = previousValue;
        }
    });
}

document.getElementById("products").addEventListener(
    "input",
    updateProductOptions
);

function showMessage(message, type) {
    const box = document.getElementById("message");
    box.className = type;
    box.textContent = message;
}

function escapeCSV(val) {
    const str = String(val ?? "");
    if (str.includes(",") || str.includes('"') || str.includes("\n")) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}

function generateLocalCSVReport(products, soldData) {
    const productMap = {};
    const clonedProducts = products.map(p => {
        const item = {
            ID: p.ID,
            Name: p.Name,
            Price: p.Price,
            InitialQuantity: p.Quantity,
            Quantity: p.Quantity,
            Sold: 0,
            Total: Number((p.Price * p.Quantity).toFixed(2))
        };
        productMap[item.ID] = item;
        return item;
    });

    let revenue = 0;
    let totalSold = 0;

    soldData.forEach(sale => {
        const product = productMap[sale.ID];
        product.Quantity -= sale.Quantity;
        product.Sold += sale.Quantity;
        revenue += product.Price * sale.Quantity;
        totalSold += sale.Quantity;
    });

    revenue = Number(revenue.toFixed(2));
    const average = totalSold ? Number((revenue / totalSold).toFixed(2)) : 0;

    const maxProduct = clonedProducts.reduce((a, b) => (b.Sold > a.Sold ? b : a), clonedProducts[0]);
    const minProduct = clonedProducts.reduce((a, b) => (b.Sold < a.Sold ? b : a), clonedProducts[0]);

    const now = new Date();
    const pad = n => String(n).padStart(2, "0");
    const timestamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}_${pad(now.getHours())}-${pad(now.getMinutes())}-${pad(now.getSeconds())}`;
    const filename = `sales_report_${timestamp}.csv`;

    const rows = [
        ["ID", "Product", "Price", "Initial Quantity", "Remaining Quantity", "Total Price", "Sold"]
    ];

    clonedProducts.forEach(p => {
        rows.push([p.ID, p.Name, p.Price, p.InitialQuantity, p.Quantity, p.Total, p.Sold]);
    });

    rows.push([]);
    rows.push(["Daily Sales Summary"]);
    rows.push(["Total Revenue", revenue]);
    rows.push(["Average Sale", average]);
    rows.push(["Maximum Sold Product", maxProduct.Name, maxProduct.Sold]);
    rows.push(["Minimum Sold Product", minProduct.Name, minProduct.Sold]);

    const csvContent = "\uFEFF" + rows.map(r => r.map(escapeCSV).join(",")).join("\r\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    return {
        success: true,
        message: "Sales report generated! CSV file downloaded automatically.",
        revenue: revenue,
        average: average,
        max_product: maxProduct.Name,
        max_product_qty: maxProduct.Sold,
        min_product: minProduct.Name,
        min_product_qty: minProduct.Sold,
        filename: filename,
        saved_path: "Downloads folder (Browser Auto-Save)",
        download_url: blobUrl
    };
}

async function sendToBackend(payload) {
    const candidateUrls = [
        "http://127.0.0.1:5001/generate-report",
        "http://127.0.0.1:5000/generate-report"
    ];

    if (window.location.protocol.startsWith("http")) {
        candidateUrls.unshift("/generate-report");
    }

    for (const url of candidateUrls) {
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const text = await response.text();
            const json = JSON.parse(text);

            if (response.ok && json.success) {
                const baseUrl = url.replace("/generate-report", "");
                json.download_url = `${baseUrl}/download/${encodeURIComponent(json.filename)}`;
                return json;
            } else if (json.error) {
                throw new Error(json.error);
            }
        } catch (err) {
            if (err.message && !err.message.includes("Failed to fetch") && !err.message.includes("Unexpected token") && !err.message.includes("NetworkError")) {
                throw err;
            }
        }
    }
    return null;
}

async function generateReport() {
    const message = document.getElementById("message");
    const result = document.getElementById("result");

    message.textContent = "";
    message.className = "";
    result.innerHTML = "";

    try {
        const products = [];

        document.querySelectorAll(".product-row").forEach(row => {
            const ID = row.querySelector(".pid").value.trim();
            const Name = row.querySelector(".pname").value.trim();
            const Price = Number(row.querySelector(".price").value);
            const Quantity = Number(row.querySelector(".quantity").value);

            if (!ID || !Name ||
                row.querySelector(".price").value === "" ||
                row.querySelector(".quantity").value === "" ||
                !Number.isFinite(Price) ||
                !Number.isInteger(Quantity) ||
                Price < 0 || Quantity < 0) {

                throw new Error("Enter valid product details.");
            }

            if (products.some(p => p.ID === ID)) {
                throw new Error("Product IDs must be unique.");
            }

            products.push({ ID, Name, Price, Quantity });
        });

        if (products.length === 0) {
            throw new Error("Please add at least one product.");
        }

        const soldData = [];

        document.querySelectorAll(".sale-row").forEach(row => {
            const ID = row.querySelector(".sale-product").value;
            const quantityInput = row.querySelector(".sold-quantity");
            const Quantity = Number(quantityInput.value);

            if (!ID || quantityInput.value === "" ||
                !Number.isInteger(Quantity) || Quantity <= 0) {

                throw new Error("Enter valid sales information.");
            }

            soldData.push({ ID, Quantity });
        });

        for (const product of products) {
            const totalSold = soldData
                .filter(sale => sale.ID === product.ID)
                .reduce((sum, sale) => sum + sale.Quantity, 0);

            if (totalSold > product.Quantity) {
                throw new Error(
                    "Sold quantity exceeds available stock for " +
                    product.Name
                );
            }
        }

        showMessage("Generating report...", "success");

        let data = await sendToBackend({ products, soldData });

        if (!data) {
            data = generateLocalCSVReport(products, soldData);
        }

        showMessage(data.message, "success");

        result.innerHTML = `
            <h2>Sales Summary</h2>

            <table>
                <tr>
                    <th>Total Revenue</th>
                    <td>${data.revenue}</td>
                </tr>

                <tr>
                    <th>Average Sale</th>
                    <td>${data.average}</td>
                </tr>

                <tr>
                    <th>Maximum Sold Product</th>
                    <td>${data.max_product} (${data.max_product_qty})</td>
                </tr>

                <tr>
                    <th>Minimum Sold Product</th>
                    <td>${data.min_product} (${data.min_product_qty})</td>
                </tr>
            </table>

            <p><strong>CSV File:</strong> ${data.filename}</p>
            <p><strong>Saved Location:</strong> <code>${data.saved_path}</code></p>
            <a class="download-link" href="${data.download_url}" download="${data.filename}">
                Download CSV Again
            </a>
        `;

    } catch (error) {
        showMessage(error.message, "error");
        console.error("Report generation error:", error);
    }
}

addProduct();
addSale();
