from ._session import Session


class Client_Cog:

    def __init__(self, session: Session):
        self.session = session