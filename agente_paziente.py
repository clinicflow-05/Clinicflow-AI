import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import re

st.set_page_config(
    page_title="ClinicFlow Italia | Assistente prenotazioni",
    page_icon="CF",
    layout="centered",
    initial_sidebar_state="collapsed"
)

LEADS_FILE = Path("leads_pazienti.csv")
WHATSAPP_CLINICA = "393512259105"
EMAIL_CLINICFLOW = "info@clinicflowitalia.it"

FAQ = {
    "💶 Quanto costa?": (
        "Il costo dipende dal trattamento, dalle tue esigenze e dalla valutazione della clinica. "
        "Puoi inviare una richiesta per ricevere informazioni personalizzate."
    ),
    "💉 Botox fa male?": (
        "Il fastidio è generalmente leggero e varia da persona a persona. "
        "La clinica ti spiegherà trattamento, tempistiche e indicazioni."
    ),
    "💋 Quanto dura il filler?": (
        "La durata varia in base alla zona trattata, al prodotto utilizzato e alle caratteristiche personali."
    ),
    "📅 Posso scegliere giorno e ora?": (
        "Sì. Puoi indicare giorno e fascia oraria preferita. La clinica ti ricontatterà per confermare."
    ),
    "📍 Dove si trova la clinica?": (
        "Puoi indicare la città o la zona che preferisci durante la richiesta. "
        "Ti metteremo in contatto con la sede più adatta."
    ),
    "⏱️ Quanto dura la visita?": (
        "La durata dipende dal trattamento o dalla consulenza. "
        "La clinica ti darà tutte le informazioni precise."
    ),
    "🔄 Posso spostare l’appuntamento?": (
        "Sì, puoi chiedere alla clinica di modificare giorno o orario in base alla disponibilità."
    ),
    "🛡️ I miei dati sono sicuri?": (
        "I tuoi dati vengono utilizzati solo per ricontattarti riguardo alla tua richiesta."
    ),
    "⚠️ Urgenze mediche": (
        "Questo assistente non sostituisce una valutazione medica. "
        "Per urgenze contatta il 112 o un medico."
    )
}

SERVIZI = {
    "Botox": {
        "icona": "👩",
        "descrizione": "Rughe d’espressione, linee sottili e ringiovanimento viso.",
        "domanda": "È la prima volta che fai Botox? Scrivi: Sì oppure No."
    },
    "Filler": {
        "icona": "💉",
        "descrizione": "Volume e armonizzazione di labbra, zigomi e mento.",
        "domanda": "Quale zona ti interessa? Labbra, zigomi, mento, occhiaie oppure altro."
    },
    "Trattamenti viso": {
        "icona": "✨",
        "descrizione": "Dermatologia estetica, PRP, biorivitalizzazione e trattamenti mirati per il viso.",
        "domanda": "Quale trattamento viso ti interessa? Dermatologia estetica, PRP, biorivitalizzazione oppure altro."
    },
    "Trattamenti corpo": {
        "icona": "🌿",
        "descrizione": "Biostimolazione, mesoterapia, radiofrequenza e percorsi per rimodellare il corpo.",
        "domanda": "Quale trattamento corpo ti interessa? Biostimolazione, mesoterapia, radiofrequenza oppure altro."
    }
}

def telefono_valido(telefono):
    cifre = re.sub(r"\D", "", telefono)
    return len(cifre) >= 8

def email_valida(email):
    email = email.strip().lower()
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def salva_lead(dati):
    riga = {
        "Data richiesta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Stato": "Nuovo",
        "Trattamento": dati.get("trattamento", ""),
        "Dettaglio trattamento": dati.get("dettaglio", ""),
        "Città / sede": dati.get("citta", ""),
        "Giorno preferito": dati.get("giorno", ""),
        "Orario preferito": dati.get("orario", ""),
        "Nome e cognome": dati.get("nome", ""),
        "Telefono": dati.get("telefono", ""),
        "Email": dati.get("email", ""),
        "Contatto preferito": dati.get("contatto", ""),
        "Nota": dati.get("nota", ""),
        "Consenso GDPR": "Sì"
    }

    df_nuovo = pd.DataFrame([riga])

    if LEADS_FILE.exists():
        try:
            df_vechi = pd.read_csv(LEADS_FILE)
            df_finale = pd.concat([df_vechi, df_nuovo], ignore_index=True)
        except Exception:
            df_finale = df_nuovo
    else:
        df_finale = df_nuovo

    df_finale.to_csv(LEADS_FILE, index=False)

