var waitingDialog = waitingDialog || (function($) {

    var $dialog = $(
        '<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
        '<div class="modal-dialog modal-m">' +
        '<div class="modal-content">' +
        '<div class="modal-header"><h3 style="margin:0;"></h3></div>' +
        '<div class="modal-body">' +
        '<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%"></div></div>' +
        '</div>' +
        '</div></div></div>');

    return {
        /**
     * Opens our dialog
     * @param message Custom message
     * @param options Custom options:
     * 				  options.dialogSize - bootstrap postfix for dialog size, e.g. "sm", "m";
     * 				  options.progressType - bootstrap postfix for progress bar type, e.g. "success", "warning".
     */
        show: function(message, options) {
            // Assigning defaults
            if (typeof options === 'undefined') {
                options = {};
            }
            if (typeof message === 'undefined') {
                message = 'Loading';
            }
            var settings = $.extend({
                dialogSize: 'm',
                progressType: '',
                onHide: null // This callback runs after the dialog was hidden
            }, options);

            // Configuring dialog
            $dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-' + settings.dialogSize);
            $dialog.find('.progress-bar').attr('class', 'progress-bar');
            if (settings.progressType) {
                $dialog.find('.progress-bar').addClass('progress-bar-' + settings.progressType);
            }
            $dialog.find('h3').text(message);
            // Adding callbacks
            if (typeof settings.onHide === 'function') {
                $dialog.off('hidden.bs.modal').on('hidden.bs.modal', function(e) {
                    settings.onHide.call($dialog);
                });
            }
            // Opening dialog
            $dialog.modal();
        },
        /**
     * Closes dialog
     */
        hide: function() {
            $dialog.modal('hide');
        }
    };
})(jQuery);

$(document).ready(function () {
    
    $('#generateHotFixForm').submit(function () {
        var email = $.trim($('#email').val());
        var product = $.trim($('#productsDropDown').val());
        var project = $.trim($('#projectsDropDown').val());
        waitingDialog.show("Generating HotFix, please wait.", {
            dialogSize: 'lg',
            progressType: 'warning'
        });
        if (email == "") {
            $('#emailGroup').addClass('has-error');
            return false;
        }
        else {
            return true;
        }        
    });

    $("#productsDropDown").change(function () {
        var selectedProduct = $("#productsDropDown option:selected").text();
        $.getJSON("products/" + selectedProduct + "/projects", function (result) {
            var mySelect = $('#projectsDropDown');
            mySelect.find('option').remove();
            mySelect.append($('<option disabled selected></option>').val(0).html('-- select an option --'));

            $.each(result, function (i, field) {
                mySelect.append($('<option></option>').val(i + 1).html(field.name));
            });
        });
    });

    $("#projectsDropDown").change(function () {
        var selectedProduct = $("#productsDropDown option:selected").text();
        $("#productFormInput").val(selectedProduct);

        var selectedProject = $("#projectsDropDown option:selected").text();
        $("#projectFormInput").val(selectedProject);

        $.getJSON("products/" + selectedProduct + "/projects/" + selectedProject + "/maps", function(result) {
            var selected = $('#mapsDropdown');
            selected.find('option').remove();
            selected.append($('<option disabled selected></option>').val(0).html('-- select an option --'));

            $.each(result, function (i, field) {
                selected.append($('<option></option>').val(i + 1).html(field.name));
            });
        });
    });

    $("#mapsDropdown").change(function () {
        var selectedProduct = $("#productsDropDown option:selected").text();
        $("#productFormInput").val(selectedProduct);

        var selectedProject = $("#projectsDropDown option:selected").text();
        $("#projectFormInput").val(selectedProject);

        var selectedVersion = $("#mapsDropdown option:selected").text();
        $('#versionFormInput').val(selectedVersion);

        $.getJSON("products/" + selectedProduct + "/projects/" + selectedProject + "/changesets", function (result) {

            $.each($("#generateHotFixForm").find(':checkbox'), function(index, value) {
                value.value = '';
                value.removeNode();
            });

            // Add table:
            var table = '<table class="table table-striped" id="changesets"><thead><tr>';
            table += '<th><i class="glyphicon glyphicon-save-file"></i></th>';
            table += '<th>ID</th>';
            table += '<th>Description</th>';
            table += '<th>Commiter</th>';
            table += '</tr></thead></table>';
            $("#generateHotFixForm").append($(table));
            $('#latestChangesetLabel').html('<br/><h4>Latest Changesets:</h4><br/>');
            // Add checkboxes to table:
            $.each(result, function (i, field) {
                checkbox = '<input type="checkbox" name="checks" value="' + field.changesetId + '">';
                var row = '<tr><td>' + checkbox + '</td><td>' + field.changesetId + '</td><td>' + field.description + '</td><td>' + field.commiter + '</td></tr>';
                $('#changesets').append(row);
            });

            // Enable visual styles for checkboxes:
            $("input[type='checkbox']").change(function () {
                $(this).closest("tr").toggleClass("success", this.checked);
            });
        });
        $.getJSON("products/" + selectedProduct + "/projects/" + selectedProject + "/version/" + selectedVersion + "/latestHotFix", function(result) {
            var obj = JSON.parse(result);
            if (obj.length == 1) {
                var version_number = obj[0].fields.number;
                $('#latestHotFixNumber').html('<br/><h4>HotFix <span id="versionText">' + version_number + '</span> will be generated.<br/><br/></h4>');
            }
        });
    });
});
 
function updateMaps() {
    var selectedProduct = $("#productsDropDown option:selected").text();
    $("#productFormInput").val(selectedProduct);

    var selectedProject = $("#projectsDropDown option:selected").text();
    $("#projectFormInput").val(selectedProject);

    if (selectedProduct.indexOf("select an option") > -1) {
        alert("Please select product and project first!");
        return;
    }

    if (selectedProject.indexOf("select an option") > -1) {
        alert("Please select project first!");
        return;
    }

    $.getJSON("products/" + selectedProduct + "/projects/" + selectedProject + "/updateMaps", function(result) {
    });
}
