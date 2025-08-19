from convisoappsec.flow.graphql_api.beta.models.issues.sast import CreateSastFindingInput

class CreateIacFindingInput(CreateSastFindingInput):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
