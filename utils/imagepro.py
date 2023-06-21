from picamera import PiCamera
import cv2
import numpy as np
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import time
from datetime import date, datetime
from time import sleep
from scipy.signal import find_peaks, peak_widths, peak_prominences, savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve
from utils.constants import get_path
import traceback

##-----------------------------------------------------camcapture function-------------------------------------------------------
def camcapture(id):
    camera = PiCamera()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(40, GPIO.OUT)
    GPIO.output(40, True)
    GPIO.cleanup

    camera.start_preview()
    time.sleep(3)
    camera.capture(get_path('captured/capturedimage'+str(id)+'.jpg'))
    camera.stop_preview()
    GPIO.output(40,False)
    input_image = cv2.imread(get_path('captured/capturedimage'+str(id)+'.jpg'))
    camera.close()
    return input_image
#------------------------------------------------Baseline correction ----------------------------------------------------------
## baseline correction 

def baseline_correction(y, lam, p):
    L = len(y)
    D = sparse.diags([1,-2,1],[0,-1,-2],shape=(L,L-2))
    D = lam*D.dot(D.transpose())
    w = np.ones(L)
    W = sparse.spdiags(w,0,L,L)
    for i in range(1,10):
        W.setdiag(w)
        Z = W+D
        z = spsolve(Z, w*y)
        w = p*(y>z)+(1-p)*(y<z)
    return z
##-------------------------------------------------------------------------------------------------------------------------------
def takefourth(array):
    return array[4]
def takefirst(array):
    return array[1]
##-------------------------------------------------rgb2cmk-----------------------------------------------------------------------
def rgb2cmk(img):
    bgrdash = img.astype(np.float64)/255
    K = 1 - np.max(bgrdash,axis=2)
    C = (1-bgrdash[...,2] -K)/(1-K)
    M = (1-bgrdash[...,1] -K)/(1-K)
    Y = (1-bgrdash[...,0] -K)/(1-K)
    CMY = (np.dstack((C,M,Y))*255).astype(np.uint8)
    return CMY
#------------------------------------------------------- roi segmentations ------------------------------------------------------
def get_cnts(img):
    image = img.copy()
    img = cv2.GaussianBlur(img, (15,15),0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)
    sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5)
    
    abs_grad_x = cv2.convertScaleAbs(sobelx)
    abs_grad_y = cv2.convertScaleAbs(sobely)
    
    grad = cv2.addWeighted(abs_grad_x, 0.05, abs_grad_y, 0.05, 0)  
    ret, thresh = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    thresh = thresh.astype(np.uint8)
    cnts,_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)
    cv2.drawContours(img, cnts, -1, (0,255,0), 3)
    return cnts
def get_tsh(dataNew, name, lines, segid, cal_id):
    n = len(dataNew)
    base = dataNew[n-1]  
    res_array = 0-dataNew
    base_array = baseline_correction(res_array, 1000, 0.005)
    i = 0
    neg_array = []
    while(i<n):
        neg_array = np.append(neg_array, res_array[i]-base_array[i])
        i = i+1
    neg_array = neg_array[10:-10]
    peaks, properties = find_peaks(neg_array, prominence=5, distance =80)
    print('peaks',peaks)
    prominences = peak_prominences(neg_array, peaks)[0]
    print(prominences)
    plt.plot(neg_array)
    x_arr =neg_array
    plt.plot(peaks, neg_array[peaks], 'x')
    plt.savefig(get_path('captured/peaks1.png'))
    plt.close()
#     dataNew=res_array[1:-1]
    index = lines-1
    value = '0'
    try:
        if (len(prominences)==0): value = "Err 03: no control line"
        elif (len(prominences)>4): value = "Err 04: high background"
        elif (len(prominences)==index): value = "No test line detected"  
        else:
            temp = prominences[index]/ prominences[0]         
            raw_value = prominences
            print('raw value',raw_value)
            cal_value = cal_conc(round(temp,2),cal_id)
            value = cal_value 
    except Exception as e:
        traceback.print_exc()
        value = e
    return value
    

