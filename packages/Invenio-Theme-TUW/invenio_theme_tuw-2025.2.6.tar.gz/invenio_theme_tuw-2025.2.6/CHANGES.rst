..
    Copyright (C) 2020-2025 TU Wien.

    Invenio-Theme-TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======


Version v2025.2.6 (released 2025-08-20)

- Rework the privacy note in the publish modal as a component override


Version v2025.2.5 (released 2025-08-14)

- Implement UI endpoint for listing background task failures
- make the new ``UppyUploader`` optional, like in ``Invenio-RDM-Records``


Version v2025.2.4 (released 2025-08-12)

- fix `record_ui` in rdm-curation notification templates some more


Version v2025.2.3 (released 2025-08-12)

- fix overzealous change of `record` to `record_ui` in rdm-curation notification templates
- use `invenio_url_for()` for generating URLs in notification templates
- disable curation consent input in user settings
- remove curation consent from users info admin endpoint


Version v2025.2.2 (released 2025-08-06)

- add necessary JS script with nonce for `Flask-DebugToolbar`
- update community-stats styling


Version v2025.2.1 (released 2025-08-02)

- v13: chase `record` type change in templates for schema.org serialization


Version v2025.2.0 (released 2025-08-01)

- update link to FAQs
- v13: fix text color of request check titles
- v13: override the new UppyUploader to not allow selection of folders
- v13: chase upstream frontend changes
- v13: add `robots.txt` template
- v13: chase change in record ownership semantics
- v13: bump minimum requirements


Version v2025.1.17 (released 2025-07-24)

- shift around places of some conveyed information:
- update wording of the text on the frontpage
- move the "account activation" email text to the "welcome email"
- shorten "account activation" email text, and gear it towards externals


Version v2025.1.16 (released 2025-07-18)

- fix community KPI dashboard controls


Version v2025.1.15 (released 2025-07-17)

- remove unused code and dependencies
- visually simplify the community stats map
- implement input controls for the map
- add table below map showing the stats numerically
- add `THEME_TUW_CRDM_URL` configuration option
- hide community statistics tab in empty communities
- allow community curators to view the stats map


Version v2025.1.14 (released 2025-06-27)

- Fix styling of dropdown elements with too many inputs
- Bump required Python version to >=3.12
- Pin `opensearch-py` to v2
- Update SLS (DE) link


Version v2025.1.13 (released 2025-06-03)

- Some styling updates
- Implement per-community record KPI dashboard, visible to community owners
- Update user welcome text


Version v2025.1.12 (released 2025-04-28)

- Remove dead link to the open science page of BMBWF
- Add redirect from `/about` to `/tuw/about`


Version v2025.1.11 (released 2025-03-29)

- Remove the customized build projects and use the standard `rspack` project instead
- Allow test jobs to be run on a schedule


Version v2025.1.10 (released 2025-03-21)

- Reverse order of listed users on admin endpoint
- Footer: Add `About` page
- Add following subpages to the `About` page: `API Docs`, `About VRE`, `About DAMAP`


Version v2025.1.9 (released 2025-03-11)

- Always show the link to the record for `rdm-curation` requests


Version v2025.1.8 (released 2025-03-01)

- Add `rspack` build
- Change styling of hovered links in the footer


Version 2025.1.7 (released 2025-02-28)

- Stop hiding the community selection input on the deposit form


Version 2025.1.6 (released 2025-02-13)

- Update the welcome text to match the new curation workflow


Version 2025.1.5 (released 2025-02-13)

- Replace mentions of "TU.it" with "Campus IT"


Version 2025.1.4 (released 2025-02-10)

- Update CHANGES.rst - the previous version seems to have broken a font in the wheel?


Version 2025.1.3 (released 2025-02-08)

- Remove record publication email templates as they're not used anymore
- Update styling of curation consent form
- Rework "contact uploader" mechanism to also use the user's secondary email and avoid leaking details
- Reduce default captcha length to 8 from 10


Version 2025.1.2 (released 2025-02-06)

- Update notification email text
- Update translation infrastructure


Version 2025.1.1 (released 2025-02-04)

- Remove stray `lazy_gettext("")` from "resubmit" notification email


Version 2025.1.0 (released 2025-01-31)

- Add missing "to" in "contact uploader" email
- Provide error handling for when schema.org serialization fails
- Add harmonized overrides for request notifications
- Add extra notifications to make the curation workflow clearer


