import cv2
import tensorflow as tf
import numpy as np
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from predictBee import detect_and_classify_bees
#IMG_SIZE = (300, 150)
#CLASSES = ['Bee','Varroa','Wasp'] # the tà đạo way
#model = tf.keras.models.load_model('SavedModel')

from Object_Detection_yolo import detect

from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client.prediction_database
collection = db.img_classification
print ('\n\n ====ready!!!====')

def run(fileEvent):
    print (fileEvent)
    #predict image
    bboxes, yolo_image, image = detect(fileEvent.src_path)
    results = detect_and_classify_bees(image)
    
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
        label = (''.join(c[0] for c in classifications)).capitalize()
        cv2.putText(display_img, label, (int(pos[0][0]), int(pos[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 250, 255), 2)
    

    # Display the image
    somebox=top_fig.subplots(1, 1)
    somebox.imshow(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB))
    somebox.axis('off')
    somebox.set_title("V: varroa, P: pollen', C: cooling, W: wasp")
    
    total_bees = stat_dict['total'] - stat_dict['wasp']
    l = lambda k: f'{stat_dict[k]}/{total_bees}' 
    table_stat = [['Bees detected','Varroa rat.','Cooling rat.','Pollen rat.','Wasp'],
                  [total_bees, l('varroa'), l('cooling'), l('pollen'), stat_dict['wasp']]]
    ax_table =  midd_fig.add_subplot(111)
    table = ax_table.table(table_stat, cellLoc='center', loc='center')
    table.scale(1, 2)
    ax_table.axis("off")
    ax_table.set_title("Statistics")
    
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
    file_name = (fileEvent.src_path).split("/")[-1]
    file_path = os.path.join('public','output',file_name + '.svg')
    plt.savefig(file_path)
    
    record = {
        "prediction": '',
        "reportPath": file_path
        
    }
    collection.update_one({'_id':file_name},{"$set":record},upsert=True)

