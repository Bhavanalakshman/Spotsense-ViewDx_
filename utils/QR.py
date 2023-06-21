from picamera import PiCamera
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from pyzbar import pyzbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton, MDRectangleFlatIconButton, MDIconButton, MDFillRoundFlatButton
import sys
from kivymd.app import MDApp
from kivy.app import App

def QR_scan_function():
    
    def captureQR():
        camera = PiCamera()
        camera.start_preview()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(40, GPIO.OUT)
        GPIO.output(40, True)
        GPIO.cleanup
        camera.capture('/home/pi/viewdx/captured/QR.jpg')
        GPIO.output(40,False)
        input_image = cv2.imread('/home/pi/viewdx/captured/QR.jpg')
        time.sleep(3)
        camera.stop_preview()
        camera.close()
        return input_image
    captureQR()

    def scan_qr_code(input_image):
        img = cv2.imread(input_image)
        barcodes = pyzbar.decode(img)
        print(type(barcodes))
        if barcodes != []:
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                print(type(barcode_type))
                QR_data=(f"Found:{barcode_data}")
                print (type(QR_data))
            
        else:
            QR_data == ""
            dialog = MDDialog(    
            text="Couldnot get QR Code",
            buttons=[
                    MDFillRoundFlatButton(text="Try Again", on_press=lambda _:dialog.dismiss()),
                    ],
                )
            dialog.open()
            
        return img
            
    scan_qr_code('/home/pi/viewdx/captured/QR.jpg')
    
#QR = QR_scan_function()
#print("QR",QR)

  
    
#             if not self.dialog:
#                 self.dialog = MDDialog(
#                     text="QRcode not found , Try again",
#                     buttons=[
#                         MDFlatButton(text="No", on_press=lambda _:self.dialog.dismiss()), MDFlatButton(text="Yes",on_press=lambda _:self.shutdown()),
#                     ],
#                 )
#             self.dialog.open()
#             pass

#             self.dialog = MDDialog(
#                 text="QRcode not found , Try again",
#                 button=[
#                         MDFlatButton(text="OK",, on_press=lambda _:self.dialog.dismiss())],
#                 )
#             print("im inside else")
#             dialog.open()
            
#     def close_dialog(instance):
#         print("im inside cloase")
#         instance.dismiss()
