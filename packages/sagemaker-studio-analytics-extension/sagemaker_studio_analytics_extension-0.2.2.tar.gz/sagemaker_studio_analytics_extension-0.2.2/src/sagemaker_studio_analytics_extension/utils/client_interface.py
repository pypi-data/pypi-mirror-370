from abc import ABCMeta, abstractmethod


class IClient(metaclass=ABCMeta):
    @abstractmethod
    def get_sts_client():
        """Interface Method"""
