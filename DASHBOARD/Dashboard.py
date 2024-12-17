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
 # Memuat dataset
    data = pd.read_csv("DASHBOARD/main_data.csv")

 # Membersihkan nama kolom dari spasi ekstra
    data.columns = data.columns.str.strip()

    # Kelompokkan data berdasarkan customer_state dan hitung jumlah pelanggan per provinsi
    jumlah_pelanggan_df = data['customer_state'].value_counts().reset_index()
    jumlah_pelanggan_df.columns = ['state', 'jumlah_pelanggan']

    # Fungsi untuk mendapatkan koordinat latitude dan longitude berdasarkan provinsi
    def get_koordinat_provinsi(state):
        # Koordinat untuk setiap provinsi di Brasil
        koordinat = {
            'AC': (-8.772, -70.0556), 'AL': (-9.5715, -36.782), 'AP': (-1.413, -51.7717),
            'AM': (-3.4168, -65.856), 'BA': (-12.962, -38.5105), 'CE': (-5.5074, -39.3205),
            'DF': (-15.7801, -47.9292), 'ES': (-20.3155, -40.3128), 'GO': (-16.6896, -49.2532),
            'MA': (-5.352, -44.4011), 'MT': (-12.6373, -56.0934), 'MS': (-20.5066, -54.6291),
            'MG': (-18.512, -44.555), 'PR': (-25.3965, -49.6883), 'PB': (-7.1586, -35.3587),
            'PA': (-5.134, -52.2405), 'PE': (-8.0476, -34.8770), 'PI': (-7.6033, -41.4367),
            'RJ': (-22.9068, -43.1729), 'RN': (-5.7945, -36.6753), 'RS': (-30.0331, -51.2300),
            'RO': (-10.2512, -62.2902), 'RR': (2.8965, -60.6683), 'SC': (-27.5954, -48.548),
            'SP': (-23.5505, -46.6333), 'SE': (-10.9472, -37.0731), 'TO': (-10.2512, -48.3021)
        }
        return koordinat.get(state, (0, 0))

    # Membuat peta yang terpusat di sekitar Brasil
    peta_pusat = [-14.2350, -51.9253]  # Koordinat pusat Brasil
    m = folium.Map(location=peta_pusat, zoom_start=4)

    # Menambahkan MarkerCluster untuk data pelanggan
    cluster_marker = MarkerCluster().add_to(m)

    # Menambahkan marker untuk setiap provinsi dengan jumlah pelanggan
    for _, row in jumlah_pelanggan_df.iterrows():
        state = row['state']
        jumlah_pelanggan = row['jumlah_pelanggan']
        latitude, longitude = get_koordinat_provinsi(state)
        
        # Menambahkan keterangan yang informatif pada setiap marker
        popup_text = f"<strong>{state}</strong><br>Jumlah Pelanggan: {jumlah_pelanggan}"
        
        folium.Marker(
            location=[latitude, longitude],
            popup=popup_text,  # Menampilkan keterangan yang lebih informatif
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(cluster_marker)

    # Menyimpan peta sebagai HTML
    map_html = m._repr_html_()

    # Menampilkan peta dalam Streamlit
    st.title("Klaster Pelanggan Berdasarkan Provinsi")
    st.write("Peta ini menunjukkan jumlah pelanggan di setiap provinsi")
    st.write("klik mark pada peta untuk melihat jumlah pelanggan pernegara bagian")
    components.html(map_html, height=1000, width=1000)

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
