// Copyright (C) 2025 CERN.
// Copyright (C) 2025 TU Wien.
//
// Invenio Theme TUW is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// override the publish modal according to: https://inveniordm.docs.cern.ch/operate/customize/compliance_info/
import React from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { PublishModal } from "@js/invenio_rdm_records";
import { parametrize } from "react-overridable";

const parameters = {
  extraCheckboxes: [
    {
      fieldPath: "acceptPrivacyRequirement",
      text: i18next.t(
        "I confirm that this dataset is effectively anonymized and GDPR-compliant.",
      ),
    },
  ],
  beforeContent: () => (
    <div class="ui tiny visible info message mb-10">
      <p>
        <i aria-hidden="true" class="secret user icon"></i>
        Privacy note: As a rule, datasets must be fully anonymized; If personal
        data are present, processing is permitted only in strict compliance with
        the GDPR and rigorous ethical standards.
      </p>
    </div>
  ),
};

export const PublishModalComponent = parametrize(PublishModal, parameters);
