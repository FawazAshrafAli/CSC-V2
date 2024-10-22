$(document).ready(() => {
    $('#toggle-blog-category-form-btn').click(() => {
        $('#blog-form').hide();
        $('#page-heading').html('Add Blog Category');
        $('#blog-category-form').show();
    });

    $('.button-pill').click(() => {
        $('#blog-category-form').hide();
        $('#page-heading').html('Add Blog');
        $('#blog-form').show();
    })
});