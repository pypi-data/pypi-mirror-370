
def get_settings_stylesheets(style_sheet):
    match style_sheet:
        case "QPushButton":
            style_sheet_str = """
                            QPushButton {background-color: #464646;
                                        color: white;
                                        border: 1px solid black;
                                        padding: 5px;
                                        }
                            QPushButton:checked {
                                                background-color: #9e9e9f;
                                                color: black;
                                                }
                                                
                            QPushButton::hover {
                                                color: black;
                                                background-color: #9e9e9f;
                                                }
                            """
                            
                            
        case "QComboBox":
            style_sheet_str = """
                        QComboBox {
                            background-color: #464646;
                            color: white;
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
                            
                            QMenu::hover {color: black;
                                        background-color: #9e9e9f;
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

    return style_sheet_str