"""
The tool to check the availability or syntax of domain, IP or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provides a way to convert our internal URL.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/#/special-thanks

Contributors:
    https://pyfunceble.github.io/#/contributors

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://docs.pyfunceble.com

Project homepage:
    https://pyfunceble.github.io/

License:
::


    Copyright 2017, 2018, 2019, 2020, 2022, 2023, 2024, 2025 Nissar Chababy

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from typing import Any

import PyFunceble.storage
from PyFunceble.converter.base import ConverterBase
from PyFunceble.utils.version import VersionUtility


class InternalUrlConverter(ConverterBase):
    """
    Converter of the internal URLs.

    .. note::
        The internal URLs are actually the URL that has nothing to
        do with what we are going to test.

        They are only relevant for the software itself.
    """

    @ConverterBase.data_to_convert.setter
    def data_to_convert(self, value: Any) -> None:
        """
        Overrides the default behavior.

        :raise TypeError:
            When the given data to convert is not :py:class:`str`
        """
        if not isinstance(value, str):
            raise TypeError(f"<value> should be {str}, {type(value)} given.")

        # pylint: disable=no-member
        super(InternalUrlConverter, self.__class__).data_to_convert.fset(self, value)

    def get_converted(self) -> str:
        """
        Provides the converted data (after conversion)
        """

        return self.convert(self.data_to_convert)

    def convert(self, data: Any, *, aggressive: bool = False) -> str:
        """
        Converts the given dataset.

        :param data:
            The data to convert.
        """

        _ = aggressive

        if VersionUtility(PyFunceble.storage.PROJECT_VERSION).is_dev():
            return data.replace("master", "dev")
        return data.replace("dev", "master")
