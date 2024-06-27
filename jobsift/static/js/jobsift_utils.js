function updateStatus(statusInput) {
    const statusIcon = document.getElementById("status-icon");
    const currentStatusSpan = document.getElementById("current-status");

    //Set the colour of the icon
    switch (statusInput.toLowerCase()) {
        case "failed":
        case "inactive":
        statusIcon.style.color = "#ef4444";
        break;
        case "partially_active":
        statusIcon.style.color = "#fb923c";
        break;
        case "active": 
        statusIcon.style.color = "#34C759";         
        break;
        default:
        statusIcon.style.color = "#34C759";  
    }
    //Update the text in the span
    currentStatusSpan.textContent = statusInput;
}

function updateJobDetails(job_board_id) {
    // highlight job board div
    $('#job-boards  li').click(function(e) {
        e.stopPropagation();
        $('li.bg-blue-300').removeClass("bg-blue-300");
        $('li.border').removeClass("border");
        $(this).addClass("bg-blue-300");
        $(this).addClass("border");
    });

    var redStatusTemplate = `
    <tr>
        <td class="px-6 py-2 whitespace-nowrap">{selector}</td>
        <td class="px-6 py-2 text-right whitespace-nowrap">
        <i class="fa-solid fa-circle" style="color: #ef4444;"></i>
        <span class="ml-1">{status}</span>
        <button id="dropdown-button" class="text-gray-400 hover:text-gray-600" onclick="revealErrorMessage(this)">
            <i id="dropdown-icon" class="fas fa-chevron-down ml-2"></i>
        </button>
        </td>
    </tr>
    <tr id="dropdown-textbox" class="hidden">
        <td colspan="2" class="px-6">
        <p class="mt-1 block w-full py-2 px-3 text-sm">{errorMessage}</p>
        </td>
    </tr>
    `;

    var greenStatusTemplate = `
    <tr>
        <td class="px-6 py-2 whitespace-nowrap">{selector}</td>
        <td class="px-6 py-2 text-right whitespace-nowrap">
        <i class="fa-solid fa-circle" style="color: #22c55e;"></i>
        <span class="ml-1">{status}</span>
        </td>
    </tr>
    `;

    // get job board data by id and update details on right hand side
    $.ajax({
        type: 'GET',
        url: '/api/job_board/' + job_board_id + '/',
        dataType: 'json',
        success: function(jobBoardData) {
            // Job Board Details
            $("h2#job-board-name").text(jobBoardData.name);
            const url_a = $("a#job-board-url");
            url_a.text(jobBoardData.url);
            url_a.attr('href', jobBoardData.url);
            $("input#job-board-id").val(job_board_id);

            // Job Selectors
            $("form#job-board-selector-form input[id^=input-]").val("");
            $.each(jobBoardData.job_board_selectors, function(index, selector) {
                $("input#input-"+selector.field).val(selector.css_selector);
            });

            // Search Selectors
            $("form#job-board-search-selector-form input[id^=input-]").val("");
            $.each(jobBoardData.job_board_search_selectors, function(index, selector) {
                $("input#input-"+selector.field).val(selector.css_selector);
            });

            lockForms();

            // Status
            // update overall status
            console.log(jobBoardData.status);
            updateStatus(jobBoardData.status);
            
            // Clear out the table
            $('tbody#inactive-rows').empty();
            $('tbody#active-rows').empty();
            $('#active-selectors-text').text('');

            var selectors = jobBoardData.job_board_search_selectors.concat(jobBoardData.job_board_selectors);

            // active selectors
            var totalSelectors = selectors.length;
            // Get the number of active selectors
            var activeSelectors = selectors.filter(function(selector) {
            return selector.status === 'active';
            }).length;


            // Update the active rows header
            const activeRowsHeader = $('#active-rows-header');
            const activeSelectorsText = $('#active-selectors-text');

            // If there are no active selectors, hide the header
            if (activeSelectors === 0) {
                activeRowsHeader.addClass('hidden');
            } else {
                activeRowsHeader.removeClass('hidden');
                activeSelectorsText.text(activeSelectors + '/' + totalSelectors + ' Active Selectors');
            }

            // fill active/inactive rows
            const inactiveTable = $('tbody#inactive-rows');
            const activeTable = $('tbody#active-rows');

            for (var i = 0; i < selectors.length; i++) {
                var selector = selectors[i];
                // Check if the status is failed or inactive
                if (selector.status === 'failed' || selector.status === 'inactive') {
                    // Create a new table row
                    var row = redStatusTemplate.replace('{selector}', selector.field).replace('{errorMessage}', selector.error_message).replace('{status}', selector.status);
                    // Add the row to the table
                    inactiveTable.append(row);
                }
                else if (selector.status === 'active') {
                    // Create a new table row
                    var row = greenStatusTemplate.replace('{selector}', selector.field).replace('{status}', selector.status);
                    // Add the row to the table
                    activeTable.append(row);
                }
            }
        },
        error: function(xhr, status, error) {
            console.log(error);
        }
    });
}

