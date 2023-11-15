import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import calendar

all_df = pd.read_csv('all_data.csv')

orders_col = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in orders_col:
    all_df[col] = pd.to_datetime(all_df[col])

def sales_per_month_func(df):
    monthly_sales = all_df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "size",
    })

    monthly_sales.index = monthly_sales.index.strftime('%B')  # Mengubah format month menjadi Tahun-Bulan
    monthly_sales = monthly_sales.reset_index()
    monthly_sales.rename(columns={
        "order_approved_at": "month",
        "order_id": "order_count",
    }, inplace=True)

    monthly_sales = monthly_sales.sort_values('order_count').drop_duplicates('month', keep='last')
    # Mengonversi nama bulan menjadi format numerik
    monthly_sales['month_numeric'] = monthly_sales['month'].apply(lambda x: list(calendar.month_name).index(x))

    # Mengurutkan DataFrame berdasarkan kolom 'month_numeric'
    monthly_sales = monthly_sales.sort_values('month_numeric').drop('month_numeric', axis=1)
    return monthly_sales

def most_least_func(df):
    product_counts = all_df.groupby('product_category_name_english')['product_id'].count().reset_index()
    category_df = product_counts.sort_values(by='product_id', ascending=False)
    return category_df

def spend_func(df):
    sum_spend_df = all_df.resample(rule='M', on='order_approved_at').agg({
    'price': 'sum'
    }).reset_index()

    sum_spend_df.rename(columns={
    'order_approved_at': 'month',
    'price': 'total_spend'
    }, inplace=True)

    sum_spend_df['month'] = sum_spend_df['month'].dt.strftime('%B')
    sum_spend_df = sum_spend_df.sort_values(['total_spend', 'month']).drop_duplicates('month', keep='last')
    return sum_spend_df

def rfm_func(df):
    now = pd.to_datetime("2019-01-01")
    
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    recency_days = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency_count = df.groupby('customer_id')['order_id'].count()
    monetary_sum = df.groupby('customer_id')['price'].sum()

    rfm = pd.DataFrame({
        'customer_id': recency_days.index,
        'Recency': recency_days.values,
        'Frequency': frequency_count.values,
        'Monetary': monetary_sum.values
    })
    return rfm


monthly_sales_df = sales_per_month_func(all_df)
most_least_df = most_least_func(all_df)
customer_spend_df = spend_func(all_df)
rfm = rfm_func(all_df)

# SIDEBAR
with st.sidebar:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Streamlit-logo-primary-colormark-darktext.png", width=100)
    st.sidebar.title("E-Commerce Analytics Dashboard")
    st.sidebar.subheader("Explore and Analyze Sales Data")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Submission Task by Ibnu Malik**")

# HEADER
st.header('Public E-Commerce Analys :sparkles:')

# Monthly Sales
st.subheader('Monthly Orders')
col1, col2 = st.columns(2)

with col1:
    high_order_num = monthly_sales_df['order_count'].max()
    high_order_month = monthly_sales_df[monthly_sales_df['order_count'] == high_order_num]['month'].values[0]
    st.markdown(f"Highest orders in {high_order_month} : **{high_order_num}**")

with col2:
    low_order = monthly_sales_df['order_count'].min()
    low_order_month = monthly_sales_df[monthly_sales_df['order_count'] == low_order]['month'].values[0]
    st.markdown(f"Lowest orders in {low_order_month} : **{low_order}**")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_sales_df["month"],
    monthly_sales_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9",
)
plt.xticks(rotation=45, ha="right")  
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Most Least Product Sales
st.subheader('Most and Least Sold Product')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Penjualan terbanyak
top_selling = most_least_df.head(5)
sns.barplot(x="product_id", y="product_category_name_english", hue="product_category_name_english", data=top_selling, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Products with the Highest Sales", loc="center", fontsize=18)
ax[0].tick_params(axis='y', labelsize=15)

# Penjualan tersedikit
bottom_selling = most_least_df.sort_values(by="product_id", ascending=True).head(5)
sns.barplot(x="product_id", y="product_category_name_english", data=bottom_selling, hue="product_category_name_english", palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Products with the Lowest Sales", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

# Customer Spend
st.subheader('Customer Spend')
col1, col2 = st.columns(2)

with col1:
    total_spend = customer_spend_df['total_spend'].sum()
    formatted_total_spend = "{:.2f}".format(total_spend)
    st.markdown(f"Total Spend : **{formatted_total_spend}**")
    
    max_spend = customer_spend_df.loc[customer_spend_df['total_spend'].idxmax()]
    st.markdown(f"Highest Spend : **{max_spend['total_spend']:.2f}** in {max_spend['month']}")

with col2:
    avg_spend = customer_spend_df['total_spend'].mean()
    formatted_avg_spend = "{:.2f}".format(avg_spend)
    st.markdown(f"Average Spend : **{formatted_avg_spend}**")
    
    min_spend = customer_spend_df.loc[customer_spend_df['total_spend'].idxmin()]
    st.markdown(f"Lowest Spend : **{min_spend['total_spend']:.2f}** in {min_spend['month']}")

fig, ax = plt.subplots(figsize=(16, 8))
min_total_spend = customer_spend_df['total_spend'].min()
max_total_spend = customer_spend_df['total_spend'].max()

sns.barplot(
    x='month',
    y='total_spend',
    data=customer_spend_df,
    color="#90CAF9",
    ax=ax
)
ax.set_xlabel('')
ax.set_ylabel('Total Spend')
ax.tick_params(axis='x', labelrotation=45)
ax.tick_params(axis='both', labelsize=10)
ax.legend().set_visible(False)  # Sembunyikan legenda

st.pyplot(fig)


# RFM Parameters
st.subheader("Best Customers Based on RFM Parameters")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(40, 8))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

# By Recency
recency_plot = sns.barplot(y="Recency", x="customer_id", data=rfm.sort_values(by="Recency", ascending=True).head(5), color=colors[0], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID")
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].set_xticks([])
for p in recency_plot.patches:
    recency_value = int(p.get_height())
    ax[0].annotate(f"{recency_value} days", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=12, color='black')

# By Frequency
frequency_plot = sns.barplot(y="Frequency", x="customer_id", data=rfm.sort_values(by="Frequency", ascending=False).head(5), color=colors[1], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('Customer ID')
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].set_xticks([])
for p in frequency_plot.patches:
    frequency_value = int(p.get_height())
    ax[1].annotate(f"{frequency_value}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=12, color='black')

# By Monetary
monetary_plot = sns.barplot(y="Monetary", x="customer_id", data=rfm.sort_values(by="Monetary", ascending=False).head(5), color=colors[2], ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel('Customer ID')
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].tick_params(axis='y', labelsize=15)
ax[2].set_xticks([])
for p in monetary_plot.patches:
    monetary_value = int(p.get_height())
    ax[2].annotate(f"${monetary_value}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=12, color='black')

st.pyplot(fig)

