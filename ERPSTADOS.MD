stateDiagram-v2
    [*] --> Borrador: Comercial crea OT
    
    Borrador --> Planificada: Planificación asigna recursos
    Planificada --> Aprobada: Cliente confirma fecha
    Aprobada --> Despachada: Metrología entrega instrumentos
    
    Despachada --> EnTránsito: Técnico inicia viaje
    EnTránsito --> EnSitio: Técnico llega a ubicación
    EnSitio --> EnProgreso: Inicia calibración
    
    EnProgreso --> PendienteRevisión: Completa mediciones
    PendienteRevisión --> EnProgreso: Calidad solicita re-medición
    PendienteRevisión --> Completada: Calidad aprueba
    
    Completada --> Certificada: Emisión certificado
    Certificada --> Facturada: Facturación emite factura
    Facturada --> Cerrada: Cliente paga
    
    Borrador --> Cancelada: Cliente cancela
    Planificada --> Cancelada: Cliente cancela
    Aprobada --> Cancelada: Fuerza mayor
    
    Cancelada --> [*]
    Cerrada --> [*]