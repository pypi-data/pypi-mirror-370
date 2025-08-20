from meerk40t.gui.scene.sceneconst import ORIENTATION_CENTERED, ORIENTATION_HORIZONTAL
from meerk40t.gui.scene.widget import Widget


class ToolbarWidget(Widget):
    def __init__(self, scene, left, top):
        Widget.__init__(self, scene, left, top, left, top)
        self.properties = ORIENTATION_CENTERED | ORIENTATION_HORIZONTAL
