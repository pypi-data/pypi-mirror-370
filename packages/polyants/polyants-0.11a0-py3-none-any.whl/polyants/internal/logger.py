""" This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Created on Aug 12, 2024

@author: pymancer@gmail.com (polyanalitika.ru)
"""

import logging


class Logger:
    log = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls).__new__(cls)
            cls.instance.setup()
        return cls.instance

    def setup(self) -> None:
        self.log = logging.getLogger('polyants')
        self.log.addHandler(logging.NullHandler())


log = Logger().log
