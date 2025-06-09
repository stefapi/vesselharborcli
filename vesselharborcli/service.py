
from .core.config_file import config_file


class svc_class:

    params_link = {}

    default_config = {}

    def __init__(self):
        pass

    @staticmethod
    def subparser():
        pass

    @staticmethod
    def test_name(name):
        return False

    @staticmethod
    def params(parser):
        pass
    def update_params_link(self,params_link):
        updt_link = self.params_link.copy()
        updt_link.update(params_link)
        return updt_link

    @staticmethod
    def __concat_dictionaries(dict1, dict2):
        """
        Concatenate two dictionaries containing dictionaries recursively.

        Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

        Returns:
        dict: The concatenated dictionary.
        """
        result = dict1.copy()  # Copy the first dictionary to avoid modifying it

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # If both values are dictionaries, recursively concatenate them
                result[key] =svc_class.__concat_dictionaries(result[key], value)
            else:
                # Otherwise, simply update the value
                result[key] = value

        return result

    def update_default_config(self,default_config):
        updt_config = self.__concat_dictionaries(default_config, self.default_config)
        return updt_config



class svc_store:
    def __init__(self, svc_list=None):
        if svc_list is None:
            svc_list = []
        self.svcs = svc_list

    def add_svc(self, svc):
        self.svcs.append(svc)

    def selected_app(self, app_name):
        # detect app kind based on program name prefix
        selected_svc = None
        for app in self.svcs:
            if app.test_name(app_name):
                selected_svc = app
        return selected_svc

    def update_params_link(self,params_link):
        for svc in self.svcs:
            updt_link = svc.update_params_link(params_link)
            params_link = updt_link
        return params_link

    def update_default_config(self,default_config):
        for svc in self.svcs:
            updt_config = svc.update_default_config(default_config)
            default_config = updt_config
        return default_config


