import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import re
import requests

WEBHOOK_GOOGLE_SHEETS = "https://script.google.com/macros/s/AKfycbyl0FgDCCuyYdzOc1F2CwwgbUjOMJuDU7CDu9MV3LSvmVs_W8SivIBb5j6EhnY3XmpbIg/exec"

def invia_a_google_sheets(row):
    try:
     response = requests.post(WEBHOOK_GOOGLE_SHEETS, json=row, timeout=10)
     print("Google Sheets status:", response.status_code)
     print("Google Sheets response:", response.text)
    except Exception as e:
        print("Eroare Google Sheets:", e)
st.set_page_config(
    page_title="Assistente Prenotazioni",
    page_icon="📅",
    layout="centered"
)

LEADS_FILE = Path("leads_pazienti.csv")

# Date ClinicFlow
WHATSAPP_CLINICA = "393512259105"
EMAIL_CLINICFLOW = "info@clinicflowitalia.it"

TRATTAMENTI = [
    "Botox",
    "Filler",
    "Dermatologia estetica",
    "Biostimolazione",
    "PRP",
    "Mesoterapia",
    "Biorivitalizzazione",
    "Longevità e benessere",
    "Altro"
]

DOMANDE = {
    "Botox": "È la prima volta che fai Botox? Scrivi: Sì oppure No.",
    "Filler": "Quale zona ti interessa? Labbra, zigomi, mento, occhiaie oppure altro.",
    "Dermatologia estetica": "Ti interessa una visita dermatologica o un trattamento estetico?",
    "Biostimolazione": "Hai già fatto biostimolazione? Scrivi: Sì oppure No.",
    "PRP": "Per quale esigenza ti interessa il PRP? Capelli, viso oppure altro.",
    "Mesoterapia": "Quale zona vuoi trattare? Viso, corpo, capelli oppure altro.",
    "Biorivitalizzazione": "È per viso, collo/decolleté oppure mani?",
    "Longevità e benessere": "Quale obiettivo ti interessa? Energia, anti-age, benessere generale oppure altro.",
    "Altro": "Descrivi brevemente la tua richiesta."
}

FAQ = {
    "💶 Quanto costa?":
        "Il costo dipende dal trattamento, dalle tue esigenze e dalla valutazione del medico. "
        "Per ricevere un’indicazione personalizzata, ti mettiamo in contatto con una clinica della tua zona per una consulenza.",

    "💉 Botox fa male?":
        "Il fastidio è generalmente leggero e varia da persona a persona. Durante la consulenza la clinica ti spiegherà trattamento, tempistiche e indicazioni.",

    "💋 Quanto dura il filler?":
        "La durata può variare in base alla zona trattata, al prodotto utilizzato e alle caratteristiche personali. "
        "La clinica potrà darti un’indicazione più precisa dopo la valutazione.",

    "📅 Posso scegliere giorno e ora?":
        "Sì. Puoi indicare giorno e fascia oraria preferita. La clinica controllerà la disponibilità e ti ricontatterà per confermare l’appuntamento.",

    "📍 Dove si trova la clinica?":
        "Ti mettiamo in contatto con una clinica disponibile nella zona o città che preferisci. Puoi indicare la città durante la richiesta.",

    "⏱️ Quanto dura la visita?":
        "La durata dipende dal tipo di trattamento o consulenza. La clinica ti darà informazioni più precise prima della conferma.",

    "🔄 Posso spostare l’appuntamento?":
        "Sì, potrai chiedere alla clinica di modificare giorno o orario in base alla disponibilità.",

    "🛡️ I miei dati sono sicuri?":
        "I dati vengono usati solo per ricontattarti riguardo alla richiesta di appuntamento.",

    "⚠️ Urgenze mediche":
        "Questo assistente non sostituisce una valutazione medica. Per urgenze mediche contatta il 112, il medico o la struttura sanitaria più vicina."
}


def telefono_valido(tel):
    cifre = re.sub(r"\D", "", tel)
    return len(cifre) >= 8, cifre


def email_valida(email):
    email = email.strip().lower()

    if "@" not in email:
        return False, email

    parte_dopo = email.split("@")[-1]

    ok = (
        "." in parte_dopo
        and not email.startswith("@")
        and not email.endswith(".")
        and len(email) >= 6
    )

    return ok, email


