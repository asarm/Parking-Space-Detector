import cv2
import numpy as np
import pickle

def empty(val):
    pass

cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 400,200)

cv2.createTrackbar("Edit Mode", "Trackbars", 0, 1, empty)
cv2.createTrackbar("C for Threshold", "Trackbars", 4, 45, empty)
cv2.createTrackbar("Blocksize for Threshold", "Trackbars", 9, 45, empty)
cv2.createTrackbar("Count Limit", "Trackbars", 50, 1000, empty)

try:
    with open('points', 'rb') as outfile:
        newptsList = pickle.load(outfile)
except:
    newptsList = np.array([], np.int32)

if len(newptsList) < 0:
    ptsList = np.array([], np.int32)
    newptsList = ptsList.reshape((len(ptsList) // 8, 4, 2))
else:
    ptsList = newptsList.reshape(len(newptsList)*8)

newPolygon = []

def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        if len(newPolygon) != 4:
            newPolygon.append((x,y))
            print(f"Selected Point ({x},{y})")

# selection order => left-top, left-bottom, right-bottom,right-top


default_color = (250, 50, 250)
available_color = (50, 250, 50)

images = ["Resources/road2.jpg", "Resources/road1.jpg", "Resources/road3.jpg"]
img_index = 0

while True:
    edit_mode = cv2.getTrackbarPos("Edit Mode", "Trackbars")

    if edit_mode == 1:
        c_val = cv2.getTrackbarPos("C for Threshold", "Trackbars")
        blocksize = cv2.getTrackbarPos("Blocksize for Threshold", "Trackbars")
        count_limit = cv2.getTrackbarPos("Count Limit", "Trackbars")

        if c_val % 2 == 0: c_val += 1
        if blocksize % 2 == 0: blocksize += 1

        img = cv2.imread(images[img_index])
        img = cv2.resize(img, (0, 0), None, 0.65, 0.65)

        imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgTreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                            blockSize=blocksize, C=c_val)

        imgMedian = cv2.medianBlur(imgTreshold, 5)

        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    else:
        img = cv2.imread(images[img_index])
        img = cv2.resize(img, (0, 0), None, 0.65, 0.65)

        imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgTreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, blockSize=9, C=4)
        imgMedian = cv2.medianBlur(imgTreshold, 5)

        kernel = np.ones((3,3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        # threshold for white pixels count
        count_limit = 900

    if len(newPolygon) == 4:
        print("Polygon completed!")
        ptsList = np.append(ptsList, newPolygon)
        newptsList = ptsList.reshape((len(ptsList) // 8, 4, 2))
        newPolygon = []

    if len(ptsList) >= 8:
        available_count, filled_count = 0,0
        for index, ply in enumerate(newptsList):
            cropped = imgDilate[ply[0][1]:ply[2][1], ply[1][0]:ply[3][0]]
            count = cv2.countNonZero(cropped)

            if count < count_limit:
                available_count += 1
                cv2.polylines(img, pts=[ply], color=available_color, isClosed=True, thickness=2)
            else:
                filled_count +=1
                cv2.polylines(img, pts=[ply], color=default_color, isClosed=True, thickness=2)

            '''
            cv2.putText(img, f"{str(count)}", (ply[1][0], ply[1][1]),
                        color=(255, 255, 255), thickness=1,
                        fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5)
            '''

        cv2.putText(img, f"Park Spaces: {available_count}/{available_count+filled_count}", (img.shape[1]-200, 20), color=(255, 255, 255), thickness=2,
                    fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5)

    if edit_mode == 1:
        cv2.setMouseCallback("Image", mouseClick)

    if edit_mode == 1:
        cv2.imshow("Dilate", imgDilate)
        cv2.imshow("Image", img)
    else:
        cv2.imshow("Image", img)

    if edit_mode == 0:
        cv2.waitKey(2000)
        if img_index == len(images)-1:
            img_index = 0
        else:
            img_index += 1
    else:
        img_index = 0

        with open('points', 'wb') as outfile:
           pickle.dump(newptsList, outfile)

        cv2.waitKey(1)

