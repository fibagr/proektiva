from pydantic import BaseModel
from typing import Optional


class ConcentrationBlock(BaseModel):
    total: Optional[int] = 0
    average: Optional[float] = 0.0
    conclusion: Optional[str] = None


class AnxietyBlock(BaseModel):
    total: Optional[float] = 0.0
    average: Optional[float] = 0.0
    level: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None


class StressBlock(BaseModel):
    total: Optional[float] = 0.0
    average: Optional[float] = 0.0
    level: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None


class SleepBlock(BaseModel):
    total: Optional[float] = 0.0
    average: Optional[float] = 0.0
    level: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None


class SensoryBlock(BaseModel):
    tactileLevel: Optional[str] = None
    tactileTotal: Optional[float] = 0.0
    tactileAvg: Optional[float] = 0.0
    proprioLevel: Optional[str] = None
    proprioTotal: Optional[float] = 0.0
    proprioAvg: Optional[float] = 0.0
    vestibularLevel: Optional[str] = None
    vestibularTotal: Optional[float] = 0.0
    vestibularAvg: Optional[float] = 0.0
    auditoryLevel: Optional[str] = None
    auditoryTotal: Optional[float] = 0.0
    auditoryAvg: Optional[float] = 0.0
    visualLevel: Optional[str] = None
    visualTotal: Optional[float] = 0.0
    visualAvg: Optional[float] = 0.0
    interoLevel: Optional[str] = None
    interoTotal: Optional[float] = 0.0
    interoAvg: Optional[float] = 0.0


class FullSurveyPayload(BaseModel):
    language: str = "ru"
    concentration: Optional[ConcentrationBlock] = None
    anxiety: Optional[AnxietyBlock] = None
    stress: Optional[StressBlock] = None
    sleep: Optional[SleepBlock] = None
    sensory: Optional[SensoryBlock] = None
