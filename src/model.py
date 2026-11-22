"""Lightweight pretrained backbones. `python -m src.model` times them on YOUR CPU."""
import time
import torch
import torch.nn as nn
import torchvision.models as tvm

ARCHS = ("mobilenet_v3_large", "efficientnet_b0", "resnet18")


def _res(arch):
    return arch.startswith("resnet")


def build_model(arch, n_classes, pretrained=True):
    m = tvm.get_model(arch, weights="DEFAULT" if pretrained else None)  # downloads ImageNet weights once
    if _res(arch):
        m.fc = nn.Sequential(nn.Dropout(0.2), nn.Linear(m.fc.in_features, n_classes))
    else:
        m.classifier[-1] = nn.Linear(m.classifier[-1].in_features, n_classes)
    return m


def freeze_backbone(m, arch):
    for p in m.parameters():
        p.requires_grad = False
    for p in (m.fc if _res(arch) else m.classifier).parameters():
        p.requires_grad = True


def unfreeze_last(m, arch, n=2):
    blocks = [m.layer4, m.layer3][:n] if _res(arch) else list(m.features.children())[-n:]
    for b in blocks:
        for p in b.parameters():
            p.requires_grad = True


def set_bn_eval(m):
    """Keep BatchNorm statistics fixed (small CPU batches make them noisy)."""
    for mod in m.modules():
        if isinstance(mod, nn.modules.batchnorm._BatchNorm):
            mod.eval()


def features(m, arch, x):
    """Penultimate pooled features."""
    if _res(arch):
        x = m.maxpool(m.relu(m.bn1(m.conv1(x))))
        return torch.flatten(m.avgpool(m.layer4(m.layer3(m.layer2(m.layer1(x))))), 1)
    return torch.flatten(m.avgpool(m.features(x)), 1)


def classify(m, arch, f):
    return m.fc(f) if _res(arch) else m.classifier(f)


def target_layer(m, arch):
    return m.layer4[-1] if _res(arch) else m.features[-1]


if __name__ == "__main__":
    for a in ARCHS:
        m = build_model(a, 38, pretrained=False).eval()
        x = torch.randn(16, 3, 224, 224)
        with torch.no_grad():
            m(x); t = time.time()
            for _ in range(3):
                m(x)
        dt = (time.time() - t) / 48
        print(f"{a:20s} params={sum(p.numel() for p in m.parameters()) / 1e6:5.2f}M  forward={dt * 1000:6.1f} ms/img")