def get_peaks(dataNew, name):
    n = len(dataNew)
    base = dataNew[n-1]  
    res_array = 0-dataNew
    base_array = baseline_correction(res_array, 1000, 0.005)
    i = 0
    neg_array = []
    while(i<n):
        neg_array = np.append(neg_array, res_array[i]-base_array[i])
        i = i+1
    neg_array = neg_array[30:-30]
    len_noise = noise(neg_array)
    print(len_noise)
    peaks, properties = find_peaks(neg_array, prominence=3, width = (5,15))
    print('peaks',peaks)
    prominences = peak_prominences(neg_array, peaks)[0]
    print(prominences)
    plt.plot(neg_array)
    x_arr =neg_array[:]
    plt.plot(peaks, neg_array[peaks], 'x')
    plt.savefig(get_path('captured/peaks1.png'))
    plt.close()
    return len_noise, peaks, prominences

def get_coordinate(rect, image):
    arr1 = rect
    x1 = arr1[0]
    y1 = arr1[1]
    w1 = arr1[2]
    h1 = arr1[3]
    crop_seg = image[y1:y1+h1, x1:x1+w1]
    return crop_seg

def roi_segment(img):
    ## roi segment general
    image = img.copy()
    cnts = get_cnts(img)
    rect = []
    [img_width, img_height] = img.shape[:2]
    for c in cnts:
        epsilon = 0.01*cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,epsilon,True)
        if (len(approx)>=4):
            (x, y, w, h) = cv2.boundingRect(approx)
            cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
            rect.append((x,y,w,h,(h*w)))
    rect.sort(key=takefourth, reverse=True)
    cv2.imwrite(get_path('captured/rect.jpg'), img)
    roi_image=get_coordinate(rect[0],image)
    cv2.imwrite(get_path('captured/roi.jpg'),roi_image)
    return roi_image

#------------------------------------------------------roicardiaccombo-----------------------------------------------------------
def roi_cardiac_combo(img):
    image = img.copy()
    cnts = get_cnts(img)
    rect = []
    [img_width, img_height] = img.shape[:2]
    for c in cnts:
        if cv2.contourArea(c)>5000:
            epsilon = 0.01*cv2.arcLength(c,True)
            approx = cv2.approxPolyDP(c,epsilon,True)
            if (len(approx)>=4):
                (x, y, w, h) = cv2.boundingRect(approx)
                if y > 20:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
                    rect.append((x,y,w,h,(h*w)))
    rect = sorted(rect, key=takefirst, reverse=False)

    ckmb = get_coordinate(rect[0],image)
    cv2.imwrite(get_path('captured/ckmb.jpg'),ckmb)
    myo = get_coordinate(rect[1],image)
    cv2.imwrite(get_path('captured/myo.jpg'),myo)
    tnI = get_coordinate(rect[2],image)
    cv2.imwrite(get_path('captured/tnI.jpg'),tnI)
    return ckmb, myo, tnI
##---------------------------------------------------
def roi_dengue_combo(img):
    ## Roi for dengue combo ab IgG/IgM and NS1
    image = img.copy()
    cnts = get_cnts(img)
    rect = []
    [img_width, img_height] = img.shape[:2]
    for c in cnts:
        print('ca',cv2.contourArea(c))
        if cv2.contourArea(c)>5000:
            epsilon = 0.01*cv2.arcLength(c,True)
            approx = cv2.approxPolyDP(c,epsilon,True)
            if (len(approx)>=4):
                (x, y, w, h) = cv2.boundingRect(approx)
                if y > 20:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
                    rect.append((x,y,w,h,(h*w)))
    rect = sorted(rect, key=takefirst, reverse=False)
    AgAb = get_coordinate(rect[0],image)
    cv2.imwrite(get_path('captured/AgAb.jpg'),AgAb)
    NS1 = get_coordinate(rect[1],img)
    cv2.imwrite(get_path('captured/NS1.jpg'),NS1)
    return AgAb, NS1
##------------------------------------------------------------------------------------------------------------------------------
def roi_singlecard(image):
    ## roi for single card test ##
    img = image[0:480, 300:510]
    cv2.imwrite(get_path('captured/croped.jpg'),img)
    cropped = roi_segment(img)
    return cropped
