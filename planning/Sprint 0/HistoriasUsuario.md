## ÉPICA 0 – Infraestructura y entorno

Objetivo: poder experimentar sin fricción y con resultados reproducibles.

### US-0.1 – Ejecutar partidas automáticamente
**Como** investigador  
**Quiero** poder lanzar múltiples partidas desde un script  
**Para** evaluar agentes de forma sistemática  

**Criterios de aceptación**
- [x] Lanzar N partidas sin interacción manual
- [x] Selección de agentes por configuración
- [x] Las partidas terminan sin errores

---

### US-0.2 – Logging del estado y acciones
**Como** investigador  
**Quiero** registrar estados, acciones y resultados  
**Para** generar datasets y analizar decisiones  

**Criterios de aceptación**
- [x] Cada turno guarda estado serializado
- [x] Cada turno guarda la acción elegida
- [x] Cada partida guarda ganador y duración
- [x] Logs exportables (JSON / CSV)

---

### US-0.3 – Representación común del estado
**Como** investigador  
**Quiero** una representación vectorial estándar del estado  
**Para** reutilizarla en todos los agentes  

**Criterios de aceptación**
- [x] Incluye HP, tipos, boosts y estado de campo
- [x] Convertible a vector numérico
- [ ] Documentación clara de features
