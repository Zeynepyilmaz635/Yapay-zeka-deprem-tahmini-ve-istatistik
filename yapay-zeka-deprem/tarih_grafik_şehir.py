import sys
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
from bs4 import BeautifulSoup

# PyQt5 GUI için ana pencere sınıfı
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # GUI penceresinin başlığı ve boyutları
        self.setWindowTitle("PyQt5 & Dash Uygulaması")
        self.setGeometry(100, 100, 800, 600)

        # Layout oluşturma
        layout = QVBoxLayout()

        # QWebEngineView nesnesi, Dash uygulamasını burada gömeceğiz
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Ana pencere için bir widget oluşturuyoruz ve layout ekliyoruz
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Dash uygulamasını başlat
        self.start_dash()

    def start_dash(self):
        # Dash uygulamasını başlatıyoruz
        app_dash = dash.Dash(__name__)

        # Deprem verisi çekme ve düzenleme
        print("DEPREM VERİSİ ÇEK")
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
                deprem_df = pd.DataFrame(data)
                deprem_df.to_csv('deprem.csv', index=False, header=False)
                print("Deprem verileri başarıyla 'deprem.csv' dosyasına yazıldı.")
            else:
                print("Hiçbir <pre> etiketi bulunamadı.")
        except requests.RequestException as e:
            print(f"Deprem verilerini çekerken hata oluştu: {e}")
        
        # Veri düzenleme
        print("VERİYİ DÜZENLE")
        deprem_df = deprem_df.drop(index=[0, 1, 2, 3, 4]).reset_index(drop=True)  # Gereksiz satırları kaldır
        deprem_df = deprem_df.rename(columns={
            deprem_df.columns[0]: 'Tarih', deprem_df.columns[1]: 'Saat', deprem_df.columns[2]: 'Enlem',
            deprem_df.columns[3]: 'Boylam', deprem_df.columns[4]: 'Derinlik', deprem_df.columns[5]: 'MD',
            deprem_df.columns[6]: 'ML', deprem_df.columns[7]: 'Mw', deprem_df.columns[8]: 'Yer',
            deprem_df.columns[9]: 'Cozum', deprem_df.columns[10]: 'Nitelik'
        })

        # 'Tarih' ve 'Saat' sütunlarını birleştirerek 'Tarih_Saat' oluştur
        deprem_df['Tarih_Saat'] = pd.to_datetime(deprem_df['Tarih'] + ' ' + deprem_df['Saat'], errors='coerce')

        # Hatalı verileri kaldır
        deprem_df = deprem_df.dropna(subset=['Tarih_Saat'])

        # Grafik için 'Büyüklük' sütununu kontrol et
        print(deprem_df.head())

        # Plotly scatter grafiği oluşturma (deprem büyüklükleri zaman serisi)
        fig1 = px.scatter(deprem_df, x='Tarih_Saat', y='ML', title="Deprem Büyüklükleri Zaman Serisi",
                         labels={"Tarih_Saat": "Tarih ve Saat", "ML": "Deprem Büyüklüğü (ML)"})

        fig1.update_traces(marker=dict(size=12, color='blue', opacity=0.6, line=dict(width=2, color='DarkSlateGrey')))
        fig1.update_layout(
            hovermode="closest",
            clickmode='event+select',
            xaxis_rangeslider_visible=True,
        )

        # Deprem şehirlerine göre bar grafiği oluşturma (seçilen tarihler arasında hangi şehirlerde ne büyüklükte deprem oldu)
        fig2 = px.bar(deprem_df, x='Yer', y='ML', title="Deprem Büyüklükleri Şehir Bazında",
                      labels={"Yer": "Şehir", "ML": "Deprem Büyüklüğü (ML)"}, 
                      color='ML', color_continuous_scale='Viridis')

        fig2.update_layout(
            xaxis_title="Şehirler",
            yaxis_title="Deprem Büyüklüğü (ML)",
            hovermode="closest",
        )

        # Dash uygulaması layout'u
        app_dash.layout = html.Div([
            # Tarih aralığı seçici (Date Range Picker)
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=deprem_df['Tarih_Saat'].min().strftime('%Y-%m-%d'),
                end_date=deprem_df['Tarih_Saat'].max().strftime('%Y-%m-%d'),
                display_format='YYYY-MM-DD',  # Görünüm formatı
            ),
            dcc.Graph(id='deprem-graph', figure=fig1),
            dcc.Graph(id='city-graph', figure=fig2),  # Şehir bazında deprem büyüklüklerini gösteren grafik
            html.Div(id='depremler-detail')  # Tıklanan tarihe göre detayları göstermek için alan
        ])

        # Callback fonksiyonu: Tarih aralığına göre veriyi filtrele ve grafiği güncelle
        @app_dash.callback(
            [dash.dependencies.Output('deprem-graph', 'figure'),
             dash.dependencies.Output('city-graph', 'figure')],
            [dash.dependencies.Input('date-picker-range', 'start_date'),
             dash.dependencies.Input('date-picker-range', 'end_date')]
        )
        def update_graph(start_date, end_date):
            # Tarih aralığını filtrele
            filtered_df = deprem_df[(deprem_df['Tarih_Saat'] >= start_date) & (deprem_df['Tarih_Saat'] <= end_date)]

            # Yeni figürler oluştur
            fig1 = px.scatter(filtered_df, x='Tarih_Saat', y='ML', title="Deprem Büyüklükleri Zaman Serisi",
                              labels={"Tarih_Saat": "Tarih ve Saat", "ML": "Deprem Büyüklüğü (ML)"})
            fig1.update_traces(marker=dict(size=12, color='blue', opacity=0.6, line=dict(width=2, color='DarkSlateGrey')))
            fig1.update_layout(
                hovermode="closest",
                clickmode='event+select',
                xaxis_rangeslider_visible=True,
            )

            fig2 = px.bar(filtered_df, x='Yer', y='ML', title="Deprem Büyüklükleri Şehir Bazında",
                          labels={"Yer": "Şehir", "ML": "Deprem Büyüklüğü (ML)"}, 
                          color='ML', color_continuous_scale='Viridis')
            fig2.update_layout(
                xaxis_title="Şehirler",
                yaxis_title="Deprem Büyüklüğü (ML)",
                hovermode="closest",
            )

            return fig1, fig2

        # Dash sunucusunu başlatıyoruz
        try:
            app_dash.run_server(port=8051, debug=True, use_reloader=False)
        except OSError as e:
            print(f"Error: {e}")

        # PyQt5 WebEngineView'ye Dash uygulamasının adresini açıyoruz
        self.browser.setUrl(QUrl("http://127.0.0.1:8051"))

# PyQt5 uygulamasını başlatan ana fonksiyon
def main():
    app = QApplication(sys.argv)

    # Ana pencereyi başlat
    window = MyWindow()
    window.show()

    # Uygulamayı çalıştır
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
