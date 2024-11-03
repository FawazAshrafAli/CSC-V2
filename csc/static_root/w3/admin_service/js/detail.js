$(document).ready(() => {
    $('#service-more-option-btn').click(() => {
        $('#update-toggle-btn, #delete-toggle-btn').show();
        setTimeout(() => {
            $('#update-toggle-btn, #delete-toggle-btn').hide();
        }, 5000)
    });
    
    $('#delete-toggle-btn').click(() => {
        $('#delete-confirmation-box').show();
        $('#delete-toggle-btn').hide()
    });
    
    $('#cancel-deletion-btn').click(() => {
        $('#delete-confirmation-box').hide();
    });
});