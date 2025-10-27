# pip install google-generativeai python-dotenv requests

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================

import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-flash-latest')

# ============================================
# EJEMPLO 1: La llamada más simple posible
# ============================================

variable = "fotosintesis"
pregunta = "¿Qué es la fotosíntesis?.  Dame una respuesta concreta y breve."
respuesta = model.generate_content(pregunta)

print(respuesta.text)

# ============================================
# EJEMPLO 2: Usando variables en el prompt
# ============================================

especie = "Jaguar"
region = "Amazonía colombiana"

prompt = f'''
Háblame sobre el {especie} en la {region}.
Incluye:
- Estado de conservación
- Amenazas principales
- Una acción concreta para protegerlo

Responde en máximo 4 líneas.
'''

respuesta = model.generate_content(prompt)
print(f"RESPUESTA DEL LLM:\n{respuesta.text}\n")

# ============================================
# EJEMPLO 3: Procesando respuesta recibida
# ============================================

prompt_lista = '''
Dame 3 consejos para reducir el uso de plástico.
Responde en formato:
1. [consejo]
2. [consejo]
3. [consejo]
'''

respuesta = model.generate_content(prompt_lista)
texto_respuesta = respuesta.text
numero_de_lineas = len(texto_respuesta.split('\n'))
numero_de_caracteres = len(texto_respuesta)

print("ANÁLISIS:")
print(f"   Líneas en la respuesta: {numero_de_lineas}")
print(f"   Caracteres totales: {numero_de_caracteres}")
print(f"   ¿Menciona 'plástico'?: {'Sí' if 'plástico' in texto_respuesta.lower() else 'No'}")

# ============================================
# EJEMPLO 4: Función reutilizable
# ============================================

def consultar_llm(pregunta):
    """Envía una pregunta al LLM y devuelve la respuesta en texto."""
    respuesta = model.generate_content(pregunta)
    return respuesta.text

pregunta1 = "¿Qué causa el cambio climático en una frase?"
print(consultar_llm(pregunta1))

pregunta2 = "Dame un dato curioso sobre las abejas"
print(consultar_llm(pregunta2))

# ============================================
# EJEMPLO 5: Combinando lógica Python + LLM
# ============================================

temperaturas_ciudad = [22, 25, 28, 31, 29, 26, 24]
promedio = sum(temperaturas_ciudad) / len(temperaturas_ciudad)

print(f"Temperaturas de la semana: {temperaturas_ciudad}\n")
print(f"Promedio calculado por Python: {promedio:.1f}°C\n")

if promedio > 26:
    prompt_calor = f"""
    La temperatura promedio esta semana fue {promedio:.1f}°C.
    Enumera 2 consejos breves para cuidar el medio ambiente en días calurosos.
    Responde en texto plano, sin formato especial.
    """

    consejos = consultar_llm(prompt_calor) # Función creada en el ejemplo 4
    print(f"CONSEJOS DEL LLM:\n{consejos}")

# ============================================
# EJEMPLO 6: Creando una "herramienta"
# ============================================

def obtener_clima(ciudad):
    """Obtiene el clima de una ciudad usando la API de wttr.in."""
    try:
        # La URL usa un formato especial para obtener la respuesta en JSON (j1)
        url = f"https://wttr.in/{ciudad}?format=j1"
        data = requests.get(url).json()

        # Extraemos los datos que nos interesan
        c = data['current_condition'][0]

        return {
            "ciudad": data['nearest_area'][0]['areaName'][0]['value'],
            "temperatura": c['temp_C'],
            "sensacion": c['FeelsLikeC'],
            "descripcion": c['weatherDesc'][0]['value'],
            "humedad": c['humidity'],
            "viento": c['windspeedKmph'],
            "precipitacion": c['precipMM']
        }
    except requests.exceptions.RequestException as e:
        print(f"Error de red al obtener el clima: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error al procesar los datos del clima. La ciudad '{ciudad}' podría no ser válida. Error: {e}")
        return None

# Pedimos al usuario una ciudad, con "Bogota" como valor por defecto
ciudad_input = input("Ingresa una ciudad (o presiona Enter para usar 'Bogota'): ")
ciudad = ciudad_input or "Bogota"

clima = obtener_clima(ciudad)

