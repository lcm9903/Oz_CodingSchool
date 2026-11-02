"""
폐렴 예측 모델의 '구조' 정의.

노션에서 제공한 모델 파일(model.pth, model_state_dict.pth)을 분석해 복원한 구조입니다.

    입력: 흑백(1채널) 128 x 128 X-ray 이미지
    conv : Conv2d(1→16, 3x3, padding=1) → ReLU → MaxPool(2)     # 128 → 64
           Conv2d(16→32, 3x3, padding=1) → ReLU → MaxPool(2)    # 64  → 32
    fc   : Flatten (32 x 32 x 32 = 32768) → Linear(32768 → 2)
    출력: [정상, 폐렴] 로짓 2개 (softmax는 worker/model.py에서 적용)

- model.pth 는 노트북의 `__main__.SimpleCNN` 클래스로 저장되어 있어,
  이 파일에 같은 이름의 클래스가 있어야 로드됩니다. (__all__에 등록)
- model_state_dict.pth 는 build_model()로 구조를 만든 뒤 가중치를 넣습니다.
- 레이어 이름(conv, fc)과 순서는 저장된 가중치의 키(conv.0.weight, fc.1.weight 등)와
  정확히 같아야 하므로 바꾸지 마세요.
"""

import torch.nn as nn

INPUT_SIZE = 128
IN_CHANNELS = 1
NUM_CLASSES = 2


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(IN_CHANNELS, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * (INPUT_SIZE // 4) * (INPUT_SIZE // 4), NUM_CLASSES),
        )

    def forward(self, x):
        return self.fc(self.conv(x))


# model.pth(구조 포함 파일)를 불러올 때 __main__ 에 등록할 클래스 목록
__all__ = ["SimpleCNN"]


def build_model() -> nn.Module:
    """model_state_dict.pth 를 불러올 때 사용할 빈 모델"""
    return SimpleCNN()
