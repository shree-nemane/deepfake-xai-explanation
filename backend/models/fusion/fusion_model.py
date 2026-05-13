import torch
import torch.nn as nn

class ForensicFusionModel(nn.Module):
    def __init__(self, convnext_dim=768, wav2vec_dim=768, forensic_dim=11, num_classes=2):
        super(ForensicFusionModel, self).__init__()
        
        self.total_dim = convnext_dim + wav2vec_dim + forensic_dim
        
        self.fusion_layer = nn.Sequential(
            nn.Linear(self.total_dim, 512),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

    def forward(self, conv_feat, wav_feat, foren_feat):
        # Concatenate features
        combined = torch.cat((conv_feat, wav_feat, foren_feat), dim=1)
        logits = self.fusion_layer(combined)
        return logits