def salva_lead(dati):
    row = {
        "Data richiesta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Stato": "Nuovo",
        "Trattamento": dati.get("trattamento", ""),
        "Dettaglio trattamento": dati.get("dettaglio", ""),
        "Nome e cognome": dati.get("nome", ""),
        "Telefono": dati.get("telefono", ""),
        "Email": dati.get("email", ""),
        "Città / sede": dati.get("citta", ""),
        "Giorno preferito": dati.get("giorno", ""),
        "Orario preferito": dati.get("orario", ""),
        "Contatto preferito": dati.get("contatto", ""),
        "Nota": dati.get("nota", ""),
        "Consenso GDPR": "Sì"
    }

    df_nuovo = pd.DataFrame([row])

    if LEADS_FILE.exists():
        df_vecchio = pd.read_csv(LEADS_FILE)
        df = pd.concat([df_vecchio, df_nuovo], ignore_index=True)
    else:
        df = df_nuovo

    df.to_csv(LEADS_FILE, index=False)
    invia_a_google_sheets(row)
    print("am ajuns la google sheet")

def aggiungi(role, testo):
    st.session_state.chat.append((role, testo))


def vai_in_fondo():
    st.components.v1.html(
        """
        <script>
        setTimeout(function() {
            window.parent.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }, 250);
        </script>
        """,
        height=0
    )


def nuova_richiesta():
    st.session_state.fase = "trattamento"
    st.session_state.dati = {}
    st.session_state.chat = [
        (
            "assistant",
            f"Ciao! 👋 Sono l’assistente prenotazioni 24/7. "
            f"Puoi chiedermi informazioni su prezzi, trattamenti e disponibilità oppure richiedere un appuntamento. "
            f"Anche quando la reception è occupata, puoi lasciare qui la tua richiesta. "
            f"Per assistenza puoi scrivere a {EMAIL_CLINICFLOW}."
        )
    ]


def capisci_richiesta_libera(testo):
    t = testo.lower().strip()

    trattamenti = {
        "botox": "Botox",
        "filler": "Filler",
        "dermatologia": "Dermatologia estetica",
        "biostimolazione": "Biostimolazione",
        "prp": "PRP",
        "mesoterapia": "Mesoterapia",
        "biorivitalizzazione": "Biorivitalizzazione",
        "longevita": "Longevità e benessere",
        "longevità": "Longevità e benessere",
        "benessere": "Longevità e benessere"
    }

    citta_lista = [
        "milano",
        "roma",
        "bologna",
        "torino",
        "napoli",
        "firenze",
        "civitanova",
        "ancona",
        "pesaro",
        "macerata",
        "verona",
        "genova",
        "bari",
        "palermo"
    ]

    trattamento_trovato = None

    for parola, nome in trattamenti.items():
        if parola in t:
            trattamento_trovato = nome
            break

    citta_trovata = None

    for citta in citta_lista:
        if citta in t:
            citta_trovata = citta.capitalize()
            break

    return trattamento_trovato, citta_trovata


def risposta_faq_testo(testo):
    t = testo.lower().strip()

    if "urgenza" in t or "emergenza" in t or "sto male" in t:
        return FAQ["⚠️ Urgenze mediche"]

    if "costo" in t or "prezzo" in t or "quanto costa" in t:
        return FAQ["💶 Quanto costa?"] + " Se vuoi, puoi richiedere un appuntamento."

    if "botox" in t and ("male" in t or "dolore" in t or "fa male" in t):
        return FAQ["💉 Botox fa male?"] + " Se vuoi, puoi richiedere un appuntamento."

    if "filler" in t and ("dura" in t or "durata" in t):
        return FAQ["💋 Quanto dura il filler?"] + " Se vuoi, puoi richiedere un appuntamento."

    if "giorno" in t or "orario" in t or "quando" in t or "appuntamento" in t:
        return FAQ["📅 Posso scegliere giorno e ora?"] + " Puoi iniziare la richiesta qui sotto."

    if "dove" in t or "zona" in t or "città" in t or "clinica" in t:
        return FAQ["📍 Dove si trova la clinica?"] + " Puoi richiedere un appuntamento qui sotto."

    if "dati" in t or "privacy" in t or "sicuri" in t:
        return FAQ["🛡️ I miei dati sono sicuri?"]

    return (
        "Posso aiutarti con informazioni su trattamenti, costi, disponibilità "
        "o richiesta appuntamento. Per esempio puoi scrivere: “Vorrei Botox a Milano”."
    )


