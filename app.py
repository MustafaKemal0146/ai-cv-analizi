import streamlit as st
import os
import pandas as pd
import json
import base64
from pypdf import PdfReader
from docx import Document
import time
import subprocess
import platform

# SDK ve Fallback için Import Ayarları
import requests  # Ollama ve Fallback için gerekli
try:
    import google.generativeai as genai
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

# --- Sayfa Yapılandırması ---
st.set_page_config(
    page_title="AI CV Analiz Uzmanı (v2.5)",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Stiller ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        color: #155724;
        margin-bottom: 1rem;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #fff3cd;
        color: #856404;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Yardımcı Fonksiyonlar ---

def cv_klasoru_olustur():
    """Çalışma dizininde 'cv' klasörü oluşturur."""
    klasor_yolu = os.path.join(os.getcwd(), 'cv')
    if not os.path.exists(klasor_yolu):
        os.makedirs(klasor_yolu)
    return klasor_yolu

def cv_klasoru_ac(klasor_yolu):
    """İşletim sistemine göre klasörü açar."""
    if platform.system() == "Windows":
        os.startfile(klasor_yolu)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", klasor_yolu])
    else:  # Linux
        subprocess.Popen(["xdg-open", klasor_yolu])

def pdf_metin_cikar(dosya_yolu):
    """PDF dosyasından metin çıkarır."""
    try:
        reader = PdfReader(dosya_yolu)
        metin = ""
        for sayfa in reader.pages:
            metin += sayfa.extract_text() + "\n"
        return metin
    except Exception as e:
        st.error(f"PDF Okuma Hatası ({os.path.basename(dosya_yolu)}): {e}")
        return None

def docx_metin_cikar(dosya_yolu):
    """DOCX dosyasından metin çıkarır."""
    try:
        doc = Document(dosya_yolu)
        metin = ""
        for para in doc.paragraphs:
            metin += para.text + "\n"
        return metin
    except Exception as e:
        st.error(f"DOCX Okuma Hatası ({os.path.basename(dosya_yolu)}): {e}")
        return None

def txt_metin_cikar(dosya_yolu):
    """TXT dosyasından metin çıkarır."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        st.error(f"TXT Okuma Hatası ({os.path.basename(dosya_yolu)}): {e}")
        return None

def csv_metin_cikar(dosya_yolu):
    """CSV dosyasından metin çıkarır."""
    try:
        df = pd.read_csv(dosya_yolu)
        return df.to_string()
    except Exception as e:
        st.error(f"CSV Okuma Hatası ({os.path.basename(dosya_yolu)}): {e}")
        return None

def ollama_modellerini_getir():
    """Yerel Ollama sunucusundan mevcut modelleri getirir."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            modeller = [model['name'] for model in response.json().get('models', [])]
            return modeller
        return []
    except Exception:
        return []

def ollama_ile_analiz_et(cv_metni, is_tanimi, model_adi):
    """CV metnini ve İş Tanımını Yerel Ollama modeline gönderir."""
    prompt_metni = f"""
    Sen uzman bir İnsan Kaynakları ve Teknik İşe Alım Uzmanısın. Aşağıdaki Aday CV'sini verilen İş Tanımı ile detaylıca karşılaştır.
    
    İŞ TANIMI:
    {is_tanimi}
    
    ADAY CV:
    {cv_metni}
    
    Lütfen çıktıyı SADECE aşağıdaki anahtarlara sahip geçerli bir JSON formatında ver:
    - 'aday_ismi': (String, CV başlığından veya dosya isminden çıkar)
    - 'uyum_puani': (Integer, 0-100 arası bir puan)
    - 'bulunan_yetenekler': (String listesi, adayda bulunan ve iş tanımıyla eşleşen yetenekler)
    - 'eksik_yetenekler': (String listesi, iş tanımında olup adayda bulunmayan kritik yetenekler)
    - 'deneyim_ozeti': (String, adayın deneyiminin işe uygunluğunu anlatan kısa paragraf)
    - 'egitim_durumu': (String, adayın eğitim seviyesi ve okulu)
    - 'karar_onerisi': (String, "Görüşmeye Çağır", "Yedekte Tut" veya "Reddet")
    
    Çıktı saf JSON olmalı, markdown formatı (```json) içermemeli.
    """
    
    try:
        payload = {
            "model": model_adi,
            "messages": [{"role": "user", "content": prompt_metni}],
            "stream": False,
            "format": "json"
        }
        response = requests.post("http://localhost:11434/api/chat", json=payload)
        response.raise_for_status()
        
        sonuc = response.json()
        yanit_metni = sonuc['message']['content']
        
        return json.loads(yanit_metni)
    except Exception as e:
        st.error(f"Ollama Analiz Hatası: {e}")
        return {
            "aday_ismi": "Hata Oluştu",
            "uyum_puani": 0,
            "bulunan_yetenekler": [],
            "eksik_yetenekler": [],
            "deneyim_ozeti": f"Analiz başarısız. Hata: {str(e)}",
            "karar_onerisi": "Hata"
        }

def dosya_icerigi_base64(yol):
    """Dosyayı okur ve gömme işlemi için base64'e çevirir."""
    with open(yol, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def gemini_ile_analiz_et(cv_metni, is_tanimi, api_anahtari):
    """CV metnini ve İş Tanımını Gemini'ye gönderir (SDK veya REST API ile)."""
    if not api_anahtari:
        return {"uyum_puani": 0, "aday_ismi": "Bilinmiyor", "ozet": "API Anahtarı eksik", "bulunan_yetenekler": [], "eksik_yetenekler": []}
    
    prompt_metni = f"""
    Sen uzman bir İnsan Kaynakları ve Teknik İşe Alım Uzmanısın. Aşağıdaki Aday CV'sini verilen İş Tanımı ile detaylıca karşılaştır.
    
    İŞ TANIMI:
    {is_tanimi}
    
    ADAY CV:
    {cv_metni}
    
    Lütfen çıktıyı SADECE aşağıdaki anahtarlara sahip geçerli bir JSON formatında ver:
    - 'aday_ismi': (String, CV başlığından veya dosya isminden çıkar)
    - 'uyum_puani': (Integer, 0-100 arası bir puan)
    - 'bulunan_yetenekler': (String listesi, adayda bulunan ve iş tanımıyla eşleşen yetenekler)
    - 'eksik_yetenekler': (String listesi, iş tanımında olup adayda bulunmayan kritik yetenekler)
    - 'deneyim_ozeti': (String, adayın deneyiminin işe uygunluğunu anlatan kısa paragraf)
    - 'egitim_durumu': (String, adayın eğitim seviyesi ve okulu)
    - 'karar_onerisi': (String, "Görüşmeye Çağır", "Yedekte Tut" veya "Reddet")
    
    Çıktı saf JSON olmalı, markdown formatı (```json) içermemeli.
    """

    try:
        if HAS_SDK:
            # --- YÖNTEM 1: Resmi SDK Kullanımı ---
            genai.configure(api_key=api_anahtari)
            model = genai.GenerativeModel('gemini-2.5-pro')
            response = model.generate_content(prompt_metni)
            yanit_metni = response.text.strip()
        else:
            # --- YÖNTEM 2: REST API (Fallback) ---
            # SDK yüklenemezse (örn. Python 3.13 sorunu) burası çalışır.
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_anahtari}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": prompt_metni}]
                }]
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            sonuc = response.json()
            try:
                yanit_metni = sonuc['candidates'][0]['content']['parts'][0]['text'].strip()
            except (KeyError, IndexError):
                raise ValueError("Gemini API'den beklenmeyen yanıt yapısı.")

        # Markdown temizliği (Her iki yöntem için ortak)
        if yanit_metni.startswith("```json"):
            yanit_metni = yanit_metni[7:]
        if yanit_metni.startswith("```"):
            yanit_metni = yanit_metni[3:]
        if yanit_metni.endswith("```"):
            yanit_metni = yanit_metni[:-3]
            
        return json.loads(yanit_metni)
        
    except Exception as e:
        st.error(f"Gemini Analiz Hatası ({'SDK' if HAS_SDK else 'REST API'}): {e}")
        return {
            "aday_ismi": "Hata Oluştu",
            "uyum_puani": 0,
            "bulunan_yetenekler": [],
            "eksik_yetenekler": [],
            "deneyim_ozeti": f"Analiz başarısız. Hata: {str(e)}",
            "karar_onerisi": "Hata"
        }

