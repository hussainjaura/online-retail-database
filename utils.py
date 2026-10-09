# this function reads an image file and converts it into binary data:
def load_image_as_blob(filepath):
    # open the image file in binary read mode:
    with open(filepath, "rb") as f:
        # return the raw binary content of the image:
        return f.read()


# this function performs simple encryption by reversing the string:
def encrypt_string(text):
    # reverse the text before storing it in the database:
    return text[::-1]


# this function decrypts the string by reversing it back:
def decrypt_string(text):
    # return the original text by reversing again:
    return text[::-1]
