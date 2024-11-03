$(document).ready(() => {
    // Pagination
    function paginator () {
        let itemsPerPage = 9;
        let currentPage = 1;
        let totalItems = $('.row-items').length;
        let totalPages = Math.ceil(totalItems / itemsPerPage);
  
        $('.prev-page').hide();      
  
        function paginationBtnVisibility() {
          $('#first-page, #second-page, #third-page').removeClass('current-page prev-page next-page uncoming-page earlier-page').hide();
          $('.next-page').hide();
          $('.prev-page').hide();
          
          if (currentPage == totalPages) {          
            $('.next-page').hide();
            
            if (totalPages == 1) {
              $('#first-page').html(currentPage).addClass('current-page').show();                       
              
            } else if (totalPages == 2) {
              $('#first-page').html(currentPage - 1).addClass('prev-page').show();            
              $('#second-page').html(currentPage).addClass('current-page').show();
              $('.prev-page').show();
              
            } else if (totalPages == 3) {
              $('#first-page').html(currentPage - 2).addClass('earlier-page').show();
              $('#second-page').html(currentPage - 1).addClass('prev-page').show();
              $('#third-page').html(currentPage).addClass('current-page').show();
              $('#prev-page').show();
  
            } else {
              $('#first-page').html(currentPage - 2).addClass('earlier-page').show();
              $('#second-page').html(currentPage - 1).addClass('prev-page').show();
              $('#third-page').html(currentPage).addClass('current-page').show();
              $('.prev-page').show();            
            };
  
          } else if (currentPage > 1) {          
            $('.prev-page').show();
            $('.next-page').show();
            $('#first-page').html(currentPage - 1).addClass('prev-page').show();
            $('#second-page').html(currentPage).addClass('current-page').show();
            $('#third-page').html(currentPage + 1).addClass('next-page').show();
  
          } else if (currentPage == 1 && totalPages > 0) {          
            $('.next-page').show();
            $('#first-page').html(currentPage).addClass('current-page').show();
            $('#second-page').html(currentPage + 1).addClass('next-page').show();
  
            if (totalPages >= 3) {          
              $('#third-page').html(currentPage + 2).addClass('upcoming-page').show();
            }
          }          
        };
  
        paginationBtnVisibility();
  
        function renderPage(page) {
            $('.row-items').hide();
            $('.row-items').slice((page - 1) * itemsPerPage, page * itemsPerPage).show();
            $('#pagination a').removeClass('active');
            $('#pagination a').eq(page).addClass('active');
            $('.prev-page').toggleClass('disabled', page === 1);
            $('.next-page').toggleClass('disabled', page === totalPages);
        }
  
        $(document).on('click', '.next-page', function() {
            if (currentPage < totalPages) {
                currentPage++;
                $('#current-page').html(currentPage);
                paginationBtnVisibility();
                renderPage(currentPage);
            }
        });
  
        $(document).on('click', '.upcoming-page', function() {
            if (currentPage < totalPages - 1) {
                currentPage += 2;
                $('#current-page').html(currentPage);
                paginationBtnVisibility();
                renderPage(currentPage);
            }
        });
  
        $(document).on('click', '.prev-page', function() {
          if (currentPage > 1) {
              currentPage--;
              $('#current-page').html(currentPage);
              paginationBtnVisibility();
              renderPage(currentPage);
          }
        });
  
        $(document).on('click', '.earlier-page', function() {
          if (currentPage > 2) {
              currentPage -= 2;
              $('#current-page').html(currentPage);
              paginationBtnVisibility();
              renderPage(currentPage);
          }
        });
  
        // Initialize the first page
        renderPage(currentPage);
      };
  
      paginator();
})