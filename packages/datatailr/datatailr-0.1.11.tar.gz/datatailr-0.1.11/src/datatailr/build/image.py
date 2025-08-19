# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import json
import os
from typing import Optional

from datatailr import ACL, User


class Image:
    """
    Represents a container image for a job.
    The image is defined based on its' python dependencies and two 'build scripts' expressed as Dockerfile commands.
    All attributes can be initialized with either a string or a file name.
    """

    def __init__(
        self,
        acl: Optional[ACL] = None,
        python_requirements: str | list[str] = "",
        build_script_pre: str = "",
        build_script_post: str = "",
        branch_name: Optional[str] = None,
        commit_hash: Optional[str] = None,
        path_to_repo: Optional[str] = None,
        path_to_module: Optional[str] = None,
    ):
        if acl is None:
            signed_user = User.signed_user()
            if signed_user is None:
                raise ValueError(
                    "ACL cannot be None. Please provide a valid ACL or ensure a user is signed in."
                )
        elif not isinstance(acl, ACL):
            raise TypeError("acl must be an instance of ACL.")
        self.acl = acl or ACL(signed_user)

        if isinstance(python_requirements, str) and os.path.isfile(python_requirements):
            with open(python_requirements, "r") as f:
                python_requirements = f.read()
        elif isinstance(python_requirements, list):
            python_requirements = "\n".join(python_requirements)
        if not isinstance(python_requirements, str):
            raise TypeError(
                "python_requirements must be a string or a file path to a requirements file."
            )
        self.python_requirements = python_requirements

        if os.path.isfile(build_script_pre):
            with open(build_script_pre, "r") as f:
                build_script_pre = f.read()
        if not isinstance(build_script_pre, str):
            raise TypeError(
                "build_script_pre must be a string or a file path to a script file."
            )
        self.build_script_pre = build_script_pre

        if os.path.isfile(build_script_post):
            with open(build_script_post, "r") as f:
                build_script_post = f.read()
        if not isinstance(build_script_post, str):
            raise TypeError(
                "build_script_post must be a string or a file path to a script file."
            )
        self.build_script_post = build_script_post
        self.branch_name = branch_name
        self.commit_hash = commit_hash
        self.path_to_repo = path_to_repo
        self.path_to_module = path_to_module

    def __repr__(self):
        return f"Image(acl={self.acl},)"

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == "acl" and not isinstance(value, ACL):
                raise TypeError("acl must be an instance of ACL.")
            elif key == "python_requirements" and not isinstance(value, str):
                raise TypeError("python_requirements must be a string.")
            elif key == "build_script_pre" and not isinstance(value, str):
                raise TypeError("build_script_pre must be a string.")
            elif key == "build_script_post" and not isinstance(value, str):
                raise TypeError("build_script_post must be a string.")
            elif (
                key in ["branch_name", "commit_hash", "path_to_repo", "path_to_module"]
                and value is not None
                and not isinstance(value, str)
            ):
                raise TypeError(f"{key} must be a string or None.")
            if key not in self.__dict__:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{key}'"
                )
            setattr(self, key, value)

    def to_dict(self):
        """
        Convert the Image instance to a dictionary representation.
        """
        return {
            "acl": self.acl.to_dict(),
            "python_requirements": self.python_requirements,
            "build_script_pre": self.build_script_pre,
            "build_script_post": self.build_script_post,
            "branch_name": self.branch_name,
            "commit_hash": self.commit_hash,
            "path_to_repo": self.path_to_repo,
            "path_to_module": self.path_to_module,
        }

    def to_json(self):
        """
        Convert the Image instance to a JSON string representation.
        """
        return json.dumps(self.to_dict(), indent=4)
