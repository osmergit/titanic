#pip install fastapi uvicorn pymysql
#127.0.0.1:8000/docs
#uvicorn main:app --reload
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pymysql
from pymysql import Error
from Conexion import obtener_conexion  # Importamos la función de conexión

app = FastAPI()

# Modelo Pydantic para la tabla personas
class Persona(BaseModel):
    nombre: str
    apellido: str
    edad: Optional[int] = None
    email: Optional[str] = None
    fecha: Optional[str] = None

class PersonaUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    edad: Optional[int] = None
    email: Optional[str] = None
    fecha: Optional[str] = None

# CREATE - Añadir una nueva persona
@app.post("/personas/")
def crear_persona(persona: Persona):
    conexion = obtener_conexion()  # Usamos la función importada
    try:
        with conexion.cursor() as cursor:
            sql = """
            INSERT INTO personas (nombre, apellido, edad, email, fecha)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                persona.nombre, 
                persona.apellido, 
                persona.edad, 
                persona.email, 
                persona.fecha
            ))
            conexion.commit()
            persona_id = cursor.lastrowid
            return {"mensaje": "Persona creada exitosamente", "id": persona_id}
    except Error as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear persona: {e}")
    finally:
        conexion.close()

# READ - Obtener todas las personas
@app.get("/personas/")
def obtener_personas():
    conexion = obtener_conexion()  # Usamos la función importada
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM personas")
            personas = cursor.fetchall()
            return {"personas": personas}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener personas: {e}")
    finally:
        conexion.close()

# READ - Obtener una persona por ID
@app.get("/personas/{persona_id}")
def obtener_persona(persona_id: int):
    conexion = obtener_conexion()  # Usamos la función importada
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM personas WHERE idpersonas = %s", (persona_id,))
            persona = cursor.fetchone()
            if persona is None:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            return {"persona": persona}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener persona: {e}")
    finally:
        conexion.close()

# UPDATE - Actualizar una persona
@app.put("/personas/{persona_id}")
def actualizar_persona(persona_id: int, persona: PersonaUpdate):
    conexion = obtener_conexion()  # Usamos la función importada
    try:
        with conexion.cursor() as cursor:
            # Primero verificamos que la persona exista
            cursor.execute("SELECT idpersonas FROM personas WHERE idpersonas = %s", (persona_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            
            # Construimos la consulta dinámica
            update_fields = []
            params = []
            
            if persona.nombre is not None:
                update_fields.append("nombre = %s")
                params.append(persona.nombre)
            
            if persona.apellido is not None:
                update_fields.append("apellido = %s")
                params.append(persona.apellido)
                
            if persona.edad is not None:
                update_fields.append("edad = %s")
                params.append(persona.edad)
                
            if persona.email is not None:
                update_fields.append("email = %s")
                params.append(persona.email)
                
            if persona.fecha is not None:
                update_fields.append("fecha = %s")
                params.append(persona.fecha)
                
            if not update_fields:
                raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
                
            sql = f"UPDATE personas SET {', '.join(update_fields)} WHERE idpersonas = %s"
            params.append(persona_id)
            
            cursor.execute(sql, tuple(params))
            conexion.commit()
            return {"mensaje": "Persona actualizada exitosamente"}
    except Error as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar persona: {e}")
    finally:
        conexion.close()

# DELETE - Eliminar una persona
@app.delete("/personas/{persona_id}")
def eliminar_persona(persona_id: int):
    conexion = obtener_conexion()  # Usamos la función importada
    try:
        with conexion.cursor() as cursor:
            # Primero verificamos que la persona exista
            cursor.execute("SELECT idpersonas FROM personas WHERE idpersonas = %s", (persona_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            
            cursor.execute("DELETE FROM personas WHERE idpersonas = %s", (persona_id,))
            conexion.commit()
            return {"mensaje": "Persona eliminada exitosamente"}
    except Error as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar persona: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)