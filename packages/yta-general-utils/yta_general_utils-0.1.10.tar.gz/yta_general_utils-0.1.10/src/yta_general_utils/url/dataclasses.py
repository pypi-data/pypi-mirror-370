from yta_validation.parameter import ParameterValidator
from urllib import parse as url_parse
from dataclasses import dataclass
from typing import Union


@dataclass
class UrlParameter:
    """
    Class to wrap an url parameter and make working
    with it easier.
    """

    @property
    def as_dict(
        self
    ) -> dict:
        """
        Get the UrlParameter as a dict. This method raises
        an Exception if it doesn't have a name.
        """
        if not self.can_be_dict:
            raise Exception('This UrlParameter does not have a name so it cannot be a dict.')

        return {
            self.name: self.value
        }

    @property
    def can_be_dict(
        self
    ) -> bool:
        """
        Check if this UrlParameter can be dict or not
        due to its name.
        """
        return self.name is not None
    
    @property
    def encoded(
        self
    ) -> str:
        """
        Get the parameter encoded as the RFC 3986 says
        by using the urllib library 'quote' method.

        - From 'hola dani' to 'hola%20dani'.
        - From 'key=value largo' to 'key=value%20largo'
        """
        return (
            f'{url_parse.quote(self.name)}={url_parse.quote(self.value)}'
            if self.name else
            url_parse.quote(self.value)
        )

    def __init__(
        self,
        name: Union[str, None],
        value: str
    ):
        self.name = name
        self.value = value

    @staticmethod
    def from_str(
        parameter: str
    ) -> 'UrlParameter':
        ParameterValidator.validate_mandatory_string('parameter', parameter, do_accept_empty = False)

        return UrlParameter(name = None, value = parameter)

    @staticmethod
    def from_dict(
        parameter: dict
    ) -> 'UrlParameter':
        """
        Transform the given 'parameter' dict into a UrlParameter
        instance. The provided 'parameter' parameter must be a
        dict containing only one key=value pair.
        """
        # TODO: Manipulate to make 'do_accept_empty' parameter
        ParameterValidator.validate_mandatory_dict('parameter', parameter)

        if len(parameter) != 1:
            raise Exception('The provided "parameter" does not contain only one key=value.')
        
        key, value = next(iter(parameter.items()))

        return UrlParameter(name = key, value = value)
    
    def __str__(
        self
    ) -> str:
        return (
            f'{self.name}={self.value}'
            if self.name else
            self.value
        )

@dataclass
class UrlParameters:
    """
    Class to wrap a group of UrlParameter elements to
    simplify the way we manage those items.
    """

    @property
    def as_dict(
        self
    ) -> dict:
        """
        Get the UrlParameters as a dict. This method raises
        an Exception if some Urlparameter don't have a name.
        The last keys will remain if duplicated.
        """
        if not self.can_be_dict:
            raise Exception('Some of the UrlParameters do not have a name so it cannot be a dict.')

        return {
            key: value
            for param in self.parameters
            for key, value in param.as_dict.items()
        }
    
    @property
    def can_be_dict(
        self
    ) -> bool:
        """
        Check if these UrlParameters can be dict or not
        due to their name.
        """
        return all(
            parameter.can_be_dict
            for parameter in self.parameters
        )
    
    @property
    def encoded(
        self
    ) -> str:
        """
        Get the parameters encoded as the RFC 3986 says
        by using the urllib library 'quote' method.

        - From 'hola dani&do_force' to 'hola%20dani%26do_force'.
        - From 'key=value largo&do_force' to 'key%3Dvalue%20largo%26do_forceo'
        """
        # This was previously being done with a dict
        # that included all the parameters together and
        # then 'url_parse.urlencode(parameters)', 
        # generating things like this:
        # '?query=esto%20es%20una%20frase&page=3...'.
        return '&'.join([ # %26 is & encoded
            parameter.encoded
            for parameter in self.parameters
        ])
    
    def __init__(
        self,
        parameters: list[UrlParameter]
    ):
        ParameterValidator.validate_mandatory_list_of_these_instances('parameters', parameters, UrlParameter)

        self.parameters = parameters

    @staticmethod
    def from_dict(
        parameters: dict
    ) -> 'UrlParameters':
        """
        Transform the given 'parameters' dict into a UrlParameters
        instance. The provided 'parameters' parameter must be a
        dict containing, at least, one key=value pair.
        """
        # TODO: Manipulate to make 'do_accept_empty' parameter
        ParameterValidator.validate_mandatory_dict('parameters', parameters)

        return UrlParameters([
            UrlParameter(name = key, value = value)
            for key, value in parameters.items()
        ])