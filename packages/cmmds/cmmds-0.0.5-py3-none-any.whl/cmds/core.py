from typing import Literal, Generic, TypeVar, Optional, Any, List, Mapping, Type, Sequence
from argparse import ArgumentParser
from subprocess import run
from dataclasses import dataclass, fields, asdict
from sys import stderr, stdout
from pprint import pprint
import re
from itertools import chain
import sys
import os


# TODO: help message for both args and command
# TODO: helper function quickly create simple command, args, etc.
# Use genertics to limit command class's args class
# TODO: support literal args

@dataclass
class Arguments:
    range: str = ''
    dry_run: bool = False
    preset: str = ''

    def __post_init__(self):
        # TODO: check reserved args (e.g. dry_run) are not used
        parser = ArgumentParser()
        for k in fields(self):
            k = k.name
            v = getattr(self, k)
            if k == 'range':    # TODO: handle literal class
                parser.add_argument(f'range', default=v, type=type(v))
            elif isinstance(v, bool):
                parser.add_argument(f'--{k}', default=int(v), type=int)
            else:
                parser.add_argument(f'--{k}', default=v, type=type(v))
        args = parser.parse_args()
        for k, v in args._get_kwargs():
            setattr(self, k, v)
        presets = self.presets()
        if self.preset:
            if self.preset in presets:
                updated_args = presets[self.preset]
                if not isinstance(updated_args, dict):
                    updated_args = asdict(updated_args)
                if not set(updated_args.keys()).issubset(set(asdict(self).keys())):
                    raise ValueError(f"Preset keys {updated_args.keys()} are not subset of arguments {asdict(self).keys()}!")
                for k, v in updated_args.items():
                    setattr(self, k, v)
            else:
                raise ValueError(f'Preset {self.preset} not found!')
        self.verify_range()

    def verify_range(self) -> bool:
        if self.range:
            single_range_pattern = '\d+(:\d+(:\d+)?)?'
            pattern = f'({single_range_pattern},)*{single_range_pattern},?'
            ret = re.match(pattern, self.range)
            if not ret:
                print("Invalid range! No steps run.", file=sys.stderr)
                return False
            return True
        else:
            return False

    @property
    def steps(self):
        if self.verify_range():
            ret = []
            for r in self.range.split(','):
                slce = r.split(':')
                slce = tuple(map(int, slce))
                if len(slce) == 1:
                    ret.append(range(slce[0], slce[0] + 1))
                else:
                    ret.append(range(*slce))
            return chain(*ret)
        else:
            return ()

    def presets(self) -> dict[str, dict[str, any] | type['Arguments']]:
        """Override this method to add presets."""
        return dict()


# TODO: use abstract base class
@dataclass
class Command:
    args: Arguments

    def command(self) -> str | Sequence[str]:
        raise NotImplementedError

    def env(self) -> Mapping[str, str] | None:
        """Override parent process's env vars."""
        return None

    def update_env(self) -> Mapping[str, str] | None:
        """Update parent process's env vars."""
        return None


    @property
    def _joined_command(self) -> str:
        if self.command():
            return ' '.join(self.command()) if isinstance(self.command(), (tuple, list)) else self.command()
        else:
            return ''


    def run(self):
        if self.command():
            env_diff = self.update_env()
            new_env = self.env()
            assert not (env_diff and new_env), 'You can only implement one of `env` and `update_env`!'
            if env_diff:
                new_env = os.environ.copy()
                new_env.update(env_diff)
            if env_diff or self.env():
                updated_env = env_diff or self.env()
                env_prefix = ' '.join(f'{k}={v}' for k, v in updated_env.items())
                env_prefix += ' '
            else:
                env_prefix = ''
            print('+ ' + env_prefix + self._joined_command)
            if not self.args.dry_run:
                run(self._joined_command, shell='bash', stdout=stdout, stderr=stderr, check=True, env=new_env)

    run_all = run

    def __repr__(self) -> str:
        return self._joined_command + '  # env: ' + str(self.env() or self.update_env() or '')


# TODO: --help message for command group
@dataclass
class CommandGroup(Command):
    commands: Sequence[Type[Command]]

    def __post_init__(self):
        self._cmd_instances = [c(self.args) for c in self.commands]

    def run_all(self):
        for cmd in self._cmd_instances:
            cmd.run_all()

    def run(self):
        for i in self.args.steps:
            cmd = self._cmd_instances[i]
            cmd.run_all()

    def __repr__(self) -> str:
        ret = type(self).__name__ + ':\n  '
        ret += '\n  '.join(f'{i} {type(cmd).__name__}:  {cmd}' for i, cmd in enumerate(self._cmd_instances))
        ret += '\n'
        return ret


    def __str__(self) -> str:
        ret = type(self).__name__ + ':\n  '
        ret += '\n  '.join(f'{i} {type(cmd).__name__}' for i, cmd in enumerate(self._cmd_instances))
        ret += '\n'
        return ret

