import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy import stats

def CameraCenter(ApproxPosition):
    #returns degrees to rotate camera
    #ApproxPosition is array in format: [[y1, x1], [y2, x2]]
    PixelsToDegrees = 0

    if len(ApproxPosition) != 0:
        Center = [240, 320]
        #computing approxPosition Center on x axis
        ObjCenter = round(ApproxPosition[0][1] + ApproxPosition[1][1] / 2)
        ObjCenter_dev =  ObjCenter - Center[1]

        #lets assume that camera field is 80 degrees range
        PixelsToDegrees = 0.125 * ObjCenter_dev
        #i assumed that because i sliced the image to 8 slices (every slice equals 10 degrees) => 0.125

    return PixelsToDegrees

def Fit_H_V_line(points_param):

    #x fit
    x_mean = np.mean(points_param[:, 0])

    #y fit
    y_mean = np.mean(points_param[:, 1])

    #validation
    dev_x = np.absolute(points_param[:, 0] - x_mean)
    dev_y = np.absolute(points_param[:, 1] - y_mean)
    dev_m_x = np.mean(dev_x)
    dev_m_y = np.mean(dev_y)

    if dev_m_x < dev_m_y: #x, y format
        return [round(x_mean), 480] #vertical
    else:
        return [round(y_mean), 320] #horizontal
        #shouldnt be 320, incorrect metrict, fix needed TODO:

def LBdetection(full_image):
    #line break detection (to detect coordinations and size of object in camera feed)
    #algorithm:
    #BGR -> grayscale -> mean blur -> threshold -> rescaling to bitmap
    # -> computing avgmap with reverse gaussian distribution 
    # -> updating final threshold image (update ROI selection, filtering white walls)
    # -> slicing -> contours -> computing centroids -> kmeans 
    # -> object bounding rect

    Boundaries = []
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

    cont = np.zeros((im_height, im_width, 3), dtype=np.uint8)
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

    #point reduction by scanning sliced regions
    points_sort = point_coords.copy()
    points_sort = points_sort[points_sort[:, 0].argsort()]
    points_new = np.zeros((16, 2), dtype=np.uint16)

    for i_slice in range(16):
        x_reg_min = (40 * i_slice)
        x_reg_max = x_reg_min + 40

        b_thresh = x_reg_min < points_sort[:, 0]
        u_thresh = points_sort[:, 0] < x_reg_max
        points_criteria = points_sort[np.logical_and(b_thresh, u_thresh)]

        if points_criteria.shape[0] > 0:
            points_criteria = points_criteria[points_criteria[:, 1].argsort()]

            points_new[i_slice] = points_criteria[-1]

    f_index = np.where(points_new[:, 0] == 0)

    points_updated = points_new.copy()
    points_updated = np.delete(points_new, f_index[0], axis=0) #points_updated is for line detection (x, y format)
    
    #outlier deletion by deleting variables under median and bias = 50

    y_component = np.sort(points_updated[:, 1])
    y_lim = np.median(y_component) - 50
    points_updated = np.delete(points_updated, np.where(points_updated[:, 1] < y_lim), axis=0)

    #for point_new in points_updated:
        #cv2.circle(approx, point_new, 5, (0, 0, 255), -1)

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
    
    """
        LINE BREAK DONE -> now going to -> WHITE LINE DIST APPROX
    """

    #reminder that points_updated is still in x, y format :)
    #reminder that points_updated is sorted by x component

    #Grouping by 2-point slope (calculating slopes between points)

    lines = []
    if points_updated.shape[0] != 0:
        slope_arr = np.zeros(points_updated.shape[0] - 1, dtype=np.float32)
        for i in range(points_updated.shape[0]):
            if i == points_updated.shape[0] - 1:
                break

            point1 = points_updated[i].astype(dtype=np.int16)
            point2 = points_updated[i+1].astype(dtype=np.int16)

            x1, y1 = point1[0], point1[1]
            x2, y2 = point2[0], point2[1]

            d_x = (x2 - x1)
            d_y = (y1 - y2)
            slope = d_y / d_x

            slope_arr[i] = slope

        #the grouping itself
        n_kernels = []
        kernel_len = 1
        for i in range(slope_arr.shape[0]):
            if i == slope_arr.shape[0] - 1:
                break

            current_s = slope_arr[i]
            next_s = slope_arr[i+1]

            dev = abs(current_s - next_s)
            if dev > 0.15:
                n_kernels.append(kernel_len)
                kernel_len = 1
            else:
                kernel_len += 1

        if len(n_kernels) == 0 or len(n_kernels) == 1:
            #considering all points as a line
            
            return_line = Fit_H_V_line(points_updated)
            lines.append(return_line)
        else:
            inc = 0
            for k in n_kernels:
                k_data = points_updated[:(k+inc)]

                return_line = Fit_H_V_line(k_data)
                lines.append(return_line)

                inc += k

        lines_converted = np.asarray(lines)


        GroupX = lines_converted[np.where(lines_converted[:, 1] == 320)]
        GroupY = lines_converted[np.where(lines_converted[:, 1] == 480)]

        if GroupY.shape[0] != 0:
            nearest_Y = np.min(GroupY[:, 0])
            lineY = [nearest_Y, 320]
        else: lineY = []
        if GroupX.shape[0] != 0:
            nearest_X = np.min(GroupX[:, 0])
            lineX = [nearest_X, 480]
        else: lineX = []

        lines = [lineX, lineY]
    
        #TODO: completely rework the algorithm you made because it fucking sucks
        #if len(lines[0]) == 2:
        #    cv2.line(approx, (0, lines[0][0]), (480, lines[0][0]), (0, 255, 0), 2)
        #if len(lines[1]) == 2:
        #    cv2.line(approx, (lines[1][0], 0), (lines[1][0], 320), (0, 255, 0), 2)

    Boundaries = [lineX, lineY]
    return ApproxPos, Boundaries

    #cv2.imshow("Points 0", points_arr0)
    #cv2.imshow("Points 1", points_arr1)
    #cv2.imshow("Contours", cont)
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("Approx", approx)

    #cv2.waitKey(1)