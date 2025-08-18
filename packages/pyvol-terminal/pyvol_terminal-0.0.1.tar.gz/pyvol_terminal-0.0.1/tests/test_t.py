import sys
import time
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np


class GLTextItemPerformanceTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLTextItem Performance Test")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create OpenGL view
        self.gl_view = gl.GLViewWidget()
        self.gl_view.setCameraPosition(distance=50)
        
        # Add grid for reference
        grid = gl.GLGridItem()
        self.gl_view.addItem(grid)
        
        # Create text item
        self.text_item = gl.GLTextItem(text="Initial Text", pos=(0, 0, 0))
        self.gl_view.addItem(self.text_item)
        
        # Create UI controls
        self.btn_run_tests = QPushButton("Run Performance Tests")
        self.result_label = QLabel("Results will appear here")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.gl_view, 1)
        layout.addWidget(self.btn_run_tests)
        layout.addWidget(self.result_label)
        self.setLayout(layout)
        
        # Connect signals
        self.btn_run_tests.clicked.connect(self.run_all_tests)
        
        # Test parameters
        self.iterations = 10000
        self.texts = [f"Text {i}" for i in range(self.iterations)]
        self.positions = [np.array([np.sin(i*0.1)*10, np.cos(i*0.1)*10, 0]) 
                          for i in range(self.iterations)]
    
    def run_all_tests(self):
        """Run both tests and compare results"""
        self.btn_run_tests.setEnabled(False)
        self.result_label.setText("Running tests...")
        QApplication.processEvents()  # Update UI immediately
        
        # Run text+position test
        both_time = self.test_both_updates()
        
        # Run text-only test
        text_time = self.test_text_only_update()
        
        # Compare results
        self.show_comparison(both_time, text_time)
        self.btn_run_tests.setEnabled(True)
    
    def test_both_updates(self):
        """Test updating both text and position in one setData call"""
        start_time = time.perf_counter()
        
        for i in range(self.iterations):
            self.text_item.setData(text=self.texts[i], pos=self.positions[i])
            if i % 100 == 0:  # Update UI occasionally for responsiveness
                QApplication.processEvents()
                
        return time.perf_counter() - start_time
    
    def test_text_only_update(self):
        """Test updating only text property"""
        start_time = time.perf_counter()
        
        for i in range(self.iterations):
            self.text_item.setData(text=self.texts[i])
            if i % 100 == 0:  # Update UI occasionally for responsiveness
                QApplication.processEvents()
                
        return time.perf_counter() - start_time
    
    def show_comparison(self, both_time, text_time):
        """Display comparison of both test results"""
        both_avg = both_time / self.iterations * 1000  # ms
        text_avg = text_time / self.iterations * 1000  # ms
        speed_diff = both_avg - text_avg
        speed_ratio = both_avg / text_avg if text_avg != 0 else 0
        
        results = (
            f"=== Performance Comparison ===\n"
            f"Test iterations: {self.iterations}\n\n"
            f"BOTH text+position updates:\n"
            f"  Total time: {both_time:.4f}s\n"
            f"  Average: {both_avg:.6f} ms/update\n\n"
            f"ONLY text updates:\n"
            f"  Total time: {text_time:.4f}s\n"
            f"  Average: {text_avg:.6f} ms/update\n\n"
            f"Comparison:\n"
            f"  Text-only is {speed_diff:.3f} ms/update faster\n"
            f"  Text-only is {speed_ratio:.1f}x faster"
        )
        
        self.result_label.setText(results)
        print(results)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GLTextItemPerformanceTest()
    window.show()
    sys.exit(app.exec())