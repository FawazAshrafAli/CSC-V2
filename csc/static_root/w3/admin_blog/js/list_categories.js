$(document).ready(() => {
    function toggleBlogDeletion(categorySlug, categoryName) {		
        $('#delete-confirmation-box form').prop('action', `/admin/delete_blog_category/${categorySlug}`);
        $('#category-name').html(`'${categoryName}'`);
        $('#delete-confirmation-box').show();
    };

    $('.toggle-delete-btn').click(function () {        
        const categorySlug = $(this).data("category-slug");
        const categoryName = $(this).data("category-name");

        toggleBlogDeletion(categorySlug, categoryName);
    });

    // Call cancel btn
    $('#cancel-deletion-btn').click(() => {
        $('#delete-confirmation-box').hide();
    })
});