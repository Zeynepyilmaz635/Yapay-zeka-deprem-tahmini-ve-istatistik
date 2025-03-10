
import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout
import sys
import time
import re

class Proje(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Deprem verilerini çek
        self.deprem_df = self.deprem_verisi_cek()

        # Şehir verisini çek
        self.sehir_df = self.sehir_verisi_cek()

        # Veriler başarılı çekildiyse işleme devam et
        if self.deprem_df is not None:
            self.deprem_df = self.veri_duzenle(self.deprem_df)
            print("Düzenlenmiş Deprem Verisi:\n", self.deprem_df.head())
        else:
            print("Deprem verileri çekilemedi.")

    def init_ui(self):
        # Kullanıcıdan şehir ismi almak için UI elemanları ekleyelim
        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Şehir ismi girin")
        self.search_button = QPushButton("Depremleri Göster", self)
        self.search_button.clicked.connect(self.son_1_hafta_depremleri)

        # Grafik için Canvas widget
        self.canvas = FigureCanvas(plt.figure())

        v_box = QVBoxLayout()
        v_box.addWidget(self.city_input)
        v_box.addWidget(self.search_button)
        v_box.addWidget(self.canvas)

        self.setLayout(v_box)
        self.setWindowTitle("Deprem Verisi")
        self.setGeometry(100, 100, 800, 600)
        self.show()

    def deprem_verisi_cek(self):
        url = "http://www.koeri.boun.edu.tr/scripts/lst1.asp"
        retries = 3
        for _ in range(retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                pre_tags = soup.find_all('pre')

                if pre_tags:
                    pre_text = pre_tags[0].get_text()
                    lines = pre_text.strip().split('\n')
                    data = [line.split() for line in lines if line]
                    df = pd.DataFrame(data)
                    df.to_csv('deprem.csv', index=False, header=False)
                    print("Deprem verileri başarıyla 'deprem.csv' dosyasına yazıldı.")
                    return df
                else:
                    print("Hiçbir <pre> etiketi bulunamadı.")
                    return None
            except requests.RequestException as e:
                print(f"Deprem verilerini çekerken hata oluştu: {e}")
                time.sleep(5)  # Bekleyip tekrar deneyelim
        return None

    def sehir_verisi_cek(self):
        url = "http://www.beycan.net/1057/illerin-enlem-ve-boylamlari.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table')

            if table:
                sehir_data = []
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        sehir = cols[1].text.strip()
                        enlem = cols[2].text.strip().replace(',', '.')
                        boylam = cols[3].text.strip().replace(',', '.')
                        sehir_data.append([sehir, enlem, boylam])
                df = pd.DataFrame(sehir_data, columns=['Şehir', 'Enlem', 'Boylam'])
                df.to_csv('sehirler_enlem_boylam.csv', index=False)
                print("Şehir verileri başarıyla 'sehirler_enlem_boylam.csv' dosyasına yazıldı.")
                return df
            else:
                print("Şehir tablosu bulunamadı.")
        except requests.RequestException as e:
            print(f"Şehir verilerini çekerken hata oluştu: {e}")
        return None

    def veri_duzenle(self, df):
        # İlgili sütun isimleriyle DataFrame'i düzenleyelim
        df = df.drop(index=[0, 1, 2, 3, 4]).reset_index(drop=True)
        df = df.drop(index=1).reset_index(drop=True)
        df = df[~df[0].isin(['----------', '--------'])]
        df = df.rename(columns={ 
            df.columns[0]: 'Tarih', df.columns[1]: 'Saat', df.columns[2]: 'Enlem',
            df.columns[3]: 'Boylam', df.columns[4]: 'Derinlik', df.columns[5]: 'MD',
            df.columns[6]: 'ML', df.columns[7]: 'Mw', df.columns[8]: 'Yer',
            df.columns[9]: 'Cozum', df.columns[10]: 'Nitelik'
        })

        # 'Tarih' formatını düzelt
        df['Tarih'] = pd.to_datetime(df['Tarih'], format='%Y.%m.%d')

        # 'Yer' sütunundaki parantez içeriğini ve - işaretiyle ayırma
        def ayracla_ayir(yer):
            # İlk olarak parantez içindekileri alıyoruz
            parantez_icerigi = re.findall(r'\((.*?)\)', yer)
            yer_parantez = parantez_icerigi[0] if parantez_icerigi else None
            yer_bolunmus = re.split(r'[-()]', yer)
            yer_bolunmus = [i.strip() for i in yer_bolunmus if i.strip()]
            return yer_bolunmus, yer_parantez

        df[['Yer_Split', 'Yer_Parantez']] = df['Yer'].apply(lambda x: pd.Series(ayracla_ayir(x)))

        df['Yer_1'] = df['Yer_Split'].apply(lambda x: x[0] if len(x) > 0 else None)
        df['Yer_2'] = df['Yer_Split'].apply(lambda x: x[1] if len(x) > 1 else None)
        df['Yer_3'] = df['Yer_Split'].apply(lambda x: x[2] if len(x) > 2 else None)
        df['Yer_Parantez'] = df['Yer_Parantez'].fillna('')

        df = df.drop(columns=['Yer_Split'])

        return df

    def son_1_hafta_depremleri(self):
        user_city = self.city_input.text()

        if self.deprem_df is None:
            print("Deprem verileri bulunamadı. Lütfen tekrar deneyin.")
            return

        # Şu anki tarihten bir hafta öncesine kadar olan verileri filtrele
        one_week_ago = datetime.now() - timedelta(weeks=1)
        self.deprem_df['Tarih'] = pd.to_datetime(self.deprem_df['Tarih'], format='%d.%m.%Y')
        last_week_df = self.deprem_df[self.deprem_df['Tarih'] >= one_week_ago]

        last_week_df['Yer'] = last_week_df['Yer'].apply(lambda x: x.split('-') if isinstance(x, str) else [])
        filtered_df = last_week_df[last_week_df['Yer'].apply(lambda x: any(user_city.lower() in city.lower() for city in x))]

        if not filtered_df.empty:
            self.grafik_yap(filtered_df)
        else:
            print(f"{user_city} için son 1 haftada deprem verisi bulunamadı.")

    def grafik_yap(self, df):
        print(f"Veri tipi kontrolü - Tarih: {df['Tarih'].dtype}, ML: {df['ML'].dtype}")

        df = df.dropna(subset=['ML'])

        # Grafik oluşturma
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.scatter(df['Tarih'], df['ML'], label='Deprem Büyüklüğü', color='red')
        ax.set_title('Son 1 Haftadaki Depremler')
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Büyüklük (ML)')
        plt.xticks(rotation=45)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    proje = Proje()
    sys.exit(app.exec_())