if "fase" not in st.session_state:
    nuova_richiesta()


st.markdown("""
<style>
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}
.hero {
    background: linear-gradient(135deg, #173d5b, #28789a);
    color: white;
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 20px;
}
.box {
    background: #f8fbfd;
    border: 1px solid #dce7ee;
    padding: 16px;
    color:#1f2937 !important;
    min-height: auto !important;                
    border-radius: 14px;
    margin-bottom: 18px;
}
.assistant {
    background: #fff7e8;
    color: #1f2937 !important;        
    border-left: 4px solid #e9a11a;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
}
.user {
    background: #f2f4f7;
    color: #1f2937 !important;        
    border-left: 4px solid #d94f4f;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
}
.start-box {
    background: #eef8f2;
    border: 1px solid #cfead9;
    padding: 14px;
    border-radius: 14px;
    margin: 12px 0;
    color: #1f2937 !important;        
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>📅 Richiedi un appuntamento</h1>
    <p>Disponibile 24/7: lascia la tua richiesta anche quando la reception è occupata.</p>
</div>
""", unsafe_allow_html=True)


st.markdown(f"""
<div class="box">
    <b>Come funziona:</b> scegli il trattamento → indica quando preferisci → lascia i tuoi contatti → la clinica conferma disponibilità, giorno e orario.
    <br><b>Nessun pagamento ora.</b>
    <br><b>Email assistenza:</b> {EMAIL_CLINICFLOW}
    <br><b>WhatsApp assistenza:</b> +39 351 225 9105
    <br><br>
    <small>L’assistente non sostituisce una valutazione medica. Per urgenze contatta il 112 o un medico.</small>
</div>
""", unsafe_allow_html=True)


if st.button("🔄 Inizia una nuova richiesta"):
    nuova_richiesta()
    st.rerun()


st.subheader("Domande frequenti")

faq_cols = st.columns(2)

for i, (domanda, risposta) in enumerate(FAQ.items()):
    with faq_cols[i % 2]:
        if st.button(domanda, use_container_width=True, key=f"faq_{domanda}"):
            aggiungi("user", domanda)
            aggiungi("assistant", risposta + " Puoi richiedere un appuntamento qui sotto.")
            st.session_state.auto_scroll = True
            st.rerun()


for role, testo in st.session_state.chat:
    css = "assistant" if role == "assistant" else "user"
    icon = "🤖" if role == "assistant" else "👤"
    st.markdown(
        f'<div class="{css}">{icon} {testo}</div>',
        unsafe_allow_html=True
    )
if st.session_state.fase== "inizio":
     st.markdown("""
    <div class="start-box">
    <b>Vuoi richiedere un appuntamento?</b><br>
    Puoi scegliere un trattamento qui sotto oppure scrivere direttamente: “Vorrei Botox Milano”.
</div>
""", unsafe_allow_html=True)


fase = st.session_state.fase
dati = st.session_state.dati


if fase == "trattamento":
    st.subheader("Scegli il trattamento")

    cols = st.columns(2)

    for i, trattamento in enumerate(TRATTAMENTI):
        with cols[i % 2]:
            if st.button(
                trattamento,
                use_container_width=True,
                key=f"trattamento_{trattamento}"
            ):
                dati["trattamento"] = trattamento
                aggiungi("user", trattamento)
                aggiungi("assistant", DOMANDE[trattamento])
                st.session_state.fase = "dettaglio"
                st.session_state.auto_scroll = True
                st.rerun()


