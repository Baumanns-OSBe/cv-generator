# ✅ **Perfekt! Hier ist der KOMPLETTE Code nochmal!**

---

## 📄 **DATEI: `streamlit_app.py`**

**Kopiere diesen KOMPLETTEN Code:**

```python
import streamlit as st
import openai
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
import json
from datetime import datetime

# Seiten-Konfiguration
st.set_page_config(
    page_title="📋 Bewerbungsdossier Generator",
    page_icon="📋",
    layout="wide"
)

# OpenAI API Key aus Secrets
openai.api_key = os.environ.get("OPENAI_API_KEY", "")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        width: 100%;
        background-color: #3498db;
        color: white;
        padding: 15px;
        font-size: 18px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Titel
st.title("📋 Bewerbungsdossier Generator")
st.markdown("### Dein persönliches Profil professionell gestaltet")
st.markdown("---")

# Session State initialisieren
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# SCHRITT 1: Benutzertyp
if st.session_state.step == 1:
    st.header("👤 Schritt 1: Wer bist du?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👨‍🎓 Jugendlich\n\n(Schüler/in oder Azubi)", key="youth", use_container_width=True):
            st.session_state.user_data['type'] = 'jugendlich'
            st.session_state.step = 2
            st.rerun()
    
    with col2:
        if st.button("👨‍💼 Erwachsen\n\n(Berufstätig)", key="adult", use_container_width=True):
            st.session_state.user_data['type'] = 'erwachsen'
            st.session_state.step = 2
            st.rerun()

# SCHRITT 2: Interview
elif st.session_state.step == 2:
    st.header("📝 Schritt 2: Erzähle uns von dir")
    
    user_type = st.session_state.user_data.get('type')
    
    with st.form("interview_form"):
        st.subheader("🙋 Persönliche Daten")
        vorname = st.text_input("Vorname *")
        nachname = st.text_input("Nachname *")
        alter = st.number_input("Alter *", min_value=10, max_value=100, value=20)
        
        if user_type == 'jugendlich':
            st.subheader("🏫 Schule")
            schule = st.text_input("Welche Schule besuchst du? *")
            klasse = st.text_input("In welcher Klasse bist du? *")
            
            st.subheader("👨‍👩‍👧‍👦 Familie")
            vater_name = st.text_input("Name deines Vaters")
            vater_beruf = st.text_input("Beruf deines Vaters")
            mutter_name = st.text_input("Name deiner Mutter")
            mutter_beruf = st.text_input("Beruf deiner Mutter")
            geschwister = st.number_input("Anzahl Geschwister", min_value=0, max_value=10, value=0)
        
        else:  # Erwachsen
            st.subheader("💼 Berufliches")
            ausbildung = st.text_input("Deine Ausbildung/Studium *")
            position = st.text_input("Aktuelle Position *")
            branche = st.text_input("Branche *")
            erfahrung = st.number_input("Jahre Berufserfahrung *", min_value=0, max_value=50, value=5)
            erfolge = st.text_area("Deine 3 größten beruflichen Erfolge", height=100)
        
        st.subheader("🌟 Über dich")
        hobbies = st.text_input("Deine Hobbys (kommagetrennt)")
        staerken = st.text_area("Deine Stärken *", max_chars=300, height=100)
        ziele = st.text_area("Deine beruflichen Ziele *", height=100)
        
        submitted = st.form_submit_button("Weiter zur KI-Analyse →", use_container_width=True)
        
        if submitted:
            if not vorname or not nachname or not staerken or not ziele:
                st.error("❌ Bitte fülle alle Pflichtfelder (*) aus!")
            else:
                st.session_state.user_data.update({
                    'vorname': vorname,
                    'nachname': nachname,
                    'alter': alter,
                    'hobbies': hobbies,
                    'staerken': staerken,
                    'ziele': ziele
                })
                
                if user_type == 'jugendlich':
                    st.session_state.user_data.update({
                        'schule': schule,
                        'klasse': klasse,
                        'vater_name': vater_name,
                        'vater_beruf': vater_beruf,
                        'mutter_name': mutter_name,
                        'mutter_beruf': mutter_beruf,
                        'geschwister': geschwister
                    })
                else:
                    st.session_state.user_data.update({
                        'ausbildung': ausbildung,
                        'position': position,
                        'branche': branche,
                        'erfahrung': erfahrung,
                        'erfolge': erfolge
                    })
                
                st.session_state.step = 3
                st.rerun()
    
    # Zurück-Button
    if st.button("← Zurück", key="back_step2"):
        st.session_state.step = 1
        st.rerun()

# SCHRITT 3: KI-Analyse
elif st.session_state.step == 3:
    st.header("🤖 Schritt 3: KI analysiert deine Kompetenzen")
    
    if 'analysis_done' not in st.session_state:
        if not openai.api_key:
            st.error("❌ Kein OpenAI API Key gefunden!")
            st.info("💡 Bitte in den Streamlit Secrets den OPENAI_API_KEY eintragen.")
            st.stop()
        
        with st.spinner("🤖 Analysiere deine Fähigkeiten mit KI... (dauert ~10-30 Sekunden)"):
            try:
                user_data = st.session_state.user_data
                
                prompt = f"""
Analysiere diese Person und identifiziere die TOP 3 Schlüsselkompetenzen:

Name: {user_data['vorname']} {user_data['nachname']}
Alter: {user_data['alter']}
Hobbys: {user_data.get('hobbies', 'N/A')}
Stärken: {user_data['staerken']}
Ziele: {user_data['ziele']}

Antworte NUR als gültiges JSON ohne Markdown:
{{
    "competencies": [
        {{"name": "Kompetenz1", "description": "Warum diese Kompetenz wichtig ist", "strength": 85}},
        {{"name": "Kompetenz2", "description": "Warum diese Kompetenz wichtig ist", "strength": 80}},
        {{"name": "Kompetenz3", "description": "Warum diese Kompetenz wichtig ist", "strength": 75}}
    ],
    "quotes": [
        {{"text": "Inspirierendes deutsches Zitat", "author": "Autor"}},
        {{"text": "Inspirierendes deutsches Zitat", "author": "Autor"}},
        {{"text": "Inspirierendes deutsches Zitat", "author": "Autor"}}
    ]
}}
"""
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Du bist ein erfahrener HR-Experte. Antworte nur mit gültigem JSON ohne Markdown-Formatierung."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                content = response.choices[0].message.content.strip()
                
                # Entferne mögliche Markdown-Code-Blöcke
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1])
                if content.startswith("json"):
                    content = content[4:].strip()
                
                result = json.loads(content)
                
                st.session_state.user_data['competencies'] = result['competencies']
                st.session_state.user_data['quotes'] = result['quotes']
                st.session_state.analysis_done = True
                st.rerun()
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Fehler beim Verarbeiten der KI-Antwort: {str(e)}")
                st.code(content)
                st.stop()
            except Exception as e:
                st.error(f"❌ Fehler bei der Analyse: {str(e)}")
                st.info("💡 Prüfe ob dein OpenAI API Key korrekt ist und ob du Guthaben hast!")
                st.stop()
    
    if st.session_state.get('analysis_done'):
        st.success("✅ Analyse abgeschlossen!")
        
        competencies = st.session_state.user_data.get('competencies', [])
        quotes = st.session_state.user_data.get('quotes', [])
        
        # Kompetenzen anzeigen
        st.subheader("✨ Deine Top 3 Schlüsselkompetenzen:")
        
        for i, comp in enumerate(competencies, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {i}. {comp['name']}")
                    st.write(comp['description'])
                with col2:
                    st.metric("Stärke", f"{comp['strength']}%")
                st.progress(comp['strength'] / 100)
                st.markdown("---")
        
        # Zitate anzeigen
        st.subheader("💡 Passende Zitate für dein Titelblatt:")
        
        selected_quote_idx = st.radio(
            "Wähle dein Lieblingszitat:",
            options=range(len(quotes)),
            format_func=lambda i: f'"{quotes[i]["text"]}" — {quotes[i]["author"]}'
        )
        
        st.session_state.user_data['selected_quote'] = quotes[selected_quote_idx]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back_step3"):
                del st.session_state.analysis_done
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("Weiter zum Design →", key="next_step3", use_container_width=True):
                st.session_state.step = 4
                st.rerun()

# SCHRITT 4: Design wählen
elif st.session_state.step == 4:
    st.header("🎨 Schritt 4: Wähle dein Design")
    
    designs = {
        "Modern Minimalist": {"colors": ["#1a1a1a", "#00d4ff"], "icon": "🔷"},
        "Creative Bold": {"colors": ["#ff6b9d", "#feca57"], "icon": "🌈"},
        "Professional Classic": {"colors": ["#2c3e50", "#3498db"], "icon": "📊"},
        "Nature Green": {"colors": ["#27ae60", "#16a085"], "icon": "🌿"}
    }
    
    cols = st.columns(4)
    
    for idx, (name, data) in enumerate(designs.items()):
        with cols[idx]:
            st.markdown(f"<div style='text-align: center; font-size: 3rem;'>{data['icon']}</div>", unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.markdown(
                f'<div style="background: linear-gradient(135deg, {data["colors"][0]}, {data["colors"][1]}); height: 100px; border-radius: 10px; margin: 10px 0;"></div>',
                unsafe_allow_html=True
            )
            if st.button(f"Wählen", key=f"design_{idx}", use_container_width=True):
                st.session_state.user_data['design'] = name
                st.session_state.user_data['design_colors'] = data['colors']
                st.session_state.step = 5
                st.rerun()
    
    st.markdown("---")
    
    if st.button("← Zurück", key="back_step4"):
        st.session_state.step = 3
        st.rerun()

# SCHRITT 5: PDF erstellen
elif st.session_state.step == 5:
    st.header("📄 Schritt 5: Dein Bewerbungsdossier")
    
    st.success("✅ Alle Informationen gesammelt!")
    
    user_data = st.session_state.user_data
    
    # Vorschau Titelblatt
    st.subheader("👀 Vorschau Titelblatt:")
    colors = user_data.get('design_colors', ['#3498db', '#2ecc71'])
    quote = user_data.get('selected_quote', {})
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {colors[0]}, {colors[1]}); 
                    padding: 60px; border-radius: 15px; color: white; text-align: center; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <h1 style="font-size: 28px; margin
