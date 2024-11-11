import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="Clasificador de Feedback",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.markdown("""
    <style>
    /* Estilos existentes de los botones */
    button {
        background-color: #0F2C4C !important;
        color: white !important;
    }
    button:hover {
        background-color: #00E6C3 !important;
        color: #0F2C4C !important;
    }

    /* Nuevos estilos para el layout */
    .main > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
        max-width: 100%;
    }
    
    .stButton>button {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    .stTextArea>div>div>textarea {
        min-height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    button {
        background-color: #0F2C4C !important;
        color: white !important;
    }
    button:hover {
        background-color: #00E6C3 !important;
        color: #0F2C4C !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style="background: linear-gradient(90deg, #0F2C4C 0%, #00E6C3 100%); 
                padding: 100px; 
                border-radius: 5px; 
                margin-bottom: 20px;
                display: flex;
                justify-content: center;
                align-items: center;">
    </div>
    """, unsafe_allow_html=True)
# Intenta cargar .env si existe (desarrollo local)
load_dotenv()

# Obtiene la API key de variables de entorno (funciona tanto en local como en producción)
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

def analizar_y_sugerir(texto):
    # Prompt que explica las categorías y solicita el análisis
    prompt = f"""Analiza el siguiente feedback y clasifícalo en una de estas categorías:
    1. Desde el ego: Feedback que se centra en el emisor, a menudo para mostrar superioridad o control.
    2. Táctica: Feedback que se enfoca en acciones específicas y cómo mejorarlas.
    3. Desde la bondad: Feedback que se da con empatía y consideración, buscando el bienestar del receptor.

    Además, identifica los sentimientos presentes en el texto y sugiere cómo podría mejorarse para que sea más claro y constructivo.

    Texto a analizar: {texto}

    Por favor, proporciona tu análisis en el siguiente formato:
    Categoría:
    Sentimientos:
    Sugerencias de mejora:
    """

    try:
        # Llamada a la API de Groq
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="mixtral-8x7b-32768",  # o el modelo que prefieras usar
            temperature=0.7,
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error al analizar el texto: {str(e)}"

# Inicializar estados
if 'feedback_text' not in st.session_state:
    st.session_state.feedback_text = ""
if 'resultado_analisis' not in st.session_state:
    st.session_state.resultado_analisis = None

# Interfaz de usuario con Streamlit
st.title("Clasificador de Feedback")
st.write("Clasifica el feedback en categorías y sugiere mejoras.")

