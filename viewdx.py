import sys
import os
import PIL
from datetime import date, datetime
from time import sleep
import csv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, ListProperty
from random import random
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from subprocess import call
from kivy.properties import ListProperty
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.metrics import dp
from kivymd.icon_definitions import md_icons
from kivymd.uix.list import OneLineIconListItem, MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem, OneLineAvatarListItem
from kivymd.uix.datatables import MDDataTable, TableHeader, TableData, TablePagination
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivymd.color_definitions import colors
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton, MDRectangleFlatIconButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from functools import partial
from picamera import PiCamera
import base64

from utils.constants import *
from utils.updater import check_for_updates, do_update
from utils.wifi import ssid_list, connect_to_ssid
from utils.local_db import *
from utils.imagepro import *
from utils.QR import *

from utils.pdf import PDF
from timeit import default_timer as timer
from kivy.properties import StringProperty
from kivy.uix.recycleview import RecycleView
from kivymd.uix.card import MDCard
from utils.testslist import md_tests
from kivy.uix.screenmanager import ScreenManager
#-------------------------------------------GLOBAL VARIABLES---------------------------------------
#IS_UPDATE_AVAILABLE = False
#IS_UPDATE_AVAILABLE = check_for_updates() # CHECK FOR UPDATES
set_app_path(os.path.abspath(__file__)) # SET ROOT DIRECTORY PATH

#-------------------------------------------First_screen--------------------------------------------

class first_screen(Screen):
    def __init(self, **kwargs):
        super(first_screen, self).__init__(**kwargs)
    pass

#------------------------------------------------Qr_scan----------------------------------------
class QR_scan(Screen):
    def __init(self, **kwargs):
        super(QR_scan, self).__init__(**kwargs)
    pass



# ----------------------------------------------mainsplash---------------------------------------------------

class mainsplash(Screen):
    def __init(self, **kwargs):
        super(mainsplash, self).__init__(**kwargs)
    pass

#-------------------------------------------item_classes-------------------------------------------
class Item(OneLineAvatarListItem):
    divider = None
    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)
    pass

class CustomKeyboard(MDBoxLayout):
    #how to use capslock
    lay = None
    def __init__(self, **kwargs):
        super(CustomKeyboard, self).__init__(**kwargs)
        self.lay = MDTextField(hint_text='', size_hint_x=1, height="30dp", font_size=20, halign = 'center')
        self.add_widget(self.lay)
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['(', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ')'],
            ['#', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '@', '<-'],
            ['_', '.', ':', '+', ' SPACE ', '-', '*', '/', '=']]
        for rows in self.keys:
            row_layout = BoxLayout(orientation="horizontal")
            for key in rows:
                btn = Button(text=key, color=(0,0,0,1), background_color=(1,1,1,0), font_size=20, border=(0,0,0,0), on_press=partial(self.add, key))
                btn.spacing = "10dp"
                row_layout.add_widget(btn)
            row_layout.spacing ="10dp"
            self.add_widget(row_layout)
        pass
    def add(self, *args):
        key = args[0]
        if (key == '<-'): self.lay.text = self.lay.text[:-1]
        elif (key == ' SPACE '): self.lay.text += " "
        else: self.lay.text += key
        pass
    pass

class resultlist(MDBoxLayout):
    req_list = []
    def __init__(self, **kwargs):
        super(resultlist, self).__init__(**kwargs)
        pass
    def render(self):
        self.clear_widgets()
        self.req_list = get_all_requisitions()
        self.scroll = ScrollView()
        self.list1 = MDList()
        try:
            for item in self.req_list:
                for result in item['test_results']:
                    first = "Requisition ID: " + item['requisition_id'] + ", Time: " + result['timestamp']
                    second = "Test Type: " + result['test_name'] + ", Normal Range: " + result['normal_range']
                    third = "Result " + str(result['value'])
                    self.list1.add_widget(ThreeLineListItem(text=first, secondary_text=second, tertiary_text=third))
            self.scroll.add_widget(self.list1)
            self.add_widget(self.scroll)
        except Exception as e:
            print("error", e)
        pass
        pass
    pass

#-------------------------------------------menubar_screens----------------------------------------
class device_infopage(Screen):
    def on_enter(self):
        self.ids['device_id'].text = "Device serial number:" + DEVICE_ID
        self.ids['device_passkey'].text = "Device activation key:" + DEVICE_PSK
        pass
    pass

class call_support(Screen):
    def on_enter(self):
        self.ids['install_date'].text = "Device installation date:" + DEVICE_INSTALL
        pass
    pass

