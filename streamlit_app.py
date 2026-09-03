import streamlit as st
import openai
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as rl_colors
from io import BytesIO
import json
from datetime import datetime, date

st.set_page_config(page_title="Bewerbungsdossier Generator", page_icon="📋", layout="wide")
openai.api_key = os.environ.get("OPENAI_API_KEY", "")
st.markdown('<style>.stApp{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);}.stButton>button{width:100%;background-color:#3498db;color:white;padding:15px;font-size:18px;border-radius:10px;font-weight:bold;}</style>', unsafe_allow_html=True)
st.title("📋 Bewerbungsdossier Generator")
st.markdown("### Dein persönliches Profil professionell gestaltet")
st.markdown("---")
if 'step' not in st.session_state:
    st.session_state.step=1
if 'user_data' not in st.session_state:
    st.session_state.user_data={}
if st.session_state.step==1:
    st.header("👤 Wer bist du?")
    col1,col2=st.columns(2)
    with col1:
        if st.button("👨‍🎓 Jugendlich",key="youth",use_container_width=True):
            st.session_state.user_data['type']='jugendlich'
            st.session_state.step=2
            st.rerun()
    with col2:
        if st.button("👨‍💼 Erwachsen",key="adult",use_container_width=True):
            st.session_state.user_data['type']='erwachsen'
            st.session_state.step=2
            st.rerun()
elif st.session_state.step==2:
    st.header("📝 Erzähle uns von dir")
    user_type=st.session_state.user_data.get('type')
    with st.form("interview_form"):
        st.subheader("🙋 Persönliche Daten")
        vorname=st.text_input("Vorname *")
        nachname=st.text_input("Nachname *")
        if user_type=='jugendlich':
            geburtsdatum=st.date_input("Geburtsdatum *",min_value=date(2000,1,1),max_value=date.today(),value=date(2008,1,1))
        else:
            alter=st.number_input("Alter *",min_value=18,max_value=100,value=30)
        if user_type=='jugendlich':
            st.subheader("🏫 Schulbildung")
            st.markdown("**Welche Schulen besuchst oder besuchtest du?**")
            anzahl_schulen=st.number_input("Wie viele Schulen?",min_value=1,max_value=5,value=1)
            schulen_temp=[]
            for i in range(anzahl_schulen):
                st.markdown("**Schule "+str(i+1)+":**")
                col1,col2=st.columns(2)
                with col1:
                    sn=st.text_input("Name der Schule "+str(i+1)+" *",key="sn"+str(i))
                    von=st.date_input("Von *",key="von"+str(i),value=date(2015,8,1))
                with col2:
                    so=st.text_input("Ort",key="so"+str(i))
                    bn=st.checkbox("Besuche ich noch",key="bn"+str(i))
                    bis="heute" if bn else st.date_input("Bis *",key="bis"+str(i),value=date.today())
                ab=st.text_input("Abschluss/Klasse",key="ab"+str(i))
                schulen_temp.append({'name':sn,'ort':so,'von':von,'bis':bis,'abschluss':ab})
            st.markdown("---")
            st.subheader("👨‍👩‍👧‍👦 Familie")
            col1,col2=st.columns(2)
            with col1:
                vn=st.text_input("Name deines Vaters")
                vb=st.text_input("Beruf deines Vaters")
            with col2:
                mn=st.text_input("Name deiner Mutter")
                mb=st.text_input("Beruf deiner Mutter")
            st.markdown("**Geschwister:**")
            ag=st.number_input("Wie viele Geschwister?",min_value=0,max_value=10,value=0)
            geschwister_temp=[]
            for i in range(ag):
                st.markdown("**Geschwister "+str(i+1)+":**")
                c1,c2,c3=st.columns(3)
                with c1:
                    gv=st.text_input("Vorname *",key="gv"+str(i))
                with c2:
                    ga=st.number_input("Alter *",min_value=0,max_value=100,value=10,key="ga"+str(i))
                with c3:
                    gb=st.text_input("Beruf/Schule",key="gb"+str(i))
                geschwister_temp.append({'vorname':gv,'alter':ga,'beruf':gb})
        else:
            st.subheader("💼 Berufliches")
            ausbildung=st.text_input("Ausbildung/Studium *")
            position=st.text_input("Aktuelle Position *")
            branche=st.text_input("Branche *")
            erfahrung=st.number_input("Jahre Berufserfahrung *",min_value=0,max_value=50,value=5)
            erfolge=st.text_area("Größte Erfolge",height=100)
        st.subheader("🌟 Über dich")
        hobbies=st.text_input("Hobbys")
        staerken=st.text_area("Stärken *",height=100)
        ziele=st.text_area("Ziele *",height=100)
        submitted=st.form_submit_button("Weiter →",use_container_width=True)
        if submitted:
            if not vorname or not nachname or not staerken or not ziele:
                st.error("Bitte fülle alle Pflichtfelder aus!")
            else:
                if user_type=='jugendlich':
                    alter_b=(date.today()-geburtsdatum).days//365
                    st.session_state.user_data.update({'vorname':vorname,'nachname':nachname,'geburtsdatum':geburtsdatum.strftime('%d.%m.%Y'),'alter':alter_b,'hobbies':hobbies,'staerken':staerken,'ziele':ziele,'schulen':schulen_temp,'vater_name':vn,'vater_beruf':vb,'mutter_name':mn,'mutter_beruf':mb,'geschwister':geschwister_temp})
                else:
                    st.session_state.user_data.update({'vorname':vorname,'nachname':nachname,'alter':alter,'hobbies':hobbies,'staerken':staerken,'ziele':ziele,'ausbildung':ausbildung,'position':position,'branche':branche,'erfahrung':erfahrung,'erfolge':erfolge})
                st.session_state.step=3
                st.rerun()
