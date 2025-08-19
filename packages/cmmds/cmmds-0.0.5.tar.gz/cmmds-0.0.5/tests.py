#!/usr/bin/env python

from typing import List, Mapping, Sequence
from cmds import Arguments, Command, CommandGroup
from dataclasses import dataclass


@dataclass
class CustomArgs(Arguments):
    a: int = 0
    b: int = 1
    c: str = 'apple'
    d: bool = True

    new_text: str = 'replaced'

    def presets(self) -> dict[str, dict[str, any] | type['Arguments']]:
        allOne = dict(a=1, b=1, c='1')
        allTwo = dict(a=2, b=2, c='2')
        allThree = dict(a=3, b=3, c='3', q=12)
        return dict(allOne=allOne, allTwo=allTwo, allThree=allThree)


class Cmd0(Command):
    def command(self) -> str | Sequence[str]:
        return f'echo {self.args.a}'


class Cmd1(Command):
    def command(self) -> str | Sequence[str]:
        return f'echo {self.args.d}'


class Cmd2(Command):
    def command(self) -> str | Sequence[str]:
        return 'AAA=2 echo $XXX'

    def update_env(self) -> Mapping[str, str] | None:
        return dict(XXX=self.args.new_text)


class Cmd3(Command):
    def command(self) -> str | Sequence[str]:
        return ['echo', '1', '2', '3']


class CmdWithPresets(Command):
    def command(self) -> str | Sequence[str]:
        return f'echo {self.args.a}...{self.args.b}...{self.args.c}'

            
def test_single():
    arg = CustomArgs()
    cmd0 = Cmd0(arg)
    cmd0.run()
    print('print result:')
    print(cmd0)


def test_single_env_update():
    arg = CustomArgs()
    cmd2 = Cmd2(arg)
    cmd2.run()
    print('print result:')
    print(cmd2)


def test_group():
    arg = CustomArgs()
    group = CommandGroup(arg, [Cmd0, Cmd1, Cmd2])
    print('print group result:')
    print(group)
    group.run()


def test_single_list():
    arg = CustomArgs()
    cmd3 = Cmd3(arg)
    cmd3.run()
    print('print result:')
    print(cmd3)


def test_presets():
    arg = CustomArgs()
    cmd4 = CmdWithPresets(arg)
    cmd4.run()
    print('print result:')
    print(cmd4)


if __name__ == '__main__':
    # TODO: support recursive command Group
    # TODO: --help message for command group
    # test_single()
    # test_single_env_update()
    test_presets()
    # test_group()
    # test_single_list()