class setup_network(Screen):
    dialog = None
    SSID = ""
    def __init__(self, **kwargs):
        super(setup_network, self).__init__(**kwargs)
    def show_menu(self):
        try:
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Select SSID",
                    type="confirmation",
                    items=[ Item(text=ssid, on_release=self.get_text) for ssid in ssid_list() ]
                )
            self.dialog.open()
        except:
            self.error = MDDialog(text="Could not fetch networks")
            self.error.open()
        pass
    def get_text(self, Item):
        self.SSID = Item.text
        pass
    def connect_to_wifi(self):
        PSK = self.ids['keyboard'].lay.text
        try:
            connect_to_ssid(ssid=self.SSID, key=PSK)
        except:
            self.error = MDDialog(text="Could not connect to network")
            self.error.open()
        pass
    pass

#--------------------------------------------test_screens------------------------------------------
class CustomOneLineIconListItem(OneLineIconListItem):
    pass

class SearchScreen(Screen):
    
    tests = ['blood_profile', 'CancerMarkers', 'CardiacPanel', 'FertilityPanel', 'InfectiousDiseases', 'Inflammation',
             'NeonatalSepsis', 'STDPanel', 'Inflammation','TSH (uIU/ml)','Fecal Occult Blood','Dengue (NS1 and Ag+Ab)','HIV', 'Malaria Ag (p.f/Pan)','S.typhi (IgG/IgM)' ]

    def filter_tests(self, query):
        filtered_tests = [test for test in self.tests if test.lower().startswith(query.lower())]
        return filtered_tests

    def select_test(self, test):
        self.ids.search_field.text = test
        # Perform additional actions with the selected test

    def update_test_list(self, query):
        filtered_tests = self.filter_tests(query)
        self.ids.rv.data = [{'text': test} for test in filtered_tests]




class homepage(Screen):
    def __init__(self, **kwargs):
        super(homepage, self).__init__(**kwargs)
        pass
    def onpress(self, id):
        analyte_page = self.manager.get_screen('analytepage')
        setattr(analyte_page, 'id', id)
        main_reqid = self.manager.get_screen('main_reqid')
        setattr(main_reqid, 'id', id)
        main_calid = self.manager.get_screen('main_calid')
        setattr(main_calid, 'id', id)
        self.manager.current='analytepage'
        pass
    
    pass



class analytepage(Screen):
    analyte=""
    calibration_data=""
    analyte_list = []
    lines = 0
    dialog = None
    def __init__(self, **kwargs):
        super(analytepage, self).__init__(**kwargs)
    def on_enter(self):
        self.ids['scroll_layout'].clear_widgets()
        self.analyte_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.9), pos_hint={'top': 1, 'right':1})
        self.scroll = ScrollView()
        self.list = MDList()
        #self.list.add_widget(TwoLineListItem(text='Add analyte', on_release=self.addanalyte))
        self.analyte_list = analyte_db.table(self.id).all()
        for item in self.analyte_list:
            first = item['test_name'] + ", " + item['manufacturer']+","+item['batch_id']
            second = item['cal_id']
            self.list.add_widget(TwoLineListItem(text=first, secondary_text=second, on_release=self.start_test))
        self.scroll.add_widget(self.list)
        self.analyte_layout.add_widget(self.scroll)
        self.ids['scroll_layout'].add_widget(self.analyte_layout)
        pass
    def addanalyte(self, *args):
        self.manager.current = 'addanalyte'
        pass
    def start_test(self, TwoLineListItem):
        self.analyte = TwoLineListItem.text
        self.calibration_data = TwoLineListItem.secondary_text
        if (self.id == 'blood_profile'):
            content = "instruction1.png"
        elif (self.id == 'CancerMarkers'):
            content = "instruction1.png"
        elif (self.id == 'CardiacPanel'):
            content = "instruction1.png"
        elif (self.id == 'FertilityPanel'):
            content = "instruction1.png"
        elif (self.id == 'InfectiousDiseases'):
            content = "instruction1.png"
        elif (self.id == 'Inflammation'):
            content = "instruction1.png"
        elif (self.id == 'NeonatalSepsis'):
            content = "instruction1.png"
        elif (self.id == 'STDPanel'):
            content = "instruction1.png"
        instruction = self.manager.get_screen('instruction')
        instruction.ids['image'].source = content
        self.manager.current='instruction'
        pass
    pass

class instruction(Screen):
    pass

class main_reqid(Screen):
    def __init__(self, **kwargs):
        super(main_reqid, self).__init__(**kwargs)
        pass
    def on_pre_enter(self):
        self.ids['keyboard'].lay.text = ""
        self.requisition = ""
        pass
    def get_req(self):
        self.requisition = self.ids['keyboard'].lay.text or ""
        self.manager.current='main_calid'
    pass


