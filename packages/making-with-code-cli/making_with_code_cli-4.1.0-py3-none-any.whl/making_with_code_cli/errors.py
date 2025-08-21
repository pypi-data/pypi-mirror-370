class MWCError(Exception):
    pass

class CurriculumSiteNotAvailable(MWCError):
    def __init__(self, site_url, *args, **kwargs):
        msg = f"Error reading curriculum metadata from {site_url}"
        super().__init__(msg)

class CurriculumNotFound(MWCError):
    def __init__(self, site_url, course_name, *args, **kwargs):
        msg = f"The curriculum site for {course_name} ({site_url}) does not have curriculum metadata for {course_name}. Ask your teacher for help."
        super().__init__(msg)

class GitServerNotAvailable(MWCError):
    def __init__(self, server_url, *args, **kwargs):
        msg = f"Error connecting to the git server at {server_url}"
        super().__init__(msg)

class MissingSetting(MWCError):
    def __init__(self, missing_setting):
        msg = f"Required setting {missing_setting} is missing. Please run mwc setup."
        super().__init__(msg)

class SoftwareInstallationError(MWCError):
    pass

class NoCurriculaAvailable(MWCError):
    pass
