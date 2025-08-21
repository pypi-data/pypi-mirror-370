from .imports import *
# ─── Size handlers ─────────────────────────────────────────────
def _on_main_size_changed(self, _):
    w, h = self.main_w_spin.value(), self.main_h_spin.value()
    logger.info("_on_main_size_changed")
    self.main_size = QtCore.QSize(w, h)
    # keep it as a minimum, not a fixed size, so it can grow
    self.image_preview.setMinimumSize(self.main_size)
    if getattr(self, "_last_image", None):
        self._show_image(self._last_image)

def _on_collapsed_changed(self, v):
    self.collapsed_thumb_size = v
    logger.info("_on_collapsed_changed")
    self._refresh()

def _on_expanded_changed(self, v):
    self.expanded_thumb_size = v
    logger.info("_on_expanded_changed")
    self.thumb_tree.setIconSize(QtCore.QSize(v, v))
    self.expanded_scroll.setFixedHeight(v + 20)
    self._refresh()

def _refresh(self):
    idx = self.tree.currentIndex()
    logger.info("_refresh")
    if idx.isValid():
        self.on_folder_selected(idx)

# ─── Folder selection ──────────────────────────────────────────
def on_folder_selected(self, idx):
    try:
        def get_all_dir(obj):
            dir_path=obj
            if type(obj) == type(idx):
                model_path = self.model.filePath(obj)
                dir_path = Path(model_path)
            else:
                dir_path = Path(obj)
                
            return dir_path,str(dir_path)
        folder,folder_str = get_all_dir(idx)
        logger.info(f"_populate_thumb_tree: {folder_str}")
        logger.info("on_folder_selected")
        self.current_dir = folder
        # Important: don't auto-rename on selection to avoid re-entrancy/IO surprises.
        # If you want it, run _renumber_images in a worker and refresh after.

        # rebuild both views
        self._populate_thumb_tree(folder)
        self._populate_expanded_strip(folder)
        
    except Exception as e:
        logger.exception("iterdir failed for %s", p)
        return []
    
            

# ─── Collapsible tree ──────────────────────────────────────────
def _safe_list(self, p: Path):
    try:
        return list(p.iterdir())
    except Exception as e:
        logger.exception("iterdir failed for %s", p)
        return []
# In DirectoryImageViewer
def _populate_thumb_tree(self, folder: Path):
    try:
        folder_str = str(folder)
        if folder_str in self.displayed_directories:
            return
        self.thumb_tree.clear()
        self.scanner_thread = DirScanner(folder)
        self.scanner_thread.dir_processed.connect(self._add_collapsible_node_threaded)
        self.scanner_thread.finished.connect(self._on_scanning_finished)
        self.scanner_thread.start()
    except Exception as e:
        print(f"{e}")        
def _populate_thumb_tree(self, folder: Path):
    try:
        folder_str = str(folder)
        if folder_str in self.displayed_directories:
            return  # Already displayed
  
        subdirs = [folder_str]
        subdirs += DIR_MGR.get_subdirs(folder_str)
        for folder in subdirs:
            self.displayed_directories.append(folder_str)
            #self.thumb_tree.clear()  # Clear previous content if needed
            # Start threaded scanning
            self.scanner_thread = DirScanner(folder)
            self.scanner_thread.dir_processed.connect(self.on_folder_selected)
            self.scanner_thread.dir_processed.connect(self._add_collapsible_node_threaded)
            self.scanner_thread.finished.connect(self._on_scanning_finished)
            self.scanner_thread.start()
    except Exception as e:
        print(f"{e}")            
def _add_collapsible_node_threaded(self, name: str, directory: str, files: list):
    # This runs in main thread via signal
    try:
        self._add_collapsible_node(name, Path(directory), files)
        self.displayed_directories.append(directory)
        QtWidgets.QApplication.processEvents()  # Update UI in real time
    except Exception as e:
        logger.error(f"Error adding node for {directory}: {e}")

