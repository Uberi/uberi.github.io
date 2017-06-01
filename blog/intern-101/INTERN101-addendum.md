
<style>
/* use a more condensed text style */
li {
  line-height: 120%;
  margin-bottom: 0.5em;
}

/* nested points should be smaller */
li > ul > li {
  font-size: 0.8em;
}

/* ensure checkbox labels don't wrap around below the checkbox itself */
label {
  display: inline-flex;
  width: 100%;
  align-items: flex-start;
  vertical-align: top;
}
label > input {
  flex: 0 0 1em; /* can't grow or shrink in flexbox, always 1em */
  margin: 0 0.5em 0.3em 0;
}
label > span {
  flex: 1; /* can grow or shrink in flexbox as necessary */
}

/* gray out checked checkbox text */
input:checked + span { color: #CCCCCC; }
input:checked + span a { color: #CCCCCC; }
</style>

<script type="text/javascript">
// current state serialization version
// each time any checkboxes change, this version needs to be incremented and
// we need to write a migration from the previous version to the new version where indicated in loadCheckboxStates()
var CURRENT_STATE_VERSION = 1;

// load checkbox states from local storage
function loadCheckboxStates() {
  var version;
  var checkboxStates;
  try {
    version = window.localStorage.getItem("checkbox_states_version");
    if (version === null) { return; } // no version available - probably user's first visit
    version = parseInt(version);
    checkboxStates = window.localStorage.getItem("checkbox_states");
  }
  catch(e) {
    console.error("READING CHECKBOX STATES FROM LOCAL STORAGE FAILED", e, e.stack);
    return;
  }

  /*
  // a useful snippet for finding the index of a checkbox:
  CHECKBOX_LABEL_TEXT = "Double check the details of your return flight to Canada."
  document.querySelectorAll("li input[type='checkbox']").forEach(function(checkbox, i) {
    if (checkbox.parentElement.innerText.indexOf(CHECKBOX_LABEL_TEXT) != -1) {
      console.log(i, checkbox.parentElement);
    }
  });
  // now the checkbox at the index the snippet printed out can be found in the state using: checkboxStates.slice(INDEX, INDEX + 1)
  */

  // MIGRATIONS GO HERE
  /*
  // example of what migrations would look like, assuming the current version is 2
  // (so we'd need to handle clients with version 0 or 1 of the checkbox states, and convert them to version 2)
  if (version === 0) { // migrate from version 0 to 1
    checkboxStates = checkboxStates.slice(0, 4) + "0" + checkboxStates.slice(4); // to get from version 0 to 1, add a checkbox between the 4rd and 5th checkbox in the document (from the top)
    version ++; // update the version now that we've migrated it
  }
  if (version === 1) { // migrate from version 1 to 2 (current version)
    checkboxStates = checkboxStates.slice(0, 6) + checkboxStates.slice(7); // to get from version 1 to 2, remove a checkbox between the 7th and 8th checkbox in the document (from the top)
    version ++; // update the version now that we've migrated it
  }
  */
  if (version === 0) { // migrate from version 0 to 1
    // three checkboxes, at indices 182 to 184 inclusive, were changed to four checkboxes with similar meanings, so we can directly transfer checkbox states
    var schoolPreparations = checkboxStates[183];
    var housingPreparations = checkboxStates[184];
    checkboxStates = checkboxStates.slice(0, 182) + schoolPreparations + schoolPreparations + schoolPreparations + schoolPreparations + housingPreparations + checkboxStates.slice(185);
    version ++; // update the version now that we've migrated it
  }

  // check that the version is correct - that the migrations moved the version up to the current version if it was older
  if (version !== CURRENT_STATE_VERSION) {
    console.error("STATE IN LOCAL STORAGE HAS INVALID VERSION " + version + ", EXPECTED " + CURRENT_STATE_VERSION);
    return;
  }

  // set checkbox states based on the loaded state data
  var checkboxes = document.querySelectorAll("li input[type='checkbox']");
  if (checkboxStates.length !== checkboxes.length) {
    console.error("STATE IN LOCAL STORAGE HAS " + checkboxStates.length + " CHECKBOXES, EXPECTED " + checkboxes.length + " CHECKBOXES");
    return;
  }
  checkboxes.forEach(function(checkbox, i) {
    checkbox.checked = checkboxStates[i] === "1";
  });
}

// save current checkbox states to local storage
function saveCheckboxStates() {
  var checkboxStates = "";
  document.querySelectorAll("li input[type='checkbox']").forEach(function(checkbox) {
    checkboxStates += checkbox.checked ? "1" : "0";
  });

  try {
    window.localStorage.setItem("checkbox_states_version", CURRENT_STATE_VERSION.toString());
    window.localStorage.setItem("checkbox_states", checkboxStates);
  }
  catch(e) {
    console.error("STORING CHECKBOX STATES TO LOCAL STORAGE FAILED", e, e.stack);
  }
}

// add some quality-of-life improvements for nested checkboxes
document.querySelectorAll("li input[type='checkbox']").forEach(function(checkbox) {
  checkbox.addEventListener("change", function() {
    var item = checkbox.parentElement.parentElement;
    if (item.tagName != "LI") { return; } // ignore checkboxes that aren't list items

    // checking/unchecking a checkbox should also check/uncheck child checkboxes
    item.querySelectorAll("li input[type='checkbox']").forEach(function(childCheckbox) {
      childCheckbox.checked = checkbox.checked;
    });

    // the parent of the checked/unchecked checkbox should be checked if and only if all of its children are checked (non-recursive)
    var parentItem = item.parentElement.parentElement;
    if (parentItem.tagName === "LI") {
      var allChecked = true;
      parentItem.querySelectorAll(":scope > ul > li input[type='checkbox']").forEach(function(siblingItem) {
        allChecked = allChecked && siblingItem.checked;
      });
      parentItem.querySelector(":scope > label input[type='checkbox']").checked = allChecked;
    }

    saveCheckboxStates();
  });
});

loadCheckboxStates();
</script>