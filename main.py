import streamlit as st
# Debe ser lo primero que se ejecute
st.set_page_config(page_title="Analizador de Feedback según Daniel Bilbao", layout="wide")

from groq import Groq
import plotly.graph_objects as go
import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

# Configurar NLTK para usar la carpeta local
nltk.data.path.append('./nltk_data')

# Inicialización de NLTK
def initialize_nltk():
    try:
        nltk.data.find('tokenizers/punkt/english.pickle')
        nltk.data.find('sentiment/vader_lexicon/vader_lexicon.txt')
    except LookupError:
        st.error("Error al cargar los recursos de NLTK.")
        st.stop()

# Verificación de API key y recursos
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ No se encontró la API key de Groq en los secrets.")
    st.stop()

# Inicializar NLTK
initialize_nltk()

class AnalizadorFeedback:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.model = "mixtral-8x7b-32768"
        self.sia = SentimentIntensityAnalyzer()

    @st.cache_data
    def analizar_sentimiento_detallado(_self, texto):
        oraciones = sent_tokenize(texto)
        sentimientos_oraciones = []
        
        # Análisis de sentimiento general
        scores_general = _self.sia.polarity_scores(texto)
        
        for oracion in oraciones:
            scores = _self.sia.polarity_scores(oracion)
            sentimientos_oraciones.append({
                'texto': oracion,
                'polaridad': scores['compound'],
                'subjetividad': (scores['pos'] + scores['neg']) / 2
            })
        
        return {
            'sentimiento_general': scores_general['compound'],
            'subjetividad_general': (scores_general['pos'] + scores_general['neg']) / 2,
            'analisis_por_oracion': sentimientos_oraciones
        }

    def crear_grafico_sentimiento(self, analisis_sentimiento):
        # Convertir el rango de -1 a 1 a un rango de 0 a 100
        valor = (analisis_sentimiento['sentimiento_general'] + 1) * 50
        
        fig_sentimiento = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valor,
            title = {'text': "Sentimiento General"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 33], 'color': "lightcoral"},
                    {'range': [33, 66], 'color': "khaki"},
                    {'range': [66, 100], 'color': "lightgreen"}
                ]
            }
        ))
        return fig_sentimiento

    @st.cache_data
    def analizar_feedback(_self, texto_feedback):
        prompt = f"""Analiza este feedback y responde:
        1. Tipo (Feedback desde la bondad, Feedback táctico o Feedback del ego)
        2. Justificación de la clasificación
        3. Análisis emocional del mensaje
        4. Si es feedback del ego o táctico, sugiere cómo transformarlo en feedback desde la bondad

        Feedback: {texto_feedback}
        """
        
        try:
            completion = _self.client.chat.completions.create(
                model=_self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de feedback y comunicación efectiva."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error en el análisis: {str(e)}"

def main():
    st.title("📝 Analizador de Feedback")
    st.write("Basado en la propuesta de Daniel Bilbao de Truora")
    
    feedback_texto = st.text_area(
        "Ingresa el texto del feedback a analizar:",
        height=150
    )
    
    if st.button("Analizar Feedback"):
        if feedback_texto.strip():
            try:
                analizador = AnalizadorFeedback()
                
                # Análisis de sentimiento detallado
                with st.spinner("Analizando sentimiento..."):
                    analisis_sentimiento = analizador.analizar_sentimiento_detallado(feedback_texto)
                
                # Crear dos columnas
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    with st.spinner("Analizando feedback..."):
                        resultado = analizador.analizar_feedback(feedback_texto)
                        st.subheader("Análisis del Feedback")
                        st.write(resultado)
                
                with col2:
                    st.subheader("Análisis de Sentimiento")
                    
                    # Mostrar gráfico de sentimiento
                    fig = analizador.crear_grafico_sentimiento(analisis_sentimiento)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mostrar análisis por oración
                    st.subheader("Análisis por oración")
                    for idx, oracion in enumerate(analisis_sentimiento['analisis_por_oracion'], 1):
                        with st.expander(f"Oración {idx}"):
                            st.write(oracion['texto'])
                            st.progress((oracion['polaridad'] + 1) / 2)
                            st.write(f"Polaridad: {oracion['polaridad']:.2f}")
                            st.write(f"Subjetividad: {oracion['subjetividad']:.2f}")
            except Exception as e:
                st.error(f"Error durante el análisis: {str(e)}")
        else:
            st.warning("Por favor, ingresa un texto para analizar.")

if __name__ == "__main__":
    main()