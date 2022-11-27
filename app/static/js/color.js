//SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
//SPDX-License-Identifier: AGPL-3.0-only


function initColor() {
  localPrimaryColor = localStorage.getItem("--primary-color")
  if (localPrimaryColor != null) {
    document.body.style.setProperty("--primary-color", localPrimaryColor);
  }

  localSecondaryColor = localStorage.getItem("--secondary-color")
  if (localSecondaryColor != null) {
    document.body.style.setProperty("--secondary-color", localSecondaryColor);
  }
}

function changeColor() {
  const target = event.target;
  var primaryColor = getComputedStyle(target).getPropertyValue("--theme-primary");
  var secondaryColor = getComputedStyle(target).getPropertyValue("--theme-secondary");
  colors.forEach((color) => color.classList.remove("active"));
  target.classList.add("active");
  document.body.style.setProperty("--primary-color", primaryColor);
  localStorage.setItem("--primary-color", primaryColor);
  localStorage.setItem("--secondary-color", secondaryColor);
  initColor()
}

initColor()
const colors = document.querySelectorAll(".submit-color-button");
colors.forEach((color) => color.addEventListener("click", changeColor));

