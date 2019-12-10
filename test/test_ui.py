from testing_framework.ui import generate_ui
import pathlib

def skip_test_ui() -> bool:
    report: str = "report"

    path: pathlib.Path = pathlib.Path("../reports/spiodufhvpo98q347hv0-9er.txt")

    try:        
        generate_ui(report, path)
    except:
        return False
    
    return True