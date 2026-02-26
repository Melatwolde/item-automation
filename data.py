import pandas as pd


data = {
    'Item Type': ['Finished Good'] * 10,
    'Category': ['Furniture', 'Furniture', 'Lighting', 'Office', 'Decor', 'Furniture', 'Lighting', 'Office', 'Furniture', 'Decor'],
    'Item Name': ['Chair-Dior-Black', 'Table-Nordic-Oak', 'Lamp-Pixie-Gold', 'Desk-Ergo-White', 'Mirror-Luna-Silver', 'Sofa-Cloud-Grey', 'Luxe-Chandelier', 'Shelf-Bolt-Black', 'Cabinet-Safe-Steel', 'Vase-Zen-White'],
    'Status': ['Active'] * 10,
    'Barcode': [f'98765432{i}' for i in range(10)],
    'Description': ['Luxury chair', 'Oak table', 'Bedside lamp', 'Standing desk', 'Wall mirror', 'Plush sofa', 'Crystal fixture', 'Wall shelf', 'Storage unit', 'Ceramic vase'],
    'Height': ['95cm', '45cm', '30cm', '120cm', '180cm', '85cm', '110cm', '200cm', '190cm', '40cm'],
    'Width': ['50cm', '120cm', '15cm', '140cm', '60cm', '220cm', '80cm', '90cm', '100cm', '20cm'],
    'Depth': ['55cm', '60cm', '15cm', '70cm', '5cm', '95cm', '80cm', '35cm', '45cm', '20cm'],
    'Weight': ['8kg', '25kg', '1.5kg', '35kg', '12kg', '60kg', '15kg', '20kg', '80kg', '3kg'],
    'Volume': ['0.26m3', '0.32m3', '0.01m3', '1.1m3', '0.05m3', '1.7m3', '0.7m3', '0.6m3', '0.8m3', '0.02m3'],
    'Color': ['Black', 'Oak', 'Gold', 'White', 'Silver', 'Grey', 'Crystal', 'Black', 'Steel', 'White'],
    'Unit of Measure': ['PCS'] * 10,
    'Cost Price': [500, 1200, 150, 2100, 400, 3500, 5000, 300, 1800, 80],
    'Price Type': ['Standard'] * 10,
    'Selling Price': [1200, 2800, 450, 4500, 950, 7200, 12000, 750, 3800, 220],
    'Quantity': [50, 15, 100, 10, 25, 5, 2, 40, 8, 60],
    'Minimum Pricing': [1000, 2400, 350, 4000, 800, 6500, 10500, 600, 3200, 180],
    'ImagePath': [f'C:/ERP_Photos/item{i+1}.png' for i in range(10)]
}

pd.DataFrame(data).to_excel("detailed_items_10.xlsx", index=False)
print("Done! Check your folder for detailed_items_10.xlsx")