# --- Oturum Durumu (Session State) ---
if 'dosya_listesi' not in st.session_state:
    st.session_state.dosya_listesi = []
if 'analiz_sonuclari' not in st.session_state:
    st.session_state.analiz_sonuclari = []

# --- Kenar Çubuğu (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("⚙️ Ayarlar")
    
    saglayici = st.radio("Yapay Zeka Sağlayıcısı", ["Google Gemini", "Ollama (Yerel)"])
    
    api_anahtari = None
    secilen_model = None
    
    if saglayici == "Google Gemini":
        api_anahtari = st.text_input("Google Gemini API Anahtarı", type="password", help="Gemini API anahtarınızı buraya girin.")
    else:
        st.info("Yerel Ollama sunucusu kontrol ediliyor...")
        modeller = ollama_modellerini_getir()
        if modeller:
            secilen_model = st.selectbox("Kullanılacak Model", modeller)
            st.success("✅ Ollama Bağlandı")
        else:
            st.error("⚠️ Ollama bulunamadı! 'ollama serve' komutunun çalıştığından emin olun.")
    
    st.markdown("---")
    st.subheader("📂 CV Yönetimi")
    
    # Otomatik Klasör Kontrolü
    cv_klasoru = cv_klasoru_olustur()
    st.info(f"Sistem şu klasörü kullanıyor:\n`{cv_klasoru}`")
    
    if st.button("📂 Klasörü Aç"):
        cv_klasoru_ac(cv_klasoru)
    
    if st.button("🔄 Klasörü Kontrol Et"):
        dosyalar = [f for f in os.listdir(cv_klasoru) if f.lower().endswith(('.pdf', '.docx', '.txt', '.csv'))]
        st.session_state.dosya_listesi = [os.path.join(cv_klasoru, f) for f in dosyalar]
        
        pdf_sayisi = sum(1 for f in dosyalar if f.lower().endswith('.pdf'))
        docx_sayisi = sum(1 for f in dosyalar if f.lower().endswith('.docx'))
        txt_sayisi = sum(1 for f in dosyalar if f.lower().endswith('.txt'))
        csv_sayisi = sum(1 for f in dosyalar if f.lower().endswith('.csv'))
        
        if len(dosyalar) > 0:
            st.success(f"✅ {len(dosyalar)} dosya bulundu ({pdf_sayisi} PDF, {docx_sayisi} DOCX, {txt_sayisi} TXT, {csv_sayisi} CSV).")
        else:
            st.warning("⚠️ Klasör boş veya uygun dosya yok. Lütfen CV'leri 'cv' klasörüne ekleyin.")

    st.markdown("---")
    st.markdown("### ℹ️ Nasıl Kullanılır?")
    st.markdown("""
    1. **Sağlayıcıyı** seçin (Gemini veya Ollama).
    2. **API Anahtarını** girin (Gemini ise).
    3. **CV'leri** projenin içindeki `cv` klasörüne atın.
    4. **Klasörü Kontrol Et** butonuna basın.
    5. **İş Tanımını** yapıştırın.
    6. **Analiz Et** butonuna tıklayın.
    """)

