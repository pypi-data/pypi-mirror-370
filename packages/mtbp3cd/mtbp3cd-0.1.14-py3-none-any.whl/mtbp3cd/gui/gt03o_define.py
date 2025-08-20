#  Copyright (C) 2025 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>

import os
import pandas as pd
from PyQt6.QtCore import Qt
from datetime import datetime
from mtbp3cd.util.lsr import LsrTree
import mtbp3cd.gui
import json
import glob
import re
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QTableWidget, QFileDialog,
    QTabWidget, QHBoxLayout,
    QTableWidgetItem, QListWidget
)

class TabDefine(QWidget):
    def __init__(self, _p):
        super().__init__()
        self._p = _p

        self.tab_button_1 = QPushButton("Find Tabulation define.xml")
        self.tab_button_1.setEnabled(True)
        self.tab_button_1.clicked.connect(self.tab_button_1_f)

        self.tab_button_2 = QPushButton("Find Analysis define.xml")
        self.tab_button_2.setEnabled(True)
        self.tab_button_2.clicked.connect(self.tab_button_2_f)

        self.tab_button_3 = QPushButton("Save Logs")
        self.tab_button_3.setEnabled(True)
        self.tab_button_3.clicked.connect(self.tab_button_3_f)

        layout_button = QHBoxLayout()
        layout_button.addWidget(self.tab_button_1)
        layout_button.addWidget(self.tab_button_2)
        layout_button.addWidget(self.tab_button_3)

        # BOX - tabs
        self.tabs = QTabWidget()
        self.tabs_sd = QTabWidget()
        self.tabs_ad = QTabWidget()
        self.tab_sd_meta = QWidget()
        self.tab_sd_tree = QWidget()
        self.tab_ad_meta = QWidget()
        self.tab_ad_tree = QWidget()

        # BOX - Tab Meta 
        self.tab_sd_meta_table = QTableWidget()
        self.tab_sd_meta_table.setColumnCount(2)
        self.tab_sd_meta_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.tab_sd_meta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_sd_meta_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tab_sd_meta_table.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_sd_meta = QVBoxLayout()
        layout_tab_sd_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_meta.addWidget(self.tab_sd_meta_table)
        self.tab_sd_meta.setLayout(layout_tab_sd_meta)

        self.tab_ad_meta_table = QTableWidget()
        self.tab_ad_meta_table.setColumnCount(2)
        self.tab_ad_meta_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.tab_ad_meta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_ad_meta_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tab_ad_meta_table.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_ad_meta = QVBoxLayout()
        layout_tab_ad_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_meta.addWidget(self.tab_ad_meta_table)
        self.tab_ad_meta.setLayout(layout_tab_ad_meta)

        # BOX - Tab Tree 
        self.tab_sd_tree_str = QListWidget()
        self.tab_sd_tree_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_sd_tree_str.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_sd_tree = QVBoxLayout()
        layout_tab_sd_tree.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_tree.addWidget(self.tab_sd_tree_str)
        self.tab_sd_tree.setLayout(layout_tab_sd_tree)

        self.tab_ad_tree_str = QListWidget()
        self.tab_ad_tree_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_ad_tree_str.setStyleSheet("font-family: 'Courier New', monospace;")

        layout_tab_ad_tree = QVBoxLayout()
        layout_tab_ad_tree.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_tree.addWidget(self.tab_ad_tree_str)
        self.tab_ad_tree.setLayout(layout_tab_ad_tree)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tabs_sd, "Data tabulation")
        self.tabs_sd.addTab(self.tab_sd_meta, "Meta")
        self.tabs_sd.addTab(self.tab_sd_tree, "Tree")
        self.tabs.addTab(self.tabs_ad, "Analysis datasets")
        self.tabs_ad.addTab(self.tab_ad_meta, "Meta")
        self.tabs_ad.addTab(self.tab_ad_tree, "MDV")

        # BOX - Message List Widget
        self.message_list = QListWidget()
        self.message_list.setFixedHeight(self.message_list.sizeHintForRow(0) + 70)
        self.message_list.setStyleSheet("background-color: rgba(80, 80, 80, 0.15);")

        layout_tab = QVBoxLayout()
        layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab.addLayout(layout_button)
        layout_tab.addWidget(self.tabs)
        layout_tab.addWidget(self.message_list)
        self.setLayout(layout_tab)

    @staticmethod
    def util_get_define_meta_info(folder):
        file = None
        xsl_file = None

        # Search for define.xml (case-insensitive)
        for f in os.listdir(folder):
            if f.lower() == "define.xml":
                file = os.path.join(folder, f)
                break

        # Search for define*.xsl (case-insensitive)
        for f in os.listdir(folder):
            if f.lower().startswith("define") and f.lower().endswith(".xsl"):
                xsl_file = os.path.join(folder, f)
                break

        meta_info = {}
        meta_info['xml_path'] = file
        meta_info['xsl_path'] = xsl_file
        gv_info = {}
        mdv_info = {}

        if not file:
            meta_info['error'] = "define.xml not found (case-insensitive)"
            return meta_info
        
        # Parse XML for meta info
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            # Get XML declaration info (version, encoding)
            with open(file, "rb") as fxml:
                first_line = fxml.readline()
                if first_line.startswith(b'<?xml'):
                    try:
                        first_line_str = first_line.decode("utf-8")
                    except Exception:
                        first_line_str = first_line.decode("latin1")
                    match1 = re.search(r'version="([^"]+)"', first_line_str)
                    match2 = re.search(r'encoding="([^"]+)"', first_line_str)
                    if match1:
                        meta_info['xml_version'] = match1.group(1)
                    if match2:
                        meta_info['xml_encoding'] = match2.group(1)
                first_line = fxml.readline()
                if first_line.startswith(b'<?xml-stylesheet' or b'<?stylesheet'):
                    try:
                        first_line_str = first_line.decode("utf-8")
                    except Exception:
                        first_line_str = first_line.decode("latin1")
                    match1 = re.search(r'type="([^"]+)"', first_line_str)
                    match2 = re.search(r'href="([^"]+)"', first_line_str)
                    if match1:
                        meta_info['xml_stylesheet_type'] = match1.group(1)
                    if match2:
                        meta_info['xml_stylesheet_href'] = match2.group(1)

            # Get root tag and attributes
            meta_info['root_tag'] = root.tag
            for key, value in root.attrib.items():
                if any(substring in key for substring in ["Version", "Date", "OID", "Source"]):
                    meta_info['attr_'+key] = value

            # Get first child with OID
            for child_idx, child in enumerate(root):
                match_ns = re.match(r"\{(.+)\}Study", child.tag)
                if match_ns:
                    ns = match_ns.group(1)
                    meta_info[f'study{child_idx}_ns'] = ns
                    meta_info[f'study{child_idx}_OID'] = child.attrib.get('OID', '')

                    global_vars = child.find(f"{{{ns}}}GlobalVariables")
                    if global_vars is not None:
                        for var_idx, var in enumerate(global_vars):
                            meta_info[f"study{child_idx}_gv{var_idx}_{var.tag}"] = var.text if var.text is not None else ''

                    mdv = child.find(f"{{{ns}}}MetaDataVersion")
                    if mdv is not None:
                        for mdv_idx, var in enumerate(mdv):
                            if 'OID' in var.attrib:
                                meta_info[f"study{child_idx}_mdv{mdv_idx}_OID"] = var.attrib['OID']
                            for attr_key, attr_value in var.attrib.items():
                                meta_info[f"study{child_idx}_mdv{mdv_idx}_{attr_key}"] = attr_value
                            # Find child with tag 'def:Standards'
                            itemgroupdefs = []
                            for sub_idx, sub in enumerate(var):
                                if sub.tag.endswith("Standards") or sub.tag == "def:Standards":
                                    for std_idx, standard in enumerate(sub):
                                        std_key_prefix = f"study{child_idx}_mdv{mdv_idx}_standard{std_idx}_"
                                        for std_attr_key, std_attr_value in standard.attrib.items():
                                            meta_info[std_key_prefix + std_attr_key] = std_attr_value
                                elif sub.tag.endswith("ItemGroupDef") or sub.tag == "ItemGroupDef":
                                    itemgroupdefs.append(sub)

                            meta_info[f"study{child_idx}_mdv{mdv_idx}_ig_count"] = len(itemgroupdefs)
                            for ig_idx, ig in enumerate(itemgroupdefs):
                                ig_key_prefix = f"study{child_idx}_mdv{mdv_idx}_ig{ig_idx}_"
                                for ig_attr_key, ig_attr_value in ig.attrib.items():
                                    meta_info[ig_key_prefix + ig_attr_key] = ig_attr_value

        except Exception as e:
            meta_info['error'] = f"XML parse error: {e}"

        return meta_info

    def tab_button_1_f(self):
        pass
    def tab_button_3_f(self):
        pass

    def tab_button_2_f(self):
        folder = None
        tab_ad_path = getattr(getattr(self._p, "tab_input", None), "tab_ad_path", None)
        if tab_ad_path and os.path.isdir(tab_ad_path):
            folder = tab_ad_path
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Analysis define.xml Folder")
        if not folder:
            return

        if folder:
            self.sd_folder_path = folder
            self.tab_sd_meta_json = self.util_get_define_meta_info(folder)

            for row, (key, value) in enumerate(self.tab_sd_meta_json.items()):
                key_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(str(value))
                self.tab_sd_meta_table.setItem(row, 0, key_item)
                self.tab_sd_meta_table.setItem(row, 1, value_item)

            self.tab_sd_meta_table.resizeColumnsToContents()
            self.tab_sd_meta_table.setRowCount(len(self.tab_sd_meta_json))

            # self.tab_sd_tree_str.clear()
            # width = len(str(len(self.tab_sd_tree_str)))
            # self.tab_sd_tree_str.addItems([f"{str(idx+1).zfill(width)}: {str(item)}" for idx, item in enumerate(self.tab_folder_tree_str)])

    # def tab_button_2_f(self):
    #     file_path_base = getattr(self._p.tab_starting, "gt01_output_folder_path", None)
    #     if not file_path_base:
    #         mtbp3cd.gui.util_show_message(self.message_list, "Please select output folder in the previous step", status="success")
    #         return
    #     file_path = os.path.join(file_path_base, "log_folder_tree.txt")
    #     try:
    #         with open(file_path, "w", encoding="utf-8") as f:
    #             for item in self.tab_folder_tree_str:
    #                 f.write(str(item) + "\n")
    #         mtbp3cd.gui.util_show_message(self.message_list, f"Tree exported: {file_path}", status="success")
    #     except Exception as e:
    #         mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export: {e}", status="success")

    #     meta_json_path = os.path.join(file_path_base, "log_folder_meta.json")
    #     try:
    #         with open(meta_json_path, "w", encoding="utf-8") as f:
    #             json.dump(self.tab_folder_meta_json, f, indent=2)
    #         mtbp3cd.gui.util_show_message(self.message_list, f"Meta exported: {meta_json_path}", status="success")
    #     except Exception as e:
    #         mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export meta.json: {e}", status="success")

    # def tab_button_3_f(self):
    #     file_path_base = getattr(self._p.tab_starting, "gt01_output_folder_path", None)
    #     if not file_path_base:
    #         mtbp3cd.gui.util_show_message(self.message_list, "Please select output folder in the previous step", status="success")
    #         return
    #     file_path = os.path.join(file_path_base, "log_folder_table.csv")
    #     try:
    #         self.folder_file_df.to_csv(file_path, index=False)
    #         mtbp3cd.gui.util_show_message(self.message_list, f"CSV exported: {file_path}", status="success")
    #     except Exception as e:
    #         mtbp3cd.gui.util_show_message(self.message_list, f"Failed to export CSV: {e}", status="success")

if __name__ == "__main__":
    pass