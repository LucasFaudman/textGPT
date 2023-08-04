from io import BytesIO
from PIL import Image
import requests

MAX_IMAGE_BYTES = 1024 * 1024  * 4 # 4MB
VALID_SIZES = [256, 512, 1024]


def download_image(url):
    response = requests.Session().get(url)
    response.raise_for_status() 
    return response.content

def make_image_object(image_bytes):
    img_obj = Image.open(BytesIO(image_bytes))
    return img_obj

def convert_to_PNG_in_RGBA_mode(img_obj):
    if img_obj.mode not in ['RGBA', 'LA', 'L']:
        img_obj = img_obj.convert('RGBA')

    with BytesIO() as png_buffer:
        img_obj.save(png_buffer, format="PNG")
        png_image_bytes = png_buffer.getvalue()
        png_img_obj = make_image_object(png_image_bytes)
    
    return png_image_bytes, png_img_obj

def resize_to_closest_smaller_square(img_obj):
    original_width, original_height = img_obj.size

    # Find the closest smaller square size
    closest_size = min(size for size in VALID_SIZES if size < original_width)

    # Calculate the new dimensions to maintain the aspect ratio and fit inside the square
    new_width = new_height = closest_size
    if original_width > original_height:
        new_height = int(closest_size * original_height / original_width)
    else:
        new_width = int(closest_size * original_width / original_height)

    # Resize the image to the closest smaller square
    resized_img_obj = img_obj.resize((new_width, new_height))
    return resized_img_obj

def get_mask_bytes(img_obj):
    mask_img_obj = Image.new('RGBA', img_obj.size, color=(0, 0, 0, 0))
    #mask_img_obj.putalpha(img_obj.split()[3])
    mask_bytes, mask_img_obj = convert_to_PNG_in_RGBA_mode(mask_img_obj) # Convert to PNG in RGBA mode
    return mask_bytes

def get_image_bytes_if_valid(url):
    # Only return bytes if the image at url is valid otherwise return error_string
    try:
        image_bytes = download_image(url)
        print(f"Downloaded {len(image_bytes)} bytes of image data.")
    except requests.exceptions.RequestException as e:
        error_string = f'Error downloading image:'
        print(error_string, e)
        return error_string
    
    try:
        img_obj = make_image_object(image_bytes)
        print(f"Image is {img_obj.width}x{img_obj.height} and {img_obj.format}.")
    except Exception as e:
        error_string = 'Error processing image with Pillow'
        print(error_string, e)
        return error_string        
        

    if img_obj.width != img_obj.height or img_obj.width not in VALID_SIZES or img_obj.height not in VALID_SIZES: 
        print(f"Invalid image dimensions: {img_obj.width}x{img_obj.height}")
        try:
            img_obj = resize_to_closest_smaller_square(img_obj)
            print(f"Resized image to {img_obj.width}x{img_obj.height}.")
        except Exception as e:
            error_string = 'Error resizing image'
            print(error_string, e)
            return error_string                

    
    if img_obj.format != 'PNG':
        print(f"Invalid image format: {img_obj.format}")
        try:
            image_bytes, img_obj = convert_to_PNG_in_RGBA_mode(img_obj)
            print(f"Converted image to {img_obj.format}.")
        except Exception as e:
            error_string = 'Error converting image to PNG'
            print(error_string, e)
            return error_string       

    
    num_bytes = len(image_bytes)
    # Check that the image is valid
    if num_bytes > MAX_IMAGE_BYTES:
        error_string = f"Image is too large ({num_bytes} bytes). Max size is 4MB ({MAX_IMAGE_BYTES} bytes)."
        print(error_string, e)
        return error_string 

    # Get the mask bytes but only if the image is valid to save time
    mask_bytes = get_mask_bytes(img_obj)
    
    return image_bytes, mask_bytes