# --- Ana Arayüz ---
st.title("🚀 AI Destekli CV Analiz Uzmanı")
st.markdown("**İşe alım süreçlerinizi yapay zeka ile hızlandırın.**")

with st.expander("ℹ️ Nasıl Kullanılır? (Başlangıç Rehberi)", expanded=False):
    st.markdown("""
    ### 🚀 Hızlı Başlangıç
    1.  **Sağlayıcı Seçimi:** Sol menüden **Google Gemini** (Cloud) veya **Ollama** (Yerel) seçin.
    2.  **CV Yükleme:** Proje klasöründeki `cv` klasörüne adayların özgeçmişlerini (PDF, DOCX, TXT, CSV) atın.
        *   *İpucu: Sol menüdeki "📂 Klasörü Aç" butonunu kullanabilirsiniz.*
    3.  **Dosyaları Tara:** "🔄 Klasörü Kontrol Et" butonuna basarak dosyaları sisteme tanıtın.
    4.  **İş Tanımı:** Aradığınız pozisyonun detaylarını aşağıdaki kutuya yapıştırın.
    5.  **Analiz:** "✨ Adayları Analiz Et" butonuna basın ve yapay zekanın sihrini izleyin!
    
    ---
    **Geliştirici:** [Mustafa Kemal Çıngıl](https://github.com/MustafaKemal0146)
    """)