# Si obtuvimos el clima correctamente, lo mostramos y consultamos al LLM
if clima:
    print(f"\n📍 {clima['ciudad']}")
    print(f"🌡️ {clima['temperatura']}°C (sensación: {clima['sensacion']}°C)")
    print(f"☁️ {clima['descripcion']}")
    print(f"💧 Humedad: {clima['humedad']}%")
    print(f"💨 Viento: {clima['viento']} km/h")
    print(f"🌧️ Precipitación: {clima['precipitacion']} mm \n")

    prompt_consejos = f'''
    Basado en el siguiente clima para {clima['ciudad']}:
    - Temperatura: {clima['temperatura']}°C
    - Descripción: {clima['descripcion']}
    - Humedad: {clima['humedad']}%
    - Precipitación: {clima['precipitacion']} mm

    Enumera 3 consejos prácticos sobre qué ropa usar o qué actividades hacer hoy.
    Responde en texto plano, sin formato especial.
    '''

    print("🤖 CONSEJOS DEL LLM:")
    print(consultar_llm(prompt_consejos))


"""
# ============================================
# EJERCICIOS
# ============================================

EJERCICIO 1: Mi Asistente Personal
Crea un programa que le pregunte al usuario su nombre y su hobby favorito, luego usa el LLM para generar 3 recomendaciones personalizadas.

# ============================================

EJERCICIO 2: Contador de Palabras Inteligente
El LLM te dará una frase sobre animales. Tu programa debe:
1. Pedirle una frase al LLM
2. Contar cuántas palabras tiene
3. Mostrar si la palabra "animal" aparece en la frase

# Pista: usa .split() para separar palabras
prompt = "Dame una frase corta sobre animales domésticos"
respuesta = consultar_llm(prompt)

# TU CÓDIGO AQUÍ:
# - Cuenta las palabras
# - Verifica si dice "animal"
# - Imprime los resultados


# ============================================

EJERCICIO 3: Clasificador de Números
Crea un programa que:

1. El usuario ingrese un número
2. Python determine si es par o impar
3. El LLM dé un dato curioso sobre ese tipo de número

numero = int(input("Ingresa un número: "))

# Python decide:
if numero % 2 == 0:
    tipo = "par"
else:
    tipo = "impar"

# Ahora consulta al LLM:
prompt = f"Dame un dato curioso sobre los números {tipo}. Máximo 2 líneas."
# Completa...

# ============================================

EJERCICIO 4: Traductor con Validación
Pide al usuario una palabra en español, tradúcela al inglés usando el LLM, y verifica que la respuesta tenga menos de 20 caracteres (para asegurar que es una sola palabra).

palabra = input("Palabra en español: ")

# Crear el prompt para traducir
# Obtener respuesta
# Verificar longitud
# Mostrar resultado o error

# ============================================

🏠 TAREA PARA LA CASA
📊 ANALIZADOR DE HÁBITOS SALUDABLES
Crea un programa completo que:
PARTE 1: Recolección de datos (Python)

Pregunta al usuario cuántos vasos de agua tomó hoy
Pregunta cuántas horas durmió
Pregunta si hizo ejercicio (sí/no)

PARTE 2: Análisis (Python)

Calcula si cumple con las recomendaciones:

Agua: mínimo 6 vasos
Sueño: entre 7-9 horas
Ejercicio: sí


Guarda en variables si cada hábito es "bueno" o "mejorable"

PARTE 3: Consulta al LLM

Envía la información al LLM
Pide que genere 2 consejos personalizados basados en lo que falta mejorar

PARTE 4: Reporte final

Muestra un resumen con:

Los datos ingresados
El análisis de Python
Los consejos del LLM
Un emoji según el resultado (😊 si todo está bien, 🤔 si hay que mejorar)


# ESTRUCTURA SUGERIDA:


# 1. Recolectar datos
vasos_agua = int(input("¿Cuántos vasos de agua tomaste? "))
# ... más inputs

# 2. Analizar con Python
agua_ok = vasos_agua >= 6
# ... más análisis

# 3. Crear prompt inteligente
prompt = f´´´
Hoy una persona:
- Tomó {vasos_agua} vasos de agua (recomendado: 6+)
- Durmió ... horas (recomendado: 7-9)
...
Dame 2 consejos específicos para mejorar.
´´´

# 4. Mostrar reporte completo

"""