def messaggio_whatsapp(dati):
    testo = f"""Nuova richiesta ClinicFlow Italia

Trattamento: {dati.get("trattamento", "")}
Dettaglio: {dati.get("dettaglio", "")}
Città / sede: {dati.get("citta", "")}
Giorno preferito: {dati.get("giorno", "")}
Orario preferito: {dati.get("orario", "")}

Nome: {dati.get("nome", "")}
Telefono: {dati.get("telefono", "")}
Email: {dati.get("email", "")}
Contatto preferito: {dati.get("contatto", "")}
Note: {dati.get("nota", "")}"""

    return f"https://wa.me/{WHATSAPP_CLINICA}?text={quote(testo)}"

def nuova_richiesta():
    st.session_state.fase = "trattamento"
    st.session_state.dati = {}
    st.session_state.chat = [
        (
            "assistant",
            "Ciao! 👋 Sono l’assistente prenotazioni 24/7 di ClinicFlow Italia. "
            "Puoi chiedermi informazioni su prezzi, trattamenti e disponibilità oppure richiedere un appuntamento. "
            "Per assistenza puoi scrivere su WhatsApp al numero +39 351 225 9105 oppure a info@clinicflowitalia.it."
        )
    ]

def aggiungi(role, testo):
    st.session_state.chat.append((role, testo))

def risposta_faq(testo):
    t = testo.lower()

    if "urgenza" in t or "emergenza" in t or "sto male" in t:
        return FAQ["⚠️ Urgenze mediche"]

    if "prezzo" in t or "costo" in t or "quanto costa" in t:
        return FAQ["💶 Quanto costa?"]

    if "botox" in t and ("male" in t or "dolore" in t):
        return FAQ["💉 Botox fa male?"]

    if "filler" in t and ("dura" in t or "durata" in t):
        return FAQ["💋 Quanto dura il filler?"]

    if "giorno" in t or "orario" in t or "quando" in t:
        return FAQ["📅 Posso scegliere giorno e ora?"]

    if "dove" in t or "zona" in t or "città" in t or "clinica" in t:
        return FAQ["📍 Dove si trova la clinica?"]

    if "privacy" in t or "dati" in t or "sicuri" in t:
        return FAQ["🛡️ I miei dati sono sicuri?"]

    return (
        "Posso aiutarti con informazioni su trattamenti, costi, disponibilità "
        "oppure puoi iniziare una richiesta di appuntamento."
    )

