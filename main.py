import pandas as pd
import matplotlib.pyplot as plt

# Load your data (assuming it's already in a DataFrame df)
df = pd.read_csv('/Users/shlomoassaf/Downloads/meter_23576720_LP_21-10-2024.csv', skiprows=10)
df.rename(columns={
    'תאריך': 'Date',
    'מועד תחילת הפעימה': 'Start Time',
    'צריכה בקוט"ש': 'Consumption (kWh)'
}, inplace=True)
df = df.drop(index=0)
# Reset the index after dropping the row
df = df.reset_index(drop=True)
# df contains the columns: 'Date', 'Start Time', 'Consumption (kWh)'
df['Consumption (kWh)'] = pd.to_numeric(df['Consumption (kWh)'], errors='coerce')
# Define the price per kWh
price_per_kwh = 0.6327

# Define discount rates
discount_7 = 0.07
discount_15 = 0.15
discount_20 = 0.20


# Define discount periods
def get_discount_offer_2(time):
    # Extract hour from the 'Start Time' (assuming format HH:MM)
    hour = int(time.split(':')[0])

    # 15% discount between 07:00 and 17:00
    if 7 <= hour < 17:
        return discount_15
    else:
        return 0  # No discount outside this period


def get_discount_offer_3(time):
    # Extract hour from the 'Start Time' (assuming format HH:MM)
    hour = int(time.split(':')[0])

    # 20% discount between 23:00 and 07:00
    if hour >= 23 or hour < 7:
        return discount_20
    else:
        return 0  # No discount outside this period


# Calculate total cost for offer 1 (7% discount for all times)
df['Offer_1_Discount'] = discount_7
df['Offer_1_Cost'] = df['Consumption (kWh)'] * (1 - df['Offer_1_Discount']) * price_per_kwh

# Calculate total cost for offer 2 (15% discount from 07:00 to 17:00)
df['Offer_2_Discount'] = df['Start Time'].apply(get_discount_offer_2)
df['Offer_2_Cost'] = df['Consumption (kWh)'] * (1 - df['Offer_2_Discount']) * price_per_kwh

# Calculate total cost for offer 3 (20% discount from 23:00 to 07:00)
df['Offer_3_Discount'] = df['Start Time'].apply(get_discount_offer_3)
df['Offer_3_Cost'] = df['Consumption (kWh)'] * (1 - df['Offer_3_Discount']) * price_per_kwh

# Calculate total cost for each offer
total_cost_offer_1 = df['Offer_1_Cost'].sum()
total_cost_offer_2 = df['Offer_2_Cost'].sum()
total_cost_offer_3 = df['Offer_3_Cost'].sum()

# Output the total costs for each offer
print(f"Total cost for Offer 1 (7% discount): ${total_cost_offer_1:.2f}")
print(f"Total cost for Offer 2 (15% discount from 07:00 to 17:00): ${total_cost_offer_2:.2f}")
print(f"Total cost for Offer 3 (20% discount from 23:00 to 07:00): ${total_cost_offer_3:.2f}")




# Assuming the calculations from previous code are done
# df contains the columns: 'Offer_1_Cost', 'Offer_2_Cost', 'Offer_3_Cost'

# Sum the total cost for each offer
total_cost_offer_1 = df['Offer_1_Cost'].sum()
total_cost_offer_2 = df['Offer_2_Cost'].sum()
total_cost_offer_3 = df['Offer_3_Cost'].sum()

# Prepare data for plotting
offers = ['Offer 1 (7%)', 'Offer 2 (15%)', 'Offer 3 (20%)']
total_costs = [total_cost_offer_1, total_cost_offer_2, total_cost_offer_3]

# Create the bar chart
plt.figure(figsize=(8, 6))
plt.bar(offers, total_costs, color=['blue', 'green', 'red'])

# Add labels and title
plt.xlabel('Offers')
plt.ylabel('Total Cost (₪)')
plt.title('Total Cost Comparison for Electricity Discount Offers')
plt.ylim(0, max(total_costs) * 1.1)  # Add some padding on y-axis

# Annotate the bars with the exact values
for i, cost in enumerate(total_costs):
    plt.text(i, cost + 0.05, f'{cost:.2f}₪', ha='center', va='bottom')

# Show the plot
plt.tight_layout()
plt.show()

# visalize the average consumption per hour over weekdays
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
df['Weekday'] = df['Date'].dt.day_name()
df['Hour'] = df['Start Time'].str.split(':').str[0].astype(int)
average_consumption_per_hour = df.groupby(['Weekday', 'Hour'])['Consumption (kWh)'].mean().unstack()
# sort the weekdays in the correct order
average_consumption_per_hour = average_consumption_per_hour.reindex(
    ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
plt.figure(figsize=(12, 6))
average_consumption_per_hour.plot(kind='bar', stacked=False)
plt.xlabel('Hour of Day')
plt.ylabel('Average Consumption (kWh)')
plt.title('Average Consumption per Hour over Weekdays')
plt.legend(title='Weekday')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# visalize the average consumption per hour over hours of the day plot each weekday separately sort the weekdays in the correct order

weekdays_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
df['Weekday'] = pd.Categorical(df['Weekday'], categories=weekdays_order, ordered=True)

# Create subplots
fig, axes = plt.subplots(3, 3, figsize=(15, 10), sharey=True)

# Iterate through grouped data and plot
for i, (weekday, data) in enumerate(df.groupby('Weekday')):
    ax = axes[i // 3, i % 3]
    average_consumption_per_hour = data.groupby('Hour')['Consumption (kWh)'].mean()
    average_consumption_per_hour.plot(kind='bar', ax=ax)
    ax.set_title(weekday)
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Average Consumption (kWh)')

plt.suptitle('Average Consumption per Hour over Weekdays')
plt.tight_layout()
plt.show()