elif fase == "dettaglio":
    val = st.text_input("Risposta", placeholder="Scrivi qui...")

    if st.button("Continua"):
        if val.strip():
            dati["dettaglio"] = val.strip()
            aggiungi("user", val.strip())
            aggiungi(
                "assistant",
                "Perfetto. In quale città o sede preferisci fare il trattamento?"
            )
            st.session_state.fase = "citta"
            st.session_state.auto_scroll = True
            st.rerun()
        else:
            st.warning("Scrivi una risposta per continuare.")


elif fase == "citta":
    val = st.text_input(
        "Città / sede",
        placeholder="Es. Milano, Roma, Civitanova"
    )

    if st.button("Continua"):
        if val.strip():
            dati["citta"] = val.strip()
            aggiungi("user", val.strip())
            aggiungi("assistant", "Quando preferisci venire?")
            st.session_state.fase = "giorno"
            st.session_state.auto_scroll = True
            st.rerun()
        else:
            st.warning("Inserisci città o sede.")


elif fase == "giorno":
    st.subheader("Giorno preferito")

    giorni = [
        "Oggi",
        "Domani",
        "Questa settimana",
        "La prossima settimana",
        "Non ho preferenze"
    ]

    cols = st.columns(2)

    for i, giorno in enumerate(giorni):
        with cols[i % 2]:
            if st.button(
                giorno,
                use_container_width=True,
                key=f"giorno_{giorno}"
            ):
                dati["giorno"] = giorno
                aggiungi("user", giorno)
                aggiungi("assistant", "Quale fascia oraria preferisci?")
                st.session_state.fase = "orario"
                st.session_state.auto_scroll = True
                st.rerun()


elif fase == "orario":
    st.subheader("Fascia oraria")

    orari = [
        "Mattina",
        "Pomeriggio",
        "Sera",
        "Non ho preferenze"
    ]

    cols = st.columns(2)

    for i, orario in enumerate(orari):
        with cols[i % 2]:
            if st.button(
                orario,
                use_container_width=True,
                key=f"orario_{orario}"
            ):
                dati["orario"] = orario
                aggiungi("user", orario)
                aggiungi("assistant", "Come ti chiami? Scrivi nome e cognome.")
                st.session_state.fase = "nome"
                st.session_state.auto_scroll = True
                st.rerun()


elif fase == "nome":
    val = st.text_input(
        "Nome e cognome",
        placeholder="Es. Maria Rossi"
    )

    if st.button("Continua"):
        if len(val.strip()) >= 2:
            dati["nome"] = val.strip()
            aggiungi("user", val.strip())
            aggiungi("assistant", "Qual è il tuo numero di telefono o WhatsApp?")
            st.session_state.fase = "telefono"
            st.session_state.auto_scroll = True
            st.rerun()
        else:
            st.warning("Inserisci nome e cognome.")


elif fase == "telefono":
    val = st.text_input(
        "Telefono / WhatsApp",
        placeholder="Es. +39 333 1234567"
    )

    if st.button("Continua"):
        ok, tel = telefono_valido(val)

        if not ok:
            st.error("Numero non valido. Inserisci almeno 8 cifre.")
        else:
            dati["telefono"] = tel
            aggiungi("user", tel)
            aggiungi("assistant", "Qual è il tuo indirizzo email?")
            st.session_state.fase = "email"
            st.session_state.auto_scroll = True
            st.rerun()


elif fase == "email":
    val = st.text_input(
        "Email",
        placeholder="Es. nome@email.it"
    )

    if st.button("Continua"):
        ok, email = email_valida(val)

        if not ok:
            st.error(
                "Email non valida. Inserisci un indirizzo con @, per esempio nome@email.it."
            )
        else:
            dati["email"] = email
            aggiungi("user", email)
            aggiungi("assistant", "Come preferisci essere ricontattato?")
            st.session_state.fase = "contatto"
            st.session_state.auto_scroll = True
            st.rerun()


elif fase == "contatto":
    cols = st.columns(3)

    for i, contatto in enumerate(["WhatsApp", "Telefonata", "Email"]):
        with cols[i]:
            if st.button(
                contatto,
                use_container_width=True,
                key=f"contatto_{contatto}"
            ):
                dati["contatto"] = contatto
                aggiungi("user", contatto)
                aggiungi(
                    "assistant",
                    "Vuoi aggiungere una nota? Scrivi il messaggio oppure “nessuna”."
                )
                st.session_state.fase = "nota"
                st.session_state.auto_scroll = True
                st.rerun()


