graph TB
    subgraph "CLIENTE"
        C1[Contacta para servicio]
        C2[Aprueba cotización]
        C3[Emite OC]
        C4[Recibe al técnico]
        C5[Firma conformidad]
        C6[Recibe certificado]
        C7[Paga factura]
    end

    subgraph "COMERCIAL"
        V1[Registra solicitud]
        V2[Elabora cotización]
        V3[Envía cotización]
        V4[Recibe OC]
        V5[Notifica a operaciones]
    end

    subgraph "PLANIFICACIÓN"
        P1[Crea Orden de Trabajo]
        P2[Verifica disponibilidad]
        P3[Asigna técnico]
        P4[Planifica ruta]
        P5[Reserva patrones]
        P6[Programa visita]
    end

    subgraph "METROLOGÍA/LAB"
        L1[Verifica calibración de patrones]
        L2[Prepara instrumentos]
        L3[Empaca para despacho]
        L4[Registra salida]
        L5[Recibe devolución]
        L6[Verifica estado]
    end

    subgraph "TÉCNICO CAMPO"
        T1[Recibe OT en app]
        T2[Revisa alcance]
        T3[Viaja a sitio]
        T4[Verifica condiciones]
        T5[Ejecuta calibración]
        T6[Registra datos]
        T7[Genera pre-certificado]
        T8[Obtiene firma cliente]
        T9[Retorna instrumentos]
    end

    subgraph "CALIDAD/REVISIÓN"
        Q1[Recibe datos de campo]
        Q2[Revisa mediciones]
        Q3[Calcula incertidumbre]
        Q4[Valida conformidad]
        Q5[Aprueba/rechaza]
        Q6[Solicita correcciones]
    end

    subgraph "CERTIFICACIÓN"
        E1[Genera certificado oficial]
        E2[Asigna número único]
        E3[Firma digital]
        E4[Envía al cliente]
        E5[Archiva en sistema]
    end

    subgraph "FACTURACIÓN"
        F1[Recibe OT completada]
        F2[Genera factura]
        F3[Envía factura]
        F4[Registra pago]
        F5[Cierra OT]
    end

    C1 --> V1
    V1 --> V2
    V2 --> V3
    V3 --> C2
    C2 --> C3
    C3 --> V4
    V4 --> V5
    
    V5 --> P1
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    
    P6 --> L1
    L1 --> L2
    L2 --> L3
    L3 --> L4
    
    P6 --> T1
    T1 --> T2
    T2 --> T3
    T3 --> C4
    C4 --> T4
    T4 --> T5
    T5 --> T6
    T6 --> T7
    T7 --> T8
    T8 --> C5
    C5 --> T9
    
    T9 --> L5
    L5 --> L6
    
    T6 --> Q1
    Q1 --> Q2
    Q2 --> Q3
    Q3 --> Q4
    Q4 -->|OK| Q5
    Q4 -->|NO OK| Q6
    Q6 --> T5
    
    Q5 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> C6
    E4 --> E5
    
    Q5 --> F1
    F1 --> F2
    F2 --> F3
    F3 --> C7
    C7 --> F4
    F4 --> F5