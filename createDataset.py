import os
import shutil
from tokenize import String
from numpy import diff, imag
from issSpeed import IssSpeed
import time
import cv2
import numpy as np
import textwrap



print(os.getcwd())

folder = os.getcwd() + '/test/imgDataset'
# folder = os.getcwd() + '/test/img'

images = []
imgNum = 0


def countData(imgNum, imgPath, lastImgPath):
    pairId = imgNum / 2

    # get speed and unusable parts data
    imgPair = IssSpeed(lastImgPath, imgPath)
    speed = imgPair.calculateSpeed()
    clouds, water = imgPair.calculateUnusablePercentage(debug=False)

    if type(speed) == str and 'error' in speed:
        return {'speed':speed}

    else:
        return {'speed':speed, 'angleSpeed':imgPair.angleSelectedSpeed, 'devSpeed':imgPair.devSpeed, 'filteredSpeed':imgPair.filteredSpeed, 'deviation1':imgPair.standardDeviation, 'deviation2':imgPair.filteredStandardDeviation, 'largestAngleGroup':imgPair.largestGroup, 'largestAnglePercentage':imgPair.largestGroupPercentage, 'clouds':clouds, 'img1':lastImgPath, 'img2':imgPath, 'pairId':pairId, 'keypoints':len(imgPair.keypoints1), 'matches':len(imgPair.matches), 'avgKpResponse':imgPair.avgKpResponse, 'maxKpResponse':imgPair.maxKpResponse, 'matchesImg':imgPair.resizedMatches, 'cloudsImg':imgPair.resizedClouds}




def writeDataOnImage(data, imgName, imgNum, matchesImg, cloudsImg, imgQuality, matches):
    imgPath = 'test/imgDataset/' + imgName
    img = cv2.imread(imgPath)

    # Text, který chceš napsat

    # Font a velikost písma
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 2.5
    font_thickness = 3
    font_color = (0, 0, 0)  # Černá barva
    background_color = (255, 255, 255)  # Bílá barva pro pozadí

    # Získání rozměrů textu
    text_size = cv2.getTextSize(data, font, font_size, font_thickness)[0]

    # Pozice pro text v pravém spodním rohu
    text_position = (img.shape[1] - text_size[0] - 10, img.shape[0] - 10)

    # Vytvoření bílého pozadí pro text
    background = np.ones((text_size[1] + 10, text_size[0] + 10, 3), dtype=np.uint8) * background_color

    lines = textwrap.wrap(data, width=30)  # Rozdělení textu do dvou řádků
    y = 30 + text_size[1]  # Y-ová pozice pro první řádek textu

    for line in lines:
        cv2.putText(img, line, (10, y), font, font_size, font_color, font_thickness)
        y += int(text_size[1] * 1.5)  # Odstup mezi řádky


    # Získání rozměrů části obrázku pro vložení textu
    img_part = img[-background.shape[0]:, -background.shape[1]:]

    # Pokud jsou rozměry části obrázku menší než rozměry pozadí, upravíme rozměry části obrázku
    if img_part.shape[0] < background.shape[0]:
        background = background[:img_part.shape[0], :]
    if img_part.shape[1] < background.shape[1]:
        background = background[:, :img_part.shape[1]]




    folder = imgQuality

    if matches < 40:
        folder = 'veryBad'

    # save to folder
    cv2.imwrite(f'test/imagesWithData/{folder}/img{imgNum}.jpg', img)
    cv2.imwrite(f'test/imagesWithData/{folder}/img{imgNum}_matches.jpg', matchesImg)
    cv2.imwrite(f'test/imagesWithData/{folder}/img{imgNum}_clouds.jpg', cloudsImg)


    resizedImg = cv2.resize(img, (1014, 760))

    # Zobrazit obrázek s textem
    # cv2.imshow('Image with Text', resizedImg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()



lastImgPath = ''
lastImage = ''
results = []
speedsList = []
cloudsList = []
waterList = []
testImages = []
unixTime = int(time.time())

debug = True






# MAIN PART

for image in os.listdir(folder):
    imgPath = os.path.join(folder, image)


    # counting from 0, so pairs will be odd
    if imgNum % 2 != 0:

        result = countData(imgNum, imgPath, lastImgPath)

        if type(result['speed']) == str and 'error' in result['speed']:
            lastImgPath = imgPath
            lastImage = image
            imgNum = imgNum + 1

            continue
        
        speedsList.append(result['speed'])
        cloudsList.append(result['clouds'])

        # count average
        averageSpeed = sum(speedsList) / len(speedsList)

        difference = result['speed'] - 7.66
        print(difference)

        if abs(difference) < 0.5 and result['clouds'] < 15:
            if not debug:
                shutil.copy(imgPath, os.getcwd() + '/test/good/' + image)
                shutil.copy(lastImgPath, os.getcwd() + '/test/good/' + lastImage)
            
            imgQuality = 'good'
            print('good ' + image)
        

        elif abs(difference) < 1 and result['clouds'] < 50:
            if not debug:
                shutil.copy(imgPath, os.getcwd() + '/test/ok/' + image)
                shutil.copy(lastImgPath, os.getcwd() + '/test/ok/' + lastImage)
            
            imgQuality = 'ok'
            print('ok ' + image)
        

        else:
            if not debug:
                shutil.copy(imgPath, os.getcwd() + '/test/bad/' + image)
                shutil.copy(lastImgPath, os.getcwd() + '/test/bad/' + lastImage)

            imgQuality = 'bad'
            print('bad ' + image)

        
        # count differences
        
        angleDifference = result['angleSpeed'] - 7.66

        devDifference = result['devSpeed'] - 7.66

        filteredDifference = result['filteredSpeed'] - 7.66

        resultReport = f"qual: {imgQuality}, spd: {round(result['speed'], 2)}, diff: {round(difference, 2)}, aSpd: {round(result['angleSpeed'], 2)}, diff: {round(angleDifference)}, dSpd: {round(result['devSpeed'], 2)}, diff: {round(devDifference, 2)}, fSpd: {round(result['filteredSpeed'])}, diff: {round(filteredDifference)}, clds: {round(result['clouds'], 2)}%, kp: {result['keypoints']}, mt: {result['matches']}, lag: {result['largestAngleGroup'][0]}, lagp: {round(result['largestAnglePercentage'], 2)}, dev1: {round(result['deviation1'], 2)}, dev2: {round(result['deviation2'], 2)}, akpr: {round(result['avgKpResponse'], 4)}, mkpr: {round(result['maxKpResponse'], 4)}"
        print(resultReport)

        writeDataOnImage(resultReport, image, imgNum, result['matchesImg'], result['cloudsImg'], imgQuality, result['matches'])

    lastImgPath = imgPath
    lastImage = image

    imgNum = imgNum + 1






