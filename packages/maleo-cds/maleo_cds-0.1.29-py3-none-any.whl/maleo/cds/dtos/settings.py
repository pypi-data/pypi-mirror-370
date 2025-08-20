from pydantic import Field
from maleo.soma.dtos.settings import Settings as BaseSettings


class Settings(BaseSettings):
    ICD9_DB_PATH: str = Field(
        "./vectorstores/icd9_chroma_db", description="ICD10 Database Path"
    )
    ICD10_DB_PATH: str = Field(
        "./vectorstores/icd10_chroma_db", description="ICD10 Database Path"
    )