col1, col2 = st.columns([2, 1])

with col1:
    is_tanimi = st.text_area("📋 İş Tanımı (Job Description)", height=250, placeholder="Aradığınız pozisyonun detaylarını buraya yapıştırın...")

with col2:
    st.markdown("### 🏁 Analiz Başlat")
    analiz_butonu = st.button("✨ Adayları Analiz Et")
    
    if st.session_state.dosya_listesi:
        st.metric("Yüklü CV Sayısı", len(st.session_state.dosya_listesi))
    else:
        st.warning("Henüz CV yüklenmedi.")

# --- Analiz Mantığı ---
if analiz_butonu:
    if saglayici == "Google Gemini" and not api_anahtari:
        st.error("Lütfen geçerli bir Google Gemini API Anahtarı girin.")
    elif saglayici == "Ollama (Yerel)" and not secilen_model:
        st.error("Lütfen geçerli bir Ollama modeli seçin.")
    elif not is_tanimi:
        st.error("Lütfen bir İş Tanımı girin.")
    elif not st.session_state.dosya_listesi:
        st.error("Lütfen önce 'cv' klasörüne dosya ekleyin ve taratın.")
    else:
        sonuclar = []
        ilerleme_cubugu = st.progress(0)
        durum_metni = st.empty()
        
        toplam_dosya = len(st.session_state.dosya_listesi)
        
        for i, dosya_yolu in enumerate(st.session_state.dosya_listesi):
            dosya_adi = os.path.basename(dosya_yolu)
            durum_metni.text(f"Analiz ediliyor ({saglayici}): {dosya_adi}...")
            
            # Metin Çıkarma
            if dosya_yolu.lower().endswith('.pdf'):
                cv_metni = pdf_metin_cikar(dosya_yolu)
            elif dosya_yolu.lower().endswith('.docx'):
                cv_metni = docx_metin_cikar(dosya_yolu)
            elif dosya_yolu.lower().endswith('.txt'):
                cv_metni = txt_metin_cikar(dosya_yolu)
            elif dosya_yolu.lower().endswith('.csv'):
                cv_metni = csv_metin_cikar(dosya_yolu)
            else:
                cv_metni = None
                
            if cv_metni:
                # Analiz (Seçilen Sağlayıcıya Göre)
                if saglayici == "Google Gemini":
                    analiz = gemini_ile_analiz_et(cv_metni, is_tanimi, api_anahtari)
                else:
                    analiz = ollama_ile_analiz_et(cv_metni, is_tanimi, secilen_model)
                    
                analiz['dosya_yolu'] = dosya_yolu
                analiz['dosya_adi'] = dosya_adi
                sonuclar.append(analiz)
            
            # İlerlemeyi Güncelle
            ilerleme_cubugu.progress((i + 1) / toplam_dosya)
            
        st.session_state.analiz_sonuclari = sonuclar
        durum_metni.text("✅ Analiz Tamamlandı!")
        time.sleep(1)
        durum_metni.empty()
        ilerleme_cubugu.empty()