class main_calid(Screen):
    def __init__(self, **kwargs):
        super(main_calid, self).__init__(**kwargs)
        pass
    def on_pre_enter(self):
        analytepage = self.manager.get_screen('analytepage')
        self.ids['keyboard'].lay.text = analytepage.calibration_data
        self.test_name = analytepage.analyte
        self.test_batch = ""
        self.cal_id = analytepage.calibration_data
        self.cal_date = ""
        self.lines = 0
        self.req = ""
        self.concentration = ""
        self.captured_image = ""
        self.roi_image = ""
        self.error = None
        self.value = ""
        pass
    def get_cal(self):
        self.cal_details = self.ids['keyboard'].lay.text or ""
        if(self.cal_details == ""):
            self.model_dialog = MDDialog(text="Calibration ID is required")
            self.model_dialog.open()
            return
        
        try:
            self.captured_image = camcapture(self.req)
        except Exception as e:
            print(e)
            if not self.error:
                self.error = MDDialog(text="Could not capture image")
            self.error.open()
        try:
            if (self.id == 'CardiacPanel'):
                test = self.test_name
                print(test.split(',')[0])
                if test.split(',')[0] =='CKMB/MYO/TnI combo':
                   self.value = val_cardic_combo(self.captured_image)
                   #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                   self.show_results_cardiaccombo()
                else:
                   self.roi_image = roi_singlecard(self.captured_image)
                   array = scan_card(self.roi_image)
                   self.value = val_card(array, 2, 1, self.test_name, self.cal_id)
                   #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                   self.show_results_single()
            elif (self.id == 'blood_profile'):
                test = self.test_name
                if test.split(',')[0] == 'TSH (uIU/ml)':
                    self.roi_image = roi_singlecard(self.captured_image)
                    array = scan_card(self.roi_image)
                    self.value = (array, self.name, 2, 1, self.cal_id)
                    self.show_results_single() 
                else:
                   self.roi_image = roi_singlecard(self.captured_image)
                   array = scan_card(self.roi_image)
                   self.value = val_card(array, 2, 1,self.test_name, self.cal_id)
                   #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                   self.show_results_single()            
            elif (self.id == 'CancerMarkers'):
                test = self.test_name
                if test.split(',')[0] == "Fecal Occult Blood":
                    self.roi_image = roi_singlecard(self.captured_image)
                    array = scan_card(self.roi_image)
                    self.value = val_card(array, 2, 1,self.test_name,self.cal_id)
                #    self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                    self.show_results_single()
                else:
                   self.roi_image = roi_singlecard(self.captured_image)
                   array = scan_card(self.roi_image)
                   self.value = val_card(array, 2, 1, self.test_name, self.cal_id)
                 #  self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                   self.show_results_single()
            elif (self.id == 'FertilityPanel'):
               self.roi_image = roi_singlecard(self.captured_image)
               array = scan_card(self.roi_image)
               self.value = val_card(array, 2, 1,self.test_name, self.cal_id)
               #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
               self.show_results_single()
            elif (self.id == 'Inflammation'):
               self.roi_image = roi_singlecard(self.captured_image)
               array = scan_card(self.roi_image)
               self.value = val_card(array, 2, 1,self.test_name, self.cal_id)
               #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
               self.show_results_single()               
            elif (self.id == 'NeonatalSepsis'):
               self.roi_image = roi_singlecard(self.captured_image)
               array = scan_card(self.roi_image)
               self.value = val_card(array, 2, 1,self.test_name,self.cal_id)
               #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
               self.show_results_single()
            elif (self.id == 'STDPanel'):
                test = self.test_name
                if test.split(',')[0] =='HIV':
                    self.roi_image = roi_singlecard(self.captured_image)
                    array = scan_card(self.roi_image)
                    self.value = HIV(array, 3, 1)
                #    self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                    self.show_results_single()
                else:
                    self.roi_image = roi_singlecard(self.captured_image)
                    array = scan_card(self.roi_image)
                    self.value = infec(array, 2, 1)
                 #   self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                    self.show_results_single()
            elif (self.id == 'InfectiousDiseases'):
                test = self.test_name
                print(test.split(',')[0])
                if test.split(',')[0] =='Dengue (NS1 and Ag+Ab)':
                    self.value = val_dengue_combo((self.captured_image))
                  #  self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                    self.show_results_dengue()
                elif test.split(',')[0] == 'Malaria Ag (p.f/Pan)':
                    self.roi_image = roi_singlecard(self.captured_image)
                    array = scan_card(self.roi_image)
                    self.value = malaria(array, 3, 1)
                #    self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                    self.show_results_single()
                elif test.split(',')[0] == 'S.typhi (IgG/IgM)':
