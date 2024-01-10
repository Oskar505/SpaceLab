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
        return timeDiff.seconds


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

        return self.matches
    
    def displayMatches(self):
        matchImg = cv2.drawMatches(self.img1Cv, self.keypoints1, self.img2Cv, self.keypoints2, self.matches[:100], None)
        resize = cv2.resize(matchImg, (1600, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('matches', resize)
        cv2.waitKey(0)
        cv2.destroyWindow('matches')



imgPair1 = IssSpeed('test/img1.jpg', 'test/img2.jpg')
imgPair1.getTimeDifference()
imgPair1.getKeypoints()
imgPair1.displayMatches()