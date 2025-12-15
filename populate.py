import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
SERVER_NAME = '.' 
DATABASE_NAME = 'Crm'
CONNECTION_STRING = f'mssql+pyodbc://{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

# ==========================================
# 2. LISTAS MAESTRAS (DATOS FIJOS)
# ==========================================

# Mantenemos Roles y Usuarios Fijos
ROLES_DATA = [
    {"nombre": "Administrador", "desc": "Acceso total"},
    {"nombre": "Gerente Comercial", "desc": "Ver reportes y aprobar descuentos"},
    {"nombre": "Ejecutivo de Ventas", "desc": "Prospección y Cierre"}
]

USUARIOS_DATA = [
    ("admin", "admin123", "Super", "Admin", 0),
    ("carlos.g", "ventas2025", "Carlos", "Guillen", 1),
    ("sofia.m", "ventas2025", "Sofia", "Mendez", 2)
]

# 10 Empresas Fijas
EMPRESAS_DATA = [
    {"nombre": "Grupo Pellas", "dir": "Km 4.5 Carretera a Masaya"},
    {"nombre": "Sinsa", "dir": "Rotonda el Gueguense"},
    {"nombre": "Banpro", "dir": "Centro Corporativo Banpro"},
    {"nombre": "Claro", "dir": "Edificio Claro Puntaldia"},
    {"nombre": "Cervecería Toña", "dir": "Carretera Norte Km 6"},
    {"nombre": "Walmart", "dir": "Frente a Club Terraza"},
    {"nombre": "Hospital Vivaz", "dir": "Km 9 Carretera Masaya"},
    {"nombre": "Auto Nica", "dir": "Pista Jean Paul Genie"},
    {"nombre": "Super La Colonia", "dir": "Plaza España"},
    {"nombre": "Pizza Hut", "dir": "Metrocentro Planta Baja"}
]

# Listas para generar combinaciones fijas de LEADS (Personas)
NOMBRES = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Elena", "Pedro", "Lucia", "Jorge", "Sofia"]
APELLIDOS = ["Perez", "Gomez", "Lopez", "Martinez", "Rodriguez", "Hernandez", "Garcia", "Torres", "Flores", "Reyes"]
# Esto generará 10x10 = 100 combinaciones posibles de nombres únicos

# Listas para generar OPORTUNIDADES variadas
PRODUCTOS = ["Licencias Office", "Servidores Dell", "Cableado Estructurado", "Consultoría SAP", "Mantenimiento Aires"]
ETAPAS = ["Prospección", "Negociación", "Cierre Ganado", "Cierre Perdido", "Análisis"]

# ==========================================
# 3. FUNCIONES
# ==========================================

def hashear(pwd):
    return hashlib.sha256(pwd.encode()).digest()

def limpiar_todo():
    print("🧹 Borrando datos antiguos...")
    # Orden específico para evitar conflictos de Foreign Keys
    tablas = ['Oportunidad', 'Contacto', 'Lead', 'Cuenta', 'Empresa', 'Usuario', 'Rol']
    for t in tablas:
        try:
            session.execute(text(f"DELETE FROM {t}"))
            # Reiniciamos el contador de ID a 0 para que empiece en 1
            session.execute(text(f"DBCC CHECKIDENT ('{t}', RESEED, 0)")) 
        except Exception as e:
            print(f"⚠️ Nota: Limpieza parcial en {t} (Tabla podría estar vacía)")
    session.commit()
    print("✅ BD Limpia.")

def insertar_roles_y_usuarios():
    print("👤 Creando Usuarios y Roles...")
    roles_ids = []
    
    # 1. Roles
    for r in ROLES_DATA:
        res = session.execute(text("""
            INSERT INTO Rol (nombreRol, descripcionRol, estadoRol, fechaAsignacion) 
            OUTPUT inserted.rol_id VALUES (:n, :d, 1, GETDATE())
        """), {"n": r['nombre'], "d": r['desc']})
        roles_ids.append(res.fetchone()[0])
    
    # 2. Usuarios
    for u_user, u_pass, u_nom, u_ape, r_idx in USUARIOS_DATA:
        session.execute(text("""
            INSERT INTO Usuario (username, hashPassword, nombreUsuario, apellidosUsuario, emailUsuario, estadoUsuario, rol_id)
            VALUES (:u, :p, :n, :a, :e, 1, :r)
        """), {
            "u": u_user,
            "p": hashear(u_pass),
            "n": f"{u_nom} {u_ape}",
            "a": u_ape,
            "e": f"{u_user}@crm.ni",
            "r": roles_ids[r_idx]
        })
    session.commit()

