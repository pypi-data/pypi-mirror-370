"""
The tool to check the availability or syntax of domain, IP or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provides the base of all mariadb related migrations.

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

import functools
from typing import Any, Generator, Tuple

from sqlalchemy.sql import text

import PyFunceble.cli.facility
from PyFunceble.cli.migrators.db_base import DBMigratorBase


class MariaDBMigratorBase(DBMigratorBase):
    """
    Provides the base of all our mariadb migration.
    """

    def execute_if_authorized(default: Any = None):  # pylint: disable=no-self-argument
        """
        Executes the decorated method only if we are authorized to process.
        Otherwise, apply the given :code:`default`.
        """

        def inner_method(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.authorized:
                    return func(self, *args, **kwargs)  # pylint: disable=not-callable
                return self if default is None else default

            return wrapper

        return inner_method

    def get_rows(
        self, statement: str, limit: int = 20
    ) -> Generator[Tuple[str, int], dict, None]:
        """
        Run the given statement with a defined limit, and yield each row.

        .. warning::
            If you don't delete the given rows, this method will be infinite.
        """

        statement += f" LIMIT {limit}"

        while True:
            db_result = list(self.db_session.execute(text(statement)).fetchall())

            if not db_result:
                break

            for result in db_result:
                yield dict(result)

    @property
    def authorized(self) -> bool:
        """
        Provides the authorization to process.
        """

        return PyFunceble.cli.facility.CredentialLoader.is_already_loaded()

    @execute_if_authorized(None)
    def migrate(self) -> "MariaDBMigratorBase":
        """
        Provides the migration (itself).
        """

        raise NotImplementedError()

    @execute_if_authorized(None)
    def start(self) -> "MariaDBMigratorBase":
        """
        Starts the migration if wanted.
        """

        PyFunceble.facility.Logger.info("Started migration.")

        self.migrate()

        PyFunceble.facility.Logger.info("Finished migration.")

        return self
