$(document).ready(() => {
    function previewServiceImageLink () {
        const serviceImageInput = $('#service-image-input')[0];
        const file = serviceImageInput.files[0]
        const fileName = file.name

        if (file) {
            const imageUrl = URL.createObjectURL(file);
            let html = `current image: <a href=${imageUrl} target="_blank" />${fileName}</a>`;
            $('#current-service-image').html(html);
            $('#current-service-image').show();
        };
    };

    $('#service-image-input').on('change', previewServiceImageLink)
})