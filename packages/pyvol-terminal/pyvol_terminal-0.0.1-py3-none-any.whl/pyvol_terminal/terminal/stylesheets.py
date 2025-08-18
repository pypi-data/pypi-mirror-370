from PySide6 import QtCore, QtGui, QtWidgets

def get_global(key):
    match key:
        case "font":
            ret = QtGui.QFont("Neue Haas Grotesk Text Pro", 10)
        
        case "widgets":
            ret = """
                  QPushButton {background-color: #fb8b1e;
                                color: black;
                                border: none;           
                                padding: 5px 10px;   
                  }
                  QPushButton:hover {background-color: #e67e17; 
                  }
                  QPushButton:pressed {background-color: #d35400;
                  }
                  """
    return ret