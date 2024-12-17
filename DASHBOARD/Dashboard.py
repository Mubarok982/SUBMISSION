import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
import folium
import streamlit.components.v1 as components
#import plotly.components

#load data 
# Data import dan processing 
customer_df = pd.read_csv("main_data.csv")
geolocation_df = pd.read_csv("main_data.csv")
order_payments_df = pd.read_csv("main_data.csv")

order_purchase = pd.read_csv("main_data.csv")
# Menampilkan judul di Sidebar
st.sidebar.title("Analisis Data Pelanggan, Pembayaran, dan Geolokasi")
st.sidebar.image("c:\SINAU\DATA ANALIS\dicoding\SUBMISSION\Image.png")
st.sidebar.title("Analisis customer berdasarkan tanggal")

# Konten lainnya
st.header("SILAKAN PILIH MENU SESUAI PREFERENSI ANDA ")

# Navigasi Tab
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Analisis Customer", "RFM Analisis", "Geospatial Analysis", "Analisis Pembayaran", "Summary"])


#integrasi dengan overview 
with tab1:
    # Info Dataset
    st.subheader("Informasi Data Pelanggan:")
    st.write(customer_df.info())
    st.subheader("Sampel Data Pelanggan:")
    st.dataframe(customer_df.head())
    
    # Statistik Deskriptif
    st.subheader("Statistik Deskriptif Dataset:")
    st.dataframe(customer_df.describe())
    
    
#Analisis customer
with tab2:
    st.header("Distribusi Customer")

    # Memuat dataset
    data = pd.read_csv('C:\SINAU\DATA ANALIS\dicoding\SUBMISSION\DASHBOARD/main_data.csv')

    # Membersihkan nama kolom dari spasi ekstra
    data.columns = data.columns.str.strip()

    # Menyusun distribusi jumlah pelanggan per customer_state
    state_counts = data['customer_state'].value_counts()

    # Mengurutkan berdasarkan jumlah pelanggan, dari yang terbesar
    state_counts_sorted = state_counts.sort_values(ascending=False)

    # Ubah menjadi DataFrame untuk kemudahan tampilan
    state_counts_sorted = state_counts_sorted.rename_axis('State').reset_index(name='Count')

    # Menampilkan judul dan bar chart
    st.subheader("Distribusi Customer per State")
    st.bar_chart(state_counts_sorted.set_index('State'))


    # Distribusi Customer per Kota (Top 10)
    st.subheader("Distribusi Customer per City (Top 10)")
    city_counts = customer_df['customer_city'].value_counts().head(10)
    city_counts_sorted = city_counts.sort_values(ascending=False)  # Urutkan berdasarkan jumlah
    city_counts_sorted = city_counts_sorted.rename_axis('City').reset_index(name='Count')  # Ubah format menjadi DataFrame
    st.bar_chart(city_counts_sorted.set_index('City'))  # Bar chart dengan index 'City'



    # Membuat Boxplot
    st.subheader("Boxplot Distribusi Jumlah Customer per Kota")

    # Menghitung statistik untuk boxplot
    customer_per_city = customer_df['customer_city'].value_counts()
    Q1 = customer_per_city.quantile(0.25)
    Q2 = customer_per_city.median()
    Q3 = customer_per_city.quantile(0.75)
    min_val = customer_per_city.min()
    max_val = customer_per_city.max()

    # Membuat boxplot
    fig, ax = plt.subplots(figsize=(10, 5))  # Ukuran lebih besar
    box = ax.boxplot(customer_per_city, vert=False, patch_artist=True, 
                     boxprops=dict(facecolor='lightblue', color='blue'),
                     medianprops=dict(color='red', linewidth=2),
                     whiskerprops=dict(color='blue', linewidth=1.5),
                     capprops=dict(color='blue', linewidth=1.5),
                     flierprops=dict(marker='o', color='blue', alpha=0.5))

    # Menambahkan garis untuk Q1, Q2 (median), dan Q3
    ax.axvline(Q1, color='green', linestyle='--', linewidth=2, label=f'Q1 ({Q1:.2f})')
    ax.axvline(Q2, color='red', linestyle='--', linewidth=2, label=f'Q2 (Median) ({Q2:.2f})')
    ax.axvline(Q3, color='orange', linestyle='--', linewidth=2, label=f'Q3 ({Q3:.2f})')

    # Menambahkan judul dan label
    ax.set_title("Boxplot Distribusi Customer per Kota", fontsize=14, fontweight='bold')
    ax.set_xlabel("Jumlah Customer", fontsize=12)
    ax.grid(axis='x', linestyle='--', alpha=0.7)  # Menambahkan grid horizontal

    # Menambahkan legend
    ax.legend()

    # Menampilkan boxplot di Streamlit
    st.pyplot(fig)

    # Menambahkan keterangan statistik
    st.write("### Statistik Boxplot:")
    st.write(f"- **Nilai Minimum**: {min_val}")
    st.write(f"- **Kuartil Pertama (Q1)**: {Q1}")
    st.write(f"- **Median (Q2)**: {Q2}")
    st.write(f"- **Kuartil Ketiga (Q3)**: {Q3}")
    st.write(f"- **Nilai Maksimum**: {max_val}")



    
