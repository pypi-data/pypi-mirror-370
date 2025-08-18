[![Tests](https://github.com/DataShades/ckanext-oidc-pkce/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-oidc-pkce/actions/workflows/test.yml)

# ckanext-oidc-pkce

OpenID connect with PKCE flow authenticator for CKAN.

> **Warning**
> Developed for Okta and not tested with other providers.
> PRs or feature-requests are welcome

The plugin adds an extra route to CKAN allowing login through an external
application. This route available at `/user/login/oidc-pkce`(`oid_pkce.login`
endpoint). Original authentication system from CKAN is unchanged and it's up to
you(or another extension) to hide original login page if only SSO accounts are
allowed on the portal.

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | yes         |
| 2.10         | yes         |

## Installation

1. Install the package
   ```sh
   pip install ckanext-oidc-pkce
   ```

1. Add `oidc_pkce` to the `ckan.plugins` setting in your CKAN
   config file

1. Add SSO settings(refer [config settings](#config-settings) section for details)

## Config settings

```ini
# URL of SSO application
# Could be overriden at runtime with env var CKANEXT_OIDC_PKCE_BASE_URL
ckanext.oidc_pkce.base_url = https://12345.example.okta.com

# ClientID of SSO application
# Could be overriden at runtime with env var CKANEXT_OIDC_PKCE_CLIENT_ID
ckanext.oidc_pkce.client_id = clientid

# ClientSecret of SSO application
# (optional, only need id Client App defines a secret, default: "")
# Could be overriden at runtime with env var CKANEXT_OIDC_PKCE_CLIENT_SECRET
ckanext.oidc_pkce.client_secret = clientsecret

# Path to the authorization endpont inside SSO application
# (optional, default: /oauth2/default/v1/authorize)
ckanext.oidc_pkce.auth_path = /auth

# Path to the token endpont inside SSO application
# (optional, default: /oauth2/default/v1/token)
ckanext.oidc_pkce.token_path = /token

# Path to the userinfo endpont inside SSO application
# (optional, default: /oauth2/default/v1/userinfo)
ckanext.oidc_pkce.userinfo_path = /userinfo

# Path to the authentication response handler inside CKAN application
# (optional, default: /user/login/oidc-pkce/callback)
ckanext.oidc_pkce.redirect_path = /local/oidc/handler

# URL to redirect user in case of failed login attempt.  When empty(default)
# redirects to `came_from` URL parameter if availabe or to CKAN login page
# otherwise.
# (optional, default: )
ckanext.oidc_pkce.error_redirect = /user/register

# Scope of the authorization token. The plugin expects at least `sub`,
# `email` and `name` attributes.
# (optional, default: openid email profile)
ckanext.oidc_pkce.scope = email

# For newly created CKAN users use the same ID as one from SSO application
# (optional, default: false)
ckanext.oidc_pkce.use_same_id = true

# When connecting to an existing(non-sso) account, override user's password
# so that it becomes impossible to login using CKAN authentication system.
# Enable this flag if you want to force SSO-logins for all users that once
# used SSO-login.
# (optional, default: false)
ckanext.oidc_pkce.munge_password = true

```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
