# RegioHelden Email template

`rh_email_tpl` is a django app used to render RegioHelden styled HTML emails. It provides also multiple Django
templatetags used as helpers for building HTML emails.

This project is meant to be used internally by RegioHelden organisation, as it has the company styles and logos.

## Installation

Simply run:
```
pip install rh_email_tpl
```

And add `rh_email_tpl` to your django `INSTALLED_APPS`. I.e.: in `settings.py` add:
```
INSTALLED_APPS = [
  ...
  "rh_email_tpl",
  ...
]
```

# Making a new release

[bump-my-version](https://github.com/callowayproject/bump-my-version) is used to manage releases.

After reaching a releasable state, run `pipx run bump-my-version bump <patch|minor|major> --message="feat: release x, refs y`

This will update the release version in `.bumpversion.toml` and the CI/CD pipelines do the rest.
