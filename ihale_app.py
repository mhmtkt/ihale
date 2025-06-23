import streamlit as st
from datetime import datetime
import pandas as pd

# --- Kullanıcı Yönetimi: Kayıt & Giriş ---
if 'users' not in st.session_state:
    st.session_state.users = {"kanka": "1234"}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def register():
    st.subheader("Kayıt Ol")
    new_user = st.text_input("Yeni Kullanıcı Adı", key="register_user")
    new_pass = st.text_input("Yeni Şifre", type="password", key="register_pass")
    if st.button("Kayıt Ol"):
        if new_user in st.session_state.users:
            st.error("Bu kullanıcı adı zaten var!")
        elif new_user.strip() == "" or new_pass.strip() == "":
            st.error("Lütfen kullanıcı adı ve şifre girin!")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")

def login():
    st.subheader("Giriş Yap")
    username = st.text_input("Kullanıcı Adı", key="login_user")
    password = st.text_input("Şifre", type="password", key="login_pass")
    if st.button("Giriş"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = username
        else:
            st.error("Hatalı kullanıcı adı veya şifre")

if not st.session_state.logged_in:
    st.title("İhale Takip Uygulaması - Giriş / Kayıt")
    col1, col2 = st.columns(2)
    with col1:
        register()
    with col2:
        login()
    st.stop()

# --- Session State Başlat ---
if 'arac_listesi' not in st.session_state:
    st.session_state.arac_listesi = []

if 'dorse_sayisi' not in st.session_state:
    st.session_state.dorse_sayisi = 0

if 'sofor_maaslari' not in st.session_state:
    st.session_state.sofor_maaslari = []

if 'bakim_giderleri' not in st.session_state:
    st.session_state.bakim_giderleri = []

if 'arac_alimlari' not in st.session_state:
    st.session_state.arac_alimlari = []

if 'arac_satimlari' not in st.session_state:
    st.session_state.arac_satimlari = []

if 'ihaleler' not in st.session_state:
    st.session_state.ihaleler = []

if 'garaj_seviyesi' not in st.session_state:
    st.session_state.garaj_seviyesi = 0

if 'garaj_harcamasi' not in st.session_state:
    st.session_state.garaj_harcamasi = 0.0

if 'garaj_bakimi' not in st.session_state:
    st.session_state.garaj_bakimi = 0.0

# --- Sol Menü (Sidebar) ---
menu = st.sidebar.radio("Sayfalar", ["Mevcut Durum", "İhale & Operasyonel Maliyetler", "Özet & Grafikler"])

# ---------------------- MEVCUT DURUM ----------------------
if menu == "Mevcut Durum":
    st.header("Mevcut Durumunuzu Girin")
    with st.form("durum_form"):
        garaj_seviyesi = st.number_input("Garaj Seviyesi", min_value=0, step=1, value=st.session_state.garaj_seviyesi)
        arac_sayisi = st.number_input("Araç Sayısı", min_value=0, step=1, value=len(st.session_state.arac_listesi))
        dorse_sayisi = st.number_input("Dorse Sayısı", min_value=0, step=1, value=st.session_state.dorse_sayisi)

        arac_isimleri = []
        for i in range(arac_sayisi):
            default_isim = st.session_state.arac_listesi[i] if i < len(st.session_state.arac_listesi) else ""
            isim = st.text_input(f"Araç {i+1} ismi (örn: Ats-2945)", value=default_isim, key=f"arac_{i}")
            arac_isimleri.append(isim)

        durum_submit = st.form_submit_button("Kaydet")

    if durum_submit:
        st.session_state.garaj_seviyesi = garaj_seviyesi
        st.session_state.dorse_sayisi = dorse_sayisi
        st.session_state.arac_listesi = [a.strip() for a in arac_isimleri if a.strip() != ""]
        st.success("Mevcut durum güncellendi!")

    st.write(f"**Garaj Seviyesi:** {st.session_state.garaj_seviyesi}")
    st.write(f"**Araç Sayısı:** {len(st.session_state.arac_listesi)}")
    st.write(f"**Dorse Sayısı:** {st.session_state.dorse_sayisi}")

# --------------- İHALE VE OPERASYONEL MALİYETLER ---------------

elif menu == "İhale & Operasyonel Maliyetler":
    # --- İhale Ekle ---
    st.header("İhale Ekle")
    with st.form("ihale_form"):
        ihale_turu = st.text_input("İhale Türü (örn: Kimyasal)")
        ihale_tutari = st.number_input("İhale Tutarı (Milyon Dolar)", min_value=0.0, format="%.2f")
        urun_miktari = st.number_input("İhale Taşınan Ürün Miktarı (Adet)", min_value=0, step=1)
        birim_maliyet = st.number_input("İhale Taşınan Ürün Birim Maliyeti (Dolar)", min_value=0.0, format="%.2f")
        ihale_submit = st.form_submit_button("İhale Ekle")

    if ihale_submit:
        yeni_ihale = {
            "tarih": datetime.now(),
            "ihale_turu": ihale_turu,
            "ihale_tutari": ihale_tutari,
            "urun_miktari": urun_miktari,
            "birim_maliyet": birim_maliyet,
            "toplam_maliyet": urun_miktari * birim_maliyet,
            "kar": ihale_tutari - (urun_miktari * birim_maliyet)
        }
        st.session_state.ihaleler.append(yeni_ihale)
        st.success("İhale başarıyla eklendi!")

    st.markdown("---")

    # --- Operasyonel Maliyetler ---
    st.header("Operasyonel Maliyetler")

    # 1. Şoför Maaşı Ekle
    with st.expander("Şoför Maaşı Ekle"):
        isim = st.text_input("Şoför Adı", key="sofor_adi")
        maas = st.number_input("Maaş (Dolar)", min_value=0.0, format="%.2f", key="sofor_maas")
        if st.button("Ekle", key="sofor_ekle"):
            if isim and maas > 0:
                st.session_state.sofor_maaslari.append({"isim": isim, "maas": maas})
                st.success(f"{isim} için maaş eklendi.")
            else:
                st.error("Lütfen isim ve maaş giriniz.")

    # 2. Araç Bakım Gideri Ekle
    with st.expander("Araç Bakım Gideri Ekle"):
        if st.session_state.arac_listesi:
            arac_secim = st.selectbox("Araç Seçin", st.session_state.arac_listesi)
            bakim_tutar = st.number_input("Bakım Maliyeti (Dolar)", min_value=0.0, format="%.2f", key="bakim_tutar")
            if st.button("Bakım Gideri Ekle", key="bakim_ekle"):
                if bakim_tutar > 0:
                    st.session_state.bakim_giderleri.append({"arac": arac_secim, "maliyet": bakim_tutar})
                    st.success(f"{arac_secim} için bakım maliyeti eklendi.")
                else:
                    st.error("Geçerli bakım maliyeti giriniz.")
        else:
            st.info("Önce araç ekleyin.")

    # 3. Yeni Araç Alımı
    with st.expander("Yeni Araç Alımı"):
        yeni_arac_adi = st.text_input("Araç Adı", key="yeni_arac_adi")
        arac_alim_fiyati = st.number_input("Alış Fiyatı (Dolar)", min_value=0.0, format="%.2f", key="arac_alim_fiyat")
        if st.button("Araç Ekle", key="arac_ekle"):
            if yeni_arac_adi and arac_alim_fiyati > 0:
                st.session_state.arac_listesi.append(yeni_arac_adi)
                st.session_state.arac_alimlari.append({"arac": yeni_arac_adi, "fiyat": arac_alim_fiyati})
                st.success(f"{yeni_arac_adi} aracı eklendi.")
            else:
                st.error("Araç adı ve fiyatını giriniz.")

    # 4. Dorse Alımı
    with st.expander("Dorse Alımı"):
        dorse_tipi = st.text_input("Dorse Tipi", key="dorse_tipi")
        dorse_alim_fiyati = st.number_input("Alış Fiyatı (Dolar)", min_value=0.0, format="%.2f", key="dorse_alim_fiyat")
        if st.button("Dorse Ekle", key="dorse_ekle"):
            if dorse_tipi and dorse_alim_fiyati > 0:
                st.session_state.dorse_sayisi += 1
                st.success(f"{dorse_tipi} dorsesi eklendi.")
            else:
                st.error("Dorse tipi ve fiyatını giriniz.")

    # 5. Araç Satımı
    with st.expander("Araç Satımı"):
        if st.session_state.arac_listesi:
            arac_satim_secim = st.selectbox("Satılacak Aracı Seçin", st.session_state.arac_listesi, key="arac_satim_secim")
            arac_satim_fiyati = st.number_input("Satış Fiyatı (Dolar)", min_value=0.0, format="%.2f", key="arac_satim_fiyat")
            if st.button("Araç Sat", key="arac_sat_button"):
                if arac_satim_fiyati > 0:
                    st.session_state.arac_listesi.remove(arac_satim_secim)
                    st.session_state.arac_satimlari.append({"arac": arac_satim_secim, "fiyat": arac_satim_fiyati})
                    st.success(f"{arac_satim_secim} satıldı.")
                else:
                    st.error("Satış fiyatı giriniz.")
        else:
            st.info("Satılacak araç yok.")

    # 6. Garaj Yükseltme
    with st.expander("Garaj Yükseltme"):
        yeni_garaj_seviye = st.number_input("Yeni Garaj Seviyesi", min_value=0, step=1, value=st.session_state.garaj_seviyesi, key="yeni_garaj_seviye")
        harcanan_tutar = st.number_input("Harcanan Tutar (Milyon Dolar)", min_value=0.0, format="%.2f", key="garaj_harcanan")
        if st.button("Garajı Yükselt", key="garaj_yukselt"):
            st.session_state.garaj_seviyesi = yeni_garaj_seviye
            st.session_state.garaj_harcamasi = harcanan_tutar
            st.success(f"Garaj seviyesi {yeni_garaj_seviye} olarak güncellendi.")

    # 7. Garaj Bakımı Maliyeti
    with st.expander("Garaj Bakımı Maliyeti Ekle"):
        bakim_tutari = st.number_input("Garaj Bakımı İçin Ödenen Tutar (Dolar)", min_value=0.0, format="%.2f", key="garaj_bakim_tutari")
        if st.button("Garaj Bakımı Maliyeti Kaydet", key="garaj_bakim_kaydet"):
            st.session_state.garaj_bakimi = bakim_tutari
            st.success(f"Garaj bakım maliyeti {bakim_tutari:.2f} $ olarak kaydedildi.")

# ---------------------- ÖZET & GRAFİKLER ----------------------
elif menu == "Özet & Grafikler":
    st.header("Özet ve Grafikler")

    # Önce ihaleleri DataFrame yap
    if len(st.session_state.ihaleler) == 0:
        st.info("Henüz ihale girişi yok.")
        filtre = pd.DataFrame(columns=['kar', 'ihale_tutari', 'toplam_maliyet', 'ihale_turu', 'tarih'])
    else:
        df_ihale = pd.DataFrame(st.session_state.ihaleler)
        df_ihale['tarih'] = pd.to_datetime(df_ihale['tarih'])

        secim = st.selectbox("Rapor Tipi", ["Günlük", "Haftalık", "Aylık"])
        now = datetime.now()

        if secim == "Günlük":
            filtre = df_ihale[df_ihale['tarih'].dt.date == now.date()]
        elif secim == "Haftalık":
            filtre = df_ihale[df_ihale['tarih'].dt.isocalendar().week == now.isocalendar()[1]]
        else:
            filtre = df_ihale[df_ihale['tarih'].dt.month == now.month]

        st.subheader(f"{secim} İhale Verileri")
        st.write(f"Toplam İhale Sayısı: {len(filtre)}")
        st.write(f"Toplam İhale Tutarı (Milyon Dolar): {filtre['ihale_tutari'].sum():.2f}")
        st.write(f"Toplam Ürün Maliyeti (Dolar): {filtre['toplam_maliyet'].sum():.2f}")
        st.write(f"Toplam İhale Karı (Milyon Dolar): {filtre['kar'].sum():.2f}")

        st.write("İhale Türü Sayıları:")
        st.write(filtre['ihale_turu'].value_counts())

    # Toplam Operasyonel Maliyetler
    toplam_sofor_maasi = sum([m['maas'] for m in st.session_state.sofor_maaslari])
    toplam_bakim_gideri = sum([b['maliyet'] for b in st.session_state.bakim_giderleri])
    toplam_arac_alim = sum([a['fiyat'] for a in st.session_state.arac_alimlari])
    toplam_arac_satim = sum([s['fiyat'] for s in st.session_state.arac_satimlari])
    garaj_harcamasi = st.session_state.garaj_harcamasi * 1_000_000  # milyon dolar -> dolar
    garaj_bakim_maliyeti = st.session_state.garaj_bakimi

    st.markdown("---")
    st.subheader("Operasyonel Maliyetler (Dolar)")
    st.write(f"Toplam Şoför Maaşları: {toplam_sofor_maasi:.2f} $")
    st.write(f"Toplam Araç Bakım Giderleri: {toplam_bakim_gideri:.2f} $")
    st.write(f"Toplam Araç Alım Maliyeti: {toplam_arac_alim:.2f} $")
    st.write(f"Toplam Araç Satış Gelirleri: {toplam_arac_satim:.2f} $")
    st.write(f"Garaj Yükseltme Harcaması: {garaj_harcamasi:.2f} $")
    st.write(f"Garaj Bakımı Maliyeti: {garaj_bakim_maliyeti:.2f} $")

    # Net Kar Hesaplama
    toplam_ihale_kar = filtre['kar'].sum() * 1_000_000 if not filtre.empty else 0  # milyon dolar -> dolar
    toplam_operasyonel_gider = toplam_sofor_maasi + toplam_bakim_gideri + toplam_arac_alim + garaj_harcamasi + garaj_bakim_maliyeti
    net_kar = toplam_ihale_kar + toplam_arac_satim - toplam_operasyonel_gider

    st.markdown("---")
    st.subheader(f"Net Kar (Dolar): {net_kar:.2f} $")

    # Grafikler
    try:
        import matplotlib.pyplot as plt

        labels = ['Şoför Maaşları', 'Araç Bakım', 'Araç Alımı', 'Garaj Yükseltme', 'Garaj Bakımı', 'Araç Satış Geliri']
        giderler = [toplam_sofor_maasi, toplam_bakim_gideri, toplam_arac_alim, garaj_harcamasi, garaj_bakim_maliyeti, -toplam_arac_satim]

        fig, ax = plt.subplots()
        ax.bar(labels, giderler, color=['red', 'orange', 'blue', 'purple', 'green', 'gray'])
        ax.set_ylabel('Dolar')
        ax.set_title('Operasyonel Giderler ve Araç Satış Geliri (Negatif Değer)')
        plt.xticks(rotation=30)
        st.pyplot(fig)
    except ImportError:
        st.info("Grafikler için matplotlib kütüphanesi gerekli.")
