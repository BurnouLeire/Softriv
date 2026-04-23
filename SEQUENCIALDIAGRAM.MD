sequenceDiagram
    participant C as Cliente
    participant V as Comercial
    participant P as Planificación
    participant M as Metrología
    participant T as Técnico
    participant Q as Calidad
    participant E as Certificación
    participant F as Facturación

    C->>V: Solicita servicio
    V->>V: Crea cotización
    V->>C: Envía cotización
    C->>V: Aprueba y envía OC
    V->>P: Solicita crear OT
    
    P->>P: Crea OT
    P->>M: Solicita reserva de patrones
    M-->>P: Confirma disponibilidad
    P->>T: Asigna OT
    P->>C: Confirma fecha visita
    
    M->>M: Prepara instrumentos
    M->>T: Entrega instrumentos
    
    T->>C: Confirma llegada
    T->>T: Ejecuta calibración
    T->>Q: Envía datos de campo
    T->>C: Obtiene firma conformidad
    T->>M: Retorna instrumentos
    
    Q->>Q: Revisa y calcula
    Q->>E: Aprueba para certificación
    
    E->>E: Genera certificado
    E->>C: Envía certificado oficial
    
    Q->>F: Notifica OT completada
    F->>F: Genera factura
    F->>C: Envía factura
    C->>F: Realiza pago
    F->>F: Cierra OT