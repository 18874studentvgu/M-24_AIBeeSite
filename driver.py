import cv2
import tensorflow as tf
import numpy as np
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from predictBee import detect_and_classify_bees
print ("** Primary Prediction stuff loaded")

try:
    from Object_Detection_yolo import detect
    YOLO_AVAILABLE=True
    print ("** YOLOv7 Prediction model loaded")
except:
    NO_YOLO_MESSAGE = "Cannot initialized YOLOv7 component, using OpenCV object counting and circumscription instead.\n(Re-upload this image to re-run the prediction)"
    import warnings
    warnings.warn(NO_YOLO_MESSAGE)
    YOLO_AVAILABLE=False
    
from pymongo import MongoClient
client = MongoClient("localhost", 27017)
print ("** Database connected")
db = client.prediction_database
collection = db.img_classification

def run(fileEvent):
    print (fileEvent)
    _, file_name = os.path.split(fileEvent.src_path)
    
    try:
        #predict image
        if YOLO_AVAILABLE:
            bboxes, yolo_image, image = detect(fileEvent.src_path)
        else: 
            # if no yolo, read image using openCV 
            # so that detect_and_classify_bees can work
            yolo_image = image = cv2.imread(fileEvent.src_path)
            bboxes = {}
        results = detect_and_classify_bees(image)
    except KeyboardInterrupt:
        print ("KeyboardInterrupted\n")
        raise
    except BaseException as e:
        # catch that one pesky exception where an image of non-standar size is fed to the YOLOv7 model
        # broaden to catch ANY pesky exception during the image reading + prediction period
        import datetime
        time = str(datetime.datetime.now())
        img_path = os.path.join('..','upload',file_name)
        record = {
            "msg": f'Error @ {time}: {str(e)}\n(You found a bug! Maybe try another pic?)',
            "prediction": '',
            "reportPath": fileEvent.src_path,
            "statistics": {}
            
        }
        collection.update_one({'_id':file_name},{"$set":record},upsert=True)
        import traceback
        traceback.print_exc()
        # print (e) # uncomment this to debug the code
        print ("....Uh oh\n")
        return
    
    #get the bee statisctics thingo
    num_bee_norm=num_bee_pollen=num_bee_varroa=num_bee_cooling=num_wasp = 0
    
    classification_keys = ['varroa', 'pollen', 'cooling', 'wasp']
    stat_dict = {k:0 for k in classification_keys}
    
    stat_dict['normal'] = 0
    
    stat_dict['total'] = max( len(bboxes), len(results))
    
    for _, _, classifications in results:
        if(len(classifications)==0):
            continue
        for k in classification_keys:
            stat_dict[k] += int(k in classifications)
    
    stat_dict['normal'] =  stat_dict['total'] - sum(stat_dict[k] for k in classification_keys)
    
    #generate the report
    fig = plt.figure(figsize=(9,16),layout='constrained')
    (top_fig, midd_fig, bottom_fig) = fig.subfigures(3, 1,height_ratios=(6,1,8))
    

    display_img = yolo_image
    for pos, _, classifications in results:
        if not(YOLO_AVAILABLE): cv2.ellipse(display_img, pos, (0, 0, 255), 2)
        label = (''.join(c[0] for c in classifications)).upper()
        cv2.putText(display_img, label, (int(pos[0][0]), int(pos[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 250, 255), 2)
    

    # put the image on top
    somebox=top_fig.subplots(1, 1)
    somebox.imshow(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB))
    somebox.axis('off')
    somebox.set_title("V: varroa, P: pollen', C: cooling, W: wasp")
    
    total_bees = stat_dict['total'] - stat_dict['wasp']
    l = lambda k: f'{stat_dict[k]}/{total_bees}' 
    table_stat = [['Bees detected','Varroa rat.','Cooling rat.','Pollen rat.','Wasp'],
                  [total_bees, l('varroa'), l('cooling'), l('pollen'), stat_dict['wasp']]]
    # some stat as a table at the middle
    ax_table =  midd_fig.add_subplot(111)
    table = ax_table.table(table_stat, cellLoc='center', loc='center')
    table.scale(1, 2)
    ax_table.axis("off")
    ax_table.set_title("Statistics")
    
    # add some tables and stuff at the bottom
    subplot0 = bottom_fig.add_subplot(221)
    subplot0.bar(list(stat_dict.keys()),list(stat_dict.values()))
    subplot0.set_title("Overall detection")  
    
    subplot1 = bottom_fig.add_subplot(222)
    KEYS = ['normal', *classification_keys]
    subplot1.pie([stat_dict[k] for k in KEYS],labels=KEYS)
    subplot1.set_title("Overall Composistion")
    
    num_bees_not_cooling = len(results) - stat_dict['wasp'] - stat_dict['cooling']
    plot2_data = [stat_dict['cooling'],num_bees_not_cooling]
    subplot2 = bottom_fig.add_subplot(223)
    subplot2.pie(plot2_data,labels=['cooling','no'])
    subplot2.set_title("R da bee cooling?")
    
    num_bees_not_infected = len(results) - stat_dict['wasp'] - stat_dict['cooling']
    plot3_data = [stat_dict['varroa'],num_bees_not_infected]
    subplot3 = bottom_fig.add_subplot(224)
    subplot3.pie(plot3_data,labels=['varroa','no'])
    subplot3.set_title("R da bee dying?")

    #save the report
    report_path = os.path.join('public','output',file_name + '.svg')
    plt.savefig(report_path)
    
    messages = None if YOLO_AVAILABLE else NO_YOLO_MESSAGE
    #TODO: find someways to make it scaleable incase of more message were to be added
    #
    record = {
        "msg": messages,
        "prediction": '',
        "reportPath": report_path,
        "statistics": stat_dict
        
    }
    collection.update_one({'_id':file_name},{"$set":record},upsert=True)

