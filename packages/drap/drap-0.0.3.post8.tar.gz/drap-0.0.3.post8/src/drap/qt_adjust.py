
import os
from PyQt5.QtCore import QLibraryInfo, QCoreApplication

def fix_qt_plugin_paths(prefer_platform: str | None = None) -> None:

    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    os.environ.pop("QT_PLUGIN_PATH", None)

    if prefer_platform:
        os.environ["QT_QPA_PLATFORM"] = prefer_platform
    else:
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")  # ou 'wayland' conforme seu público


    for p in list(QCoreApplication.libraryPaths()):
        if "cv2/qt/plugins" in p:
            QCoreApplication.removeLibraryPath(p)


    pyqt_plugins = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    QCoreApplication.addLibraryPath(pyqt_plugins)

def assert_not_using_cv2_plugins() -> None:

    for p in QCoreApplication.libraryPaths():
        if "cv2/qt/plugins" in p:
            raise RuntimeError(
                "Error"
            )
