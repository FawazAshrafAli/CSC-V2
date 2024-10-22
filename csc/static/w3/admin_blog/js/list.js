$(document).ready(() => {
    function toggleBlogDeletion(blogSlug, blogTitle) {		
        $('#delete-confirmation-box form').prop('action', `/admin/delete_blog/${blogSlug}`);
        $('#blog-name').html(`'${blogTitle}'`);
        $('#delete-confirmation-box').show();
        };				
        
    // Calling delete confirmation box
    $('.toggle-blog-delete-btn').click(function (e) {
        e.stopPropagation();
        const blogSlug = $(this).data("blog-slug");
        const blogTitle = $(this).data("blog-title");

        toggleBlogDeletion(blogSlug, blogTitle);
    })

    // Calling cancel function		
    $('.cancel-btn').click(() => $('#delete-confirmation-box').hide());						
});