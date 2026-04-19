from aqt import mw
from aqt.qt import *

class TagConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Tag-Auswahl Konfiguration")
        self.resize(400, 500)
        
        # Layout
        self.layout = QVBoxLayout(self)
        
        # Der Baum
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Tags auswählen")
        self.layout.addWidget(self.tree)
        
        # Buttons (Abbrechen / Speichern)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        self.setup_tree()

    def setup_tree(self):
        # Alle Tags von Anki holen
        all_tags = mw.col.tags.all()
        # Aktuelle Config laden, um bereits gewählte Tags anzuhaken
        config = mw.addonManager.getConfig(__name__) or {}
        selected_tags = config.get("selected_tags", [])

        nodes = {}
        for tag in all_tags:
            parts = tag.split("::")
            parent = self.tree.invisibleRootItem()
            
            path = ""
            for i, part in enumerate(parts):
                path = f"{path}::{part}" if path else part
                if path not in nodes:
                    item = QTreeWidgetItem(parent)
                    item.setText(0, part)
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                    # Falls der Tag in der Config steht, anhaken
                    if path in selected_tags:
                        item.setCheckState(0, Qt.CheckState.Checked)
                    
                    item.setData(0, Qt.ItemDataRole.UserRole, path)
                    nodes[path] = item
                parent = nodes[path]

    def get_selected_tags(self):
        """Geht den Baum durch und gibt alle angehakten Tags zurück."""
        selected = []
        it = QTreeWidgetItemIterator(self.tree)
        while it.value():
            item = it.value()
            if item.checkState(0) == Qt.CheckState.Checked:
                selected.append(item.data(0, Qt.ItemDataRole.UserRole))
            it += 1
        return selected

def start_config_gui():
    dialog = TagConfigDialog(mw)
    if dialog.exec():
        new_tags = dialog.get_selected_tags()
        # Speichern in der config.json
        config = mw.addonManager.getConfig(__name__) or {}
        config["selected_tags"] = new_tags
        mw.addonManager.writeConfig(__name__, config)
        print("Config gespeichert:", new_tags)

# Den Config-Button in der Addon-Liste umleiten
mw.addonManager.setConfigAction(__name__, start_config_gui)