if "fase" not in st.session_state:
    nuova_richiesta()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 980px;
        padding-top: 2rem;
        padding-bottom: 5rem;
        background: #fbf8f2;
    }

    .hero {
        background: linear-gradient(135deg, #0b2545, #17476b);
        color: white;
        padding: 30px;
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(11, 37, 69, 0.16);
    }

    .hero h1 {
        font-size: 31px;
        margin: 0 0 7px 0;
    }

    .hero p {
        margin: 0;
        font-size: 16px;
        opacity: 0.94;
    }

    .info-box {
        background: #fffdf9;
        border: 1px solid #e6d6bb;
        border-radius: 18px;
        padding: 18px 20px;
        margin: 12px 0 22px 0;
        line-height: 1.65;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    }

    .section-title {
        color: #0b2545;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
        margin: 28px 0 18px 0;
        font-family: Georgia, serif;
    }

    .service-card {
        background: #fffdf9;
        border: 1px solid #eadfce;
        border-radius: 18px;
        padding: 20px 14px 16px 14px;
        text-align: center;
        min-height: 205px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        margin-bottom: 8px;
    }

    .service-icon {
        font-size: 34px;
        margin-bottom: 10px;
    }

    .service-title {
        font-size: 19px;
        font-weight: 800;
        color: #0b2545;
        margin-bottom: 9px;
        font-family: Georgia, serif;
    }

    .service-desc {
        font-size: 14px;
        color: #3f3f3f;
        line-height: 1.45;
        min-height: 62px;
    }

    .assistant-bubble {
        background: #ffffff;
        border: 1px solid #e7dfd2;
        border-left: 4px solid #c69b45;
        border-radius: 16px;
        padding: 14px 16px;
        margin: 12px 0;
        line-height: 1.55;
        box-shadow: 0 5px 16px rgba(0,0,0,0.04);
    }

    .user-bubble {
        background: linear-gradient(135deg, #0b2545, #173d68);
        color: white;
        border-radius: 16px;
        padding: 13px 16px;
        margin: 12px 0 12px auto;
        max-width: 72%;
        line-height: 1.5;
    }

    .appointment-box {
        background: #fffaf0;
        border: 1px solid #d6b77a;
        border-radius: 18px;
        padding: 18px 20px;
        margin: 20px 0;
        line-height: 1.55;
    }

    .success-box {
        background: #eef8f2;
        border: 1px solid #b9dfc7;
        border-radius: 18px;
        padding: 20px;
        margin-top: 18px;
        line-height: 1.6;
    }

    [data-testid="stChatInput"] {
        border-radius: 18px;
    }

    div.stButton > button {
        border-radius: 14px;
        min-height: 44px;
        border: 1px solid #d9c7a6;
        background: #fffdf9;
        color: #0b2545;
        font-weight: 650;
    }

    div.stButton > button:hover {
        border-color: #b8872b;
        color: #0b2545;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero">
        <h1>📅 Richiedi un appuntamento</h1>
        <p>ClinicFlow Italia · Assistente prenotazioni 24/7</p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("🔄 Inizia una nuova richiesta", use_container_width=False):
    nuova_richiesta()
    st.rerun()

st.markdown("<div class='section-title'>Domande frequenti</div>", unsafe_allow_html=True)

faq_items = list(FAQ.keys())
for riga in range(0, len(faq_items), 2):
    col1, col2 = st.columns(2)

    with col1:
        domanda = faq_items[riga]
        if st.button(domanda, key=f"faq_{riga}", use_container_width=True):
            aggiungi("user", domanda)
            aggiungi("assistant", FAQ[domanda])
            st.rerun()

    if riga + 1 < len(faq_items):
        with col2:
            domanda = faq_items[riga + 1]
            if st.button(domanda, key=f"faq_{riga + 1}", use_container_width=True):
                aggiungi("user", domanda)
                aggiungi("assistant", FAQ[domanda])
                st.rerun()

for role, testo in st.session_state.chat:
    if role == "assistant":
        st.markdown(
            f"<div class='assistant-bubble'>🤖 {testo}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='user-bubble'>👤 {testo}</div>",
            unsafe_allow_html=True
        )

fase = st.session_state.fase
dati = st.session_state.dati

if fase == "trattamento":
    st.markdown(
        """
        <div class="appointment-box">
            <b>✨ Vuoi richiedere un appuntamento?</b><br>
            Puoi scegliere un trattamento qui sotto oppure scrivere direttamente:
            “Vorrei Botox Milano”.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>Scegli il trattamento</div>", unsafe_allow_html=True)

    colonne = st.columns(4)

    for indice, (servizio, info) in enumerate(SERVIZI.items()):
        with colonne[indice]:
            st.markdown(
                f"""
                <div class="service-card">
                    <div class="service-icon">{info["icona"]}</div>
                    <div class="service-title">{servizio}</div>
                    <div class="service-desc">{info["descrizione"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Scegli", key=f"servizio_{servizio}", use_container_width=True):
                dati["trattamento"] = servizio
                aggiungi("user", servizio)
                aggiungi("assistant", info["domanda"])
                st.session_state.fase = "dettaglio"
                st.rerun()

elif fase == "dettaglio":
    st.markdown("<div class='appointment-box'><b>Dettaglio della richiesta</b><br>Scrivi una risposta breve per continuare.</div>", unsafe_allow_html=True)

elif fase == "citta":
    st.markdown("<div class='appointment-box'><b>Città / sede preferita</b></div>", unsafe_allow_html=True)

    citta = st.text_input(
        "Città / sede",
        placeholder="Es. Milano, Roma, Civitanova",
        key="input_citta"
    )

    if st.button("Continua", key="continua_citta"):
        if citta.strip():
            dati["citta"] = citta.strip()
            aggiungi("user", citta.strip())
            aggiungi("assistant", "Perfetto. Quando preferisci venire?")
            st.session_state.fase = "giorno"
            st.rerun()
        else:
            st.warning("Inserisci una città o una sede.")

elif fase == "giorno":
    st.markdown("<div class='section-title'>Giorno preferito</div>", unsafe_allow_html=True)

    opzioni_giorno = ["Oggi", "Domani", "Questa settimana", "La prossima settimana", "Non ho preferenze"]
    for riga in range(0, len(opzioni_giorno), 2):
        col1, col2 = st.columns(2)

        with col1:
            giorno = opzioni_giorno[riga]
            if st.button(giorno, key=f"giorno_{riga}", use_container_width=True):
                dati["giorno"] = giorno
                aggiungi("user", giorno)
                aggiungi("assistant", "Quale fascia oraria preferisci?")
                st.session_state.fase = "orario"
                st.rerun()

        if riga + 1 < len(opzioni_giorno):
            with col2:
                giorno = opzioni_giorno[riga + 1]
                if st.button(giorno, key=f"giorno_{riga + 1}", use_container_width=True):
                    dati["giorno"] = giorno
                    aggiungi("user", giorno)
                    aggiungi("assistant", "Quale fascia oraria preferisci?")
                    st.session_state.fase = "orario"
                    st.rerun()

elif fase == "orario":
    st.markdown("<div class='section-title'>Orario preferito</div>", unsafe_allow_html=True)

    opzioni_orario = ["Mattina", "Pomeriggio", "Sera", "Non ho preferenze"]
    for riga in range(0, len(opzioni_orario), 2):
        col1, col2 = st.columns(2)

        with col1:
            orario = opzioni_orario[riga]
            if st.button(orario, key=f"orario_{riga}", use_container_width=True):
                dati["orario"] = orario
                aggiungi("user", orario)
                aggiungi("assistant", "Come ti chiami?")
                st.session_state.fase = "nome"
                st.rerun()

        if riga + 1 < len(opzioni_orario):
            with col2:
                orario = opzioni_orario[riga + 1]
                if st.button(orario, key=f"orario_{riga + 1}", use_container_width=True):
                    dati["orario"] = orario
                    aggiungi("user", orario)
                    aggiungi("assistant", "Come ti chiami?")
                    st.session_state.fase = "nome"
                    st.rerun()

elif fase == "nome":
    nome = st.text_input("Nome e cognome", placeholder="Es. Maria Rossi", key="input_nome")

    if st.button("Continua", key="continua_nome"):
        if len(nome.strip()) >= 3:
            dati["nome"] = nome.strip()
            aggiungi("user", nome.strip())
            aggiungi("assistant", "Inserisci il tuo numero di telefono o WhatsApp.")
            st.session_state.fase = "telefono"
            st.rerun()
        else:
            st.warning("Inserisci nome e cognome.")

elif fase == "telefono":
    telefono = st.text_input(
        "Telefono / WhatsApp",
        placeholder="Es. +39 351 225 9105",
        key="input_telefono"
    )

    if st.button("Continua", key="continua_telefono"):
        if telefono_valido(telefono):
            dati["telefono"] = telefono.strip()
            aggiungi("user", telefono.strip())
            aggiungi("assistant", "Inserisci la tua email per ricevere conferma.")
            st.session_state.fase = "email"
            st.rerun()
        else:
            st.warning("Inserisci un numero di telefono valido.")

elif fase == "email":
    email = st.text_input(
        "Email",
        placeholder="Es. nome@email.it",
        key="input_email"
    )

    if st.button("Continua", key="continua_email"):
        if email_valida(email):
            dati["email"] = email.strip().lower()
            aggiungi("user", dati["email"])
            aggiungi("assistant", "Come preferisci essere ricontattata/o?")
            st.session_state.fase = "contatto"
            st.rerun()
        else:
            st.warning("Inserisci un indirizzo email valido.")

elif fase == "contatto":
    contatto = st.radio(
        "Contatto preferito",
        ["WhatsApp", "Telefono", "Email"],
        horizontal=True,
        key="input_contatto"
    )

    if st.button("Continua", key="continua_contatto"):
        dati["contatto"] = contatto
        aggiungi("user", contatto)
        aggiungi("assistant", "Vuoi aggiungere una nota? Puoi scrivere anche “No”.")
        st.session_state.fase = "nota"
        st.rerun()

elif fase == "nota":
    nota = st.text_area(
        "Note per la clinica",
        placeholder="Es. Vorrei sapere disponibilità e prezzo. Oppure scrivi No.",
        key="input_nota"
    )

    consenso = st.checkbox(
        "Acconsento al trattamento dei dati per essere ricontattata/o riguardo alla mia richiesta.",
        key="consenso_gdpr"
    )

    if st.button("Invia richiesta", key="invia_richiesta", use_container_width=True):
        if not consenso:
            st.warning("Per inviare la richiesta devi accettare il consenso dati.")
        else:
            dati["nota"] = "" if nota.strip().lower() == "no" else nota.strip()
            salva_lead(dati)
            aggiungi("assistant", "Grazie! La tua richiesta è stata registrata. La clinica ti ricontatterà appena possibile.")
            st.session_state.fase = "conferma"
            st.rerun()

elif fase == "conferma":
    link_whatsapp = messaggio_whatsapp(dati)

    st.markdown(
        f"""
        <div class="success-box">
            <b>✓ Richiesta inviata con successo</b><br><br>
            Grazie <b>{dati.get("nome", "")}</b>. La tua richiesta per
            <b>{dati.get("trattamento", "")}</b> è stata registrata.<br><br>
            La clinica ti ricontatterà tramite <b>{dati.get("contatto", "")}</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        "Apri WhatsApp con il riepilogo della richiesta",
        link_whatsapp,
        use_container_width=True
    )

    st.caption(
        "La richiesta viene salvata nel file leads_pazienti.csv. "
        "L’invio automatico di email e WhatsApp verrà configurato quando pubblichiamo l’agente online."
    )

messaggio = st.chat_input("Scrivi qui una domanda...")

if messaggio:
    aggiungi("user", messaggio)

    fase = st.session_state.fase
    dati = st.session_state.dati
    testo = messaggio.strip()

    if fase == "trattamento":
        testo_basso = testo.lower()

        servizio_trovato = None
        if "botox" in testo_basso:
            servizio_trovato = "Botox"
        elif "filler" in testo_basso:
            servizio_trovato = "Filler"
        elif any(parola in testo_basso for parola in ["prp", "viso", "dermatologia", "biorivitalizzazione"]):
            servizio_trovato = "Trattamenti viso"
        elif any(parola in testo_basso for parola in ["corpo", "mesoterapia", "biostimolazione", "cellulite", "rimodellamento"]):
            servizio_trovato = "Trattamenti corpo"

        if servizio_trovato:
            dati["trattamento"] = servizio_trovato
            aggiungi("assistant", f"Perfetto. Hai scelto {servizio_trovato}. {SERVIZI[servizio_trovato]['domanda']}")
            st.session_state.fase = "dettaglio"
        else:
            aggiungi("assistant", risposta_faq(testo))

    elif fase == "dettaglio":
        dati["dettaglio"] = testo
        aggiungi("assistant", "Perfetto. In quale città o sede preferisci fare il trattamento?")
        st.session_state.fase = "citta"

    elif fase == "citta":
        dati["citta"] = testo
        aggiungi("assistant", "Perfetto. Quando preferisci venire?")
        st.session_state.fase = "giorno"

    elif fase == "giorno":
        dati["giorno"] = testo
        aggiungi("assistant", "Quale fascia oraria preferisci?")
        st.session_state.fase = "orario"

    elif fase == "orario":
        dati["orario"] = testo
        aggiungi("assistant", "Come ti chiami?")
        st.session_state.fase = "nome"

    elif fase == "nome":
        dati["nome"] = testo
        aggiungi("assistant", "Inserisci il tuo numero di telefono o WhatsApp.")
        st.session_state.fase = "telefono"

    elif fase == "telefono":
        if telefono_valido(testo):
            dati["telefono"] = testo
            aggiungi("assistant", "Inserisci la tua email per ricevere conferma.")
            st.session_state.fase = "email"
        else:
            aggiungi("assistant", "Inserisci un numero di telefono valido, ad esempio +39 351 225 9105.")

    elif fase == "email":
        if email_valida(testo):
            dati["email"] = testo.lower()
            aggiungi("assistant", "Come preferisci essere ricontattata/o? WhatsApp, Telefono oppure Email?")
            st.session_state.fase = "contatto"
        else:
            aggiungi("assistant", "Inserisci un indirizzo email valido, ad esempio nome@email.it.")

    elif fase == "contatto":
        dati["contatto"] = testo
        aggiungi("assistant", "Vuoi aggiungere una nota? Puoi scrivere anche No.")
        st.session_state.fase = "nota"

    elif fase == "nota":
        dati["nota"] = "" if testo.lower() == "no" else testo
        salva_lead(dati)
        aggiungi("assistant", "Grazie! La tua richiesta è stata registrata. La clinica ti ricontatterà appena possibile.")
        st.session_state.fase = "conferma"

    else:
        aggiungi("assistant", risposta_faq(testo))

    st.rerun()

st.divider()
st.caption("© ClinicFlow Italia · Assistente prenotazioni 24/7 · WhatsApp: +39 351 225 9105")