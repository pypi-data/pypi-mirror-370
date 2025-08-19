from pymongo.errors import BulkWriteError

class ProtocoloRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_protocolo(self, protocolo: dict) -> bool:
        
        try:
            protocolo_no_db = await self.__db.protocolo.find_one(
                {"SolicitacaoId": protocolo["solicitacaoId"], "evento": protocolo["evento"]}
            )

            if protocolo_no_db is None:
                await self.__db.protocolo.insert_one(protocolo)
                return True

            await self.__db.protocolo.delete_one(
                   {"SolicitacaoId": protocolo["solicitacaoId"], "evento": protocolo["evento"]}
            )
            await self.__db.protocolo.insert_one(protocolo)
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir o protocolo: {e}")
            return False
        
    async def inserir_protocolos_em_lote(self, protocolos: list[dict]) -> bool:
        try:
            if not protocolos:
                return False

            filtros = [{"SolicitacaoId": a["solicitacaoId"], "evento": a["evento"]} for a in protocolos]
            await self.__db.protocolo.delete_many({"$or": filtros})

            await self.__db.protocolo.insert_many(protocolos)
            return True
        except BulkWriteError as bwe:
            print(f"❌ Erro de escrita em lote: {bwe.details}")
            return False
        except Exception as e:
            print(f"❌ Erro ao inserir protocolos em lote: {e}")
            return False

    async def remover_protocolo(self, solicitacaoId: int) -> bool:
        try:
            await self.__db.protocolo.delete_many({"SolicitacaoId": solicitacaoId})
            return True
        except Exception as e:
            print(f"❌ Erro ao remover o protocolo: {e}")
            return False

    async def buscar_por_solicitacao_id(self, solicitacaoId: int) -> list[dict]:
        try:
            return await self.__db.protocolo.find({"solicitacaoId": solicitacaoId}).to_list(length=None)
        except Exception as e:
            print(f"❌ Erro ao buscar protocolo por solicitacaoId: {e}")
            return []