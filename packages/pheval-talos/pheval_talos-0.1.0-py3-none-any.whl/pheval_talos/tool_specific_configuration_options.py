from pydantic import BaseModel, Field


class TALOSConfigurations(BaseModel):
    apptainer: bool = Field(...)
