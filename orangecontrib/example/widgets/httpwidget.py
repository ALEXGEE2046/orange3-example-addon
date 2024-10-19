import requests
import numpy as np

from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui

import Orange
from Orange.data import Table, Domain, ContinuousVariable, DiscreteVariable


class HTTP(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "HTTP"
    # Short widget description
    description = "Lets the user input a URL"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/http.svg"

    # Widget's outputs; here, a single output named "Data", of type str
    class Outputs:
        data = Output("Data", Table)

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    url = Setting('https://')
    res = ''

    def __init__(self):
        super().__init__()

        from AnyQt.QtGui import QRegularExpressionValidator
        from AnyQt.QtCore import QRegularExpression
        gui.lineEdit(self.controlArea, self, "url", "Enter a URL",
                     box="URL",
                     callback=self.fetch_data,
                     valueType=str,
                     validator=QRegularExpressionValidator(
                                QRegularExpression(
                                r'^(https?://)?'  # http:// or https://
                                r'(([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,6})'  # domain name
                                r'(:[0-9]{1,5})?'  # optional port
                                r'(/.*)?$'  # optional path
                                )))
        self.fetch_data()

    def fetch_data(self):
        """Fetch data from the web."""
        response = requests.get(self.url)
        # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()

        self.res = response.text
        self.Outputs.data.send(self.handle_response())

    def handle_response(self):
        # 分割文本
        lines = str(self.res).split('\n')

        # 创建特征列表，这里我们使用每行的字符数作为特征
        char_counts = np.array([[len(line)] for line in lines])

        # 创建目标变量列表，检查每行是否包含 "<p>"
        contains_test = np.array([[1 if '<script>' in line else 0] for line in lines])

        # 创建特征变量和目标变量
        feature_var = ContinuousVariable("Char Count")
        target_var = DiscreteVariable("Contains Script", values=["No", "Yes"])

        # 创建数据域
        domain = Domain([feature_var], [target_var])

        # 创建数据表
        table = Table.from_numpy(domain, char_counts, contains_test)

        return table