#                     cv2.imwrite(get_path('captured/croped2.jpg'),self.captured_image[50:480, 280:-350])
                    self.roi_image = roi_segment(self.captured_image[:480, 280:-350])
                    print("self.roi_image",self.roi_image)
                    print(type(self.roi_image))
#                     cv2.imwrite(get_path('captured/croped2.jpg'),self.captured_image[:480, 300:-600])
                    array = scan_card(self.roi_image)
                    self.value = styphi(array, 3, 1)
                    print('inst',self.value)
                #    self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                    self.show_results_single()
                    
                else:
                   self.roi_image = roi_singlecard(self.captured_image)
                   array = scan_card(self.roi_image)
                   self.value = infec(array, 2, 1)
                   #self.testlist = (self.test_name, self.test_batch, self.cal_id, self.cal_date, self.value, self.captured_image)
                   self.show_results_single()
        except Exception as e:
             print(e)
             self.error = MDDialog(text="Err 01: Could not analyze test")
             self.error.open()           
        pass

    def show_results_single(self):
        result_page = self.manager.get_screen('test_result_single')
        test_time = str(datetime.now().replace(microsecond=0))
        result_page.ids['test_name'].text = self.test_name
        result_page.ids['test_time'].text = test_time 
        result_page.ids['req_id'].text = self.req
        result_page.ids['test_name'].text = "Test: "+self.test_name
        result_page.ids['test_batch_id'].text = "Batchid: "+self.test_batch
        result_page.ids['test_cal_id'].text = "Cal_id: "+self.cal_id
        result_page.ids['test_cal_date'].text = "Cal_date: "+self.cal_date
        result_page.ids['test_value'].text = "Value: " + self.value
        result_page.ids['test_image'].source = get_path('captured/roi.jpg')
        result_page.ids['chart_image'].source = get_path('captured/peaks1.png')
        result_page.ids['test_image'].reload()
        result_page.ids['chart_image'].reload()
#         with open(r'/home/pi/viewdx/results.csv', 'a', newline='') as csvfile:
#             fieldnames = ['TestName','TestTime','Req_id', 'Value']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerow({'TestName':self.test_name, 'TestTime':test_time,'Req_id':self.req, 'Value':self.value})
#             csvfile.close()
        self.manager.current = 'test_result_single'
    pass

    def show_results_dengue(self):
        result_page = self.manager.get_screen('test_result_virdict4')
        test_time = str(datetime.now().replace(microsecond=0))
        result_page.ids['test_name'].text = "Test: DENGUE COMBO"
        result_page.ids['test_batch_id'].text = "Batchid: "+self.test_batch
        print(self.value)
        result_page.ids['test_value'].text = "Raw Value: " + self.value
        result_page.ids['test_image'].source = get_path('captured/dc.jpg')
        result_page.ids['test_image'].reload()
        result_page.ids['chart_image1'].source = get_path('captured/peaks1NS1.png')
        result_page.ids['chart_image2'].source = get_path('captured/peaks1AgAb.png')
        result_page.ids['chart_image1'].reload()
        result_page.ids['chart_image2'].reload()
#         with open(r'/home/pi/viewdx/results.csv', 'a', newline='') as csvfile:
#             fieldnames = ['TestName','TestTime','Req_id', 'Value']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerow({'TestName':self.test_name, 'TestTime':test_time,'Req_id':self.req, 'Value':self.value})
#             csvfile.close()
        self.manager.current = 'test_result_dengue'
        pass

    def show_results_cardiaccombo(self):
        result_page = self.manager.get_screen('test_result_cardiaccombo')
        test_time = str(datetime.now().replace(microsecond=0))
        result_page.ids['test_name'].text = "Test: cardiaccombo"
        result_page.ids['test_batch_id'].text = "Batchid: "+self.test_batch
       # result_page.ids['test_cal_id'].text = "Cal_id: "+self.cal_id
        #result_page.ids['test_cal_date'].text = "Cal_date: "+self.cal_date
        print(self.value)
        result_page.ids['test_value'].text = "Raw Value: " + self.value[0]+', '+self.value[1]+', '+self.value[2]
        result_page.ids['test_image'].source = get_path('captured/cc.jpg')
        result_page.ids['test_image'].reload()
        result_page.ids['chart_image1'].source = get_path('captured/peaks1ckmb.png')
        result_page.ids['chart_image2'].source = get_path('captured/peaks1myo.png')
        result_page.ids['chart_image3'].source = get_path('captured/peaks1tnI.png')
