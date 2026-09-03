import streamlit as st
import openai
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import json
from datetime import datetime, date

st.set_page_config(page_title="Bewerbungsdossier Generator", page_icon="📋", layout="wide")

openai.api_key = os.environ.get("OPENAI_API_KEY", "")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.stButton>button {width: 100%; background-color: #3498db; color: white; padding: 15px; font-size: 18px; border-radius: 10px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("📋 Bewerbungsdossier Generator")
st.markdown("### Dein persönliches Profil professionell gestaltet")
st.markdown("---")

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

if st.session_state.step == 1:
    st.header("👤 Wer bist du?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍🎓 Jugendlich", key="youth", use_container_width=True):
            st.session_state.user_data['type'] = 'jugendlich'
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("👨‍💼 Erwachsen", key="adult", use_container_width=True):
            st.session_state.user_data['type'] = 'erwachsen'
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.header("📝 Erzähle uns von dir")
    user_type = st.session_state.user_data.get('type')
    
    with st.form("interview_form"):
        st.subheader("🙋 Persönliche Daten")
        vorname = st.text_input("Vorname *")
        nachname = st.text_input("Nachname *")
        
        if user_type == 'jugendlich':
            geburtsdatum = st.date_input("Geburtsdatum *", min_value=date(2000, 1, 1), max_value=date.today(), value=date(2008, 1, 1))
        else:
            alter = st.number_input("Alter *", min_value=18, max_value=100, value=30)
        
        if user_type == 'jugendlich':
            st.subheader("🏫 Schulbildung")
            st.markdown("**Welche Schulen besuchst oder besuchtest du?**")
            
            anzahl_schulen = st.number_input("Wie viele Schulen möchtest du angeben?", min_value=1, max_value=5, value=1)
            
            schulen_temp = []
            for i in range(anzahl_schulen):
                st.markdown(f"**Schule {i+1}:**")
                col1, col2 = st.columns(2)
                with col1:
                    schule_name = st.text_input(f"Name der Schule {i+1} *", key=f"schule_name_{i}")
                    von = st.date_input(f"Von (Schule {i+1}) *", key=f"von_{i}", value=date(2015, 8, 1))
                with col2:
                    schule_ort = st.text_input(f"Ort (Schule {i+1})", key=f"schule_ort_{i}")
                    bis_noch = st.checkbox(f"Besuche ich noch", key=f"noch_{i}")
                    if not bis_noch:
                        bis = st.date_input(f"Bis (Schule {i+1}) *", key=f"bis_{i}", value=date.today())
                    else:
                        bis = "heute"
                
                abschluss = st.text_input(f"Abschluss/Klasse (Schule {i+1})", key=f"abschluss_{i}")
                
                schulen_temp.append({
                    'name': schule_name,
                    'ort': schule_ort,
                    'von': von,
                    'bis': bis,
                    'abschluss': abschluss
                })
            
            st.markdown("---")
            st.subheader("👨‍👩‍👧‍👦 Familie")
            
            col1, col2 = st.columns(2)
            with col1:
                vater_name = st.text_input("Name deines Vaters")
                vater_beruf = st.text_input("Beruf deines Vaters")
            with col2:
                mutter_name = st.text_input("Name deiner Mutter")
                mutter_beruf = st.text_input("Beruf deiner Mutter")
            
            st.markdown("**Geschwister:**")
            anzahl_geschwister = st.number_input("Wie viele Geschwister hast du?", min_value=0, max_value=10, value=0)
            
            geschwister_temp = []
            for i in range(anzahl_geschwister):
                st.markdown(f"**Geschwister {i+1}:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    g_vorname = st.text_input(f"Vorname *", key=f"g_vorname_{i}")
                with col2:
                    g_alter = st.number_input(f"Alter *", min_value=0, max_value=100, value=10, key=f"g_alter_{i}")
                with col3:
                    g_beruf = st.text_input(f"Beruf/Schule (optional)", key=f"g_beruf_{i}")
                
                geschwister_temp.append({
                    'vorname': g_vorname,
                    'alter': g_alter,
                    'beruf': g_beruf
                })
        
        else:
            st.subheader("💼 Berufliches")
            ausbildung = st.text_input("Deine Ausbildung/Studium *")
            position = st.text_input("Aktuelle Position *")
            branche = st.text_input("Branche *")
            erfahrung = st.number_input("Jahre Berufserfahrung *", min_value=0, max_value=50, value=5)
            erfolge = st.text_area("Deine größten Erfolge", height=100)
        
        st.subheader("🌟 Über dich")
        hobbies = st.text_input("Deine Hobbys")
        staerken = st.text_area("Deine Stärken *", height=100)
        ziele = st.text_area("Deine Ziele *", height=100)
        
        submitted = st.form_submit_button("Weiter →", use_container_width=True)
        
        if submitted:
            if not vorname or not nachname or not staerken or not ziele:
                st.error("Bitte fülle alle Pflichtfelder (*) aus!")
            else:
                if user_type == 'jugendlich':
                    alter_berechnet = (date.today() - geburtsdatum).days // 365
                    st.session_state.user_data.update({
                        'vorname': vorname,
                        'nachname': nachname,
                        'geburtsdatum': geburtsdatum.strftime('%d.%m.%Y'),
                        'alter': alter_berechnet,
                        'hobbies': hobbies,
                        'staerken': staerken,
                        'ziele': ziele,
                        'schulen': schulen_temp,
                        'vater_name': vater_name,
                        'vater_beruf': vater_beruf,
                        'mutter_name': mutter_name,
                        'mutter_beruf': mutter_beruf,
                        'geschwister': geschwister_temp
                    })
                else:
                    st.session_state.user_data.update({
                        'vorname': vorname,
                        'nachname': nachname,
                        'alter': alter,
                        'hobbies': hobbies,
                        'staerken': staerken,
                        'ziele': ziele,
                        'ausbildung': ausbildung,
                        'position': position,
                        'branche': branche,
                        'erfahrung': erfahrung,
                        'erfolge': erfolge
                    })
                
                st.session_state.step = 3
                st.rerun()

elif st.session_state.step == 3:
    st.header("🤖 KI analysiert deine Kompetenzen")
    if 'analysis_done' not in st.session_state:
        if not openai.api_key:
            st.error("Kein OpenAI API Key gefunden!")
            st.stop()
        with st.spinner("Analysiere... (10-30 Sekunden)"):
            try:
                user_data = st.session_state.user_data
                prompt = f"""Analysiere diese Person und finde TOP 3 Kompetenzen:
Name: {user_data['vorname']} {user_data['nachname']}
Alter: {user_data['alter']}
Hobbys: {user_data.get('hobbies', 'N/A')}
Stärken: {user_data['staerken']}
Ziele: {user_data['ziele']}

Antworte als JSON:
{{"competencies": [{{"name": "...", "description": "...", "strength": 85}}], "quotes": [{{"text": "...", "author": "..."}}]}}"""
                response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": "Du bist HR-Experte. Antworte nur JSON."}, {"role": "user", "content": prompt}], temperature=0.7)
                content = response.choices[0].message.content.strip()
                if content.startswith("```"):
                    content = "\n".join(content.split("\n")[1:-1])
                result = json.loads(content)
                st.session_state.user_data['competencies'] = result['competencies']
                st.session_state.user_data['quotes'] = result['quotes']
                st.session_state.analysis_done = True
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {str(e)}")
                st.stop()
    if st.session_state.get('analysis_done'):
        st.success("Analyse abgeschlossen!")
        competencies = st.session_state.user_data.get('competencies', [])
        quotes = st.session_state.user_data.get('quotes', [])
        st.subheader("Deine Top 3 Kompetenzen:")
        for i, comp in enumerate(competencies, 1):
            st.markdown(f"**{i}. {comp['name']}**")
            st.write(comp['description'])
            st.progress(comp['strength'] / 100)
            st.markdown("---")
        st.subheader("Passende Zitate:")
        selected = st.radio("Wähle dein Zitat:", options=range(len(quotes)), format_func=lambda i: f'"{quotes[i]["text"]}" - {quotes[i]["author"]}')
        st.session_state.user_data['selected_quote'] = quotes[selected]
        if st.button("Weiter →", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

elif st.session_state.step == 4:
    st.header("🎨 Wähle dein Design")
    designs = {"Modern": {"colors": ["#1a1a1a", "#00d4ff"], "icon": "🔷"}, "Creative": {"colors": ["#ff6b9d", "#feca57"], "icon": "🌈"}, "Professional": {"colors": ["#2c3e50", "#3498db"], "icon": "📊"}, "Nature": {"colors": ["#27ae60", "#16a085"], "icon": "🌿"}}
    cols = st.columns(4)
    for idx, (name, data) in enumerate(designs.items()):
        with cols[idx]:
            st.markdown(f"<div style='text-align:center;font-size:3rem'>{data['icon']}</div>", unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.markdown(f'<div style="background:linear-gradient(135deg,{data["colors"][0]},{data["colors"][1]});height:100px;border-radius:10px"></div>', unsafe_allow_html=True)
            if st.button("Wählen", key=f"d{idx}", use_container_width=True):
                st.session_state.user_data['design'] = name
                st.session_state.user_data['colors'] = data['colors']
                st.session_state.step = 5
                st.rerun()

elif st.session_state.step == 5:
    st.header("📄 Dein Bewerbungsdossier")
    user_data = st.session_state.user_data
    colors = user_data.get('colors', ['#3498db', '#2ecc71'])
    quote = user_data.get('selected_quote', {})
    st.markdown(f'<div style="background:linear-gradient(135deg,{colors[0]},{colors[1]});padding:60px;border-radius:15px;color:white;text-align:center"><h1>Bewerbungsdossier</h1><h2>{user_data["vorname"]} {user_data["nachname"]}</h2><p style="font-style:italic">"{quote.get("text", "")}"</p><p>— {quote.get("author", "")}</p></div>', unsafe_allow_html=True)
    
    if st.button("PDF erstellen", type="primary", use_container_width=True):
        with st.spinner("Erstelle PDF..."):
            try:
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
                story = []
                styles = getSampleStyleSheet()
                
                story.append(Paragraph("Bewerbungsdossier", styles['Title']))
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph(f"{user_data['vorname']} {user_data['nachname']}", styles['Heading1']))
                story.append(Spacer(1, 0.5*inch))
                story.append(Paragraph(f'"{quote.get("text", "")}"
