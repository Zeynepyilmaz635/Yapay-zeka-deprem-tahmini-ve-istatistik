import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QDate
import sys

class Proje(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Deprem ve şehir verilerini çek
        self.deprem_df = self.deprem_verisi_cek()

        # Veriler başarılı çekildiyse işleme devam et
        if self.deprem_df is not None:
            self.deprem_df = self.veri_duzenle(self.deprem_df)
            print("Düzenlenmiş Deprem Verisi:\n", self.deprem_df.head())
        else:
            print("Deprem verileri çekilemedi.")

    def init_ui(self):
        # Başlangıç ve Bitiş Tarihi Seçimi
        self.baslangic_tarihi = QDateEdit(calendarPopup=True)
        self.baslangic_tarihi.setDate(QDate.currentDate().addDays(-30))

        self.bitis_tarihi = QDateEdit(calendarPopup=True)
        self.bitis_tarihi.setDate(QDate.currentDate())

        # Grafik Göster Butonu
        self.grafik_buton = QPushButton("Grafiği Göster")
        self.grafik_buton.clicked.connect(self.grafik_goster)

        # Layout Yapılandırması
        h_box = QHBoxLayout()
        h_box.addWidget(QLabel("Başlangıç Tarihi:"))
        h_box.addWidget(self.baslangic_tarihi)
        h_box.addWidget(QLabel("Bitiş Tarihi:"))
        h_box.addWidget(self.bitis_tarihi)
        h_box.addWidget(self.grafik_buton)

        v_box = QVBoxLayout()
        v_box.addLayout(h_box)

        # Grafiği gösterecek alan
        self.canvas = FigureCanvas(plt.figure(figsize=(10, 6)))
        v_box.addWidget(self.canvas)

        self.setLayout(v_box)
        self.setWindowTitle("Tarih Seçim ve Grafik Uygulaması")
        self.setGeometry(100, 100, 800, 600)
        self.show()

    def deprem_verisi_cek(self):
        url = "http://www.koeri.boun.edu.tr/scripts/lst1.asp"
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
        except requests.RequestException as e:
            print(f"Deprem verilerini çekerken hata oluştu: {e}")
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

        # Tarih sütununu Timestamp'e dönüştür
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
        
        return df

    def grafik_goster(self):
        baslangic = self.baslangic_tarihi.date().toPyDate()
        bitis = self.bitis_tarihi.date().toPyDate()

        if baslangic > bitis:
            QMessageBox.warning(self, "Geçersiz Tarih Aralığı", "Başlangıç tarihi, bitiş tarihinden sonra olamaz!")
            return

        # Seçilen tarih aralığına göre veriyi filtrele
        filtrelenmis_veri = self.deprem_df[(self.deprem_df['Tarih'] >= pd.Timestamp(baslangic)) &
                                           (self.deprem_df['Tarih'] <= pd.Timestamp(bitis))]

        if filtrelenmis_veri.empty:
            QMessageBox.warning(self, "Veri Yok", "Bu tarih aralığında veri bulunmamaktadır.")
            return

        # Grafiği çiz
        self.canvas.figure.clf()  # Önceki grafiği temizle
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(filtrelenmis_veri['Tarih'], filtrelenmis_veri['ML'], marker='o', linestyle='-')
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Şehir Büyüklüğü')
        ax.set_title('Seçilen Tarih Aralığındaki Şehir Büyüklükleri')
        ax.grid(True)
        plt.xticks(rotation=45)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = Proje()
    sys.exit(app.exec_())
