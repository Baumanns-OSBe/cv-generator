import streamlit as st
import openai
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
import json
from datetime import date

st.set_page_config(page_title="Bewerbungsdossier Generator", page_icon="📋", layout="wide")
openai.api_key = os.environ.get("OPENAI_API_KEY", "")
st.markdown('<style>.stApp{background:linear-gradient(135deg,#667eea,#764ba2);}.stButton>button{width:100%;background:#3498db;color:white;padding:15px;font-size:18px;border-radius:10px;font-weight:bold;}</style>', unsafe_allow_html=True)
st.title("📋 Bewerbungsdossier Generator")
st.markdown("---")

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

if st.session_state.step == 1:
    st.header("Wer bist du?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Jugendlich", use_container_width=True):
            st.session_state.user_data['type'] = 'jugendlich'
            st.session_state.step = 2
            st.rerun()
    with c2:
        if st.button("Erwachsen", use_container_width=True):
            st.session_state.user_data['type'] = 'erwachsen'
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.header("Erzähle von dir")
    ut = st.session_state.user_data.get('type')
    with st.form("form"):
        vn = st.text_input("Vorname")
        nn = st.text_input("Nachname")
        if ut == 'jugendlich':
            gd = st.date_input("Geburtsdatum", value=date(2008, 1, 1))
            st.subheader("Schulen")
            anz_s = st.number_input("Anzahl Schulen", 1, 5, 1)
            schulen = []
            for i in range(anz_s):
                sn = st.text_input("Schule " + str(i+1), key="s" + str(i))
                so = st.text_input("Ort", key="so" + str(i))
                v = st.date_input("Von", key="v" + str(i), value=date(2015, 8, 1))
                bn = st.checkbox("Noch", key="bn" + str(i))
                b = "heute" if bn else st.date_input("Bis", key="b" + str(i))
                ab = st.text_input("Abschluss", key="ab" + str(i))
                schulen.append({'name': sn, 'ort': so, 'von': v, 'bis': b, 'abschluss': ab})
            st.subheader("Familie")
            van = st.text_input("Vater Name")
            vab = st.text_input("Vater Beruf")
            man = st.text_input("Mutter Name")
            mab = st.text_input("Mutter Beruf")
            anz_g = st.number_input("Anzahl Geschwister", 0, 10, 0)
            geschwister = []
            for i in range(anz_g):
                gvn = st.text_input("Geschwister Vorname", key="gv" + str(i))
                gal = st.number_input("Alter", 0, 100, 10, key="ga" + str(i))
                gbe = st.text_input("Beruf/Schule", key="gb" + str(i))
                geschwister.append({'vorname': gvn, 'alter': gal, 'beruf': gbe})
        else:
            al = st.number_input("Alter", 18, 100, 30)
            aus = st.text_input("Ausbildung")
            pos = st.text_input("Position")
            bra = st.text_input("Branche")
            erf = st.number_input("Jahre Erfahrung", 0, 50, 5)
            erg = st.text_area("Erfolge")
        hob = st.text_input("Hobbys")
        sta = st.text_area("Stärken")
        zie = st.text_area("Ziele")
        sub = st.form_submit_button("Weiter", use_container_width=True)
        if sub:
            if ut == 'jugendlich':
                alt = (date.today() - gd).days // 365
                st.session_state.user_data.update({'vorname': vn, 'nachname': nn, 'geburtsdatum': gd.strftime('%d.%m.%Y'), 'alter': alt, 'hobbies': hob, 'staerken': sta, 'ziele': zie, 'schulen': schulen, 'vater_name': van, 'vater_beruf': vab, 'mutter_name': man, 'mutter_beruf': mab, 'geschwister': geschwister})
            else:
                st.session_state.user_data.update({'vorname': vn, 'nachname': nn, 'alter': al, 'hobbies': hob, 'staerken': sta, 'ziele': zie, 'ausbildung': aus, 'position': pos, 'branche': bra, 'erfahrung': erf, 'erfolge': erg})
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.header("KI Analyse")
    if 'done' not in st.session_state:
        if not openai.api_key:
            st.error("Kein API Key")
            st.stop()
        with st.spinner("Analysiere..."):
            try:
                u = st.session_state.user_data
                p = "Analysiere: " + u['vorname'] + " " + u['nachname'] + ", " + str(u['alter']) + " Jahre, Hobbys: " + u.get('hobbies', 'N/A') + ", Stärken: " + u['staerken'] + ", Ziele: " + u['ziele'] + ". Antworte JSON: {\"competencies\":[{\"name\":\"X\",\"description\":\"Y\",\"strength\":85}],\"quotes\":[{\"text\":\"Z\",\"author\":\"A\"}]}"
                r = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": "HR. JSON only."}, {"role": "user", "content": p}], temperature=0.7)
                c = r.choices[0].message.content.strip()
                if c.startswith("```"):
                    c = "\n".join(c.split("\n")[1:-1])
                res = json.loads(c)
                st.session_state.user_data['comp'] = res['competencies']
                st.session_state.user_data['quot'] = res['quotes']
                st.session_state.done = True
                st.rerun()
            except Exception as e:
                st.error(str(e))
                st.stop()
    if st.session_state.get('done'):
        st.success("Fertig!")
        for i, c in enumerate(st.session_state.user_data.get('comp', []), 1):
            st.markdown("**" + str(i) + ". " + c['name'] + "**")
            st.write(c['description'])
            st.progress(c['strength'] / 100)
        q = st.session_state.user_data.get('quot', [])
        sel = st.radio("Zitat:", range(len(q)), format_func=lambda i: q[i]["text"])
        st.session_state.user_data['sq'] = q[sel]
        if st.button("Weiter", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

elif st.session_state.step == 4:
    st.header("Design")
    d = {"Modern": ["#1a1a1a", "#00d4ff"], "Creative": ["#ff6b9d", "#feca57"], "Pro": ["#2c3e50", "#3498db"], "Nature": ["#27ae60", "#16a085"]}
    cols = st.columns(4)
    for i, (n, c) in enumerate(d.items()):
        with cols[i]:
            st.markdown("**" + n + "**")
            st.markdown('<div style="background:linear-gradient(135deg,' + c[0] + ',' + c[1] + ');height:100px;border-radius:10px"></div>', unsafe_allow_html=True)
            if st.button("Wählen", key=str(i), use_container_width=True):
                st.session_state.user_data['col'] = c
                st.session_state.step = 5
                st.rerun()

elif st.session_state.step == 5:
    st.header("Dein Dossier")
    u = st.session_state.user_data
    cl = u.get('col', ['#3498db', '#2ecc71'])
    q = u.get('sq', {})
    st.markdown('<div style="background:linear-gradient(135deg,' + cl[0] + ',' + cl[1] + ');padding:60px;border-radius:15px;color:white;text-align:center"><h1>Bewerbungsdossier</h1><h2>' + u["vorname"] + ' ' + u["nachname"] + '</h2><p>"' + q.get("text", "") + '"</p><p>— ' + q.get("author", "") + '</p></div>', unsafe_allow_html=True)
    if st.button("PDF", type="primary", use_container_width=True):
        with st.spinner("PDF..."):
            try:
                buf = BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4)
                story = []
                s = getSampleStyleSheet()
                story.append(Paragraph("Bewerbungsdossier", s['Title']))
                story.append(Spacer(1, 0.3 * inch))
                story.append(Paragraph(u['vorname'] + " " + u['nachname'], s['Heading1']))
                if u.get('type') == 'jugendlich':
                    story.append(Paragraph("Geburtsdatum: " + u.get('geburtsdatum', ''), s['Normal']))
                story.append(Spacer(1, 0.3 * inch))
                story.append(Paragraph(q.get("text", ""), s['Normal']))
                story.append(Paragraph("- " + q.get("author", ""), s['Normal']))
                story.append(Spacer(1, 0.5 * inch))
                story.append(Paragraph("Kompetenzen", s['Heading2']))
                for i, c in enumerate(u.get('comp', []), 1):
                    story.append(Paragraph(str(i) + ". " + c['name'], s['Heading3']))
                    story.append(Paragraph(c['description'], s['Normal']))
                if u.get('type') == 'jugendlich' and u.get('schulen'):
                    story.append(Spacer(1, 0.3 * inch))
                    story.append(Paragraph("Schulbildung", s['Heading2']))
                    for sch in u['schulen']:
                        vd = sch['von'].strftime('%m/%Y') if isinstance(sch['von'], date) else str(sch['von'])
                        bd = sch['bis'].strftime('%m/%Y') if isinstance(sch['bis'], date) else str(sch['bis'])
                        story.append(Paragraph(vd + " - " + bd + ": " + sch['name'] + ", " + sch.get('ort', ''), s['Normal']))
                if u.get('type') == 'jugendlich' and u.get('geschwister'):
                    story.append(Spacer(1, 0.3 * inch))
                    story.append(Paragraph("Geschwister", s['Heading2']))
                    for g in u['geschwister']:
                        story.append(Paragraph(g['vorname'] + ", " + str(g['alter']) + " Jahre, " + g.get('beruf', ''), s['Normal']))
                doc.build(story)
                buf.seek(0)
                st.download_button("Download PDF", buf, file_name="Bewerbungsdossier_" + u['vorname'] + "_" + u['nachname'] + ".pdf", mime="application/pdf")
                st.success("Fertig!")
                st.balloons()
            except Exception as e:
                st.error(str(e))
    if st.button("Neu"):
        st.session_state.step = 1
        st.session_state.user_data = {}
        if 'done' in st.session_state:
            del st.session_state.done
        st.rerun()

st.markdown("---")
st.markdown('<div style="text-align:center;color:white"><p>Datenschutzfreundlich - DSGVO-konform</p></div>', unsafe_allow_html=True)
