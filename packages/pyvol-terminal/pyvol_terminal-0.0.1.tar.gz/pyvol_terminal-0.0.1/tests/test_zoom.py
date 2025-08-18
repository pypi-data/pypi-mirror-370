#%%
import numpy as np


def print_output(p, vr, new_vr):
    pct_c_d_from_point_to_lim = np.abs(p.reshape(vr.shape[0], 1) - vr) / np.abs(vr[:, :1] - vr[:, 1:])
    pct_c = (100 * (new_vr / vr -1)).round(5)
    print("\n\n")
    print(f"Point to range limit:")
    print(f"x: {pct_c_d_from_point_to_lim[0]}\ny: {pct_c_d_from_point_to_lim[1]}\nz: {pct_c_d_from_point_to_lim[2]}\n")
    print(f"pct change:")
    print(f"x: {pct_c[0]}\ny: {pct_c[1]}\nz: {pct_c[2]}\n")


def zoom_2d(point, drag, viewRange, base=1.1):
    axis_mins = np.array([vr[0] for vr in viewRange])
    axis_maxs = np.array([vr[1] for vr in viewRange])

    
    scales = base ** -drag
    
    new_axis_mins = scales * axis_mins + (1 - scales) * point
    new_axis_maxs = scales * axis_maxs + (1 - scales) * point
    
    return [[new_min, new_max] for new_min, new_max in zip(new_axis_mins, new_axis_maxs)]




drags = [np.array([0.01, 0.02, 0.015]), np.array([-0.02, 0.03, 0.012])]
viewRanges = [np.array([[10,20], [-23, 45], [-55, -40]], dtype=float), np.array([[-30,44], [-30, 23], [-40,-50]], dtype=float)]

points = [np.array([19, 10, -30]), np.array([21, 22., -43])]


for point, drag, viewRange in zip(points, drags, viewRanges):
    newviewRange = zoom_2d(point, drag, viewRange)
    
    
    
#%%

print("--- Original Test Cases ---")
drags_orig = [np.array([0.01, 0.02, 0.015]), np.array([-0.02, 0.03, 0.012])]
viewRanges_orig = [np.array([[10,20], [-23, 45], [-55, -40]], dtype=float), np.array([[-30,44], [-30, 23], [-40,-50]], dtype=float)]
points_orig = [np.array([19, 10, -30]), np.array([21, 22., -43])]

for i in range(len(points_orig)):
    point = points_orig[i]
    drag = drags_orig[i]
    viewRange = viewRanges_orig[i]
    newviewRange = zoom_2d(point, drag, viewRange)
    #print_output(point, viewRange, newviewRange)

print("\n--- Edge Case Tests ---")

# Edge Case 1: Zero drag
point_ec1 = np.array([15, 0, -47.5])
drag_ec1 = np.array([0.0, 0.0, 0.0])
viewRange_ec1 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Zero Drag")
newviewRange_ec1 = zoom_2d(point_ec1, drag_ec1, viewRange_ec1)
#print_output(point_ec1, viewRange_ec1, newviewRange_ec1)

# Edge Case 2: Large positive drag (zoom in significantly)
point_ec2 = np.array([15, 0, -47.5])
drag_ec2 = np.array([5.0, 5.0, 5.0])
viewRange_ec2 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Large Positive Drag (Zoom In)")
newviewRange_ec2 = zoom_2d(point_ec2, drag_ec2, viewRange_ec2)
#print_output(point_ec2, viewRange_ec2, newviewRange_ec2)

# Edge Case 3: Large negative drag (zoom out significantly)
point_ec3 = np.array([15, 0, -47.5])
drag_ec3 = np.array([-5.0, -5.0, -5.0])
viewRange_ec3 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Large Negative Drag (Zoom Out)")
newviewRange_ec3 = zoom_2d(point_ec3, drag_ec3, viewRange_ec3)
#print_output(point_ec3, viewRange_ec3, newviewRange_ec3)

# Edge Case 4: Point at min of view range
point_ec4 = np.array([10, -10, -50])
drag_ec4 = np.array([0.1, 0.1, 0.1])
viewRange_ec4 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Point at Min of View Range")
newviewRange_ec4 = zoom_2d(point_ec4, drag_ec4, viewRange_ec4)
#print_output(point_ec4, viewRange_ec4, newviewRange_ec4)

# Edge Case 5: Point at max of view range
point_ec5 = np.array([20, 10, -45])
drag_ec5 = np.array([0.1, 0.1, 0.1])
viewRange_ec5 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Point at Max of View Range")
newviewRange_ec5 = zoom_2d(point_ec5, drag_ec5, viewRange_ec5)
#print_output(point_ec5, viewRange_ec5, newviewRange_ec5)

# Edge Case 6: Point outside view range (below min)
point_ec6 = np.array([5, -20, -60])
drag_ec6 = np.array([0.1, 0.1, 0.1])
viewRange_ec6 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Point Outside View Range (Below Min)")
newviewRange_ec6 = zoom_2d(point_ec6, drag_ec6, viewRange_ec6)
#print_output(point_ec6, viewRange_ec6, newviewRange_ec6)

