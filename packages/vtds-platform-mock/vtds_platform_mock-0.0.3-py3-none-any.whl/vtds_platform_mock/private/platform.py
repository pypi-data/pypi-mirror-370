#
# MIT License
#
# (C) Copyright [2024] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Private layer implementation module for the mock platform.

"""

from vtds_base import (
    ContextualError,
)
from vtds_base.layers.platform import PlatformAPI


class Platform(PlatformAPI):
    """Platform class, implements the mock platform layer
    accessed through the python Platform API.

    """
    def __init__(self, stack, config, build_dir):
        """Constructor, stash the root of the platfform tree and the
        digested and finalized platform configuration provided by the
        caller that will drive all activities at all layers.

        """
        self.__doc__ = PlatformAPI.__doc__
        self.config = config.get('platform', None)
        if self.config is None:
            raise ContextualError(
                "no platform configuration found in top level configuration"
            )
        self.stack = stack
        self.build_dir = build_dir
        self.prepared = False

    def consolidate(self):
        return

    def prepare(self):
        self.prepared = True
        print("Preparing vtds-platform-mock")

    def validate(self):
        if not self.prepared:
            raise ContextualError(
                "cannot validate an unprepared platform, call prepare() first"
            )
        print("Validating vtds-platform-mock")

    def deploy(self):
        if not self.prepared:
            raise ContextualError(
                "cannot deploy an unprepared platform, call prepare() first"
            )
        print("Deploying vtds-platform-mock")

    def remove(self):
        if not self.prepared:
            raise ContextualError(
                "cannot deploy an unprepared platform, call prepare() first"
            )
        print("Removing vtds-platform-mock")

    def get_blade_venv_path(self):
        python_config = self.config.get('python', {})
        return python_config.get('blade_venv_path', "/root/blade-venv")

    def get_blade_python_executable(self):
        # NOTE: do not use path_join() here to construct the path. The
        # path here is being constructed for a Linux environment,
        # where path separators are always '/' and which might not
        # match the system this code is running on.
        return "%s/bin/python3" % self.get_blade_venv_path()
