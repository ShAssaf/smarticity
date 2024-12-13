from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle CSV file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        # Read CSV into DataFrame
        df = pd.read_csv(file, skiprows=10)
        
        # Preprocess and run your script
        df.rename(columns={
            'תאריך': 'Date',
            'מועד תחילת הפעימה': 'Start Time',
            'צריכה בקוט"ש': 'Consumption (kWh)'
        }, inplace=True)
        df = df.drop(index=0)
        df = df.reset_index(drop=True)
        df['Consumption (kWh)'] = pd.to_numeric(df['Consumption (kWh)'], errors='coerce')

        price_per_kwh = 0.6327
        discount_7 = 0.07
        discount_15 = 0.15
        discount_20 = 0.20

        # Discount functions
        def get_discount_offer_2(time):
            hour = int(time.split(':')[0])
            if 7 <= hour < 17:
                return discount_15
            else:
                return 0

        def get_discount_offer_3(time):
            hour = int(time.split(':')[0])
            if hour >= 23 or hour < 7:
                return discount_20
            else:
                return 0

        # Calculate total cost for offers
        df['Offer_1_Cost'] = df['Consumption (kWh)'] * (1 - discount_7) * price_per_kwh
        df['Offer_2_Discount'] = df['Start Time'].apply(get_discount_offer_2)
        df['Offer_2_Cost'] = df['Consumption (kWh)'] * (1 - df['Offer_2_Discount']) * price_per_kwh
        df['Offer_3_Discount'] = df['Start Time'].apply(get_discount_offer_3)
        df['Offer_3_Cost'] = df['Consumption (kWh)'] * (1 - df['Offer_3_Discount']) * price_per_kwh

        total_cost_offer_1 = df['Offer_1_Cost'].sum()
        total_cost_offer_2 = df['Offer_2_Cost'].sum()
        total_cost_offer_3 = df['Offer_3_Cost'].sum()

        # Prepare bar chart
        offers = ['Offer 1 (7%)', 'Offer 2 (15%)', 'Offer 3 (20%)']
        total_costs = [total_cost_offer_1, total_cost_offer_2, total_cost_offer_3]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(offers, total_costs, color=['blue', 'green', 'red'])
        ax.set_xlabel('Offers')
        ax.set_ylabel('Total Cost (₪)')
        ax.set_title('Total Cost Comparison for Electricity Discount Offers')

        # Annotate bars
        for i, cost in enumerate(total_costs):
            ax.text(i, cost + 0.05, f'{cost:.2f}₪', ha='center', va='bottom')

        # Save the plot as a base64 encoded image
        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

        return render_template('result.html', plot_url=plot_url,
                               total_cost_offer_1=total_cost_offer_1,
                               total_cost_offer_2=total_cost_offer_2,
                               total_cost_offer_3=total_cost_offer_3)

    return "Please upload a valid CSV file."

if __name__ == '__main__':
    app.run(debug=True)