# AA Fleet Finder<a name="aa-fleet-finder"></a>

[![Version](https://img.shields.io/pypi/v/aa-fleetfinder?label=release)](https://pypi.org/project/aa-fleetfinder/)
[![License](https://img.shields.io/github/license/ppfeufer/aa-fleetfinder)](https://github.com/ppfeufer/aa-fleetfinder/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/aa-fleetfinder)](https://pypi.org/project/aa-fleetfinder/)
[![Django](https://img.shields.io/pypi/djversions/aa-fleetfinder?label=django)](https://pypi.org/project/aa-fleetfinder/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ppfeufer/aa-fleetfinder/master.svg)](https://results.pre-commit.ci/latest/github/ppfeufer/aa-fleetfinder/master)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)
[![Checks](https://github.com/ppfeufer/aa-fleetfinder/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/ppfeufer/aa-fleetfinder/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/ppfeufer/aa-fleetfinder/branch/master/graph/badge.svg?token=GFOR9GWRNQ)](https://codecov.io/gh/ppfeufer/aa-fleetfinder)
[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-fleetfinder/svg-badge.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ppfeufer/aa-fleetfinder/blob/master/CODE_OF_CONDUCT.md)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N8CL1BY)

Control access to your fleets through Alliance Auth.

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Installation](#installation)
  - [Step 1: Install the Package](#step-1-install-the-package)
  - [Step 2: Configure Alliance Auth](#step-2-configure-alliance-auth)
  - [Step 3: Add the Scheduled Task](#step-3-add-the-scheduled-task)
  - [Step 4: Finalizing the Installation](#step-4-finalizing-the-installation)
  - [Step 4: Setup Permissions](#step-4-setup-permissions)
- [Changelog](#changelog)
- [Translation Status](#translation-status)
- [Contributing](#contributing)

<!-- mdformat-toc end -->

______________________________________________________________________

## Installation<a name="installation"></a>

> [!NOTE]
>
> **AA Fleet Finder >= 2.0.0 needs at least Alliance Auth v4.0.0!**
>
> Please make sure to update your Alliance Auth instance _before_ you install this
> module or update to the latest version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.
>
> The last version compatible with Alliance Auth v3 is `1.5.2`.

### Step 1: Install the Package<a name="step-1-install-the-package"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth installation Then install the latest release directly from PyPi.

```shell
pip install aa-fleetfinder
```

### Step 2: Configure Alliance Auth<a name="step-2-configure-alliance-auth"></a>

This is fairly simple, just add the following to the `INSTALLED_APPS` of your `local.py`

Configure your AA settings (`local.py`) as follows:

- Add `"fleetfinder",` to `INSTALLED_APPS`

### Step 3: Add the Scheduled Task<a name="step-3-add-the-scheduled-task"></a>

To set up the scheduled task, add the following code to your `local.py`:

```python
# AA Fleetfinder - https://github.com/ppfeufer/aa-fleetfinder
if "fleetfinder" in INSTALLED_APPS:
    CELERYBEAT_SCHEDULE["fleetfinder_check_fleet_adverts"] = {
        "task": "fleetfinder.tasks.check_fleet_adverts",
        "schedule": crontab(minute="*/1"),
    }
```

### Step 4: Finalizing the Installation<a name="step-4-finalizing-the-installation"></a>

Run static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 4: Setup Permissions<a name="step-4-setup-permissions"></a>

Now it's time to set up access permissions for your new Fleetfinder module.

| ID                   | Description                       | Notes                                                                                                       |
| :------------------- | :-------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `access_fleetfinder` | Can access the Fleetfinder module | Your line members should have this permission, together with everyone you want to have access to he module. |
| `manage_fleets`      | Can manage fleets                 | Everyone with this permission can open and edit fleets                                                      |

## Changelog<a name="changelog"></a>

See [CHANGELOG.md](https://github.com/ppfeufer/aa-fleetfinder/blob/master/CHANGELOG.md)

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-fleetfinder/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

You want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines](https://github.com/ppfeufer/aa-fleetfinder/blob/master/CONTRIBUTING.md).\
(I promise, it's not much, just some basics)

<!-- Links -->

[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/ "Weblate Translations"
