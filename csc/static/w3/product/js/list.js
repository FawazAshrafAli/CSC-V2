$(document).ready(() => {
    function getProducts(categoryId) {
        $.ajax({
          type: 'GET',
          url: `/products/tags/${categoryId}`,
          dataType: 'json',
          success: response => {
            if (response.products && Array.isArray(response.products)) {
              $('#list-product-div').html('');
              response.products.forEach(product => {
                html = `<div class="col-lg-3 col-md-4">
                        <div class="product-grid">
                          <div class="product-image">
                            <a href="#" class="image order-btn" data-slug="${product.slug}">
                              <img class="pic-1" data-slug="${product.slug}" src="${product.image ? product.image : '/static/w3/images/noe_image.png'}" />
                              <img class="pic-2" data-slug="${product.slug}" src="${product.image ? product.image : '/static/w3/images/noe_image.png'}" />
                            </a>
                            <span class="product-sale-label">sale!</span>
  
                            <div class="product-rating">
                              <a class="add-to-cart order-btn" href="#" data-slug="${product.slug}"> ORDER NOW </a>
                            </div>
                          </div>
                          <div class="product-content">
                            <h3 class="title"><a href="#" class="order-btn" data-slug="${product.slug}">${product.name}</a></h3>
                            <div class="price">₹${product.price}</div>
                          </div>
                        </div>
                      </div>`
                $('#list-product-div').append(html);
              });
            }
          },
          error: error => {
            console.error('Error: ', error)
          }
        });
      };
  
      $('#category-dropdown').on('change', function () {
        getProducts($(this).val())
      })

    //   *****************************
    


})