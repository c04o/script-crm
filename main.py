import sys
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary, DECIMAL, BigInteger, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ==========================================
# 1. CONFIGURACIÓN DE CONEXIÓN
# ==========================================
# Ajusta el SERVER_NAME si es necesario (ej: 'LOCALHOST\SQLEXPRESS' o '.')
SERVER_NAME = '.' 
DATABASE_NAME = 'Crm'
CONNECTION_STRING = f'mssql+pyodbc://{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# ==========================================
# 2. MODELOS (Reflejo exacto de tu crm.sql)
# ==========================================

class Rol(Base):
    __tablename__ = 'Rol'
    rol_id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombreRol = Column(String(30), nullable=False)
    descripcionRol = Column(String(200), nullable=True)
    estadoRol = Column(Boolean, default=True)
    fechaAsignacion = Column(DateTime, default=datetime.now)

class Usuario(Base):
    __tablename__ = 'Usuario'
    usuario_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(10), nullable=False)
    hashPassword = Column(LargeBinary(256), nullable=False)
    nombreUsuario = Column(String(50), nullable=False)
    apellidosUsuario = Column(String(50), nullable=True)
    emailUsuario = Column(String(50), nullable=False)
    telefonoUsuario = Column(String(15), nullable=True)
    estadoUsuario = Column(Boolean, default=True)
    rol_id = Column(BigInteger, ForeignKey('Rol.rol_id'))
    
    # Relación para navegar
    rol = relationship("Rol")

class Empresa(Base):
    __tablename__ = 'Empresa'
    empresa_id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombreEmpresa = Column(String(100), nullable=False)
    direccionEmpresa = Column(String(180), nullable=True)
    telefonoEmpresa = Column(String(15), nullable=True)
    emailEmpresa = Column(String(50), nullable=True)
    estadoEmpresa = Column(String(10), default='Activo')
    fechaRegistro = Column(DateTime, default=datetime.now)

class Cuenta(Base):
    __tablename__ = 'Cuenta'
    cuenta_id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(30), nullable=False)
    telefono = Column(String(15), nullable=True)
    email = Column(String(50), nullable=True)
    estado = Column(String(10), default='Activo')
    fechaCreado = Column(DateTime, default=datetime.now)
    empresa_id = Column(BigInteger, ForeignKey('Empresa.empresa_id'))

class Lead(Base):
    __tablename__ = 'Lead'
    lead_id = Column(BigInteger, primary_key=True, autoincrement=True)
    origen = Column(String(40), nullable=False)
    nombreLead = Column(String(100), nullable=False)
    emailLead = Column(String(50), nullable=True)
    interes = Column(String(120), nullable=True)
    estadoLead = Column(String(20), default='Abierto')
    fechaCreadoLead = Column(DateTime, default=datetime.now)

class Contacto(Base):
    __tablename__ = 'Contacto'
    contacto_id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombreCliente = Column(String(30), nullable=False)
    apellidoCliente = Column(String(50), nullable=False)
    telefonoCliente = Column(String(15), nullable=True)
    emailCliente = Column(String(50), nullable=False)
    estadoCliente = Column(Boolean, default=True)
    fechaCreadoCliente = Column(DateTime, default=datetime.now)
    lead_id = Column(BigInteger, ForeignKey('Lead.lead_id'))
    cuenta_id = Column(BigInteger, ForeignKey('Cuenta.cuenta_id'))

class Oportunidad(Base):
    __tablename__ = 'Oportunidad'
    oportunidad_id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombreOp = Column(String(100), nullable=False)
    probabilidad = Column(DECIMAL(5, 2), default=0)
    monto = Column(DECIMAL(18, 2), nullable=True)
    etapa = Column(String(30), default='Prospección')
    fechaCreacionOp = Column(DateTime, default=datetime.now)
    cuenta_id = Column(BigInteger, ForeignKey('Cuenta.cuenta_id'))
    lead_id = Column(BigInteger, ForeignKey('Lead.lead_id'))

# ==========================================
# 3. INTERFAZ DE USUARIO (INPUTS)
# ==========================================

def get_input(prompt, required=True):
    while True:
        valor = input(prompt)
        if not valor and required:
            print("❌ Este campo es obligatorio.")
        else:
            return valor if valor else None

def menu_principal():
    while True:
        print("\n" + "="*40)
        print("   INTERFAZ DE LLENADO CRM (PYTHON)")
        print("="*40)
        print("1. Agregar ROL (Sistema)")
        print("2. Agregar USUARIO (Sistema)")
        print("3. Agregar EMPRESA (Cliente)")
        print("4. Agregar CUENTA (Cliente)")
        print("5. Registrar LEAD (Prospecto)")
        print("6. Convertir Lead a CONTACTO")
        print("7. Crear OPORTUNIDAD de Venta")
        print("8. VER DATOS (Reporte rápido)")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1': agregar_rol()
        elif opcion == '2': agregar_usuario()
        elif opcion == '3': agregar_empresa()
        elif opcion == '4': agregar_cuenta()
        elif opcion == '5': agregar_lead()
        elif opcion == '6': agregar_contacto()
        elif opcion == '7': agregar_oportunidad()
        elif opcion == '8': ver_datos()
        elif opcion == '0': sys.exit()
        else: print("Opción inválida.")

