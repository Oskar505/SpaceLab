from exif import Image
from datetime import datetime
import cv2
import math
import numpy as np
import statistics
import logzero
from logzero import logger



logzero.logfile('logs.log')



class IssSpeed:
    def __init__(self, img1, img2):
        self.img1 = img1
        self.img2 = img2


    def calculateSpeed(self, featureNum=1000, gsd=12927):
        # get time data
        try:
            with open(self.img1, 'rb') as imageFile:
                imgObj = Image(imageFile)
                timeStr = imgObj.get('datetime_original')
                time1 = datetime.strptime(timeStr, '%Y:%m:%d %H:%M:%S')
        
            with open(self.img2, 'rb') as imageFile:
                imgObj = Image(imageFile)
                timeStr = imgObj.get('datetime_original')
                time2 = datetime.strptime(timeStr, '%Y:%m:%d %H:%M:%S')
        
        except KeyError:
            logger.error('Exif data reading error')
            return 'Exif reading error'


        # count time difference
        timeDiff = time2 - time1
        self.timeDiff = timeDiff.seconds

        if self.timeDiff == 0:
            logger.error("Time difference error: time difference can't be 0")
            return "Time difference error: time difference can't be 0"


        # images to cv object
        self.img1Cv = cv2.imread(self.img1, 0)
        self.img2Cv = cv2.imread(self.img2, 0)

        # check resolution
        height1, width1 = self.img1Cv.shape
        height2, width2 = self.img2Cv.shape

        if width1 != 4056 or width2 != 4056 or height1 != 3040 or height2 != 3040:
            logger.error('Image resolution error')
            return 'Image resolution error'


        # get features
        orb = cv2.ORB_create(nfeatures = featureNum)
        self.keypoints1, self.descriptors1 = orb.detectAndCompute(self.img1Cv, None)
        self.keypoints2, self.descriptors2 = orb.detectAndCompute(self.img2Cv, None)


        # FILTER 1 - keypoints
        # self.descriptors1 = self.filterKeypoints(self.keypoints1, self.descriptors1)
        self.filterKeypoints(self.keypoints1, self.descriptors1)
        
        # if not isinstance(self.descriptors1, np.ndarray):
        #     return 'Error: not enough good keypoints - filter 1'
        

        # print(self.descriptors1)


        # get matches
        bruteForce = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bruteForce.match(self.descriptors1, self.descriptors2)
        self.matches = sorted(matches, key=lambda x: x.distance)

        if len(self.matches) == 0:
            logger.error('0 matches')
            return False


        # get coordinates
        self.coordinates1 = []
        self.coordinates2 = []

        for match in self.matches:
            img1Idx = match.queryIdx
            img2Idx = match.trainIdx

            (x1,y1) = self.keypoints1[img1Idx].pt
            (x2,y2) = self.keypoints2[img2Idx].pt

            self.coordinates1.append((x1, y1))
            self.coordinates2.append((x2, y2))


        distanceList = []
        self.angleData = {}
        allDistances = 0
        mergedCoordinates = list(zip(self.coordinates1, self.coordinates2))

        for coordinates in mergedCoordinates:
            xDiff = coordinates[0][0] - coordinates[1][0]
            yDiff = coordinates[0][1] - coordinates[1][1]

            

            distance = math.hypot(xDiff, yDiff)
            distanceList.append(distance)

            # print(f"x1: {coordinates[0][0]}, x2: {coordinates[1][0]}, y1 {coordinates[0][1]}, y2 {coordinates[1][1]},,, xDiff {xDiff}, yDiff {yDiff}, distance: {distance}")
            
            allDistances = allDistances + distance


            # Angle
            angle_rad = math.atan2(yDiff, xDiff)
            angleDeg = round(math.degrees(angle_rad) % 360)

            if angleDeg in self.angleData:
                self.angleData[angleDeg]['count'] += 1
                self.angleData[angleDeg]['totalDist'] += distance
                self.angleData[angleDeg]['distanceList'].append(distance)
            
            else:
                self.angleData[angleDeg] = {'count': 1, 'totalDist': distance, 'distanceList':[distance]}



        # ANGLES
        self.largestGroup = max(self.angleData.items(), key=lambda x: x[1]['count'])

        if self.largestGroup[1]['count'] == 0:
            logger.error('largest angle group is 0')
            return False

        self.largestGroupPercentage = (self.largestGroup[1]['count'] / len(self.matches)) # 1 = 100%
        self.angleSelectedDist = self.largestGroup[1]['totalDist'] / self.largestGroup[1]['count'] # distance
        self.selectedDistanceList = self.largestGroup[1]['distanceList']


        if len(mergedCoordinates) == 0:
            logger.error('mergedCoordinates length is 0')
            return False

        self.distance = allDistances / len(mergedCoordinates)


        # STANDARD DEVIATION
        filteredDistances = []

        # count first st. dev
        standardDeviation, avg = self.countStDev(self.selectedDistanceList)

        # filter numbers
        for number in distanceList:
            if abs(avg - number) < standardDeviation:
                filteredDistances.append(number)


        # count second st. dev from filtered numbers
        self.filteredStandardDeviation, self.filteredAvg = self.countStDev(filteredDistances)

    
        realDistance = self.filteredAvg * gsd / 100000 # distance px * gsd (px to cm) / 100 000 (cm to km)
        self.speed = realDistance / self.timeDiff


        # FILTER
        if self.filteredStandardDeviation < 80 and self.largestGroupPercentage >= 0.40:
            return self.speed
        
        # ok quality
        elif self.filteredStandardDeviation <= 120 and self.largestGroupPercentage > 0.25:
            logger.warn('Filter ok: high deviation')
            return 'Filter ok: high deviation'
        
        else: #self.filteredStandardDeviation > 120:  bad quality
            logger.warn('Filter bad: high deviation')
            return 'Filter bad: high deviation'
        

    

    # not for filters
    def calculateUnusablePercentage(self, debug=False):
        # 4056 x 3040 = 12 330 240

        # count clouds
        ret, cloudsThreshImg = cv2.threshold(self.img1Cv, 182, 255, cv2.THRESH_BINARY)
        self.clouds = cv2.countNonZero(cloudsThreshImg) / 123302.4


        # count water
        rgbImage1Cv = cv2.imread(self.img1)

        # Convert BGR to HSV
        hsv = cv2.cvtColor(rgbImage1Cv, cv2.COLOR_BGR2HSV)

        # define range of blue color in cv2's HSV (255 is max)
        lower_blue = np.array([110,53,112])
        upper_blue = np.array([130,255,255])

        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # use mask on image
        result = cv2.bitwise_and(rgbImage1Cv, rgbImage1Cv, mask=mask)

        self.water = 0


        # debug
        if debug:
            print(self.clouds)

            img1resized = cv2.resize(rgbImage1Cv, (1014, 760))
            maskResized = cv2.resize(mask, (1014, 760))
            resultResized = cv2.resize(result, (1014, 760))

            cv2.imshow('img1', img1resized)
            cv2.imshow('image', resultResized)
            # cv2.imshow('mask', maskResized)
            cv2.waitKey(0)
            cv2.destroyWindow('image')
            cv2.destroyWindow('img1')
            cv2.destroyWindow('mask')
        


        return (self.clouds, self.water)


        


    def countStDev(self, numbers):
        if len(numbers) == 0:
            logger.error("length of numbers list in countStDev can't be 0")
            return False, False
        

        avg = math.fsum(numbers) / len(numbers)
        squareSum = 0

        # count square sum
        for number in numbers:
            squareSum = squareSum + abs(number - avg)**2

        var = (1/len(numbers)) * squareSum # count var

        standardDeviation = math.sqrt(var) # count st. deviation


        return standardDeviation, avg
    



    def filterKeypoints(self, keypoints, descriptors):
        if len(keypoints) == 0:
            logger.error('0 keypoints given in filterKeypoints')
            return False


        responseSum = 0
        responseList = []
        filteredDesc = []
        responseNum = 0

        for kp in keypoints:
            responseSum = responseSum + kp.response
            responseList.append(kp.response)


        responseMedian = statistics.median(responseList)
        self.avgKpResponse = responseSum / len(keypoints)
        self.maxKpResponse = max(responseList)


        # low response
        if responseMedian < 0.00005:
            # return False
            ''


        # select good kp
        for response in responseList:
            if response >= responseMedian:
                filteredDesc.append(descriptors[responseNum])
            
            responseNum += 1
        

        filteredDesc = np.array(filteredDesc)


        # return only if enough
        if len(filteredDesc) > 100:
            return filteredDesc
        
        else:
            return False