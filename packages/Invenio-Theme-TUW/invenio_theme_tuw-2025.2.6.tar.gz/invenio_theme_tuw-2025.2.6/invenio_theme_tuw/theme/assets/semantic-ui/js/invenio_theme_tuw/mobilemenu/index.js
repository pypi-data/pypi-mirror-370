// This file is part of InvenioRDM
// Copyright (C) 2021 TU Wien.
//
// Invenio Theme TUW is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import $ from "jquery";

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("nav-icon").addEventListener("click", function () {
    $(this).toggleClass("open");
    $("#sidebar").sidebar("setting", "onHide", () => {
      $("#nav-icon").removeClass("open");
    });
    $("#sidebar").sidebar("show");
  });
});
