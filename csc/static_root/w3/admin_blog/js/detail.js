$(document).ready(() => {
    $('#blog-more-option-btn').click(() => {            
        $('#delete-toggle-btn').show();
        $('#update-toggle-btn').show();
        setTimeout(() => {
            $('#delete-toggle-btn').hide();
            $('#update-toggle-btn').hide();
        }, 5000)
    });

    $('#delete-toggle-btn').click(() => {
        $('#delete-confirmation-box').show();
        $('#delete-toggle-btn').hide();
        $('#update-toggle-btn').hide();
    });

    $('#cancel-deletion-btn').click(() => {
        $('#delete-confirmation-box').hide();
    });
})