# Agregar sección informativa sobre tipos de feedback
with st.expander("ℹ️ Información sobre tipos de feedback"):
    st.markdown("""
    <div style="border-left: 4px solid #00E6C3; padding-left: 20px; margin: 20px 0;">
    <h3 style="color: #0F2C4C;">Tipos de Feedback y Ejemplos en Empresas Tech</h3>
    
    <div style="background-color: rgba(15, 44, 76, 0.05); padding: 15px; border-radius: 5px;">
    <em>Esta clasificación está basada en la propuesta de Daniel Bilbao, CEO de Truora, 
    empresa líder latinoamericana en soluciones de verificación de identidad y prevención 
    de fraude para empresas digitales.</em>
    </div>
    
    <h4 style="color: #0F2C4C;">1. Feedback desde el Ego</h4>
    <strong>Definición:</strong> Comentarios que reflejan más sobre quien los emite que sobre el trabajo evaluado, 
    frecuentemente buscando demostrar autoridad o superioridad.
    
    <div style="border-left: 3px solid #00E6C3; padding-left: 10px; margin: 10px 0;">
    <em>"Como líder técnico con 15 años de experiencia, puedo decirte que tu código está 
    completamente desordenado. Yo lo habría hecho de una manera totalmente diferente."</em>
    </div>
    
    <h4 style="color: #0F2C4C;">2. Feedback Táctico</h4>
    <strong>Definición:</strong> Observaciones específicas y accionables enfocadas en comportamientos o resultados concretos, 
    proporcionando dirección clara para mejoras.
    
    <div style="border-left: 3px solid #00E6C3; padding-left: 10px; margin: 10px 0;">
    <em>"En el último sprint, noté que la documentación de las APIs que desarrollaste carece de 
    ejemplos de uso. Sugiero agregar casos de uso comunes y respuestas esperadas para facilitar la 
    integración del equipo frontend."</em>
    </div>
    
    <h4 style="color: #0F2C4C;">3. Feedback desde la Bondad</h4>
    <strong>Definición:</strong> Retroalimentación constructiva entregada con empatía y enfoque en el crecimiento, 
    considerando el contexto y las circunstancias del receptor.
    
    <div style="border-left: 3px solid #00E6C3; padding-left: 10px; margin: 10px 0;">
    <em>"Aprecio el esfuerzo que has puesto en el desarrollo del nuevo feature. He notado que 
    tienes un buen manejo de la lógica de negocio. Para potenciar aún más tu trabajo, ¿te gustaría que 
    revisemos juntos algunas prácticas de clean code que podrían hacer tu código más mantenible?"</em>
    </div>

    <hr style="border: 1px solid rgba(15, 44, 76, 0.1); margin: 20px 0;">
    
    <div style="background-color: rgba(0, 230, 195, 0.1); padding: 15px; border-radius: 5px;">
    <em>Truora es una compañía tecnológica que proporciona servicios de verificación de identidad, 
    prevención de fraude y onboarding digital para empresas en Latinoamérica. Sus soluciones 
    permiten a las empresas validar la identidad de sus usuarios, realizar verificaciones de 
    antecedentes y automatizar procesos de contratación de manera segura y eficiente.</em>
    </div>
    </div>
    """, unsafe_allow_html=True)

# Entrada de texto con placeholder que sugiere la longitud
texto_feedback = st.text_area(
    "Escribe el feedback que quieres analizar aquí:",
    value=st.session_state.feedback_text,
    key="texto_area",
    height=150,
    placeholder="Ingresa tu feedback aquí (se sugiere entre 50 y 500 palabras para un mejor análisis)",
    help="Para un análisis óptimo, se recomienda un texto de entre 50 y 500 palabras"
)

# Contar palabras
num_palabras = len(texto_feedback.split()) if texto_feedback else 0
st.caption(f"Número de palabras: {num_palabras}")

# Crear dos columnas para los botones
col1, col2 = st.columns(2)

# Botones de analizar y limpiar lado a lado
with col1:
    if st.button("📝 Analizar Feedback", key="analizar"):
        if texto_feedback:
            st.session_state.feedback_text = texto_feedback
            with st.spinner('Analizando el feedback...'):
                resultado = analizar_y_sugerir(texto_feedback)
                st.session_state.resultado_analisis = resultado
        else:
            st.warning("Por favor, ingresa un texto de feedback.")

with col2:
    if st.button("↺ Nueva consulta",
                 key="nueva_consulta", 
                 help="Haz clic dos veces para limpiar el texto y comenzar una nueva consulta",  # Tooltip explicativo
                 type="secondary"):  # Estilo secundario para diferenciarlo
        # Clear the session state for feedback text and analysis result
        st.session_state.feedback_text = ""  # Clear the text input
        st.session_state.resultado_analisis = None  # Clear the result
        # Since the session state has changed, this will update the text area value immediately

# Mostrar resultados
if st.session_state.resultado_analisis:
    st.markdown("### Resultado del Análisis")
    st.write(st.session_state.resultado_analisis)

st.markdown("""
    <div style="background: linear-gradient(270deg, #0F2C4C 0%, #00E6C3 100%); 
                padding: 30px; 
                border-radius: 5px; 
                margin-top: 20px;
                display: flex;
                justify-content: center;
                align-items: center;">
        <div style='text-align: center; color: white; font-size: 0.8em;'>
            🛸 Desarrollado con Cursor AI, Streamlit y Groq API - Kelyn Botina Trujillo 👨‍🚀
        </div>
    </div>
    """, unsafe_allow_html=True)