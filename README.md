<div align="center">

<h1>🧠 AI CV Analiz Uzmanı</h1>

<strong>🚀 Google Gemini & Ollama (Yerel AI) ile Güçlendirilmiş Akıllı İşe Alım Asistanı</strong>

</div>

<div align="center">

<img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Streamlit-Frontend-red?style=for-the-badge&logo=streamlit&logoColor=white" />
<img src="https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/Ollama-Local%20AI-black?style=for-the-badge&logo=ollama&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" />

</div>

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=24&duration=3000&pause=1000&color=333333&center=true&vCenter=true&width=900&lines=Yapay+Zeka+Destekli+CV+Analizi;Google+Gemini+ve+Ollama+Deste%C4%9Fi;PDF,+DOCX,+TXT,+CSV+Okuma;Otomatik+Puanlama+ve+S%C4%B1ralama" alt="Typing SVG" />

---

## 🎯 Proje Hakkında
Bu proje, işe alım süreçlerini hızlandırmak ve daha objektif değerlendirmeler yapmak için geliştirilmiş bir yapay zeka asistanıdır. Adayların CV'lerini (PDF, DOCX, TXT, CSV) analiz eder, verilen iş tanımıyla karşılaştırır ve detaylı bir uyum raporu sunar.

Hem bulut tabanlı **Google Gemini** hem de tamamen yerel ve gizlilik odaklı **Ollama** modellerini destekler.

<div align="center">
<img src="/images/arayuz.png" alt="Ana Arayüz" width="800" />
<p><em>Modern ve kullanıcı dostu arayüz</em></p>
</div>

---

## ✨ Özellikler

*   **Çoklu Model Desteği:** Google Gemini (v1.5 Flash, v2.5 Pro vb.) veya Yerel Ollama modelleri (Llama 3, Mistral vb.) ile çalışabilir.
*   **Geniş Dosya Desteği:** PDF, DOCX, TXT ve CSV formatındaki özgeçmişleri okuyabilir.
*   **Otomatik Puanlama:** Adayları iş tanımına göre 0-100 arasında puanlar.
*   **Detaylı Analiz:** Eksik yetenekleri, güçlü yönleri ve eğitim durumunu raporlar.
*   **Akıllı Sıralama:** En uygun adayları otomatik olarak en üste taşır.
*   **Kolay Kullanım:** Sürükle-bırak gerektirmeyen, klasör bazlı otomatik tarama sistemi.
*   **CV Önizleme:** Uygulama içinden CV'leri görüntüleme imkanı.

<div align="center">
<img src="/images/ollama.png" alt="Ollama Desteği" width="200" />
<p><em>Yerel AI modelleri ile tam gizlilik</em></p>
</div>

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
*   Python 3.10 veya üzeri
*   (Opsiyonel) Ollama (Yerel modeller için)

### Adım 1: Projeyi İndirin
```bash
git clone https://github.com/MustafaKemal0146/ai-cv-analyzer.git
cd ai-cv-analyzer
```

### Adım 2: Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 3: Uygulamayı Başlatın
```bash
python -m streamlit run app.py
```

<div align="center">
<img src="/images/cv-ekleme.png" alt="CV Ekleme" width="200" />
<p><em>Klasör bazlı otomatik CV tarama sistemi</em></p>
</div>

---

## 📖 Kullanım Rehberi

### 1. Google Gemini ile Kullanım
1.  Uygulamayı açın.
2.  Sol menüden **"Google Gemini"** seçeneğini işaretleyin.
3.  [Google AI Studio](https://aistudio.google.com/app/apikey) adresinden aldığınız API anahtarını girin.
4.  CV dosyalarınızı projenin içindeki `cv` klasörüne atın (veya "📂 Klasörü Aç" butonunu kullanın).
5.  **"🔄 Klasörü Kontrol Et"** butonuna basın.
6.  İş tanımını yapıştırın ve **"✨ Adayları Analiz Et"** butonuna tıklayın.

### 2. Ollama (Yerel AI) ile Kullanım
1.  Bilgisayarınızda [Ollama](https://ollama.com/) kurulu olduğundan ve çalıştığından emin olun (`ollama serve`).
2.  Uygulamada sol menüden **"Ollama (Yerel)"** seçeneğini işaretleyin.
3.  Listeden kullanmak istediğiniz modeli seçin (örn: `llama3`).
4.  Analizi başlatın! (API anahtarı gerekmez).

<div align="center">
<img src="/images/cv-analiz.png" alt="CV Analiz Sonuçları" width="800" />
<p><em>Detaylı analiz ve akıllı sıralama</em></p>
</div>

---

## 👤 Geliştirici

<div align="center">

**Mustafa Kemal Çıngıl**

[![GitHub](https://img.shields.io/badge/GitHub-MustafaKemal0146-181717?style=for-the-badge&logo=github)](https://github.com/MustafaKemal0146)

</div>

---

## 📝 Lisans
Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

