class MegatronPPOPolicy:
    def __init__(self, model, optimizer, cfg):
        self.model = model
        self.optimizer = optimizer
        self.cfg = cfg

    def forward(self, data):
        return self.model(data)