Version 2025.0.0 (released 2025-01-13)

- Update user welcome text template
- Add tombstone page for Derek


Version 2024.3 (released 2024-10-01, updated 2024-11-29)

- Replace `setuptools` with `hatchling` as build system
- Clean up old built-up cruft
- Brush up tests
- Fix frontpage override
- Fix some new SonarQube complaints
- Register admin menu entry for TUW users administration page
- Prevent the local login segment from being hidden on small screens
- Chase copy from/to instruction update from Invenio-Assets for webpack config
- Reorganize email templates and add templates for publication notifications


Version 2024.2 (released 2024-06-24, updated 2024-09-17)

- v12 compat: Update frontend build project
- v12 compat: Replace Flask-BabelEx with Invenio-i18n
- v12 compat: Chase jinja template changes
- v12 compat: Chase Invenio-App-RDM styling changes
- v12 compat: Chase record ownership changes
- v12 compat: Exclude deleted records from frontpage search
- Replace startup hacks with `finalize_app` entrypoint
- Export JSON-LD locally instead of querying doi.org
- Modernize & update tests
- Only display statistics in the sidebar to record owners
- Hide community selection on deposit form
- Handle `NoResultFound` exception in guarded deposit page
- Add support for `Invenio-Banners`
- Remove `THEME_TUW_FRONTPAGE_{INFO,WARNING}` config options
- Hide data volume from metrics sidebar box
- Tweak FAIRsharing logo to reduce data transfer
- Provide fallback values for record searches on the frontpage
- Make background colour consistent with control bar for audio file preview iframes
- Add admin page with response texts for permission requests
- Render missing administration menu items in the settings menu
- Redirect user to draft preview page if they are allowed to preview but not to edit
- Fix styling of the login page in case it ever gets rendered again
- Tighten default rate limit on "contact uploader" form
- Require longer captchas for that form as well
- Send contact email to admins in BCC


Version 2024.1 (released 2024-03-01, updated 2024-05-29)

- Views: add status code in guards' response
- Add automated tests
- Add TUW-specific user administration page
- Fetch TISS ID from user profile rather than from old access tokens
- Updated the text on the deposit guard page


Version 2023.2 (released 2023-04-24, updated 2023-12-22)

- v11 compat: Update templates and frontend build project
- Remove PDF preview override, as it has been merged upstream
- Rework "contact uploader" feature to a dedicated contact form
- Distribute ``.jinja`` files with releases
- Update PyPI publication flow
- Partially prefill "contact uploader" form on authenticated users
- Add FAIRsharing logo to the footer and readjust CSS grid
- Add rate limiting for the "contact uploader" feature
- Add a feature flag for enabling/disabling the feature
- Hide the contact form link when viewing one's own records' landing pages
- Optionally add the specified email address to CC (disabled by default)
- Preserve message formatting in HTML emails
- Remove "Fair Data Austria" logo from the footer and readjust CSS grid
- Add TU Wien logo to static assets
- Frontpage: Add link to the CRDM
- Prepare the repository for seasonal weather
- Add user settings page about record curation


Version 2023.1 (released 2023-01-13, updated 2023-04-24)

- Display the record's first uploaders on the landing pages
- Fix the draft preview page failing with a 404 code
- Update links to policies
- UI: fix header warning styling and improve permission guard pages
- UI: rework deposit permission guard page text
- UI: further improve deposit permission guard page text and modify its header icon
- Footer: Improve layout and responsiveness on smaller screens
- Fix naming of grid classes in css to avoid overlaps with `semantic-ui-less`
- UI: remove reference to test instance from deposit guard page
- Add possibility to a render an info box in the frontpage


Version 2022.6 (released 2022-10-17, updated 2022-11-30)

- v10 compat: Replace direct 'elasticsearch' import
- v10 compat: Load and pass ``custom_fields`` in ``communities_new`` view function
- Override ``app.config`` to specially handle our ``SITE_{API,UI}_URL`` config items
- Remove the ``communities_new`` override
- Remove "under development" text in frontpage
- Render missing flashed messages
- Rework the initialization procedure used for some custom overrides
- Migrate from setup.py to setup.cfg
- Remove old documents
- Hide the privacy policy for now, until it is accepted and published centrally
- Move Flask config override from Invenio-Theme-TUW to Invenio-Config-TUW
- Disable Matomo integration by default
- Use fallback system font during initial page load
- Update footer logos, links and file links


