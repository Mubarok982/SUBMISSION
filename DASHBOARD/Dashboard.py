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

# Memuat dataset
def load_data():
    data_path = "DASHBOARD/main_data.csv"  
    data = pd.read_csv(data_path)
    return data

# Memuat data
customer_df = load_data()

# Pastikan kolom 'tanggal' ada dan dalam format datetime
customer_df['order_purchase_timestamp'] = pd.to_datetime(customer_df['order_purchase_timestamp'], errors='coerce')

# Menampilkan judul di Sidebar
st.sidebar.title("Analisis Data Pelanggan, Pembayaran, dan Geolokasi")
st.sidebar.title("Analisis Customer Berdasarkan Tanggal")

# Fitur filter berdasarkan tanggal di sidebar
st.sidebar.subheader("Filter Berdasarkan Tanggal")
start_date = st.sidebar.date_input("Tanggal Mulai", customer_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input("Tanggal Akhir", customer_df['order_purchase_timestamp'].max())

# Filter data berdasarkan rentang tanggal
filtered_data = customer_df[(customer_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & (customer_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

# Navigasi Tab
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Analisis Customer", "RFM Analisis", "Geospatial Analysis", "Analisis Pembayaran", "Summary"])

# Overview
with tab1:
    st.subheader("Informasi Data Pelanggan:")
    st.write(filtered_data.info())
    st.subheader("Sampel Data Pelanggan:")
    st.dataframe(filtered_data.head())
    
    # Statistik Deskriptif
    st.subheader("Statistik Deskriptif Dataset:")
    st.dataframe(filtered_data.describe())

    # Heatmap Korelasi
    st.subheader("Heatmap Korelasi")
    fig, ax = plt.subplots(figsize=(10, 8))
    numeric_data = filtered_data.select_dtypes(include=['float64', 'int64'])
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
        sns.histplot(filtered_data[column], kde=True, ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada kolom numerik yang tersedia untuk histogram.")

    # Scatter Plot Kolom Numerik
    st.subheader("Scatter Plot Kolom Numerik")
    if len(num_columns) > 1:
        col_x = st.selectbox("Pilih Kolom X", num_columns, key="scatter_x")
        col_y = st.selectbox("Pilih Kolom Y", num_columns, key="scatter_y")
        fig = px.scatter(filtered_data, x=col_x, y=col_y, title=f"Scatter Plot: {col_x} vs {col_y}")
        st.plotly_chart(fig)
    else:
        st.warning("Kolom numerik tidak cukup untuk membuat scatter plot.")

    # Boxplot untuk Outliers
    st.subheader("Boxplot Kolom Numerik")
    if not num_columns.empty:
        box_column = st.selectbox("Pilih Kolom", num_columns, key="boxplot_column")
        fig, ax = plt.subplots()
        sns.boxplot(y=filtered_data[box_column], ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Tidak ada kolom numerik yang tersedia untuk boxplot.")

    # Pie Chart Kolom Kategori
    cat_columns = filtered_data.select_dtypes(include=['object']).columns
    if not cat_columns.empty:
        st.subheader("Pie Chart Kolom Kategori")
        pie_column = st.selectbox("Pilih Kolom Kategori untuk Pie Chart", cat_columns, key="pie_chart_column")
        if filtered_data[pie_column].isnull().all():
            st.warning(f"Kolom '{pie_column}' kosong. Tidak dapat membuat Pie Chart.")
        else:
            pie_data = filtered_data[pie_column].value_counts()
            fig = px.pie(names=pie_data.index, values=pie_data.values, title=f"Distribusi {pie_column}")
            st.plotly_chart(fig)

# Analisis Customer
with tab2:
    st.header("Distribusi Customer")

    # Distribusi Customer per State
    state_counts = filtered_data['customer_state'].value_counts()
    state_counts_sorted = state_counts.sort_values(ascending=False)
    state_counts_sorted = state_counts_sorted.rename_axis('State').reset_index(name='Count')
    st.subheader("Distribusi Customer per State")
    st.bar_chart(state_counts_sorted.set_index('State'))

    # Distribusi Customer per City
    st.subheader("Distribusi Customer per City (Top 10)")
    city_counts = filtered_data['customer_city'].value_counts().head(10)
    city_counts_sorted = city_counts.sort_values(ascending=False)
    city_counts_sorted = city_counts_sorted.rename_axis('City').reset_index(name='Count')
    st.bar_chart(city_counts_sorted.set_index('City'))

    # Boxplot Distribusi Jumlah Customer per Kota
    st.subheader("Boxplot Distribusi Jumlah Customer per Kota")
    customer_per_city = filtered_data['customer_city'].value_counts()
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
    st.write("1. Statistik Deskriptif")
    st.write("""Statistik deskriptif memberi kita gambaran umum tentang data pelanggan. 
    Di sini kita bisa melihat angka-angka penting seperti rata-rata usia pelanggan, total transaksi, dan berbagai metrik lainnya. 
    Ini seperti melihat snapshot data, membantu kita memahami sebaran dan variasi data yang ada.""")

    st.write("2. Heatmap Korelasi")
    st.write(""" Heatmap ini menampilkan hubungan antara berbagai aspek data. Dengan melihat warna, kita bisa tahu apakah dua variabel saling memengaruhi. 
    Ini sangat berguna untuk menemukan pola tersembunyi yang mungkin belum kita sadari.
    Contoh: "Melalui heatmap, kita bisa melihat apakah ada hubungan antara jumlah transaksi dan frekuensi pembelian. Misalnya, apakah semakin sering pelanggan berbelanja, semakin tinggi pengeluarannya?""")

    st.write("3. Histogram Kolom Numerik")
    st.write(""" Histogram membantu kita memahami bagaimana data numerik terdistribusi. Apakah data banyak terkumpul di nilai tertentu atau tersebar merata? 
    Ini memberi kita insight tentang pola yang ada.
    Contoh: "Histogram ini menunjukkan bagaimana jumlah transaksi tersebar di seluruh pelanggan. Apakah sebagian besar pelanggan berbelanja sedikit atau ada yang sangat sering berbelanja?""")

    st.write("4. Scatter Plot Kolom Numerik")
    st.write(""" Scatter plot menampilkan hubungan antara dua variabel. Ini membantu kita melihat apakah ada pola atau tren tertentu yang bisa kita manfaatkan, atau bahkan mengidentifikasi titik-titik yang berbeda dari yang lainnya.
    Contoh: "Dengan scatter plot ini, kita bisa melihat apakah ada hubungan antara usia pelanggan dan jumlah transaksi mereka. Mungkin pelanggan muda lebih sering bertransaksi, atau sebaliknya?""")

    st.write("5. Boxplot untuk Outliers")
    st.write(""" Boxplot ini membantu kita menemukan nilai-nilai yang terlalu jauh dari kebanyakan data, atau yang biasa disebut outliers. 
    Ini sangat penting karena bisa menunjukkan anomali atau data yang perlu perhatian lebih.
    Contoh: "Boxplot ini menunjukkan apakah ada kota atau pelanggan dengan transaksi yang sangat besar atau kecil dibandingkan lainnya. Ini bisa membantu kita melihat pola unik dalam data.""")

    st.write("6. Pie Chart Kolom Kategori")
    st.write(""" Pie chart ini memberi gambaran yang jelas tentang bagaimana pelanggan tersebar berdasarkan kategori tertentu. Misalnya, kita bisa melihat berapa banyak pelanggan yang memilih metode pembayaran tertentu atau status pelanggan.
    Contoh: "Pie chart ini memperlihatkan persentase metode pembayaran yang digunakan pelanggan. Apakah mayoritas memilih transfer bank, atau lebih suka menggunakan kartu kredit?""")

    st.write("7. Distribusi Customer per State dan City")
    st.write(""" Visualisasi ini membantu kita melihat sebaran pelanggan berdasarkan lokasi geografis, baik itu negara bagian atau kota. 
    Ini memberi kita pemahaman lebih baik tentang konsentrasi pelanggan di berbagai area.
    Contoh: "Grafik ini menunjukkan kota dan negara bagian mana yang memiliki jumlah pelanggan terbanyak. Ini membantu kita memahami di mana pelanggan kita terkonsentrasi dan apakah ada area yang perlu perhatian lebih.""")

    st.write("8. Boxplot Distribusi Jumlah Customer per Kota")
    st.write(""" Boxplot ini menunjukkan variasi jumlah pelanggan di setiap kota. 
    Ini membantu kita melihat kota mana yang memiliki banyak pelanggan, dan kota mana yang mungkin kurang terlayani.
    Contoh: "Boxplot ini memperlihatkan bagaimana jumlah pelanggan berbeda di setiap kota. Ada kota dengan jumlah pelanggan sangat tinggi, dan ada pula yang lebih rendah.""")

    st.write("9. Peta Geospasial (Folium Map)")
    st.write(""" Peta ini memberi gambaran visual mengenai lokasi pelanggan di seluruh wilayah, lengkap dengan marker untuk menunjukkan konsentrasi pelanggan di setiap daerah. 
    Ini sangat berguna untuk memahami pola geografis dan menentukan strategi pemasaran yang lebih tepat.
    Contoh: "Dengan peta ini, kita bisa melihat di mana saja pelanggan kita berada. Setiap marker mewakili jumlah pelanggan di provinsi tertentu, dan kita bisa segera melihat area dengan konsentrasi tinggi.""")

    st.write("10. Analisis Pembayaran")
    st.write(""" Di sini, kita melihat cara pelanggan melakukan pembayaran. 
    Ini membantu kita memahami preferensi mereka, apakah mereka lebih suka bayar dengan kartu kredit, transfer bank, atau metode lain.
    Contoh: "Grafik ini menunjukkan metode pembayaran mana yang paling sering digunakan oleh pelanggan. Apakah pelanggan kita lebih banyak yang memilih bayar dengan kartu kredit atau dompet digital?""")

    st.write("""Kesimpulan Akhir:
      Dengan semua visualisasi ini, kita bisa mendapatkan gambaran lengkap tentang siapa pelanggan kita, bagaimana mereka berbelanja, dan di mana mereka berada. 
    Ini memberi kita wawasan penting untuk membuat keputusan yang lebih baik dan strategi yang lebih terarah.""")

    st.caption("Copyright © Rizqy Mubarok 2024")

