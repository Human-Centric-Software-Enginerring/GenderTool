class UtteranceData(BaseModel):
    start_timestamp: float
    end_timestamp: float
    event: str
    transcription: str = None
    words : float = None