def _on_scanning_finished(self):
    try:
        logger.info("Scanning finished")
        self.scanner_thread = None  # Clean up reference
        # root images
        #root_imgs = sorted(p for p in self._safe_list(folder)if p.is_file() and p.suffix.lower() in self.EXTS)
        #if files:
        #    self._add_collapsible_node(folder.name or "Root", folder, files)
    except Exception as e:
        print(f"{e}")  
    
def _add_collapsible_node(self, title, dirpath: Path, imgs):
    logger.info("_add_collapsible_node")
    try:
        node = QtWidgets.QTreeWidgetItem(self.thumb_tree)
        
        node.setData(0, QtCore.Qt.ItemDataRole.UserRole, {"dir": str(dirpath), "loaded": False})

        # Build a light collapsed preview strip (icons; no full-size decode)
        cont = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(cont)
        hl.setContentsMargins(2, 2, 2, 2)
        hl.setSpacing(4)

        lbl = QtWidgets.QLabel(f"<b>{title}</b>")
        hl.addWidget(lbl)

        preview_cap = 1100  # keep it snappy
        for img in imgs[:preview_cap]:
            thumb = QtWidgets.QLabel()
            thumb.setFixedSize(self.collapsed_thumb_size, self.collapsed_thumb_size)
            thumb.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            thumb.setStyleSheet("border:1px solid #ccc; background:#eee;")
            icon = QtGui.QIcon(str(img))
            pm = icon.pixmap(self.collapsed_thumb_size, self.collapsed_thumb_size)
            thumb.setPixmap(pm)
            thumb.setProperty("path", str(img))
            thumb.mousePressEvent = (lambda ev, p=str(img): self._show_from_thumb(p))
            hl.addWidget(thumb)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        self.expanded_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.expanded_scroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setWidget(cont)
        scroll.setFixedHeight(self.collapsed_thumb_size + 20)

        self.thumb_tree.setItemWidget(node, 0, scroll)
    except Exception as e:
        print(f"{e}")
def on_item_expanded(self, item):
    data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
    logger.info("on_item_expanded")

    # Only parent nodes (dict payload) are expandable. Children carry a string path.
    if not isinstance(data, dict):
        return

    if data.get("loaded"):
        return

    dir_path = Path(data.get("dir", ""))
    if not dir_path.exists():
        data["loaded"] = True
        item.setData(0, QtCore.Qt.ItemDataRole.UserRole, data)
        return

    try:
        pics = sorted(
            p for p in dir_path.iterdir()
            if p.is_file() and p.suffix.lower() in self.EXTS
        )
    except Exception:
        logger.exception("Failed to list %s", dir_path)
        pics = []

    for img in pics:
        ch = QtWidgets.QTreeWidgetItem(item)
        ch.setText(0, img.name)
        ch.setIcon(0, QtGui.QIcon(str(img)))  # cheap icon; avoids full decode
        ch.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(img))

    # Remove the heavy inline preview widget once expanded
    self.thumb_tree.setItemWidget(item, 0, None)

    data["loaded"] = True
    item.setData(0, QtCore.Qt.ItemDataRole.UserRole, data)

def on_tree_thumb_clicked(self, item, _):
    logger.info("on_tree_thumb_clicked")
    try:
        val = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
       
        if isinstance(val, str):
            self._show_image(val)
            self._select_index(val)
    except Exception as e:
        print(f"{e}")
# ─── Expanded strip ────────────────────────────────────────────
def _populate_expanded_strip(self, folder: Path):
    logger.info("_populate_expanded_strip")
    try:
        # clear existing widgets
        for i in reversed(range(self.expanded_layout.count())):
            w = self.expanded_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        try:
            imgs = sorted(
                p for p in folder.iterdir()
                if p.is_file() and p.suffix.lower() in self.EXTS
            )
        except Exception:
            logger.exception("iterdir failed for %s", folder)
            imgs = []

        self.current_images = [str(p) for p in imgs]
        self.current_index = 0

        for path in self.current_images:
            lbl = QtWidgets.QLabel()
            lbl.setFixedSize(self.expanded_thumb_size, self.expanded_thumb_size)
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("border:1px solid #ccc; background:#eee;")
            icon = QtGui.QIcon(path)
            pm = icon.pixmap(self.expanded_thumb_size, self.expanded_thumb_size)
            if not pm.isNull():
                lbl.setPixmap(pm)
            lbl.setProperty("path", path)
            lbl.mousePressEvent = (lambda ev, p=path: self._show_image(p))
            self.expanded_layout.addWidget(lbl)

        if self.current_images:
            self._show_image(self.current_images[0])
    except Exception as e:
        print(f"{e}")
