--Farid Zúñiga 

USE master;                               -- Cambia el contexto a la base de datos 'master'
GO

IF DB_ID(N'Crm') IS NOT NULL              -- Si ya existe una BD llamada 'Crm'...
BEGIN
    ALTER DATABASE Crm 
        SET SINGLE_USER WITH ROLLBACK IMMEDIATE;  -- La pone en modo de un solo usuario y revierte conexiones
    DROP DATABASE Crm;                    -- Elimina la base de datos 'Crm'
END
GO

/* Crear la base de datos Crm desde cero */
CREATE DATABASE Crm
CONTAINMENT = NONE                        -- Contención clásica (sin características de contained DB)
ON PRIMARY
(
        NAME = 'crm.mdf',                 -- Nombre lógico del archivo de datos
        FILENAME = 'C:\DATABASES\Crm.mdf',-- Ruta física donde se guardará el archivo .mdf
        SIZE = 10 MB,                     -- Tamaño inicial del archivo de datos
        MAXSIZE = 50 MB,                  -- Tamaño máximo permitido del archivo de datos
        FILEGROWTH = 5 MB                 -- Crecimiento del archivo cuando se llena
)
LOG ON
(
        NAME = 'crm.ldf',                 -- Nombre lógico del archivo de log
        FILENAME = 'C:\DATABASES\Crm.ldf',-- Ruta física del archivo de log
        SIZE = 5 MB,                      -- Tamaño inicial del log
        MAXSIZE = 25 MB,                  -- Tamaño máximo del log
        FILEGROWTH = 5 MB                 -- Crecimiento del archivo de log
)
COLLATE Modern_Spanish_CI_AS;             -- Intercalación en español moderno, case insensitive, accent sensitive
GO

USE Crm                                   -- Cambia el contexto a la nueva base de datos Crm
GO 

DROP TABLE IF EXISTS Rol                  -- Elimina la tabla Rol si ya existe
GO

CREATE TABLE Rol
(
    rol_id BIGINT IDENTITY(1,1)  NOT NULL,    -- PK numérica autoincremental para el rol
    nombreRol NVARCHAR(30) NOT NULL,          -- Nombre del rol (Administrador, Vendedor, etc.)
    descripcionRol NVARCHAR(200) NULL,        -- Descripción más detallada del rol
    estadoRol BIT DEFAULT 1 NOT NULL,         -- Estado del rol: 1 = activo, 0 = inactivo
    fechaAsignacion DATETIME2 NULL,           -- Fecha en que se asigna/crea el rol

    CONSTRAINT PK_Rol PRIMARY KEY (rol_id)    -- Clave primaria de la tabla Rol
);
GO
--------------------------------------------------------------------------------
DROP TABLE IF EXISTS Usuario              -- Elimina la tabla Usuario si existe
GO

CREATE TABLE Usuario
(
    usuario_id BIGINT IDENTITY(1,1) NOT NULL,  -- PK autoincremental del usuario
    username NVARCHAR(10) NOT NULL,           -- Nombre de usuario para login
    hashPassword VARBINARY(256) NOT NULL,     -- Hash de la contraseña, jamás texto plano
    nombreUsuario NVARCHAR(50) NOT NULL,      -- Nombre real del usuario
    apellidosUsuario NVARCHAR(50) NULL,       -- Apellidos del usuario
    emailUsuario NVARCHAR(50) NOT NULL,       -- Correo electrónico de contacto/login
    telefonoUsuario NVARCHAR(15) NULL,        -- Teléfono de contacto
    estadoUsuario BIT DEFAULT 1 NOT NULL,     -- Estado del usuario: 1 = activo, 0 = inactivo
    ultimoAcceso DATETIME2 NULL,              -- Última fecha y hora de acceso al sistema
    rol_id BIGINT NULL,                       -- FK al rol que tiene asignado (N:1 con Rol)

    CONSTRAINT PK_Usuario PRIMARY KEY (usuario_id),              -- PK de Usuario
    CONSTRAINT FK_Usuario_Rol FOREIGN KEY (rol_id) REFERENCES Rol (rol_id) -- Enlace al rol
);
GO
-----------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Empresa              -- Elimina Empresa si ya existe
GO

CREATE TABLE Empresa
(
    empresa_id BIGINT IDENTITY(1,1)  NOT NULL,   -- PK autoincremental de Empresa
    nombreEmpresa NVARCHAR(100) NOT NULL,        -- Nombre de la empresa cliente
    direccionEmpresa NVARCHAR(180) NULL,         -- Dirección física
    telefonoEmpresa NVARCHAR(15) NULL,           -- Teléfono de la empresa
    emailEmpresa NVARCHAR(50) NULL,              -- Correo de la empresa
    estadoEmpresa NVARCHAR(10) NOT NULL DEFAULT 'Activo', -- Estado (Activo/Inactivo)
    fechaRegistro DATETIME2 NOT NULL DEFAULT GETDATE(),   -- Fecha de registro de la empresa

    CONSTRAINT PK_Empresa PRIMARY KEY (empresa_id)        -- PK de Empresa
);
GO
------------------------------------------------------------------------------