#         result_page.ids['chart_image4'].source = get_path('captured/peaks4.png')
        result_page.ids['chart_image1'].reload()
        result_page.ids['chart_image2'].reload()
        result_page.ids['chart_image3'].reload()
#         result_page.ids['chart_image4'].reload()       
#         with open(r'/home/pi/viewdx/results.csv', 'a', newline='') as csvfile:
#             fieldnames = ['TestName','TestTime','Req_id', 'Value']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerow({'TestName':self.test_name, 'TestTime':test_time,'Req_id':self.req, 'Value':self.value})
#             csvfile.close()
        self.manager.current = 'test_result_cardiaccombo'
        pass
    pass

class test_result_single(Screen):
    def __init__(self, **kwargs):
        super(test_result_single, self).__init__(**kwargs)
    pass

class test_result_dengue(Screen):
    def __init__(self, **kwargs):
        super(test_result_dengue, self).__init__(**kwargs)
    pass
class test_result_cardiaccombo(Screen):
    def __init__(self, **kwargs):
        super(test_result_cardiaccombo, self).__init__(**kwargs)
    pass


class viewdx(MDApp):
    
    dialog = None
    def build(self):
       # Window.size = (800, 480)
        Window.fullscreen = 'auto'
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.primary_hue = "900"
        self.theme_cls.accent_palette = 'Cyan'
        self.theme_cls.accent_hue = '900'
        self.error = None
        
        screen_manager = ScreenManager()
        screen_manager.add_widget(first_screen(name='first_screen '))
        #INITIALIZATION
        screen_manager.add_widget(QR_scan(name='QR_scan'))
        #sm.add_widget(search_menu(name='search_menu'))
        screen_manager.add_widget(mainsplash(name='mainsplash'))
        screen_manager.add_widget(homepage(name='homepage'))
        screen_manager.add_widget(SearchScreen(name='search'))
        screen_manager.add_widget(analytepage(name='analytepage'))                                                                                                       
        screen_manager.add_widget(instruction(name='instruction'))
        screen_manager.add_widget(main_reqid(name='main_reqid'))
        screen_manager.add_widget(main_calid(name='main_calid'))
        screen_manager.add_widget(test_result_single(name='test_result_single'))
        screen_manager.add_widget(test_result_dengue(name='test_result_dengue'))
        screen_manager.add_widget(test_result_cardiaccombo(name='test_result_cardiaccombo'))
        screen_manager.add_widget(setup_network(name='setup_network'))
        screen_manager.add_widget(device_infopage(name='device_infopage'))
        screen_manager.add_widget(call_support(name='call_support'))

        
        return screen_manager
    
          
    def on_left_action(self):
        
        self.root.current= 'search'


    #--------------functions
    def gotoprevious(self):
        self.root.current = self.root.previous()
        pass
    def featureerror(self):
        if not self.dialog:
            self.dialog = MDDialog(text="This feature isn't enabled for this device.")
        self.dialog.open()
        pass
    def gohome(self):
        self.root.current = "homepage"
    def setwifi(self):
        self.root.current = "setup_network"
        pass
    def deviceinfo(self):
        self.root.current = "device_infopage"
    def callsupport(self):
        self.root.current = "call_support"
        pass
    def update(self):
        self.featureerror()

    def shutdevice(self):
        pass
    def changeto(self):
        self.root.current = self.root.next()
    def shutdevice(self):
        
        if not self.dialog:
            self.dialog = MDDialog(
                text="Shutdown the system?",
                buttons=[
                    MDFlatButton(text="No", on_press=lambda _:self.dialog.dismiss()), MDFlatButton(text="Yes",on_press=lambda _:self.shutdown()),
                ],
            )
        self.dialog.open()
        pass
    def shutdown(*args):
        os.system("shutdown now -h")
    def QR_scan(self):
        try:
            captureQR()
            QR_output = scan_qr_code()
            if QR_output == True:
                
                self.dialog = MDDialog(
                    text="QR Code Verified!",
                    buttons=[
                        MDFillRoundFlatButton(text="Proceed", on_press=lambda _:self.dialog.dismiss()),
                    ],
                )
                self.dialog.open()
                self.changeto()
            else:
                
                self.dialog = MDDialog(
                    text="Could not read QR code",
                    buttons=[
                        MDFillRoundFlatButton(text="Try Again", on_press=lambda _:self.dialog.dismiss()),
                    ],
                )
                self.dialog.open()
                
        except Exception as e:
            print(e)
            if not self.error:
                self.error = MDDialog(text="Card Not Found")
            self.error.open()
      
             
viewdx().run()