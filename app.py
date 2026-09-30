import streamlit as st
import re
from transformers import pipeline

st.set_page_config(page_title="KVKK Anonimleştirici", page_icon="⚖️")
st.title("⚖️ KVKK & GDPR Uyumlu Metin Anonimleştirici")
st.write("Dilekçe veya sözleşmelerinizi büyük dil modellerine göndermeden önce kişisel verilerden (İsim, Kurum, TC, IBAN vb.) arındırın. Veriler hiçbir sunucuya kaydedilmez.")

# Yapay zeka modelini önbelleğe (cache) alarak sitenin hızlı çalışmasını sağlıyoruz
@st.cache_resource
def load_model():
    return pipeline("ner", model="savasy/bert-base-turkish-ner-cased", aggregation_strategy="simple")

ner_modeli = load_model()

metin = st.text_area("Metninizi buraya yapıştırın:", height=200)

if st.button("Metni Temizle"):
    if metin:
        with st.spinner("Yapay zeka analiz ediyor..."):
            # Regex Temizliği
            metin = re.sub(r'\b[1-9][0-9]{10}\b', '[TCKN GİZLENDİ]', metin)
            metin = re.sub(r'TR[0-9]{24}', '[IBAN GİZLENDİ]', metin)
            metin = re.sub(r'\b0?5[0-9]{2}[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}\b', '[TELEFON GİZLENDİ]', metin)
            metin = re.sub(r'\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b', '[TARİH GİZLENDİ]', metin)
            
            # Yapay Zeka (NLP) Temizliği
            tespitler = ner_modeli(metin)
            for tespit in tespitler:
                aranan = tespit['word']
                etiket = tespit['entity_group']
                if etiket == 'PER': gizli = '[KİŞİ GİZLENDİ]'
                elif etiket == 'ORG': gizli = '[KURUM GİZLENDİ]'
                elif etiket == 'LOC': gizli = '[LOKASYON GİZLENDİ]'
                else: gizli = '[VERİ GİZLENDİ]'
                metin = metin.replace(aranan, gizli)
            
            st.success("İşlem Başarılı! Aşağıdaki metni güvenle kopyalayabilirsiniz.")
            st.info(metin)
    else:
        st.warning("Lütfen temizlenecek bir metin girin.")
