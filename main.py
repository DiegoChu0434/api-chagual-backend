import decimal
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

URL_DATABASE = os.getenv("DATABASE_URL")

engine = create_engine(
    URL_DATABASE,
    pool_recycle=3600,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED"
)

SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="API FICHA CHAGUAL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

class RepuestaControl(BaseModel):
    id_control: int
    estado: str
    fecha_borrador: Optional[str] = None
    hora_borrador: Optional[str] = None
    fecha_finalizado: Optional[str] = None
    hora_finalizado: Optional[str] = None
    fecha_enviado: Optional[str] = None
    hora_enviado: Optional[str] = None
    fecha_registro: Any
    model_config = ConfigDict(from_attributes=True)

class RespuestaFoto(BaseModel):
    id_foto: int
    id_ficha: int
    url_foto: str
    tipo_foto: Optional[str]
    origen: Optional[str]
    fecha_subida: Any
    model_config = ConfigDict(from_attributes=True)

@app.get("/")
def chequeo_api():
    return {"status": "Online", "modo": "Procedimiento almacenado - Proyecto CHAGUAL"}

@app.post("/controles")
def crear_control(data: Dict[str, Any], db: Session = Depends(obtener_db)):
    try:
        query = text("CALL insertar_control(:estado)")
        db.execute(query, {"estado": data.get("estado", "BORRADOR")})
        db.commit()
        res = db.execute(text("SELECT LAST_INSERT_ID()"))
        new_id = res.scalar()
        return {"message": "Control registrado correctamente", "id_control": new_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/controles", response_model=List[RepuestaControl])
def listar_controles(db: Session = Depends(obtener_db)):
    result = db.execute(text("CALL listar_control()"))
    return result.mappings().all()

@app.put("/controles/{id_control}")
def actualizar_control_estado(id_control: int, data: Dict[str, Any], db: Session = Depends(obtener_db)):
    try:
        query = text("CALL actualizar_control(:id, :estado)")  
        db.execute(query, {"id": id_control, "estado": data.get("estado")})
        db.commit()
        return {"message": "Estado del control actualizado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/controles/{id_control}")
def eliminar_control(id_control: int, db: Session = Depends(obtener_db)):
    try:
        db.execute(text("CALL eliminar_control(:id)"), {"id": id_control})
        db.commit()
        return {"message": "Control eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/fichas")
def listar_fichas(db: Session = Depends(obtener_db)):
    try:
        result = db.execute(text("CALL listar_ficha_chagual()"))
        return result.mappings().all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/fichas")
def crear_ficha(data: Dict[str, Any], db: Session = Depends(obtener_db)):
    try:
        query = text("""
            CALL insertar_ficha_chagual(
                :id_control, :codigo, :telefono_contacto, :centro_poblado, :nombres_apellidos, :dni, :audio, 
                :uso_area_afectada, :tenencia_edificacion, :total_ambientes, 
                :anios_construccion, :agua_utilizada, :tiene_desague, 
                :necesidades_fisiologicas, :tipo_alumbrado, :servicios_edificacion, 
                :nivel_estudio, :centros_educativos, :tiempo_acceso, 
                :sintomas_recientes, :centro_salud_cercano, 
                :tiempo_demora_establecimiento, :atencion_enfermedad, 
                :ocupacion_principal, :ocupacion_secundaria, :frecuencia_ingreso, 
                :tipo_riego, :produccion_agricola, :produccion_pecuaria, 
                :vende_cultivos, :latitud, :longitud, :altitud, 
                :precision_gps, :registro_digital_dni
            )
        """)
        db.execute(query, data)
        db.commit()
        return {"message": "Datos de la ficha sincronizados correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/fichas/{id_ficha}")
def actualizar_ficha(id_ficha: int, data: Dict[str, Any], db: Session = Depends(obtener_db)):
    try:
        data["p_id_ficha"] = id_ficha
        query = text("""
            CALL actualizar_ficha_chagual(
                :p_id_ficha, :codigo, :telefono_contacto, :centro_poblado, :nombres_apellidos, :dni, :audio, 
                :uso_area_afectada, :tenencia_edificacion, :total_ambientes, 
                :anios_construccion, :agua_utilizada, :tiene_desague, 
                :necesidades_fisiologicas, :tipo_alumbrado, :servicios_edificacion, 
                :nivel_estudio, :centros_educativos, :tiempo_acceso, 
                :sintomas_recientes, :centro_salud_cercano, 
                :tiempo_demora_establecimiento, :atencion_enfermedad, 
                :ocupacion_principal, :ocupacion_secundaria, :frecuencia_ingreso, 
                :tipo_riego, :produccion_agricola, :produccion_pecuaria, 
                :vende_cultivos, :latitud, :longitud, :altitud, 
                :precision_gps, :registro_digital_dni
            )
        """)
        db.execute(query, data)
        db.commit()
        return {"message": "Ficha actualizada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/fichas/{id_ficha}")
def eliminar_ficha(id_ficha: int, db: Session = Depends(obtener_db)):
    try:
        db.execute(text("CALL eliminar_ficha_chagual(:id)"), {"id": id_ficha})
        db.commit()
        return {"message": "Ficha eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/fotos")
def crear_foto(data: Dict[str, Any], db: Session = Depends(obtener_db)):
    try:
        query = text("CALL insertar_ficha_foto(:id_ficha, :url_foto, :tipo_foto, :origen)")
        db.execute(query, {
            "id_ficha": data.get("id_ficha"),
            "url_foto": data.get("url_foto"),
            "tipo_foto": data.get("tipo_foto", ""),
            "origen": data.get("origen", "")
        })
        db.commit()
        return {"message": "Foto vinculada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/fotos/{id_ficha}", response_model=List[RespuestaFoto])
def listar_fotos_por_ficha(id_ficha: int, db: Session = Depends(obtener_db)):
    result = db.execute(text("CALL listar_ficha_foto(:id_ficha)"), {"id_ficha": id_ficha})
    return result.mappings().all()

@app.put("/fotos/{id_foto}")
def actualizar_foto(id_foto: int, data: Dict[str, Any], db: Session = Depends(obtener_db)):
    try:
        query = text("CALL actualizar_ficha_foto(:id, :url, :tipo, :origen)")
        db.execute(query, {
            "id": id_foto,
            "url": data.get("url_foto"),
            "tipo": data.get("tipo_foto"),
            "origen": data.get("origen")
        })
        db.commit()
        return {"message": "Foto actualizada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/fotos/{id_foto}")
def eliminar_foto(id_foto: int, db: Session = Depends(obtener_db)):
    try:
        db.execute(text("CALL eliminar_ficha_foto(:id)"), {"id": id_foto})
        db.commit()
        return {"message": "Foto eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))