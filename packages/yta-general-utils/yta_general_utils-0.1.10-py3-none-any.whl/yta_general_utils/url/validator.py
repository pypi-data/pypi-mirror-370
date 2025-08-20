from yta_validation.parameter import ParameterValidator
from yta_constants.regex import GeneralRegularExpression

import requests
import mimetypes


class UrlValidator:
    """
    Class to wrap functionality related to
    validating urls.
    """

    @staticmethod
    def is_url_ok(
        url: str
    ) -> bool:
        """
        Checks if the provided url is valid. It returns True if yes or
        False if not. This method uses a head request to check the 
        status_code of the response.
        """
        ParameterValidator.validate_mandatory_string('url', url, do_accept_empty = False)
        
        try:
            response = requests.head(url)

            return response.status_code == 200
        except requests.ConnectionError as e:
            # TODO: Maybe warning (?)
            #print('Something went wrong with "' + url + '" (exception raised).')
            return False
    
    def verify_image_url(
        url: str
    ):
        """
        This method will check that the provided 'url'
        is a valid one, that it is an image, and also
        will return the image file extension (if
        available), or False if not valid 'url'. The
        extension returned, if returned, contains the
        dot '.'.

        Use this method before trying to download an
        image from a url.

        This method will send a head request to the
        provided 'url', check the status_code and
        also the content-type.
        """
        # TODO: I don't like what this returns and
        # how its logic is built
        ParameterValidator.validate_mandatory_string('url', url, do_accept_empty = False)
        
        try:
            response = requests.head(url)

            if response.status_code != 200: # Maybe more than only 200 are valid
                return False
            
            if not response.headers['content-type'].startswith('image/'):
                return False
            
            # This below is like 'image/jpeg', 'application/pdf' so maybe we can just
            # split by '/' and obtain the second part, because when I guess from a
            # 'image/jpeg' content-type, the response is '.jpg' and not '.jpeg'...
            content_type = response.headers['content-type']
            extension = mimetypes.guess_extension(content_type)

            # TODO: Review this below when tested 
            # This 'other_extension' below could be a better choice maybe (read above)
            other_extension = '.' + content_type.split('/')[1]

            return (
                extension
                if extension is not None else
                other_extension
            )
        except requests.ConnectionError as e:
            # TODO: Maybe warning (?)
            #print('Something went wrong with "' + url + '" (exception raised).')
            return False

    @staticmethod
    def is_youtube_video_url(
        url: str
    ):
        """
        Checks if the provided `url` is string containing
        a valid Youtube video url. This method only checks
        that the given url is well formatted.

        Example of a valid url:
        - `https://www.youtube.com/watch?v=OpA2ZxnRs6`
        """
        ParameterValidator.validate_mandatory_string('url', url, do_accept_empty = False)

        return GeneralRegularExpression.YOUTUBE_VIDEO_URL.parse(url)