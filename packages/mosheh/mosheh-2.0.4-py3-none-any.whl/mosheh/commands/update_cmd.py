"""
Encapsulating the `update` command logic, this file deals with the most important
feature present on Mosheh: to update the codebase documentation.

It seems extremely complex, but reading just a few lines shows that here is handled
more about the IO and data validation from the `mosheh.json` config file than the
logic implementation itself.
"""

from argparse import Namespace
from json import loads
from logging import Logger, getLogger
from os.path import abspath, join
from subprocess import CalledProcessError

from mosheh.codebase import read_codebase
from mosheh.doc.update import update_doc
from mosheh.types.basic import CodebaseDict
from mosheh.types.jsoncfg import IOJSON, DefaultJSON, DocumentationJSON


logger: Logger = getLogger('mosheh')


def update(args: Namespace) -> None:
    """
    Runs the Mosheh's feature for codebase tracking and updating.

    While handling the IO and data validation from the `mosheh.json` config file,
    which takes the most lines of it's body, once everything is ok, call the proper
    read-codebase function and then the generate-documentation one.

    :param args: Namespace object containing the creation information.
    :type args: argparse.Namespace
    :return: None
    :rtype: None
    """

    success_json_reading: bool = False
    doc_config: DocumentationJSON | None = None
    io_config: IOJSON | None = None

    try:
        with open(join(args.json, 'mosheh.json'), encoding='utf-8') as f:
            json_config: DefaultJSON = loads(f.read())

        doc_config = DocumentationJSON(**json_config['documentation'])
        io_config = IOJSON(**json_config['io'])

        success_json_reading = True

    except FileNotFoundError:
        logger.error(f'"{args.json}" does not exists as directory')
    except KeyError:
        logger.error(
            '"mosheh.json" must follow the `init` cmd struct with documentation and io'
        )
    except Exception as e:
        logger.critical(f'Not implemented logic for {type(e).__name__}: {e}')

    if not success_json_reading:
        return

    assert io_config and doc_config, 'io_config and doc_config must not be None'

    ROOT: str = abspath(join(args.json, io_config.get('rootDir', './')))
    logger.debug(f'JSON "io.rootDir" = {ROOT}')

    OUTPUT: str = abspath(join(args.json, io_config.get('outputDir', './')))
    logger.debug(f'JSON "io.outputDir" = {OUTPUT}')

    PROJ_NAME: str = doc_config.get('projectName', 'PROJECT')
    logger.debug(f'JSON "documentation.projectName" = {PROJ_NAME}')

    REPO_NAME: str = doc_config.get('repoName', 'REPO_NAME')
    logger.debug(f'JSON "documentation.repoName" = {REPO_NAME}')

    REPO_URL: str = doc_config.get('repoUrl', 'REPO_URL')
    logger.debug(f'JSON "documentation.repoUrl" = {REPO_URL}')

    EDIT_URI: str = doc_config.get('editUri', 'blob/main/documentation/docs')
    logger.debug(f'JSON "documentation.editUri" = {EDIT_URI}')

    LOGO_PATH: str | None = doc_config.get('logoPath')
    logger.debug(f'JSON "documentation.logoPath" = {LOGO_PATH}')

    README_PATH: str | None = doc_config.get('readmePath')
    logger.debug(f'JSON "documentation.readmePath" = {README_PATH}')

    CODEBASE_NAV_PATH: str = doc_config.get('codebaseNavPath', 'Codebase')
    logger.debug(f'JSON "documentation.codebaseNavPath" = {CODEBASE_NAV_PATH}')

    logger.info('Arguments parsed successfully')

    # Codebase Reading
    logger.info(f'Starting codebase loading at {ROOT}')
    data: CodebaseDict = read_codebase(ROOT)
    logger.info('Codebase successfully loaded')

    # Doc Generation
    logger.info('Starting final documentation updating')
    try:
        update_doc(
            codebase=data,
            root=ROOT,
            readme_path=README_PATH,
            output=OUTPUT,
            codebase_nav_path=CODEBASE_NAV_PATH,
        )
        logger.info('Documentation updated successfully')

    except CalledProcessError as e:
        logger.error(e)
    except FileNotFoundError:
        logger.error(f'"{args.json}" does not exists as directory')
    except PermissionError:
        logger.error(
            '"--json" must be a valid dir and Mosheh must have permission for this,'
            f' got "{args.json}" instead'
        )
    except Exception as e:
        logger.critical(f'Not implemented logic for {type(e).__name__}: {e}')
