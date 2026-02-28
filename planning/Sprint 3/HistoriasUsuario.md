## ÉPICA 3 – Aprendizaje supervisado

Objetivo: imitar decisiones existentes.

### US-3.1 – Generación de dataset
**Como** investigador  
**Quiero** generar un dataset estado → acción  
**Para** entrenar un modelo supervisado  

**Criterios de aceptación**
- [ ] Dataset balanceado
- [ ] Estados vectorizados
- [ ] Acciones correctamente codificadas

---

### US-3.2 – Entrenamiento de clasificador
**Como** investigador  
**Quiero** entrenar un modelo supervisado  
**Para** predecir acciones  

**Criterios de aceptación**
- [ ] Accuracy superior a random
- [ ] Validación cruzada
- [ ] Modelo serializado

---

### US-3.3 – Agente supervisado integrado
**Como** sistema  
**Quiero** usar el modelo entrenado como agente  
**Para** competir en el engine  

**Criterios de aceptación**
- [ ] Inferencia en tiempo real
- [ ] No genera acciones inválidas

---