elif fase == "nota":
    val = st.text_input(
        "Nota",
        placeholder="Scrivi una nota oppure nessuna"
    )

    if st.button("Continua"):
        if val.strip():
            if val.strip().lower() in ["nessuna", "nessuno", "no"]:
                dati["nota"] = ""
            else:
                dati["nota"] = val.strip()

            aggiungi("user", val.strip())
            aggiungi(
                "assistant",
                "Ultimo passaggio: confermi il consenso al trattamento dei dati?"
            )
            st.session_state.fase = "gdpr"
            st.session_state.auto_scroll = True
            st.rerun()
        else:
            st.warning("Scrivi una nota oppure 'nessuna'.")


elif fase == "gdpr":
    consenso = st.checkbox(
        "Acconsento al trattamento dei miei dati per essere ricontattato dalla clinica."
    )

    if st.button("✅ Invia richiesta"):
        if consenso:
            salva_lead(dati)

            nome = dati.get("nome", "")

            aggiungi(
                "assistant",
                f"Grazie {nome}! ✅ Abbiamo registrato la tua richiesta.\n\n"
                f"Trattamento: {dati.get('trattamento', '')}\n"
                f"Dettaglio: {dati.get('dettaglio', '')}\n"
                f"Città / sede: {dati.get('citta', '')}\n"
                f"Giorno: {dati.get('giorno', '')}\n"
                f"Orario: {dati.get('orario', '')}\n\n"
                f"La clinica ti ricontatterà per confermare disponibilità e appuntamento. "
                f"Per assistenza puoi scrivere su WhatsApp al +39 351 225 9105 "
                f"oppure via email a {EMAIL_CLINICFLOW}."
            )

            st.session_state.fase = "concluso"
            st.session_state.auto_scroll = True
            st.rerun()

        else:
            st.warning("Per inviare la richiesta devi confermare il consenso.")


elif fase == "concluso":
    st.success("Richiesta registrata con successo.")

    testo_whatsapp = (
        "Ciao, ho appena inviato una richiesta di appuntamento.\n\n"
        f"Trattamento: {dati.get('trattamento', '')}\n"
        f"Città / sede: {dati.get('citta', '')}\n"
        f"Preferenza: {dati.get('giorno', '')} - {dati.get('orario', '')}\n"
        f"Nome: {dati.get('nome', '')}"
    )

    link = f"https://wa.me/{WHATSAPP_CLINICA}?text={quote(testo_whatsapp)}"

    st.markdown(
        f"""
        <a href="{link}" target="_blank" style="
            display:inline-block;
            background:#25D366;
            color:white;
            padding:13px 20px;
            border-radius:10px;
            text-decoration:none;
            font-weight:700;
            margin-top:10px;">
            💬 Scrivi ora alla clinica su WhatsApp
        </a>
        """,
        unsafe_allow_html=True
    )


msg = st.chat_input("Scrivi qui una domanda...")

if msg:
    aggiungi("user", msg)

    trattamento, citta = capisci_richiesta_libera(msg)

    if trattamento and citta:
        st.session_state.dati["trattamento"] = trattamento
        st.session_state.dati["citta"] = citta
        st.session_state.fase = "giorno"

        aggiungi(
            "assistant",
            f"Perfetto! Ho capito che ti interessa {trattamento} a {citta}. "
            "Quando preferisci venire?"
        )

    elif trattamento:
        st.session_state.dati["trattamento"] = trattamento
        st.session_state.fase = "dettaglio"

        aggiungi(
            "assistant",
            f"Perfetto, ti interessa {trattamento}. {DOMANDE[trattamento]}"
        )

    else:
        aggiungi("assistant", risposta_faq_testo(msg))

    st.session_state.auto_scroll = True
    st.rerun()


if st.session_state.get("auto_scroll", False):
    vai_in_fondo()
    st.session_state.auto_scroll = False


st.divider()

st.caption(
    f"© ClinicFlow Italia • Assistente prenotazioni 24/7 • "
    f"WhatsApp +39 351 225 9105 • {EMAIL_CLINICFLOW}"
)