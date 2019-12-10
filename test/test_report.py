from testing_framework.report import report
from typing import Tuple
import html

def test_report():
    result = report(("test_report", "second line"))
    expected_result = f"""
<!DOCTYPE html>
<html>
  <body>
    <div>test_report</div><div>second line</div>
  </body>
</html>
"""
    assert html.escape(expected_result) == html.escape(result)