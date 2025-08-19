from transformers import PretrainedConfig

class LPRConfig(PretrainedConfig):
    model_type = "lpr"

    def __init__(self, num_classes=9, esmc_model="esmc_300m", bert_model="./bert-base-uncased", **kwargs):
        super().__init__(**kwargs)
        self.num_classes = num_classes
        self.esmc_model = esmc_model
        self.bert_model = bert_model