DROP TABLE IF EXISTS Cuenta               -- Elimina Cuenta si existe
GO

-- Tabla Cuenta: entidad principal de cliente en el CRM
CREATE TABLE Cuenta
(
    cuenta_id BIGINT IDENTITY(1,1) NOT NULL, -- PK de Cuenta, ID autonumérico
    nombre NVARCHAR(30) NOT NULL,            -- Nombre de la Cuenta (cliente, empresa o persona)
    telefono NVARCHAR(15) NULL,              -- Teléfono de la cuenta
    email NVARCHAR(50) NULL,                 -- Correo de la cuenta
    estado NVARCHAR(10) NOT NULL DEFAULT 'Activo', -- Estado de la cuenta
    fechaCreado DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha de creación de la cuenta
    empresa_id BIGINT NULL,                  -- FK opcional a Empresa (N:1)

    CONSTRAINT PK_Cuenta PRIMARY KEY (cuenta_id),     -- PK de Cuenta
    CONSTRAINT FK_Empresa_Cuenta FOREIGN KEY (empresa_id) REFERENCES Empresa(empresa_id) -- Enlace a Empresa
);
GO

-----------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Lead                 -- Elimina Lead si existe
GO

CREATE TABLE Lead
(
    lead_id BIGINT IDENTITY(1,1) NOT NULL,   -- PK del lead, autonumérico
    origen NVARCHAR(40) NOT NULL,            -- Origen del lead ('WebForm','Llamada','Referencia', etc.)
    nombreLead NVARCHAR(100) NOT NULL,       -- Nombre de la persona/empresa interesada
    emailLead NVARCHAR(50) NULL,             -- Correo del lead
    interes NVARCHAR(120) NULL,              -- Descripción del interés (producto, servicio, etc.)
    estadoLead NVARCHAR(20) NOT NULL DEFAULT 'Abierto', -- Estado del lead
    fechaCreadoLead DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha de creación del registro del lead

    CONSTRAINT PK_Lead PRIMARY KEY (lead_id)  -- PK de Lead
);
GO
--------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Oportunidad          -- Elimina Oportunidad si existe
GO

CREATE TABLE Oportunidad
(
    oportunidad_id BIGINT IDENTITY(1,1) NOT NULL, -- PK de Oportunidad
    nombreOp NVARCHAR(100) NOT NULL,              -- Nombre/título de la oportunidad
    probabilidad DECIMAL(5,2) NOT NULL DEFAULT 0, -- Probabilidad de cierre (0–100)
    monto DECIMAL(18,2) NULL,                     -- Monto potencial de la venta
    etapa NVARCHAR(30) NOT NULL DEFAULT 'Prospección', -- Etapa del pipeline de ventas
    fechaCreacionOp DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha creación oportunidad

    cuenta_id BIGINT,                             -- FK a Cuenta (cliente asociado)
    lead_id BIGINT NULL,                          -- FK opcional al Lead original

    CONSTRAINT PK_Oportunidad PRIMARY KEY (oportunidad_id),     -- PK de Oportunidad
    CONSTRAINT UQ_Oportunidad_Lead UNIQUE (lead_id),            -- Un lead solo puede tener 1 oportunidad (1:1 lógico)
    CONSTRAINT FK_Oportunidad_Lead FOREIGN KEY (lead_id) REFERENCES Lead(lead_id), -- FK a Lead
    CONSTRAINT FK_Oportunidad_Cuenta FOREIGN KEY (cuenta_id) REFERENCES Cuenta(cuenta_id) -- FK a Cuenta
);
GO
---------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Contacto             -- Elimina Contacto si existe
GO

CREATE TABLE Contacto
(
    contacto_id BIGINT IDENTITY(1,1) NOT NULL,  -- PK del contacto
    nombreCliente NVARCHAR(30) NOT NULL,        -- Nombre del contacto (persona)
    apellidoCliente NVARCHAR(50) NOT NULL,      -- Apellido del contacto
    telefonoCliente NVARCHAR(15) NULL,          -- Teléfono del contacto
    emailCliente NVARCHAR(50) NOT NULL,         -- Correo del contacto
    estadoCliente BIT DEFAULT 1 NOT NULL,       -- Estado del contacto: 1 = activo
    fechaCreadoCliente DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha creación contacto

    lead_id BIGINT,                             -- FK al Lead del cual viene este contacto (N:1)
    cuenta_id BIGINT NULL,                      -- FK a Cuenta asociada (N:1)

    CONSTRAINT PK_Contacto PRIMARY KEY (contacto_id),         -- PK de Contacto
    CONSTRAINT FK_Contacto_Cuenta FOREIGN KEY (cuenta_id) REFERENCES Cuenta(cuenta_id), -- Enlace a Cuenta
    CONSTRAINT FK_Contacto_Lead FOREIGN KEY (lead_id) REFERENCES Lead (lead_id)         -- Enlace a Lead
);
GO

