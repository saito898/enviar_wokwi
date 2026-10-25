import time
import json
import streamlit as st
import paho.mqtt.client as paho


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="MQTT Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BROKER = "157.230.214.127"
PORT = 1883
TOPIC_DIGITAL = "saito1"
TOPIC_ANALOG = "saito2"


# =====================================================
# ESTILOS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(119,94,255,.17), transparent 30%),
        radial-gradient(circle at 95% 35%, rgba(44,207,230,.10), transparent 28%),
        #0b1020;
    color: #f3f4ff;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: #f3f4ff !important;
}

p {
    color: #aab6d1;
}

.hero {
    text-align: center;
    padding: 25px 10px 30px;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(38px, 6vw, 58px);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -2px;
    color: #f6f5ff;
}

.hero-description {
    max-width: 650px;
    margin: 14px auto 0;
    color: #aab6d1;
    font-size: 16px;
    line-height: 1.8;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(21,31,53,.78);
    border: 1px solid rgba(164,177,255,.16);
    border-radius: 20px;
}

div[data-testid="stMetric"] {
    background: rgba(21,31,53,.8);
    border: 1px solid rgba(164,177,255,.14);
    border-radius: 15px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #9facc9;
}

div[data-testid="stMetricValue"] {
    color: #f0f1ff;
}

