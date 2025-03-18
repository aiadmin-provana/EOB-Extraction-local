from PIL import Image, ImageDraw

def draw_bounding_box(image_path, bounding_box_coordinates, output_path=r"Llama_Parse\temp_imgs\\"):
    """
    Draws a bounding box on an image and saves the result.

    Args:
        image_path: Path to the input image.
        bounding_box_coordinates: Tuple (x1, y1, x2, y2) representing the bounding box.
        output_path: Path to save the output image.
    """
    try:
        # Open the image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Draw the bounding box
        x1, y1, x2, y2 = bounding_box_coordinates
        draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)  # Red box, 3 pixels wide

        # Save the image
        img.save(output_path)

        print(f"Bounding box drawn and saved to {output_path}")
        img.show() #show the image.

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
image_file = r"Llama_Parse\temp_imgs\page_1.png"  # Replace with your image path
bbox = (269, 33, 281, 256)  # Example bounding box (x1, y1, x2, y2)

draw_bounding_box(image_file, bbox)