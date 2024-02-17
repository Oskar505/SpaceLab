from issSpeed import IssSpeed
import time

# test
import os



def takePhoto():
    # take photo with picamera
    # save it
    # imgPath = f'test/img/img{imgNum}.jpg'
    imgList = []


    for img in os.listdir('test\dataset1'):
        imgPath = os.path.join('test\dataset1', img)
        imgList.append(imgPath)

        if not os.path.exists(imgPath):
            print('path err')



    return imgList



def countData(imgNum, imgPath, lastImgPath):
    pairId = imgNum / 2

    # get speed and unusable parts data
    imgPair = IssSpeed(lastImgPath, imgPath)
    # imgPair.getAllExif()
    speed = imgPair.calculateSpeed()


    # Error
    if isinstance(speed, str):
        print(speed)
        return False
    
    
    # Ok
    else:
        clouds, water = imgPair.calculateUnusablePercentage()

        return {'speed':speed, 'clouds':clouds, 'water':water, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId, 'standardDeviation':imgPair.filteredStandardDeviation, 'angleMedianPercentage':imgPair.largestGroupPercentage, 'avgResponse':imgPair.avgKpResponse, 'maxResponse':imgPair.maxKpResponse}




lastImgPath = ''
results = []
speedsList = []
cloudsList = []
waterList = []
testImages = []
unixTime = int(time.time())



imgList = takePhoto()

for i in range(0, len(imgList), 2):
    result = countData(i, imgList[i+1], imgList[i])
    

    if result != False:
        speedsList.append(result['speed'])
        cloudsList.append(result['clouds'])
        waterList.append(result['water'])

        # count average
        averageSpeed = sum(speedsList) / len(speedsList) 

        print(f"average: {round(averageSpeed, 4)}, speed: {round(result['speed'], 4)}, clouds: {round(result['clouds'], 2)}%, dev: {round(result['standardDeviation'], 4)}, agmp: {round(result['angleMedianPercentage'], 4)}, avgResp: {round(result['avgResponse'], 4)}, maxResp: {round(result['maxResponse'], 4)}")



# tohle pouziju v normalnim kodu, pro test pouziju for
# while unixTime + 10 > int(time.time()):
#     print(int(time.time()) - unixTime)