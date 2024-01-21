from importlib.abc import ResourceLoader
from itertools import count
from exif import Image
from datetime import datetime
import cv2
import math
import numpy as np



class IssSpeed:
    def __init__(self, img1, img2):
        self.img1 = img1
        self.img2 = img2


    def calculateSpeed(self, featureNum=1000, gsd=12648, debug=False):
        # images to cv object
        self.img1Cv = cv2.imread(self.img1, 0)
        self.img2Cv = cv2.imread(self.img2, 0)


        # get time data
        with open(self.img1, 'rb') as imageFile:
            imgObj = Image(imageFile)
            try:
                timeStr = imgObj.get('datetime_original')

            except KeyError as e:
                print(f"Exif data loading error {self.img1}: {e}")
                return "Exif reading error"

            time1 = datetime.strptime(timeStr, '%Y:%m:%d %H:%M:%S')
        
        with open(self.img2, 'rb') as imageFile:
            imgObj = Image(imageFile)
            try:
                timeStr = imgObj.get('datetime_original')

            except KeyError as e:
                print(f"Exif data loading error {self.img2}: {e}")
                return "Exif reading error"
            
            time2 = datetime.strptime(timeStr, '%Y:%m:%d %H:%M:%S')


        # count time difference
        timeDiff = time2 - time1

        self.timeDiff = timeDiff.seconds



        # get features
        orb = cv2.ORB_create(nfeatures = featureNum)
        self.keypoints1, self.descriptors1 = orb.detectAndCompute(self.img1Cv, None)
        self.keypoints2, self.descriptors2 = orb.detectAndCompute(self.img2Cv, None)

        print(f'keypoints: {len(self.keypoints1)}')

        # get matches
        bruteForce = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bruteForce.match(self.descriptors1, self.descriptors2)
        self.matches = sorted(matches, key=lambda x: x.distance)

        print(f'{len(self.matches)} matches')

        # error, not enough matches
        if len(self.matches) < 40:
            print(f'Only {len(self.matches)} matches')
            # TODO: only for data on images
            # return f'Not enough matches error, only {len(self.matches)}'
        

        #TODO: filter matches




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

    
        allDistances = 0
        mergedCoordinates = list(zip(self.coordinates1, self.coordinates2))

        for coordinates in mergedCoordinates:
            xDiff = coordinates[0][0] - coordinates[1][0]
            yDiff = coordinates[0][1] - coordinates[1][1]
            distance = math.hypot(xDiff, yDiff)
            allDistances = allDistances + distance
        
        self.distance = allDistances / len(mergedCoordinates) # average


    
        realDistance = self.distance * gsd / 100000 # distance px * gsd (px to cm) / 100 000 (cm to km)
        self.speed = realDistance / self.timeDiff


        # TODO: only for writing data on images
        matchImg = cv2.drawMatches(self.img1Cv, self.keypoints1, self.img2Cv, self.keypoints2, self.matches[:100], None)
        self.resizedMatch = cv2.resize(matchImg, (1600, 600), interpolation = cv2.INTER_AREA)

        if debug:
            print(f"speed: {self.speed}")
            print(f"img: {self.img1}")

            cv2.imshow('matches', self.resizedMatch)
            cv2.waitKey(0)
            cv2.destroyWindow('matches')


        return self.speed

    
    def calculateUnusablePercentage(self, debug=False):
        # 4056 x 3040 = 12 330 240

        # count clouds
        threshold = 182

        ret, cloudsThreshImg = cv2.threshold(self.img1Cv, threshold, 255, cv2.THRESH_BINARY)
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


        # TODO: only for writing data on images
        self.resizedClouds = cv2.resize(cloudsThreshImg, (1014, 760))

        # debug
        if debug:
            print(f"clouds {self.clouds}")

            img1resized = cv2.resize(rgbImage1Cv, (1014, 760))
            maskResized = cv2.resize(mask, (1014, 760))
            resultResized = cv2.resize(result, (1014, 760))

            cv2.imshow('img1', img1resized)
            cv2.imshow('clouds', self.resizedClouds)
            # cv2.imshow('image', resultResized)
            # cv2.imshow('mask', maskResized)
            cv2.waitKey(0)
            cv2.destroyWindow('image')
            cv2.destroyWindow('clouds')
            cv2.destroyWindow('img1')
            cv2.destroyWindow('mask')
        


        return (self.clouds, self.water)

    
    def displayMatches(self):
        matchImg = cv2.drawMatches(self.img1Cv, self.keypoints1, self.img2Cv, self.keypoints2, self.matches[:100], None)
        resize = cv2.resize(matchImg, (1600, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('matches', resize)
        cv2.waitKey(0)
        cv2.destroyWindow('matches')



# imgPair1 = IssSpeed('test/img3.jpg', 'test/img4.jpg')
# imgPair1.getTimeDifference()
# imgPair1.getKeypoints()
# imgPair1.calculateDist()
# imgPair1.calculateSpeed()

# print(imgPair1.speed)

# imgPair1.displayMatches()