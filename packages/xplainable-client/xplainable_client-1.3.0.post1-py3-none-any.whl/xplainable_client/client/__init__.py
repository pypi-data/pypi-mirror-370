from ._models import *
from ._misc import *
from ._session import Session
from ._misc import Misc
from ._models import Models
from ._preprocessing import Preprocessing
from ._deployments import Deployments
from ._gpt import GPT
from ._collections import Collections
from ._datasets import Datasets
from ._inference import Inference


class Client(Misc, Models, Preprocessing, GPT, Collections, Datasets, Inference, Deployments):

    def __init__(self, api_key=None, hostname='https://api.xplainable.io', org_id=None, team_id=None):
        self.session = Session(api_key=api_key, hostname=hostname, org_id=org_id, team_id=team_id)
        Misc.__init__(self, self.session)
        Models.__init__(self, self.session)
        Preprocessing.__init__(self, self.session)
        Deployments.__init__(self, self.session)
        GPT.__init__(self, self.session)
        Collections.__init__(self, self.session)
        Datasets.__init__(self, self.session)
        Inference.__init__(self, self.session)