elif st.session_state.step==3:
    st.header("🤖 KI analysiert")
    if 'analysis_done' not in st.session_state:
        if not openai.api_key:
            st.error("Kein OpenAI API Key!")
            st.stop()
        with st.spinner("Analysiere..."):
            try:
                ud=st.session_state.user_data
                pr="Analysiere: Name: "+ud['vorname']+" "+ud['nachname']+", Alter: "+str(ud['alter'])+", Hobbys: "+ud.get('hobbies','N/A')+", Stärken: "+ud['staerken']+", Ziele: "+ud['ziele']+". Antworte JSON: {\"competencies\":[{\"name\":\"...\",\"description\":\"...\",\"strength\":85}],\"quotes\":[{\"text\":\"...\",\"author\":\"...\"}]}"
                resp=openai.ChatCompletion.create(model="gpt-4",messages=[{"role":"system","content":"HR-Experte. Nur JSON."},{"role":"user","content":pr}],temperature=0.7)
                cont=resp.choices[0].message.content.strip()
                if cont.startswith("```"):
                    cont="\n".join(cont.split("\n")[1:-1])
                res=json.loads(cont)
                st.session_state.user_data['competencies']=res['competencies']
                st.session_state.user_data['quotes']=res['quotes']
                st.session_state.analysis_done=True
                st.rerun()
            except Exception as e:
                st.error("Fehler: "+str(e))
                st.stop()
    if st.session_state.get('analysis_done'):
        st.success("Fertig!")
        comp=st.session_state.user_data.get('competencies',[])
        quo=st.session_state.user_data.get('quotes',[])
        st.subheader("Top 3 Kompetenzen:")
        for i,c in enumerate(comp,1):
            st.markdown("**"+str(i)+". "+c['name']+"**")
            st.write(c['description'])
            st.progress(c['strength']/100)
            st.markdown("---")
        st.subheader("Zitate:")
        sel=st.radio("Wähle:",options=range(len(quo)),format_func=lambda i:'"'+quo[i]["text"]+'" - '+quo[i]["author"])
        st.session_state.user_data['selected_quote']=quo[sel]
        if st.button("Weiter →",use_container_width=True):
            st.session_state.step=4
            st.rerun()