#Analisis Recency,Frequency dan Monetary
# Contoh sederhana pembuatan DataFrame untuk RFM
data = {
    'customer_unique_id': [1, 2, 3],
    'Recency': [10, 20, 30],
    'Frequency': [5, 2, 1],
    'Monetary': [1000, 500, 200]
}
rfm_df = pd.DataFrame(data)

def assign_segment(row):
    if row['Recency'] < 30 and row['Frequency'] > 5:
        return 'Loyal'
    elif row['Monetary'] > 1000:
        return 'High Value'
    else:
        return 'Low Value'

rfm_df['Segment'] = rfm_df.apply(assign_segment, axis=1)


with tab3:
    st.header("Analisis RFM (Recency, Frequency, Monetary)")

    # Tampilkan Data RFM
    st.subheader("Tabel RFM:")
    st.dataframe(rfm_df)

    # Visualisasi Segmentasi Pelanggan
    st.subheader("Distribusi Pelanggan Berdasarkan Segmentasi RFM")
    st.bar_chart(rfm_df['Segment'].value_counts())
        

    # Langkah 1: Memuat dataset
    df = pd.read_csv('main_data.csv')

    # Langkah 2: Mengubah kolom 'order_purchase_timestamp' menjadi tipe datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Langkah 3: Menghitung Recency (berapa lama sejak pembelian terakhir)
    tanggal_terakhir = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    df['Recency'] = (tanggal_terakhir - df['order_purchase_timestamp']).dt.days

    # Langkah 4: Menghitung Frequency (frekuensi pembelian per pelanggan)
    rfm_df = df.groupby('customer_id').agg(
        Frequency=('order_id', 'nunique'),  # Menghitung jumlah order unik per customer_id
        Monetary=('payment_value', 'sum')   # Menjumlahkan total pembayaran per customer_id
    ).reset_index()

    # Langkah 5: Menggabungkan data Recency dengan Frequency dan Monetary
    rfm_df = pd.merge(rfm_df, df[['customer_id', 'Recency']].drop_duplicates(), on='customer_id', how='left')

    # Langkah 6: Menghitung RFM Score
    rfm_df['RFM_Score'] = rfm_df[['Recency', 'Frequency', 'Monetary']].apply(lambda x: (x['Recency'] + x['Frequency'] + x['Monetary']), axis=1)

    # Langkah 7: Membuat Segmentasi Berdasarkan RFM Score
    rfm_df['Segment'] = pd.cut(rfm_df['RFM_Score'],
                            bins=[0, 3, 6, 9],
                            labels=['Nilai Rendah', 'Nilai Sedang', 'Nilai Tinggi'])

    # Langkah 8: Menampilkan tabel RFM
    print(rfm_df.head())

    # Langkah 9: Visualisasi Distribusi Segmen Pelanggan
    plt.figure(figsize=(8, 6))
    sns.countplot(data=rfm_df, x='Segment', palette='viridis')
    plt.title('Distribusi Pelanggan Berdasarkan Segmentasi RFM')
    plt.xlabel('Segment')
    plt.ylabel('Jumlah Pelanggan')
    plt.show()

with tab4:

    # Memuat dataset
    data = pd.read_csv(r'C:\SINAU\DATA ANALIS\dicoding\SUBMISSION\DASHBOARD\main_data.csv')

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

with tab5:

    # Memuat dataset
    order_payments_df = pd.read_csv('C:/SINAU/DATA ANALIS/dicoding/SUBMISSION/DASHBOARD/order_payments_dataset.csv')

    # Membersihkan kolom dari spasi ekstra
    order_payments_df.columns = order_payments_df.columns.str.strip()

    # Tab untuk analisis pembayaran
    with st.expander("Analisis Pembayaran"):

        # Menghitung jumlah untuk tiap jenis pembayaran
        payment_type_counts = order_payments_df['payment_type'].value_counts().head(10)
        
        # Membuat grafik distribusi jenis pembayaran
        plt.figure(figsize=(10, 6))
        sns.barplot(x=payment_type_counts.index, y=payment_type_counts.values, palette="coolwarm")
        plt.title("Distribusi Jenis Pembayaran (Top 10)", fontsize=16)
        plt.xlabel("Jenis Pembayaran", fontsize=12)
        plt.ylabel("Jumlah", fontsize=12)
        plt.xticks(rotation=45)
        
        # Menampilkan grafik dalam Streamlit
        st.pyplot(plt)

with tab6:
    st.write("mmm")

st.caption('Copyright © Rizqy Mubarok 2024')   



