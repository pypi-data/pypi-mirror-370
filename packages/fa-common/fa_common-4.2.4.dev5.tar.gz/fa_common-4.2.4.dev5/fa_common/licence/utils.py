import getpass
import platform
from datetime import datetime
from importlib import import_module
from json import loads as load_json
from os.path import isfile

from requests import post

from fa_common import logger as LOG


def get_licence_data(package: str):
    try:
        pt_module = import_module(f"{package}.pytransform")
        _pytransform = pt_module._pytransform  # type: ignore
    except Exception:
        # For super mode
        pt_module = import_module(f"{package}.pytransform")
        get_user_data = pt_module.get_user_data  # type: ignore

        return get_user_data().decode()

    from ctypes import PYFUNCTYPE, py_object

    prototype = PYFUNCTYPE(py_object)
    dlfunc = prototype(("get_registration_code", _pytransform))
    rcode = dlfunc().decode()
    index = rcode.find(";", rcode.find("*CODE:"))
    return rcode[index + 1 :]


def _check_expiry(date_str: str):
    curr_date = datetime.today()  # noqa: DTZ002
    lic_date = datetime.strptime(date_str, "%Y-%m-%d")  # noqa: DTZ007
    if curr_date > lic_date:
        raise RuntimeError(f"Licence expired {date_str}")

    else:
        print(f"Licence valid until {date_str}")


def _get_container_id():
    cgroup_file = "/proc/self/cgroup"
    cid = None

    # Check the file exists..
    if not isfile(cgroup_file):
        return cid

    with open(cgroup_file) as f:
        for line in f:
            if line.split(":", 2)[1] == "name=systemd":
                cid = line.strip().split("/")[-1]
                break

    # Return the container id, else None
    return cid if cid is not None and len(cid) > 0 else None


def _get_distro_name():
    if platform.system() != "Linux":
        return None

    if isfile("/etc/os-release"):
        with open("/etc/os-release") as f:
            vals = dict([line.split("=") for line in f])
            if vals.get("PRETTY_NAME") is not None:
                return vals.get("PRETTY_NAME")

    if isfile("/etc/issue.net"):
        with open("/etc/issue.net") as f:
            return f.readline()

    if isfile("/etc/issue"):
        with open("/etc/issue") as f:
            return f.readline()

    return None


def _call_home(package: str, audit_url: str, data, silent_audit_fail: bool = True):
    product_version = None
    try:
        product_version = import_module(package).__version__  # type: ignore
    except Exception as e:
        LOG.debug(f"product_version Error: {e}")

    try:
        # Only include fields from licence payload that we want
        key_list = ["product", "licensee", "expiry", "auditUrl", "features"]
        data = {key: value for (key, value) in data.items() if key in key_list}

        # Add the __version__ from the obfuscated package is available
        if product_version is not None:
            data["productVersion"] = product_version

        # Add Container ID (docker) if applicable
        cid = _get_container_id()
        if cid is not None:
            data["containerId"] = cid

        # Add username
        data["username"] = getpass.getuser()

        # Add node name (hostname)
        data["node"] = platform.node()

        # Add python version
        data["pythonVersion"] = platform.python_version()

        # Add platform (os/kernel/arch)
        data["platform"] = platform.platform()

        # For posix platforms include the distro version if possible
        distro = _get_distro_name()
        if distro is not None:
            data["distro"] = distro

        # Send audit information via web api
        response = post(audit_url, json=data)
        LOG.debug(f"POST Response: {response}")
    except Exception as e:
        LOG.debug(f"Error collecting/sending audit: {e}")
        if silent_audit_fail:
            # Fail silently, we don't actually want to impact the
            # user just because the audit event failed to log
            pass
        else:
            raise RuntimeError(f"Failed to contact licence audit server! ({audit_url})") from e


def check_licence(package: str, product_name: str, silent_audit_fail: bool = True):
    """
    Plugin to verify the licence file for packages obfuscated with PyArmor.

    This plugin will also call a rest api when the plugin is triggered. This call includes
    a payload containing details of the product, the licence, and the client's environment.

    To use you need to create a wrapper in your project which imports this plugin. Then
    reference the wrapper in your package (e.g. in the parent `__init__.py`) using PyArmor's
    plugin syntax.

    Example:
    ========
    data_mosaic_core/scripts/check_licence.py:
    ------------------------------------------
        from fa_common.licence.utils import check_licence as _check_licence

        def check_licence():
            _check_licence(package = "data_mosaic_core",
                        product_name = "data-mosaic-core",
                        silent_audit_fail = True)

    data_mosaic_core/data_mosaic_core/__init__.py:
    ----------------------------------------------
        # {PyArmor Plugins}
        # PyArmor Plugin: check_licence()

    Obfuscate the package:
    ----------------------
    pipenv run pyarmor \
                obfuscate \
                --with-license outer \
                --plugin scripts/check_licence.py \
                --recursive \
                --output $OUTDIR/data_mosaic_core \
                data_mosaic_core/__init__.py

    Arguments:
        package {str}: Name of the python package
        product_name {str}: Name of the product which should match the licence.lic
        silent_audit_fail {bool}: Suppress error if web service call fails

    raises:
        RuntimeError
    """

    # Load data embedded in licence
    payload = get_licence_data(package)
    lic_data = load_json(payload)

    # Check licence is for this product
    product = lic_data.get("product")
    if product != product_name:
        raise RuntimeError(f"Licence file is for {product} not {product_name}")

    # Check expiry date
    exp_date = lic_data.get("expiry")
    if exp_date is not None:
        _check_expiry(exp_date)

    # Record an audit event using the web service
    audit_url = lic_data.get("auditUrl")
    if audit_url is not None:
        _call_home(package, audit_url, lic_data, silent_audit_fail)
