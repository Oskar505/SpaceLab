from exif import Image
from datetime import datetime
import cv2
import math


class IssSpeed:
    def __init__(self, img1, img2):
        self.img1 = img1
        self.img2 = img2


    def getTimeDifference(self):
        # get time data
        with open(self.img1, 'rb') as imageFile:
            imgObj = Image(imageFile)
            timeStr = imgObj.get('datetime_original')
            time1 = datetime.strptime(timeStr, '%Y:%m:%d %H:%M:%S')
        
        with open(self.img2, 'rb') as imageFile:
            imgObj = Image(imageFile)
            timeStr = imgObj.get('datetime_original')
            time2 = datetime.strptime(timeStr, '%Y:%m:%d %H:%M:%S')


        # count time difference
        timeDiff = time2 - time1

        self.timeDiff = timeDiff.seconds
        return self.timeDiff


    def getKeypoints(self, featureNum=1000):
        # images to cv object
        self.img1Cv = cv2.imread(self.img1, 0)
        self.img2Cv = cv2.imread(self.img2, 0)

        # get features
        orb = cv2.ORB_create(nfeatures = featureNum)
        self.keypoints1, self.descriptors1 = orb.detectAndCompute(self.img1Cv, None)
        self.keypoints2, self.descriptors2 = orb.detectAndCompute(self.img2Cv, None)

        # get matches
        bruteForce = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bruteForce.match(self.descriptors1, self.descriptors2)
        self.matches = sorted(matches, key=lambda x: x.distance)


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

        return self.coordinates1[0], self.coordinates2[0]
    

    def calculateDist(self):
        allDistances = 0
        mergedCoordinates = list(zip(self.coordinates1, self.coordinates2))

        for coordinates in mergedCoordinates:
            xDiff = coordinates[0][0] - coordinates[1][0]
            yDiff = coordinates[0][1] - coordinates[1][1]
            distance = math.hypot(xDiff, yDiff)
            allDistances = allDistances + distance
        
        self.distance = allDistances / len(mergedCoordinates)
        return self.distance


    def calculateSpeed(self, gsd=12648):
        realDistance = self.distance * gsd / 100000 # distance px * gsd (px to cm) / 100 000 (cm to km)
        self.speed = realDistance / self.timeDiff
        return self.speed

    
    def calculateCloudsPercentage(self):
        # 4056 x 3040  12 330 240
        # self.clouds = cv2.countNonZero(self.img1Cv) / 123302.4

        ret, threshImg = cv2.threshold(self.img1Cv, 182, 255, cv2.THRESH_BINARY)


        self.clouds = cv2.countNonZero(threshImg) / 123302.4

        # test
        # print(self.clouds)

        # img1resized = cv2.resize(self.img1Cv, (1014, 760))
        # threshImg = cv2.resize(threshImg, (1014, 760))

        # cv2.imshow('image', threshImg)
        # cv2.imshow('img1', img1resized)
        # cv2.waitKey(0)
        # cv2.destroyWindow('image')
        # cv2.destroyWindow('img1')

        return self.clouds

    
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