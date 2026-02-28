# 🗺️ ROADMAP – TFM Agente Pokémon VGC

Este documento describe el plan de trabajo temporal para el desarrollo
de un Trabajo Fin de Máster centrado en el diseño y comparación de
diferentes técnicas de Inteligencia Artificial aplicadas a batallas
Pokémon VGC usando el motor `pokemon-vgc-engine`.

---

## 📌 Objetivo general

Diseñar, implementar y comparar agentes de batalla Pokémon basados en
diferentes paradigmas de IA:

- Heurísticas
- Aprendizaje supervisado
- Algoritmos evolutivos
- Aprendizaje por refuerzo

El objetivo es analizar **rendimiento, coste computacional, estabilidad
y facilidad de implementación** de cada enfoque en un entorno común.

---

## 🗓️ Calendario global

- **Inicio del trabajo**: 8 de febrero de 2026
- **Entrega ideal**: Julio 2026
- **Convocatoria alternativa**: Septiembre 2026

---

## 🧩 FASE 0 – Infraestructura y entorno  
📅 **Febrero 2026 (Semanas 1–3)**

### Objetivos
- Preparar el entorno experimental
- Garantizar reproducibilidad
- Facilitar evaluación automática

### Historias de usuario
- US-0.1 Script de ejecución automática de partidas
- US-0.2 Sistema de logging (estados, acciones, resultados)
- US-0.3 Representación común del estado del combate

### Entregables
- Pipeline de simulación funcional
- Logs exportables
- Documento técnico de diseño del estado

---

## 🧱 FASE 1 – Agente baseline heurístico  
📅 **Febrero 2026 (Semanas 3–4)**

### Objetivos
- Definir una línea base sólida
- Validar el correcto funcionamiento del entorno

### Historias de usuario
- US-1.1 Heurística de daño esperado
- US-1.2 Heurística de ventaja de tipo
- US-1.3 Evaluación frente a agente aleatorio

### Entregables
- Agente heurístico estable
- Métricas iniciales (winrate, duración, HP diferencial)

---

## 🧪 FASE 2 – Framework de evaluación  
📅 **Marzo 2026 (Semana 4)**

### Objetivos
- Comparar agentes sin modificar su implementación
- Definir métricas comunes

### Historias de usuario
- US-2.1 Torneos round-robin automatizados
- US-2.2 Cálculo de métricas estándar

### Entregables
- Script de evaluación reproducible
- Tablas de resultados automáticas

---

## 🎓 FASE 3 – Aprendizaje supervisado  
📅 **Marzo 2026 (Semanas 5–6)**

### Objetivos
- Entrenar un agente por imitación
- Evaluar el valor del aprendizaje supervisado

### Historias de usuario
- US-3.1 Generación del dataset estado → acción
- US-3.2 Entrenamiento del clasificador
- US-3.3 Integración del modelo como agente

### Entregables
- Dataset documentado
- Agente supervisado funcional
- Comparativa frente al baseline

---

## 📊 FASE 4 – Análisis comparativo inicial  
📅 **Abril 2026 (Semana 7)**

### Objetivos
- Consolidar resultados parciales
- Redactar primeras conclusiones

### Historias de usuario
- US-4.1 Comparativa heurístico vs supervisado

### Entregables
- Gráficos y tablas comparativas
- Sección de resultados preliminares del TFM

---

## 🧬 FASE 5 – Agente evolutivo  
📅 **Abril–Mayo 2026 (Semanas 8–9)**

### Objetivos
- Explorar estrategias sin gradientes
- Analizar robustez y convergencia

### Historias de usuario
- US-5.1 Definición del genotipo
- US-5.2 Función fitness
- US-5.3 Evaluación del agente evolutivo

### Entregables
- Agente evolutivo
- Análisis de convergencia
- Comparativa con agentes previos

---

## 🤖 FASE 6 – Aprendizaje por refuerzo  
📅 **Mayo–Junio 2026 (Semanas 10–11)**

### Objetivos
- Entrenar un agente adaptativo
- Analizar estabilidad y coste computacional

### Historias de usuario
- US-6.1 Definición de reward shaping
- US-6.2 Entrenamiento mediante self-play
- US-6.3 Evaluación del agente RL

### Entregables
- Agente RL entrenado
- Curvas de aprendizaje
- Resultados comparativos

---

## 🧾 FASE 7 – Comparativa final y cierre  
📅 **Junio 2026 (Semana 12)**

### Objetivos
- Comparar todos los agentes
- Extraer conclusiones finales

### Historias de usuario
- US-7.1 Torneo final entre todos los agentes
- US-7.2 Discusión, conclusiones y trabajo futuro

### Entregables
- Resultados finales
- Documento completo del TFM
- Conclusiones defendibles

---

## 🛟 Plan de contingencia – Convocatoria de septiembre

En caso de retrasos:

- El trabajo **sin RL** sigue siendo válido:
  - Infraestructura
  - Baseline
  - Supervisado
  - Evolutivo
- Julio–Agosto:
  - Refinar RL
  - Aumentar seeds
  - Análisis estadístico
- Septiembre:
  - Pulido final y entrega

---

## 📝 Notas finales

- La redacción del documento comenzará en marzo y se mantendrá paralela
  al desarrollo.
- Cada fase cerrada corresponde a una sección escrita del TFM.
- Se prioriza reproducibilidad y claridad metodológica sobre rendimiento
  absoluto.
