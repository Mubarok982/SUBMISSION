import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from folium.plugins import MarkerCluster
import folium
import streamlit.components.v1 as components

# Fungsi untuk memuat data (hanya developer yang bisa memuat dataset)
def load_data():
    data_path = "DASHOARD/main_datacsv" 
    data = pd.read_csv(data_path)
    return data

# Fungsi untuk mendapatkan koordinat provinsi (khusus Brasil)
def get_koordinat_provinsi(state):
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
    koordinat_state = koordinat.get(state)
    if koordinat_state is None:
        st.warning(f"Koordinat untuk state '{state}' tidak ditemukan. Menggunakan nilai default (0, 0).")
        return (0, 0)
    return koordinat_state

# Judul aplikasi Streamlit
st.title("Dashboard Analisis Data")

# Memuat data (tanpa opsi upload file)
data = load_data()

def toggle_preview(data):
    """
    Fungsi untuk menampilkan preview atau seluruh data berdasarkan pilihan pengguna.
    """
    preview_toggle = st.radio("Tampilkan Data:", ["Preview (Head)", "Seluruh Data"], key="data_toggle")
    if preview_toggle == "Preview (Head)":
        st.write(data.head())
    else:
        st.write(data)

if data is not None:
    # Tampilkan ringkasan data
    st.subheader("Ringkasan Data")
    toggle_preview(data)
    st.write("Jumlah baris dan kolom:", data.shape)

    # Statistik deskriptif
    st.subheader("Statistik Deskriptif")
    st.write(data.describe())

    # Visualisasi: Korelasi matriks menggunakan heatmap
    st.subheader("Heatmap Korelasi")
    fig, ax = plt.subplots(figsize=(10, 8))
    numeric_data = data.select_dtypes(include=['float64', 'int64'])
    if numeric_data.empty:
        st.warning("Data tidak memiliki kolom numerik untuk menghitung korelasi.")
    else:
        sns.heatmap(numeric_data.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Visualisasi: Histogram untuk kolom numerik
    st.subheader("Histogram Kolom Numerik")
    num_columns = numeric_data.columns
    if not num_columns.empty:
        column = st.selectbox("Pilih Kolom", num_columns, key="histogram_column")
        fig, ax = plt.subplots()
        sns.histplot(data[column], kde=True, ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada kolom numerik yang tersedia untuk histogram.")

    # Visualisasi: Scatter Plot dua kolom numerik
    st.subheader("Scatter Plot Kolom Numerik")
    if len(num_columns) > 1:
        col_x = st.selectbox("Pilih Kolom X", num_columns, key="scatter_x")
        col_y = st.selectbox("Pilih Kolom Y", num_columns, key="scatter_y")
        fig = px.scatter(data, x=col_x, y=col_y, title=f"Scatter Plot: {col_x} vs {col_y}")
        st.plotly_chart(fig)
    else:
        st.warning("Kolom numerik tidak cukup untuk membuat scatter plot.")

    # Visualisasi: Boxplot untuk mendeteksi outlier
    st.subheader("Boxplot Kolom Numerik")
    if not num_columns.empty:
        box_column = st.selectbox("Pilih Kolom", num_columns, key="boxplot_column")
        fig, ax = plt.subplots()
        sns.boxplot(y=data[box_column], ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada kolom numerik yang tersedia untuk boxplot.")

    # Filter data berdasarkan kolom kategori jika ada
    cat_columns = data.select_dtypes(include=['object']).columns
    if not cat_columns.empty:
        st.subheader("Filter Data Berdasarkan Kolom Kategori")
        filter_col = st.selectbox("Pilih Kolom Kategori", cat_columns)
        if data[filter_col].isnull().all():
            st.warning(f"Kolom '{filter_col}' kosong. Silakan pilih kolom lain.")
        else:
            unique_vals = data[filter_col].dropna().unique()
            selected_val = st.selectbox("Pilih Nilai", unique_vals)
            filtered_data = data[data[filter_col] == selected_val]
            st.write(filtered_data)

    # Menambahkan visualisasi Pie Chart untuk kolom kategori
    st.subheader("Pie Chart Kolom Kategori")
    if not cat_columns.empty:
        pie_column = st.selectbox("Pilih Kolom Kategori untuk Pie Chart", cat_columns, key="pie_chart_column")
        if data[pie_column].isnull().all():
            st.warning(f"Kolom '{pie_column}' kosong. Tidak dapat membuat Pie Chart.")
        else:
            pie_data = data[pie_column].value_counts()
            fig = px.pie(names=pie_data.index, values=pie_data.values, title=f"Distribusi {pie_column}")
            st.plotly_chart(fig)

    # Menambahkan analisis geospasial jika kolom 'customer_state' ada
    if 'customer_state' in data.columns:
        st.subheader("Analisis Geospasial - Jumlah Pelanggan per State")
        state_counts = data['customer_state'].value_counts().reset_index()
        state_counts.columns = ['State', 'Jumlah Pelanggan']

        # Membuat peta dengan folium
        peta_pusat = [-14.2350, -51.9253]  # Koordinat Brasil
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

    # Validasi data sebelum diunduh
    st.subheader("Unduh Data")
    if 'filtered_data' in locals() and not filtered_data.empty:
        download_data = filtered_data
        st.download_button(label="Unduh Data CSV", data=download_data.to_csv(index=False).encode('utf-8'), file_name="filtered_data.csv", mime="text/csv")
    else:
        st.warning("Pastikan data sudah difilter sebelum diunduh.")

