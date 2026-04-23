graph TD
    A[Inicio: Técnico en Sitio] --> B[Crear Visita a Sitio]
    B --> C[Seleccionar Cliente]
    B --> D[Definir Ubicación: LÍNEA DE GLICOLADO]
    B --> E[Seleccionar Tipo de Visita: CAL/VER/MAN]
    
    E --> F{¿Agregar Equipo?}
    F -->|Sí| G[Crear Formulario de Equipo]
    F -->|No| Z[Finalizar]
    
    G --> H[Seleccionar Tipo: PRESSURE/TEMP/FLOW]
    G --> I[Ingresar Datos de Codificación]
    G --> J[Ingresar Datos Variables]
    G --> K[Definir Ubicación Específica]
    
    K --> L{¿Agregar Mediciones?}
    L -->|Sí| M[Agregar Punto de Medición]
    L -->|No| N
    
    M --> O[Ingresar Valor Nominal]
    M --> P[Ingresar Valor Medido]
    M --> Q[Calcular Error]
    
    Q --> R{¿Más puntos?}
    R -->|Sí| M
    R -->|No| N[Agregar Instrumentos Usados]
    
    N --> S[Seleccionar del Inventario]
    S --> T[Definir Rol: Patrón/Simulador]
    T --> U[Verificar Vencimiento]
    
    U --> V{¿Agregar más equipos?}
    V -->|Sí| G
    V -->|No| W[Revisar Datos]
    
    W --> X[Completar Visita]
    X --> Y[Generar Reporte PDF]
    Y --> Z[Fin]