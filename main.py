from tracemalloc import start
from venv import logger
from issSpeed import IssSpeed
from datetime import datetime, timedelta
from time import sleep
import logzero
from logzero import logger

# test
import os


logzero.logfile('logs.log')


# DEFINE FUNCTIONS

# test function
def loadPhotos():
    imgList = []


    for img in os.listdir('test\dataset1'):
        imgPath = os.path.join('test\dataset1', img)
        imgList.append(imgPath)

        if not os.path.exists(imgPath):
            print('path err')



    return imgList



def takePhoto(imgList, index):
    # take photo with picamera
    # save it
    # imgPath = f'test/img/img{imgNum}.jpg'

    logger.info(f'photo taken, index: {index}')

    return imgList[index]


def takePhotoRpi(index):
    from picamera import PiCamera


    cam = PiCamera()
    cam.resolution = (4056, 3040)

    location = f'img/image{index}.jpg'

    try:
        cam.capture(location)
    
    except Exception as e:
        logger.error(e)


    logger.info(f'photo taken, index: {index}')


    return imgList[index]
    



def countData(imgNum, imgPath, lastImgPath):
    pairId = imgNum / 2

    # get speed
    imgPair = IssSpeed(lastImgPath, imgPath)
    logger.info(f'Comparing images: {lastImgPath} and {imgPath}')
    speed = imgPair.calculateSpeed()


    # Error
    if isinstance(speed, str):
        print(speed) # print error
        return False
    
    
    # Ok
    else:
        return {'speed':speed, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId, 'standardDeviation':imgPair.filteredStandardDeviation, 'angleMedianPercentage':imgPair.largestGroupPercentage, 'avgResponse':imgPair.avgKpResponse, 'maxResponse':imgPair.maxKpResponse}



# DEFINE VARIABLES
logger.info('start')
speedsList = []
testImages = []
startTime = datetime.now()
index = 0
imgList = loadPhotos() # test



# MAIN PART - take two photos, count speed, save data
while datetime.now() < startTime + timedelta(minutes=10):
    # Take photos

    if index == 0:
        img1 = takePhoto(imgList, index)
        index += 1
        # sleep(5)

    else:
        img1 = img2
        # sleep(5)

    

    img2 = takePhoto(imgList, index)
    


    # Get data
    result = countData(index, img2, img1)

    index += 1
    

    # Process data if there is not an error
    if result != False:
        # for debug log
        speedsList.append(result['speed'])

        # count average
        averageSpeed = sum(speedsList) / len(speedsList) 

        # log
        logger.info(f"Result: average: {round(averageSpeed, 4)}, speed: {round(result['speed'], 4)}, dev: {round(result['standardDeviation'], 4)}, agmp: {round(result['angleMedianPercentage'], 4)}, avgResp: {round(result['avgResponse'], 4)}, maxResp: {round(result['maxResponse'], 4)}")


        # save result
        with open('result.txt', 'w', buffering=1) as file:
            file.write(str(round(averageSpeed, 4)))
