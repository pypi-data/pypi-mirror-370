# Copyright 2016 Pixar
#
# Licensed under the terms set forth in the LICENSE.txt file available at
# https://openusd.org/license.
#
# Modified by Jeremy Retailleau.

import difflib
import shutil
import tempfile
import sys
import itertools
import functools

from argparse import ArgumentParser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateError, TemplateSyntaxError


def main():
    parser = ArgumentParser(description="Generate source code from templates")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    tmp_dir = Path(tempfile.mkdtemp()) if args.validate else None

    root = Path(__file__).parent
    project_root = root.parent
    src_path = root / "templates"
    dst_paths = {
        "src": project_root / "src" / "pxr" / "gf",
        "python": project_root / "src" / "python"
    }

    env = Environment(loader=FileSystemLoader(str(src_path)), trim_blocks=True)
    env.globals.update({
        'UPPER': str.upper,
        'LOWER': str.lower,
        'ALLOW_IMPLICIT_CONVERSION': allow_implicit_conversion,
        'IS_FLOATING_POINT': is_floating_point
    })

    generators = [
        get_vec_specs(),
        get_range_specs(),
        get_quat_specs(),
        get_dual_quat_specs(),
        get_matrix_specs(2),
        get_matrix_specs(3),
        get_matrix_specs(4)
    ]

    try:
        render_templates(generators, env, dst_paths, tmp_dir, args.validate)
        if args.validate:
            validate_generated_files(tmp_dir, dst_paths)
    finally:
        if args.validate and tmp_dir:
            shutil.rmtree(tmp_dir)


def is_floating_point(scalar_type):
    return scalar_type in ['double', 'float', 'GfHalf']


def rank_scalar(scalar):
    order = ['int', 'GfHalf', 'float', 'double']
    return order.index(scalar)


def allow_implicit_conversion(src, dst):
    return rank_scalar(src) <= rank_scalar(dst)


def get_vec_specs():
    scalar_types = ['double', 'float', 'GfHalf', 'int']
    dimensions = [2, 3, 4]

    specs = sorted([
        {
            'SCL': scl,
            'DIM': dim,
            'SUFFIX': f'{dim}{scalar_suffix(scl)}',
            'VEC': vec_name(dim, scl),
            'EPS': eps(scl),
            'LIST': make_list_fn(dim),
            'VECNAME': vec_name,
            'SCALAR_SUFFIX': scalar_suffix,
            'SCALARS': scalar_types
        }
        for scl, dim in itertools.product(scalar_types, dimensions)
    ], key=lambda d: rank_scalar(d['SCL']))

    return {
        'templates': ['vec{0}.h', 'vec{0}.cpp', 'wrapVec{0}.cpp'],
        'specs': specs
    }


def get_range_specs():
    def range_name(dim, scl):
        return f'GfRange{dim}{scalar_suffix(scl)}'

    def minmax_type(dim, scl):
        return scl if dim == 1 else vec_name(dim, scl)

    def minmax_param(dim, scl):
        t = minmax_type(dim, scl)
        return f'{t} ' if dim == 1 else f'const {t} &'

    scalar_types = ['double', 'float']
    dimensions = [1, 2, 3]

    specs = sorted([
        {
            'SCL': scl,
            'MINMAX': minmax_type(dim, scl),
            'MINMAXPARM': minmax_param(dim, scl),
            'DIM': dim,
            'SUFFIX': f'{dim}{scalar_suffix(scl)}',
            'RNG': range_name(dim, scl),
            'RNGNAME': range_name,
            'SCALARS': scalar_types,
            'LIST': make_list_fn(dim)
        }
        for scl, dim in itertools.product(scalar_types, dimensions)
    ], key=lambda d: rank_scalar(d['SCL']))

    return {
        'templates': ['range{0}.h', 'range{0}.cpp', 'wrapRange{0}.cpp'],
        'specs': specs
    }


def get_quat_specs():
    def quat_name(scl):
        return f'GfQuat{scalar_suffix(scl)}'

    scalar_types = ['double', 'float', 'GfHalf']

    specs = sorted([
        {
            'SCL': scl,
            'SUFFIX': scalar_suffix(scl),
            'QUAT': quat_name(scl),
            'QUATNAME': quat_name,
            'SCALAR_SUFFIX': scalar_suffix,
            'SCALARS': scalar_types,
            'LIST': make_list_fn(4)
        }
        for scl in scalar_types
    ], key=lambda d: rank_scalar(d['SCL']))

    return {
        'templates': ['quat{0}.h', 'quat{0}.cpp', 'wrapQuat{0}.cpp'],
        'specs': specs
    }