.stButton > button {
    width: 100%;
    min-height: 52px;
    border-radius: 13px;
    border: 1px solid rgba(182,171,255,.35);
    background: linear-gradient(105deg,#8978fa,#6856dc);
    color: white;
    font-size: 15px;
    font-weight: 700;
    transition: .2s ease;
}

.stButton > button:hover {
    background: linear-gradient(105deg,#a095ff,#7d6df0);
    color: white;
    border-color: #c6beff;
    transform: translateY(-1px);
}

div[data-testid="stSlider"] [data-baseweb="slider"] {
    margin-top: 12px;
}

.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #a89aff;
    border-color: #a89aff;
}

div[data-testid="stAlert"] {
    border-radius: 13px;
}

hr {
    border-color: rgba(164,177,255,.15);
}

.status-label {
    color: #8f9dbb;
    font-size: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.footer {
    text-align: center;
    color: #7281a2;
    font-size: 12px;
    line-height: 2;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# ESTADO DE LA APLICACIÓN
# =====================================================

if "estado_digital" not in st.session_state:
    st.session_state.estado_digital = "OFF"

if "valor_analogico" not in st.session_state:
    st.session_state.valor_analogico = 0.0

if "ultimo_mensaje" not in st.session_state:
    st.session_state.ultimo_mensaje = ""


# =====================================================
# FUNCIONES MQTT
# =====================================================

def enviar_mqtt(topic, payload):
    """Publica un mensaje JSON en el broker MQTT."""

    cliente = None

    try:
        client_id = "Salitostreamlit_" + str(int(time.time() * 1000))

        # Compatible con diferentes versiones de paho-mqtt
        try:
            cliente = paho.Client(
                callback_api_version=paho.CallbackAPIVersion.VERSION1,
                client_id=client_id
            )
        except (AttributeError, TypeError):
            cliente = paho.Client(client_id=client_id)

        cliente.connect(BROKER, PORT, keepalive=30)
        cliente.loop_start()

        mensaje = json.dumps(payload, ensure_ascii=False)
        resultado = cliente.publish(topic, mensaje, qos=0)

        resultado.wait_for_publish(timeout=10)

        if resultado.is_published():
            st.session_state.ultimo_mensaje = (
                f"Tema: {topic} | Mensaje: {mensaje}"
            )
            return True, mensaje

        return False, "No se pudo confirmar la publicación MQTT."

    except Exception as error:
        return False, str(error)

    finally:
        if cliente is not None:
            try:
                cliente.loop_stop()
                cliente.disconnect()
            except Exception:
                pass


# =====================================================
# ENCABEZADO
# =====================================================

st.markdown("""
<div class="hero">
    <div style="
        color:#b9b0ff;
        letter-spacing:3px;
        font-size:12px;
        font-weight:700;
        margin-bottom:18px;
    ">
        ✦ INTERFACES MULTIMODALES ✦
    </div>
    <div class="hero-title">
        MQTT <span style="color:#9586ff;">Control.</span>
    </div>
    <div class="hero-description">
        Controla las salidas digitales y los valores analógicos
        desde una interfaz interactiva conectada a tu dispositivo.
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# INDICADORES
# =====================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "⚡ SALIDA DIGITAL",
        st.session_state.estado_digital
    )

with c2:
    st.metric(
        "〰️ VALOR ANALÓGICO",
        f"{st.session_state.valor_analogico:.1f}"
    )

with c3:
    st.metric(
        "📡 PROTOCOLO",
        "MQTT"
    )

st.write("")


# =====================================================
# PANELES DE CONTROL
# =====================================================

col_digital, col_analogico = st.columns(2, gap="large")


# =====================================================
# CONTROL DIGITAL ON / OFF
# =====================================================

with col_digital:

    with st.container(border=True):

        st.subheader("⚡ Control digital")

        st.write(
            "Enciende o apaga la salida enviando un comando "
            "al dispositivo conectado."
        )

        st.divider()

        if st.session_state.estado_digital == "ON":
            st.success("Estado actual: ENCENDIDO")
        else:
            st.info("Estado actual: APAGADO")

        col_on, col_off = st.columns(2)

        with col_on:
            if st.button("🟢 ENCENDER", use_container_width=True):

                with st.spinner("Enviando comando..."):

                    correcto, respuesta = enviar_mqtt(
                        TOPIC_DIGITAL,
                        {"Act1": "ON"}
                    )

                if correcto:
                    st.session_state.estado_digital = "ON"
                    st.success("Comando ON enviado.")
                    st.rerun()
                else:
                    st.error("No se pudo enviar el comando.")
                    st.caption(str(respuesta))

        with col_off:
            if st.button("🔴 APAGAR", use_container_width=True):

                with st.spinner("Enviando comando..."):

                    correcto, respuesta = enviar_mqtt(
                        TOPIC_DIGITAL,
                        {"Act1": "OFF"}
                    )

                if correcto:
                    st.session_state.estado_digital = "OFF"
                    st.success("Comando OFF enviado.")
                    st.rerun()
                else:
                    st.error("No se pudo enviar el comando.")
                    st.caption(str(respuesta))


# =====================================================
# CONTROL ANALÓGICO
# =====================================================

with col_analogico:

    with st.container(border=True):

        st.subheader("〰️ Control analógico")

        st.write(
            "Selecciona un valor entre 0 y 100 y envíalo "
            "al dispositivo mediante MQTT."
        )

        st.divider()

        valor = st.slider(
            "Selecciona el rango de valores",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.valor_analogico),
            step=1.0,
            key="slider_analogico"
        )

        st.session_state.valor_analogico = valor

        st.markdown(
            f"<div style='text-align:center; padding:15px 0;'>"
            f"<div style='color:#8f9dbb; font-size:12px; "
            f"letter-spacing:2px;'>VALOR SELECCIONADO</div>"
            f"<div style='font-size:48px; font-weight:800; "
            f"color:#a89aff;'>{valor:.1f}</div>"
            f"<div style='color:#8f9dbb;'>de 100</div>"
            f"</div>",
            unsafe_allow_html=True
        )

        if st.button(
            "📡 ENVIAR VALOR ANALÓGICO",
            use_container_width=True
        ):

            with st.spinner("Enviando valor..."):

                correcto, respuesta = enviar_mqtt(
                    TOPIC_ANALOG,
                    {"Analog": float(valor)}
                )

            if correcto:
                st.success(f"Valor {valor:.1f} enviado correctamente.")
            else:
                st.error("No se pudo enviar el valor.")
                st.caption(str(respuesta))


# =====================================================
# INFORMACIÓN DE CONEXIÓN
# =====================================================

st.write("")

with st.container(border=True):

    st.subheader("📡 Información de conexión")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.caption("BROKER")
        st.code(BROKER, language=None)

    with info2:
        st.caption("PUERTO")
        st.code(str(PORT), language=None)

    with info3:
        st.caption("TEMAS")
        st.code("saito1 · saito2", language=None)

    if st.session_state.ultimo_mensaje:
        st.divider()
        st.caption("Último mensaje publicado")
        st.write(st.session_state.ultimo_mensaje)


# =====================================================
# PIE DE PÁGINA
# =====================================================

st.markdown("""
<div class="footer">
    INTERFACES MULTIMODALES<br>
    MQTT CONTROL · COMUNICACIÓN EN TIEMPO REAL<br>
    Control digital y analógico desde una sola interfaz.
</div>
""", unsafe_allow_html=True)
