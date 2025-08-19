import torch
import torch.nn as nn
import torch.nn.functional as F
import timm


class ResidualBlock(nn.Module):
    def __init__(self, channels, dilation=1):
        super().__init__()
        self.conv = nn.Conv2d(
            channels, channels, kernel_size=3,
            padding=dilation, dilation=dilation,
            padding_mode='circular'
        )
        self.norm = nn.GroupNorm(8, channels)
        self.act = nn.PReLU()

    def forward(self, x):
        y = self.act(self.norm(self.conv(x)))
        return y + x


class ASPPModule(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.branches = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(channels, channels, 1, padding=0, padding_mode='circular'),
                nn.GroupNorm(8, channels),
                nn.PReLU(),
            ),
            nn.Sequential(
                nn.Conv2d(channels, channels, 3, padding=6, dilation=6, padding_mode='circular'),
                nn.GroupNorm(8, channels),
                nn.PReLU(),
            ),
            nn.Sequential(
                nn.Conv2d(channels, channels, 3, padding=12, dilation=12, padding_mode='circular'),
                nn.GroupNorm(8, channels),
                nn.PReLU(),
            ),
        ])
        self.project = nn.Sequential(
            nn.Conv2d(channels * 3, channels, 1, padding=0, padding_mode='circular'),
            nn.GroupNorm(8, channels),
            nn.PReLU(),
        )

    def forward(self, x):
        feats = [b(x) for b in self.branches]
        return self.project(torch.cat(feats, dim=1))


class RefineHeadV2(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        self.res1 = ResidualBlock(in_channels, dilation=1)
        self.res2 = ResidualBlock(in_channels, dilation=2)
        self.aspp = ASPPModule(in_channels)
        self.res3 = ResidualBlock(in_channels, dilation=1)
        self.final = nn.Conv2d(in_channels, 1, kernel_size=1)

    def forward(self, v):
        v = self.res1(v)
        v = self.res2(v)
        v = self.aspp(v)
        v = self.res3(v)
        return self.final(v)


class WSASurrogateModel(nn.Module):
    """
    WSA surrogate model predicting 0.1 AU speed map from 2-channel input.

    Input: [B, 2, 360, 180] -> internally augmented to 4 channels (lon & lat).
    Output: [B, 1, 360, 180] km/s
    """

    def __init__(self, img_size=(360, 180), vmin=200, vmax=1200):
        super().__init__()
        self.vmin = vmin
        self.vmax = vmax

        self.backbone = timm.create_model(
            'swin_small_patch4_window7_224',
            pretrained=False,
            img_size=img_size,
            in_chans=4,
            features_only=True,
            drop_rate=0.2,
            attn_drop_rate=0.2,
            drop_path_rate=0.2,
            out_indices=(0, 1, 2, 3),
        )

        c1, c2, c3, c4 = self.backbone.feature_info.channels()

        self.activation = nn.ReLU(inplace=False)
        self.decoder_dropout = nn.Dropout2d(p=0.5)
        self.last_activation = nn.PReLU(num_parameters=1, init=0.25)

        self.up4_to_3 = nn.ConvTranspose2d(c4, c3, 4, 2, 1)
        self.merge3 = nn.Conv2d(c3 * 2, c3, kernel_size=3, padding=1, padding_mode='circular')

        self.up3_to_2 = nn.ConvTranspose2d(c3, c2, 4, 2, 1)
        self.merge2 = nn.Conv2d(c2 * 2, c2, kernel_size=3, padding=1, padding_mode='circular')

        self.up2_to_1 = nn.ConvTranspose2d(c2, c1, 4, 2, 1)
        self.merge1 = nn.Conv2d(c1 * 2, c1, kernel_size=3, padding=1, padding_mode='circular')

        self.refine = RefineHeadV2(c1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        device = x.device

        lon = torch.linspace(0, 1, steps=H, device=device).view(1, 1, H, 1).expand(B, 1, H, W)
        lat = torch.linspace(0, 1, steps=W, device=device).view(1, 1, 1, W).expand(B, 1, H, W)
        x = torch.cat([x, lon, lat], dim=1)

        f1, f2, f3, f4 = self.backbone(x.contiguous())
        f1 = f1.permute(0, 3, 1, 2)
        f2 = f2.permute(0, 3, 1, 2)
        f3 = f3.permute(0, 3, 1, 2)
        f4 = f4.permute(0, 3, 1, 2)

        u3 = self.activation(self.up4_to_3(f4))
        u3 = self.decoder_dropout(u3)
        u3 = u3[:, :, : f3.shape[2], : f3.shape[3]]
        x3 = torch.cat([u3, f3], dim=1)
        x3 = self.activation(self.merge3(x3))

        u2 = self.activation(self.up3_to_2(x3))
        u2 = self.decoder_dropout(u2)
        u2 = u2[:, :, : f2.shape[2], : f2.shape[3]]
        x2 = torch.cat([u2, f2], dim=1)
        x2 = self.activation(self.merge2(x2))

        u1 = self.activation(self.up2_to_1(x2))
        u1 = self.activation(u1)
        u1 = self.decoder_dropout(u1)
        u1 = u1[:, :, : f1.shape[2], : f1.shape[3]]
        x1 = self.last_activation(self.merge1(torch.cat([u1, f1], dim=1)))

        u0 = F.interpolate(x1, scale_factor=4, mode='bilinear', align_corners=False)
        output_raw = self.refine(u0)

        scale = (self.vmax - self.vmin) / 2
        mid = (self.vmax + self.vmin) / 2
        output_0p1AU = mid + scale * torch.tanh(output_raw)

        return output_0p1AU
