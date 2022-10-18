# SPDX-FileCopyrightText: 2022 Aurelie Herbelot <aurelie.herbelot@unitn.it>
#
# SPDX-License-Identifier: AGPL-3.0-only


# -*- mode: python -*- 
# Run with pyinstaller run.spec
# Add config.py to dist/pears directory

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, BUNDLE, TOC


def collect_pkg_data(package, include_py_files=False, subdir=None):
    import os
    from PyInstaller.utils.hooks import get_package_paths, remove_prefix, PY_IGNORE_EXTENSIONS

    # Accept only strings as packages.
    if type(package) is not str:
        raise ValueError

    pkg_base, pkg_dir = get_package_paths(package)
    if subdir:
        pkg_dir = os.path.join(pkg_dir, subdir)
    # Walk through all file in the given package, looking for data files.
    data_toc = TOC()
    for dir_path, dir_names, files in os.walk(pkg_dir):
        for f in files:
            extension = os.path.splitext(f)[1]
            if include_py_files or (extension not in PY_IGNORE_EXTENSIONS):
                source_file = os.path.join(dir_path, f)
                dest_folder = remove_prefix(dir_path, os.path.dirname(pkg_base) + os.sep)
                dest_file = os.path.join(dest_folder, f)
                data_toc.append((dest_file, source_file, 'DATA'))

    return data_toc

pkg_data = collect_pkg_data('app')  # <<< Put the name of your package here


block_cipher = None

added_files = [
         ( 'app/templates', 'templates' ),
         ( 'app/static', 'static' ),
         ( 'env/lib/python3.5/site-packages/langdetect', 'langdetect' ),
         ( 'env/lib/python3.5/site-packages/justext', 'justext' ),
         ( 'env/lib/python3.5/site-packages/flask_admin', 'flask_admin' )
        ]


a = Analysis(['run.py'],
             pathex=['/home/aurelie/PeARS-org/PeARS-orchard'],
             binaries=[],
             datas=added_files,
             hiddenimports=["flask",
         "flask_restful",
         "flask_sqlalchemy",
         "flask.views",
         "flask.signals",
         "flask_restful.utils",
         "flask.helpers",
         "flask_restful.representations",
         "flask_restful.representations.json",
         "sqlalchemy.orm",
         "sqlalchemy.event",
         "sqlalchemy.ext.declarative",
         "sqlalchemy.engine.url",
          "sqlalchemy.connectors.mxodbc",
          "sqlalchemy.connectors.mysqldb",
          "sqlalchemy.connectors.zxJDBC",
          "sqlalchemy.connectorsodbc.py",
          "sqlalchemy.dialects.sqlite.base",
          "sqlalchemy.dialects.sqlitesqlite.py",
          "sqlalchemy.dialects.sybase.base",
          "sqlalchemy.dialects.sybase.mxodbc",
          "sqlalchemy.dialects.sybaseodbc.py",
          "sqlalchemy.dialects.sybasesybase.py",
          "sqlalchemy.engine.base",
          "sqlalchemy.engine.default",
          "sqlalchemy.engine.interfaces",
          "sqlalchemy.engine.reflection",
          "sqlalchemy.engine.result",
          "sqlalchemy.engine.strategies",
          "sqlalchemy.engine.threadlocal",
          "sqlalchemy.engine.url",
          "sqlalchemy.engine.util",
          "sqlalchemy.event.api",
          "sqlalchemy.event.attr",
          "sqlalchemy.event.base",
          "sqlalchemy.event.legacy",
          "sqlalchemy.event.registry",
          "sqlalchemy.events",
          "sqlalchemy.exc",
          "sqlalchemy.ext.associationproxy",
          "sqlalchemy.ext.automap",
          "sqlalchemy.ext.compiler",
          "sqlalchemy.ext.declarative.api",
          "sqlalchemy.ext.declarative.base",
          "sqlalchemy.ext.declarative.clsregistry",
          "sqlalchemy.ext.horizontal_shard",
          "sqlalchemy.ext.hybrid",
          "sqlalchemy.ext.instrumentation",
          "sqlalchemy.ext.mutable",
          "sqlalchemy.ext.orderinglist",
          "sqlalchemy.ext.serializer",
          "sqlalchemy.inspection",
          "sqlalchemy.interfaces",
          "sqlalchemy.log",
          "sqlalchemy.orm.attributes",
          "sqlalchemy.orm.base",
          "sqlalchemy.orm.collections",
          "sqlalchemy.orm.dependency",
          "sqlalchemy.orm.deprecated_interfaces",
          "sqlalchemy.orm.descriptor_props",
          "sqlalchemy.orm.dynamic",
          "sqlalchemy.orm.evaluator",
          "sqlalchemy.orm.events",
          "sqlalchemy.orm.exc",
          "sqlalchemy.orm.identity",
          "sqlalchemy.orm.instrumentation",
          "sqlalchemy.orm.interfaces",
          "sqlalchemy.orm.loading",
          "sqlalchemy.orm.mapper",
          "sqlalchemy.orm.path_registry",
          "sqlalchemy.orm.persistence",
          "sqlalchemy.orm.properties",
          "sqlalchemy.orm.query",
          "sqlalchemy.orm.relationships",
          "sqlalchemy.orm.scoping",
          "sqlalchemy.orm.session",
          "sqlalchemy.orm.state",
          "sqlalchemy.orm.strategies",
          "sqlalchemy.orm.strategy_options",
          "sqlalchemy.orm.sync",
          "sqlalchemy.orm.unitofwork",
          "sqlalchemy.orm.util",
          "sqlalchemy.pool",
          "sqlalchemy.processors",
          "sqlalchemy.schema",
          "sqlalchemy.sql.annotation",
          "sqlalchemy.sql.base",
          "sqlalchemy.sql.compiler",
          "sqlalchemy.sql.ddl",
          "sqlalchemy.sql.default_comparator",
          "sqlalchemy.sql.dml",
          "sqlalchemy.sql.elements",
          "sqlalchemy.sql.expression",
          "sqlalchemy.sql.functions",
          "sqlalchemy.sql.naming",
          "sqlalchemy.sql.operators",
          "sqlalchemy.sql.schema",
          "sqlalchemy.sql.selectable",
          "sqlalchemy.sql.sqltypes",
          "sqlalchemy.sql.type_api",
          "sqlalchemy.sql.util",
          "sqlalchemy.sql.visitors",
          "sqlalchemy.types",
          "sqlalchemy.util._collections",
          "sqlalchemy.util.compat",
          "sqlalchemy.util.deprecations",
          "sqlalchemy.util.langhelpers",
          "sqlalchemy.util.queue",
          "sqlalchemy.util.topological",
          "flask_sqlalchemy._compat",
                       ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pears',
          debug=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               pkg_data,
               strip=False,
               upx=True,
               name='pears')
