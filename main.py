from issSpeed import IssSpeed
import time



def takePhoto(imgNum):
    # take photo with picamera
    # save it
    imgPath = f'test/img{imgNum}.jpg'

    return imgPath



def countData(imgNum, imgPath, lastImgPath):
    pairId = imgNum / 2

    # get speed and cluds data
    imgPair = IssSpeed(lastImgPath, imgPath)
    imgPair.getTimeDifference()
    imgPair.getKeypoints()
    imgPair.calculateDist()
    speed = imgPair.calculateSpeed()
    clouds = 0


    return {'speed':speed, 'clouds':clouds, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId}




lastImgPath = ''
results = []
speedsList = []
cloudsList = []
testImages = []
unixTime = int(time.time())


for imgNum in range(7):
    imgPath = takePhoto(imgNum)

    # counting from 0, so pairs will be odd
    if imgNum % 2 != 0:

        result = countData(imgNum, imgPath, lastImgPath)
        
        speedsList.append(result['speed'])
        cloudsList.append(result['clouds'])

        # count average
        averageSpeed = sum(speedsList) / len(speedsList) 

        print(f"average: {averageSpeed}, speed: {result['speed']}")
    

    lastImgPath = imgPath




# tohle pouziju v normalnim kodu, pro test pouziju for
# while unixTime + 10 > int(time.time()):
#     print(int(time.time()) - unixTime)