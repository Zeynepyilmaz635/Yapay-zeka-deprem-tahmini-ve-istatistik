# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 04:27:56 2024

@author: pc
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QMouseEvent
class Proje(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.city_map = [
            ("ADANA", 506,387,  5,22),  # (name, x, y, width, height)
            ("ADIYAMAN", 659,331, 32,7),
            ("AFYONKARAHİSAR", 257,267, 34,22),
            ("AĞRI" , 895,184,22,11),
            ("AKSARAY" , 437,298,17,20),
            ("AMASYA" , 528,147,20,8),
            ("ANKARA" , 379,194,24,44),
            ("ANTALYA" , 264,390,49,2),
            ("ARDAHAN" , 869,97,9,11), 
            ("ARTVİN" , 825,96,15,13),
            ("AYDIN" , 115,320,30,3),
            ("BALIKESİR" ,123,203,20,16 ),
            ("BARTIN" , 355,81,8,3),
            ("BATMAN" , 808,315,1,10),  
            ("BAYBURT" , 750, 165,10,7), 
            ("BİLECİK" ,  231, 175,4,9),
            ("BİNGÖL" , 770, 253,4,13),
            ("BİTLİS" , 856, 276,7,9),
            ("BOLU" , 316, 139,8,3),
            ("BURDUR" ,236, 350,19,11),
            ("BURSA" , 187, 171,24,8),
            ("ÇANAKKALE" , 74, 171,22,17),
            ("ÇANKIRI" , 416, 152,18,9),
            ("ÇORUM" , 466, 150,22,3), 
            ("DENİZLİ" ,  180, 332,11,29), 
            ("DİYARBAKIR" , 759, 317,25,8),
            ("DÜZCE" , 293, 134,9,9),
            ("EDİRNE" ,67, 64,16,9 ),
            ("ELAZIĞ" ,703, 271,20,6 ),
            ("ERZİNCAN" ,716, 199,30,6 ),
            ("ERZURUM" ,803, 181,23,28 ),
            ("ESKİŞEHİR" , 273, 210,5,18 ),
            ("GAZİANTEP" ,615, 380,22,4 ),
            ("GİRESUN" , 657, 143,8,19 ),
            ("GÜMÜŞHANE" ,711, 152,8,9 ),
            ("HAKKARİ" ,945, 324,10,9 ),
            ("HATAY" ,550, 438 , 14,24 ),
            ("IĞDIR" ,945, 167,28,9 ),
            ("ISPARTA" ,271, 322,10,12 ),
            ("İSTANBUL" , 183, 114,16,4 ),
            ("İZMİR" ,87, 281,4,28 ),
            ("KAHRAMANMARAŞ" , 589, 347,26,16 ),
            ("KARABÜK" ,366, 109,13,5 ),
            ("KARAMAN" , 394, 376,16,8 ),
            ("KARS" ,890, 128,24,18 ),
            ("KASTAMONU" ,425, 99,18,16 ),
            ("KAYSERİ" ,524, 278,29,15 ),
            ("KIRIKKALE",423, 204,6,6),
            ("KIRKLARELİ",112, 66,21,13),
            ("KIRŞEHİR",441, 237,13,13),
            ("KİLİS",601, 403,12,7),
            ("KOCAELİ",232, 134,15,13),
            ("KONYA",357, 330,38,14),
            ("KÜTAHYA",217, 228,24,21),
            ("MALATYA",643, 284,13,18),
            ("MANİSA",127, 261,23,17),
            ("MARDİN", 789, 353,33,11),
            ("MERSİN",  454, 391,31,5),
            ("MUĞLA",  139, 364,19,16),
            ("MUŞ",839, 242,9,10),
            ("NEVŞEHİR",  473, 284,12,11),
            ("NİĞDE",   471, 322,9,14),
            ("ORDU",  612, 133,23,14),
            ("OSMANİYE",  556, 375,8,11),
            ("RİZE",  781, 116,12,13),
            ("SAKARYA",  261, 138,11,26),
            ("SAMSUN", 540, 112,32,8),
            ("SİİRT",  857, 310,18,12),
            ("SİNOP",  479, 79 ,11,15),
            ("SİVAS",  589, 203,44,11),
            ("ŞANLIURFA", 689, 369,43,12),
            ("ŞIRNAK", 879, 332,24,2),
            ("TEKİRDAĞ",  110, 105,23,6),
            ("TOKAT", 565, 169,17,5),
            ("TRABZON", 724, 124,28,7),
            ("TUNCELİ", 716, 235,22,15),
            ("UŞAK", 199, 270,16,2),
            ("VAN" , 939, 265,28,39 ),
            ("YALOVA" , 199, 142,10,5 ),
            ("YOZGAT" ,  495, 210,33,18 ),
            ("ZONGULDAK" , 326, 100,16,6 ),
            
            
        ]
        
        
        
        
        
        
        
        
        
        # Deprem ve şehir verilerini çek
        self.deprem_df = self.deprem_verisi_cek()
        self.sehir_df = self.sehir_verisi_cek()
        
        # Veriler başarılı çekildiyse işleme devam et
        if self.deprem_df is not None:
            self.deprem_df = self.veri_duzenle(self.deprem_df)
            print("Düzenlenmiş Deprem Verisi:\n", self.deprem_df.head())
        else:
            print("Deprem verileri çekilemedi.")
        
        if self.sehir_df is not None:
            print("Düzenlenmiş Şehir Verisi:\n", self.sehir_df.head())
        else:
            print("Şehir verileri çekilemedi.")


    def init_ui(self):
         self.resim = QLabel()
         self.resim.setPixmap(QPixmap("harita.png"))  # Harita resmini yükle
         v_box = QVBoxLayout()
         v_box.addWidget(self.resim)
         self.setLayout(v_box)
         self.setWindowTitle("Harita Uygulaması")
         self.setGeometry(100, 100, 1014, 479) #  genşlk yükslskl
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
        return df

    def zaman_serisi(self):
        if self.deprem_df is not None:
            self.deprem_df['Tarih_Saat'] = pd.to_datetime(self.deprem_df['Tarih'] + ' ' + self.deprem_df['Saat'], errors='coerce')
            self.deprem_df = self.deprem_df.dropna(subset=['Tarih_Saat', 'ML'])
            self.deprem_df['ML'] = pd.to_numeric(self.deprem_df['ML'], errors='coerce')
            plt.figure(figsize=(12, 6))
            self.deprem_df.set_index('Tarih_Saat')['ML'].plot()
            plt.title('Zaman İçinde Deprem Büyüklüğü')
            plt.xlabel('Tarih ve Saat')
            plt.ylabel('Büyüklük (ML)')
            plt.show()

    def model(self):
        if self.deprem_df is not None:
            self.deprem_df[['Enlem', 'Boylam',  'ML']] = self.deprem_df[['Enlem', 'Boylam', 'ML']].astype(float)
            X = self.deprem_df[['Enlem', 'Boylam']]
            y = self.deprem_df['ML']
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            return model
        
   
    def mousePressEvent(self, event: QMouseEvent):
        x, y = event.x(), event.y()
        print(f"Tıklanan koordinatlar: {x}, {y}")  # Tıklanan koordinatları yazdır
        
        for city, cx, cy, width, height in self.city_map:
            # Tıklanan koordinatların şehir koordinatları ile örtüşüp örtüşmediğini kontrol et
            if cx - width <= x <= cx + width and cy - height <= y <= cy + height:
                QMessageBox.information(self, "Şehir Tıklandı", f"{city} şehrine tıkladınız!")
                print(f"{city} şehrine tıkladınız!")  # Hangi şehir tıklandığını yazdır
                
                # Şehir ismini büyük harflere çevirip kontrol edelim
                city_name = city.upper()
                
                # Şehir verisi var mı kontrol et
                city_bilgi = self.sehir_df[self.sehir_df['Şehir'].str.upper().str.contains(city_name, na=False)]
                
                if city_bilgi.empty:
                    # Eğer şehir için veri yoksa uyarı göster
                    print(f"{city} için deprem verisi bulunamadı.")
                    QMessageBox.warning(self, "Veri Eksik", f"{city} için deprem verisi bulunamadı.")
                else:
                    # Şehrin enlem ve boylam değerlerini al
                    city_enlem = city_bilgi['Enlem'].values[0]
                    city_boylam = city_bilgi['Boylam'].values[0]
    
                    # Kullanıcı verisini oluştur, sadece Enlem ve Boylam'ı içermeliyiz
                    kullanici_veri = pd.DataFrame([[city_enlem, city_boylam]], columns=['Enlem', 'Boylam'])
    
                    # Modelden tahmin yap
                    tahmin = trained_model.predict(kullanici_veri)
                    print(f"{city} için tahmin edilen büyüklük: {tahmin[0]}")
                    QMessageBox.information(self, "Tahmin", f"{city} için tahmin edilen büyüklük: {tahmin[0]}")
                break  # Şehir bulunduğunda döngüyü kır

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    proje = Proje()
    proje.zaman_serisi()
    trained_model = proje.model()
    

    sys.exit(app.exec_())




