class ExportException(Exception):
    def __init__(self, measurement_uuid: str, agent_uuid: str):
        self.measurement_uuid = measurement_uuid
        self.agent_uuid = agent_uuid
        super().__init__()
