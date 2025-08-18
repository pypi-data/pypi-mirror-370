def get_settings_stylesheets(style_sheet):
    match style_sheet:

        case "QPushButton":
            style_sheet_str = """
                        QPushButton {background-color: #464646;
                                    color: white;
                                    border: 1px solid black;
                                    padding: 5px;
                                    }
                        QPushButton:checked {background-color: #9e9e9f;
                                            color: black;
                                            }
                    """
        case "QComboBox":
            style_sheet_str = """

                            QComboBox {
                                background-color: #464646;
                                color: white;
                                padding: 1px 15px 1px 3px;
                            }
                            QComboBox::drop-down {
                                border-color: #464646;
                                background-color: #464646;
                            }
                            QComboBox::item {
                                background-color: #464646;
                                color: white; 
                            }
                            QComboBox::item:selected {
                                background-color:  #9e9e9f;
                                color: black; 
                            }
                            QComboBox QAbstractItemView {
                                background-color: #464646;
                                color: white; 
                            }
                            """
                
        case "QMenu":
            style_sheet_str = """
                            QMenu::item {
                                        background-color: #464646;
                                        color: white
                                        }
                            QMenu::item:selected {
                                                background-color: #9e9e9f; 
                                                color: black;
                                                }
                            """
        case "QToolButton":
            style_sheet_str = """
                                QToolButton {
                                            color: white;
                                            background-color: #464646;
                                            }
                                            
                                QToolButton::selected {
                                                        color: black;
                                                        background-color: #9e9e9f;
                                                        }

                                QToolButton::hover {
                                                        color: black;
                                                        background-color: #9e9e9f;
                                                        }

                                """
        case "QTableWidget":
            style_sheet_str = """
                              QTableView {border-style: none;
                                        background-color: black;
                                        padding: 0px;
                                        margin: 0px; 
                                        border-left: 2px solid #414141;
                                        border-right: 2px solid #414141;
                                        color: #fb8b1e;
                                        }
                              QTableWidget::item:selected {
                                                        background-color: #414141;
                                                        }
                            
                              QTableWidgetItem {
                                            border-radius: 0px; 
                                            border: 1px solid black;
                                            color: #fb8b1e;
                                            }
                            
                              """                   
        case "TitleLabel":
            style_sheet_str = """background-color : #232323; color : white"""
        
        case "QLineEdit":
            style_sheet_str = """
                            QLineEdit {
                                    background-color: #fb8b1e;
                                    color: black;
                                }
                            QLineEdit:focus {
                                    background-color: #fb8b1e;
                                    border: 2px solid black;
                                            }
                            QLineEdit::selection {
                                                    background-color:  lightblue;
                                                    color: #ffffff;                                  
                                                    }
                            """
        case "SpotQLabel":
            style_sheet_str = """
                            QLabel {
                                        background-color: black;
                                        color: #fb8b1e;
                                    }
                              """
                              
        case "StrikeOptionsComboBox":
            style_sheet_str = """
                            QComboBox {
                                background-color: #fb8b1e;
                                color: black;
                                border: 1px solid black;
                                text-align: right;
                                padding: 1px 15px 1px 3px;
                            }
                            QComboBox:focus {
                                background-color: #fb8b1e;
                                border: 2px solid black;
                                text-align: right;
                            }
                            QComboBox::drop-down {
                                border-color: black;
                                background-color: #fb8b1e;
                                subcontrol-position: right center;
                                text-align: right;
                            }
                            QComboBox::item {
                                background-color: #fb8b1e;
                                color: black;
                                text-align: right;
                            }
                            QComboBox::item:selected {
                                background-color: #d97d1a; 
                                color: black;
                                text-align: right;
                            }
                            QComboBox QAbstractItemView {
                                background-color: #fb8b1e;
                                color: black;
                                border: 1px solid black;
                                text-align: right;
                            }
                        """
        
    return style_sheet_str