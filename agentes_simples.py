# pip install google-generativeai python-dotenv

"""
CONSTRUCCIÓN DE AGENTES EFECTIVOS CON GEMINI
Basado en: https://www.anthropic.com/engineering/building-effective-agents

PRINCIPIOS CLAVE:
1. Empezar con lo más simple posible
2. Solo agregar complejidad cuando sea necesario
3. Medir el rendimiento antes de hacer más complejo
4. Mantener transparencia en los pasos del agente
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modelo base para uso general
model = genai.GenerativeModel("models/gemini-flash-latest")


# ============================================
# EJEMPLO 1: LLM AUMENTADO (Con herramientas)
# ============================================
# Concepto: El LLM puede usar funciones externas para ampliar sus capacidades


def calculadora(operacion: str) -> dict:
    """
    Herramienta simple que realiza operaciones matemáticas.
    El LLM decide cuándo y cómo usarla.
    """
    resultado = eval(operacion)  # En producción usar ast.literal_eval o similar
    return {"resultado": resultado}


# Crear modelo con acceso a la herramienta
model_con_tools = genai.GenerativeModel(
    "models/gemini-flash-latest", tools=[calculadora]
)

# El chat con enable_automatic_function_calling=True hace que Gemini
# ejecute las funciones automáticamente cuando las necesite
chat = model_con_tools.start_chat(enable_automatic_function_calling=True)

pregunta = (
    "Si tengo 15 manzanas y compro 8 paquetes de 12 manzanas cada uno, ¿cuántas tengo?"
)
response = chat.send_message(pregunta)

# La respuesta final está en el historial después de ejecutar las funciones
print(f"💡 Respuesta: {chat.history[-1].parts[0].text}\n")

time.sleep(2)  # Pausa por límites de API gratuita


# ============================================
# EJEMPLO 2: PROMPT CHAINING (Encadenamiento)
# ============================================
# Concepto: Dividir tareas complejas en pasos secuenciales con validación

print("=" * 60)
print("PROMPT CHAINING: Generar contenido y traducirlo")
print("=" * 60 + "\n")

# PASO 1: Generar contenido en español
print("📝 Paso 1: Generando contenido...")
response_1 = model.generate_content(
    "Escribe 3 párrafos cortos sobre la importancia de reciclar. Hazlo motivador."
)
contenido_espanol = response_1.text
print(f"{contenido_espanol}\n")

# Validación (gate): Verificar que el contenido es adecuado
palabras = len(contenido_espanol.split())
print(f"✓ Verificación: {palabras} palabras generadas")

if palabras < 50:
    print("⚠️ Contenido muy corto, workflow interrumpido\n")
else:
    # PASO 2: Solo continuamos si la validación pasa
    print("\n🌍 Paso 2: Traduciendo al inglés...")
    response_2 = model.generate_content(
        f"Traduce al inglés manteniendo el tono motivador:\n\n{contenido_espanol}"
    )
    print(f"{response_2.text}\n")
    print("✓ Workflow completado: Generar → Validar → Traducir\n")

time.sleep(2)


# ============================================
# EJEMPLO 3: ROUTING (Enrutamiento)
# ============================================
# Concepto: Clasificar la entrada y dirigirla al prompt especializado correcto

print("=" * 60)
print("ROUTING: Clasificación y respuesta especializada")
print("=" * 60 + "\n")


def procesar_consulta_soporte(consulta):
    """Clasifica la consulta y la envía al especialista correcto"""

    print(f"📩 Consulta: '{consulta}'\n")

    # PASO 1: Clasificar automáticamente
    response = model.generate_content(
        f"""Clasifica esta consulta en UNA categoría:
        - TECNICO (errores, bugs, problemas técnicos)
        - FACTURACION (pagos, facturas, cargos)
        - GENERAL (información general)

        Consulta: {consulta}

        Responde SOLO la categoría en mayúsculas."""
    )

    categoria = response.text.strip()
    print(f"🔍 Categoría: {categoria}\n")

    # PASO 2: Crear modelo con prompt especializado según categoría
    prompts = {
        "TECNICO": "Experto en soporte técnico. Da soluciones paso a paso y técnicas.",
        "FACTURACION": "Asistente de facturación. Sé empático y explica claramente.",
        "GENERAL": "Asistente amigable. Responde de forma concisa y útil.",
    }

    instruccion = prompts.get(categoria, prompts["GENERAL"])
    model_especializado = genai.GenerativeModel(
        "models/gemini-flash-latest", system_instruction=instruccion
    )

    # PASO 3: Generar respuesta especializada
    response = model_especializado.generate_content(consulta)

    return categoria, response.text


# Probar con diferentes tipos de consultas
consultas_ejemplo = [
    "Mi app se cierra al subir fotos",
    "¿Por qué me cobraron dos veces?",
    "¿Cuál es el horario de atención?",
]

for consulta in consultas_ejemplo:
    print("-" * 60)
    categoria, respuesta = procesar_consulta_soporte(consulta)
    print(f"💬 Respuesta ({categoria}):\n{respuesta}\n")
    time.sleep(2)

time.sleep(2)


# ============================================
# EJEMPLO 4: PARALLELIZATION (Paralelización)
# ============================================
# Concepto: Obtener múltiples perspectivas en paralelo para mayor confianza

print("=" * 60)
print("PARALLELIZATION: Múltiples perspectivas")
print("=" * 60 + "\n")

codigo_ejemplo = """
def procesar_datos(datos):
    resultado = []
    for item in datos:
        if item > 0:
            resultado.append(item * 2)
    return resultado
