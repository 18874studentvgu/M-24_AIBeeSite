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

from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client.prediction_database
collection = db.img_classification

def run(fileEvent):
    print (fileEvent)
    image = cv2.imread(fileEvent.src_path)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #img = tf.image.resize(img, IMG_SIZE)
    #predict image
    results = detect_and_classify_bees(image)
    # print(results)
    
    num_bee_norm=num_bee_pollen=num_bee_varroa=num_bee_cooling=num_wasp = 0
    
    keys = ['normal','varroa', 'pollen', 'cooling', 'wasp']
    stat_dict = {k:0 for k in keys}
    
    for _, _, classifications in results:
        print(len(classifications))
        if(len(classifications)==0):
            stat_dict['normal'] += 1
        else:
            for k in keys:
                stat_dict[k] += int(k in classifications)
#                
#                
#            for classification in classifications:
#                print(classification)
#                # stupid python, doen't support switch-cases
#                # or assignments in lambda
#                # or--
#                if(classification=='varroa'):
#                    num_bee_varroa += 1
#                elif(classification=='pollen'):
#                    num_bee_pollen += 1
#                elif(classification=='cooling'):
#                    num_bee_cooling += 1
#                elif(classification=='wasps'):
#                    num_wasp += 1
                
            
    print(stat_dict)
    
    #generate the report
    fig = plt.figure(figsize=(9,16),layout='constrained')
    (top_fig, bottom_fig) = fig.subfigures(2, 1,height_ratios=(6,8))
    

    ## Create a copy of the frame
    display_img = image.copy()
    # Draw ellipses on the copy of the frame
    for pos, _, classifications in results:
        cv2.ellipse(display_img, pos, (0, 0, 255), 2)
        label = ''.join(c[0] for c in classifications)
        cv2.putText(display_img, label, (int(pos[0][0]), int(pos[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    

    # Display the image
    somebox=top_fig.subplots(1, 1)
    somebox.imshow(cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB))
    somebox.axis('off')
    somebox.set_title("v: varroa, p: pollen', c: cooling, w: wasp")
    
#    
    subplot0 = bottom_fig.add_subplot(221)
    print((list(stat_dict.values())[1:],list(stat_dict.keys())[1:]))
    subplot0.bar(list(stat_dict.keys())[1:],list(stat_dict.values())[1:])
    subplot0.set_title("Overall detection")  
    
    subplot1 = bottom_fig.add_subplot(222)
    subplot1.pie(stat_dict.values(),labels=stat_dict.keys())
    subplot1.set_title("Overall Composistion")
    
    num_bees_not_cooling = len(results) - stat_dict['wasp'] - stat_dict['cooling']
    plot2_data = [stat_dict['cooling'],num_bees_not_cooling]
    print((plot2_data, len(results),stat_dict['wasp'],stat_dict['cooling']))
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

