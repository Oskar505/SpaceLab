import os
import shutil
from numpy import diff, imag
from issSpeed import IssSpeed
import time


print(os.getcwd())

folder = os.getcwd() + '/test/imgDataset'
# folder = os.getcwd() + '/test/img'

images = []
imgNum = 2


def countData(imgNum, imgPath, lastImgPath):
    pairId = 1

    # get speed and unusable parts data
    imgPair = IssSpeed(lastImgPath, imgPath)
    speed = imgPair.calculateSpeed(debug=False)
    clouds, water = imgPair.calculateUnusablePercentage(debug=True)


    return {'speed':speed, 'clouds':clouds, 'water':water, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId}


lastImgPath = ''
lastImage = ''
results = []
speedsList = []
cloudsList = []
waterList = []
testImages = []
unixTime = int(time.time())



image = input('nazev obrazku: ')
lastImage = input('dalsi fotka: ')


imgPath = os.path.join(folder, image)
lastImgPath = os.path.join(folder, lastImage)



result = countData(imgNum, imgPath, lastImgPath)

if 'error' in str(result['speed']).lower():
    exit('Speed error')
    

speedsList.append(result['speed'])
cloudsList.append(result['clouds'])
waterList.append(result['water'])


# count average
averageSpeed = sum(speedsList) / len(speedsList)

difference = 7.66 - result['speed']
print(difference)

if abs(difference) < 0.5 and result['clouds'] < 15:
    print('good ' + str(imgNum))

elif abs(difference) < 1 and result['clouds'] < 50:
    print('ok ' + str(imgNum))

else:
    print('bad ' + str(imgNum))


print(f"average: {averageSpeed}, speed: {result['speed']}, clouds: {result['clouds']}%, water: {result['water']}%")