function filterFlags() {
    var corporationId = document.getElementById("corporation_id").value;
    var boxId = document.getElementById("box_id").value;
    var flagSelect = document.getElementById("flag_id");
    var options = flagSelect.options;
    
    // First filter boxes based on corporation selection
    var boxSelect = document.getElementById("box_id");
    for (var i = 0; i < boxSelect.options.length; i++) {
        var boxOption = boxSelect.options[i];
        if (boxOption.value === "") continue; // Skip "All Boxes" option
        var boxCorpId = boxOption.getAttribute("data-corporation");
        if (corporationId === "" || boxCorpId === corporationId) {
            boxOption.style.display = "";
        } else {
            boxOption.style.display = "none";
            // If current box selection is hidden, reset to "All Boxes"
            if (boxOption.value === boxId) {
                boxSelect.value = "";
                boxId = "";
            }
        }
    }
    
    // Then filter flags
    var hasVisibleOptions = false;
    for (var i = 0; i < options.length; i++) {
        var option = options[i];
        var flagCorporationId = option.getAttribute("data-corporation");
        var flagBoxId = option.getAttribute("data-box");
        
        var showOption = (corporationId === "" || flagCorporationId === corporationId) && 
                        (boxId === "" || flagBoxId === boxId);
        
        option.style.display = showOption ? "" : "none";
        option.disabled = !showOption;
        
        if (showOption && !hasVisibleOptions) {
            hasVisibleOptions = true;
            flagSelect.value = option.value;
        }
    }
    
    // If no flags match, select the first available option
    if (!hasVisibleOptions && options.length > 0) {
        flagSelect.value = "";
    }
}