# Edge Case 7: Point outside view range (above max)
point_ec7 = np.array([25, 20, -30])
drag_ec7 = np.array([0.1, 0.1, 0.1])
viewRange_ec7 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
print("\nTest Case: Point Outside View Range (Above Max)")
newviewRange_ec7 = zoom_2d(point_ec7, drag_ec7, viewRange_ec7)
#print_output(point_ec7, viewRange_ec7, newviewRange_ec7)

# Edge Case 8: View range with min and max being the same (zero width)
# This will likely cause division by zero in print_output for pct_c_d_from_point_to_lim
point_ec8 = np.array([5, 5, 5])
drag_ec8 = np.array([0.1, 0.1, 0.1])
viewRange_ec8 = np.array([[5, 5], [5, 5], [5, 5]], dtype=float)
print("\nTest Case: Zero Width View Range (Expect Division by Zero for 'Point to range limit')")
newviewRange_ec8 = zoom_2d(point_ec8, drag_ec8, viewRange_ec8)
#print_output(point_ec8, viewRange_ec8, newviewRange_ec8)

# Edge Case 9: View range with negative values and crossing zero
point_ec9 = np.array([0, 0, 0])
drag_ec9 = np.array([0.1, 0.1, 0.1])
viewRange_ec9 = np.array([[-10, 10], [-5, 5], [-20, -10]], dtype=float)
print("\nTest Case: View Range with Negative Values and Crossing Zero")
newviewRange_ec9 = zoom_2d(point_ec9, drag_ec9, viewRange_ec9)
#print_output(point_ec9, viewRange_ec9, newviewRange_ec9)

# Edge Case 10: Different base for zoom_2d
point_ec10 = np.array([15, 0, -47.5])
drag_ec10 = np.array([0.1, 0.1, 0.1])
viewRange_ec10 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
base_ec10 = 2.0
print(f"\nTest Case: Different Base ({base_ec10})")
newviewRange_ec10 = zoom_2d(point_ec10, drag_ec10, viewRange_ec10, base=base_ec10)
#print_output(point_ec10, viewRange_ec10, newviewRange_ec10)

# Edge Case 11: Base < 1 (e.g., 0.5)
point_ec11 = np.array([15, 0, -47.5])
drag_ec11 = np.array([0.1, 0.1, 0.1])
viewRange_ec11 = np.array([[10, 20], [-10, 10], [-50, -45]], dtype=float)
base_ec11 = 0.5
print(f"\nTest Case: Base < 1 ({base_ec11})")
newviewRange_ec11 = zoom_2d(point_ec11, drag_ec11, viewRange_ec11, base=base_ec11)
#print_output(point_ec11, viewRange_ec11, newviewRange_ec11)

# Edge Case 12: Point and view range with all zeros
point_ec12 = np.array([0, 0, 0])
drag_ec12 = np.array([0.1, 0.1, 0.1])
viewRange_ec12 = np.array([[0, 0], [0, 0], [0, 0]], dtype=float)
print("\nTest Case: All Zeros (Expect Division by Zero for 'Point to range limit')")
newviewRange_ec12 = zoom_2d(point_ec12, drag_ec12, viewRange_ec12)
#print_output(point_ec12, viewRange_ec12, newviewRange_ec12)





# %%


test_cases = [
    (np.array([0, 0]), np.array([0, 0]), np.array([[1, 2], [3, 4]], dtype=float)),
    (np.array([5, 5]), np.array([5, 5]), np.array([[0, 10], [0, 10]], dtype=float)),
    (np.array([5, 5]), np.array([-5, -5]), np.array([[0, 10], [0, 10]], dtype=float)),
    (np.array([1000, -1000]), np.array([1, -1]), np.array([[0.0001, 0.0002], [999.9999, 1000.0001]], dtype=float)),
    (np.array([5, 5]), np.array([0.5, -0.5]), np.array([[5, 5], [5, 5]], dtype=float)),
    (np.array([0, 0]), np.array([1e-10, -1e-10]), np.array([[-1e10, 1e10], [-1e-10, 1e-10]], dtype=float)),
    (np.array([-1, 1]), np.array([2, 2]), np.array([[0, 0], [0, 0]], dtype=float)),
    (np.array([0.5, 0.5]), np.array([1, 1]), np.array([[0, 1], [0, 1]], dtype=float)),
    (np.array([0, 0]), np.array([10, -10]), np.array([[1, 2], [3, 4]], dtype=float)),
    (np.array([1e5, -1e5]), np.array([0.1, 0.2]), np.array([[1e5-1, 1e5+1], [-1e5-1, -1e5+1]], dtype=float))
]

for i, (point, drag, viewRange) in enumerate(test_cases):
    result = zoom_2d(point, drag, viewRange)
    print(f"Test case {i+1}:")
    print("Result:", result)