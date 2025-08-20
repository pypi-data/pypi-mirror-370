
import os
from PyQt5.QtCore import QLibraryInfo, QCoreApplication

def fix_qt_plugin_paths(prefer_platform: str | None = None) -> None:
    """
    Força o Qt a usar os plugins do PyQt5 e remove caminhos herdados do cv2.
    Chame isso ANTES de criar o QApplication.
    """
    # 1) Limpa variáveis que podem apontar para plugins errados
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    os.environ.pop("QT_PLUGIN_PATH", None)

    # 2) Define plataforma padrão (ajude o usuário)
    if prefer_platform:
        os.environ["QT_QPA_PLATFORM"] = prefer_platform
    else:
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")  # ou 'wayland' conforme seu público

    # 3) Remove library paths que contenham plugins do cv2
    for p in list(QCoreApplication.libraryPaths()):
        if "cv2/qt/plugins" in p:
            QCoreApplication.removeLibraryPath(p)

    # 4) Garante o diretório oficial de plugins do PyQt5
    pyqt_plugins = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    QCoreApplication.addLibraryPath(pyqt_plugins)

def assert_not_using_cv2_plugins() -> None:
    """
    Se ainda houver um caminho de plugins do cv2, emite uma dica amigável.
    """
    for p in QCoreApplication.libraryPaths():
        if "cv2/qt/plugins" in p:
            raise RuntimeError(
                "Qt ainda está apontando para plugins do OpenCV (cv2/qt/plugins). "
                "Instale apenas 'opencv-python-headless' e remova resíduos:\n"
                "  pip uninstall -y opencv-python opencv-contrib-python\n"
                "  # apague a pasta 'cv2' do seu site-packages deste venv\n"
                "  pip install --no-cache-dir opencv-python-headless PyQt5\n"
            )