Version 2022.5 (released 2022-09-06, updated 2022-10-11)

- Add surrounding element to the recent uploads on the frontpage
- Some styling fixes
- Add config variable for Matomo site ID
- Rework the staging warning into a more general customizable warning
- Make the input element sizing on the deposit page more uniform
- Update the contact page
- Self-serve Google fonts used for the TUW corporate design
- Fix missing search bar in results page
- Remove inline styling from templates
- Add total record count to the search bar placeholder
- Scale down hero images
- Add possibility to a render a warning box in the frontpage


Version 2022.4 (released 2022-07-19, updated 2022-08-25)

- v9 compat: Chase upstream changes in our overridden templates
- v9 compat: Add permission guard page for community creation
- Add config variable for the FAQ link
- Remove unnecessary/outdated template and JS overrides
- Refactor directory structure for remaining template overrides
- Add comments marking the changes and their reasons in remaining overrides
- UI enhancements for mobile (side bar and communities frontpage)
- Reverse contents of CHANGES.rst (recent changes are shown on top)
- Fix wrong route in deposit guard template
- Update description in frontpage
- Override the ``communities_new`` view function (to support ``LocalProxy`` objects as ``SITE_UI_URL``)


Version 2022.3 (released 2022-03-11, updated 2022-07-14)

- Make the theme compatible with the v8 release of InvenioRDM
- Fix some styling issues
- Fix race conditions regarding blueprint overrides during init phase
- Add layer of protection around the deposit pages
- Update text on frontpage and contact page
- Reformat jinja templates
- Add tombstone page for Florian
- Refactor the module to actually play nice with InvenioRDM v8


Version 2022.2 (released 2022-02-07)

- Rebrand to 'TU Data Repository'
- Adjust Recent Uploads
- 'More'-button added to frontpage


Version 2022.1 (released 2022-01-26)

- Frontpage lists recent uploads
- Display creators of records nicely on frontpage
- Restyled Records on frontpage


Version 2021.11 (released 2022-01-05)

- Make ready for InvenioRDM v7 and Flask 2.0.2+
- Fix upload deposit upload quota


Version 2021.10 (released 2021-09-27, updated 2021-11-09)

- Add THEME_SITENAME config variable
- Make site name configurable
- Override webpack configuration in order to enable webp image assets
- Fix Manifest file
- Improved Accessibility on frontpage
- Increase Link Contrast
- SEO improvements
- Remove left-over usage of removed config variable
- Removed unintended link on frontpage
- Tooltip added to filenames on record landingpages


Version 2021.9 (released 2021-08-16, updated 2021-09-20)

- Capsulated CSS into Semantic UI Theme
- Fixed UI bugs (sticky header and mobile menu)
- Fixed typos on frontpage
- Fixed button text color
- Fixed footer (footer should still stick to the bottom of the page on pages with small content)
- Fixed Dropdown element font
- Fixed Login/Logout Button
- Added `alt`-text to all images
- Compressed hero images
- Improved Accessibility
- Fix mobile bugs on mobile version
- TU Data renamed to TU Research Data
- Feature section headings renamed
- Fix display of licenses
- Use configured search settings rather than hard-coded values
- Use upstream implementation of "cite as"
- Improve translation support
- Fix checkboxes not having visible check marks


Version 2021.8 (released 2021-07-29, updated 2021-08-12)

- Added hero images.
- Fixed navigation.
- Fix build errors.
- Update module for InvenioRDM 6.0 release.


Version 2021.7 (released 2021-07-29)

- Fix PDF files not being previewed.
- Fix incorrect sources for images in footer.
- Housekeeping (removing old scripts, ...).


Version 2021.6 (released 2021-07-18)

-  Fixes to corporate design, e.g.

   -  login button
   -  flipping tiles
   -  spacing


Version 2021.5 (released 2021-07-16)

- Fix set of distributed files.


Version 2021.4 (released 2021-07-16)

- Implement new TUW corporate design.


Version 2021.3 (released 2021-07-16)

- Fix set of distributed files.


Version 2021.2 (released 2021-07-16)

- Rework caching of result for schemaorg metadata.


Version 2021.1 (released 2021-07-15)

- Initial public release.
