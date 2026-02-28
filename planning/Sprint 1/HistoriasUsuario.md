## ÉPICA 1 – Agente baseline heurístico

Objetivo: establecer una línea base sólida.

### US-1.1 – Heurística de daño esperado
**Como** agente  
**Quiero** elegir el movimiento con mayor daño esperado  
**Para** maximizar impacto inmediato  

**Criterios de aceptación**
- [ ] Cálculo de daño estimado
- [ ] Selección consistente del mejor movimiento
- [ ] No produce acciones inválidas

---

### US-1.2 – Heurística de ventaja de tipo
**Como** agente  
**Quiero** evitar enfrentamientos desfavorables  
**Para** aumentar supervivencia  

**Criterios de aceptación**
- [ ] Detecta desventaja clara de tipo
- [ ] Decide cambiar cuando corresponde
- [ ] No entra en bucles infinitos

---

### US-1.3 – Evaluación del agente baseline
**Como** investigador  
**Quiero** evaluar el baseline contra un agente random  
**Para** validar su funcionamiento  

**Criterios de aceptación**
- [ ] Winrate significativamente > 50%
- [ ] Métricas guardadas automáticamente

---
