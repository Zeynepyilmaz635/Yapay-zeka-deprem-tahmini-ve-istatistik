import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import sys
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, LSTM
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap

class Proje(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Deprem verilerini çek
        self.deprem_df = self.deprem_verisi_cek()

        # Veriler başarılı çekildiyse işleme devam et
        if self.deprem_df is not None:
            self.deprem_df = self.veri_duzenle(self.deprem_df)
            print("Düzenlenmiş Deprem Verisi:\n", self.deprem_df.head())

            # Yapay sinir ağı ile deprem büyüklüğünü tahmin et
            self.yapay_sinir_aglari_tahmin()

            # Deprem dağılım haritasını CNN ile analiz et
            self.cnn_ile_deprem_haritasi()

            # LSTM ile anomali tespiti yap
            self.lstm_anomali_tespiti()
        else:
            print("Deprem verileri çekilemedi.")

    def init_ui(self):
        self.setWindowTitle('Deprem Analizi')
        self.layout = QVBoxLayout()
        self.label = QLabel('Deprem Verisi Analizi')
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
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
    
        # Hatalı değerleri kaldırma
        for col in ['Enlem', 'Boylam', 'Derinlik', 'Mw']:
            df = df[df[col] != '-.-']
    
        # Gerekli sütunları seçip float türüne dönüştürme
        df = df[['Enlem', 'Boylam', 'Derinlik', 'Mw']].astype(float)
    
        return df


    def yapay_sinir_aglari_tahmin(self):
        X = self.deprem_df[['Enlem', 'Boylam', 'Derinlik']]
        y = self.deprem_df['Mw']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = Sequential([
            Dense(64, activation='relu', input_shape=(3,)),
            Dense(64, activation='relu'),
            Dense(1)
        ])

        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test))

        loss, mae = model.evaluate(X_test, y_test)
        print(f"Test MAE: {mae}")

    def cnn_ile_deprem_haritasi(self):
        plt.figure(figsize=(8, 6))
        plt.scatter(self.deprem_df['Boylam'], self.deprem_df['Enlem'], c=self.deprem_df['Mw'], cmap='hot', s=10)
        plt.colorbar(label='Magnitude (Mw)')
        plt.xlabel('Boylam')
        plt.ylabel('Enlem')
        plt.title('Deprem Dağılım Haritası')
        plt.savefig('deprem_haritasi.png')
        plt.show()

    def lstm_anomali_tespiti(self):
        X = self.deprem_df[['Mw']].values.reshape(-1, 1)
        X_train = X[:-20]
        X_test = X[-20:]

        model = Sequential([
            LSTM(50, activation='relu', input_shape=(1, 1)),
            Dense(1)
        ])

        model.compile(optimizer='adam', loss='mse')
        X_train = X_train.reshape((X_train.shape[0], 1, 1))
        model.fit(X_train, X_train, epochs=300, verbose=0)

        X_test = X_test.reshape((X_test.shape[0], 1, 1))
        predictions = model.predict(X_test)

        plt.plot(range(len(X_test)), X_test.flatten(), label='Gerçek Veriler')
        plt.plot(range(len(predictions)), predictions.flatten(), label='Tahminler', linestyle='dashed')
        plt.legend()
        plt.title('LSTM ile Anomali Tespiti')
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    proje = Proje()
    sys.exit(app.exec_()) 