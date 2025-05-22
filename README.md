# Sürücü Yorgunluk ve Duygu Durumu İzleme Sistemi

Bu proje, otonom araçlarda ve sürücü destek sistemlerinde kullanılmak üzere, sürücülerin yorgunluk belirtilerini ve genel duygu durumlarını analiz ederek güvenli sürüşü sağlamak amacıyla geliştirilmiş bir Python tabanlı uygulamadır. Sistem, kameradan alınan görüntüleri kullanarak yorgunluk belirtilerini tespit eder ve sesli uyarılarla sürücüye geri bildirim sağlar.

## Projenin Amacı

Trafik kazalarının önemli bir kısmı, sürücünün yorgunluk veya dikkat dağınıklığı nedeniyle gerçekleşmektedir. Bu proje, otonom araçlarda ve sürücü destek sistemlerinde:
- **Göz kapanma süresini ölçerek** sürücünün uyuklama durumunu algılar.
- **Kafa pozisyonunu analiz ederek** dikkat dağınıklığına işaret eden kafa hareketlerini tespit eder.
- **Esneme tespiti yaparak** sürücünün yorgunluk belirtilerini izler.
- **Sesli uyarılar vererek** sürücünün dikkatini tekrar toplamasına yardımcı olur.

Kullanılan eşik değerler, uluslararası akademik çalışmalar ve tezlerden alınan bilimsel verilere dayanmaktadır. Bu, algoritmanın hassasiyetini ve doğruluğunu artırmak için önemli bir adım teşkil eder.

## Örnek Kullanım Senaryosu ve Sistem Testi

[Sistem Testi Videosunu İzlemek için Tıklayınız](https://drive.google.com/file/d/198FS9jOuJ1eHVdP3FZgIxpNdNBbEzDeD/view?usp=sharing)

## Özellikler

- **Göz Kapanma Tespiti:** Eye Aspect Ratio (EAR) algoritması ile sürücünün göz kapanma süresi hesaplanır. Uzun süreli göz kapanmaları algılanır ve uyarı verilir.
- **Kafa Hareketi Analizi:** 3D kafa pozisyonu hesaplaması ile sürücünün kafa eğim açıları analiz edilir. Aşırı sağa, sola, öne veya arkaya eğilme durumlarında uyarı sağlar.
- **Esneme Algılama:** Ağız açıklık oranını analiz ederek sürücünün esneme durumunu tespit eder.
- **Dinamik Eşik Değer Ayarları:** Sistem, son 5 dakikadaki yorgunluk belirtilerine göre eşik değerlerini otomatik olarak ayarlar.
- **Sesli Uyarı Sistemi:** Tespit edilen belirtiler doğrultusunda sesli uyarılar verir ve uyarı devam ettiği sürece belirli aralıklarla tekrar eder.

## Gereksinimler

Uygulamanın çalışabilmesi için aşağıdaki kütüphanelerin kurulu olması gerekmektedir:

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy
- Pygame

Gerekli kütüphaneleri yüklemek için aşağıdaki komutu çalıştırabilirsiniz:

```bash
pip install opencv-python mediapipe numpy pygame
```

## Kullanım

1. **Proje Dosyalarını İndirin:** Proje dosyalarını bu repo üzerinden bilgisayarınıza indirin.
2. **Ses Dosyasını Ekleyin:** `warning.wav` dosyasını proje dizinine yerleştirin. Bu dosya uyarılar için kullanılacaktır.
3. **Uygulamayı Çalıştırın:** Aşağıdaki komut ile uygulamayı çalıştırın:
   ```bash
   python main.py
   ```
4. **Kamera İzni Verin:** Uygulama, kameranıza erişim isteyecektir. İzin vererek video akışını başlatın.
5. **Uyarıları İzleyin:** Sistem yorgunluk veya dikkat dağınıklığı belirtilerini algıladığında ekranda uyarı mesajları görüntüler ve sesli uyarı verir.

## Yapılandırma

- **Eşik Değerleri Düzenleme:** Kodda aşağıdaki değişkenleri düzenleyerek uygulamanın hassasiyetini ayarlayabilirsiniz:
  - `EAR_THRESHOLD`: Göz kapanma algılama eşiği.
  - `HEAD_HORIZONTAL_THRESHOLD` ve `HEAD_VERTICAL_THRESHOLD`: Kafa eğim eşikleri.
  - `YAWN_THRESHOLD`: Esneme oranı algılama eşiği.

- **Ses Dosyası:** `warning.wav` dosyasını dilediğiniz bir ses dosyası ile değiştirebilirsiniz.

## Çalışma Prensibi

1. **MediaPipe FaceMesh:** Yüzdeki önemli noktaları (landmarks) tespit eder.
2. **EAR Hesaplama:** Göz kapanma oranını hesaplar ve belirtilen eşik değerinin altına düştüğünde uyarı verir.
3. **Kafa Pozisyonu Analizi:** Kafa eğim açılarını analiz ederek dikkat dağınıklığını algılar.
4. **Esneme Tespiti:** Ağız açıklık oranını analiz ederek yorgunluk belirtilerini izler.
5. **Sesli Uyarı:** Algılanan belirtiler doğrultusunda sesli uyarılar verir.

Kullanılan algoritmaların eşik değerleri, akademik araştırmalar ve uluslararası standartlar dikkate alınarak belirlenmiştir.

## Örnek Çıktılar

- **Normal Durum:** Ekranda "Durum: Normal" mesajı görüntülenir.
- **Yorgunluk Algılandığında:**
  - "UYARI: Yorgunluk Algilandi!"
  - "UYARI: Kafa SAGA Egik (45 derece)" gibi mesajlar ekranda görüntülenir.
  - Sesli bir uyarı çalar.

## Sınırlamalar ve Geliştirme Fırsatları

- **Karanlık Ortamlar:** Sistem, iyi bir aydınlatma gerektirir. Karanlık ortamlarda doğruluk düşebilir.
- **Duygu Durumu Analizi:** Ek olarak sürücünün genel ruh hali ve stres seviyesinin izlenmesi için geliştirme yapılabilir.
- **Otonom Araç Entegrasyonu:** Sistem, otonom araçların sürücü destek modüllerine entegre edilerek daha kapsamlı bir güvenlik çözümü sunabilir.

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## İletişim

Sorularınız veya önerileriniz için aşağıdaki kanallardan benimle iletişime geçebilirsiniz:

- **GitHub:** [alicanaltun](https://github.com/alicanaltun)
- **E-posta:** [alicanaltun61@gmail.com](mailto:alicanaltun61@gmail.com)
