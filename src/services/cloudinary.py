import hashlib

import cloudinary
import cloudinary.uploader

from src.conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    def get_name(self, email):
        """
        The get_name function takes an email address and returns a unique name for the user.
        It does this by hashing the email address with SHA256, then taking only the first 8 characters of that hash.

        :param self: Represent the instance of the class
        :param email: Create a unique name for the user
        :return: A hash of the email address
        :doc-author: Trelent
        """
        return hashlib.sha256(email.encode()).hexdigest()[:8]

    def upload(self, file, route):
        """
        The upload function takes a file and a route as arguments.
        The function then uploads the file to cloudinary with the given route, overwriting any existing files with that name.

        :param self: Represent the instance of the class
        :param file: Upload the file to cloudinary
        :param route: Specify the folder and file name that is used to store the image on cloudinary
        :return: A dictionary with the following keys:
        :doc-author: Trelent
        """
        r = cloudinary.uploader.upload(file, folder='NoteBook', public_id=route, overwrite=True)
        return r

    def get_url_for_avatar(self, route, r):
        """
        The get_url_for_avatar function is used to generate a URL for the avatar image.
        The function takes two arguments: route and r. The route argument is the name of
        the file that contains the avatar image, and r is a dictionary containing information
        about that file (such as its version number).
        The function then uses Cloudinary's build_url() method to create a URL for an image with specific attributes
        (width, height, crop type) based on those arguments.

        :param self: Represent the instance of the class
        :param route: Specify the image that is to be displayed
        :param r: Get the version of the image
        :return: The url for the avatar of a user
        :doc-author: Trelent
        """
        src_url = cloudinary.CloudinaryImage(f'NoteBook/{route}') \
            .build_url(width=250, height=250, crop='fill', version=r.get('version'))
        return src_url
