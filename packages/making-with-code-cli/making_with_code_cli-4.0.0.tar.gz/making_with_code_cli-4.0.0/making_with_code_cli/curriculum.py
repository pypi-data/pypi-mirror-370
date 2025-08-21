import requests
import json
from making_with_code_cli.errors import (
    CurriculumSiteNotAvailable,
    CurriculumNotFound,
)

LIVE_RELOAD = '<script src="/livereload.js?port=1024&amp;mindelay=10"></script>'

def get_curriculum(mwc_site_url, course_name=None):
    """Fetches curriculum metadata from the site url specified in settings.
    Returns the curriculum metadata for course_name.
    """
    url = mwc_site_url + "/manifest"
    response = requests.get(url)
    if response.ok:
        text = response.text.strip(LIVE_RELOAD)
        metadata = json.loads(text)
        if course_name:
            for course in metadata["courses"]:
                if course["name"] == course_name:
                    return course
        else:
            return metadata
        raise CurriculumNotFound(mwc_site_url, course_name)
    else:
        raise CurriculumSiteNotAvailable(mwc_site_url)
