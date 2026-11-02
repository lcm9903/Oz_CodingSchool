"""
폐렴 예측 AI 모델을 메모리에 올려두고, X-ray 이미지로 예측하는 모듈.

사용 흐름
    1) 노션의 모델 파일(model.pth 또는 model_state_dict.pth)을 worker/models/ 에 복사한다.
    2) 서버 시작 시(app/main.py의 lifespan) predictor.load() 가 한 번 호출되어 모델이 메모리에 올라간다.
    3) 예측 API가 호출되면 predictor.predict(이미지경로) 로 결과를 얻는다.

지원하는 모델 파일 형식
    - 모델 구조 포함 파일 (torch.save(model, ...))           → 그대로 로드
    - TorchScript 파일 (torch.jit.save)                      → 그대로 로드
    - state_dict 파일 (torch.save(model.state_dict(), ...))  → worker/architecture.py 의
      build_model()로 구조를 만든 뒤 가중치를 넣는다.

※ 모델 구조 포함 파일이 노트북(__main__)에서 정의한 클래스로 저장되었다면,
   그 클래스 정의를 worker/architecture.py 에 그대로 옮겨 적어야 로드된다.
"""

import logging
import sys
from pathlib import Path

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class ModelNotReadyError(RuntimeError):
    """모델 파일이 없거나 로드에 실패했을 때 발생"""


class PneumoniaPredictor:
    def __init__(
        self,
        model_path: Path,
        model_name: str,
        image_size: int = 224,
        threshold: float = 0.5,
        normalize: str = "none",
    ):
        self.model_path = Path(model_path)
        self.model_name = model_name
        self.image_size = image_size
        self.threshold = threshold
        self.normalize = normalize  # "none" | "imagenet" (학습 시 전처리와 맞출 것)

        self._model = None
        self._torch = None
        self._in_channels = 3
        self._output_is_probability = False
        self.load_error: str | None = None

    # ------------------------------------------------------------------ 로드
    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        """모델을 메모리에 올린다. 실패해도 서버는 뜨고, 예측 API만 503을 반환한다."""
        try:
            import torch
        except ImportError:
            self.load_error = "PyTorch(torch)가 설치되어 있지 않습니다. `uv sync`로 설치해주세요."
            logger.warning(self.load_error)
            return

        if not self.model_path.exists():
            self.load_error = f"모델 파일이 없습니다: {self.model_path}"
            logger.warning(self.load_error)
            return

        self._torch = torch
        try:
            model = self._load_model_object(torch)
            model.eval()
            self._in_channels = self._detect_in_channels(model, torch)
            self._output_is_probability = self._ends_with_activation(model, torch)
            self._model = model
            self.load_error = None
            logger.info(
                "AI 모델 로드 완료: %s (입력 채널=%d)", self.model_path.name, self._in_channels
            )
        except Exception as exc:  # noqa: BLE001 - 어떤 이유로든 실패하면 원인을 기록
            self.load_error = f"모델 로드 실패: {exc}"
            logger.exception(self.load_error)

    def _load_model_object(self, torch):
        # 1) TorchScript 시도
        try:
            return torch.jit.load(str(self.model_path), map_location="cpu")
        except Exception:  # noqa: BLE001
            pass

        # 2) 노트북에서 저장된 사용자 정의 클래스를 찾을 수 있도록 __main__에 등록
        from worker import architecture

        main_module = sys.modules["__main__"]
        for name in getattr(architecture, "__all__", []):
            setattr(main_module, name, getattr(architecture, name))

        loaded = torch.load(self.model_path, map_location="cpu", weights_only=False)

        # 3) 모델 구조 포함 파일
        if isinstance(loaded, torch.nn.Module):
            return loaded

        # 4) state_dict 파일 (체크포인트 dict 안에 들어있는 경우도 처리)
        if isinstance(loaded, dict):
            state_dict = loaded.get("state_dict") or loaded.get("model_state_dict") or loaded
            model = architecture.build_model()
            model.load_state_dict(state_dict)
            return model

        raise TypeError(f"지원하지 않는 모델 파일 형식입니다: {type(loaded)}")

    @staticmethod
    def _detect_in_channels(model, torch) -> int:
        """첫 번째 Conv2d 레이어의 입력 채널 수(1=흑백, 3=RGB)를 찾는다."""
        for module in model.modules():
            if isinstance(module, torch.nn.Conv2d):
                return module.in_channels
        return 3

    @staticmethod
    def _ends_with_activation(model, torch) -> bool:
        """모델 마지막 레이어가 Sigmoid/Softmax면 출력이 이미 확률이다."""
        last = None
        for module in model.modules():
            if not list(module.children()):
                last = module
        return isinstance(last, (torch.nn.Sigmoid, torch.nn.Softmax))

    # ------------------------------------------------------------------ 예측
    def _preprocess(self, image_path: Path):
        mode = "L" if self._in_channels == 1 else "RGB"
        image = Image.open(image_path).convert(mode)
        image = image.resize((self.image_size, self.image_size))

        array = np.asarray(image, dtype=np.float32) / 255.0
        if array.ndim == 2:  # 흑백: (H, W) -> (H, W, 1)
            array = array[:, :, None]
        if self.normalize == "imagenet" and array.shape[2] == 3:
            array = (array - IMAGENET_MEAN) / IMAGENET_STD

        tensor = self._torch.from_numpy(array.transpose(2, 0, 1).copy())  # (C, H, W)
        return tensor.unsqueeze(0)  # (1, C, H, W)

    def predict(self, image_path: Path) -> tuple[bool, float]:
        """
        Returns:
            (폐렴 여부, confidence)
            confidence는 '예측한 클래스'에 대한 확신도(0~100, 소수점 2자리)이다.
        """
        if not self.is_ready:
            raise ModelNotReadyError(self.load_error or "AI 모델이 준비되지 않았습니다.")

        torch = self._torch
        with torch.no_grad():
            output = self._model(self._preprocess(image_path)).flatten()

        if output.numel() == 1:  # 출력 1개: 폐렴 확률(또는 로짓)
            value = output[0]
            prob = value if self._output_is_probability else torch.sigmoid(value)
        else:  # 출력 2개: [정상, 폐렴]
            probs = output if self._output_is_probability else torch.softmax(output, dim=0)
            prob = probs[1]

        pneumonia_prob = float(prob)
        is_pneumonia = pneumonia_prob >= self.threshold
        confidence = pneumonia_prob if is_pneumonia else 1.0 - pneumonia_prob
        return is_pneumonia, round(confidence * 100, 2)


def _build_default_predictor() -> PneumoniaPredictor:
    from app.core.config import settings

    return PneumoniaPredictor(
        model_path=settings.AI_MODEL_PATH,
        model_name=settings.AI_MODEL_NAME,
        image_size=settings.AI_IMAGE_SIZE,
        threshold=settings.AI_THRESHOLD,
        normalize=settings.AI_NORMALIZE,
    )


# 앱 전체에서 공유하는 단일 인스턴스 (모델을 한 번만 메모리에 올리기 위함)
predictor = _build_default_predictor()
