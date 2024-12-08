import pickle
import random
import uuid
import json
import threading
import time
import os
import sys
from kafka import KafkaProducer  
from kafka import KafkaConsumer

BOOTSTRAPIP = "192.168.5.39:9092"
PRODUCERTOPIC = "images"
CONSUMERTOPIC = "results"

if(len(sys.argv) == 2):
    BOOTSTRAPIP = sys.argv[1]
    print("Using provided bootstrap ip: " + BOOTSTRAPIP)
else:
    print("Using default bootstrap ip: " + BOOTSTRAPIP)



#reads a "pickled" file and returns a dictionary with its data
def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

data = unpickle("cifar-10-batches-py/data_batch_1")
labelNames = unpickle("cifar-10-batches-py/batches.meta")[b"label_names"]

#holds the UUIDs of images that this producer has sent, as well as the times they were sent
sentIDs = {}
#lock fo sentIDs since it is thread shared
sentIDsLock = threading.Lock()

#label the data in CIFAR-10 dataset
for i in range(0, len(labelNames)):
    labelNames[i] = labelNames[i].decode("utf-8")

#add random csv noise to an image
#image is formatted as an array of rgb values
def noise(image):
    for i in range(0, len(image)):
        val = image[i]
        val += random.randint(-5,5)
        if(val < 0):
            val = 0
        elif(val > 255):
            val = 255
        image[i] = val

#gets the average value of the pixels immediately surrounding the one
#at the given index
def getRadAvg(image, index):
    nums = [image[index]]

    if((index % 1024) > 0):
        nums.append(image[index-1])
    if((index % 1024) > 31):
        nums.append(image[index-32])
    if((index % 1024) < 1023):
        nums.append(image[index+1])
    if((index % 1024) < 991):
        nums.append(image[index+32])

    avg = int(sum(nums) / len(nums))
    if(avg < 0):
        avg = 0
    elif(avg > 255):
        avg = 255

    return avg

#Applies a gaussian blur to an image with a radius of 1 pixel
def blur(image):
    for i in range(0, len(image)):
        image[i] = getRadAvg(image, i)

#fetches a random CIFAR-10 image, adds noise, blurs it,
#packs it into a JSON file, and returns it
def getRandomImage():
    index = random.randint(0,9999)

    imageData = data[b'data'][index].tolist()
    noise(imageData)
    blur(imageData)
    label = labelNames[data[b"labels"][index]]
    return [imageData, label]
    
#creates a producer and sends images at the specified frequency, the specified number of times
#will produce images indefinitely if numImages = 0
def sender(frequency=1, numImages = 0):

    producer = KafkaProducer(bootstrap_servers=BOOTSTRAPIP, acks=1)
    waitTime = 1/frequency
    ID = uuid.uuid4()

    def doSend():
        img = getRandomImage()
        
        obj = {
        "ID": str(ID),
        "label": img[1],
        "data": img[0]
        }
        outText = json.dumps(obj)
                
        sentIDsLock.acquire()
        sentIDs[str(ID)] = int(time.perf_counter_ns() / 1000000)
        sentIDsLock.release()
                
        producer.send (PRODUCERTOPIC, value=bytes (outText, 'ascii'))
        producer.flush ()
        time.sleep(waitTime)
        
    if numImages == 0:
        while(True):
            doSend()
    else:
        for i in range(0, numImages):
            doSend()

def e2eTimer():
    consumer = KafkaConsumer (bootstrap_servers=BOOTSTRAPIP)
    consumer.subscribe (topics=[CONSUMERTOPIC])
    
    file = open("e2elatency.csv", "a+") #opens file in append mode. creates it if DNE
    
    for msg in consumer:
        print("received message: " + msg.value.decode("utf-8"))
        receivedTimeMS = int(time.perf_counter_ns() / 1000000)
        msgDict = json.loads(msg.value.decode("utf-8"))
        receivedID = msgDict["ID"]
        print("Received message with ID: " + receivedID)
        
        sentIDsLock.acquire()
        if receivedID in sentIDs:
            print("WE HAVE A MATCH")            
            sentTimeMS = sentIDs[receivedID]
            del sentIDs[receivedID]
            #release the lock here so the sender thread doesn't have to wait for a 
            #lengthy file write operation
            sentIDsLock.release()
            file.write(f"\n{receivedID}, {receivedTimeMS - sentTimeMS}")
            file.flush()
            os.fsync(file.fileno())
        else:
            sentIDsLock.release()

def main():

    #receiver = threading.Thread(target = e2eTimer, args = [])
    producer = threading.Thread(target = sender, args = [])
    print("starting receiver")
    receiver.start()
    print("starting producer")
    producer.start()

if __name__=="__main__":
    main()
