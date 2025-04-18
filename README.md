# EduPlus - Dijital Eğitim Platformu

![EduPlus Logo](static/images/logo.png)

## Proje Hakkında

EduPlus, çevrimiçi eğitim ve öğrenme deneyimlerini geliştirmek için tasarlanmış modern bir dijital eğitim platformudur. Kullanıcılar kursları inceleyebilir, kaydolabilir, içeriklere erişebilir ve eğitimlerini takip edebilir.

### Özellikler

- 🎓 **Kapsamlı Kurs Yönetimi**: Kategorilere ayrılmış kurs listesi, detaylı kurs sayfaları
- 👥 **Kullanıcı Rolü Sistemi**: Öğrenci, eğitmen ve yönetici rolleri
- 💳 **Ödeme Entegrasyonu**: Stripe ile güvenli ödeme işlemleri
- 📱 **Duyarlı Tasarım**: Tüm cihazlarda optimal görünüm
- 📊 **Admin Paneli**: Gelişmiş istatistikler ve yönetim araçları
- 🔍 **Arama ve Filtreleme**: Gelişmiş kurs arama ve filtreleme özellikleri

## Teknoloji Yığını

- **Backend**: Django 5.1
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Veritabanı**: PostgreSQL (Üretim), SQLite (Geliştirme)
- **Ödeme Sistemi**: Stripe API
- **Deployment**: Gunicorn, Whitenoise

## Kurulum

### Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)
- PostgreSQL (opsiyonel, geliştirme için SQLite yeterli)

### Kurulum Adımları

1. Repo'yu klonlayın:
   ```bash
   git clone https://github.com/kullanici_adi/digitalEdu.git
   cd digitalEdu
   ```

2. Virtual environment oluşturun ve aktive edin:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Veritabanı migrations'larını uygulayın:
   ```bash
   python manage.py migrate
   ```

5. Statik dosyaları toplayın:
   ```bash
   python manage.py collectstatic
   ```

6. Sunucuyu çalıştırın:
   ```bash
   python manage.py runserver
   ```

7. Tarayıcınızda [http://127.0.0.1:8000](http://127.0.0.1:8000) adresine gidin

### Ortam Değişkenleri (Üretim İçin)

Üretim ortamında aşağıdaki ortam değişkenlerini ayarlayın:

```
DEBUG=False
SECRET_KEY=sizin_gizli_anahtarınız
DATABASE_URL=veritabanı_url_adresi
STRIPE_PUBLIC_KEY=stripe_public_key
STRIPE_SECRET_KEY=stripe_secret_key
```

## Proje Yapısı

```
digitalEdu/
├── core/               # Ana uygulama (ana sayfa, statik sayfalar)
├── courses/            # Kurslarla ilgili tüm işlevler
├── users/              # Kullanıcı yönetimi ve profiller
├── payments/           # Ödeme işlemleri
├── eduplus/            # Proje ayarları
├── static/             # Statik dosyalar (CSS, JS, resimler)
├── templates/          # HTML şablonları
├── media/              # Kullanıcı yüklenen dosyalar
├── manage.py           # Django yönetim betiği
├── requirements.txt    # Python bağımlılıkları
└── README.md           # Proje dokümantasyonu
```

## Kullanım

### Yönetici Hesabı Oluşturma

```bash
python manage.py createsuperuser
```

### Demo Verileri Yükleme

```bash
python manage.py loaddata fixtures/demo_data.json
```

## Geliştirme ve Katkıda Bulunma

1. Yeni bir feature branch oluşturun:
   ```bash
   git checkout -b yeni-ozellik
   ```

2. Değişikliklerinizi commit edin:
   ```bash
   git commit -m "Yeni özellik: açıklama"
   ```

3. Değişikliklerinizi push edin:
   ```bash
   git push origin yeni-ozellik
   ```
<img width="1710" alt="Ekran Resmi 2025-04-18 22 06 18" src="https://github.com/user-attachments/assets/9eb6a30a-f434-4778-a025-74556ea1a93a" />

<img width="1710" alt="Ekran Resmi 2025-04-18 22 06 49" src="https://github.com/user-attachments/assets/4c6891c1-956c-42c2-b15c-ce97757175fc" />

<img width="1710" alt="Ekran Resmi 2025-04-18 22 06 38" src="https://github.com/user-attachments/assets/2d30fada-255e-4b7c-85ad-5addc09e9f10" />

<img width="1710" alt="Ekran Resmi 2025-04-18 22 06 33" src="https://github.com/user-attachments/assets/988577b0-f12f-4d76-9f18-9a12d181fd39" />









