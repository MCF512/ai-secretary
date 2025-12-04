from pathlib import Path

from classes import SpeechToTextModel


def main() -> None:
    model = SpeechToTextModel(language="ru")

    audio_path = Path("sample_ru.wav")
    if not audio_path.exists():
        raise FileNotFoundError(
            "Файл sample_ru.wav не найден. "
        )

    text = model.predict(str(audio_path))
    print("Распознанный текст:")
    print(text)


if __name__ == "__main__":
    main()


