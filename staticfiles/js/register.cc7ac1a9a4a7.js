$(document).ready(function() {
    $('#policy_check_box').on('change', function() {
        if ($(this).is(':checked')) {
        $('#form_submit').prop('disabled', false);
        } else {
        $('#form_submit').prop('disabled', true);
        }
    });
});