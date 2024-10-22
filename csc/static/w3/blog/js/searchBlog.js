$(document).ready(function() {
    function searchBlog(e) {
        if (e) {
            e.preventDefault();
        }
        const query = $('#search-input-value').val();
        const jsonLd = {
            "@context": "http://schema.org",
            "@type": "WebSite",
            "url": "https://cscindia.info",
            "potentialAction": {
                "@type": "SearchAction",
                "target": "https://cscindia.info/?q=" + encodeURIComponent(query),
                "query-input": "required name=q"
            }
        };
        
        // Update the JSON-LD script in the DOM
        $('#dynamic-ld-json').html(JSON.stringify(jsonLd));



        // const url = `/blog/search/?q=` + encodeURIComponent(query);
        const url = `/blog/?q=` + query;

        history.pushState(null, '', url);
        $.ajax({
            type: 'get',
            url: `/blog/search/?=${query}`,
            data: {'q': query},
            dataType: 'json',
            success: (response) => {
                if (response.data.length > 0) {					
                    $('#list-blogs').html(`<h2>Search results for "${query}" </h2><br>`);
                } else {
                    $('#list-blogs').html(`<h2>No results found for "${query}" </h2><br>`);
                }

                if (Array.isArray(response.data)) {						
                    response.data.forEach((blog) => {							
                        html = `<div class="blog-post">				
                            <!-- Img -->
                            <a href="/blog/detail/${blog.slug}" class="post-img">
                                <img src=${blog.image ? blog.image : '/static/images/blog-post-01.jpg'} alt="Blog Image">
                            </a>				
                            <!-- Content -->
                            <div class="post-content">
                                <h3><a href="/blog/detail/${blog.slug}">${blog.title}</a></h3>
                                <ul class="post-meta">
                                    <li>${blog.created_at}</li>
                                </ul>
                                <p>${blog.summary}</p>
                                <a href="/blog/detail/${blog.slug}" class="read-more">Read More <i class="fa fa-angle-right"></i></a>
                            </div>
                        </div>`;

                        $('#list-blogs').append(html);
                    });
                };
            },
            error: (jqXHR, testStatus, errorThrown) => {
                console.error("Error: ", testStatus, errorThrown);
            }
        });
    };

    $('#blog-search-form').on('submit', (e) => searchBlog(e));
});