#----------------------------------------------------------------Scan Card ---------------------------------------------------#
def scan_card(segment):
    input = segment
    #input = cv2.cvtColor(segment, cv2.COLOR_BGR2LAB)
    [a, b] = input.shape[:2]
    result_array = []
    x = 1
    y = 1
    sum = 0
    while (y<(a-20)):
        line = input[y:y+3, x:x+b]
        avg_color_per_row = np.average(line, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        sum = avg_color[0]+avg_color[1]+avg_color[2]
        #sum_b = avg_color[0]
        #sum_g = avg_color[1]
        #sum_r = avg_color[2]
        result_array = np.append(result_array, sum)
        y = y+1
    return result_array
#--------------------------------------------------------calculate value --------------------------------------------------------
def noise(neg_array):
    check_noise, properties = find_peaks(neg_array)
    noise1 = peak_prominences(neg_array, check_noise)[0]
    if len(noise1)<50:
        if (max(noise1)-min(noise1)) < 20:
            len_noise = 51
        else: len_noise = len(noise1)
    else: len_noise = len(noise1)
    print('noise value', len(noise1), min(noise1),max(noise1))
    return len_noise

def val_card(result_array, lines, segid, name, cal_id):
    dataNew=result_array[1:-1]
    len_noise, peaks, prominences = get_peaks(dataNew, name)
    index = lines-1
    value = '0'
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if len(prominences)==0: value = "Err 02: no control line"
            elif 10>len(prominences)>3: value = "Err 03: high background"
            elif len(prominences)==index:
                value = "Below detecable limits"  
            else:
                test_value = (round(prominences[index],2))
                control_value = (round(prominences[0],2))
                #value = test_value+':'+control_value
                try:
                    temp = test_value/control_value
                    cal_value = cal_conc(round(temp,2),cal_id)
                    value = cal_value
                except Exception as e:
                    value = str(e)        
    except Exception as e:
        print(e)
        value = "Err 04: Test not detected"
    print('value',value)
    return value

def val_cardic_combo(image):
    cv2.imwrite(get_path('captured/cc.jpg'),image)
    ckmb, myo, tnI = roi_cardiac_combo(image)
    array1 = scan_card(ckmb)
    array2 = scan_card(myo)
    array3 = scan_card(tnI)
    result = []
    value = []
    result = np.append(result, infec(array1, 2, 0))
    result = np.append(result, infec(array2, 2, 1))
    result = np.append(result, infec(array3, 2, 2))
    print('results',result)
    if "Err" not in result[0]:
        if result[0] == "Positive":
            value.append('>5 ng/ml')
        else:value.append('<5 ng/ml')
    else: value.append(result[0])
    if "Err" not in result[1]:
        if result[1] == "Positive":
            value.append('>50 ng/ml')
        else:value.append('<50 ng/ml')
    else: value.append(result[2])
    if "Err" not in result[2]:
        if result[2] == "Positive":
            value.append('>0.5 ng/ml')
        else:value.append('<0.5 ng/ml')
    else: value.append(result[2])
    return value 

##----------------------------------------------infec----------------------------------------------------------------------------
def infec(result_array, lines, segid):
    dataNew=result_array[1:-1]
    index = lines-1
    len_noise,peaks, prominences = get_peaks(dataNew, '')
    index = lines-1
    value = '0'
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if len(prominences)==0: value = "Err 02: no control line"
            elif 10>len(prominences)>3: value = "Err 03: high background"
            elif len(prominences)==1:
                value = "Negative"  
            else: value = 'Positive'       
    except Exception as e:
        print(e)
        value = "Err 04: Test not detected"
    return value
    

def HIV(result_array, lines, segid):
    dataNew=result_array[1:-1]
    len_noise, peaks, prominences = get_peaks(dataNew, 'HIV')
    value = '0'
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if (len(prominences)==0): value = "Err 03: no control line"
            elif (len(prominences)>4): value = "Err 04: high background"
            elif (len(prominences)==3): value = "Positive for HIV-1 and HIV-2"
            elif len(prominences)==1:
                value = "Negative" 
            else:
                if (peaks[1]-peaks[0])<100:
                    value = "Positive for HIV-2"
                else:
                    value = "Positive for HIV-1"
    except Exception as e:
        print(e)
        value = "Err 04: Test not detected"
    print(value)
    return value

def styphi(result_array, lines, segid):
    dataNew=result_array[1:-1]
    len_noise, peaks, prominences = get_peaks(dataNew, 'styphi')
    value = '0'
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if (len(prominences)==0): value = "Err 03: no control line"
            elif (len(prominences)>4): value = "Err 04: high background"
            elif (len(prominences)==3): value = "Positive for IgG and IgM"
            elif len(prominences)==1:
                value = "Negative" 
            else:
                if (peaks[1]-peaks[0])<100:
                    value = "Positive for IgG"
                else:
                    value = "Positive for IgM"
    except Exception as e:
#         print(e)
        value = "Err 04: Test not detected"
    print(value)
    return value


def malaria(result_array, lines, segid):
    dataNew=result_array[1:-1]
    len_noise, peaks, prominences = get_peaks(dataNew, 'styphi')
    value = '0'
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if (len(prominences)==0): value = "Err 03: no control line"
            elif (len(prominences)>4): value = "Err 04: high background"
            elif (len(prominences)==3): value = "Positive for Pf and Pan"
            elif len(prominences)==1: value = "Negative" 
            else:
                if (peaks[1]-peaks[0])<100:
                    value = "Positive for Pan"
                else:
                    value = "Positive for Pf"
    except Exception as e:
#         print(e)
        value = "Err 04: Test not detected"
    print(value)
    return value
def val_dengue_combo(image):
    cv2.imwrite(get_path('captured/dc.jpg'),image)
    AgAb, NS1 = roi_dengue_combo(image)
    array_AgAb = scan_card(AgAb)
    array_NS1 = scan_card(NS1)
    dataNew_AgAb = array_AgAb[1:-1]
    dataNew_NS1 = array_NS1[1:-1]
    len_noise_AgAb, peaks_AgAb, prominences_AgAb = get_peaks(dataNew_AgAb, 'AgAb')
    len_noise_BS1, peaks_NS1, prominences_NS1 = get_peaks(dataNew_NS1, 'NS1')
    value = '0'
    value1 = '0'
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if (len(prominences_AgAb)==0): value = "Err 03: no control line"
            elif (len(prominences_AgAb)>4): value = "Err 04: high background"
            elif (len(prominences_AgAb)==3): value = "Positive for IgG and IgM"
            elif (len(prominences_AgAb) ==1): value = "Negative for IgG and IgM"
            else:
                if (peaks_AgAb[1] - peaks_AgAb[0])<100:
                    value = "Positive for IgG"
                else:
                    value = "Positive for IgM"
    except Exception as e:
#          print(e)
        value = "Err 04: Test not detected"
    try:
        if len_noise>50:
            value = "Err 01: could not detect sample"
        else:
            if (len(prominences_NS1)==0): value1 = "Err 03: no control line"
            elif (len(prominences_NS1)>3): value1 = "Err 04: high background"
            elif (len(prominences_NS1)==2): value1 = "Positive for NS1"
            elif (len(prominences_NS1) == 1): value1 = "Negative"
    except Exception as e:
#          print(e)
        value1 = "Err 04: Test not detected"
    return ('Ag+Ab: ' + value + " , "+'NS1: ' + value1)

#--------------------------------------------------------------------------------------------------------------------------------
def cal_conc(temp,cal_id):
    try:
        y = float(temp)
        print(y)
        #the calibration text needs to be f/c1/c2:mm/yy:l
        details_cal = cal_id.split("/")
        p_factor = int(details_cal[0])
        const1 = float(details_cal[1])/100
        const2 = float(details_cal[2])/100
        #for p_factor = 1 (linear curve); y = const1*x+const2
        #for p_factor = 2 (log-linear curve); y = const1*ln(x)+const2
        #for p_factor = 3 (power curve); y = const1*x^const2
        if (p_factor==1):
            res = (y - const2)/const1
        elif (p_factor==2):
            temp = ((y - const2)/const1)
            res = np.exp(temp)
        elif (p_factor==3):
            temp = np.log(y/const1)/const2
            res = pow(10,temp)
        if res>0 : result = str(round(res, 2))
        else: result = "0"
    except Exception as e:
        traceback.print_exc()
        result = 'could not read test'
        print(e)
    return result    