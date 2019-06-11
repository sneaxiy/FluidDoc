#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import argparse
import sys
import types

import paddle.fluid as fluid


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--submodules', nargs="*")
    parser.add_argument(
        '--module', type=str, help='Generate the documentation of which module')
    parser.add_argument(
        '--module_prefix', type=str, help='Generate the prefix of module')
    return parser.parse_args()


class DocGenerator(object):
    def __init__(self, module_name=None, module_prefix=None, stream=sys.stdout):
        if module_name == "":
            module_name = None

        if module_prefix == "":
            module_prefix = None

        self.stream = stream
        if module_name is None:
            self.module_name = "fluid"
        else:
            self.module_name = "fluid." + module_name
        if module_name is None:
            self.module = fluid
        else: 
            self.module = fluid
            for each_module_name in module_name.split('.'): 
                if not hasattr(self.module, each_module_name):
                    raise ValueError("Cannot find fluid.{0}".format(module_name))
                else:
                    self.module = getattr(self.module, each_module_name)

        if module_prefix is None:
            self.module_prefix = self.module_name 
        else:
            self.module_prefix = "fluid." + module_prefix

        self.stream.write('''..  THIS FILE IS GENERATED BY `gen_doc.{py|sh}`
    !DO NOT EDIT THIS FILE MANUALLY!

''')            

        header_name = self.module_name
        if module_prefix is not None:
            prefix_len = len(self.module_prefix)
            assert self.module_prefix == self.module_name[0:prefix_len],    \
                "module_prefix must be prefix of module_name"
            diff_name = self.module_name[prefix_len+1:]
            if diff_name != "":
                header_name = diff_name
         
        self._print_header_(header_name, dot='=', is_title=True)

    def print_submodule(self, submodule_name):
        submodule = getattr(self.module, submodule_name)
        if submodule is None:
            raise ValueError("Cannot find submodule {0}".format(submodule_name))
        self.print_section(submodule_name)

        for item in sorted(submodule.__all__,key=str.lower):
            self.print_item(item)

    def print_current_module(self):
        for item in sorted(self.module.__all__,key=str.lower):
            self.print_item(item)

    def print_section(self, name):
        self._print_header_(name, dot='=', is_title=False)

    def print_item(self, name):
        item = getattr(self.module, name, None)
        if item is None:
            return
        if isinstance(item, types.TypeType):
            self.print_class(name)
        elif isinstance(item, types.FunctionType):
            self.print_method(name)
        else:
            pass

    def print_class(self, name):
        self._print_ref_(name)
        self._print_header_(name, dot='-', is_title=False)
        self.stream.write('''..  autoclass:: paddle.{0}.{1}
    :members:
    :noindex:

'''.format(self.module_prefix, name))

    def print_method(self, name):
        self._print_ref_(name)
        self._print_header_(name, dot='-', is_title=False)
        self.stream.write('''..  autofunction:: paddle.{0}.{1}
    :noindex:

'''.format(self.module_prefix, name))

    def _print_header_(self, name, dot, is_title):
        dot_line = dot * len(name)
        if is_title:
            self.stream.write(dot_line)
            self.stream.write('\n')
        self.stream.write(name)
        self.stream.write('\n')
        self.stream.write(dot_line)
        self.stream.write('\n')
        self.stream.write('\n')

    def _print_ref_(self, name):
        self.stream.write(".. _api_{0}_{1}:\n\n".format("_".join(
            self.module_prefix.split(".")), name))


def main():
    args = parse_arg()
    gen = DocGenerator(args.module, args.module_prefix)
    if args.submodules is None:
        gen.print_current_module()
    else:
        for submodule_name in args.submodules:
            gen.print_submodule(submodule_name)


if __name__ == '__main__':
    main()
