import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from folium.plugins import MarkerCluster
import folium
import streamlit.components.v1 as components

# Memuat dataset
def load_data():
    data_path = "DASHBOARD/main_data.csv"  
    data = pd.read_csv(data_path)
    return data

# Memuat data
customer_df = load_data()

# Menampilkan judul di Sidebar
st.sidebar.title("Analisis Data Pelanggan, Pembayaran, dan Geolokasi")
st.sidebar.title("Analisis customer berdasarkan tanggal")

# Navigasi Tab
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Analisis Customer", "RFM Analisis", "Geospatial Analysis", "Analisis Pembayaran", "Summary"])

# Overview
with tab1:
    st.subheader("Informasi Data Pelanggan:")
    st.write(customer_df.info())
    st.subheader("Sampel Data Pelanggan:")
    st.dataframe(customer_df.head())
    
    # Statistik Deskriptif
    st.subheader("Statistik Deskriptif Dataset:")
    st.dataframe(customer_df.describe())

    # Heatmap Korelasi
    st.subheader("Heatmap Korelasi")
    fig, ax = plt.subplots(figsize=(10, 8))
    numeric_data = customer_df.select_dtypes(include=['float64', 'int64'])
    if numeric_data.empty:
        st.warning("Data tidak memiliki kolom numerik untuk menghitung korelasi.")
    else:
        sns.heatmap(numeric_data.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Histogram Kolom Numerik
    st.subheader("Histogram Kolom Numerik")
    num_columns = numeric_data.columns
    if not num_columns.empty:
        column = st.selectbox("Pilih Kolom", num_columns, key="histogram_column")
        fig, ax = plt.subplots()
        sns.histplot(customer_df[column], kde=True, ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada kolom numerik yang tersedia untuk histogram.")

    # Scatter Plot Kolom Numerik
    st.subheader("Scatter Plot Kolom Numerik")
    if len(num_columns) > 1:
        col_x = st.selectbox("Pilih Kolom X", num_columns, key="scatter_x")
        col_y = st.selectbox("Pilih Kolom Y", num_columns, key="scatter_y")
        fig = px.scatter(customer_df, x=col_x, y=col_y, title=f"Scatter Plot: {col_x} vs {col_y}")
        st.plotly_chart(fig)
    else:
        st.warning("Kolom numerik tidak cukup untuk membuat scatter plot.")

    # Boxplot untuk Outliers
    st.subheader("Boxplot Kolom Numerik")
    if not num_columns.empty:
        box_column = st.selectbox("Pilih Kolom", num_columns, key="boxplot_column")
        fig, ax = plt.subplots()
        sns.boxplot(y=customer_df[box_column], ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada kolom numerik yang tersedia untuk boxplot.")

    # Pie Chart Kolom Kategori
    cat_columns = customer_df.select_dtypes(include=['object']).columns
    if not cat_columns.empty:
        st.subheader("Pie Chart Kolom Kategori")
        pie_column = st.selectbox("Pilih Kolom Kategori untuk Pie Chart", cat_columns, key="pie_chart_column")
        if customer_df[pie_column].isnull().all():
            st.warning(f"Kolom '{pie_column}' kosong. Tidak dapat membuat Pie Chart.")
        else:
            pie_data = customer_df[pie_column].value_counts()
            fig = px.pie(names=pie_data.index, values=pie_data.values, title=f"Distribusi {pie_column}")
            st.plotly_chart(fig)

# Analisis Customer
with tab2:
    st.header("Distribusi Customer")

    # Distribusi Customer per State
    state_counts = customer_df['customer_state'].value_counts()
    state_counts_sorted = state_counts.sort_values(ascending=False)
    state_counts_sorted = state_counts_sorted.rename_axis('State').reset_index(name='Count')
    st.subheader("Distribusi Customer per State")
    st.bar_chart(state_counts_sorted.set_index('State'))

    # Distribusi Customer per City
    st.subheader("Distribusi Customer per City (Top 10)")
    city_counts = customer_df['customer_city'].value_counts().head(10)
    city_counts_sorted = city_counts.sort_values(ascending=False)
    city_counts_sorted = city_counts_sorted.rename_axis('City').reset_index(name='Count')
    st.bar_chart(city_counts_sorted.set_index('City'))

    # Boxplot Distribusi Jumlah Customer per Kota
    st.subheader("Boxplot Distribusi Jumlah Customer per Kota")
    customer_per_city = customer_df['customer_city'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(customer_per_city, vert=False, patch_artist=True, ax=ax)
    st.pyplot(fig)

# Analisis Geospasial
with tab4:
    st.subheader("Analisis Geospasial - Jumlah Pelanggan per State")
    state_counts = customer_df['customer_state'].value_counts().reset_index()
    state_counts.columns = ['State', 'Jumlah Pelanggan']

    # Membuat peta dengan folium
    peta_pusat = [-14.2350, -51.9253]
    m = folium.Map(location=peta_pusat, zoom_start=4)
    cluster_marker = MarkerCluster().add_to(m)

    for _, row in state_counts.iterrows():
        state = row['State']
        jumlah_pelanggan = row['Jumlah Pelanggan']
        latitude, longitude = get_koordinat_provinsi(state)
        folium.Marker(
            location=[latitude, longitude],
            popup=f"{state}: {jumlah_pelanggan} pelanggan",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(cluster_marker)

    map_html = m._repr_html_()
    components.html(map_html, height=600)

# Analisis Pembayaran
with tab5:
    st.subheader("Analisis Pembayaran")
    order_payments_df = pd.read_csv("DASHBOARD/order_payments_dataset.csv")
    payment_type_counts = order_payments_df['payment_type'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=payment_type_counts.index, y=payment_type_counts.values, palette="coolwarm")
    st.pyplot(plt)

# Summary
with tab6:
    st.write("Saring dan tampilkan analisis berdasarkan pilihan yang Anda buat di tab lainnya.")
    st.caption('Copyright © Rizqy Mubarok 2024')
