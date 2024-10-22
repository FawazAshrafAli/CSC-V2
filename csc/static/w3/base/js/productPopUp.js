$(document).ready(() => {

    $(document).on('click', '.order-btn', (e) => {
        $('body *').css('pointer-events', 'none');
        $('#product-pop-up-box, #product-pop-up-box *').css('pointer-events', 'auto');

        const slug = e.target.getAttribute("data-slug");
        let select = $('#product-pop-up-box form select');
        
        select.find('option').each(function () {
        if ($(this).val() == slug) {
            $(this).prop('selected', true);
        } else {
            $(this).prop('selected', false);
        }
        })
        
        $('#product-pop-up-box form select').trigger('chosen:updated');

        $('#product-pop-up-box form').prop('action', `/products/request_product/${slug}`);

        $('#product-pop-up-box').show();
    })

    // Close product pop up box
    $('.close-btn').click(() => {
        $('#product-pop-up-box').hide();
        $('body *').css('pointer-events', 'auto');      
    });
});