------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS CasoReclamo          -- Elimina CasoReclamo si existe
GO

CREATE TABLE CasoReclamo
(
    caso_id BIGINT IDENTITY(1,1) NOT NULL,      -- PK del caso o reclamo
    canal NVARCHAR(20) NOT NULL,                -- Canal por el que llega ('Presencial','Teléfono','Web', etc.)
    prioridad NVARCHAR(15) NULL,                -- Prioridad ('Baja','Media','Alta','Crítica')
    categoria NVARCHAR(40) NOT NULL,            -- Tipo de caso ('Cobranza','Producto','Entrega','Soporte', etc.)
    estadoCaso NVARCHAR(15) NOT NULL DEFAULT 'Abierto', -- Estado del caso
    resolucion NVARCHAR(MAX) NULL,              -- Texto de cómo se resolvió el caso
    fechaApertura DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha de apertura del caso
    fechaCierre DATETIME2 NULL,                 -- Fecha de cierre del caso
    satisfaccionCliente TINYINT NULL,           -- Nivel de satisfacción (0–10 o 1–5, según definas)

    usuario_id BIGINT NULL,                     -- FK al Usuario que atiende el caso

    CONSTRAINT PK_CasoReclamo PRIMARY KEY (caso_id),        -- PK de CasoReclamo
    CONSTRAINT FK_CasoReclamo_Usuario FOREIGN KEY (usuario_id) REFERENCES Usuario (usuario_id) -- Enlace al usuario
);
GO
-------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Interaccion          -- Elimina Interaccion si existe
GO

CREATE TABLE Interaccion
(
    interaccion_id BIGINT IDENTITY(1,1) NOT NULL, -- PK de Interacción
    tipo NVARCHAR(20) NOT NULL,                  -- Tipo ('Llamada','Email','WhatsApp','Reunión')
    descripcion NVARCHAR(250) NULL,              -- Descripción breve de la interacción
    canalInteraccion NVARCHAR(20) NULL,          -- Canal ('Teléfono','Email','WhatsApp','Presencial','SMS')
    fecha DATETIME2 NOT NULL DEFAULT GETDATE(),  -- Fecha y hora de la interacción

    usuario_id BIGINT NULL,                      -- FK al Usuario que registra la interacción
    contacto_id BIGINT NULL,                     -- FK al Contacto involucrado
    oportunidad_id BIGINT NULL,                  -- FK a la Oportunidad relacionada
    caso_id BIGINT NOT NULL,                     -- FK al Caso/Reclamo asociado

    CONSTRAINT PK_Interaccion PRIMARY KEY (interaccion_id), -- PK de Interaccion

    CONSTRAINT FK_Interaccion_Usuario FOREIGN KEY (usuario_id) REFERENCES Usuario (usuario_id), -- Enlace Usuario
    CONSTRAINT FK_Interaccion_Contacto FOREIGN KEY (contacto_id) REFERENCES Contacto (contacto_id), -- Enlace Contacto
    CONSTRAINT FK_Interaccion_Oportunidad FOREIGN KEY (oportunidad_id) REFERENCES Oportunidad(oportunidad_id), -- Enlace Oportunidad
    CONSTRAINT FK_Interaccion_Caso FOREIGN KEY (caso_id) REFERENCES CasoReclamo(caso_id) -- Enlace Caso
);
GO
-------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Adjunto              -- Elimina Adjunto si existe
GO

CREATE TABLE Adjunto
(
    adjunto_id BIGINT IDENTITY(1,1) NOT NULL,    -- PK del adjunto
    nombreArchivo NVARCHAR(100) NOT NULL,        -- Nombre del archivo (ej: factura.pdf)
    rutaArchivo NVARCHAR(400) NOT NULL,          -- Ruta completa donde se almacena el archivo
    tipoArchivo NVARCHAR(80) NULL,               -- Tipo MIME o descripción (PDF, JPG, etc.)
    fechaCreadoAdj DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha en que se registra el adjunto

    interaccion_id BIGINT NULL,                  -- FK a Interaccion (adjunto a una interacción)
    caso_id BIGINT NULL,                         -- FK a CasoReclamo (adjunto al caso directamente)

    CONSTRAINT PK_Adjunto PRIMARY KEY (adjunto_Id),        -- PK de Adjunto
    CONSTRAINT FK_Adjunto_Interaccion FOREIGN KEY (interaccion_id) REFERENCES Interaccion(interaccion_id), -- Enlace Interaccion
    CONSTRAINT FK_Ajunto_CasoReclamo FOREIGN KEY (caso_id) REFERENCES CasoReclamo(caso_id)                -- Enlace Caso
);
GO