# --- Sonuç Ekranı ---
if st.session_state.analiz_sonuclari:
    st.divider()
    st.subheader("🏆 Aday Sıralaması")
    
    # DataFrame'e Çevir ve Sırala
    df = pd.DataFrame(st.session_state.analiz_sonuclari)
    
    # Eksik kolonları tamamla
    gerekli_kolonlar = ['aday_ismi', 'uyum_puani', 'deneyim_ozeti', 'bulunan_yetenekler', 'eksik_yetenekler', 'egitim_durumu', 'karar_onerisi']
    for kol in gerekli_kolonlar:
        if kol not in df.columns:
            df[kol] = None
            
    df = df.sort_values(by='uyum_puani', ascending=False)
    
    # Ana Liste ve Detay Görünümü
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.dataframe(
            df[['aday_ismi', 'uyum_puani', 'karar_onerisi']],
            column_config={
                "uyum_puani": st.column_config.ProgressColumn(
                    "Puan",
                    help="Uyum Puanı (0-100)",
                    format="%d",
                    min_value=0,
                    max_value=100,
                ),
                "aday_ismi": "Aday İsmi",
                "karar_onerisi": "Öneri"
            },
            use_container_width=True,
            hide_index=True
        )
    
    with c2:
        st.markdown("### 🔍 Detaylı İnceleme")
        for index, row in df.iterrows():
            with st.expander(f"**{row['aday_ismi']}** - Puan: {row['uyum_puani']} ({row['karar_onerisi']})"):
                
                tab1, tab2, tab3 = st.tabs(["📝 Özet & Eğitim", "✅ Yetenek Analizi", "📄 CV Önizleme"])
                
                with tab1:
                    st.markdown(f"**Deneyim Özeti:**\n{row['deneyim_ozeti']}")
                    st.markdown(f"**Eğitim Durumu:**\n{row['egitim_durumu']}")
                    
                    if row['karar_onerisi'] == "Görüşmeye Çağır":
                        st.success(f"**Karar:** {row['karar_onerisi']}")
                    elif row['karar_onerisi'] == "Reddet":
                        st.error(f"**Karar:** {row['karar_onerisi']}")
                    else:
                        st.warning(f"**Karar:** {row['karar_onerisi']}")

                with tab2:
                    k1, k2 = st.columns(2)
                    with k1:
                        st.markdown("**✅ Eşleşen Yetenekler**")
                        for yetenek in row['bulunan_yetenekler'] if isinstance(row['bulunan_yetenekler'], list) else []:
                            st.markdown(f"- {yetenek}")
                    with k2:
                        st.markdown("**❌ Eksik Yetenekler**")
                        for yetenek in row['eksik_yetenekler'] if isinstance(row['eksik_yetenekler'], list) else []:
                            st.markdown(f"- {yetenek}")
                
                with tab3:
                    if st.button(f"CV'yi Görüntüle: {row['dosya_adi']}", key=f"btn_{index}"):
                        dosya_yolu = row['dosya_yolu']
                        if dosya_yolu.lower().endswith('.pdf'):
                            try:
                                b64_pdf = dosya_icerigi_base64(dosya_yolu)
                                pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"PDF görüntülenemedi: {e}")
                        elif dosya_yolu.lower().endswith('.txt'):
                            try:
                                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                                    st.code(f.read())
                            except Exception as e:
                                st.error(f"TXT görüntülenemedi: {e}")
                        elif dosya_yolu.lower().endswith('.csv'):
                            try:
                                df_preview = pd.read_csv(dosya_yolu)
                                st.dataframe(df_preview)
                            except Exception as e:
                                st.error(f"CSV görüntülenemedi: {e}")
                        else:
                            st.info("Önizleme şu an sadece PDF, TXT ve CSV dosyaları için desteklenmektedir. DOCX dosyasını yerel olarak açınız.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        Geliştirici: <a href="https://github.com/MustafaKemal0146" target="_blank" style="text-decoration: none; color: #0366d6;">Mustafa Kemal Çıngıl</a> | 
        🤖 Powered by Gemini & Ollama
    </div>
    """,
    unsafe_allow_html=True
)
