_This package is part of [The Synthetic Data Vault Project](https://sdv.dev/),
a project from [DataCebo](https://datacebo.com/)._

# Overview

The [**Synthetic Data Vault**](https://docs.sdv.dev/sdv) (SDV) is a Python
library designed to be your one-stop shop for creating tabular synthetic data.
You can get started with the publicly-available SDV Community for exploring the
benefits of synthetic data. When you're ready to take synthetic data to the
next level, upgrade to [SDV Enterprise](https://docs.sdv.dev/sdv/explore/sdv-enterprise)
and purchase [Bundles](https://docs.sdv.dev/sdv/explore/sdv-bundles) to access additional features.

This package provides a CLI for SDV Enterprise customers to easily access and
manage all SDV-related software. It allows you to:

* Input your SDV username and license key
* List out all the SDV-related packages that you have access to
* Download and install those packages

```
% sdv-installer install

Username: <email>
License Key: ********************************

Installing SDV Enterprise:
sdv-enterprise (version 0.30.0) - Installed!

Installing Bundles:
bundle-cag - Installed!
bundle-xsynthesizers - Installed!

Success! All packages have been installed. You are ready to use SDV Enterprise.
```

# How it works

The SDV Installer is a convenience wrapper around
[pip](https://pypi.org/project/pip/), the package installer for Python.
Under-the-hood, SDV Installer takes your input, determines which
package you can access, and calls pip to install those packages with the
appropriate flags and options.

To see the exact pip commands, use the `--debug` flag:

```
% sdv-installer install --debug

Username: <email>
License Key: ********************************

Installing SDV Enterprise:

pip install sdv-enterprise==0.30.0 --index-url <URL>@pypi.datacebo.com/ --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.datacebo.com

Installing Bundles:
...

Success! All packages have been installed. You are ready to use SDV Enterprise.
```

# Get the SDV Installer

Get the latest version of the SDV Installer.

```
pip install sdv-installer --update
```

SDV Installer is set up to access and manage all SDV-related packages – SDV
Enterprise, as well as Bundles. You can manage installation for a variety of
scenarios, including offline installation, partial installation, upgrading, and
more.


**For more details about installing SDV Enterprise, please see our
[Installation
Guide](https://docs.sdv.dev/sdv-enterprise/installation/instructions).**