function revealAdvancedFields(event) {
    event.preventDefault();
    if ($('#advanced-fields').is(':hidden')) {
      $('#advanced-fields').slideDown();
      $("#toggle-advanced-fields").text("-");
    } else {
        $('#advanced-fields').slideUp();
        $("#toggle-advanced-fields").text("+");
    }
}

function revealStatusTable(event){
    event.preventDefault();
    if ($('#status-table').is(':hidden')) {
        $('#status-table').slideDown();
        $('#dropdown-icon').toggleClass('fa-chevron-down fa-chevron-up');
    }
    else {
        $('#status-table').slideUp();
        $('#dropdown-icon').toggleClass('fa-chevron-down fa-chevron-up');
    }
}

function revealErrorMessage(element) {
    const textbox = $(element).closest('tr').next('tr#dropdown-textbox');
    if (textbox.is(':hidden')) {
        textbox.slideDown();
        textbox.toggleClass('hidden');
        $(element).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    }
    else {
        textbox.slideUp();
        textbox.toggleClass('hidden');
        $(element).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    }
}

function revealActiveRows() {
    const activeRows = $('tbody#active-rows');
    if (activeRows.is(':hidden')) {
        activeRows.slideDown();
        activeRows.toggleClass('hidden');
    }
    else {
        activeRows.slideUp();
        activeRows.toggleClass('hidden');
    }
}

// (un)locks form on job boards page
function lockForms() {
    $("form#job-board-selector-form input").prop('disabled', true);
    $("form#job-board-search-selector-form input").prop('disabled', true);
    $("i#form-lock").attr('class', 'fa-solid fa-lock');
}

function unlockForm(formId) {
    lockForms();
    $(`form#${formId} input`).prop('disabled', false);
    $(`form#${formId} i#form-lock`).attr('class', 'fa-solid fa-lock-open');
    $(`form#${formId} #save-changes-button`).removeClass("hidden");
}

function revealJobBoardForm(element) {
    const parentDiv = $("#job-board-list-container");
    const revealForm = $('#job-board-form');

    if (parentDiv.hasClass('w-72')) { 
        // Grow the div to w-1/2 with a transition
        parentDiv.animate({
            width: '50%',
        }, 400);
        revealForm.animate({
            width: 'toggle',
        }, 400);
        $("#job-board-form input").prop("disabled", false);
        $("#job-board-form-title").text("New Job Board");
    } else { 
        $("#job-board-form-title").text("");
        // Shrink the div back to w-72 with a transition
        parentDiv.animate({
            width: '296px' // Use the actual pixel width for w-72
        }, 400);
        revealForm.animate({
            width: 'toggle',
        }, 400);
        $("#job-board-form input").prop("disabled", true);
    }
    parentDiv.toggleClass('w-72 w-1/2');
    revealForm.toggleClass('hidden');
}