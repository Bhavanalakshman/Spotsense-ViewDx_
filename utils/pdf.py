from fpdf import FPDF
from utils.constants import get_path

"""
USAGE:
from utiuls.pdf import PDF

pdf = PDF(title="..") # Document title (Req.id + TimeStamp)
pdf.topbar(device_id="..", date_time="..") # Pass DEVICE_ID & DateTime (02/02/2021 01:22 PM)
pdf.body(req_id="..", cal_id="..", test_type="..", batch="..", manufacturer="..", value="..", result_image="..", plot_image="..", unit="ng/ml")
    # unit has default value (ng/ml)
    # value can be either float, int, string

pdf.output('path/__file_name__.pdf', 'F') # To save the pdf
"""

class PDF(FPDF):
    def __init__(self, title, **kwargs):
        super(PDF, self).__init__(**kwargs)
        self.orientation = "P"
        self.unit = "mm"
        self.format = "A4"
        self.set_font('Arial', '', 16)
        self.set_title(title)
        self.set_author("ViewDx")
        self.set_creator("ViewDx")
        self.add_page()
        pass
    def header(self):
        self.cell(40)
        self.text(txt='Report Generated on:', x=50, y=22)
        self.image(get_path('logos.png'), x=100, y=9, w=50)
        pass
    def topbar(self, device_id, date_time):
        self.set_xy(10, 35)
        self.set_font('Arial', '', 18)
        self.cell(w=0, h=32, border=1)
        self.text(x=15, y=45, txt="Device ID : " + device_id)
        self.text(x=15, y=60, txt="Date Time : " + date_time)
        pass
    def body(self, req_id, cal_id, test_type, batch, manufacturer, value, result_image, unit="ng/ml", plot_image = ""):
        self.set_font('Arial', '', 16)
        self.set_xy(15, 120)
        self.text(x=15, y=120, txt="Requisition ID : " + req_id)
        self.text(x=15, y=135, txt="Calibration ID : " + cal_id)
        self.text(x=15, y=150, txt="Test Type : " + test_type)
        self.text(x=15, y=165, txt="Manufacturer : " + manufacturer)
        self.text(x=15, y=180, txt="Batch ID : " + batch)
        self.text(x=15, y=195, txt="OD Values : " + str(value))
        self.image(result_image, x=160, y=90, w=22, h=0)
        if(plot_image != ""):
            self.image(plot_image, x=140, y=180, w=65, h=0)
        pass
    # def footer(self):
    #     self.set_xy(10, -57)
    #     self.cell(w=0, h=36, border=1)
    #     self.text(x=15, y=248, txt="Report verified by:")
    #     self.text(x=15, y=258, txt="___________________________")
    #     self.text(x=45, y=268, txt="(signature)")
    #     self.text(x=110, y=248, txt="Date:")
    #     self.text(x=110, y=258, txt="__________________________")
    #     pass
    pass