-------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS Segmento             -- Elimina Segmento si existe
GO

CREATE TABLE Segmento
(
    segmento_id BIGINT IDENTITY(1,1) NOT NULL,   -- PK del segmento de marketing
    nombreSeg NVARCHAR(50) NOT NULL,            -- Nombre del segmento (Ej: "Clientes VIP")
    criterio NVARCHAR(MAX) NULL,                -- Descripción de criterios de segmentación
    descripcionSeg NVARCHAR(300) NULL,          -- Descripción adicional del segmento
    estadoSeg NVARCHAR(10) NOT NULL DEFAULT 'Activo', -- Estado del segmento
    fechaCreacion DATE NOT NULL DEFAULT (CONVERT(DATE,GETDATE())), -- Fecha de creación del segmento

    CONSTRAINT PK_Segmento PRIMARY KEY (segmento_id) -- PK de Segmento
);
GO
---------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS MarketingCamp        -- Elimina MarketingCamp si existe
GO

CREATE TABLE MarketingCamp
(
    camp_id BIGINT IDENTITY(1,1) NOT NULL,      -- PK de la campaña de marketing
    nombreCamp NVARCHAR(120) NOT NULL,          -- Nombre de la campaña
    objetivo NVARCHAR(200) NULL,                -- Objetivo de la campaña
    presupuesto DECIMAL(18,2) NULL,             -- Presupuesto asignado a la campaña
    fechaInicio DATE NOT NULL,                  -- Fecha de inicio de la campaña
    fechaFin DATE NULL,                         -- Fecha de fin de la campaña
    estadoCamp NVARCHAR(10) NOT NULL DEFAULT 'Activo', -- Estado de la campaña

    usuario_id BIGINT NULL,                     -- FK al usuario responsable de la campaña
    segmento_id BIGINT NOT NULL,                -- FK al segmento objetivo (N:1)

    CONSTRAINT PK_MarketingCamp PRIMARY KEY (camp_id),            -- PK de MarketingCamp
    CONSTRAINT FK_MarketingCamp_Usuario FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id),  -- Enlace Usuario
    CONSTRAINT FK_MarketingCamp_Segmento FOREIGN KEY (segmento_id) REFERENCES Segmento(segmento_id) -- Enlace Segmento
);
GO

--------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS EncuestaSatisfaccion -- Elimina EncuestaSatisfaccion si existe
GO

CREATE TABLE EncuestaSatisfaccion
(
    encuesta_id BIGINT IDENTITY(1,1) NOT NULL,   -- PK de la encuesta
    fechaEncuesta DATETIME2 NOT NULL DEFAULT GETDATE(), -- Fecha en que se llena la encuesta
    puntaje TINYINT NOT NULL,                    -- Puntaje de satisfacción (definido por tu escala)
    comentarios NVARCHAR(300) NULL,              -- Comentarios del cliente

    caso_id BIGINT NULL,                         -- FK al caso asociado (1:1 lógico con caso)
    contacto_id BIGINT NULL,                     -- FK al contacto que responde

    CONSTRAINT PK_EncuestaSatisfaccion PRIMARY KEY (encuesta_id), -- PK de Encuesta
    CONSTRAINT FK_Encuesta_Caso FOREIGN KEY (caso_id) REFERENCES CasoReclamo(caso_id), -- Enlace Caso
    CONSTRAINT FK_Encuesta_Contacto FOREIGN KEY (contacto_id) REFERENCES Contacto(contacto_id), -- Enlace Contacto
    CONSTRAINT UQ_Encuesta_Caso UNIQUE (caso_id) -- Asegura que solo haya una encuesta por caso
);
GO

-------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS ContactoToMarketingCamp -- Elimina tabla puente si existe
GO

CREATE TABLE ContactoToMarketingCamp
( 
    camp_id BIGINT NOT NULL,                  -- FK a campaña de marketing
    contacto_id BIGINT NOT NULL,              -- FK a contacto

    CONSTRAINT PK_ContactoMarketingCamp PRIMARY KEY (contacto_id, camp_id), -- PK compuesta (evita duplicados)
    CONSTRAINT FK_CMC_Contacto FOREIGN KEY (contacto_id) REFERENCES Contacto(contacto_id), -- Enlace Contacto
    CONSTRAINT FK_CMC_MarketingCamp FOREIGN KEY (camp_id) REFERENCES MarketingCamp(camp_id) -- Enlace Campaña
);
GO