elif st.session_state.step==4:
    st.header("🎨 Design")
    des={"Modern":{"colors":["#1a1a1a","#00d4ff"],"icon":"🔷"},"Creative":{"colors":["#ff6b9d","#feca57"],"icon":"🌈"},"Professional":{"colors":["#2c3e50","#3498db"],"icon":"📊"},"Nature":{"colors":["#27ae60","#16a085"],"icon":"🌿"}}
    cols=st.columns(4)
    for idx,(name,data) in enumerate(des.items()):
        with cols[idx]:
            st.markdown('<div style="text-align:center;font-size:3rem">'+data['icon']+'</div>',unsafe_allow_html=True)
            st.markdown("**"+name+"**")
            st.markdown('<div style="background:linear-gradient(135deg,'+data["colors"][0]+','+data["colors"][1]+');height:100px;border-radius:10px"></div>',unsafe_allow_html=True)
            if st.button("Wählen",key="d"+str(idx),use_container_width=True):
                st.session_state.user_data['design']=name
                st.session_state.user_data['colors']=data['colors']
                st.session_state.step=5
                st.rerun()
elif st.session_state.step==5:
    st.header("📄 Dossier")
    ud=st.session_state.user_data
    cl=ud.get('colors',['#3498db','#2ecc71'])
    qu=ud.get('selected_quote',{})
    st.markdown('<div style="background:linear-gradient(135deg,'+cl[0]+','+cl[1]+');padding:60px;border-radius:15px;color:white;text-align:center"><h1>Bewerbungsdossier</h1><h2>'+ud["vorname"]+' '+ud["nachname"]+'</h2><p style="font-style:italic">"'+qu.get("text","")+'"</p><p>— '+qu.get("author","")+'</p></div>',unsafe_allow_html=True)
    if st.button("PDF erstellen",type="primary",use_container_width=True):
        with st.spinner("Erstelle PDF..."):
            try:
                buf=BytesIO()
                doc=SimpleDocTemplate(buf,pagesize=A4)
                story=[]
                sty=getSampleStyleSheet()
                story.append(Paragraph("Bewerbungsdossier",sty['Title']))
                story.append(Spacer(1,0.3*inch))
                story.append(Paragraph(ud['vorname']+" "+ud['nachname'],sty['Heading1']))
                if ud.get('type')=='jugendlich':
                    story.append(Paragraph("Geburtsdatum: "+ud.get('geburtsdatum',''),sty['Normal']))
                story.append(Spacer(1,0.3*inch))
                story.append(Paragraph('"'+qu.get("text","")+'"',sty['Normal']))
                story.append(Paragraph('- '+qu.get("author",""),sty['Normal']))
                story.append(Spacer(1,0.5*inch))
                story.append(Paragraph("Persönliche Daten",sty['Heading2']))
                info="Name: "+ud['vorname']+" "+ud['nachname']+"<br/>Alter: "+str(ud['alter'])
                story.append(Paragraph(info,sty['Normal']))
                story.append(Spacer(1,0.3*inch))
                if ud.get('type')=='jugendlich' and ud.get('schulen'):
                    story.append(Paragraph("Schulbildung",sty['Heading2']))
                    tdata=[['Zeitraum','Schule','Ort','Abschluss']]
                    for sch in ud['schulen']:
                        vd=sch['von'].strftime('%m/%Y') if isinstance(sch['von'],date) else str(sch['von'])
                        bd=sch['bis'].strftime('%m/%Y') if isinstance(sch['bis'],date) else str(sch['bis'])
                        tdata.append([vd+' - '+bd,sch['name'],sch.get('ort',''),sch.get('abschluss','')])
                    t=Table(tdata)
                    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),rl_colors.grey),('TEXTCOLOR',(0,0),(-1,0),rl_colors.whitesmoke),('ALIGN',(0,0),(-1,-1),'LEFT'),('FONTNAME',(0,0),(-1,0),'