# ─── Image viewing helpers ─────────────────────────────────────
def _show_from_thumb(self, path: str):
    logger.info("_show_from_thumb")
    try:
        self._select_index(path)

        
        self._show_image(path)
    except Exception as e:
        print(f"{e}")
def _select_index(self, path: str):
        logger.info("_select_index")
        try:
            
            self.current_index = self.current_images.index(path)
        except ValueError:
            self.current_index = 0
        except Exception as e:
            print(f"{e}")
def _show_image(self, path: str):
    # store last path for resize redraw
    try:
        self._last_image = path
        pm = QtGui.QPixmap(path)
        if not pm.isNull():
            self.image_preview.setPixmap(
                pm.scaled(self.image_preview.size(),
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                          QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.image_preview.setText("Failed to load image")
    except Exception as e:
        print(f"{e}")
# ─── Slideshow / navigation ────────────────────────────────────
def next_image(self):
    logger.info("next_image")
    try:
        if not self.current_images:
            return
        
        self.current_index = (self.current_index + 1) % len(self.current_images)
        self._show_image(self.current_images[self.current_index])
    except Exception as e:
        print(f"{e}")
def prev_image(self):
    logger.info("prev_image")
    try:
        if not self.current_images:
            return
        
        self.current_index = (self.current_index - 1) % len(self.current_images)
        self._show_image(self.current_images[self.current_index])
    except Exception as e:
        print(f"{e}")
def toggle_slideshow(self):
    try:
        if self.slideshow_timer.isActive():
            logger.info("toggle_slideshow")
            self.slideshow_timer.stop()
            self.play_btn.setText("▶ Play")
        else:
            self.slideshow_timer.start()
            self.play_btn.setText("⏸ Pause")
    except Exception as e:
        print(f"{e}")
# ─── Open folder ───────────────────────────────────────────────
def open_folder(self):
    try:
        if self.current_dir:
            logger.info("open_folder")
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.current_dir)))
    except Exception as e:
        print(f"{e}")
# ─── Renaming / undo ───────────────────────────────────────────
def undo_last_renaming(self):
    try:
        idx = self.tree.currentIndex()
        logger.info("undo_last_renaming")
        folder = Path(self.model.filePath(idx))
        log = folder / "rename_log.json"
        if not log.exists():
            QtWidgets.QMessageBox.warning(self, "Undo Failed", "No rename log found.")
            return
        try:
            mapping = json.loads(log.read_text(encoding='utf-8'))
            for new, old in mapping.items():
                pnew = folder / new
                pold = folder / old
                if pnew.exists():
                    pnew.rename(pold)
            log.unlink()
            QtWidgets.QMessageBox.information(self, "Undo Complete", "Restored names.")
            self.on_folder_selected(idx)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Undo Error", str(e))
    except Exception as e:
        print(f"{e}")
def _renumber_images(self, folder: Path):
    try:
        if not self.renumber_cb.isChecked():
            return
        logger.info("_renumber_images")
        imgs = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in self.EXTS)
        prefix = (self.prefix_inp.text().strip() if self.prefix_cb.isChecked() else "") or folder.name
        log = {}
        for i, old in enumerate(imgs, 1):
            num = f"{i:03d}"
            new = f"{prefix}_{num}{old.suffix.lower()}"
            pnew = folder / new
            if old.name != new:
                try:
                    old.rename(pnew)
                    log[new] = old.name
                except Exception:
                    pass
        if log:
            (folder / "rename_log.json").write_text(json.dumps(log, indent=2), encoding='utf-8')
            QtWidgets.QMessageBox.information(self, "Renamed", f"Renamed {len(log)} files.")
    except Exception as e:
        print(f"{e}")
    
