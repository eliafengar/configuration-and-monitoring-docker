from abc import ABCMeta, abstractmethod


class ConfigDAO(metaclass=ABCMeta):

    def __init__(self):
        self.config_change_listeners = []

    @abstractmethod
    def get_app_config(self):
        pass

    @abstractmethod
    def set_app_config(self, data):
        pass

    @abstractmethod
    def update_app_config(self, data):
        pass

    @abstractmethod
    def delete_app_config(self):
        pass

    def add_app_config_change_listener(self, method_to_call):
        self.config_change_listeners.append(method_to_call)

    def raise_app_config_change_event(self, data):
        for method in self.config_change_listeners:
            method(data)

    @classmethod
    def get_configured_app_names(cls):
        pass


class MonitorDAO(metaclass=ABCMeta):

    def __init__(self):
        self.stats_change_listeners = []

    @abstractmethod
    def get_app_stats(self):
        pass

    @abstractmethod
    def set_app_stats(self, data):
        pass

    @abstractmethod
    def update_app_stats(self, data):
        pass

    @abstractmethod
    def delete_app_stats(self):
        pass

    def add_app_stats_change_listener(self, method_to_call):
        self.stats_change_listeners.append(method_to_call)

    def raise_app_stats_change_event(self, data):
        for method in self.stats_change_listeners:
            method(data)

    @classmethod
    def get_stats_app_names(cls):
        pass


class ActionsDAO(metaclass=ABCMeta):

    def __init__(self):
        self.actions_change_listeners = []

    @abstractmethod
    def get_app_actions(self):
        """
        Get the Actions from Store
        :return:
        """

    @abstractmethod
    def set_app_actions(self, action):
        """
        Set the Actions in Store
        :param action:
        :return:
        """

    @abstractmethod
    def update_app_actions(self, action):
        """
        Update the Actions in Store
        :param action:
        :return:
        """

    def add_app_action_change_listener(self, method_to_call):
        self.actions_change_listeners.append(method_to_call)

    def raise_app_action_change_event(self, data):
        for method in self.actions_change_listeners:
            method(data)

    @classmethod
    def get_actions_app_names(cls):
        pass
