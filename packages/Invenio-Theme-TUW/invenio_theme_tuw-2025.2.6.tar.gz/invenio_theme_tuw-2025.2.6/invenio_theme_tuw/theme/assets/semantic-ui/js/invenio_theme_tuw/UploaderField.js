// Copyright (C) 2025 TU Wien.
//
// Invenio Theme TUW is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import {
  UppyUploader,
  FileUploader,
  getInputFromDOM,
} from "@js/invenio_rdm_records";

// override the upstream uppy uploader to now allow selection of folders
export const TUppyUploader = (props) => {
  if (getInputFromDOM("deposits-use-uppy-ui")) {
    return <UppyUploader fileManagerSelectionType="files" {...props} />;
  } else {
    return <FileUploader {...props} />;
  }
};