def insertar_flujo_masivo():
    print("🏭 Generando Datos Masivos (Empresas, Leads, Oportunidades)...")
    
    # --- 1. CREAR 10 EMPRESAS ---
    empresa_ids = []
    for emp in EMPRESAS_DATA:
        # Generamos email y telefono fijos basados en el nombre para que parezcan reales
        clean_name = emp['nombre'].replace(" ", "").lower()
        res = session.execute(text("""
            INSERT INTO Empresa (nombreEmpresa, direccionEmpresa, telefonoEmpresa, emailEmpresa, estadoEmpresa, fechaRegistro)
            OUTPUT inserted.empresa_id VALUES (:n, :d, :t, :e, 'Activo', GETDATE())
        """), {
            "n": emp['nombre'],
            "d": emp['dir'],
            "t": "+505 22" + str(len(emp['nombre'])*111111)[:6], # Telefono pseudo-aleatorio fijo
            "e": f"contacto@{clean_name}.com.ni"
        })
        empresa_ids.append(res.fetchone()[0])
    
    # --- 2. CREAR 10 CUENTAS (1 por Empresa) ---
    cuenta_ids = []
    for idx, emp_id in enumerate(empresa_ids):
        nombre_cuenta = f"Cuenta {EMPRESAS_DATA[idx]['nombre']}"
        res = session.execute(text("""
            INSERT INTO Cuenta (nombre, telefono, email, estado, fechaCreado, empresa_id)
            OUTPUT inserted.cuenta_id VALUES (:n, '2255-0000', 'factura@cliente.com', 'Activo', GETDATE(), :eid)
        """), {"n": nombre_cuenta, "eid": emp_id})
        cuenta_ids.append(res.fetchone()[0])

    # --- 3. CREAR 50 LEADS (Para cubrir las 50 oportunidades) ---
    # Usamos bucles para combinar Nombres y Apellidos de forma determinista
    lead_ids = []
    contador_leads = 0
    for nombre in NOMBRES:
        for apellido in APELLIDOS:
            if contador_leads >= 50: break # Solo queremos 50
            
            res = session.execute(text("""
                INSERT INTO Lead (nombreLead, origen, interes, emailLead, estadoLead, fechaCreadoLead)
                OUTPUT inserted.lead_id VALUES (:n, 'Web', 'Servicios Varios', :e, 'Nuevo', GETDATE())
            """), {
                "n": f"{nombre} {apellido}",
                "e": f"{nombre}.{apellido}@gmail.com".lower()
            })
            lead_ids.append(res.fetchone()[0])
            contador_leads += 1

    # --- 4. CREAR 50 OPORTUNIDADES ---
    # Distribuimos las 50 oportunidades entre las 10 Cuentas
    for i in range(50):
        # Matemática para distribuir datos:
        idx_cuenta = i % 10  # Cicla de 0 a 9 (Cuentas)
        idx_prod = i % 5     # Cicla de 0 a 4 (Productos)
        idx_etapa = i % 5    # Cicla de 0 a 4 (Etapas)
        
        monto_fijo = (i + 1) * 1500.00 # Montos variados pero fijos: 1500, 3000, 4500...
        
        # Cada oportunidad NECESITA un Lead único. Usamos la lista de leads que creamos.
        lead_asociado = lead_ids[i] 
        
        nombre_op = f"Venta {PRODUCTOS[idx_prod]} - Op#{i+1}"
        
        session.execute(text("""
            INSERT INTO Oportunidad (nombreOp, probabilidad, monto, etapa, fechaCreacionOp, cuenta_id, lead_id)
            VALUES (:n, 50, :m, :e, GETDATE(), :cid, :lid)
        """), {
            "n": nombre_op,
            "m": monto_fijo,
            "e": ETAPAS[idx_etapa],
            "cid": cuenta_ids[idx_cuenta],
            "lid": lead_asociado
        })

    session.commit()

# ==========================================
# 4. EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    try:
        print("🚀 INICIANDO POBLADO MASIVO DE DATOS...")
        limpiar_todo()
        insertar_roles_y_usuarios()
        insertar_flujo_masivo()
        
        print("\n✅ PROCESO FINALIZADO.")
        print(f"📊 Estadísticas Generadas:")
        print(f"   - 10 Empresas y Cuentas (Nicas)")
        print(f"   - 50 Leads Únicos")
        print(f"   - 50 Oportunidades de Venta")
        print("------------------------------------------------")
        print("🔐 Credenciales Admin: admin / admin123")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")