# import sys
import os
import logging
import unittest
from unittest.suite import TestSuite

from django.conf import settings
from django.test.runner import DiscoverRunner


# sys.stdout = None
# requests.packages.urllib3.disable_warnings( InsecureRequestWarning )


def debug_print( *args ):
    pass
    # print( '[DEBUG]', *args, file=sys.stderr )


class List_handler( logging.Handler ):
    """
    Handler que guarda los logs en memoria en vez de imprimirlos,
    para poder decidir despues si se muestran o se descartan.
    """
    def __init__( self, *args, **kw ):
        super().__init__( *args, **kw )
        self.records = []

    def emit( self, record ):
        self.records.append( record )

    def flush_to_console( self ):
        debug_print(
            f"flush_to_console llamado, {len(self.records)} records" )
        formatter = self.formatter or logging.Formatter(
            '%(levelname)s %(name)s %(asctime)s %(message)s' )
        for record in self.records:
            print( formatter.format( record ) )

    def clear( self ):
        debug_print(
            f"clear llamado, descartando {len(self.records)} records" )
        self.records = []


class Log_when_fail_result( unittest.TextTestResult ):
    def __init__( self, *args, **kw  ):
        super().__init__( *args, **kw )
        self._log_handler = List_handler()
        self._log_handler.setLevel( logging.DEBUG )
        logging.getLogger().addHandler( self._log_handler )
        debug_print(
            "root handlers tras agregar List_handler:",
            logging.getLogger().handlers )

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line)) + '\n'
        else:
            return str(test) + '\n'

    def startTest( self, test ):
        super().startTest( test, )
        debug_print( f"startTest -> {test}" )

    def stopTest( self, test ):
        logging.getLogger().removeHandler( self._log_handler )
        super().stopTest( test )

    def addError( self, test, err ):
        debug_print( f"addError -> {test}" )
        # self._log_handler.flush_to_console()
        super().addError( test, err )

    def addFailure( self, test, err ):
        debug_print( f"addFailure -> {test}" )
        # self._log_handler.flush_to_console()
        super().addFailure( test, err )

    def addSuccess( self, test ):
        # self._log_handler.clear()
        super().addSuccess( test )

    def addSkip( self, test, reason ):
        # self._log_handler.clear()
        super().addSkip( test, reason )

    def printErrorList(self, flavour, errors):
        t = self._theme
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(
                f"{flavour}{t.fail_info}: {self.getDescription(test)}{t.reset}"
            )
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)
            self.stream.flush()


class Log_when_fail_test_runner( unittest.TextTestRunner ):
    resultclass = Log_when_fail_result


class CustomizedRunner( DiscoverRunner ):
    test_runner = Log_when_fail_test_runner

    def __init__( self, *args, **kw ):
        super().__init__( *args, **kw )

    def build_suite(self, *args, **kwargs):
        suite = super().build_suite( *args, **kwargs )
        filtered = TestSuite()

        for test in suite:
            testname = str( test )
            if 'unittest.loader._FailedTest' in testname.lower():
                print( testname )
            if '.tests.' in testname and self.package in testname:
                filtered.addTest( test )
        return filtered

    def setup_test_environment( self, **kargs ):
        settings.TEST_MODE = True
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
        settings.CELERY_TASK_EAGER_PROPAGATES = True
        settings.DEBUG = False
        # del settings.LOGGING[ 'root' ][ 'handlers' ]

        # from unittest.mock import patch
        # basic_config = patch( 'chibi.config.basic_config' )
        # basic_config.start()

        super().setup_test_environment( **kargs )

        root_logger = logging.getLogger()
        root_logger.setLevel( logging.DEBUG )
        for handler in list( root_logger.handlers ):
            root_logger.removeHandler( handler )

        debug_print( "test_runner class:", self.test_runner )
        debug_print(
            "test_runner.resultclass:", self.test_runner.resultclass )
        debug_print(
            "root handlers despues de limpiar:", root_logger.handlers )

        for logger_name in [
                'django.request', 'requests', 'elasticsearch', 'vcr' ]:
            logger = logging.getLogger( logger_name )
            debug_print(
                f"logger '{logger_name}': handlers={logger.handlers} "
                f"propagate={logger.propagate} level={logger.level}" )


class UnitRunner( CustomizedRunner ):
    package = '.unit.'

    def setup_databases( self, *args, **kwargs ):
        pass

    def teardown_databases( self, *args, **kwargs ):
        pass


class IntegrationRunner( CustomizedRunner ):
    package = '.integration.'


class AcceptanceRunner( CustomizedRunner ):
    package = '.acceptance.'
    os.environ[ 'DJANGO_LIVE_TEST_SERVER_ADDRESS' ] = 'localhost:8001'
