import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy import stats

def LBdetection(full_image): #TODO: setup for more compact than passing whole frame
    #line break detection (to detect coordinations and size of object in camera feed)
    #algorithm:
    #BGR -> grayscale -> mean blur -> threshold -> rescaling to bitmap
    # -> computing avgmap with reverse gaussian distribution 
    # -> updating final threshold image (update ROI selection, filtering white walls)
    # -> slicing -> contours -> computing centroids -> kmeans 
    # -> object bounding rect

    """
    TODO: setup, test and clean
    rawCapture.truncate(0)
    rawCapture.seek(0)
    """
    f_height, f_width, channels = full_image.shape

    image = full_image[int(f_height/2):f_height]
    im_height, im_width, im_channels = image.shape

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((5, 5), np.float32) / 25
    blur = cv2.filter2D(grayscale, -1, kernel)
    

    """
    THRESHOLD AND WHITE PIXEL DENSITY KERNEL (adjusting ROI)
    """
    ret, thresh = cv2.threshold(blur, 130, 255, cv2.THRESH_BINARY)

    #Summing all to bitmap

    bitmap = np.zeros((6, 16), dtype=np.uint8)
    for y in range(int(im_height / 40)): #6, kernel size is 40
        for x in range(int(im_width / 40)): #16
            kernel = thresh[(y * 40):(y * 40) + 40, (x * 40):(x * 40) + 40]
            average = np.mean(kernel.flatten())
            
            bitmap[y][x] = average

    #Generating gaussian distribution
    
    x_data = np.arange(-8, 8, 1)
    y_data = (1000 * stats.norm.pdf(x_data, 0, 5)).round()

    Max = y_data.max()
    y_data = (Max - y_data).astype(dtype=np.uint16)
    y_sum = np.sum(y_data)

    #apply gaussian distribution to weighted average of vector

    avgmap = np.zeros((6, 1), dtype=np.uint8)
    for i in range(avgmap.shape[0]):
        avgmap[i] = np.mean(bitmap[i] * y_data) / y_sum

    #setting finite threshold to improve ROI
    for i in range(avgmap.shape[0]):
        if avgmap[i] >= 10:
            bitmap[i].fill(0)
            bitmap[i].astype(dtype=np.uint8)
        else:
            break #just iterate until the white is being crossed by black

    #updating final threshold image from ROI selection
    for y in range(bitmap.shape[0]):
        if np.count_nonzero(bitmap[y]) == 0:
            thresh[(y * 40):(y * 40) + 40, :].fill(0)
            thresh[(y * 40):(y * 40) + 40, :].astype(dtype=np.uint8)

    for x in range(8):
        if x == 0 and x == im_height: continue

        cv2.line(thresh, (x * 80, 0), (x * 80, im_height), (0, 0, 0), thickness = 1)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #cont = np.zeros((im_height, im_width, 3), dtype=np.uint8)
    #points_arr0 = cont.copy()
    #points_arr1 = cont.copy()
    #approx = cont.copy()

    point_coords = np.zeros((len(contours), 2), dtype=np.uint16)

    for i, contour in enumerate(contours):
        #Computing the centroid
        y_cont = contour[:, :, 0].flatten()
        x_cont = contour[:, :, 1].flatten()

        coord = np.array([round(np.mean(y_cont)), round(np.mean(x_cont))])
        
        point_coords[i][0] = coord[0] #y, x format
        point_coords[i][1] = coord[1]

        #cv2.circle(cont, point_coords[i], 5, (255, 0, 0), -1)
        #cv2.circle(approx, point_coords[i], 5, (0, 0, 255), -1)
        #cv2.drawContours(cont, [contour], 0, (0, 100, 0), 3)

    if point_coords.shape[0] > 1:
        kmeans = KMeans(2)
        kmeans.fit(point_coords)
        clusters = kmeans.fit_predict(point_coords)
    else:
        clusters = np.full(point_coords.shape[0], 1)

    len1 = np.count_nonzero(clusters)
    len0 = clusters.shape[0] - len1

    points1 = np.zeros((len1, 2), dtype=np.uint16) #y, x format
    if len0 != 0:
        points0 = np.zeros((len0, 2), dtype=np.uint16)
    else:
        points0 = np.zeros((1), dtype=np.uint8)

    iter0 = 0
    iter1 = 0
    for i_cluster, color in enumerate(clusters):
        if color == 0:
            points0[iter0] = point_coords[i_cluster]
            #cv2.circle(points_arr0, points0[iter0], 5, (255, 0, 0), -1)
            iter0 += 1
        
        else: #1
            points1[iter1] = point_coords[i_cluster]
            #cv2.circle(points_arr1, points1[iter1], 5, (0, 0, 255), -1)
            iter1 += 1

    ApproxPos = np.zeros((2, 2), dtype=np.uint16) #y, x format
    if points0.shape[0] == 1:
        #No points avaliable
        pass
    else:
        #approximating target location
        x_min0 = points0[:, 0].min()
        x_min1 = points1[:, 0].min()

        x_max0 = points0[:, 0].max()
        x_max1 = points1[:, 0].max()

        if x_max1 < x_min0:
            #line 1 is on left
            if not 75 < (x_min0 - x_max1) < 85: #one slice batch (meaning kmeans didnt find anything)
                ApproxPos[0] = [0, x_max1] #y, x
                ApproxPos[1] = [x_min0, image.shape[0]]

                #cv2.rectangle(approx, (ApproxPos[0][1], ApproxPos[0][0]), (ApproxPos[1][0], ApproxPos[1][1]), (255, 0, 0), 2)
            

        elif x_max0 < x_min1:
            #line 0 is on left
            if not 75 < (x_min1 - x_max0) < 85: #one slice batch (meaning kmeans didnt find anything)
                ApproxPos[0] = [0, x_max0]
                ApproxPos[1] = [x_min1, image.shape[0]]

                #cv2.rectangle(approx, (ApproxPos[0][1], ApproxPos[0][0]), (ApproxPos[1][0], ApproxPos[1][1]), (255, 0, 0), 2)

    return ApproxPos

    #cv2.imshow("Points 0", points_arr0)
    #cv2.imshow("Points 1", points_arr1)
    #cv2.imshow("Contours", cont)
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("Approx", approx)

    #cv2.waitKey(1)