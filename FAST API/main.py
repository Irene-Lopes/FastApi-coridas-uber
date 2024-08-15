from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4, UUID

app = FastAPI()

class Corrida(BaseModel):
    id: UUID
    origem: str
    destino: str
    distancia: float
    valor: float
    estado: str

corridas_db = []

def calcular_valor(distancia: float) -> float:
    return 6.65 + (2 * distancia)

@app.post("/corridas/", response_model=Corrida)
def criar_corrida(origem: str, destino: str, distancia: float):
    corrida = Corrida(
        id=uuid4(),
        origem=origem,
        destino=destino,
        distancia=distancia,
        valor=calcular_valor(distancia),
        estado="Requisitada"
    )
    corridas_db.append(corrida)
    return corrida

@app.get("/corridas/", response_model=List[Corrida])
def listar_corridas(estado: Optional[str] = None):
    if estado:
        return [corrida for corrida in corridas_db if corrida.estado == estado.capitalize()]
    return corridas_db

@app.put("/corridas/{corrida_id}", response_model=Corrida)
def alterar_corrida(corrida_id: UUID, origem: Optional[str] = None, destino: Optional[str] = None, distancia: Optional[float] = None):
    for corrida in corridas_db:
        if corrida.id == corrida_id:
            if corrida.estado not in ["Requisitada", "Em Andamento"]:
                raise HTTPException(status_code=400, detail="Corrida não pode ser alterada")
            if origem:
                corrida.origem = origem
            if destino:
                corrida.destino = destino
            if distancia:
                corrida.distancia = distancia
                corrida.valor = calcular_valor(distancia)
            return corrida
    raise HTTPException(status_code=404, detail="Corrida não encontrada")

@app.post("/corridas/{corrida_id}/iniciar", response_model=Corrida)
def iniciar_corrida(corrida_id: UUID):
    for corrida in corridas_db:
        if corrida.id == corrida_id:
            if corrida.estado != "Requisitada":
                raise HTTPException(status_code=400, detail="Somente corridas requisitadas podem ser iniciadas")
            corrida.estado = "Em Andamento"
            return corrida
    raise HTTPException(status_code=404, detail="Corrida não encontrada")

@app.post("/corridas/{corrida_id}/finalizar", response_model=Corrida)
def finalizar_corrida(corrida_id: UUID):
    for corrida in corridas_db:
        if corrida.id == corrida_id:
            if corrida.estado != "Em Andamento":
                raise HTTPException(status_code=400, detail="Somente corridas em andamento podem ser finalizadas")
            corrida.estado = "Finalizado"
            return corrida
    raise HTTPException(status_code=404, detail="Corrida não encontrada")

@app.delete("/corridas/{corrida_id}", response_model=Corrida)
def remover_corrida(corrida_id: UUID):
    for corrida in corridas_db:
        if corrida.id == corrida_id:
            if corrida.estado != "Requisitada":
                raise HTTPException(status_code=400, detail="Somente corridas requisitadas podem ser removidas")
            corridas_db.remove(corrida)
            return corrida
    raise HTTPException(status_code=404, detail="Corrida não encontrada")