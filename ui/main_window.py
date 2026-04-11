from aqt.qt import *
from aqt import mw


HIDDEN_TAGS = ["!delete", "§Anki_AG"]


class SelectionWindow(QDialog):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw  
        self.setWindowTitle("Auswahlstapel Erlangen")
        self.resize(350, 320)
        self.init_ui()

    # -----------------------
    # CONFIG
    # -----------------------

    def _config_path(self):
        import os
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(addon_dir, "user_config.json")

    def _load_config(self):
        import json
        try:
            with open(self._config_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self, config):
        import json
        with open(self._config_path(), "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    # -----------------------
    # ... rest des Codes

    #------------------------------
    # Letzte angewählten Tags laden
    #------------------------------

    def get_expanded_tags(self, tree):
        expanded = []

        def recurse(item):
            if item.isExpanded():
                expanded.append(item.data(0, Qt.ItemDataRole.UserRole))
            for i in range(item.childCount()):
                recurse(item.child(i))

        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            recurse(root.child(i))

        return expanded


    def restore_expanded_state(self, tree, expanded_tags):
        def recurse(item):
            tag = item.data(0, Qt.ItemDataRole.UserRole)

            if tag in expanded_tags:
                tree.expandItem(item)

            for i in range(item.childCount()):
                recurse(item.child(i))

        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            recurse(root.child(i))

    # -----------------------
    # UI
    # -----------------------

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tabs.addTab(self.build_name_tab(), "Name")
        self.tabs.addTab(self.build_tag1_tab(), "Tag 1")
        self.tabs.addTab(self.build_filter1_tab(), "Filter 1")
        self.tabs.addTab(self.build_tag2_tab(), "Tag 2")
        self.tabs.addTab(self.build_filter2_tab(), "Filter 2")

        self.create_button = QPushButton("Auswahlstapel erstellen")
        self.create_button.clicked.connect(self.create_filtered_deck)
        main_layout.addWidget(self.create_button)

    # -----------------------
    # NAME TAB
    # -----------------------

    def build_name_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)

        layout.addWidget(QLabel("Name des Auswahlstapels:"))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Erlangen Auswahlstapel")
        self.name_input.setText("Erlangen Auswahlstapel")

        layout.addWidget(self.name_input)
        layout.addStretch()

        return widget

    # -----------------------
    # TAG TAB
    # -----------------------

    def build_tag1_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.tree1 = QTreeWidget()
        self.tree1.setHeaderHidden(True)
        self.tree1.setUniformRowHeights(True)

        layout.addWidget(self.tree1)

        self.load_erlangen_tags(self.tree1)

        return widget

    def build_filter1_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.filter1_due = QCheckBox("Fällige Karten (is:due)")
        self.filter1_new = QCheckBox("Neue Karten (is:new)")
        self.filter1_resched_cb = QCheckBox("Reschedule beim Rebuild")

        layout.addWidget(self.filter1_due)
        layout.addWidget(self.filter1_new)
        layout.addWidget(self.filter1_resched_cb)

        # -------------------
        # Logik OR/AND
        layout.addSpacing(6)
        layout.addWidget(QLabel("Mehrere Tags kombinieren mit:"))
        self.filter1_logic_combo = QComboBox()
        self.filter1_logic_combo.addItems(["OR (empfohlen)", "AND"])
        layout.addWidget(self.filter1_logic_combo)
        # -------------------

        layout.addSpacing(6)
        layout.addWidget(QLabel("Max. Kartenanzahl"))
        self.filter1_limit = QSpinBox()
        self.filter1_limit.setMinimum(1)
        self.filter1_limit.setMaximum(9999)
        self.filter1_limit.setValue(100)
        layout.addWidget(self.filter1_limit)

        layout.addStretch()
        return widget


    def build_tag2_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.tree2 = QTreeWidget()
        self.tree2.setHeaderHidden(True)
        self.tree2.setUniformRowHeights(True)

        layout.addWidget(self.tree2)

        self.load_erlangen_tags(self.tree2)

        return widget

    def build_filter2_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.filter2_due = QCheckBox("Fällige Karten (is:due)")
        self.filter2_new = QCheckBox("Neue Karten (is:new)")
        self.filter2_resched_cb = QCheckBox("Reschedule beim Rebuild")

        layout.addWidget(self.filter2_due)
        layout.addWidget(self.filter2_new)
        layout.addWidget(self.filter2_resched_cb)

        # -------------------
        # Logik OR/AND
        layout.addSpacing(6)
        layout.addWidget(QLabel("Mehrere Tags kombinieren mit:"))
        self.filter2_logic_combo = QComboBox()
        self.filter2_logic_combo.addItems(["OR (empfohlen)", "AND"])
        layout.addWidget(self.filter2_logic_combo)
        # -------------------

        layout.addSpacing(6)
        layout.addWidget(QLabel("Max. Kartenanzahl"))
        self.filter2_limit = QSpinBox()
        self.filter2_limit.setMinimum(1)
        self.filter2_limit.setMaximum(9999)
        self.filter2_limit.setValue(100)
        layout.addWidget(self.filter2_limit)

        layout.addStretch()
        return widget

    # -----------------------
    # LOAD TAGS
    # -----------------------

    def load_erlangen_tags(self, tree_widget):
        tree_widget.clear()

        all_tags = self.mw.col.tags.all()
        prefix = "Anki_Erlangen"

        tree_dict = {}

        for tag in all_tags:
            if not tag.startswith(prefix + "::"):
                continue
            if any(hidden in tag for hidden in HIDDEN_TAGS):
                continue

            clean_tag = tag[len(prefix) + 2:]  # "::" mitentfernen
            parts = clean_tag.split("::")

            current = tree_dict
            for part in parts:
                current = current.setdefault(part, {})

        self.build_tree_from_dict(tree_dict, tree_widget, prefix=prefix)

        config = self._load_config()

        if tree_widget == self.tree1:
            expanded = config.get("expanded_tags_1", [])
        else:
            expanded = config.get("expanded_tags_2", [])

        self.restore_expanded_state(tree_widget, expanded)

    def build_tree_from_dict(self, tree_dict, tree_widget, prefix="Anki_Erlangen"):
        tree_widget.clear()

        def add_items(parent, dictionary, parent_path):
            for key, value in dictionary.items():
                full_path = parent_path + "::" + key
                item = QTreeWidgetItem([key])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                item.setData(0, Qt.ItemDataRole.UserRole, full_path)
                parent.addChild(item)
                add_items(item, value, full_path)

        for key, value in tree_dict.items():
            full_path = prefix + "::" + key
            top = QTreeWidgetItem([key])
            top.setFlags(top.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            top.setCheckState(0, Qt.CheckState.Unchecked)
            top.setData(0, Qt.ItemDataRole.UserRole, full_path)
            tree_widget.addTopLevelItem(top)
            add_items(top, value, full_path)


    # -----------------------
    # CHECKBOX LOGIC
    # -----------------------

    def handle_item_change(self, item, column):
        self.tree.blockSignals(True)

        state = item.checkState(0)

        for i in range(item.childCount()):
            item.child(i).setCheckState(0, state)

        self.update_parents(item)

        self.tree.blockSignals(False)

    def update_parents(self, item):
        parent = item.parent()
        if not parent:
            return

        checked = 0
        partial = 0

        for i in range(parent.childCount()):
            child_state = parent.child(i).checkState(0)
            if child_state == Qt.CheckState.Checked:
                checked += 1
            elif child_state == Qt.CheckState.PartiallyChecked:
                partial += 1

        if checked == parent.childCount():
            parent.setCheckState(0, Qt.CheckState.Checked)
        elif checked > 0 or partial > 0:
            parent.setCheckState(0, Qt.CheckState.PartiallyChecked)
        else:
            parent.setCheckState(0, Qt.CheckState.Unchecked)

        self.update_parents(parent)

    # -----------------------
    # GET TAGS
    # -----------------------

    def get_checked_tags(self, tree_widget):
        checked_tags = []

        def recurse(item, path):
            if item.checkState(0) == Qt.CheckState.Checked:
                full_tag = "Anki_Erlangen::" + "::".join(path + [item.text(0)])
                checked_tags.append(full_tag)

            for i in range(item.childCount()):
                recurse(item.child(i), path + [item.text(0)])

        for i in range(tree_widget.topLevelItemCount()):
            recurse(tree_widget.topLevelItem(i), [])

        return checked_tags

    #-----------------------
    # geöffnete Tags speichern
    #-----------------------

    def closeEvent(self, event):
        config = self._load_config()
        config["expanded_tags_1"] = self.get_expanded_tags(self.tree1)
        config["expanded_tags_2"] = self.get_expanded_tags(self.tree2)
        self._save_config(config)
        event.accept()

    # -----------------------
    # CREATE FILTERED DECK
    # -----------------------

    def create_filtered_deck(self):

        deck_name = self.name_input.text().strip()
        if not deck_name:
            deck_name = "Erlangen Auswahlstapel"

        # =========================
        # TERM 1
        # =========================
        selected_tags1 = self.get_checked_tags(self.tree1)
        search_query1 = ""

        if selected_tags1:
            joiner1 = " OR " if self.filter1_logic_combo.currentIndex() == 0 else " AND "
            tag_query1 = joiner1.join([f'tag:"{tag}"' for tag in selected_tags1])
            search_query1 = f"({tag_query1})"

        if self.filter1_due.isChecked() and self.filter1_new.isChecked():
            search_query1 += " (is:due OR is:new)"
        elif self.filter1_due.isChecked():
            search_query1 += " is:due"
        elif self.filter1_new.isChecked():
            search_query1 += " is:new"

        limit1 = self.filter1_limit.value()


        # =========================
        # TERM 2
        # =========================
        selected_tags2 = self.get_checked_tags(self.tree2)
        search_query2 = ""

        if selected_tags2:
            joiner2 = " OR " if self.filter2_logic_combo.currentIndex() == 0 else " AND "
            tag_query2 = joiner2.join([f'tag:"{tag}"' for tag in selected_tags2])
            search_query2 = f"({tag_query2})"

        if self.filter2_due.isChecked() and self.filter2_new.isChecked():
            search_query2 += " (is:due OR is:new)"
        elif self.filter2_due.isChecked():
            search_query2 += " is:due"
        elif self.filter2_new.isChecked():
            search_query2 += " is:new"

        limit2 = self.filter2_limit.value()


        # =========================
        # Deck erstellen / laden
        # =========================
        if self.mw.col.decks.by_name(deck_name):
            deck = self.mw.col.decks.by_name(deck_name)
        else:
            self.mw.col.decks.new_filtered(deck_name)
            deck = self.mw.col.decks.by_name(deck_name)

        # =========================
        # TERMS setzen
        # =========================
        terms = []

        if search_query1.strip():
            terms.append([search_query1.strip(), limit1, 0])

        if search_query2.strip():
            terms.append([search_query2.strip(), limit2, 0])

        if not terms:
            return  # nichts ausgewählt

        deck["terms"] = terms
        deck["resched"] = self.filter1_resched_cb.isChecked() or self.filter2_resched_cb.isChecked()

        self.mw.col.decks.save(deck)
        self.mw.col.sched.rebuild_filtered_deck(deck["id"])

        self.mw.reset()

        config = self._load_config()
        config["expanded_tags_1"] = self.get_expanded_tags(self.tree1)
        config["expanded_tags_2"] = self.get_expanded_tags(self.tree2)
        self._save_config(config)
        
        self.accept()


