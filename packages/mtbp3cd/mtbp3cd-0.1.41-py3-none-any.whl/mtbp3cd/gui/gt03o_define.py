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
from mtbp3cd.util.ltr import ListTree
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

class DefaultTableWidget(QTableWidget):
    def __init__(self, column_titles, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(column_titles))
        self.setHorizontalHeaderLabels(column_titles)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setStyleSheet("font-family: 'Courier New', monospace;")

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
        self.tab_sd_igdef = QWidget()
        self.tab_sd_tree = QWidget()
        self.tab_sd_desc = QWidget()
        self.tab_ad_meta = QWidget()
        self.tab_ad_igdef = QWidget()
        self.tab_ad_tree = QWidget()
        self.tab_ad_desc = QWidget()

        # BOX - Tab Meta 
        self.tab_sd_meta_table = DefaultTableWidget(["Key", "Value", "ns"])
        layout_tab_sd_meta = QVBoxLayout()
        layout_tab_sd_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_meta.addWidget(self.tab_sd_meta_table)
        self.tab_sd_meta.setLayout(layout_tab_sd_meta)

        self.tab_ad_meta_table = DefaultTableWidget(["Key", "Value", "ns"])
        layout_tab_ad_meta = QVBoxLayout()
        layout_tab_ad_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_meta.addWidget(self.tab_ad_meta_table)
        self.tab_ad_meta.setLayout(layout_tab_ad_meta)

        # BOX - Tab igdef 
        self.tab_sd_igdef_table = DefaultTableWidget(["Id", "File Name", "Description"])
        layout_tab_sd_igdef = QVBoxLayout()
        layout_tab_sd_igdef.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_igdef.addWidget(self.tab_sd_igdef_table)
        self.tab_sd_igdef.setLayout(layout_tab_sd_igdef)

        self.tab_ad_igdef_table = DefaultTableWidget(["Id", "File Name", "Description"])
        layout_tab_ad_igdef = QVBoxLayout()
        layout_tab_ad_igdef.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_igdef.addWidget(self.tab_ad_igdef_table)
        self.tab_ad_igdef.setLayout(layout_tab_ad_igdef)

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

        # BOX - Tab desc 
        self.tab_sd_desc_table = DefaultTableWidget(["Column_value", "Type", "Length", "Description", "CL_OID"])
        layout_tab_sd_desc = QVBoxLayout()
        layout_tab_sd_desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_sd_desc.addWidget(self.tab_sd_desc_table)
        self.tab_sd_desc.setLayout(layout_tab_sd_desc)

        self.tab_ad_desc_table = DefaultTableWidget(["Column_value", "Type", "Length", "Description", "CL_OID"])
        layout_tab_ad_desc = QVBoxLayout()
        layout_tab_ad_desc.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_ad_desc.addWidget(self.tab_ad_desc_table)
        self.tab_ad_desc.setLayout(layout_tab_ad_desc)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tabs_sd, "Data tabulation")
        self.tabs_sd.addTab(self.tab_sd_meta, "Meta")
        self.tabs_sd.addTab(self.tab_sd_igdef, "File")
        self.tabs_sd.addTab(self.tab_sd_tree, "Column")
        self.tabs_sd.addTab(self.tab_sd_desc, "Col. Description")
        self.tabs.addTab(self.tabs_ad, "Analysis datasets")
        self.tabs_ad.addTab(self.tab_ad_meta, "Meta")
        self.tabs_ad.addTab(self.tab_ad_igdef, "File")
        self.tabs_ad.addTab(self.tab_ad_tree, "Column")
        self.tabs_ad.addTab(self.tab_ad_desc, "Col. Description")

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

        meta_info_list = []
        ig_def_list = []
        ig_def_oid_list = []
        ig_def_oid_list_desc = []

        if file:
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
                        meta_info_list.append({"key": "xml_version", "value": match1.group(1), "ns": ""})
                    if match2:
                        meta_info_list.append({"key": "xml_encoding", "value": match2.group(1), "ns": ""})
                    first_line = fxml.readline()
                    if first_line.startswith(b'<?xml-stylesheet' or b'<?stylesheet'):
                        try:
                            first_line_str = first_line.decode("utf-8")
                        except Exception:
                            first_line_str = first_line.decode("latin1")
                    # match1 = re.search(r'type="([^"]+)"', first_line_str)
                    # match2 = re.search(r'href="([^"]+)"', first_line_str)
                    # if match1:
                    #     meta_info_list.append({"key": "xml_stylesheet_type", "value": match1.group(1), "ns": ""})
                    # if match2:
                    #     meta_info_list.append({"key": "xml_stylesheet_href", "value": match2.group(1), "ns": ""})

                # Get root tag and attributes
                match_ns = re.match(r"^\{(.+)\}", root.tag)
                ns = match_ns.group(1) if match_ns else None
                root_tag = re.sub(r'^\{.*\}', '', root.tag)
                meta_info_list.append({"key": "root_tag", "value": root_tag, "ns": ns})
                for key, value in root.attrib.items():
                    if any(substring in key for substring in ["Version", "Date", "OID", "Source"]):
                        meta_info_list.append({"key": "root_"+key, "value": value, "ns": ""})

                for child_idx, child in enumerate(root):
                    match_ns = re.match(r"\{(.+)\}Study", child.tag)
                    if match_ns:
                        ns = match_ns.group(1)
                        meta_info_list.append({"key": f"study{child_idx}_OID", "value": child.attrib.get('OID', ''), "ns": ns})

                    global_vars = child.find(f"{{{ns}}}GlobalVariables")
                    if global_vars is not None:
                        for var_idx, var in enumerate(global_vars):
                            if "}" in var.tag:
                                ns_match = re.match(r"^\{(.+)\}", var.tag)
                                var_ns = ns_match.group(1) if ns_match else ""
                                var_tag_clean = re.sub(r'^\{.*\}', '', var.tag)
                            else:
                                var_ns = ""
                                var_tag_clean = var.tag
                            meta_info_list.append({
                                "key": f"study{child_idx}_gv{var_idx}_{var_tag_clean}",
                                "value": var.text if var.text is not None else '',
                                "ns": var_ns
                            })

                    mdv = child.find(f"{{{ns}}}MetaDataVersion")
                    if mdv is not None:
                        itemgroupdef_list = [c for c in mdv if re.sub(r'^\{.*\}', '', c.tag) == "ItemGroupDef"]
                        for ig_idx, ig in enumerate(itemgroupdef_list):
                            ns_match = re.match(r"^\{(.+)\}", ig.tag)
                            ig_ns = ns_match.group(1) if ns_match else ""

                            ig_attr_oid = ig.attrib.get("OID", "")
                            if ig_attr_oid.startswith("IG."):
                                ig_attr_oid = ig_attr_oid[3:]
                            ig_def_oid_list.append(ig_attr_oid)
                            ig_def_oid_list.append(ig_attr_oid+".Attr")

                            desc = ig.find(f"{{{ig_ns}}}Description")
                            if desc is not None:
                                translate_text = desc.find(f"{{{ig_ns}}}TranslatedText")

                            ig_def_list.append({
                                "key": f"study{child_idx}_mdv_IgDef{ig_idx}_OID",
                                "value": ig_attr_oid,
                                "description": translate_text.text
                            })

                            for attr_key, attr_value in ig.attrib.items():
                                if attr_key.lower() == "oid":
                                    continue
                                if attr_key.startswith("{"):
                                    attr_key_clean = re.sub(r'^\{.*\}', '', attr_key)
                                    attr_key_clean = attr_key_clean.replace('.', '__')
                                else:
                                    attr_key_clean = attr_key.replace('.', '__')
                                attr_value_clean = attr_value.replace('.', '__')
                                ig_def_oid_list.append(ig_attr_oid + ".Attr." + attr_key_clean + ':' + attr_value_clean)


                            ig_def_oid_list.append(ig_attr_oid+".IT")
                            itemref_list = [itemref for itemref in ig if re.sub(r'^\{.*\}', '', itemref.tag) == "ItemRef"]
                            # Get last section of ig_attr_oid separated by "."
                            for itemref in itemref_list:
                                item_oid = itemref.attrib.get("ItemOID", "")
                                mandatory = itemref.attrib.get("Mandatory", "")
                                item_oid = re.sub(r'^\{.*\}', '', item_oid)
                                item_oid = item_oid.replace(f"IT.{ig_attr_oid}.", "IT.")
                                if item_oid:
                                    if mandatory == "Yes":
                                        ig_def_oid_list.append(f"{ig_attr_oid}.{item_oid} (Mandatory)")
                                    else:
                                        ig_def_oid_list.append(f"{ig_attr_oid}.{item_oid}")

                        itemdef_list = [c for c in mdv if re.sub(r'^\{.*\}', '', c.tag) == "ItemDef"]
                        for item_idx, itemdef in enumerate(itemdef_list):
                            item_oid = itemdef.attrib.get("OID", "")
                            desc = itemdef.find(f"{{{ns}}}Description")
                            data_type = itemdef.attrib.get("DataType", "")
                            code_list_ref = itemdef.find(f"{{{ns}}}CodeListRef")
                            code_list_oid = code_list_ref.attrib.get("CodeListOID", "") if code_list_ref is not None else ""
                            length = itemdef.attrib.get("Length", "")
                            if desc is not None:
                                translate_text = desc.find(f"{{{ns}}}TranslatedText")
                                description = translate_text.text if translate_text is not None else ""
                            else:
                                description = ""
                            if item_oid:
                                ig_def_oid_list_desc.append([item_oid, data_type, length, description, code_list_oid])

            except Exception as e:
                meta_info_list.append({"key": "error", "value": f"XML parse error: {e}", "ns": ""})
        else:
            meta_info_list.append({"key": "error", "value": "define.xml not found (case-insensitive)", "ns": ""})

        meta_info = pd.DataFrame(meta_info_list, columns=["key", "value", "ns"])
        igdef_info = pd.DataFrame(ig_def_list, columns=["key", "value", "description"])
        igdef_oid_desc_info = pd.DataFrame(ig_def_oid_list_desc, columns=["column","type", "length", "description", "cloid"])

        #ig_def_oid_list = [f"{item}_idx_{idx}" for idx, item in enumerate(ig_def_oid_list)]

        return meta_info, igdef_info, ig_def_oid_list, igdef_oid_desc_info

    def tab_button_3_f(self):
        pass

    def tab_button_1_f(self):
        folder = None
        tab_sd_path = getattr(getattr(self._p, "tab_input", None), "tab_sd_path", None)
        if tab_sd_path and os.path.isdir(tab_sd_path):
            folder = tab_sd_path
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Analysis define.xml Folder")
        if not folder:
            return
        self.tabs.setCurrentWidget(self.tabs_ad)

        if folder:
            self.sd_folder_path = folder
            self.tab_sd_meta_df, self.tab_sd_igdef_df, self.tab_sd_igdef_oid, self.tab_sd_igdef_oid_desc = self.util_get_define_meta_info(folder)

            self.tab_sd_meta_table.setRowCount(0)
            for row_idx, row in self.tab_sd_meta_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                self.tab_sd_meta_table.insertRow(row_idx)
                self.tab_sd_meta_table.setItem(row_idx, 0, item1)
                self.tab_sd_meta_table.setItem(row_idx, 1, item2)
            self.tab_sd_meta_table.resizeColumnsToContents()

            self.tab_sd_igdef_table.setRowCount(0)
            for row_idx, row in self.tab_sd_igdef_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                item3 = QTableWidgetItem(str(row["description"]))
                self.tab_sd_igdef_table.insertRow(row_idx)
                self.tab_sd_igdef_table.setItem(row_idx, 0, item1)
                self.tab_sd_igdef_table.setItem(row_idx, 1, item2)
                self.tab_sd_igdef_table.setItem(row_idx, 2, item3)
            self.tab_sd_igdef_table.resizeColumnsToContents()

            self.tab_sd_desc_table.setRowCount(0)
            for row_idx, row in self.tab_sd_igdef_oid_desc.iterrows():
                item1 = QTableWidgetItem(str(row["column"]))
                item2 = QTableWidgetItem(str(row["type"]))
                item3 = QTableWidgetItem(str(row["length"]))
                item4 = QTableWidgetItem(str(row["description"]))
                item5 = QTableWidgetItem(str(row["cloid"]))
                self.tab_sd_desc_table.insertRow(row_idx)
                self.tab_sd_desc_table.setItem(row_idx, 0, item1)
                self.tab_sd_desc_table.setItem(row_idx, 1, item2)
                self.tab_sd_desc_table.setItem(row_idx, 2, item3)
                self.tab_sd_desc_table.setItem(row_idx, 3, item4)
                self.tab_sd_desc_table.setItem(row_idx, 4, item5)
            self.tab_sd_desc_table.resizeColumnsToContents()

            if self.tab_sd_igdef_oid:
                lsr1 = ListTree(self.tab_sd_igdef_oid, infmt='dotspace', label="last_section")
                lsr1_str = lsr1.list_tree()

                self.tab_sd_tree_str.clear()
                width = len(str(len(lsr1_str)))
                self.tab_sd_tree_str.addItems([f"{str(idx+1).zfill(width)}: {str(item)}" for idx, item in enumerate(lsr1_str)])
            else:
                self.tab_sd_tree_str.clear()
                self.tab_sd_tree_str.addItem("No ItemGroup OIDs found in define.xml")

    def tab_button_2_f(self):
        folder = None
        tab_ad_path = getattr(getattr(self._p, "tab_input", None), "tab_ad_path", None)
        if tab_ad_path and os.path.isdir(tab_ad_path):
            folder = tab_ad_path
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Analysis define.xml Folder")
        if not folder:
            return
        self.tabs.setCurrentWidget(self.tabs_ad)

        if folder:
            self.ad_folder_path = folder
            self.tab_ad_meta_df, self.tab_ad_igdef_df, self.tab_ad_igdef_oid, self.tab_ad_igdef_oid_desc = self.util_get_define_meta_info(folder)

            self.tab_ad_meta_table.setRowCount(0)
            for row_idx, row in self.tab_ad_meta_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                self.tab_ad_meta_table.insertRow(row_idx)
                self.tab_ad_meta_table.setItem(row_idx, 0, item1)
                self.tab_ad_meta_table.setItem(row_idx, 1, item2)
            self.tab_ad_meta_table.resizeColumnsToContents()

            self.tab_ad_igdef_table.setRowCount(0)
            for row_idx, row in self.tab_ad_igdef_df.iterrows():
                item1 = QTableWidgetItem(str(row["key"]))
                item2 = QTableWidgetItem(str(row["value"]))
                item3 = QTableWidgetItem(str(row["description"]))
                self.tab_ad_igdef_table.insertRow(row_idx)
                self.tab_ad_igdef_table.setItem(row_idx, 0, item1)
                self.tab_ad_igdef_table.setItem(row_idx, 1, item2)
                self.tab_ad_igdef_table.setItem(row_idx, 2, item3)
            self.tab_ad_igdef_table.resizeColumnsToContents()

            self.tab_ad_desc_table.setRowCount(0)
            for row_idx, row in self.tab_ad_igdef_oid_desc.iterrows():
                item1 = QTableWidgetItem(str(row["column"]))
                item2 = QTableWidgetItem(str(row["type"]))
                item3 = QTableWidgetItem(str(row["length"]))
                item4 = QTableWidgetItem(str(row["description"]))
                item5 = QTableWidgetItem(str(row["cloid"]))
                self.tab_ad_desc_table.insertRow(row_idx)
                self.tab_ad_desc_table.setItem(row_idx, 0, item1)
                self.tab_ad_desc_table.setItem(row_idx, 1, item2)
                self.tab_ad_desc_table.setItem(row_idx, 2, item3)
                self.tab_ad_desc_table.setItem(row_idx, 3, item4)
                self.tab_ad_desc_table.setItem(row_idx, 4, item5)
            self.tab_ad_desc_table.resizeColumnsToContents()

            if self.tab_ad_igdef_oid:
                lsr1 = ListTree(self.tab_ad_igdef_oid, infmt='dotspace', label="last_section")
                lsr1_str = lsr1.list_tree()

                self.tab_ad_tree_str.clear()
                width = len(str(len(lsr1_str)))
                self.tab_ad_tree_str.addItems([f"{str(idx+1).zfill(width)}: {str(item)}" for idx, item in enumerate(lsr1_str)])
            else:
                self.tab_ad_tree_str.clear()
                self.tab_ad_tree_str.addItem("No ItemGroup OIDs found in define.xml")

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