import os
import math
from image import Image

def load_images_from_directory(directory_path):
    # revised LLM generated function contracts 
    """Loads and returns a list of .bmp image objects from a directory.
    
    Args:
        directory_path (str): The path to the directory containing .bmp image files.
        
    Returns:
        list: A list of Image objects loaded from the directory.
    """

    image_files = [f for f in os.listdir(directory_path) if f.endswith('.bmp')]
    images = [Image.read_bmp(os.path.join(directory_path, file)) for file in image_files]
    return images

def get_top_row(image):
    """Extracts the top row of pixels from an image.
    
    Args:
        image (Image): The image object.
        
    Returns:
        list: A list of pixel objects representing the top row of the image.
    """ 

    return [image.get_pixel(0, c) for c in range(image.get_width())]

def get_bottom_row(image):
    """Extracts the bottom row of pixels from an image.
    
    Args:
        image (Image): The image object.
        
    Returns:
        list: A list of pixel objects representing the bottom row of the image.
    """

    return [image.get_pixel(image.get_height() - 1, c) for c in range(image.get_width())]

def manhattan_distance(row1, row2): # Used LLM to explore pixel relation options 
    return sum(
        abs(row1[i].get_r() - row2[i].get_r()) +
        abs(row1[i].get_g() - row2[i].get_g()) +
        abs(row1[i].get_b() - row2[i].get_b())
        for i in range(len(row1))
    )

def find_best_bottom_match(current_bottom_row, remaining_strips, max_distance_threshold):
    """Finds the best matching strip for the current strip based on the bottom row.
    
    Args:
        current_bottom_row (list): The bottom row of the current strip.
        remaining_strips (list): The list of remaining image strips.
        
    Returns:
        Image: The best matching strip, or None if no match is found.
    """
    best_match = None
    best_distance = float('inf') #LLM suggested this use of infinity as a highest number
    best_index = -1

    for j in range(len(remaining_strips)):
        top_row = get_top_row(remaining_strips[j])
        distance = manhattan_distance(current_bottom_row, top_row)

        if distance < best_distance and distance <= max_distance_threshold:
            best_match = remaining_strips[j]
            best_distance = distance
            best_index = j

    return best_match, best_index

def find_best_top_match(current_top_row, remaining_strips, max_distance_threshold):
    """Finds the best matching strip for the current strip based on the top row.
    
    Args:
        current_top_row (list): The top row of the current strip.
        remaining_strips (list): The list of remaining image strips.
        
    Returns:
        Image: The best matching strip, or None if no match is found.
    """
    best_match = None
    best_distance = float('inf')
    best_index = -1

    for j in range(len(remaining_strips)):
        bottom_row = get_bottom_row(remaining_strips[j])
        distance = manhattan_distance(current_top_row, bottom_row)

        if distance < best_distance and distance <= max_distance_threshold:
            best_match = remaining_strips[j]
            best_distance = distance
            best_index = j

    return best_match, best_index

def reconstruct_image(strips):
    """Reconstructs the image by placing bottom strips based on their best matches, 
    then after reaching the max distance threshold adds strips to the top.
    
    Args:
        strips (list): A list of image strips to be placed in order.
        
    Returns:
        list: The ordered list of image strips after reconstruction.
    """

    if not strips:
        return []

    ordered_strips = [strips[0]]  
    remaining_strips = strips[1:]
    max_distance_threshold = 20422  # Max threshold is from trial and error, may be a limitation of solution 

    # Builds image downward
    while remaining_strips:
        current_bottom_row = get_bottom_row(ordered_strips[-1])
        best_match, best_index = find_best_bottom_match(current_bottom_row, remaining_strips, max_distance_threshold)

        if best_match:
            ordered_strips.append(best_match)
            remaining_strips.pop(best_index)
        else:
            break 
    
    #Builds image upward
    while remaining_strips:
        current_top_row = get_top_row(ordered_strips[0])
        best_match, best_index = find_best_top_match(current_top_row, remaining_strips, max_distance_threshold)

        if best_match:
            ordered_strips.insert(0, best_match)  # Insert at the beginning
            remaining_strips.pop(best_index)
        else:
            break 

    return ordered_strips


def save_reconstructed_image(ordered_strips):
    """Saves the reconstructed image to a file.
    
    Args:
        ordered_strips (list): A list of ordered image strips that make up the full image.
        
    Returns:
        None
    """

    width = ordered_strips[0].get_width()
    height = sum(strip.get_height() for strip in ordered_strips)
    full_image = Image(width, height)

    current_y = 0
    for strip in ordered_strips:
        for y in range(strip.get_height()):
            for x in range(strip.get_width()):
                full_image.set_pixel(current_y + y, x, strip.get_pixel(y, x)) #set each pixel to values from list
        current_y += strip.get_height()

    full_image.save_bmp("reconstructed.bmp")

def main():
    directory_path = '/home/images'
    images = load_images_from_directory(directory_path)
    ordered_strips = reconstruct_image(images)
    save_reconstructed_image(ordered_strips)

main()
