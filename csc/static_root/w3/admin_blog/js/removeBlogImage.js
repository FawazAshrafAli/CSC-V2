function removeBlogImage(blogId) {
    $.ajax({
        type: 'POST',
        url: `/admin/remove_blog_image/${blogId}`,
        dataType: 'json',
        success: (data) => {
            if (data.message) {
                console.log(data.message);
                $('#current-blog-image').hide();
            };
        },
        error: (error) => {
            console.error("Error: ", error);
        },
    });
};