"""

print(f"Código a revisar:\n{codigo_ejemplo}\n")

# Crear revisiones desde 3 perspectivas diferentes
perspectivas = [
    ("🔒 Seguridad", "Busca SOLO vulnerabilidades de seguridad. Sé breve."),
    ("⚡ Performance", "Busca SOLO problemas de rendimiento. Sé breve."),
    ("📖 Legibilidad", "Evalúa SOLO legibilidad y mantenibilidad. Sé breve."),
]

for nombre, enfoque in perspectivas:
    print(f"{nombre}:")
    response = model.generate_content(f"{enfoque}\n\nCódigo:\n{codigo_ejemplo}")
    print(f"{response.text}\n")
    time.sleep(2)

print("✓ Revisión completa desde múltiples ángulos\n")
time.sleep(2)


# ============================================
# EJEMPLO 5: EVALUATOR-OPTIMIZER (Evaluador-Optimizador)
# ============================================
# Concepto: Un LLM genera, otro evalúa, y el primero mejora basado en feedback

print("=" * 60)
print("EVALUATOR-OPTIMIZER: Generación iterativa mejorada")
print("=" * 60 + "\n")

tema = "el impacto de las redes sociales en los jóvenes"

# PASO 1: Generar versión inicial
print(f"📝 Generando título sobre '{tema}'...")
response = model.generate_content(
    f"Crea un título atractivo para un artículo sobre {tema}. Solo el título."
)
titulo_v1 = response.text.strip()
print(f"\n✏️ Título v1: {titulo_v1}\n")

# PASO 2: Evaluar la primera versión
print("🔍 Evaluando título...")
response = model.generate_content(
    f"""Evalúa este título de 1-10 considerando:
    - Claridad
    - Atractivo
    - Relevancia

    Título: {titulo_v1}

    Formato: Puntuación (1-10) y una sugerencia breve de mejora."""
)
evaluacion = response.text
print(f"{evaluacion}\n")

# PASO 3: Optimizar basado en la evaluación
print("✨ Optimizando título...")
response = model.generate_content(
    f"""Mejora este título basándote en la evaluación:

    Título original: {titulo_v1}
    Evaluación: {evaluacion}

    Dame solo el título mejorado, nada más."""
)
titulo_v2 = response.text.strip()
print(f"\n✅ Título v2: {titulo_v2}\n")
print("✓ Ciclo completo: Generar → Evaluar → Optimizar\n")

time.sleep(2)


# ============================================
# EJEMPLO 6: AGENTE AUTÓNOMO (Con múltiples herramientas)
# ============================================
# Concepto: El agente decide qué herramientas usar y en qué orden

print("=" * 60)
print("AGENTE AUTÓNOMO: Decisiones independientes")
print("=" * 60 + "\n")


# Definir herramientas que el agente puede usar
def buscar_informacion(tema: str) -> dict:
    """Simula búsqueda en base de conocimientos"""
    datos = {
        "velocidad luz": "299,792 km/s en el vacío",
        "temperatura sol": "5,500°C en la superficie",
        "distancia tierra luna": "384,400 km promedio",
    }
    return {"informacion": datos.get(tema.lower(), "No disponible")}


def calcular(expresion: str) -> dict:
    """Realiza cálculos matemáticos"""
    return {"resultado": eval(expresion)}


def convertir_unidades(valor: float, de: str, a: str) -> dict:
    """Convierte entre unidades comunes"""
    conversiones = {
        ("km", "millas"): valor * 0.621371,
        ("millas", "km"): valor * 1.60934,
        ("celsius", "fahrenheit"): (valor * 9 / 5) + 32,
        ("fahrenheit", "celsius"): (valor - 32) * 5 / 9,
    }
    resultado = conversiones.get((de.lower(), a.lower()))
    return (
        {"resultado": resultado, "unidad": a}
        if resultado
        else {"error": "No soportado"}
    )


# Crear agente con todas las herramientas
model_agente = genai.GenerativeModel(
    "models/gemini-flash-latest",
    tools=[buscar_informacion, calcular, convertir_unidades],
)


def ejecutar_agente(tarea):
    """
    El agente decide autónomamente qué herramientas usar para resolver la tarea.
    Este es el patrón más flexible pero también el más impredecible.
    """
    print(f"🤖 Tarea asignada: {tarea}\n")

    chat = model_agente.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(tarea)

    # Mostrar qué herramientas decidió usar el agente
    print("🔧 Herramientas usadas por el agente:")
    for mensaje in chat.history[-10:]:
        for part in mensaje.parts:
            if hasattr(part, "function_call"):
                nombre = part.function_call.name
                params = (
                    dict(part.function_call.args) if part.function_call.args else {}
                )
                print(f"  • {nombre}{params}")
            if hasattr(part, "function_response"):
                resultado = dict(part.function_response.response)
                print(f"    → {resultado}")

    print(f"\n✅ Resultado final:\n{chat.history[-1].parts[0].text}\n")
    return response


# Tarea compleja que requiere múltiples pasos
tarea = """
¿Cuántas millas recorre la luz en un segundo?

