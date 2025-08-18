from PySide6 import QtCore, QtGui



def sheet(opt):
    match opt:
        case "QComboBox":
            style_sheet_str = """
                            QComboBox {
                                background-color: #fb8b1e;
                                color: black;
                                border: None;
                                text-align: center;
                            }
                            QComboBox:focus {
                                background-color: #fb8b1e;
                                border: 2px solid black;
                                text-align: center;
                            }
                            QComboBox::drop-down {
                                border-color: black;
                                background-color: #fb8b1e;
                                text-align: center;
                            }
                            QComboBox::item {
                                background-color: #fb8b1e;
                                color: black;
                                text-align: center;
                            }
                            QComboBox::item:selected {
                                background-color: #d97d1a; 
                                color: black;
                                text-align: center;
                            }
                            QComboBox QAbstractItemView {
                                background-color: #fb8b1e;
                                color: black;
                                border: None;
                                text-align: center;
                            }
                        """
        case "QTableWidget":
            style_sheet_str = """
                QTableView {
                    border-style: none;
                    background-color: black;
                    padding: 0px;
                    margin: 0px;
                    color: white;
                    border-left: 2px solid #414141;
                    border-right: 2px solid #414141;
                    selection-background-color: #9e9e9f;
                }
                QTableWidget::item {
                    padding: 0px;
                    margin: 0px;
                    border: none; 
                }
                QTableWidget::item:selected {
                    background-color: #414141;
                    padding: 0px;
                    margin: 0px;
                    color: white;
                }
            """                   

                        
                        
                        
    return style_sheet_str