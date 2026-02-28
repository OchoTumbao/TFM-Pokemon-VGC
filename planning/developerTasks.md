# 🛠️ DEVELOPER_TASKS.md

Lista de tareas técnicas y decisiones de bajo nivel
para el desarrollo del TFM: Agente Pokémon VGC.

Este documento sirve como referencia operativa diaria
durante la implementación.

---

## 📦 Setup inicial del proyecto

- [x] Clonar y ejecutar `pokemon-vgc-engine`
- [x] Entender flujo de una partida (init → turnos → fin)
- [x] Identificar puntos de extensión para agentes
- [x] Definir estructura del proyecto (`agents/`, `eval/`, `utils/`)
- [x] Configurar entorno virtual / dependencias
- [x] Fijar versión de Python y librerías

---

## 🧠 Representación del estado

- [x] Decidir granularidad del estado (completo vs reducido)
- [x] Identificar variables observables:
  - HP propios y rivales
  - tipos
  - boosts
  - estados alterados
  - clima / terreno
- [x] Codificar variables categóricas
- [x] Normalizar valores numéricos
- [ ] Documentar features del estado
- [x] Implementar función `state_to_vector()`

---

## 🧾 Logging y datasets

- [x] Definir formato de log (JSON / CSV)
- [x] Guardar estado por turno
- [x] Guardar acción seleccionada
- [x] Guardar resultado final
- [ ] Incluir seed de la partida
- [ ] Implementar compresión / batching de logs
- [ ] Script de limpieza y validación de logs

---

## ⚙️ Infraestructura de simulación

- [ ] Script para ejecutar N partidas consecutivas
- [ ] Parámetros configurables por archivo (YAML / JSON)
- [ ] Control de seeds aleatorias
- [ ] Manejo de excepciones (partidas corruptas)
- [ ] Paralelización ligera (opcional)

---

## 🧱 Agente heurístico

- [ ] Implementar cálculo de daño esperado
- [ ] Implementar evaluación de ventaja de tipo
- [ ] Implementar lógica de cambio / protección
- [ ] Resolver empates entre acciones
- [ ] Asegurar decisiones válidas
- [ ] Añadir logs de decisiones (debug)

---

## 🧪 Framework de evaluación

- [ ] Implementar round-robin de agentes
- [ ] Controlar número de partidas por enfrentamiento
- [ ] Calcular winrate por pareja
- [ ] Calcular HP diferencial medio
- [ ] Calcular duración media de partida
- [ ] Medir tiempo medio por turno
- [ ] Exportar resultados a CSV
- [ ] Script para reproducir resultados exactos

---

## 🎓 Aprendizaje supervisado

- [ ] Generar dataset desde logs
- [ ] Balancear acciones (si necesario)
- [ ] Seleccionar modelo base (MLP / RF / XGBoost)
- [ ] Entrenar modelo
- [ ] Validar con cross-validation
- [ ] Guardar modelo entrenado
- [ ] Implementar agente wrapper del modelo
- [ ] Controlar latencia de inferencia

---

## 🧬 Algoritmos evolutivos

- [ ] Definir genotipo (pesos / reglas / red pequeña)
- [ ] Mapear genotipo → política
- [ ] Definir población inicial
- [ ] Implementar selección
- [ ] Implementar cruce
- [ ] Implementar mutación
- [ ] Diseñar función fitness
- [ ] Ejecutar evolución durante N generaciones
- [ ] Guardar mejores individuos
- [ ] Analizar convergencia

---

## 🤖 Aprendizaje por refuerzo

- [ ] Definir espacio de acciones reducido
- [ ] Definir espacio de estados (usar vector común)
- [ ] Diseñar reward shaping inicial
- [ ] Implementar entorno RL (wrapper)
- [ ] Integrar algoritmo (PPO / A2C)
- [ ] Entrenar con self-play
- [ ] Guardar checkpoints
- [ ] Monitorizar curvas de aprendizaje
- [ ] Detectar exploits del reward
- [ ] Evaluar estabilidad del entrenamiento

---

## 📊 Análisis y visualización

- [ ] Scripts de generación de gráficos
- [ ] Curvas de aprendizaje
- [ ] Comparativas de winrate
- [ ] Boxplots de HP diferencial
- [ ] Análisis de varianza (si aplica)
- [ ] Guardar figuras en formato publicable

---

## 🧾 Reproducibilidad y calidad

- [ ] Fijar seeds globales
- [ ] Versionar configuraciones
- [ ] Documentar hiperparámetros
- [ ] Guardar versiones finales de agentes
- [ ] Script de reproducción completa del experimento
- [ ] README con instrucciones claras

---

## 📝 Redacción del TFM

- [ ] Describir entorno y reglas del juego
- [ ] Justificar elección de técnicas
- [ ] Explicar representación del estado
- [ ] Detallar métricas
- [ ] Presentar resultados
- [ ] Discusión crítica
- [ ] Limitaciones
- [ ] Trabajo futuro

---

## 🚨 Riesgos técnicos a vigilar

- [ ] Exploits en reward shaping
- [ ] Overfitting al agente baseline
- [ ] Dataset sesgado
- [ ] Entrenamiento RL inestable
- [ ] Tiempo de cómputo excesivo
- [ ] Resultados no reproducibles

---

## 📌 Notas personales

(Espacio para decisiones técnicas, ideas, problemas encontrados)