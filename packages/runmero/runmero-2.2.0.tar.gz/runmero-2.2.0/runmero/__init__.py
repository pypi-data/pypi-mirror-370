# حقوق الطبع والنشر محفوظة © 2025 mero - من أرض الكنانة فلسطين
# مكتبة RunMero - قوة التشغيل المستمر في راحة يدك

__version__ = "2.5.0"
__author__ = "mero"
__email__ = "mero@palestine.dev"
__copyright__ = "حقوق الطبع والنشر محفوظة © 2025 mero - فلسطين الحبيبة"

from .core.manager import ProcessManager
from .core.process import BackgroundProcess
from .frameworks.fastapi_server import FastAPIServer
from .frameworks.flask_server import FlaskServer
from .frameworks.django_server import DjangoServer
from .frameworks.tornado_server import TornadoServer
from .termux.optimizer import TermuxOptimizer
from .termux.persistence import PersistenceManager

__all__ = [
    'ProcessManager',
    'BackgroundProcess', 
    'FastAPIServer',
    'FlaskServer',
    'DjangoServer',
    'TornadoServer',
    'TermuxOptimizer',
    'PersistenceManager'
]

def get_version():
    return __version__

def get_author():
    return __author__

def get_copyright():
    return __copyright__
