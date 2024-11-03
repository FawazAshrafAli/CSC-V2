$(document).ready(() => {
    function toggleProductCategoryDeletion(productCategorySlug, productCategoryName) {		
        $('#delete-confirmation-box form').prop('action', `/admin/delete_product_category/${productCategorySlug}`);
        $('#category-name').html(`'${productCategoryName}'`);
        $('#delete-confirmation-box').show();
    };

    // Call delete confirmation box
    $('.toggle-category-delete-btn').click(function (e) {
        event.stopPropagation();
        const categorySlug = $(this).data("category-slug");
        const categoryName = $(this).data("category-name");

        toggleProductCategoryDeletion(categorySlug, categoryName);
    })

    // Call Cancel function
    $('.cancel-btn').click(() => {
        $('#delete-confirmation-box').hide();
    });
});