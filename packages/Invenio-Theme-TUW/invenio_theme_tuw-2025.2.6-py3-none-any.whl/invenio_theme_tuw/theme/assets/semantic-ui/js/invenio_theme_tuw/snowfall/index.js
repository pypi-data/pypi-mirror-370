// This file is part of InvenioRDM
// Copyright (C) 2023 TU Wien.
//
// Invenio Theme TUW is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import $ from "jquery";
import snowFall from "jquery-snowfall";

document.addEventListener("DOMContentLoaded", () => {
  $(document).snowfall({
    flakeCount: 100,
    maxSpeed: 5,
    minSize: 3,
    maxSize: 10,
    flakeColor: "#FEFEFE",
    round: true,
    shadow: true,
  });
});
