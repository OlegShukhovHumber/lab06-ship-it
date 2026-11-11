import json
from importlib.metadata import version
from pathlib import Path

import sklearn

ROOT = Path(__file__).parent.parent


def read_model_info():
    return json.loads((ROOT / "models" / "model_info.json").read_text())


def read_requirements():
    return (ROOT / "requirements.txt").read_text(encoding="utf-8")


def read_readme_settings():
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    markers = [i for i, line in enumerate(lines) if line.strip() == "---"]
    assert len(markers) >= 2
    settings = {}
    for line in lines[markers[0] + 1 : markers[1]]:
        if ":" in line:
            key, value = line.split(":", 1)
            settings[key.strip()] = value.strip().strip('"').strip("'")
    return settings


def test_sklearn_version_matches_model_info():
    assert sklearn.__version__ == read_model_info()["sklearn_version"]


def test_sklearn_version_matches_requirements_pin():
    pins = [
        line.strip()
        for line in read_requirements().splitlines()
        if line.strip().lower().startswith("scikit-learn==")
    ]
    assert len(pins) == 1, "requirements.txt must pin scikit-learn exactly 1 time."
    assert pins[0].split("==")[1] == sklearn.__version__


def test_gradio_not_in_requirements():
    assert "gradio" not in read_requirements().lower()


def test_readme_sdk_version_matches_installed_gradio():
    assert read_readme_settings()["sdk_version"] == version("gradio")


def test_readme_app_file_exists():
    app_file = read_readme_settings()["app_file"]
    assert (ROOT / app_file).is_file()
