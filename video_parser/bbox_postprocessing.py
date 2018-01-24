import numpy as np

def between(x,a,b):
    if x >= a and x <= b:
        return True
    return False

def join_splitlines(a,b):
    # splitline comes in [left, middle, right, middle]
    left = np.min([a[0],b[0]])
    right = np.max([a[2],b[2]])
    return [left, a[1], right, a[1]]

def splitlines_intersect_horizontally(a,b):
    # splitline comes in [left, middle, right, middle]
    if a[1] == b[1]:
        a_left = a[0]
        b_left = b[0]
        a_right = a[2]
        b_right = b[2]
        if between(a_right, b_left, b_right) or between(a_left, b_left, b_right):
            return True
    return False

def crops_intersect_vertically(a,b):
    # both a,b are crops with (_,[left,bottom,right,top])
    a_bottom = a[1][1]
    a_top = a[1][3]

    b_bottom = b[1][1]
    b_top = b[1][3]

    a_left = a[1][0]
    b_left = b[1][0]
    a_right = a[1][2]
    b_right = b[1][2]

    if a_top == b_top or b_bottom == a_bottom:
        return False

    if a_top > b_bottom and a_top < b_top:
        if a_left > b_left and a_left < b_right:
            return True
        elif a_right >= b_left and a_right <= b_right:
            return True
    elif a_bottom < b_top and a_bottom > b_bottom:
        if a_left >= b_left and a_left <= b_right:
            return True
        elif a_right >= b_left and a_right <= b_right:
            return True
    return False

def vertical_splitline_between(a,b):
    # both a,b are crops with (_,[left,bottom,right,top])
    a_bottom = a[1][1]
    a_top = a[1][3]

    b_bottom = b[1][1]
    b_top = b[1][3]

    top = np.max([a_top,a_bottom,b_top,b_bottom])
    bottom = np.min([a_top,a_bottom,b_top,b_bottom])

    middle = (top + bottom) / 2.0

    a_left = a[1][0]
    b_left = b[1][0]
    # we want the rightmost one
    left = np.max([a_left,b_left])

    a_right = a[1][2]
    b_right = b[1][2]
    # we want the leftmost one
    right = np.min([a_right,b_right])

    return [left, middle, right, middle]

def postprocess_bboxes_by_splitlines(cropboxes, crop_size, overlap_px_h):
    # structure of bounding box = top, left, bottom, right, (top < bottom), (left < right)
    # structure of crop = left, bottom, right, top, (bottom < top),(left < bottom)

    N = len(cropboxes)
    ignore_matrix = np.ones((N, N), dtype=bool)
    for i in range(0,N):
        ignore_matrix[i,i] = False

    splitlines = []

    for i in range(0,N):
        for j in range(i,N):
            if ignore_matrix[i,j]:
                # we can now work with crop_i and crop_j
                cropi = cropboxes[i]
                cropj = cropboxes[j]
                if crops_intersect_vertically(cropi,cropj):
                    #print("split line between", i,j)
                    ignore_matrix[i,j] = False
                    ignore_matrix[j,i] = False
                    splitline = vertical_splitline_between(cropi,cropj)
                    splitlines.append(splitline)

    #print(ignore_matrix)

    #print("splitlines before", len(splitlines), splitlines)

    # test with randomly mixing the list = if its robust

    M = len(splitlines)
    ignore_vector = np.ones((M), dtype=bool)

    final_list = []

    for i in range(0,M):
        if ignore_vector[i]:
            splitline_a = splitlines[i]
            ignore_vector[i] = False

            for j in range(i,M):
                if ignore_vector[j]:
                    splitline_b = splitlines[j]

                    if splitlines_intersect_horizontally(splitline_a, splitline_b):
                        splitline_a = join_splitlines(splitline_a, splitline_b)
                        #print("joined", i, j)
                        ignore_vector[j] = False

            #print(i, "final", splitline_a)
            final_list.append(splitline_a)

    #print("pre splitlines", len(final_list), final_list)
    #final_list = set(tuple(i) for i in final_list)

    splitlines = final_list
    print("final splitlines", len(splitlines), splitlines)

    debug_add = []

    for splitline in splitlines:

        left = splitline[0]
        bottom = splitline[1]
        right = splitline[2]
        top = splitline[3]

        debug_add.append(['person', [top, left, bottom, right], 1.0, 6])

    return debug_add