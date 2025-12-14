# Try to use the new Kivy UI if available, otherwise fall back to the legacy PyQt UI.
try:
    from ui.kivy_ui import launch_ui as launch_kivy_ui
    UI_BACKEND = 'kivy'
except Exception as e:
    launch_kivy_ui = None
    UI_BACKEND = None
    _kivy_import_error = e

if UI_BACKEND == 'kivy' and launch_kivy_ui:
    def launch_ui():
        return launch_kivy_ui()
else:
    try:
        from ui.gatewise_ui import launch_ui as launch_pyqt_ui
        UI_BACKEND = 'pyqt'
    except Exception as e:
        launch_pyqt_ui = None
        _pyqt_import_error = e

    def launch_ui():
        if launch_pyqt_ui:
            print('[INFO] Kivy not available, falling back to PyQt UI')
            return launch_pyqt_ui()
        else:
            print('[ERROR] No UI backend available.')
            print('Kivy import error:')
            print(repr(_kivy_import_error))
            print('PyQt import error:')
            print(repr(_pyqt_import_error))

if __name__ == "__main__":
    launch_ui()
