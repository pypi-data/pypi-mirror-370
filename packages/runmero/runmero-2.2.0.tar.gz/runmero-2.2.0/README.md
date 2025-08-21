# RunMero - مكتبة إدارة العمليات في الخلفية

![RunMero Logo](https://via.placeholder.com/800x200/2E7D32/FFFFFF?text=RunMero+%7C+%D9%85%D9%83%D8%AA%D8%A8%D8%A9+%D8%A5%D8%AF%D8%A7%D8%B1%D8%A9+%D8%A7%D9%84%D8%B9%D9%85%D9%84%D9%8A%D8%A7%D8%AA)

## نظرة عامة

**RunMero** هي مكتبة Python قوية ومتقدمة مصممة خصيصاً لإدارة العمليات في الخلفية وخوادم الويب في بيئة **Termux** على نظام Android. تقدم المكتبة دعماً شاملاً لأطر عمل الويب المتعددة مع إمكانيات متقدمة للمراقبة والتحسين.

## الميزات الرئيسية

### 🚀 إدارة العمليات المتقدمة
- **إدارة العمليات في الخلفية**: تشغيل وإدارة العمليات بشكل مستمر حتى عند إغلاق التطبيق
- **المراقبة التلقائية**: مراقبة حالة العمليات وإعادة تشغيلها تلقائياً عند الحاجة
- **إدارة الموارد**: تحكم ذكي في استهلاك الموارد والذاكرة
- **نظام التبعيات**: إدارة تبعيات العمليات وترتيب تشغيلها

### 🌐 دعم أطر الويب المتعددة
- **FastAPI**: خوادم حديثة وسريعة مع دعم async/await
- **Flask**: خوادم WSGI خفيفة وموثوقة
- **Django**: إطار عمل شامل مع قاعدة بيانات ولوحة إدارة
- **Tornado**: خوادم عالية الأداء مع دعم WebSocket

### 📱 تحسين Termux المتخصص
- **تحسين البطارية**: إعدادات خاصة لتوفير استهلاك البطارية
- **تحسين الذاكرة**: إدارة ذكية للذاكرة في البيئات المحدودة
- **مراقبة النظام**: مراقبة متقدمة لموارد النظام والأداء
- **الاستمرارية**: ضمان استمرار العمليات عبر دورات حياة التطبيق

### 🖥️ واجهة سطر الأوامر التفاعلية
- **الأمر `helpmero`**: واجهة تفاعلية سهلة الاستخدام
- **إدارة الخدمات**: تشغيل وإيقاف وإعادة تشغيل الخدمات
- **مراقبة الحالة**: عرض حالة النظام والعمليات في الوقت الفعلي
- **سجلات مفصلة**: عرض وتصفية سجلات النظام والتطبيقات

## التثبيت

### متطلبات النظام
- **Termux** (إصدار حديث)
- **Python 3.11+**
- **أنظمة Android 7.0+**

### التثبيت السريع

```bash
# تثبيت المكتبة
pip install runmero

# أو للتثبيت من المصدر
git clone https://github.com/mero-palestine/runmero.git
cd runmero
pip install -e .
```

### التثبيت التفاعلي (موصى به)

```bash
# تشغيل التثبيت التفاعلي الجذاب (2-3 دقائق)
python -c "from runmero.utils.installer import install_runmero; install_runmero()"
```

## الاستخدام السريع

### بدء الواجهة التفاعلية

```bash
# تشغيل واجهة RunMero التفاعلية
helpmero

# أو
runmero
```

### مثال أساسي - خادم FastAPI

```python
from runmero.frameworks import FastAPIServer
from runmero.core import ProcessManager

# إنشاء مدير العمليات
manager = ProcessManager()

# إنشاء خادم FastAPI
server = FastAPIServer(
    name="my_fastapi_server",
    port=8000,
    host="0.0.0.0"
)

# تسجيل وتشغيل الخادم
manager.register_process(server)
manager.start_process("my_fastapi_server")

# الخادم يعمل الآن في الخلفية!
```

### مثال متقدم - إدارة متعددة الخوادم

```python
from runmero.core import ProcessManager
from runmero.frameworks import FastAPIServer, FlaskServer
from runmero.services import BackgroundServiceManager

# إنشاء مدير الخدمات
service_manager = BackgroundServiceManager()

# إعداد خوادم متعددة
fastapi_server = FastAPIServer(name="api_server", port=8000)
flask_server = FlaskServer(name="web_server", port=5000)

# تسجيل الخوادم
service_manager.register_service(fastapi_server.get_service_config())
service_manager.register_service(flask_server.get_service_config())

# تشغيل جميع الخدمات
service_manager.start_all_services()
```

## الأوامر الأساسية

### واجهة سطر الأوامر

```bash
# عرض المساعدة والأوامر المتاحة
helpmero help

# عرض حالة النظام
helpmero status

# تشغيل خدمة معينة
helpmero start <service_name>

# إيقاف خدمة
helpmero stop <service_name>

# إعادة تشغيل خدمة
helpmero restart <service_name>

# عرض السجلات
helpmero logs <service_name>

# مراقبة الموارد
helpmero monitor

# إعدادات التحسين
helpmero optimize
```

## أمثلة متقدمة

### Django مع قاعدة بيانات

```python
from runmero.frameworks import DjangoServer
from runmero.core import ProcessManager

# إعداد خادم Django
django_server = DjangoServer(
    name="django_app",
    port=8080,
    settings_module="myproject.settings",
    wsgi_application="myproject.wsgi:application"
)

# تشغيل مع قاعدة بيانات
manager = ProcessManager()
manager.register_process(django_server)
manager.start_process("django_app")
```

### WebSocket مع Tornado

```python
from runmero.frameworks import TornadoServer
from runmero.core import ProcessManager

# خادم Tornado مع WebSocket
tornado_server = TornadoServer(
    name="websocket_server",
    port=9000,
    enable_websockets=True
)

manager = ProcessManager()
manager.register_process(tornado_server)
manager.start_process("websocket_server")
```

## إعدادات التحسين

### تحسين Termux

```python
from runmero.termux import TermuxOptimizer

# تطبيق تحسينات Termux
optimizer = TermuxOptimizer()
optimizer.optimize_battery()
optimizer.optimize_memory()
optimizer.optimize_cpu()
optimizer.setup_persistence()
```

### مراقبة النظام

```python
from runmero.services import SystemMonitor

# بدء مراقبة النظام
monitor = SystemMonitor()
monitor.start_monitoring()

# الحصول على إحصائيات النظام
stats = monitor.get_system_stats()
print(f"استهلاك CPU: {stats['cpu_percent']}%")
print(f"استهلاك الذاكرة: {stats['memory_percent']}%")
```

## واجهة برمجة التطبيقات (API)

### ProcessManager

```python
from runmero.core import ProcessManager

manager = ProcessManager()

# تسجيل عملية
manager.register_process(process_instance)

# تشغيل عملية
manager.start_process("process_name")

# إيقاف عملية
manager.stop_process("process_name")

# الحصول على حالة العمليات
status = manager.get_process_status("process_name")
```

### BackgroundServiceManager

```python
from runmero.services import BackgroundServiceManager

service_manager = BackgroundServiceManager()

# تسجيل خدمة
service_manager.register_service(service_config)

# تشغيل جميع الخدمات
service_manager.start_all_services()

# إيقاف خدمة معينة
service_manager.stop_service("service_name")
```

## الدعم والمساهمة

### المساهمة في المشروع

نرحب بمساهماتكم! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) للحصول على تفاصيل حول كيفية المساهمة في تطوير RunMero.

### الإبلاغ عن المشاكل

إذا واجهت أي مشاكل أو لديك اقتراحات، يرجى فتح [issue جديد](https://github.com/mero-palestine/runmero/issues) على GitHub.

### الدعم الفني

- **الوثائق**: [runmero.readthedocs.io](https://runmero.readthedocs.io)
- **GitHub**: [github.com/mero-palestine/runmero](https://github.com/mero-palestine/runmero)
- **البريد الإلكتروني**: mero@palestine.ps

## الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف [LICENSE](LICENSE) للحصول على التفاصيل الكاملة.

## شكر وتقدير

تم تطوير RunMero بفخر في **فلسطين** 🇵🇸

### المطورون

- **mero** - المطور الرئيسي - [GitHub](https://github.com/mero-palestine)

### شكر خاص

شكر خاص لجميع المساهمين والمختبرين الذين ساعدوا في تطوير هذه المكتبة.

---

**RunMero** - قوة إدارة العمليات في راحة يدك 💪

صنع بـ ❤️ في فلسطين 🇵🇸