def get_dual_quat_specs():
    def quat_name(scl):
        return f'GfQuat{scalar_suffix(scl)}'

    def dual_quat_name(scl):
        return f'GfDualQuat{scalar_suffix(scl)}'

    scalar_types = ['double', 'float', 'GfHalf']

    specs = sorted([
        {
            'SCL': scl,
            'SUFFIX': scalar_suffix(scl),
            'QUAT': quat_name(scl),
            'DUALQUAT': dual_quat_name(scl),
            'QUATNAME': quat_name,
            'DUALQUATNAME': dual_quat_name,
            'SCALAR_SUFFIX': scalar_suffix,
            'SCALARS': scalar_types,
            'LIST': make_list_fn(4)
        }
        for scl in scalar_types
    ], key=lambda d: rank_scalar(d['SCL']))

    return {
        'templates': [
            'dualQuat{0}.h',
            'dualQuat{0}.cpp',
            'wrapDualQuat{0}.cpp'
        ],
        'specs': specs
    }


def get_matrix_specs(dim):
    def matrix_name(dim, scl):
        return f'GfMatrix{dim}{scalar_suffix(scl)}'

    scalar_types = ['double', 'float']
    dimensions = [dim]

    specs = sorted([
        {
            'SCL': scl,
            'DIM': _dim,
            'FILESUFFIX': scalar_suffix(scl),
            'SUFFIX': f'{_dim}{scalar_suffix(scl)}',
            'MAT': matrix_name(_dim, scl),
            'LIST': make_list_fn(_dim),
            'MATRIX': make_matrix_fn(_dim),
            'MATNAME': matrix_name,
            'SCALARS': scalar_types
        }
        for scl, _dim in itertools.product(scalar_types, dimensions)
    ], key=lambda d: rank_scalar(d['SCL']))

    return {
        'templates': [
            f'matrix{dim}{{0}}.h',
            f'matrix{dim}{{0}}.cpp',
            f'wrapMatrix{dim}{{0}}.cpp'
        ],
        'specs': specs
    }


def scalar_suffix(scalar):
    return 'h' if scalar == 'GfHalf' else scalar[0]


def vec_name(dim, scalar):
    return f'GfVec{dim}{scalar_suffix(scalar)}'


def eps(scalar):
    return '0.001' if scalar == 'GfHalf' else 'GF_MIN_VECTOR_LENGTH'


def make_list_fn(default_n):
    def _format_list(fmt, sep=', ', num=None):
        count = num or default_n
        return sep.join(fmt % {'i': i} for i in range(count))

    return functools.partial(_format_list)


def make_matrix_fn(default_n):
    def _format_matrix(fmt, sep=', ', indent=0, diagFmt=None, num=None):
        n = default_n if num is None else num
        diag_fmt = diagFmt or fmt
        indent_str = ' ' * indent
        line_sep = sep + ('\n' + indent_str if '\n' not in sep else '')

        lines = []
        for i in range(n):
            line = [
                (diag_fmt if i == j else fmt) % {'i': i, 'j': j}
                for j in range(n)
            ]
            lines.append(sep.join(line))

        return line_sep.join(lines)
    return functools.partial(_format_matrix)


def render_templates(generators, env, dst_paths, temp_dir, validate):
    for gen in generators:
        for spec in gen['specs']:
            env.globals.update(**spec)

            for tmpl in gen['templates']:
                tmpl_file = tmpl.format('.template')
                suffix = spec.get('FILESUFFIX', spec['SUFFIX'])
                output_name = tmpl.format(suffix)
                target_dir = temp_dir or resolve_target(output_name, dst_paths)
                path = target_dir / output_name

                try:
                    content = env.get_template(tmpl_file).render(**spec)
                    if content and not content.endswith('\n'):
                        content += '\n'

                    if path.exists() and path.read_text() == content:
                        if not validate:
                            print(f"\tunchanged {path}")
                        continue

                    path.write_text(content)
                    if not validate:
                        print(f"\twrote {path}")

                except TemplateSyntaxError as err:
                    print(
                        f"Syntax Error: {err.name}:{err.lineno}: {err.message}",
                        file=sys.stderr
                    )

                except TemplateError as err:
                    print(
                        f"Template Error in {tmpl_file}: {err}",
                        file=sys.stderr
                    )


def validate_generated_files(tmp_dir, dst_paths):
    missing, diffs = [], []
    for gen_file in tmp_dir.iterdir():
        src_dir = resolve_target(gen_file.name, dst_paths)
        src_file = src_dir / gen_file.name
        if not src_file.exists():
            missing.append(str(src_file))
            continue

        src, gen = src_file.read_text(), gen_file.read_text()
        if src != gen:
            diff = '\n'.join(difflib.unified_diff(
                src.splitlines(), gen.splitlines(),
                fromfile=f'Source {src_file}', tofile=f'Generated {gen_file}'
            ))
            diffs.append(diff)

    if missing or diffs:
        messages = []
        if missing:
            messages.append(
                '*** Missing Generated Files:\n' + '\n'.join(missing))
        if diffs:
            messages.append(
                '*** Differing Generated Files:\n' + '\n\n'.join(diffs))
        raise RuntimeError('\n' + '\n'.join(messages))


def resolve_target(output_name, dst_paths):
    return (
        dst_paths["python"] if output_name.startswith('wrap')
        else dst_paths["src"]
    )


if __name__ == '__main__':
    main()