# --- FUNCIONES DE LLENADO ---

def agregar_rol():
    print("\n--- NUEVO ROL ---")
    nombre = get_input("Nombre del Rol (ej. Vendedor): ")
    desc = get_input("Descripción: ", required=False)
    
    rol = Rol(nombreRol=nombre, descripcionRol=desc)
    guardar(rol)

def agregar_usuario():
    print("\n--- NUEVO USUARIO ---")
    listar(Rol, "rol_id", "nombreRol")
    id_rol = get_input("ID del Rol a asignar: ")
    
    user = get_input("Username: ")
    pwd = get_input("Password: ")
    nombre = get_input("Nombre real: ")
    email = get_input("Email: ")
    
    # Hash password para cumplir con VARBINARY(256)
    pwd_hash = hashlib.sha256(pwd.encode()).digest()
    
    nuevo_usuario = Usuario(
        username=user, hashPassword=pwd_hash, nombreUsuario=nombre,
        emailUsuario=email, rol_id=id_rol
    )
    guardar(nuevo_usuario)

def agregar_empresa():
    print("\n--- NUEVA EMPRESA ---")
    nombre = get_input("Nombre Empresa Legal: ")
    direccion = get_input("Dirección: ", required=False)
    nuevo = Empresa(nombreEmpresa=nombre, direccionEmpresa=direccion)
    guardar(nuevo)

def agregar_cuenta():
    print("\n--- NUEVA CUENTA ---")
    listar(Empresa, "empresa_id", "nombreEmpresa")
    emp_id = get_input("ID Empresa (Enter si no tiene): ", required=False)
    
    nombre = get_input("Nombre de la Cuenta: ")
    email = get_input("Email de contacto: ", required=False)
    
    nueva = Cuenta(nombre=nombre, email=email, empresa_id=emp_id)
    guardar(nueva)

def agregar_lead():
    print("\n--- NUEVO LEAD (PROSPECTO) ---")
    nombre = get_input("Nombre del Lead: ")
    origen = get_input("Origen (Web, Llamada, etc): ")
    interes = get_input("Interés (Producto X): ", required=False)
    
    nuevo = Lead(nombreLead=nombre, origen=origen, interes=interes)
    guardar(nuevo)

def agregar_contacto():
    print("\n--- NUEVO CONTACTO ---")
    print("¿Viene de un Lead existente? (Deja vacío si es nuevo directo)")
    listar(Lead, "lead_id", "nombreLead")
    lid = get_input("ID Lead: ", required=False)
    
    print("Asignar a Cuenta:")
    listar(Cuenta, "cuenta_id", "nombre")
    cid = get_input("ID Cuenta: ", required=False)
    
    nombre = get_input("Nombre Pila: ")
    apellido = get_input("Apellido: ")
    email = get_input("Email: ")
    
    nuevo = Contacto(nombreCliente=nombre, apellidoCliente=apellido, 
                     emailCliente=email, lead_id=lid, cuenta_id=cid)
    guardar(nuevo)

def agregar_oportunidad():
    print("\n--- NUEVA OPORTUNIDAD ---")
    listar(Cuenta, "cuenta_id", "nombre")
    cid = get_input("ID Cuenta (Obligatorio): ")
    
    nombre = get_input("Nombre Oportunidad (ej. Venta Licencias 2025): ")
    monto = get_input("Monto estimado: ", required=False)
    prob = get_input("Probabilidad (0-100): ", required=False)
    
    nueva = Oportunidad(nombreOp=nombre, cuenta_id=cid, 
                        monto=monto, probabilidad=prob)
    guardar(nueva)

# --- UTILIDADES ---

def guardar(objeto):
    try:
        session.add(objeto)
        session.commit()
        print("✅ ¡Guardado exitosamente en la Base de Datos!")
    except Exception as e:
        session.rollback()
        print(f"❌ Error SQL: {e}")

def listar(clase, id_field, name_field):
    registros = session.query(clase).all()
    print(f"\n--- Lista de {clase.__tablename__} ---")
    for r in registros:
        # Obtiene dinámicamente los valores de los atributos
        rid = getattr(r, id_field)
        rname = getattr(r, name_field)
        print(f"[{rid}] {rname}")
    print("-------------------------")

def ver_datos():
    print("\nRESUMEN:")
    print(f"Roles: {session.query(Rol).count()}")
    print(f"Usuarios: {session.query(Usuario).count()}")
    print(f"Empresas: {session.query(Empresa).count()}")
    print(f"Cuentas: {session.query(Cuenta).count()}")
    print(f"Leads: {session.query(Lead).count()}")
    print(f"Oportunidades: {session.query(Oportunidad).count()}")

if __name__ == "__main__":
    try:
        # Prueba conexión
        engine.connect()
        menu_principal()
    except Exception as e:
        print("❌ Error de conexión. Revisa que SQL Server esté corriendo.")
        print(e)