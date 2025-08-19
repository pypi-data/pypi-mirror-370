import torch
import torch.nn as nn
from transformers import PreTrainedModel, BertModel
from .configuration_lpr import LPRConfig
from esm.models.esmc import ESMC

class LPR(PreTrainedModel):
    config_class = LPRConfig

    def __init__(self, config: LPRConfig):
        super().__init__(config)

        self.num_classes = config.num_classes

        # 1. ESMC
        self.esmc = ESMC.from_pretrained(config.esmc_model).to(torch.float32)
        for p in self.esmc.parameters():
            p.requires_grad = True  # 可调为 False 冻结

        # 2. 960 → 768
        self.Linear960_768 = nn.Sequential(
            nn.Linear(960, 768),
            nn.GELU(),
            nn.LayerNorm(768, eps=1e-5)
        )

        # 3. BERT
        self.bert = BertModel.from_pretrained(config.bert_model)
        for p in self.bert.parameters():
            p.requires_grad = True

        # 4. 分类头
        self.classifier = nn.Sequential(
            nn.Linear(768, 768),
            nn.Dropout(0.1),
            nn.GELU(),
            nn.LayerNorm(768, eps=1e-5),
            nn.Linear(768, self.num_classes)
        )

        self.post_init()  # HuggingFace 权重初始化

    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        # 1. ESMC
        esmc_out = self.esmc(input_ids, attention_mask)
        embeddings = esmc_out.embeddings  # [B, L, 960]

        # 2. 映射到 BERT 维度
        embeddings = self.Linear960_768(embeddings)

        # 3. Position IDs
        batch_size, seq_len, _ = embeddings.size()
        position_ids = torch.arange(seq_len, dtype=torch.long, device=embeddings.device).unsqueeze(0).expand(batch_size, seq_len)

        # 4. BERT
        bert_out = self.bert(
            inputs_embeds=embeddings,
            attention_mask=attention_mask,
            position_ids=position_ids,
            return_dict=True
        )

        cls_output = bert_out.last_hidden_state[:, 0]
        logits = self.classifier(bert_out.pooler_output)

        return {"logits": logits, "cls_output": cls_output}
