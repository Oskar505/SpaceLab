from numpy import sort
from issSpeed import IssSpeed
from datetime import datetime, timedelta
from time import sleep
import logzero
from logzero import logger
import os



scriptDir = os.path.dirname(os.path.abspath(__file__))

logzero.logfile(os.path.join(scriptDir, 'logs.log'))



# import picamera or picamera2, on my 64bit raspberry pi i couldn't use picamera
picameraVersion = 1

try:
    from picamera import PiCamera

    cam = PiCamera()
    cam.resolution = (4056, 3040)


except:
    logger.warning("picamera couldn't be imported")

    from picamera2 import Picamera2

    picam2 = Picamera2()
    camConfig = picam2.create_still_configuration()
    picam2.configure(camConfig)
    picam2.options['quality'] = 100
    picam2.start()

    logger.info('picamera2 imported')
    picameraVersion = 2






# DEFINE FUNCTIONS

def takePhotoRpi(index):
    location = os.path.join(scriptDir, f'image{index}.jpg')

    
    if picameraVersion == 1:
        try:
            cam.capture(location)
        
        except Exception as e:
            logger.error(e)
            return False


        
    
    elif picameraVersion == 2:
        picam2.capture_file(location)
    

    logger.info(f'photo taken, index: {location}')

    return location
    



def countData(imgNum, imgPath, lastImgPath):
    pairId = imgNum / 2

    # get speed
    imgPair = IssSpeed(lastImgPath, imgPath)
    logger.info(f'Comparing images: {lastImgPath} and {imgPath}')
    speed = imgPair.calculateSpeed()


    # Error
    if isinstance(speed, str):
        if 'Filter ok' in speed: # if the result isn't good but isn't bad either
            speed = imgPair.speed
            return {'speed':speed, 'okSpeed':True, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId, 'standardDeviation':imgPair.filteredStandardDeviation, 'angleMedianPercentage':imgPair.largestGroupPercentage, 'avgResponse':imgPair.avgKpResponse, 'maxResponse':imgPair.maxKpResponse}

        else:
            return False
    
    elif imgNum == 1:
        return {'speed':speed, 'okSpeed':True, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId, 'standardDeviation':imgPair.filteredStandardDeviation, 'angleMedianPercentage':imgPair.largestGroupPercentage, 'avgResponse':imgPair.avgKpResponse, 'maxResponse':imgPair.maxKpResponse}
    
    # Ok
    else:
        return {'speed':speed, 'okSpeed':False, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId, 'standardDeviation':imgPair.filteredStandardDeviation, 'angleMedianPercentage':imgPair.largestGroupPercentage, 'avgResponse':imgPair.avgKpResponse, 'maxResponse':imgPair.maxKpResponse}


def deleteSomePhotos(photosToSave):
    directory = os.path.dirname(__file__)
    myFiles = os.listdir(directory)

    size = 0
    count = 0


    for file in myFiles:
        if file.lower().endswith('jpg'):
            size += os.path.getsize(file)
            count += 1

            if size > 241172480 and count < 42: # 230 MB
                imgPath = os.path.join(directory, file)
                os.remove(imgPath)
            
            




# DEFINE VARIABLES
logger.info('start')
speedsList = []
okSpeedsList = []
startTime = datetime.now()
index = 0 
goodResultsCount = 0
img1 = ''
imgList = []
photosToSave = []
resultLocation = os.path.join(scriptDir, 'result.txt')



# MAIN PART - take two photos, count speed, save data
while datetime.now() < startTime + timedelta(seconds=570):
    # Take photos

    if index == 0 or img1 is False:
        img1 = takePhotoRpi(index)
        index += 1
        sleep(5)

    else:
        img1 = img2
        sleep(5)

    

    img2 = takePhotoRpi(index)
    

    if img1 is False or img2 is False:
        break

    # Get data
    result = countData(index, img2, img1)

    index += 1
    

    # Process data if there is not an error
    if result != False:
        # for debug log

        # result is only ok
        if result['okSpeed'] and index != 2:
            okSpeedsList.append(result['speed'])

            if len(okSpeedsList) == 0:
                logger.error('okSpeedsList length is 0')
                continue

            # count average
            okAverageSpeed = sum(okSpeedsList) / len(okSpeedsList)

            # log
            logger.info(f"OK Result: average: {round(okAverageSpeed, 4)}, speed: {round(result['speed'], 4)}, dev: {round(result['standardDeviation'], 4)}, agmp: {round(result['angleMedianPercentage'], 4)}, avgResp: {round(result['avgResponse'], 4)}, maxResp: {round(result['maxResponse'], 4)}")

            # if there are no good results save the ok results
            if goodResultsCount == 0:
                with open(resultLocation, 'w', buffering=1) as file:
                    file.write(str(round(okAverageSpeed, 4)))


            if img1 not in photosToSave:
                photosToSave.append(img1)


        elif index == 2:
            # log
            logger.info(f"First Result: speed: {round(result['speed'], 4)}, dev: {round(result['standardDeviation'], 4)}, agmp: {round(result['angleMedianPercentage'], 4)}, avgResp: {round(result['avgResponse'], 4)}, maxResp: {round(result['maxResponse'], 4)}")

            # if there are no good results save the ok results
            if goodResultsCount == 0:
                with open(resultLocation, 'w', buffering=1) as file:
                    file.write(str(round(result['speed'], 4)))


        # result is good
        else:
            speedsList.append(result['speed'])

            if len(speedsList) == 0:
                logger.error('speedsList length is 0')
                continue

            # count average
            averageSpeed = sum(speedsList) / len(speedsList) 

            # log
            logger.info(f"Result: average: {round(averageSpeed, 4)}, speed: {round(result['speed'], 4)}, dev: {round(result['standardDeviation'], 4)}, agmp: {round(result['angleMedianPercentage'], 4)}, avgResp: {round(result['avgResponse'], 4)}, maxResp: {round(result['maxResponse'], 4)}")


            # save result
            with open(resultLocation, 'w', buffering=1) as file:
                file.write(str(round(averageSpeed, 4)))
            

            goodResultsCount += 1


            if img1 not in photosToSave:
                photosToSave.append(img1)



# delete photos
deleteSomePhotos(photosToSave)