Necesitas:
1. Buscar la velocidad de la luz
2. Convertir de kilómetros a millas
"""

ejecutar_agente(tarea)


# ============================================
# RESUMEN COMPARATIVO
# ============================================

print("=" * 60)
print("CUÁNDO USAR CADA PATRÓN")
print("=" * 60 + "\n")

print(
    """
📊 WORKFLOWS (Predefinidos):
   ✓ Cuándo: Los pasos son conocidos y fijos
   ✓ Ventaja: Predecible, fácil de debugear, transparente
   ✓ Ejemplo: Pipeline de contenido (generar → revisar → publicar)
   ✓ Usa: Prompt Chaining, Routing, Parallelization, Evaluator-Optimizer

🤖 AGENTES (Autónomos):
   ✓ Cuándo: Los pasos dependen del contexto y entrada
   ✓ Ventaja: Flexible, se adapta a situaciones inesperadas
   ✓ Ejemplo: "Investiga X y dame un informe" (decide qué buscar)
   ✓ Desventaja: Menos predecible, más difícil de debugear

💡 REGLA DE ORO:
   Empieza con workflows → Mide resultados → Usa agentes solo si es necesario

   La mayoría de problemas se resuelven mejor con workflows simples.
"""
)


# ============================================
# EJERCICIOS PROPUESTOS
# ============================================

print(
    """
EJERCICIOS PARA PRACTICAR:
==========================

1. ROUTING AVANZADO:
   Crea un clasificador de emails que categorice en:
   - URGENTE (respuesta inmediata)
   - IMPORTANTE (respuesta en 24h)
   - INFORMATIVO (solo leer)
   Y genera respuestas apropiadas según la categoría.

2. EVALUATOR-OPTIMIZER PARA CÓDIGO:
   - LLM 1: Genera código para resolver un problema
   - LLM 2: Evalúa eficiencia y legibilidad (puntaje 1-10)
   - LLM 1: Si puntaje < 8, mejora el código
   - Repite hasta lograr puntaje ≥ 8

3. AGENTE DE INVESTIGACIÓN:
   Dale herramientas para:
   - buscar_informacion(tema)
   - calcular_estadisticas(datos)
   - generar_resumen(info)
   Y pídele que investigue un tema y genere un reporte.

4. COMBINAR PATRONES:
   - Usa ROUTING para clasificar consultas
   - Usa CHAINING para responder en 2 pasos
   - Usa EVALUATOR para verificar calidad
   Es el ejercicio más complejo pero más realista.


RECURSOS:
=========
Documentación Gemini: https://ai.google.dev/gemini-api/docs
Artículo original: https://www.anthropic.com/engineering/building-effective-agents
Ejemplos: https://github.com/google-gemini/cookbook

No olvides crear .env con: GEMINI_API_KEY=tu_clave_aqui

Obtén tu clave en: https://aistudio.google.com/app/apikey
"""
)
